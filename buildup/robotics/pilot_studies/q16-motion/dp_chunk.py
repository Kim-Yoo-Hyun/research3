"""Prospective paired 8-action versus 2-action execution of the released Push-T policy."""
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

from diffusion_policy.env.pusht.pusht_keypoints_env import PushTKeypointsEnv
from dp_evaluate import coverage, full, state5

OUT = Path('/output/chunk1')
CHECKPOINT = Path('/checkpoint/model.ckpt')
SEEDS = tuple(range(49200, 49216))
ROUTES = ('eight', 'two')
HORIZON = 300


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def run(seed, route, policy):
    env = PushTKeypointsEnv(legacy=True, keypoint_visible_rate=1.0,
                            agent_keypoints=False, render_action=False)
    try:
        env.seed(seed)
        obs = env.reset()
        history = collections.deque([obs], maxlen=2)
        policy.reset()
        physical, states = [full(env)], [state5(env)]
        observations, covers = [np.asarray(obs, np.float64)], [coverage(env)]
        actions, contacts, chunk_starts = [], [], []
        inference_seconds = 0.0
        start = time.perf_counter()
        done = False
        while len(actions) < HORIZON and not done:
            step = len(actions)
            recent = list(history)
            if len(recent) == 1:
                recent = [recent[0], recent[0]]
            raw = np.stack(recent)
            inputs = raw[:, :20].astype(np.float32)
            mask = raw[:, 20:] > .5
            assert inputs.shape == mask.shape == (2, 20) and mask.all()
            assert np.isfinite(inputs).all()
            # Fixed by seed and *physical decision step*, shared by both routes.
            sample_seed = seed * 1000 + step
            torch.manual_seed(sample_seed)
            torch.cuda.manual_seed_all(sample_seed)
            torch.cuda.synchronize()
            t0 = time.perf_counter()
            with torch.inference_mode():
                result = policy.predict_action({
                    'obs': torch.from_numpy(inputs[None]).cuda(),
                    'obs_mask': torch.from_numpy(mask[None]).cuda()})
            plan = result['action'][0].detach().cpu().numpy()
            torch.cuda.synchronize()
            inference_seconds += time.perf_counter() - t0
            assert plan.shape == (8, 2) and np.isfinite(plan).all()
            chunk_starts.append(step)
            for target in plan[:8 if route == 'eight' else 2]:
                if len(actions) >= HORIZON:
                    break
                action = np.asarray(target, np.float64)
                obs, _, done, info = env.step(action)
                history.append(obs)
                actions.append(action)
                contacts.append(int(info['n_contacts']))
                physical.append(full(env))
                states.append(state5(env))
                observations.append(np.asarray(obs, np.float64))
                covers.append(coverage(env))
                if done:
                    break
        trace = dict(full=np.asarray(physical), observation=np.asarray(states),
                     policy_observation=np.asarray(observations),
                     coverage=np.asarray(covers), action=np.asarray(actions),
                     contact=np.asarray(contacts),
                     chunk_start=np.asarray(chunk_starts, np.int64))
        return trace, time.perf_counter() - start, inference_seconds
    finally:
        env.close()


def row(seed, route, trace, elapsed, inference, path):
    contact_steps = np.flatnonzero(trace['contact'] > 0)
    near_steps = np.flatnonzero(trace['coverage'] >= .90)
    return dict(seed=seed, route=route, steps=len(trace['action']),
                native_success=bool(np.any(trace['coverage'] > .95)),
                final_success=bool(trace['coverage'][-1] > .95),
                maximum_overlap=float(np.max(trace['coverage'])),
                final_overlap=float(trace['coverage'][-1]),
                first_contact_step=int(contact_steps[0]) if len(contact_steps) else None,
                first_090_overlap_step=int(near_steps[0]) if len(near_steps) else None,
                policy_calls=len(trace['chunk_start']),
                wall_seconds=elapsed, inference_seconds=inference,
                trace=path.name, sha256=digest(path))


def main():
    OUT.mkdir(exist_ok=False)
    torch.set_num_threads(4)
    config = json.loads(Path('/output/inspect1/config.json').read_text())
    parity = json.loads(Path('/output/parity1/assessment.json').read_text())
    assert config['checkpoint_sha256'] == digest(CHECKPOINT)
    assert (config['task_obs_dim'], config['task_action_dim'], config['n_obs_steps'],
            config['n_action_steps'], config['inference_steps']) == (20, 2, 2, 8, 100)
    assert config['runner_legacy_test'] is True and config['use_ema'] is True
    assert all(case['max_source_vs_maintained_drift'] <= parity['tolerance'] and
               case['keypoint_agent_position_drift'] <= parity['tolerance'] and
               case['source_vs_keypoint_contact_match'] and case['all_masks_visible']
               for case in parity['cases'])
    OmegaConf.register_new_resolver('eval', eval, replace=True)
    payload = torch.load(CHECKPOINT, map_location='cpu', pickle_module=dill,
                         weights_only=False)
    policy = hydra.utils.instantiate(payload['cfg'].policy)
    policy.load_state_dict(payload['state_dicts']['ema_model'], strict=True)
    policy.to('cuda:0').eval()
    rows = []
    for seed in SEEDS:
        paired = {}
        for route in ROUTES:
            trace, elapsed, inference = run(seed, route, policy)
            path = OUT / f'{seed}_{route}.npz'
            np.savez_compressed(path, **trace)
            rows.append(row(seed, route, trace, elapsed, inference, path))
            paired[route] = trace
            print(json.dumps({k: rows[-1][k] for k in
                              ('seed', 'route', 'steps', 'native_success',
                               'maximum_overlap', 'policy_calls', 'wall_seconds')}), flush=True)
        eight, two = paired['eight'], paired['two']
        assert np.max(np.abs(eight['full'][0] - two['full'][0])) <= 1e-8
        assert np.max(np.abs(eight['action'][:2] - two['action'][:2])) <= 1e-8
        assert np.max(np.abs(eight['full'][:3] - two['full'][:3])) <= 1e-8
    result = dict(status='completed', source_commit='5ba07ac6661db573af695b419a7947ecb704690f',
                  checkpoint_sha256=digest(CHECKPOINT),
                  source_config_sha256=digest(Path('/output/inspect1/config.json')),
                  parity_assessment_sha256=digest(Path('/output/parity1/assessment.json')),
                  device='cuda:0', source_environment='PushTKeypointsEnv legacy=True',
                  observation='two 20D visible-keypoint frames',
                  action='unmodified eight-target policy prediction, execute first 8 or 2',
                  policy_sampling_seed='seed*1000 + physical decision step, reseeded before each policy call',
                  shared_first_call='same seed and observation; first two actions/states checked',
                  horizon=HORIZON, native_success='coverage > 0.95',
                  seeds=list(SEEDS), routes=list(ROUTES), rows=rows)
    (OUT / 'evaluation.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')


if __name__ == '__main__':
    main()
