"""Post hoc simple multi-view controls; no fitted threshold or performance inference."""
import json
from pathlib import Path
from statistics import mean, median

scored = Path('/output/scored')
rows = [json.loads(x) for x in (scored/'scores.jsonl').read_text().splitlines()]
assert not (scored/'aggregation.json').exists()
groups = sorted(set(r['group'] for r in rows) - {'controls'})
output = []
for group in groups:
    values = {role: [r['mean_absolute_change'] for r in rows if r['group']==group and r['role']==role]
              for role in ['source_failure', 'source_success']}
    assert all(len(x)==3 for x in values.values())
    entry = {'group':group}
    for name,func in [('mean',mean),('median',median)]:
        fail,succ=func(values['source_failure']),func(values['source_success'])
        entry[name]={'failure':fail,'success':succ,'failure_minus_success':fail-succ}
    output.append(entry)
result={'purpose':'Post-score exploratory control; not preplanned confirmatory analysis',
        'independent_pairs_claimed':False,'groups':output,
        'performance_claim':None,'source_rows_unchanged':True}
(scored/'aggregation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
