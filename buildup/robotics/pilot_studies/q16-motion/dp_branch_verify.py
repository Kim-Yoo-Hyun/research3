"""Independent source-environment replay and fixed-branch contract checks."""
import json
from pathlib import Path

import numpy as np

from dp_verify import check_replay, digest

ROOT = Path('/output')
OUT = ROOT/'branch1'


def load(path):
    with np.load(path, allow_pickle=False) as data:
        return {key:data[key].copy() for key in data.files}


def main():
    assessment = json.loads((OUT/'assessment.json').read_text())
    evaluation = json.loads((ROOT/'eval1/evaluation.json').read_text())
    assert assessment['status']=='completed'
    assert assessment['source_evaluation_sha256']==digest(ROOT/'eval1/evaluation.json')
    assert assessment['source_verification_sha256']==digest(ROOT/'eval1/verification.json')
    assert len(assessment['selected_seeds'])<=2
    assert len(assessment['rows'])==4*len(assessment['selected_seeds'])
    results = []
    for seed in assessment['selected_seeds']:
        parent = next(x for x in evaluation['rows'] if x['seed']==seed and x['route']=='released_dp')
        original = load(ROOT/'eval1'/parent['trace'])
        rows = [x for x in assessment['rows'] if x['seed']==seed]
        assert [x['route'] for x in rows] == assessment['routes']
        step = rows[0]['branch_step']
        assert all(x['branch_step']==step for x in rows)
        assert step in original['chunk_start'] and 0<step<=268
        assert np.any(original['contact'][:step]>0)
        assert np.linalg.norm(original['full'][step,4:6]-original['full'][0,4:6])>=1.
        controls = []
        for row in rows:
            path=OUT/row['trace']
            assert digest(path)==row['sha256']
            trace=load(path)
            assert all(np.isfinite(x).all() for x in trace.values())
            assert trace['action'].shape==(row['steps'],2)
            drift=check_replay(seed,'released_dp',trace)
            assert drift<=1e-8
            assert np.max(np.abs(trace['action'][:step]-original['action'][:step]))<=1e-8
            assert max(np.max(np.abs(trace[k][:step+1]-original[k][:step+1]))
                       for k in ('observation','policy_observation','full','coverage'))<=1e-8
            # Replacement is assigned into the policy's float32 action chunk.
            executed=np.asarray(row['target'],dtype=np.float32).astype(np.float64)
            assert np.max(np.abs(trace['action'][step]-executed))<=1e-8
            expected_original=original['action'][step]
            assert np.max(np.abs(expected_original-np.asarray(row['original_target'])))<=1e-8
            if row['route']=='feedback':
                state=original['observation'][step]
                direction=np.asarray([256.,256.])-state[2:4]
                direction*=min(1.,60./max(float(np.linalg.norm(direction)),1e-12))
                expected=np.clip(state[:2]+direction,0.,512.)
                assert np.max(np.abs(expected-np.asarray(row['target'])))<=1e-8
            elif row['route']=='plus_x':
                expected=np.clip(expected_original+np.asarray([40.,0.]),0.,512.)
                assert np.max(np.abs(expected-np.asarray(row['target'])))<=1e-8
            else:
                assert trace['action'].shape==original['action'].shape
                assert max(np.max(np.abs(trace[k]-original[k])) for k in original)<=1e-8
                controls.append(trace)
            assert row['any_success']==bool(np.any(trace['coverage']>.95))
            assert abs(row['max_coverage']-np.max(trace['coverage']))<=1e-10
            assert abs(row['final_coverage']-trace['coverage'][-1])<=1e-10
            assert row['contact_steps']==int(np.sum(trace['contact']>0))
            results.append(dict(seed=seed,route=row['route'],replay_max_drift=drift))
        assert len(controls)==2
        assert max(np.max(np.abs(controls[0][k]-controls[1][k])) for k in controls[0])<=1e-8
    output=dict(status='passed',assessment_sha256=digest(OUT/'assessment.json'),
                checked_traces=len(results),checked_seeds=len(assessment['selected_seeds']),
                max_replay_drift=max(x['replay_max_drift'] for x in results),rows=results)
    (OUT/'verification.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:output[k] for k in ('status','checked_traces','checked_seeds',
                                            'max_replay_drift')},indent=2),flush=True)


if __name__=='__main__':
    main()
