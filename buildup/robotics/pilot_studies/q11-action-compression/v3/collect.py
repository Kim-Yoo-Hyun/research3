"""One fixed-seed attempt, Docker only. Recording delegates unchanged simulator calls."""
import argparse
import hashlib
import json
import random
import signal
import time
from pathlib import Path
import gymnasium as gym
import numpy as np
import torch
import mani_skill.envs
from mani_skill.examples.motionplanning.panda.solutions.stack_cube import solve

P = json.loads(Path('/work/protocol.json').read_text())
LABELS = ['success', 'is_cubeA_on_cubeB', 'is_cubeA_static', 'is_cubeA_grasped']


def arr(x):
    if isinstance(x, torch.Tensor): x = x.detach().cpu().numpy()
    return np.asarray(x).copy()


def snapshot(e):
    r = e.agent.robot
    data = {'qpos': arr(r.get_qpos())[0], 'qvel': arr(r.get_qvel())[0],
            'robot_pose': arr(r.pose.raw_pose)[0],
            'tcp_pose': arr(e.agent.tcp.pose.raw_pose)[0]}
    for name in ['cubeA', 'cubeB']:
        a = getattr(e, name)
        data[name+'_pose'] = arr(a.pose.raw_pose)[0]
        data[name+'_linear_velocity'] = arr(a.linear_velocity)[0]
        data[name+'_angular_velocity'] = arr(a.angular_velocity)[0]
    for i, finger in enumerate([e.agent.finger1_link, e.agent.finger2_link]):
        data[f'finger{i}_pose'] = arr(finger.pose.raw_pose)[0]
        data[f'finger{i}_force'] = arr(e.scene.get_pairwise_contact_forces(finger, e.cubeA))[0]
    data['cube_contact_force'] = arr(e.scene.get_pairwise_contact_forces(e.cubeA, e.cubeB))[0]
    labels = e.evaluate()
    for name in LABELS: data[name] = arr(labels[name]).reshape(())
    return data


def save_record(path, actions, states):
    a = np.stack(actions) if actions else np.empty((0, 8), dtype=np.float64)
    data = {'actions': a}
    if states:
        data.update({k: np.stack([s[k] for s in states]) for k in states[0]})
    np.savez_compressed(path, **data)
    assert np.load(path)['actions'].tobytes() == a.tobytes()
    return {'steps': len(a), 'action_dtype': str(a.dtype),
            'action_sha256': hashlib.sha256(a.tobytes()).hexdigest()}


def make_env():
    return gym.make(P['task'], robot_uids=P['robot'], control_mode=P['controller'],
                    obs_mode='none', reward_mode='none', num_envs=1,
                    sim_backend=P['sim_backend'], render_backend=P['render_backend'],
                    max_episode_steps=P['max_steps'],
                    sim_config={'sim_freq': P['sim_freq'], 'control_freq': P['control_freq']})


class AttemptLimit(Exception): pass


def deadline(*_): raise AttemptLimit('wall-clock attempt timeout')


def collect(seed, mode):
    root = Path('/outputs')/f'seed_{seed}'
    root.mkdir(exist_ok=True)
    target = root/(mode+'.npz')
    receipt = root/(mode+'.json')
    assert not target.exists() and not receipt.exists(), 'do not overwrite an attempt'
    np.random.seed(seed); random.seed(seed); torch.manual_seed(seed)
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    actions, states = [], []
    env = None
    info = {'seed': seed, 'mode': mode, 'status': 'running', 'started': time.time()}
    receipt.write_text(json.dumps(info, indent=2))
    signal.signal(signal.SIGALRM, deadline)
    signal.alarm(P['attempt_timeout_seconds'])
    try:
        env = make_env()
        e = env.unwrapped
        assert e._sim_freq == P['sim_freq'] and e._control_freq == P['control_freq']
        assert str(e.device) == 'cpu'
        real_reset, real_step = e.reset, e.step

        def reset(*args, **kwargs):
            out = real_reset(*args, **kwargs)
            assert not states, 'unexpected second reset'
            states.append(snapshot(e))
            return out

        def step(action):
            if len(actions) >= P['max_steps']: raise AttemptLimit('control-step cap')
            a = arr(action)
            assert a.shape == (8,) and np.isfinite(a).all()
            out = real_step(action)
            actions.append(a)
            states.append(snapshot(e))
            return out

        e.reset, e.step = reset, step
        if mode == 'generation':
            result = solve(env, seed=seed, debug=False, vis=False)
            info['status'] = 'planner_failed' if isinstance(result, int) and result == -1 else 'completed'
        else:
            original = np.load(root/'generation.npz')['actions'] if mode.startswith('replay_') else np.load(root/'planned'/f'{mode}.npy')
            env.reset(seed=seed)
            for a in original: env.step(a.copy())
            info['status'] = 'completed'
        info['schema'] = {'action_low': arr(e.single_action_space.low).tolist(),
                          'action_high': arr(e.single_action_space.high).tolist(),
                          'sim_freq': e._sim_freq, 'control_freq': e._control_freq,
                          'device': str(e.device), 'wrapper_max_steps': env.spec.max_episode_steps,
                          'controller': str(e.agent.controller),
                          'cube_half_size': arr(e.cube_half_size).tolist()}
    except Exception as exc:
        info['status'] = 'incomplete' if isinstance(exc, AttemptLimit) else 'error'
        info['error'] = type(exc).__name__+': '+str(exc)
    finally:
        signal.alarm(0)
        info.update(save_record(target, actions, states))
        info['elapsed_seconds'] = time.time()-info['started']
        info['final_success'] = bool(states[-1]['success']) if states else False
        receipt.write_text(json.dumps(info, indent=2))
        print(json.dumps({k:v for k,v in info.items() if k != 'schema'}), flush=True)
        if env is not None: env.close()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=int, required=True)
    ap.add_argument('--mode', required=True)
    args = ap.parse_args()
    assert args.seed in P['seeds']
    assert args.mode.replace('_','').isalnum()
    collect(args.seed, args.mode)
