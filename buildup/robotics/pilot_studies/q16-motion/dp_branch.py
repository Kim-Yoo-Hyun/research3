"""Fixed, paired action branches from two released-policy contact failures."""
import collections
import json
from pathlib import Path
import time

import dill
import hydra
import numpy as np
from omegaconf import OmegaConf
import torch

from diffusion_policy.env.pusht.pusht_keypoints_env import PushTKeypointsEnv
from dp_evaluate import coverage, digest, full, state5

ROOT = Path('/output')
OUT = ROOT / 'branch1'
MAX_STEPS = 300


def select_cases(evaluation):
    candidates = []
    for row in evaluation['rows']:
        if row['route'] != 'released_dp' or row['any_success'] or not row['any_contact']:
            continue
        with np.load(ROOT/'eval1'/row['trace'], allow_pickle=False) as saved:
            trace = {key:saved[key].copy() for key in saved.files}
        boundaries = [int(t) for t in trace['chunk_start'] if
                      0 < t <= min(MAX_STEPS-32, len(trace['action'])-32) and
                      np.any(trace['contact'][:t] > 0) and
                      np.linalg.norm(trace['full'][t,4:6]-trace['full'][0,4:6]) >= 1.0]
        if boundaries:
            selected = max(boundaries, key=lambda t:(float(trace['coverage'][t]), -t))
            candidates.append((float(row['max_coverage']), row['seed'], selected, row, trace))
    candidates.sort(key=lambda x:(-x[0], x[1]))
    return candidates[:2]


def branch_target(route, original, env):
    if route == 'feedback':
        direction = np.asarray([256.,256.]) - np.asarray(env.block.position)
        direction *= min(1., 60./max(float(np.linalg.norm(direction)),1e-12))
        return np.clip(np.asarray(env.agent.position)+direction, 0., 512.)
    if route == 'plus_x':
        return np.clip(original + np.asarray([40.,0.]), 0., 512.)
    return original


def rollout(seed, policy, step, route, original):
    env = PushTKeypointsEnv(legacy=True, keypoint_visible_rate=1.,
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
        physical, covers = [full(env)], [coverage(env)]
        contacts, actions, chunks = [], [], []
        actual_original, actual_replacement = None, None
        started = time.perf_counter()
        done = False
        while len(actions) < MAX_STEPS and not done:
            recent = list(history)
            if len(recent) == 1:
                recent = [recent[0], recent[0]]
            raw = np.stack(recent, axis=0)
            input_obs = raw[:, :20].astype(np.float32)
            input_mask = raw[:, 20:] > .5
            assert input_obs.shape == input_mask.shape == (2,20) and input_mask.all()
            with torch.inference_mode():
                result = policy.predict_action({
                    'obs':torch.from_numpy(input_obs[None]).cuda(),
                    'obs_mask':torch.from_numpy(input_mask[None]).cuda()})
            plan = result['action'][0].detach().cpu().numpy()
            assert plan.shape == (8,2) and np.isfinite(plan).all()
            chunks.append(len(actions))
            if len(actions) == step:
                actual_original = np.asarray(plan[0],np.float64).copy()
                assert np.max(np.abs(actual_original-original)) <= 1e-8
                actual_replacement = branch_target(route, actual_original, env)
                plan[0] = actual_replacement
            for target in plan:
                if len(actions) >= MAX_STEPS:
                    break
                obs, _, done, info = env.step(np.asarray(target,np.float64))
                history.append(obs)
                observations.append(state5(env))
                policy_observations.append(np.asarray(obs,np.float64))
                physical.append(full(env))
                covers.append(coverage(env))
                contacts.append(int(info['n_contacts']))
                actions.append(np.asarray(target,np.float64))
                if done:
                    break
        assert actual_original is not None
        trace = dict(observation=np.asarray(observations),
                     policy_observation=np.asarray(policy_observations),
                     full=np.asarray(physical), coverage=np.asarray(covers),
                     contact=np.asarray(contacts), action=np.asarray(actions),
                     chunk_start=np.asarray(chunks,np.int64))
        return trace, actual_original, actual_replacement, time.perf_counter()-started
    finally:
        env.close()


def prefix_drift(trace, original, step):
    return max(float(np.max(np.abs(trace[key][:step+1]-original[key][:step+1])))
               for key in ('observation','policy_observation','full','coverage'))


def full_drift(trace, original):
    if any(trace[key].shape != original[key].shape for key in original):
        return float('inf')
    return max(float(np.max(np.abs(trace[key]-original[key]))) for key in
               ('observation','policy_observation','full','coverage','action','contact'))


def main():
    OUT.mkdir(exist_ok=False)
    torch.set_num_threads(4)
    evaluation = json.loads((ROOT/'eval1/evaluation.json').read_text())
    verification = json.loads((ROOT/'eval1/verification.json').read_text())
    assert verification['status'] == 'passed'
    selected = select_cases(evaluation)
    assert selected, 'No moved-contact released-policy failure with enough steps remains.'
    OmegaConf.register_new_resolver('eval', eval, replace=True)
    payload = torch.load('/checkpoint/model.ckpt', map_location='cpu',
                         pickle_module=dill, weights_only=False)
    policy = hydra.utils.instantiate(payload['cfg'].policy)
    policy.load_state_dict(payload['state_dicts']['ema_model'], strict=True)
    policy.to('cuda:0').eval()
    rows = []
    for _, seed, step, parent, original in selected:
        original_target = original['action'][step].copy()
        case_rows = []
        for route in ('control_first','feedback','plus_x','control_last'):
            trace, source_target, target, elapsed = rollout(seed,policy,step,route,original_target)
            drift = prefix_drift(trace,original,step)
            assert drift <= 1e-8, f'{seed} {route} prefix drift {drift}'
            assert np.max(np.abs(trace['action'][:step]-original['action'][:step])) <= 1e-8
            if route.startswith('control'):
                control_drift = full_drift(trace,original)
                assert control_drift <= 1e-8, f'{seed} {route} full drift {control_drift}'
            else:
                control_drift = None
            path = OUT/f'{seed}_{route}.npz'
            np.savez_compressed(path, **trace)
            row = dict(seed=seed, route=route, branch_step=step,
                       original_target=source_target.tolist(), target=target.tolist(),
                       prefix_max_drift=drift, original_control_max_drift=control_drift,
                       steps=len(trace['action']),
                       any_success=bool(np.any(trace['coverage']>.95)),
                       max_coverage=float(np.max(trace['coverage'])),
                       final_coverage=float(trace['coverage'][-1]),
                       any_contact=bool(np.any(trace['contact']>0)),
                       contact_steps=int(np.sum(trace['contact']>0)),
                       rollout_seconds=elapsed, trace=path.name, sha256=digest(path))
            rows.append(row); case_rows.append(row)
            print(json.dumps({k:row[k] for k in ('seed','route','branch_step','any_success',
                                                 'max_coverage','prefix_max_drift',
                                                 'original_control_max_drift')}),flush=True)
        with np.load(OUT/case_rows[0]['trace'], allow_pickle=False) as first:
            with np.load(OUT/case_rows[-1]['trace'], allow_pickle=False) as last:
                repeated_drift = max(float(np.max(np.abs(first[k]-last[k])))
                                     for k in first.files)
        assert repeated_drift <= 1e-8, f'{seed} repeated-control drift {repeated_drift}'
        case_rows[-1]['repeated_control_max_drift'] = repeated_drift
    assessment = dict(status='completed', source_evaluation_sha256=digest(ROOT/'eval1/evaluation.json'),
                      source_verification_sha256=digest(ROOT/'eval1/verification.json'),
                      selection='two highest max-coverage failures with native contact, T motion >=1px, >=32 remaining steps',
                      selected_seeds=[x[1] for x in selected],
                      branch_point='highest coverage eligible 8-step chunk boundary after contact and T motion',
                      routes=['control_first','feedback','plus_x','control_last'],
                      comparison='one first-target replacement; next seven chunk actions unchanged; same policy then resumes',
                      rows=rows)
    (OUT/'assessment.json').write_text(json.dumps(assessment,indent=2,allow_nan=False)+'\n')


if __name__ == '__main__':
    main()
