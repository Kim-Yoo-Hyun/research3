"""Small paired contact-task feasibility audit. Execute inside the study Docker image."""
import argparse
import csv
import hashlib
import json
import time
from pathlib import Path

import numpy as np
from mani_skill.utils.structs.pose import Pose

from task_audit_env import make_env, native_metric, observe

ROOT = Path('/output')
SEEDS = range(46000, 46008)
ROUTES = ('hold', 'feedback', 'fixed_reference')
HORIZON = {'push_t': 100, 'roll_ball': 80}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')


def yaw(q):
    w, x, y, z = q
    return float(np.arctan2(2 * (w*z + x*y), 1 - 2 * (y*y + z*z)))


class Controller:
    def __init__(self, task, reference):
        self.task = task
        self.reference = reference
        self.phase = 'lift'

    def action(self, state):
        obj = self.reference['object'][:3]
        goal = self.reference['goal'][:3]
        tcp = state['tcp'][:3]
        direction = goal[:2] - obj[:2]
        direction /= max(float(np.linalg.norm(direction)), 1e-6)
        radius = 0.085 if self.task == 'push_t' else 0.14
        contact_z = 0.03 if self.task == 'push_t' else 0.045
        safe_z = 0.15
        behind = np.r_[obj[:2] - radius * direction, contact_z]
        if self.phase == 'lift' and tcp[2] >= safe_z - 0.025:
            self.phase = 'approach'
        if self.phase == 'approach' and np.linalg.norm(tcp[:2] - behind[:2]) < 0.035:
            self.phase = 'lower'
        if self.phase == 'lower' and np.linalg.norm(tcp[:2] - behind[:2]) < 0.045 and tcp[2] <= contact_z + 0.02:
            self.phase = 'push'
        if self.phase == 'lift':
            target = np.r_[tcp[:2], safe_z]
        elif self.phase == 'approach':
            target = np.r_[behind[:2], safe_z]
        elif self.phase == 'lower':
            target = behind
        else:
            # Move through the object toward its goal; reference is live or frozen at t=0.
            target = np.r_[goal[:2] - 0.035 * direction, contact_z]
        world_xyz = (target - tcp) / 0.1
        if self.task == 'roll_ball':
            # Panda base has native -90 degree yaw; PDEE delta is expressed in its root frame.
            root_xyz = np.array([-world_xyz[1], world_xyz[0], world_xyz[2]])
            return np.r_[np.clip(root_xyz, -0.25, 0.25), -1.].astype(np.float32)
        return np.clip(world_xyz, -0.25, 0.25).astype(np.float32)


def set_object_to_goal(env, task, state):
    actor = env.unwrapped.tee if task == 'push_t' else env.unwrapped.ball
    p = state['goal'][:3].copy()
    p[2] = state['object'][2]
    q = state['goal'][3:].copy() if task == 'push_t' else state['object'][3:].copy()
    actor.set_pose(Pose.create_from_pq(p=p, q=q))


def smoke(task, attempt):
    out = ROOT / attempt
    out.mkdir(exist_ok=True)
    env = make_env(task)
    rows = []
    try:
        for seed in SEEDS:
            env.reset(seed=seed)
            initial = observe(env, task)
            initial_metric, initial_success = native_metric(env, task)
            set_object_to_goal(env, task, initial)
            goal_metric, goal_success = native_metric(env, task)
            if not goal_success:
                raise AssertionError(f'goal-pose native label failed: {task} {seed} {goal_metric}')
            env.reset(seed=seed)
            repeat = observe(env, task)
            for key in ('object', 'goal', 'tcp'):
                if not np.allclose(initial[key], repeat[key], atol=1e-5):
                    raise AssertionError(f'reset mismatch: {task} {seed} {key}')
            for route in ROUTES:
                env.reset(seed=seed)
                state = observe(env, task)
                reference = {k: v.copy() for k, v in state.items()}
                ctrl = Controller(task, reference)
                states = {k: [v] for k, v in state.items()}
                metrics = []
                success = []
                actions = []
                phases = []
                value, passed = native_metric(env, task)
                metrics.append(value)
                success.append(passed)
                started = time.perf_counter()
                for step in range(HORIZON[task]):
                    if route == 'hold':
                        action = np.zeros(3 if task == 'push_t' else 4, np.float32)
                        phase = 'hold'
                    else:
                        if route == 'feedback':
                            ctrl.reference = state
                        action = ctrl.action(state)
                        phase = ctrl.phase
                    env.step(action)
                    state = observe(env, task)
                    value, passed = native_metric(env, task)
                    actions.append(action)
                    phases.append(phase)
                    for key in states:
                        states[key].append(state[key])
                    metrics.append(value)
                    success.append(passed)
                elapsed = time.perf_counter() - started
                trace = out / f'{task}_{seed}_{route}.npz'
                np.savez_compressed(trace, **{k: np.asarray(v) for k, v in states.items()},
                                    actions=np.asarray(actions), metric=np.asarray(metrics),
                                    success=np.asarray(success, np.bool_), phase=np.asarray(phases))
                obj = np.asarray(states['object'])
                row = dict(task=task, seed=seed, route=route, trace=trace.name,
                           sha256=sha256(trace), steps=HORIZON[task],
                           initial_metric=initial_metric, initial_success=initial_success,
                           goal_pose_metric=goal_metric, goal_pose_success=goal_success,
                           final_metric=value, best_metric=max(metrics) if task == 'push_t' else min(metrics),
                           final_success=passed, any_success=any(success),
                           object_xy_displacement=float(np.linalg.norm(obj[-1, :2] - obj[0, :2])),
                           object_yaw_change=abs(yaw(obj[-1, 3:]) - yaw(obj[0, 3:])),
                           elapsed_seconds=elapsed, push_phase_steps=phases.count('push'))
                rows.append(row)
                print(json.dumps({k: row[k] for k in ('task', 'seed', 'route', 'final_metric', 'final_success', 'object_xy_displacement')}), flush=True)
        save_json(out / 'episodes.json', dict(task=task, seeds=list(SEEDS), routes=ROUTES,
                                              rows=rows, variant='collision-only native task subclass',
                                              horizon=HORIZON[task]))
    finally:
        env.close()


def verify(attempt, push_attempt, ball_attempt):
    out = ROOT / attempt
    out.mkdir(exist_ok=True)
    all_rows = []
    checks = 0
    for task, source_attempt in (('push_t', push_attempt), ('roll_ball', ball_attempt)):
        source = ROOT / source_attempt
        manifest = json.loads((source / 'episodes.json').read_text())
        assert manifest['task'] == task and len(manifest['rows']) == len(SEEDS)*len(ROUTES)
        groups = {}
        for row in manifest['rows']:
            assert row['task'] == task and row['seed'] in SEEDS and row['route'] in ROUTES
            assert row['goal_pose_success']
            path = source / row['trace']
            assert sha256(path) == row['sha256']
            with np.load(path, allow_pickle=False) as trace:
                n = HORIZON[task]
                assert trace['object'].shape == (n+1, 7)
                assert trace['goal'].shape == (n+1, 7)
                assert trace['tcp'].shape == (n+1, 7)
                assert trace['actions'].shape == (n, 3 if task == 'push_t' else 4)
                assert trace['metric'].shape == (n+1,) and trace['success'].shape == (n+1,)
                assert all(np.isfinite(trace[k]).all() for k in ('object', 'goal', 'tcp', 'actions', 'metric'))
                expected = trace['metric'] >= 0.90 if task == 'push_t' else trace['metric'] < 0.1
                assert np.array_equal(trace['success'], expected)
                assert bool(trace['success'][-1]) == row['final_success']
                assert np.isclose(float(trace['metric'][-1]), row['final_metric'])
                groups.setdefault(row['seed'], []).append((trace['object'][0].copy(), trace['goal'][0].copy(),
                                                             trace['tcp'][0].copy()))
            checks += 1
            all_rows.append(row)
        for seed, initial in groups.items():
            assert len(initial) == 3
            for a in initial[1:]:
                assert all(np.allclose(x, y, atol=1e-5) for x, y in zip(initial[0], a)), (task, seed)
    summary = {}
    for task in HORIZON:
        summary[task] = {}
        for route in ROUTES:
            rows = [r for r in all_rows if r['task'] == task and r['route'] == route]
            summary[task][route] = dict(final_success=sum(r['final_success'] for r in rows),
                                        any_success=sum(r['any_success'] for r in rows),
                                        mean_initial_metric=float(np.mean([r['initial_metric'] for r in rows])),
                                        mean_final_metric=float(np.mean([r['final_metric'] for r in rows])),
                                        mean_best_metric=float(np.mean([r['best_metric'] for r in rows])),
                                        mean_object_xy_displacement=float(np.mean([r['object_xy_displacement'] for r in rows])),
                                        mean_elapsed_seconds=float(np.mean([r['elapsed_seconds'] for r in rows])),
                                        mean_push_phase_steps=float(np.mean([r['push_phase_steps'] for r in rows])))
    with (out / 'episodes.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=all_rows[0].keys())
        writer.writeheader()
        writer.writerows(all_rows)
    save_json(out / 'verification.json', dict(status='passed', trace_checks=checks,
                                               paired_seeds=8, summary=summary,
                                               source_attempts=dict(push_t=push_attempt, roll_ball=ball_attempt)))
    print(json.dumps(summary, indent=2), flush=True)


def diagnose(attempt, push_attempt, ball_attempt):
    out = ROOT / attempt
    out.mkdir(exist_ok=True)
    rows = []
    for task, source in (('push_t', push_attempt), ('roll_ball', ball_attempt)):
        for seed in SEEDS:
            path = ROOT / source / f'{task}_{seed}_feedback.npz'
            with np.load(path, allow_pickle=False) as trace:
                obj, goal, tcp, phase = (trace[k] for k in ('object', 'goal', 'tcp', 'phase'))
                direction = goal[0, :2] - obj[0, :2]
                direction /= np.linalg.norm(direction)
                behind = obj[0, :2] - (0.065 if task == 'push_t' else 0.075)*direction
                row = dict(task=task, seed=seed, object_initial=obj[0, :3].tolist(),
                           object_final=obj[-1, :3].tolist(), goal=goal[0, :3].tolist(),
                           tcp_initial=tcp[0, :3].tolist(), tcp_final=tcp[-1, :3].tolist(),
                           tcp_min=tcp[:, :3].min(0).tolist(), tcp_max=tcp[:, :3].max(0).tolist(),
                           behind=behind.tolist(), min_tcp_behind_xy=float(np.linalg.norm(tcp[:, :2]-behind, axis=1).min()),
                           min_tcp_object_xy=float(np.linalg.norm(tcp[:, :2]-obj[:, :2], axis=1).min()),
                           push_steps=int(np.sum(phase == 'push')))
                rows.append(row)
    save_json(out / 'diagnosis.json', rows)
    print(json.dumps(rows, indent=2), flush=True)


def demo(attempt, state_initialize=False):
    import h5py
    import torch
    out = ROOT / attempt
    out.mkdir(exist_ok=True)
    dataset = ROOT / 'demos/extracted/trajectory.none.pd_ee_delta_pos.physx_cuda.h5'
    metadata = json.loads(dataset.with_suffix('.json').read_text())
    assert metadata['env_info']['env_id'] == 'PushT-v1'
    assert metadata['env_info']['env_kwargs']['control_mode'] == 'pd_ee_delta_pos'
    rows = []
    with h5py.File(dataset, 'r') as h5:
        layout = {}
        first = h5[f"traj_{metadata['episodes'][0]['episode_id']}"]
        first.visititems(lambda name, obj: layout.update({name: list(obj.shape)}) if isinstance(obj, h5py.Dataset) else None)
        print(json.dumps(dict(episodes=len(metadata['episodes']), source_commit=metadata['commit_info']['commit_id'],
                              first_layout=layout), indent=2), flush=True)
        env = make_env('push_t')
        try:
            for episode in metadata['episodes'][:8]:
                key = f"traj_{episode['episode_id']}"
                actions = np.asarray(h5[key]['actions'], dtype=np.float32)
                assert actions.ndim == 2 and actions.shape[1] == 3
                assert actions.shape[0] == episode['elapsed_steps']
                assert np.isfinite(actions).all()
                env.reset(seed=episode['episode_seed'])
                if state_initialize:
                    states = h5[key]['env_states']
                    initial_state = {
                        category: {name: torch.as_tensor(states[category][name][0], dtype=torch.float32).unsqueeze(0)
                                   for name in states[category]}
                        for category in ('actors', 'articulations')
                    }
                    env.unwrapped.set_state_dict(initial_state)
                first_obs = observe(env, 'push_t')
                if state_initialize:
                    expected_pose = np.asarray(h5[key]['env_states']['actors']['Tee'][0, :7])
                    assert np.allclose(first_obs['object'], expected_pose, atol=1e-4)
                initial_metric, _ = native_metric(env, 'push_t')
                any_success = False
                for action in actions:
                    env.step(action)
                    _, native_success = native_metric(env, 'push_t')
                    any_success |= native_success
                final_metric, final_success = native_metric(env, 'push_t')
                row = dict(episode_id=episode['episode_id'], seed=episode['episode_seed'],
                           source_success=episode['success'], steps=len(actions),
                           initial_object=first_obs['object'].tolist(),
                           initial_goal=first_obs['goal'].tolist(),
                           replay_initial_metric=initial_metric, replay_final_metric=final_metric,
                           replay_final_success=final_success, replay_any_success=any_success)
                rows.append(row)
                print(json.dumps({k: row[k] for k in ('episode_id','steps','replay_initial_metric','replay_final_metric','replay_final_success')}), flush=True)
        finally:
            env.close()
    result = dict(status='completed', state_initialize=state_initialize,
                  source_commit=metadata['commit_info']['commit_id'],
                  pinned_task_commit='a4a4f9272ad64b1564035874b605ceb687b63ed8',
                  source_episode_count=len(metadata['episodes']), replay_count=len(rows),
                  replay_success=sum(r['replay_final_success'] for r in rows),
                  h5_layout=layout, rows=rows)
    save_json(out / 'demo.json', result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=('smoke', 'diagnose', 'verify', 'demo'))
    parser.add_argument('--attempt', required=True)
    parser.add_argument('--task', choices=tuple(HORIZON))
    parser.add_argument('--push', default='push_t1')
    parser.add_argument('--ball', default='roll_ball1')
    parser.add_argument('--state-initialize', action='store_true')
    args = parser.parse_args()
    if args.stage == 'smoke':
        assert args.task
        smoke(args.task, args.attempt)
    elif args.stage == 'verify':
        verify(args.attempt, args.push, args.ball)
    elif args.stage == 'diagnose':
        diagnose(args.attempt, args.push, args.ball)
    else:
        demo(args.attempt, args.state_initialize)
