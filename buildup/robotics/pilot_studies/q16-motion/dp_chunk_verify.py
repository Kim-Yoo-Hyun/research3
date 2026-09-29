"""Independent source-environment replay and paired-contract check for chunk1."""
import hashlib
import json
from pathlib import Path

import numpy as np
from diffusion_policy.env.pusht.pusht_keypoints_env import PushTKeypointsEnv
from diffusion_policy.env.pusht.pusht_env import pymunk_to_shapely

OUT = Path('/output/chunk1')
SEEDS = tuple(range(49200, 49216))
ROUTES = ('eight', 'two')


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def physical(env):
    return np.asarray([*env.agent.position, *env.agent.velocity, *env.block.position,
                       *env.block.velocity, env.block.angle, env.block.angular_velocity], np.float64)


def coverage(env):
    goal = env._get_goal_pose_body(env.goal_pose)
    target = pymunk_to_shapely(goal, env.block.shapes)
    block = pymunk_to_shapely(env.block, env.block.shapes)
    return float(target.intersection(block).area / target.area)


def replay(seed, trace):
    env = PushTKeypointsEnv(legacy=True, keypoint_visible_rate=1.0,
                            agent_keypoints=False, render_action=False)
    try:
        env.seed(seed)
        observation = env.reset()
        worst = max(float(np.max(np.abs(physical(env)-trace['full'][0]))),
                    float(np.max(np.abs(observation-trace['policy_observation'][0]))),
                    abs(coverage(env)-trace['coverage'][0]))
        assert worst <= 1e-8
        for i, action in enumerate(trace['action']):
            observation, _, done, info = env.step(np.asarray(action, np.float64))
            worst = max(worst, float(np.max(np.abs(physical(env)-trace['full'][i+1]))),
                        float(np.max(np.abs(observation-trace['policy_observation'][i+1]))),
                        abs(coverage(env)-trace['coverage'][i+1]))
            assert int(info['n_contacts']) == int(trace['contact'][i])
            assert not done or i == len(trace['action'])-1
        assert worst <= 1e-8
        return worst
    finally:
        env.close()


def load(path):
    with np.load(path, allow_pickle=False) as saved:
        return {key: saved[key].copy() for key in saved.files}


def main():
    result = json.loads((OUT/'evaluation.json').read_text())
    assert result['status'] == 'completed'
    assert result['seeds'] == list(SEEDS) and result['routes'] == list(ROUTES)
    assert result['horizon'] == 300 and len(result['rows']) == 32
    assert result['checkpoint_sha256'] == digest(Path('/checkpoint/model.ckpt'))
    assert result['source_config_sha256'] == digest(Path('/output/inspect1/config.json'))
    assert result['parity_assessment_sha256'] == digest(Path('/output/parity1/assessment.json'))
    checked, rescue, harm = [], [], []
    for seed in SEEDS:
        paired = {}
        for route in ROUTES:
            matches = [row for row in result['rows'] if row['seed'] == seed and row['route'] == route]
            assert len(matches) == 1
            row = matches[0]
            path = OUT/row['trace']
            assert digest(path) == row['sha256']
            trace = load(path)
            n = row['steps']
            assert 2 <= n <= 300
            assert trace['action'].shape == (n, 2)
            assert trace['full'].shape == (n+1, 10)
            assert trace['observation'].shape == (n+1, 5)
            assert trace['policy_observation'].shape == (n+1, 40)
            assert trace['coverage'].shape == (n+1,)
            assert trace['contact'].shape == (n,)
            assert all(np.isfinite(value).all() for value in trace.values())
            starts = trace['chunk_start']
            assert starts[0] == 0 and len(starts) == row['policy_calls']
            assert np.all(np.diff(starts) == (8 if route == 'eight' else 2))
            assert np.all(trace['policy_observation'][:, 20:] == 1)
            assert row['native_success'] == bool(np.any(trace['coverage'] > .95))
            assert row['final_success'] == bool(trace['coverage'][-1] > .95)
            assert abs(row['maximum_overlap'] - np.max(trace['coverage'])) <= 1e-10
            assert abs(row['final_overlap'] - trace['coverage'][-1]) <= 1e-10
            contacts = np.flatnonzero(trace['contact'] > 0)
            near = np.flatnonzero(trace['coverage'] >= .90)
            assert row['first_contact_step'] == (int(contacts[0]) if len(contacts) else None)
            assert row['first_090_overlap_step'] == (int(near[0]) if len(near) else None)
            assert 0 <= row['inference_seconds'] <= row['wall_seconds']
            drift = replay(seed, trace)
            paired[route] = (row, trace)
            checked.append(dict(seed=seed, route=route, replay_max_drift=drift))
        original, short = paired['eight'], paired['two']
        assert np.max(np.abs(original[1]['full'][0]-short[1]['full'][0])) <= 1e-8
        assert np.max(np.abs(original[1]['policy_observation'][0]-short[1]['policy_observation'][0])) <= 1e-8
        assert np.max(np.abs(original[1]['action'][:2]-short[1]['action'][:2])) <= 1e-8
        assert np.max(np.abs(original[1]['full'][:3]-short[1]['full'][:3])) <= 1e-8
        assert np.max(np.abs(original[1]['policy_observation'][:3]-short[1]['policy_observation'][:3])) <= 1e-8
        if short[0]['native_success'] and not original[0]['native_success']:
            rescue.append(seed)
        if original[0]['native_success'] and not short[0]['native_success']:
            harm.append(seed)
    summary = dict(status='passed', evaluation_sha256=digest(OUT/'evaluation.json'),
                   checked_traces=len(checked), checked_seeds=len(SEEDS),
                   max_replay_drift=max(item['replay_max_drift'] for item in checked),
                   rescue_seeds=rescue, harm_seeds=harm, rows=checked)
    (OUT/'verification.json').write_text(json.dumps(summary, indent=2, allow_nan=False)+'\n')
    print(json.dumps({key: summary[key] for key in
                      ('status', 'checked_traces', 'max_replay_drift',
                       'rescue_seeds', 'harm_seeds')}, indent=2), flush=True)


if __name__ == '__main__':
    main()
