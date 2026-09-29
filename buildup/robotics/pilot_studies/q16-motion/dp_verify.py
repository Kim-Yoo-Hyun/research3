"""Independently replay saved released-policy actions and native Push-T labels."""
import hashlib
import json
from pathlib import Path

import numpy as np

from diffusion_policy.env.pusht.pusht_env import PushTEnv, pymunk_to_shapely
from diffusion_policy.env.pusht.pusht_keypoints_env import PushTKeypointsEnv

ROOT = Path('/output')
OUT = ROOT / 'eval1'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def state5(env):
    return np.asarray([*env.agent.position, *env.block.position,
                       env.block.angle % (2*np.pi)], np.float64)


def full(env):
    return np.asarray([*env.agent.position, *env.agent.velocity, *env.block.position,
                       *env.block.velocity, env.block.angle, env.block.angular_velocity], np.float64)


def coverage(env):
    goal = env._get_goal_pose_body(env.goal_pose)
    goal_geom = pymunk_to_shapely(goal, env.block.shapes)
    block_geom = pymunk_to_shapely(env.block, env.block.shapes)
    return float(goal_geom.intersection(block_geom).area / goal_geom.area)


def check_replay(seed, route, trace):
    env = (PushTKeypointsEnv(legacy=True, keypoint_visible_rate=1.0,
                            agent_keypoints=False, render_action=False)
           if route == 'released_dp' else PushTEnv(legacy=True, render_action=False))
    try:
        env.seed(seed)
        policy_obs = env.reset()
        assert np.max(np.abs(state5(env)-trace['observation'][0])) <= 1e-8
        assert np.max(np.abs(full(env)-trace['full'][0])) <= 1e-8
        assert abs(coverage(env)-trace['coverage'][0]) <= 1e-8
        if route == 'released_dp':
            assert policy_obs.shape == (40,)
            assert np.max(np.abs(policy_obs-trace['policy_observation'][0])) <= 1e-8
            assert np.all(trace['policy_observation'][:, 20:] == 1)
            assert trace['chunk_start'][0] == 0
            assert np.all(np.diff(trace['chunk_start']) == 8)
        worst = 0.0
        for i, action in enumerate(trace['action']):
            obs, _, done, info = env.step(np.asarray(action, np.float64))
            worst = max(worst, float(np.max(np.abs(state5(env)-trace['observation'][i+1]))),
                        float(np.max(np.abs(full(env)-trace['full'][i+1]))),
                        abs(coverage(env)-trace['coverage'][i+1]))
            assert int(info['n_contacts']) == int(trace['contact'][i])
            if route == 'released_dp':
                worst = max(worst, float(np.max(np.abs(obs-trace['policy_observation'][i+1]))))
            assert not done or i == len(trace['action'])-1
        assert worst <= 1e-8
        return worst
    finally:
        env.close()


def main():
    evaluation = json.loads((OUT/'evaluation.json').read_text())
    config = json.loads((ROOT/'inspect1/config.json').read_text())
    parity = json.loads((ROOT/'parity1/assessment.json').read_text())
    assert evaluation['status'] == 'completed'
    assert evaluation['checkpoint_sha256'] == config['checkpoint_sha256']
    assert evaluation['source_config_sha256'] == digest(ROOT/'inspect1/config.json')
    assert evaluation['parity_assessment_sha256'] == digest(ROOT/'parity1/assessment.json')
    assert all(row['max_source_vs_maintained_drift'] <= parity['tolerance'] and
               row['keypoint_agent_position_drift'] <= parity['tolerance'] and
               row['source_vs_keypoint_contact_match'] and row['all_masks_visible'] and
               row['policy_input_dim'] == 20 for row in parity['cases'])
    assert evaluation['seeds'] == list(range(49000, 49008))
    assert len(evaluation['rows']) == 16
    results = []
    for seed in evaluation['seeds']:
        rows = [row for row in evaluation['rows'] if row['seed']==seed]
        assert {row['route'] for row in rows} == {'released_dp','ridge_bc'}
        initials = []
        for row in rows:
            path = OUT/row['trace']
            assert digest(path) == row['sha256']
            with np.load(path, allow_pickle=False) as data:
                trace = {key:data[key].copy() for key in data.files}
            n = row['steps']
            assert 1 <= n <= evaluation['horizon']==300
            assert trace['action'].shape==(n,2) and trace['observation'].shape==(n+1,5)
            assert trace['full'].shape==(n+1,10) and trace['coverage'].shape==(n+1,)
            assert trace['contact'].shape==(n,)
            assert all(np.isfinite(x).all() for x in trace.values())
            initials.append(trace['full'][0])
            drift = check_replay(seed, row['route'], trace)
            assert abs(row['final_coverage']-trace['coverage'][-1]) < 1e-10
            assert abs(row['max_coverage']-np.max(trace['coverage'])) < 1e-10
            assert row['any_success'] == bool(np.any(trace['coverage']>.95))
            assert row['final_success'] == bool(trace['coverage'][-1]>.95)
            assert row['any_contact'] == bool(np.any(trace['contact']>0))
            assert row['contact_steps'] == int(np.sum(trace['contact']>0))
            assert row['action_out_of_bounds'] == int(np.sum(np.any((trace['action']<0)|
                                                                 (trace['action']>512), axis=1)))
            motion = np.linalg.norm(trace['full'][-1,4:6]-trace['full'][0,4:6])
            assert abs(row['object_motion_px']-motion) < 1e-10
            results.append(dict(seed=seed, route=row['route'], replay_max_drift=drift,
                                success=row['any_success'], max_coverage=row['max_coverage']))
        assert np.max(np.abs(initials[0]-initials[1])) <= 1e-8
    output = dict(status='passed', evaluation_sha256=digest(OUT/'evaluation.json'),
                  checked_traces=len(results), checked_seeds=len(evaluation['seeds']),
                  max_replay_drift=max(x['replay_max_drift'] for x in results), rows=results)
    (OUT/'verification.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(status='passed', checked_traces=len(results),
                          max_replay_drift=output['max_replay_drift']),indent=2),flush=True)


if __name__ == '__main__':
    main()
