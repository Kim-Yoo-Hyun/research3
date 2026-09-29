"""Evaluate released keypoint Diffusion Policy and prior state BC on paired source Push-T seeds."""
import collections
import hashlib
import json
from pathlib import Path
import time

import dill
import hydra
import numpy as np
from omegaconf import OmegaConf
import torch

from diffusion_policy.env.pusht.pusht_env import PushTEnv, pymunk_to_shapely
from diffusion_policy.env.pusht.pusht_keypoints_env import PushTKeypointsEnv
from repeat_bc import action_from_model

OUT = Path('/output/eval1')
CHECKPOINT = Path('/checkpoint/model.ckpt')
SEEDS = tuple(range(49000, 49008))
MAX_STEPS = 300


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def full(env):
    return np.asarray([*env.agent.position, *env.agent.velocity, *env.block.position,
                       *env.block.velocity, env.block.angle, env.block.angular_velocity], np.float64)


def state5(env):
    return np.asarray([*env.agent.position, *env.block.position,
                       env.block.angle % (2*np.pi)], np.float64)


def coverage(env):
    goal = env._get_goal_pose_body(env.goal_pose)
    goal_geom = pymunk_to_shapely(goal, env.block.shapes)
    block_geom = pymunk_to_shapely(env.block, env.block.shapes)
    return float(goal_geom.intersection(block_geom).area / goal_geom.area)


def run_dp(seed, policy):
    env = PushTKeypointsEnv(legacy=True, keypoint_visible_rate=1.0,
                            agent_keypoints=False, render_action=False)
    try:
        env.seed(seed)
        obs = env.reset()
        history = collections.deque([obs], maxlen=2)
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        policy.reset()
        observations = [state5(env)]
        policy_observations = [np.asarray(obs, np.float64)]
        physical = [full(env)]
        covers = [coverage(env)]
        contacts, actions, chunks = [], [], []
        started = time.perf_counter()
        terminated = False
        while len(actions) < MAX_STEPS and not terminated:
            recent = list(history)
            if len(recent) == 1:
                recent = [recent[0], recent[0]]
            input_obs = np.stack(recent, axis=0)[:, :20].astype(np.float32)
            assert input_obs.shape == (2, 20) and np.isfinite(input_obs).all()
            input_mask = np.stack(recent, axis=0)[:, 20:] > .5
            assert input_mask.shape == (2, 20) and input_mask.all()
            with torch.inference_mode():
                result = policy.predict_action({
                    'obs':torch.from_numpy(input_obs[None]).cuda(),
                    'obs_mask':torch.from_numpy(input_mask[None]).cuda()})
            plan = result['action'][0].detach().cpu().numpy()
            assert plan.shape == (8, 2) and np.isfinite(plan).all()
            chunks.append(len(actions))
            for target in plan:
                if len(actions) >= MAX_STEPS:
                    break
                # The official runner executes unmodified targets from the action chunk.
                obs, _, done, info = env.step(target.astype(np.float64))
                history.append(obs)
                observations.append(state5(env))
                policy_observations.append(np.asarray(obs, np.float64))
                physical.append(full(env))
                covers.append(coverage(env))
                contacts.append(int(info['n_contacts']))
                actions.append(np.asarray(target, np.float64))
                if done:
                    terminated = True
                    break
        elapsed = time.perf_counter()-started
        trace = dict(observation=np.asarray(observations),
                     policy_observation=np.asarray(policy_observations),
                     full=np.asarray(physical), coverage=np.asarray(covers),
                     contact=np.asarray(contacts), action=np.asarray(actions),
                     chunk_start=np.asarray(chunks, np.int64))
        return trace, elapsed
    finally:
        env.close()


def run_bc(seed, mean, std, coef):
    env = PushTEnv(legacy=True, render_action=False)
    try:
        env.seed(seed)
        obs = env.reset()
        observations, physical, covers = [np.asarray(obs)], [full(env)], [coverage(env)]
        contacts, actions = [], []
        started = time.perf_counter()
        for _ in range(MAX_STEPS):
            action = action_from_model(obs, mean, std, coef)
            obs, _, done, info = env.step(action.astype(np.float64))
            observations.append(np.asarray(obs, np.float64))
            physical.append(full(env))
            covers.append(coverage(env))
            contacts.append(int(info['n_contacts']))
            actions.append(action)
            if done:
                break
        elapsed = time.perf_counter()-started
        trace = dict(observation=np.asarray(observations), full=np.asarray(physical),
                     coverage=np.asarray(covers), contact=np.asarray(contacts),
                     action=np.asarray(actions))
        return trace, elapsed
    finally:
        env.close()


def summary(seed, route, trace, elapsed, path):
    success = bool(np.any(trace['coverage'] > .95))
    return dict(seed=seed, route=route, steps=len(trace['action']),
                any_success=success, final_success=bool(trace['coverage'][-1] > .95),
                max_coverage=float(np.max(trace['coverage'])),
                final_coverage=float(trace['coverage'][-1]),
                any_contact=bool(np.any(trace['contact'] > 0)),
                contact_steps=int(np.sum(trace['contact'] > 0)),
                object_motion_px=float(np.linalg.norm(trace['full'][-1, 4:6]-trace['full'][0, 4:6])),
                action_out_of_bounds=int(np.sum(np.any((trace['action'] < 0)|(trace['action'] > 512), axis=1))),
                rollout_seconds=elapsed, trace=path.name, sha256=digest(path))


def main():
    OUT.mkdir(exist_ok=False)
    torch.set_num_threads(4)
    config = json.loads(Path('/output/inspect1/config.json').read_text())
    parity = json.loads(Path('/output/parity1/assessment.json').read_text())
    assert config['checkpoint_sha256'] == digest(CHECKPOINT)
    assert (config['task_obs_dim'], config['task_action_dim'], config['n_obs_steps'],
            config['n_action_steps'], config['inference_steps']) == (20, 2, 2, 8, 100)
    assert config['runner_legacy_test'] is True and config['use_ema'] is True
    # One scene differs only in the count of simultaneous contact points;
    # all physical states, coverage and source/keypoint contact counts agree.
    assert all(row['max_source_vs_maintained_drift'] <= parity['tolerance'] and
               row['keypoint_agent_position_drift'] <= parity['tolerance'] and
               row['source_vs_keypoint_contact_match'] and row['all_masks_visible'] and
               row['policy_input_dim'] == 20 for row in parity['cases'])
    OmegaConf.register_new_resolver('eval', eval, replace=True)
    payload = torch.load(CHECKPOINT, map_location='cpu', pickle_module=dill, weights_only=False)
    cfg = payload['cfg']
    policy = hydra.utils.instantiate(cfg.policy)
    policy.load_state_dict(payload['state_dicts']['ema_model'], strict=True)
    policy.to('cuda:0').eval()
    with np.load('/previous/bc_fit1/ridge.npz', allow_pickle=False) as model:
        mean, std, coef = (model[key].copy() for key in ('mean', 'std', 'coef'))
    rows = []
    for seed in SEEDS:
        paired = []
        for route in ('released_dp', 'ridge_bc'):
            trace, elapsed = (run_dp(seed, policy) if route=='released_dp'
                              else run_bc(seed, mean, std, coef))
            path = OUT / f'{route}_{seed}.npz'
            np.savez_compressed(path, **trace)
            rows.append(summary(seed, route, trace, elapsed, path))
            paired.append(trace['full'][0])
            print(json.dumps({key:rows[-1][key] for key in ('seed','route','steps','any_success',
                                                             'max_coverage','any_contact','rollout_seconds')}),
                  flush=True)
        assert np.max(np.abs(paired[0]-paired[1])) <= 1e-8
    (OUT/'evaluation.json').write_text(json.dumps(dict(status='completed',
              checkpoint_sha256=digest(CHECKPOINT), source_commit='5ba07ac6661db573af695b419a7947ecb704690f',
              previous_ridge_checkpoint_sha256=digest(Path('/previous/bc_fit1/ridge.npz')),
              source_config_sha256=digest(Path('/output/inspect1/config.json')),
              parity_assessment_sha256=digest(Path('/output/parity1/assessment.json')),
              device='cuda:0', source_environment='PushTKeypointsEnv legacy=True for released policy',
              comparison_environment='PushTEnv legacy=True for 5D state BC',
              policy_observation='2*20 keypoint+agent-position history; visibility mask all 1',
              action='unclipped 2D absolute target; 8-step chunks',
              policy_rng='torch CPU/CUDA manual_seed(seed) immediately before each episode',
              seeds=list(SEEDS), horizon=MAX_STEPS, native_success='coverage > 0.95',
              rows=rows), indent=2, allow_nan=False)+'\n')


if __name__ == '__main__':
    main()
