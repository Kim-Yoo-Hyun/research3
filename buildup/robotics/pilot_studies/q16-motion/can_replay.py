"""Bounded Can PH action replay with the source-matched robosuite simulator."""
import json
import time
import traceback
from copy import deepcopy
from pathlib import Path

import h5py
import numpy as np
import robosuite


DATA = Path('/data/low_dim_v15.hdf5')
OUTPUT = Path('/output/replay6/result.json')
EPISODES = ('demo_0', 'demo_1')
STEPS = 32
POLICY_KEYS = ('object', 'robot0_eef_pos', 'robot0_eef_quat', 'robot0_gripper_qpos')
STATE_TOL = 1e-5
OBS_TOL = 1e-4
REPEAT_TOL = 1e-10


def policy_obs(raw):
    return {
        key: np.asarray(raw['object-state'] if key == 'object' else raw[key], dtype=np.float64).copy()
        for key in POLICY_KEYS
    }


def compare(actual, expected):
    diff = np.asarray(actual, dtype=np.float64) - np.asarray(expected, dtype=np.float64)
    return {'max_abs': float(np.max(np.abs(diff))), 'l2': float(np.linalg.norm(diff)),
            'exact': bool(np.array_equal(actual, expected))}


def compare_obs(actual, episode, group, index):
    by_key = {key: compare(actual[key], episode[group][key][index]) for key in POLICY_KEYS}
    return {'max_abs': max(item['max_abs'] for item in by_key.values()),
            'l2': float(np.sqrt(sum(item['l2'] ** 2 for item in by_key.values()))),
            'exact': all(item['exact'] for item in by_key.values()), 'by_key': by_key}


def make_env(env_args):
    assert robosuite.__version__ == '1.5.1', robosuite.__version__
    assert env_args['env_name'] == 'PickPlaceCan'
    assert env_args['env_version'] == '1.5.1'
    kwargs = deepcopy(env_args['env_kwargs'])
    assert kwargs['has_renderer'] is False and kwargs['has_offscreen_renderer'] is False
    assert kwargs['use_object_obs'] is True and kwargs['use_camera_obs'] is False
    env = robosuite.make(env_args['env_name'], **kwargs)
    for name in env.observation_names:
        if 'joint_pos' in name or 'eef_vel' in name:
            env.modify_observable(observable_name=name, attribute='active', modifier=True)
    assert env.action_spec[0].shape == (7,)
    return env


def restore(env, episode):
    meta = episode.attrs.get('ep_meta')
    env.set_ep_meta(json.loads(meta) if meta is not None else {})
    env.reset()
    xml = env.edit_model_xml(episode.attrs['model_file'])
    env.reset_from_xml_string(xml)
    env.sim.reset()
    env.sim.set_state_from_flattened(episode['states'][0])
    env.sim.forward()
    return policy_obs(env._get_observations(force_update=True))


def rollout(env, episode, name):
    start = time.monotonic()
    initial_obs = restore(env, episode)
    initial_state = np.asarray(env.sim.get_state().flatten(), dtype=np.float64)
    initial_state_error = compare(initial_state, episode['states'][0])
    initial_obs_error = compare_obs(initial_obs, episode, 'obs', 0)
    assert episode['actions'].shape[0] > STEPS
    rows, states, observations = [], [], []
    nq = env.sim.model.nq
    for index in range(STEPS):
        raw, reward, done, _ = env.step(episode['actions'][index])
        state = np.asarray(env.sim.get_state().flatten(), dtype=np.float64).copy()
        observation = policy_obs(raw)
        states.append(state)
        observations.append(observation)
        success = env._check_success()
        if isinstance(success, dict):
            success = success['task']
        state_error = compare(state, episode['states'][index + 1])
        stored_state = episode['states'][index + 1]
        state_parts = {'time': compare(state[:1], stored_state[:1]),
                       'qpos': compare(state[1:1+nq], stored_state[1:1+nq]),
                       'qvel': compare(state[1+nq:], stored_state[1+nq:])}
        assert nq == 37 and env.sim.model.nv == 33
        state_groups = {key: compare(state[indices], stored_state[indices]) for key, indices in {
            'robot_qpos': slice(1, 10), 'other_object_qpos': slice(10, 31),
            'can_qpos': slice(31, 38), 'robot_qvel': slice(38, 47),
            'other_object_qvel': slice(47, 65), 'can_qvel': slice(65, 71),
        }.items()}
        top_state_errors = None
        if index in (0, 30, 31):
            differences = np.abs(state - stored_state)
            largest = np.argsort(differences)[-5:][::-1]
            top_state_errors = [{'index': int(i), 'abs_error': float(differences[i]),
                                 'actual': float(state[i]), 'stored': float(stored_state[i])}
                                for i in largest]
        next_obs_error = compare_obs(observation, episode, 'next_obs', index)
        following_obs_error = compare_obs(observation, episode, 'obs', index + 1)
        rows.append({'step': index, 'state': state_error, 'state_parts': state_parts,
                     'state_groups': state_groups,
                     'top_state_errors': top_state_errors,
                     'next_obs': next_obs_error,
                     'following_obs': following_obs_error, 'native_success': bool(success),
                     'native_done': bool(done), 'native_reward': float(reward),
                     'stored_done': bool(episode['dones'][index]),
                     'stored_reward': float(episode['rewards'][index])})
    maxima = {'initial_state': initial_state_error['max_abs'],
              'initial_obs': initial_obs_error['max_abs'],
              'post_state': max(row['state']['max_abs'] for row in rows),
              'post_qpos': max(row['state_parts']['qpos']['max_abs'] for row in rows),
              'post_qvel': max(row['state_parts']['qvel']['max_abs'] for row in rows),
              'post_obs': max(row['next_obs']['max_abs'] for row in rows)}
    maxima['state_groups'] = {key: max(row['state_groups'][key]['max_abs'] for row in rows)
                              for key in rows[0]['state_groups']}
    status = ('passed' if maxima['initial_state'] <= STATE_TOL
              and maxima['initial_obs'] <= OBS_TOL and maxima['post_state'] <= STATE_TOL
              and maxima['post_obs'] <= OBS_TOL else 'diverged')
    result = {'name': name, 'status': status, 'steps': STEPS,
              'initial_state': initial_state_error, 'initial_obs': initial_obs_error,
              'maxima': maxima, 'rows': rows,
              'native_success_steps': sum(row['native_success'] for row in rows),
              'native_done_steps': sum(row['native_done'] for row in rows),
              'elapsed_s': round(time.monotonic() - start, 3)}
    return result, states, observations


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=False)
    result = {'status': 'running', 'device': 'cpu', 'robosuite_version': robosuite.__version__,
              'robosuite_file': robosuite.__file__, 'episodes': {},
              'criteria': {'state_max_abs': STATE_TOL, 'obs_max_abs': OBS_TOL,
                           'repeat_max_abs': REPEAT_TOL, 'steps': STEPS}}
    env = None
    try:
        with h5py.File(DATA, 'r') as data:
            env_args = json.loads(data['data'].attrs['env_args'])
            env = make_env(env_args)
            first_states = first_obs = None
            for name in EPISODES:
                episode = data['data'][name]
                ep_result, states, obs = rollout(env, episode, name)
                result['episodes'][name] = ep_result
                if name == 'demo_0':
                    first_states, first_obs = states, obs
            repeat_result, repeat_states, repeat_obs = rollout(env, data['data']['demo_0'], 'demo_0_repeat')
            state_errors = [compare(a, b) for a, b in zip(first_states, repeat_states)]
            obs_errors = [max(compare(a[k], b[k])['max_abs'] for k in POLICY_KEYS)
                          for a, b in zip(first_obs, repeat_obs)]
            result['repeat'] = {'source': 'demo_0', 'steps': STEPS,
                                'state_max_abs': max(x['max_abs'] for x in state_errors),
                                'observation_max_abs': max(obs_errors),
                                'state_exact_steps': sum(x['exact'] for x in state_errors),
                                'second_rollout_status': repeat_result['status']}
            result['status'] = ('passed' if all(x['status'] == 'passed' for x in result['episodes'].values())
                                and result['repeat']['state_max_abs'] <= REPEAT_TOL
                                and result['repeat']['observation_max_abs'] <= REPEAT_TOL else 'diverged')
    except Exception as exc:
        result['status'] = 'error'
        result['error'] = {'type': type(exc).__name__, 'message': str(exc),
                           'traceback': traceback.format_exc(limit=10)}
    finally:
        if env is not None:
            env.close()
        OUTPUT.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
        print(json.dumps({'status': result['status'],
                          'maxima': {name: ep['maxima'] for name, ep in result['episodes'].items()},
                          'repeat': result.get('repeat'), 'error': result.get('error')}, indent=2))
    if result['status'] == 'error':
        raise SystemExit(2)


if __name__ == '__main__':
    main()
