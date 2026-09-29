"""Replay source-matched PushT demonstrations in a separate CPU Docker image."""
import argparse
import hashlib
import json
import os
from pathlib import Path

import h5py
import numpy as np
import torch

from compat_env import make_env, native_metric, observe

OUT = Path('/output')
H5 = Path('/demos/trajectory.none.pd_ee_delta_pos.physx_cuda.h5')
META = H5.with_suffix('.json')
SOURCE_COMMIT = 'baab60ede2e89167c1b7aaed41a9aa8e690a9d1e'
DEVICE = os.environ.get('Q16_COMPAT_DEVICE', 'cpu')
NATIVE = os.environ.get('Q16_COMPAT_NATIVE') == '1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')


def restore_initial(env, group, frame=0):
    states = group['env_states']
    initial = {
        category: {name: torch.as_tensor(states[category][name][frame], dtype=torch.float32,
                                         device=env.unwrapped.device).unsqueeze(0)
                   for name in states[category]}
        for category in ('actors', 'articulations')
    }
    env.unwrapped.set_state_dict(initial)


def audit_data(attempt, count):
    """Reconstruct state observations; this is not closed-loop replay."""
    out = OUT / attempt
    out.mkdir(exist_ok=True)
    checkpoint = Path('/demos/ppo_pd_ee_delta_pos_ckpt.pt')
    weights = torch.load(checkpoint, map_location='cpu', weights_only=True)
    actor_input = int(weights['actor_mean.0.weight'].shape[1])
    actor_output = int(weights['actor_mean.6.weight'].shape[0])
    meta = json.loads(META.read_text())
    env = make_env('push_t', device=DEVICE, obs_mode='state', native=NATIVE)
    rows = []
    try:
        with h5py.File(H5, 'r') as h5:
            for item in meta['episodes'][:count]:
                group = h5[f"traj_{item['episode_id']}"]
                actions = np.asarray(group['actions'], np.float32)
                env.reset(seed=item['episode_seed'])
                observations = []
                for frame in range(len(actions)):
                    restore_initial(env, group, frame)
                    obs = env.unwrapped.get_obs()
                    observations.append(obs.detach().cpu().numpy().reshape(-1))
                observations = np.asarray(observations, np.float32)
                assert observations.shape == (len(actions), actor_input)
                assert actions.shape == (len(actions), actor_output)
                assert np.isfinite(observations).all() and np.isfinite(actions).all()
                state = group['env_states']
                articulation = np.asarray(state['articulations']['panda_stick'][:len(actions)], np.float32)
                tee = np.asarray(state['actors']['Tee'][:len(actions), :7], np.float32)
                goal = np.asarray(state['actors']['goal_Tee'][:len(actions), :3], np.float32)
                assert np.allclose(observations[:, :7], articulation[:, 13:20], atol=1e-4)
                assert np.allclose(observations[:, 7:14], articulation[:, 20:27], atol=1e-4)
                assert np.allclose(observations[:, -10:-7], goal, atol=1e-4)
                assert np.allclose(observations[:, -7:], tee, atol=1e-4)
                path = out / f"traj_{item['episode_id']}.npz"
                np.savez_compressed(path, observations=observations, actions=actions)
                rows.append(dict(episode_id=item['episode_id'], rows=len(actions),
                                 observation_dim=actor_input, action_dim=actor_output,
                                 trace=path.name, sha256=sha(path)))
                print(json.dumps(rows[-1]), flush=True)
    finally:
        env.close()
    save(out / 'data_audit.json', dict(status='completed', source_commit=SOURCE_COMMIT,
                                      device=DEVICE, observation_mode='state',
                                      reconstruction='recorded physical state per frame',
                                      checkpoint_sha256=sha(checkpoint),
                                      demo_h5_sha256=sha(H5), rows=rows))


def replay(attempt, count):
    out = OUT / attempt
    out.mkdir(exist_ok=True)
    meta = json.loads(META.read_text())
    assert meta['env_info']['env_id'] == 'PushT-v1'
    assert meta['env_info']['env_kwargs']['control_mode'] == 'pd_ee_delta_pos'
    assert meta['env_info']['env_kwargs']['sim_backend'] == 'physx_cuda'
    assert meta['commit_info']['commit_id'] == SOURCE_COMMIT
    env = make_env('push_t', device=DEVICE, native=NATIVE)
    assert env.unwrapped.sim_freq == 100 and env.unwrapped.control_freq == 20
    rows = []
    try:
        with h5py.File(H5, 'r') as h5:
            for item in meta['episodes'][:count]:
                episode_id = item['episode_id']
                group = h5[f'traj_{episode_id}']
                actions = np.asarray(group['actions'], np.float32)
                source_obj = np.asarray(group['env_states']['actors']['Tee'][:, :7], np.float32)
                source_qpos = np.asarray(group['env_states']['articulations']['panda_stick'][:, 13:20], np.float32)
                source_success = np.asarray(group['success']).astype(bool)
                assert actions.shape == (item['elapsed_steps'], 3)
                assert len(source_obj) == len(actions)+1 and len(source_success) == len(actions)
                assert np.isfinite(actions).all() and item['success']
                env.reset(seed=item['episode_seed'])
                restore_initial(env, group)
                state = observe(env, 'push_t')
                assert np.allclose(state['object'], source_obj[0], atol=1e-4)
                objects = [state['object']]
                tcps = [state['tcp']]
                qposes = [state['qpos']]
                metric, success = native_metric(env, 'push_t')
                metrics = [metric]
                successes = [success]
                for action in actions:
                    env.step(action)
                    state = observe(env, 'push_t')
                    metric, success = native_metric(env, 'push_t')
                    objects.append(state['object'])
                    tcps.append(state['tcp'])
                    qposes.append(state['qpos'])
                    metrics.append(metric)
                    successes.append(success)
                objects = np.asarray(objects)
                qposes = np.asarray(qposes)
                errors = np.linalg.norm(objects[:, :3] - source_obj[:, :3], axis=1)
                qpos_errors = np.linalg.norm(qposes - source_qpos, axis=1)
                trace = out / f'traj_{episode_id}.npz'
                np.savez_compressed(trace, actions=actions, source_object=source_obj,
                                    replay_object=objects, replay_tcp=np.asarray(tcps),
                                    replay_qpos=qposes, source_qpos=source_qpos,
                                    source_success=source_success,
                                    replay_success=np.asarray(successes, bool),
                                    metric=np.asarray(metrics, np.float32))
                row = dict(episode_id=episode_id, seed=item['episode_seed'], steps=len(actions),
                           source_final_success=bool(source_success[-1]),
                           replay_final_success=bool(successes[-1]),
                           replay_any_success=bool(any(successes)),
                           initial_metric=float(metrics[0]), final_metric=float(metrics[-1]),
                           first_step_position_error=float(errors[1]),
                           initial_qpos_error=float(qpos_errors[0]),
                           first_step_qpos_error=float(qpos_errors[1]),
                           final_qpos_error=float(qpos_errors[-1]),
                           final_position_error=float(errors[-1]),
                           mean_position_error=float(errors.mean()),
                           source_replay_step_label_agreement=float(np.mean(source_success == successes[1:])),
                           trace=trace.name, sha256=sha(trace))
                rows.append(row)
                print(json.dumps({k: row[k] for k in ('episode_id','replay_final_success',
                                                       'first_step_position_error','final_position_error')}), flush=True)
    finally:
        env.close()
    save(out / 'replay.json', dict(status='completed', source_commit=SOURCE_COMMIT,
                                   source_backend='physx_cuda',
                                   replay_backend='physx_cuda' if DEVICE == 'gpu' else 'physx_cpu',
                                   adapter='native-visual' if NATIVE else 'collision-only',
                                   sim_freq=100, control_freq=20,
                                   demo_h5_sha256=sha(H5), rows=rows))


def verify(attempt, replay_attempt):
    out = OUT / attempt
    out.mkdir(exist_ok=True)
    source = OUT / replay_attempt
    manifest = json.loads((source / 'replay.json').read_text())
    assert manifest['status'] == 'completed' and len(manifest['rows']) == 8
    assert manifest['demo_h5_sha256'] == sha(H5)
    for row in manifest['rows']:
        path = source / row['trace']
        assert sha(path) == row['sha256']
        with np.load(path, allow_pickle=False) as data:
            n = row['steps']
            assert data['actions'].shape == (n, 3)
            assert data['source_object'].shape == (n+1, 7)
            assert data['replay_object'].shape == (n+1, 7)
            assert data['source_success'].shape == (n,)
            assert data['replay_success'].shape == (n+1,)
            assert np.isfinite(data['replay_object']).all() and np.isfinite(data['metric']).all()
            assert np.allclose(data['replay_object'][0], data['source_object'][0], atol=1e-4)
            assert np.array_equal(data['metric'] >= .90, data['replay_success'])
            assert bool(data['replay_success'][-1]) == row['replay_final_success']
            assert bool(data['source_success'][-1]) == row['source_final_success']
    summary = dict(status='passed', episodes=8, hashes=8,
                   replay_final_success=sum(r['replay_final_success'] for r in manifest['rows']),
                   replay_any_success=sum(r['replay_any_success'] for r in manifest['rows']),
                   mean_first_step_position_error=float(np.mean([r['first_step_position_error'] for r in manifest['rows']])),
                   mean_final_position_error=float(np.mean([r['final_position_error'] for r in manifest['rows']])),
                   replay_attempt=replay_attempt)
    save(out / 'verification.json', summary)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=('replay', 'verify', 'audit'))
    parser.add_argument('--attempt', required=True)
    parser.add_argument('--count', type=int, default=8)
    parser.add_argument('--replay', default='replay1')
    args = parser.parse_args()
    if args.stage == 'replay':
        replay(args.attempt, args.count)
    elif args.stage == 'audit':
        audit_data(args.attempt, args.count)
    else:
        verify(args.attempt, args.replay)
