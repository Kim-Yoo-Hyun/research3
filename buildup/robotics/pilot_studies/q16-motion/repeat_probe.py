"""Two constructed contact-state repeatability probes for public gym-pusht; Docker only."""
import hashlib
import json
from pathlib import Path

import gymnasium as gym
import gym_pusht  # noqa: F401 - registers the public environment
import numpy as np

OUT = Path('/output/probe1')
TOL = 1e-8
CASES = (
    dict(name='straight_push', seed=16031,
         requested_state=[256.0, 390.0, 256.0, 310.0, 0.0],
         target=[256.0, 230.0], changed_target=[310.0, 230.0]),
    dict(name='oblique_push', seed=16032,
         requested_state=[190.0, 350.0, 260.0, 320.0, 0.7853981633974483],
         target=[320.0, 270.0], changed_target=[270.0, 230.0]),
)


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def env_new():
    return gym.make('gym_pusht/PushT-v0', obs_type='state', render_mode=None,
                    disable_env_checker=True)


def sample(env, reward=0.0, contacts=0):
    e = env.unwrapped
    full = np.array([*e.agent.position, *e.agent.velocity,
                     *e.block.position, *e.block.velocity,
                     e.block.angle, e.block.angular_velocity], np.float64)
    observation = np.asarray(e.get_obs(), np.float64)
    return dict(full=full, observation=observation,
                coverage=float(e._get_coverage()), contacts=int(contacts), reward=float(reward))


def pack(samples):
    return {key: np.asarray([sample[key] for sample in samples]) for key in samples[0]}


def maximum_difference(a, b):
    return max(float(np.max(np.abs(a[key] - b[key]))) for key in ('full', 'observation', 'coverage',
                                                                  'contacts', 'reward'))


def run_case(case):
    target = np.asarray(case['target'], np.float32)
    changed = np.asarray(case['changed_target'], np.float32)
    reference = env_new()
    try:
        reference.reset(seed=case['seed'], options={'reset_to_state': case['requested_state']})
        prefix = [sample(reference)]
        initial_block = prefix[0]['full'][4:6].copy()
        contact_step = None
        for step in range(1, 31):
            _, reward, _, _, info = reference.step(target)
            prefix.append(sample(reference, reward, info['n_contacts']))
            moved = float(np.linalg.norm(prefix[-1]['full'][4:6] - initial_block))
            if info['n_contacts'] > 0 and moved >= 0.1:
                contact_step = step
                break
        prefix_arrays = pack(prefix)
        prefix_path = OUT / f"{case['name']}_prefix.npz"
        np.savez_compressed(prefix_path, **prefix_arrays)
        row = dict(name=case['name'], seed=case['seed'], requested_state=case['requested_state'],
                   actual_initial_observation=prefix[0]['observation'].tolist(),
                   actual_initial_full_state=prefix[0]['full'].tolist(),
                   prefix_target=case['target'], changed_target=case['changed_target'],
                   contact_step=contact_step, prefix_trace=prefix_path.name,
                   prefix_sha256=digest(prefix_path),
                   prefix_max_contacts=int(prefix_arrays['contacts'].max()),
                   prefix_object_motion=float(np.linalg.norm(prefix_arrays['full'][-1, 4:6] - initial_block)))
        if contact_step is None:
            row['status'] = 'no_contact_and_motion'
            return row
        split = prefix[-1]
        branches = []
        for route, first in (('baseline_a', target), ('changed', changed), ('baseline_b', target)):
            env = env_new()
            try:
                env.reset(seed=case['seed'], options={'reset_to_state': case['requested_state']})
                replay = [sample(env)]
                for _ in range(contact_step):
                    _, reward, _, _, info = env.step(target)
                    replay.append(sample(env, reward, info['n_contacts']))
                drift = maximum_difference(pack(replay), prefix_arrays)
                branch = [replay[-1]]
                for action in (first,) + (target,) * 10:
                    _, reward, _, _, info = env.step(action)
                    branch.append(sample(env, reward, info['n_contacts']))
                arrays = pack(branch)
                path = OUT / f"{case['name']}_{route}.npz"
                np.savez_compressed(path, **arrays)
                branches.append(dict(route=route, action=first.tolist(), trace=path.name,
                                     sha256=digest(path), prefix_max_drift=drift,
                                     split_full_state=branch[0]['full'].tolist(),
                                     split_coverage=split['coverage'],
                                     first_coverage=branch[1]['coverage'],
                                     final_coverage=branch[-1]['coverage'],
                                     first_object_position=branch[1]['full'][4:6].tolist(),
                                     final_object_position=branch[-1]['full'][4:6].tolist()))
            finally:
                env.close()
        with np.load(OUT / branches[0]['trace']) as first, np.load(OUT / branches[2]['trace']) as last:
            repeat_drift = maximum_difference(first, last)
        row.update(status='repeatable' if max(repeat_drift, *(x['prefix_max_drift'] for x in branches)) <= TOL
                   else 'invalid_repeat', branches=branches, baseline_repeat_max_drift=repeat_drift,
                   changed_action_distance=float(np.linalg.norm(changed - target)),
                   changed_final_object_distance=float(np.linalg.norm(np.asarray(branches[1]['final_object_position'])-
                                                               np.asarray(branches[0]['final_object_position']))))
        return row
    finally:
        reference.close()


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    rows = []
    for case in CASES:
        row = run_case(case)
        rows.append(row)
        print(json.dumps({key: row.get(key) for key in ('name', 'status', 'contact_step',
                                                       'prefix_max_contacts', 'prefix_object_motion',
                                                       'baseline_repeat_max_drift',
                                                       'changed_final_object_distance')}), flush=True)
    (OUT / 'assessment.json').write_text(json.dumps(dict(status='completed',
                                                        environment='gym_pusht/PushT-v0',
                                                        observation='state 5D',
                                                        action='agent target XY',
                                                        case_count=len(rows), tolerance=TOL,
                                                        cases=rows), indent=2, allow_nan=False) + '\n')


if __name__ == '__main__':
    main()
