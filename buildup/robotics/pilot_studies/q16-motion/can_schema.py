"""Metadata-only audit of the pinned robomimic Can PH HDF5 inside Docker."""
import hashlib
import json
from pathlib import Path

import h5py
import numpy as np

DATA = Path('/data/low_dim_v15.hdf5')
OUT = Path('/output/schema1')
EXPECTED_SHA = '3f2eb92e0a5025d0095e866ac16cc8092d6a762abe27dec90dbaff9027282962'
EXPECTED_BYTES = 46889752
OBS_KEYS = ('object', 'robot0_eef_pos', 'robot0_eef_quat', 'robot0_gripper_qpos')


def sha256(path):
    result = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1 << 20), b''):
            result.update(block)
    return result.hexdigest()


def serial(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')
    if isinstance(value, np.generic):
        return value.item()
    return value


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    digest = sha256(DATA)
    assert DATA.stat().st_size == EXPECTED_BYTES and digest == EXPECTED_SHA
    with h5py.File(DATA, 'r') as h5:
        assert 'data' in h5
        group = h5['data']
        env_args_raw = serial(group.attrs.get('env_args', '{}'))
        env_args = json.loads(env_args_raw)
        names = sorted(group.keys(), key=lambda x: int(x.split('_')[-1]))
        observations = {}
        action_shapes = set()
        state_shapes = set()
        lengths = []
        xml_count = 0
        done_terminal_count = 0
        sampled_action_min = np.full(7, np.inf)
        sampled_action_max = np.full(7, -np.inf)
        first_episode = None
        for name in names:
            episode = group[name]
            action = episode['actions']
            n = int(action.shape[0])
            lengths.append(n)
            action_shapes.add(tuple(action.shape[1:]))
            state_shapes.add(tuple(episode['states'].shape[1:]) if 'states' in episode else None)
            xml = episode.attrs.get('model_file')
            xml_count += int(xml is not None and len(xml) > 0)
            assert episode['obs'] and episode['next_obs']
            for key in episode['obs']:
                obs = episode['obs'][key]
                next_obs = episode['next_obs'][key]
                observations.setdefault(key, set()).add(tuple(obs.shape[1:]))
                assert obs.shape[0] == next_obs.shape[0] == n
                assert obs.shape[1:] == next_obs.shape[1:]
            assert episode['dones'].shape[0] == n
            done_terminal_count += int(bool(episode['dones'][-1]))
            if action.shape[1:] == (7,):
                sample = np.asarray(action[sorted(set((0, n // 2, n - 1)))], dtype=np.float64)
                assert np.isfinite(sample).all()
                sampled_action_min = np.minimum(sampled_action_min, sample.min(axis=0))
                sampled_action_max = np.maximum(sampled_action_max, sample.max(axis=0))
            if first_episode is None:
                first_episode = dict(name=name, attributes={k:(len(serial(v)) if k=='model_file'
                    else serial(v)) for k,v in episode.attrs.items()},
                    datasets={key:list(episode[key].shape) for key in episode if key not in ('obs','next_obs')})
        obs_shapes = {key:[list(shape) for shape in sorted(shapes)]
                      for key, shapes in sorted(observations.items())}
        policy_dim = sum(int(np.prod(next(iter(observations[key])))) for key in OBS_KEYS
                         if key in observations and len(observations[key]) == 1)
        contract = (len(names) == 200 and action_shapes == {(7,)}
                    and all(key in observations and len(observations[key]) == 1 for key in OBS_KEYS)
                    and policy_dim == 23 and xml_count == len(names)
                    and sum(lengths) == int(group.attrs['total']))
        result = dict(status='passed' if contract else 'mismatch',
                      dataset_sha256=digest, dataset_bytes=DATA.stat().st_size,
                      root_keys=list(h5.keys()), root_attributes={k:serial(v) for k,v in h5.attrs.items()},
                      data_attributes={k:serial(v) for k,v in group.attrs.items() if k!='env_args'},
                      env_args=env_args, episodes=len(names), total_rows=sum(lengths),
                      length_min=min(lengths), length_max=max(lengths),
                      action_shapes=[list(x) for x in sorted(action_shapes)],
                      state_shapes=[list(x) if x is not None else None for x in sorted(state_shapes, key=str)],
                      observation_shapes=obs_shapes, policy_observation_dim=policy_dim,
                      model_xml_episode_count=xml_count, terminal_done_episode_count=done_terminal_count,
                      sampled_action_min=sampled_action_min.tolist(),
                      sampled_action_max=sampled_action_max.tolist(),
                      first_episode=first_episode)
    path = OUT / 'assessment.json'
    path.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({k:result[k] for k in ('status','episodes','total_rows',
        'action_shapes','policy_observation_dim','model_xml_episode_count')}, indent=2))
    assert contract


if __name__ == '__main__':
    main()
