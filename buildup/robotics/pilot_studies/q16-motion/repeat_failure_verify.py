"""Independent paired-contact trace check for selected small-BC failures."""
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path('/output')
OUT = ROOT / 'failure_branch1'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    doc = json.loads((OUT / 'assessment.json').read_text())
    assert doc['status'] == 'completed' and doc['selected_seeds'] == [48007, 48010]
    assert digest(ROOT / 'bc_eval1/evaluation.json') == doc['source_evaluation_sha256']
    assert digest(ROOT / 'bc_fit1/ridge.npz') == doc['policy_checkpoint_sha256']
    result_rows = []
    for case in doc['cases']:
        source = ROOT / 'bc_eval1' / case['source_trace']
        assert digest(source) == case['source_sha256']
        with np.load(source, allow_pickle=False) as data:
            original = {key: data[key].copy() for key in data.files}
        if case['status'] == 'no_moved_contact':
            result_rows.append(dict(seed=case['seed'], status=case['status']))
            continue
        step = case['selected_step']
        assert 1 <= step < len(original['action']) - 10
        assert original['contact'][step-1] > 0
        assert np.linalg.norm(original['full'][step, 4:6] - original['full'][0, 4:6]) > 1
        assert abs(case['selected_coverage'] - float(original['coverage'][step])) < 1e-10
        assert {branch['route'] for branch in case['branches']} == {'baseline_a', 'changed', 'baseline_b'}
        traces = {}
        for branch in case['branches']:
            path = OUT / branch['trace']
            assert digest(path) == branch['sha256']
            with np.load(path, allow_pickle=False) as data:
                traces[branch['route']] = {key: data[key].copy() for key in data.files}
            trace = traces[branch['route']]
            assert trace['observation'].shape == (12, 5)
            assert trace['full'].shape == (12, 10)
            assert trace['coverage'].shape == (12,)
            assert trace['contact'].shape == (11,)
            assert trace['action'].shape == (11, 2)
            assert all(np.isfinite(value).all() for value in trace.values())
            assert np.allclose(trace['action'][0], branch['first_action'], atol=1e-6)
            split_drift = max(float(np.max(np.abs(trace[key][0] - original[key][step])))
                              for key in ('observation', 'full', 'coverage'))
            assert split_drift <= branch['prefix_drift'] + 1e-10
            assert abs(float(trace['coverage'][-1]) - branch['final_coverage']) < 1e-10
            assert np.allclose(trace['full'][-1, 4:6], branch['final_object_position'], atol=1e-10)
        assert np.allclose(traces['baseline_a']['action'][0], traces['baseline_b']['action'][0])
        assert not np.allclose(traces['baseline_a']['action'][0], traces['changed']['action'][0])
        repeated = max(float(np.max(np.abs(traces['baseline_a'][key] - traces['baseline_b'][key])))
                       for key in traces['baseline_a'])
        assert abs(repeated-case['baseline_repeat_max_drift']) < 1e-10
        changed = float(np.linalg.norm(traces['changed']['full'][-1, 4:6] -
                                       traces['baseline_a']['full'][-1, 4:6]))
        assert abs(changed-case['changed_final_object_distance']) < 1e-10
        if case['status'] == 'repeatable':
            assert repeated <= doc['tolerance']
            assert all(branch['prefix_drift'] <= doc['tolerance'] for branch in case['branches'])
        result_rows.append(dict(seed=case['seed'], status=case['status'], selected_step=step,
                                baseline_repeat_max_drift=repeated,
                                changed_final_object_distance=changed))
    result = dict(status='passed', assessment_sha256=digest(OUT / 'assessment.json'),
                  case_count=len(result_rows), repeatable_count=sum(x['status']=='repeatable' for x in result_rows),
                  cases=result_rows)
    (OUT / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
