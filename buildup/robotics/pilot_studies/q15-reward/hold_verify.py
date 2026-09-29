"""Independent CPU reconstruction from saved state/action; no simulator/policy imports."""
import csv
import hashlib
import itertools
import json
from pathlib import Path
import shutil
import numpy as np

OUT, INPUT = Path('/output'), Path('/input')
STATE_KEYS = ['obs', 'qpos', 'qvel', 'cube_pose', 'cube_velocity', 'cube_angular_velocity', 'goal', 'tcp_pose']
STEP_KEYS = ['action', 'reward', 'success', 'is_obj_placed', 'is_robot_static', 'is_grasped',
             'terminated', 'truncated', 'elapsed_steps']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def equal(actual, expected, label):
    assert np.array_equal(actual, expected), label


def near(actual, expected, label, atol=5e-7):
    assert np.allclose(actual, expected, atol=atol, rtol=0), (label, float(np.max(np.abs(actual-expected))))


def tcp_relative(data):
    # SAPIEN raw_pose uses [x,y,z,qw,qx,qy,qz]; inverse unit-quaternion rotation.
    v = data['cube_pose'][..., :3] - data['tcp_pose'][..., :3]
    q = data['tcp_pose'][..., 3:]
    near(np.linalg.norm(q, axis=-1), np.ones(q.shape[:-1]), 'TCP unit quaternion', atol=1e-5)
    u = q[..., 1:]
    return v - 2*q[..., :1]*np.cross(u, v) + 2*np.cross(u, np.cross(u, v))


def main():
    archive = OUT / 'verification_source'
    archive.mkdir(exist_ok=True)
    source = Path('/study/hold_verify.py')
    saved = archive / source.name
    if saved.exists():
        assert saved.read_bytes() == source.read_bytes(), 'Preserve previous verifier before changes'
    else:
        shutil.copyfile(source, saved)
    status = json.loads((OUT / 'run_status.json').read_text())
    assert status['status'] == 'completed' and len(status['evaluation']) == 18
    assert not status['training'] and status['reset_seed'] == 2026091901
    for record in json.loads((OUT / 'inputs.json').read_text()):
        path = INPUT / record['path']
        assert path.stat().st_size == record['bytes'] and sha(path) == record['sha256']
    checks = dict(input_files=45, checkpoints=9, label_elements=0, reward_elements=0,
                  drive_target_elements=0, pairs=0, valid_prefix_pairs=0, clipped_arm_components=0,
                  hold_control_steps=0, unchanged_prior_conditions=0)
    rows, pairs, prior_differences, invalid_prefixes = [], [], [], []
    nominal_meta = json.loads((INPUT / 'evaluation/native_101_u195_d1_f1.json').read_text())
    ref_initial = None
    for variant, seed in itertools.product(['native', 'no_grasp', 'half'], [101, 202, 303]):
        traces = {}
        checkpoint_meta = json.loads((INPUT / 'fits' / f'{variant}_{seed}' / 'checkpoint_195.json').read_text())
        for route in ['continued', 'hold']:
            name = f'{variant}_{seed}_{route}'
            path = OUT / 'evaluation' / name
            m = json.loads(path.with_suffix('.json').read_text())
            d = dict(np.load(path.with_suffix('.npz'), allow_pickle=False))
            traces[route] = d
            assert m['trace_sha256'] == sha(path.with_suffix('.npz'))
            assert m['checkpoint_sha256'] == checkpoint_meta['sha256']
            assert (m['variant'], m['training_seed'], m['route']) == (variant, seed, route)
            assert (m['seed'], m['num_envs'], m['steps'], m['physical_steps']) == (2026091901, 32, 50, 250)
            for key in ['sim_config', 'controllers', 'physical', 'cube_half_size', 'goal_threshold', 'source_commit']:
                assert m['config'][key] == nominal_meta['config'][key], (name, key)
            assert m['config']['goal_threshold'] == .025
            assert d['qpos'].shape == (51,32,9) and d['success'].shape == (50,32)
            assert d['action'].shape == (50,32,8) and np.max(np.abs(d['action'])) <= 1
            for key, value in d.items():
                assert np.isfinite(value).all(), (name, key)
            if ref_initial is None:
                ref_initial = {k:d[k][0] for k in STATE_KEYS}
            for key in STATE_KEYS:
                equal(d[key][0], ref_initial[key], (name,'initial',key))
            equal(d['elapsed_steps'], np.broadcast_to(np.arange(1,51)[:,None], (50,32)), 'elapsed')
            assert not d['truncated'][:-1].any() and d['truncated'][-1].all()
            distance = np.linalg.norm(d['cube_pose'][1:,:,:3] - d['goal'][1:], axis=-1)
            speed = np.max(np.abs(d['qvel'][1:,:,:7]), axis=-1)
            placed, static = distance <= .025, speed <= .2
            success = placed & static
            for key, expected in [('success',success), ('is_obj_placed',placed), ('is_robot_static',static)]:
                equal(d[key], expected, (name,key)); checks['label_elements'] += expected.size
            reach = 1-np.tanh(5*np.linalg.norm(d['cube_pose'][1:,:,:3]-d['tcp_pose'][1:,:,:3],axis=-1))
            place = 1-np.tanh(5*distance)
            shaping_static = 1-np.tanh(5*np.linalg.norm(d['qvel'][1:,:,:7],axis=-1))
            reward = (reach + d['is_grasped']*(1+place) + placed*shaping_static)/5
            reward = np.where(success, 1, reward)
            if variant == 'no_grasp': reward = reward-.2*d['is_grasped']*(~success)
            if variant == 'half': reward = reward*.5
            near(d['reward'], reward, (name,'reward'), atol=1e-6)
            checks['reward_elements'] += reward.size
            # Original controller preprocess: normalized [-1,1] -> delta [-.1,.1].
            expected_target = d['qpos'][:-1,:,:7] + (-.1 + (d['action'][...,:7]+1)*.1)
            near(d['target_arm'], expected_target, (name,'arm target'))
            expected_gripper = -.01 + (d['action'][...,7:8]+1)*.025
            near(d['target_gripper'], np.repeat(expected_gripper,2,axis=-1), (name,'gripper target'), atol=2e-8)
            equal(d['target_buffer'][...,:7], d['target_arm'], 'arm drive buffer')
            equal(d['target_buffer'][...,7:], d['target_gripper'], 'gripper drive buffer')
            checks['drive_target_elements'] += d['target_buffer'].size
            relative = tcp_relative(d)
            for i in range(32):
                events = np.flatnonzero(success[:,i])
                first = int(events[0]+1) if len(events) else None
                active = np.zeros(50,dtype=bool)
                if route == 'hold' and first is not None:
                    active[first:] = True
                equal(d['active'][:,i], active, (name,i,'latching'))
                equal(d['action'][~active,i], d['policy_action'][~active,i], (name,i,'policy action'))
                clipped, tracking, reference_error, drift, first_loss, uninterrupted = 0, None, None, None, None, None
                if first is not None:
                    q = d['qpos'][first,i,:7]
                    g = d['action'][first-1,i,7]
                    if first < 50:
                        equal(d['q_hold'][first:,i], np.broadcast_to(q,(50-first,7)), 'saved reference')
                        equal(d['gripper_hold'][first:,i], np.full(50-first,g,dtype=d['action'].dtype), 'saved gripper')
                    drift = float(np.linalg.norm(relative[-1,i]-relative[first,i])*1000)
                    losses = np.flatnonzero(~success[first:,i])
                    first_loss = int(first+losses[0]+1) if len(losses) else None
                    uninterrupted = int(losses[0]) if len(losses) else 50-first
                    if active.any():
                        raw = (q-d['qpos'][:-1,i,:7][active])/.1
                        near(d['action'][active,i,:7], np.clip(raw,-1,1), (name,i,'hold action'), atol=1e-7)
                        equal(d['action'][active,i,7], np.full(active.sum(),g,dtype=d['action'].dtype), 'gripper hold')
                        clipped = int(np.count_nonzero(np.abs(raw)>1))
                        tracking = float(np.max(np.abs(d['qpos'][1:,i,:7][active]-q)))
                        reference_error = float(np.max(np.abs(d['target_arm'][active,i]-q)))
                        if not clipped:
                            near(d['target_arm'][active,i],np.broadcast_to(q,(active.sum(),7)), 'fixed reference')
                checks['clipped_arm_components'] += clipped
                checks['hold_control_steps'] += int(active.sum())
                rows.append(dict(variant=variant,training_seed=seed,route=route,initial_state=i,
                    success_at_end=int(success[-1,i]),success_once=int(bool(len(events))),first_success_step=first,
                    first_success_at_final_step=first==50,intervention_steps=int(active.sum()),
                    first_loss_step=first_loss,uninterrupted_post_success_steps=uninterrupted,
                    successful_post_success_steps=int(success[first:,i].sum()) if first is not None else None,
                    final_goal_distance_mm=float(distance[-1,i]*1000),final_static=bool(static[-1,i]),
                    final_grasp=bool(d['is_grasped'][-1,i]),final_max_arm_velocity_rad_s=float(speed[-1,i]),
                    tcp_relative_displacement_mm=drift,max_hold_tracking_error_rad=tracking,
                    max_hold_reference_error_rad=reference_error,clipped_arm_components=clipped))
        c,h = traces['continued'],traces['hold']
        old = dict(np.load(INPUT/'evaluation'/f'{variant}_{seed}_u195_d1_f1.npz',allow_pickle=False))
        diff = {}
        for key in STATE_KEYS+STEP_KEYS:
            if not np.array_equal(c[key],old[key]):
                diff[key] = dict(elements=int(np.count_nonzero(c[key]!=old[key])),
                                 max_abs=float(np.max(np.abs(c[key].astype(float)-old[key].astype(float)))))
        if diff: prior_differences.append(dict(variant=variant,seed=seed,differences=diff))
        else: checks['unchanged_prior_conditions'] += 1
        for i in range(32):
            events = np.flatnonzero(c['success'][:,i])
            first = int(events[0]+1) if len(events) else 50
            differences = [key for key in STATE_KEYS if not np.array_equal(c[key][:first+1,i],h[key][:first+1,i])]
            differences += [key for key in STEP_KEYS if not np.array_equal(c[key][:first,i],h[key][:first,i])]
            valid = not differences
            checks['pairs'] += 1; checks['valid_prefix_pairs'] += int(valid)
            if not valid: invalid_prefixes.append(dict(variant=variant,seed=seed,initial_state=i,keys=differences))
            cr = next(r for r in rows if (r['variant'],r['training_seed'],r['route'],r['initial_state'])==(variant,seed,'continued',i))
            hr = next(r for r in rows if (r['variant'],r['training_seed'],r['route'],r['initial_state'])==(variant,seed,'hold',i))
            pairs.append(dict(variant=variant,training_seed=seed,initial_state=i,prefix_valid=valid,
                improved=bool(valid and not cr['success_at_end'] and hr['success_at_end']),
                worsened=bool(valid and cr['success_at_end'] and not hr['success_at_end']),
                continued=cr,hold=hr))
    assert len(rows)==576 and len(pairs)==288
    cells=[]
    for variant in ['native','no_grasp','half']:
        rr=[r for r in rows if r['variant']==variant]
        pp=[p for p in pairs if p['variant']==variant]
        cells.append(dict(variant=variant,episodes_per_route=96,independent_training_seeds=3,
            valid_pairs=sum(p['prefix_valid'] for p in pp),improved=sum(p['improved'] for p in pp),
            worsened=sum(p['worsened'] for p in pp),
            routes={route:dict(end=sum(r['success_at_end'] for r in rr if r['route']==route),
                              once=sum(r['success_once'] for r in rr if r['route']==route),
                              end_by_seed={str(s):sum(r['success_at_end'] for r in rr if r['route']==route and r['training_seed']==s) for s in [101,202,303]}) for route in ['continued','hold']}))
    with (OUT/'episodes.csv').open('w') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    summary=dict(exploratory=True,episodes=576,paired_initial_states=288,cells=cells,
                 execution_seconds=status['seconds'],prior_differences=prior_differences,
                 invalid_prefixes=invalid_prefixes,first_success_at_final_step=sum(r['first_success_at_final_step'] for r in rows),
                 boundary='Oracle-triggered, same observed states, nominal-only, finite-horizon comparison; no new training.')
    save(OUT/'summary.json',summary)
    save(OUT/'cases.json',dict(changed=[p for p in pairs if p['improved'] or p['worsened']],
                              remaining_failures=[p for p in pairs if not p['hold']['success_at_end']]))
    verification=dict(status='passed' if not invalid_prefixes else 'paired interpretation unavailable',**checks,
                      reward_tolerance=1e-6,controller_tolerance=5e-7,prefix_tolerance=0)
    save(OUT/'verification.json',verification)
    save(OUT/'manifest.json',[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p))
         for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='manifest.json'])
    print(json.dumps(verification)); print(json.dumps(summary))


if __name__=='__main__': main()
