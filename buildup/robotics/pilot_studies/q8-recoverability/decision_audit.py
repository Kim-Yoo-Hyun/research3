"""Apply the frozen zero-control and demonstration-transition gates to retained artifacts."""
import json
from pathlib import Path

root=Path('/outputs')
cold=[json.loads((root/f'cold_{i}.json').read_text()) for i in range(3)]
summary={'per_process':[]}
for d in cold:
    qualified={(z['seed'],z['anchor']) for z in d['zero_controls'] if z['error']<=1e-5 and z['label_equal']}
    rows=[r for r in d['grid'] if r['admitted'] and (r['seed'],r['anchor']) in qualified]
    summary['per_process'].append(dict(zero_passed=len(qualified),zero_total=len(d['zero_controls']),
        qualified_rows=len(rows),qualified_nonzero=sum(r['radius']>0 for r in rows),
        qualified_success=sum(r['success_once'] and r['success_at_end'] for r in rows)))
assert summary['per_process'][0]==summary['per_process'][1]==summary['per_process'][2]
demo=json.loads((root/'demo_audit.json').read_text())
assert len(demo)==27 and len({(r['trajectory'],r['anchor'],r['repeat']) for r in demo})==27
for r in demo: assert r['passed']==(r['pre_state_error']<=1e-5 and r['next_state_error']<=1e-5)
for t in range(3):
    for anchor in [0,5,20]:
        group=[r for r in demo if r['trajectory']==t and r['anchor']==anchor]
        assert len({(r['pre_state_error'],r['next_state_error']) for r in group})==1
summary['demonstration']=dict(passed=sum(r['passed'] for r in demo),n=len(demo),
    max_next_state_error=max(r['next_state_error'] for r in demo),
    mid_trajectory_passed=sum(r['passed'] for r in demo if r['anchor']>0),
    mid_trajectory_n=sum(r['anchor']>0 for r in demo))
summary['decision']='REFINE_Q8; TESTED_GRID_UNINFORMATIVE; RECOMMEND_Q1_STAGE6'
with (root/'decision_audit.json').open('x') as f: json.dump(summary,f,indent=2)
print(json.dumps(summary,indent=2))
