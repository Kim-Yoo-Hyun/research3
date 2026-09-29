"""Check the saved bounded replay result without simulator imports."""
import json
import math
from pathlib import Path


ROOT = Path('/home/yoohyun/research3')
RESULT = ROOT / 'runs/q16/can_replay/replay6/result.json'
STATE_MAP = ROOT / 'runs/q16/can_replay/state_map.json'


def main():
    result = json.loads(RESULT.read_text())
    mapping = json.loads(STATE_MAP.read_text())
    assert result['criteria'] == {'state_max_abs': 1e-5, 'obs_max_abs': 1e-4,
                                  'repeat_max_abs': 1e-10, 'steps': 32}
    assert set(result['episodes']) == {'demo_0', 'demo_1'}
    assert mapping['nq'] == 37 and mapping['nv'] == 33
    assert mapping['targets']['62'] == ['Cereal_joint0']
    for name, episode in result['episodes'].items():
        rows = episode['rows']
        assert len(rows) == episode['steps'] == 32
        assert [row['step'] for row in rows] == list(range(32))
        assert episode['initial_state']['exact']
        for key in ('post_state', 'post_obs'):
            row_key = 'state' if key == 'post_state' else 'next_obs'
            maximum = max(row[row_key]['max_abs'] for row in rows)
            assert math.isfinite(maximum) and maximum == episode['maxima'][key]
        for key, value in episode['maxima']['state_groups'].items():
            assert math.isfinite(value) and value == max(row['state_groups'][key]['max_abs'] for row in rows)
        assert episode['status'] == 'diverged'
        assert episode['maxima']['post_state'] > result['criteria']['state_max_abs']
        assert episode['maxima']['post_obs'] > result['criteria']['obs_max_abs']
        assert all(row['next_obs']['max_abs'] > result['criteria']['obs_max_abs'] for row in rows)
    assert result['repeat']['steps'] == 32
    assert result['repeat']['state_exact_steps'] == 32
    assert result['repeat']['state_max_abs'] == result['repeat']['observation_max_abs'] == 0.0
    assert result['status'] == 'diverged'
    print('verified: two 32-step prefixes diverge from HDF5; demo_0 repeat is exact')


if __name__ == '__main__':
    main()
