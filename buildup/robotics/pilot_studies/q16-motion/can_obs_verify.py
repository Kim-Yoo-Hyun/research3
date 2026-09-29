"""Verify the four policy observation keys in every Can PH demonstration."""
import json
from pathlib import Path

import h5py


DATA = Path('/data/low_dim_v15.hdf5')
KEY_DIMS = {
    'object': 14,
    'robot0_eef_pos': 3,
    'robot0_eef_quat': 4,
    'robot0_gripper_qpos': 2,
}


def main():
    with h5py.File(DATA, 'r') as h5:
        episodes = h5['data']
        for name in episodes:
            episode = episodes[name]
            count = episode['actions'].shape[0]
            for group_name in ('obs', 'next_obs'):
                group = episode[group_name]
                for key, dim in KEY_DIMS.items():
                    assert key in group, (name, group_name, key)
                    assert group[key].shape == (count, dim), (name, group_name, key)
        print(json.dumps({'status': 'passed', 'episodes': len(episodes),
                          'policy_observation_dim': sum(KEY_DIMS.values()),
                          'keys': KEY_DIMS}, sort_keys=True))


if __name__ == '__main__':
    main()
