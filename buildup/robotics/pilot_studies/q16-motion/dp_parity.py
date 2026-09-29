"""Compare released PushT physics and keypoint observation with maintained gym-pusht."""
import json
from pathlib import Path

import gymnasium as gymnasium
import gym_pusht  # noqa: F401
import numpy as np

from diffusion_policy.env.pusht.pusht_env import PushTEnv, pymunk_to_shapely
from diffusion_policy.env.pusht.pusht_keypoints_env import PushTKeypointsEnv

OUT = Path('/output/parity1')
TOL = 1e-8
CASES = (
    dict(seed=16031, requested=[256., 390., 256., 310., 0.], action=[256., 230.]),
    dict(seed=16032, requested=[190., 350., 260., 320., np.pi/4], action=[320., 270.]),
)


def full(env):
    e = env.unwrapped if hasattr(env, 'unwrapped') else env
    return np.asarray([*e.agent.position, *e.agent.velocity, *e.block.position,
                       *e.block.velocity, e.block.angle, e.block.angular_velocity], np.float64)


def source_coverage(env):
    goal = env._get_goal_pose_body(env.goal_pose)
    goal_geom = pymunk_to_shapely(goal, env.block.shapes)
    block_geom = pymunk_to_shapely(env.block, env.block.shapes)
    return float(goal_geom.intersection(block_geom).area / goal_geom.area)


def main():
    OUT.mkdir(exist_ok=False)
    rows = []
    for case in CASES:
        original = PushTEnv(legacy=True, reset_to_state=case['requested'])
        keypoint = PushTKeypointsEnv(legacy=True, keypoint_visible_rate=1.0,
                                    agent_keypoints=False, reset_to_state=case['requested'])
        maintained = gymnasium.make('gym_pusht/PushT-v0', obs_type='state', render_mode=None,
                                     disable_env_checker=True)
        try:
            original.seed(case['seed'])
            keypoint.seed(case['seed'])
            source_obs = original.reset()
            keypoint_obs = keypoint.reset()
            maintained_obs, _ = maintained.reset(seed=case['seed'],
                                                  options={'reset_to_state': case['requested']})
            actual_initial = source_obs.copy()
            initial_keypoint_mask = keypoint_obs[20:].copy()
            drifts = []
            keypoint_state_drifts = []
            masks_all_visible = []
            contacts = []
            for i in range(6):
                source_full, maintained_full = full(original), full(maintained)
                source_cover, maintained_cover = source_coverage(original), maintained.unwrapped._get_coverage()
                drift = max(float(np.max(np.abs(source_obs-maintained_obs))),
                            float(np.max(np.abs(source_full-maintained_full))),
                            abs(source_cover-maintained_cover))
                drifts.append(drift)
                keypoint_state_drifts.append(max(
                    float(np.max(np.abs(keypoint_obs[18:20] - source_obs[:2]))),
                    float(np.max(np.abs(full(keypoint) - source_full)))))
                masks_all_visible.append(bool(np.all(keypoint_obs[20:] == 1)))
                if i == 5:
                    break
                action = np.asarray(case['action'], np.float32)
                source_obs, _, _, info_original = original.step(action)
                keypoint_obs, _, _, info_keypoint = keypoint.step(action)
                maintained_obs, _, _, _, info_maintained = maintained.step(action)
                contacts.append([int(info_original['n_contacts']), int(info_keypoint['n_contacts']),
                                 int(info_maintained['n_contacts'])])
            row = dict(seed=case['seed'], requested_state=case['requested'], action=case['action'],
                       source_actual_initial=actual_initial.tolist(),
                       max_source_vs_maintained_drift=max(drifts), step_drifts=drifts,
                       keypoint_observation_dim=len(keypoint_obs), policy_input_dim=len(keypoint_obs)//2,
                       initial_mask_all_visible=bool(np.all(initial_keypoint_mask == 1)),
                       all_masks_visible=all(masks_all_visible),
                       keypoint_agent_position_drift=max(keypoint_state_drifts),
                       contact_records=contacts,
                       source_vs_keypoint_contact_match=all(x[0] == x[1] for x in contacts),
                       source_vs_maintained_contact_match=all(x[0] == x[2] for x in contacts))
            row['status'] = ('compatible' if row['max_source_vs_maintained_drift'] <= TOL and
                             row['all_masks_visible'] and row['keypoint_agent_position_drift'] <= TOL and
                             row['source_vs_keypoint_contact_match'] and
                             row['source_vs_maintained_contact_match'] and row['policy_input_dim']==20
                             else 'incompatible')
            rows.append(row)
            print(json.dumps({k:row[k] for k in ('seed','status','max_source_vs_maintained_drift',
                                                'policy_input_dim','source_vs_maintained_contact_match')}),
                  flush=True)
        finally:
            original.close()
            keypoint.close()
            maintained.close()
    (OUT/'assessment.json').write_text(json.dumps(dict(status='completed', tolerance=TOL,
                                  steps_per_case=5, cases=rows), indent=2, allow_nan=False)+'\n')


if __name__ == '__main__':
    main()
