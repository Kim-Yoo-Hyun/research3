"""Independent field, hash, contact, and pair checks for the two-case CPU probe."""
import hashlib
import json
from pathlib import Path

import numpy as np

OUT = Path('/output/probe1')


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def load(row, key, sha_key):
    path = OUT / row[key]
    assert digest(path) == row[sha_key]
    with np.load(path, allow_pickle=False) as data:
        return {name: data[name].copy() for name in data.files}


def main():
    doc = json.loads((OUT / 'assessment.json').read_text())
    assert doc['status'] == 'completed' and doc['case_count'] == 2
    cases = []
    for row in doc['cases']:
        prefix = load(row, 'prefix_trace', 'prefix_sha256')
        assert len(prefix['full']) == len(prefix['observation']) == len(prefix['contacts'])
        assert prefix['full'].shape[1] == 10 and prefix['observation'].shape[1] == 5
        assert np.isfinite(prefix['full']).all() and np.isfinite(prefix['coverage']).all()
        assert np.all((prefix['coverage'] >= 0) & (prefix['coverage'] <= 1))
        assert np.max(prefix['contacts']) == row['prefix_max_contacts']
        assert np.allclose(prefix['full'][0], row['actual_initial_full_state'], atol=1e-10)
        if row['contact_step'] is None:
            assert row['status'] == 'no_contact_and_motion' and 'branches' not in row
            cases.append(dict(name=row['name'], status=row['status']))
            continue
        assert len(prefix['full']) == row['contact_step'] + 1
        assert row['prefix_max_contacts'] > 0 and row['prefix_object_motion'] >= 0.1
        assert {branch['route'] for branch in row['branches']} == {'baseline_a', 'baseline_b', 'changed'}
        branch = {item['route']: (item, load(item, 'trace', 'sha256')) for item in row['branches']}
        for route, (item, trace) in branch.items():
            assert trace['full'].shape == (12, 10) and trace['observation'].shape == (12, 5)
            assert np.isfinite(trace['full']).all() and np.isfinite(trace['coverage']).all()
            split_full_drift = float(np.max(np.abs(trace['full'][0] - prefix['full'][-1])))
            split_obs_drift = float(np.max(np.abs(trace['observation'][0] - prefix['observation'][-1])))
            assert max(split_full_drift, split_obs_drift) <= item['prefix_max_drift'] + 1e-10
            if row['status'] == 'repeatable':
                assert item['prefix_max_drift'] <= doc['tolerance']
        a, b = branch['baseline_a'][1], branch['baseline_b'][1]
        delta = max(float(np.max(np.abs(a[key] - b[key]))) for key in a)
        assert abs(delta - row['baseline_repeat_max_drift']) <= 1e-10
        assert np.allclose(branch['baseline_a'][0]['action'], branch['baseline_b'][0]['action'])
        assert not np.allclose(branch['baseline_a'][0]['action'], branch['changed'][0]['action'])
        if row['status'] == 'repeatable':
            assert delta <= doc['tolerance']
        cases.append(dict(name=row['name'], status=row['status'], contact_step=row['contact_step'],
                          baseline_repeat_max_drift=delta,
                          changed_final_object_distance=row['changed_final_object_distance']))
    result = dict(status='passed', assessment_sha256=digest(OUT / 'assessment.json'),
                  case_count=len(cases), repeatable_count=sum(x['status'] == 'repeatable' for x in cases),
                  cases=cases)
    (OUT / 'verification.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
