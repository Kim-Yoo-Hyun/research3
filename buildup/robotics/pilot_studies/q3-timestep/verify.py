"""Independent CPU reconstruction from raw trajectories; never import the rollout adapter."""
import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--attempt', required=True)
    args = parser.parse_args()
    out = Path('/output') / args.attempt
    status = json.loads((out / 'run_status.json').read_text())
    assert status['status'] == 'completed' and len(status['conditions']) == 12
    names = [f'{m}_{f}_{r}' for m in ['closed', 'replay'] for f in [100, 200, 400] for r in [0, 1]]
    data = {name: dict(np.load(out / f'{name}.npz', allow_pickle=False)) for name in names}
    meta = {name: json.loads((out / f'{name}.json').read_text()) for name in names}
    ref = data['closed_100_0']
    outcomes, rows = {}, []
    checks = dict(conditions=0, reconstructed_step_labels=0, matching_initial_arrays=0,
                  replay_target_elements=0, buffer_target_elements=0, reconstructed_action_targets=0)
    fixed_meta = ['controller_configs', 'cube_mass', 'cube_half_size', 'robot_materials',
                  'checkpoint_sha256', 'official_ppo_sha256', 'goal_threshold', 'target_indices']
    ref_config = dict(meta['closed_100_0']['sim_config'])
    ref_config.pop('sim_freq')
    for name in names:
        d, m = data[name], meta[name]
        assert digest(out / f'{name}.npz') == m['trace_sha256']
        assert m['seed'] == 20260918 and m['environments'] == 8 and m['control_steps'] == 50
        assert m['control_frequency'] == 20 and m['actual_physics_steps'] == 50 * m['frequency'] // 20
        assert np.isclose(m['actual_physics_timestep'], 1 / m['frequency'], rtol=1e-6, atol=0)
        cfg = dict(m['sim_config'])
        assert cfg.pop('sim_freq') == m['frequency'] and cfg == ref_config
        for key in fixed_meta:
            assert m[key] == meta['closed_100_0'][key], (name, key)
        assert all(not c['interpolate'] for c in m['controller_configs'].values())
        for key, value in d.items():
            assert np.isfinite(value).all(), (name, key)
        snapshot_keys = ['obs', 'qpos', 'qvel', 'cube_pose', 'cube_velocity', 'cube_angular_velocity', 'goal']
        snapshot_keys += [key for key in d if key.startswith('state/')]
        for key in snapshot_keys:
            assert d[key].shape[:2] == (51, 8), (name, key, d[key].shape)
            assert np.array_equal(d[key][0], ref[key][0]), (name, key)
            checks['matching_initial_arrays'] += 1
        assert np.array_equal(d['control_time'], np.arange(51) / 20)
        assert np.array_equal(d['physics_steps'], np.arange(51) * (m['frequency'] // 20))
        assert np.array_equal(d['elapsed_steps'], np.broadcast_to(np.arange(1, 51)[:, None], (50, 8)))
        assert d['truncated'][-1].all() and not d['truncated'][:-1].any()
        distance = np.sqrt(np.square(d['cube_pose'][1:, :, :3] - d['goal'][1:]).sum(axis=-1))
        speed = np.abs(d['qvel'][1:, :, :7]).max(axis=-1)
        placed, static = distance <= 0.025, speed <= 0.2
        success = placed & static
        for key, values in [('is_obj_placed', placed), ('is_robot_static', static), ('success', success)]:
            assert np.array_equal(values, d[f'official/{key}']), (name, key)
            checks['reconstructed_step_labels'] += values.size
        assert np.array_equal(success, d['terminated'])
        for key, indices in m['target_indices'].items():
            targets = d[f'target/{key}']
            assert np.array_equal(d['target/buffer'][:, :, indices], targets)
            checks['buffer_target_elements'] += targets.size
            if m['mode'] == 'replay':
                assert np.array_equal(targets, ref[f'target/{key}'])
                checks['replay_target_elements'] += targets.size
        if m['mode'] == 'closed':
            action = np.clip(d['action'], -1, 1)
            arm = d['qpos'][:-1, :, :7] + action[:, :, :7] * 0.1
            assert np.allclose(arm, d['target/arm'], rtol=0, atol=3e-7)
            gc = m['controller_configs']['gripper']
            grip = (action[:, :, 7:8] + 1) * (gc['upper'] - gc['lower']) / 2 + gc['lower']
            assert np.allclose(np.repeat(grip, 2, axis=-1), d['target/gripper'], rtol=0, atol=3e-8)
            checks['reconstructed_action_targets'] += d['target/buffer'].size
        outcomes[name] = dict(end=success[-1], once=success.any(axis=0))
        for i in range(8):
            event = np.flatnonzero(success[:, i])
            rows.append(dict(condition=name, mode=m['mode'], frequency=m['frequency'], repeat=m['repeat'],
                             initial_state=i, success_at_end=bool(success[-1, i]),
                             success_once=bool(success[:, i].any()), final_goal_distance_mm=float(distance[-1, i]*1000),
                             final_arm_speed=float(speed[-1, i]),
                             first_success_control_step=int(event[0]+1) if len(event) else None))
        checks['conditions'] += 1

    def compare(a, b, kind):
        left, right = data[a], data[b]
        dp = np.linalg.norm(left['cube_pose'][1:, :, :3] - right['cube_pose'][1:, :, :3], axis=-1)
        dq = left['qpos'][1:] - right['qpos'][1:]
        dt = left['target/buffer'] - right['target/buffer']
        peak_step, peak_state = np.unravel_index(np.argmax(dp), dp.shape)
        return dict(kind=kind, left=a, right=b,
                    end_disagreements=np.flatnonzero(outcomes[a]['end'] != outcomes[b]['end']).tolist(),
                    once_disagreements=np.flatnonzero(outcomes[a]['once'] != outcomes[b]['once']).tolist(),
                    cube_rms_mm=float(np.sqrt(np.mean(dp**2))*1000), cube_max_mm=float(dp.max()*1000),
                    cube_final_per_state_mm=(dp[-1]*1000).tolist(),
                    arm_qpos_rmse_rad=float(np.sqrt(np.mean(dq[:, :, :7]**2))),
                    gripper_qpos_rmse_m=float(np.sqrt(np.mean(dq[:, :, 7:]**2))),
                    arm_target_rmse_rad=float(np.sqrt(np.mean(dt[:, :, :7]**2))),
                    gripper_target_rmse_m=float(np.sqrt(np.mean(dt[:, :, 7:]**2))),
                    peak_control_step=int(peak_step+1), peak_initial_state=int(peak_state))

    comparisons = []
    for mode in ['closed', 'replay']:
        for f in [100, 200, 400]:
            comparisons.append(compare(f'{mode}_{f}_0', f'{mode}_{f}_1', 'repeat'))
        for a, b in itertools.combinations([100, 200, 400], 2):
            for repeat in [0, 1]:
                comparisons.append(compare(f'{mode}_{a}_{repeat}', f'{mode}_{b}_{repeat}', 'frequency'))
    for repeat in [0, 1]:
        comparisons.append(compare('closed_100_0', f'replay_100_{repeat}', 'reference_replay'))
    summary = dict(episodes=96, independent_initial_states=8, primary='success_at_end',
                   exploratory=True, conditions=[dict(condition=name,
                       success_at_end=int(outcomes[name]['end'].sum()), success_once=int(outcomes[name]['once'].sum()),
                       end_states=np.flatnonzero(outcomes[name]['end']).tolist(),
                       once_states=np.flatnonzero(outcomes[name]['once']).tolist()) for name in names],
                   comparisons=comparisons,
                   final_goal_distance_range_mm=[min(r['final_goal_distance_mm'] for r in rows),
                                                 max(r['final_goal_distance_mm'] for r in rows)])
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    with (out / 'episodes.csv').open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (out / 'verify_executed.py').write_text(Path(__file__).read_text())
    (out / 'verification.json').write_text(json.dumps(dict(status='PASS', **checks,
        verifier_sha256=digest(Path(__file__)),
        boundary='Raw-state success reconstruction and target/time/config checks; no real-world or ranking claim'), indent=2) + '\n')
    files = sorted(p for p in out.iterdir() if p.is_file() and p.name != 'checksums.txt')
    (out / 'checksums.txt').write_text(''.join(f'{digest(p)}  {p.name}\n' for p in files))
    print(json.dumps({'status': 'PASS', 'checks': checks, 'episodes': summary['episodes'],
                      'final_goal_distance_range_mm': summary['final_goal_distance_range_mm']}), flush=True)


if __name__ == '__main__':
    main()
