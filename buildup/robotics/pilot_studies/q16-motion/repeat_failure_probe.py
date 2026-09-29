"""Paired branches at two observed contact failures of the small public PushT BC policy."""
import hashlib
import json
from pathlib import Path

import gymnasium as gym
import gym_pusht  # noqa: F401
import numpy as np

from repeat_bc import action_from_model, full_state

ROOT = Path('/output')
OUT = ROOT / 'failure_branch1'
TOL = 1e-8
SEEDS = (48007, 48010)


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def env_new():
    return gym.make('gym_pusht/PushT-v0', obs_type='state', render_mode=None,
                    disable_env_checker=True)


def capture(env, obs=None):
    if obs is None:
        obs = env.unwrapped.get_obs()
    return dict(observation=np.asarray(obs, np.float64), full=full_state(env),
                coverage=float(env.unwrapped._get_coverage()))


def select_step(trace):
    contacts = trace['contact']
    position = trace['full'][:, 4:6]
    eligible = [i+1 for i in range(min(len(contacts)-11, len(contacts)))
                if contacts[i] > 0 and np.linalg.norm(position[i+1]-position[0]) > 1.0]
    if not eligible:
        return None
    return max(eligible, key=lambda t: float(trace['coverage'][t]))


def replay_prefix(env, seed, trace, step):
    obs, _ = env.reset(seed=seed)
    states = [capture(env, obs)]
    contacts = []
    for action in trace['action'][:step]:
        obs, _, _, _, info = env.step(action)
        states.append(capture(env, obs))
        contacts.append(int(info['n_contacts']))
    return states, np.asarray(contacts)


def branch_once(seed, trace, step, first_action, mean, std, coef):
    env = env_new()
    try:
        prefix, prefix_contacts = replay_prefix(env, seed, trace, step)
        prefix_drift = max(float(np.max(np.abs(np.stack([item[key] for item in prefix]) -
                                               trace[key][:step+1])))
                           for key in ('full', 'observation', 'coverage'))
        prefix_drift = max(prefix_drift, float(np.max(np.abs(prefix_contacts-trace['contact'][:step]))))
        observations = [prefix[-1]['observation']]
        full = [prefix[-1]['full']]
        coverage = [prefix[-1]['coverage']]
        contacts = []
        actions = []
        for index in range(11):
            current = observations[-1]
            action = first_action if index == 0 else action_from_model(current, mean, std, coef)
            obs, _, _, _, info = env.step(action)
            sample = capture(env, obs)
            observations.append(sample['observation'])
            full.append(sample['full'])
            coverage.append(sample['coverage'])
            contacts.append(int(info['n_contacts']))
            actions.append(action)
        return dict(observation=np.asarray(observations), full=np.asarray(full),
                    coverage=np.asarray(coverage), contact=np.asarray(contacts),
                    action=np.asarray(actions)), prefix_drift
    finally:
        env.close()


def main():
    OUT.mkdir(exist_ok=False)
    with np.load(ROOT / 'bc_fit1/ridge.npz') as model:
        mean, std, coef = (model[key].copy() for key in ('mean', 'std', 'coef'))
    evaluation = json.loads((ROOT / 'bc_eval1/evaluation.json').read_text())
    rows = []
    for seed in SEEDS:
        source_row = next(row for row in evaluation['rows']
                          if row['seed'] == seed and row['route'] == 'ridge_bc')
        assert source_row['any_contact'] and not source_row['final_success']
        source_file = ROOT / 'bc_eval1' / source_row['trace']
        assert digest(source_file) == source_row['sha256']
        with np.load(source_file, allow_pickle=False) as saved:
            trace = {key: saved[key].copy() for key in saved.files}
        step = select_step(trace)
        if step is None:
            rows.append(dict(seed=seed, status='no_moved_contact', source_trace=source_row['trace'],
                             source_sha256=source_row['sha256']))
            continue
        base = action_from_model(trace['observation'][step], mean, std, coef)
        assert np.allclose(base, trace['action'][step], atol=1e-6)
        changed = np.clip(base + np.array([60., 0.], np.float32), 0, 512)
        assert np.linalg.norm(changed-base) > 1
        branches = []
        arrays = {}
        for route, action in (('baseline_a', base), ('changed', changed), ('baseline_b', base)):
            result, prefix_drift = branch_once(seed, trace, step, action, mean, std, coef)
            file = OUT / f'{seed}_{route}.npz'
            np.savez_compressed(file, **result)
            arrays[route] = result
            branches.append(dict(route=route, first_action=action.tolist(),
                                 prefix_drift=prefix_drift, trace=file.name, sha256=digest(file),
                                 final_coverage=float(result['coverage'][-1]),
                                 final_object_position=result['full'][-1, 4:6].tolist()))
        repeat_drift = max(float(np.max(np.abs(arrays['baseline_a'][key] -
                                               arrays['baseline_b'][key]))) for key in arrays['baseline_a'])
        changed_distance = float(np.linalg.norm(arrays['changed']['full'][-1, 4:6] -
                                                arrays['baseline_a']['full'][-1, 4:6]))
        row = dict(seed=seed, status='repeatable' if max(repeat_drift, *(b['prefix_drift'] for b in branches)) <= TOL
                   else 'invalid_repeat', selected_step=step, selected_coverage=float(trace['coverage'][step]),
                   source_trace=source_row['trace'], source_sha256=source_row['sha256'],
                   baseline_action=base.tolist(), changed_action=changed.tolist(),
                   baseline_repeat_max_drift=repeat_drift,
                   changed_final_object_distance=changed_distance, branches=branches)
        rows.append(row)
        print(json.dumps({key: row[key] for key in ('seed', 'status', 'selected_step',
                                                   'selected_coverage', 'baseline_repeat_max_drift',
                                                   'changed_final_object_distance')}), flush=True)
    (OUT / 'assessment.json').write_text(json.dumps(dict(status='completed',
                                                        source_evaluation_sha256=digest(ROOT / 'bc_eval1/evaluation.json'),
                                                        policy_checkpoint_sha256=digest(ROOT / 'bc_fit1/ridge.npz'),
                                                        selected_seeds=list(SEEDS), tolerance=TOL,
                                                        cases=rows), indent=2, allow_nan=False) + '\n')


if __name__ == '__main__':
    main()
