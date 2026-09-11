"""Independent artifact verification; no simulator or policy import."""
import collections
import hashlib
import json
import os
from pathlib import Path
import numpy as np

root=Path('/outputs')
prefix=os.environ.get('Q8_VERIFY_PREFIX','audit')
expected_restore=150 if prefix=='cold' else 450
files=sorted(root.glob(prefix+'_[012].json'))
assert len(files)==3, files
data=[json.loads(p.read_text()) for p in files]
assert all(len(d['restore'])==expected_restore and len(d['grid'])==312 for d in data)
summary=dict(files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
             seconds=[d['seconds'] for d in data],restore={},grid={},
             restore_passes_per_process=[sum(r['pass'] for r in d['restore']) for d in data])
restore_keys=['pre_state_error','pre_obs_error','action_error','next_obs_error','next_state_error']
for d in data:
    assert len({(r['mode'],r['seed'],r['anchor'],r['route'],r['repeat']) for r in d['restore']})==expected_restore
    assert len({(r['seed'],r['anchor'],r['axis'],r['radius']) for r in d['grid']})==312
    for r in d['restore']:
        assert r['pass']==(max(r[k] for k in restore_keys)<=1e-5)
    for r in d['grid']:
        v=r['validity']; b=np.array(v['cube_bounds']); xyz=np.array(v['cube_position'])
        collision=all(np.any(b[1]+.001<np.array(lb)[0]) or np.any(np.array(lb)[1]+.001<b[0])
                      for lb in v['robot_bounds'].values())
        assert collision==v['checks']['collision_free']
        assert (np.abs(xyz[:2])<=.1).all()==v['checks']['spawn']
        assert (abs(b[0,2])<=.001 and v['tilt']<.01)==v['checks']['support']
        assert (v['linear_speed']<.02 and v['angular_speed']<.1)==v['checks']['slow']
        assert v['valid']==all(v['checks'].values())
        assert r['admitted']==(v['valid'] and r['anchor_validity']['valid'] and r['restore_ok'] and r['invariant_error']<=1e-5)
        if r['admitted']:
            tr=r['trajectory']; assert [m['step'] for m in tr]==list(range(r['anchor']+1,51))
            for m in tr:
                assert m['success']==(m['distance']<=.025 and m['robot_speed']<=.2)
            assert r['success_once']==any(m['success'] for m in tr)
            assert r['success_at_end']==tr[-1]['success']
first=data[0]
for mode in ['pd_joint_delta_pos','pd_ee_delta_pos']:
    for route in ['direct','reset_state','prefix']:
        rows=[r for r in first['restore'] if r['mode']==mode and r['route']==route]
        if not rows: continue
        summary['restore'][mode+'/'+route]=dict(n=len(rows),passed=sum(r['pass'] for r in rows),
            maximum={k:max(r[k] for r in rows) for k in restore_keys},
            success_disagreements=sum(r['success']!=r['reference_success'] for r in rows))
rows=first['grid']; admitted=[r for r in rows if r['admitted']]
summary['grid']=dict(proposed=len(rows),admitted=len(admitted),
    nonzero_admitted=sum(r['radius']>0 for r in admitted),
    success_once=sum(r['success_once'] for r in admitted),
    success_at_end=sum(r['success_at_end'] for r in admitted),
    by_anchor={},invalid_reasons=dict(collections.Counter(k for r in rows for k,v in r['validity']['checks'].items() if not v)),
    repeat_label_disagreements=0,max_repeat_trajectory_error=0.0)
for t in [0,5,10]:
    group=[r for r in admitted if r['anchor']==t]
    summary['grid']['by_anchor'][str(t)]=dict(n=len(group),success=sum(r['success_once'] for r in group),
        nominal_success=sum(r['nominal_success_once'] for r in group))
for other in data[1:]:
    for a,b in zip(first['grid'],other['grid']):
        assert all(a[k]==b[k] for k in ['seed','anchor','axis','radius'])
        assert a['admitted']==b['admitted'], (a['seed'],a['anchor'])
        if a['admitted']:
            summary['grid']['repeat_label_disagreements']+=int(a['success_once']!=b['success_once'] or a['success_at_end']!=b['success_at_end'])
            for x,y in zip(a['trajectory'],b['trajectory']):
                summary['grid']['max_repeat_trajectory_error']=max(summary['grid']['max_repeat_trajectory_error'],
                    abs(x['distance']-y['distance']),abs(x['robot_speed']-y['robot_speed']))
summary['nominal']=[dict(mode=r['mode'],seed=r['seed'],success_once=any(m['success'] for m in r['metrics'][1:]),
                         success_at_end=r['metrics'][-1]['success']) for r in first['nominal']]
if prefix=='cold':
    zeros=[r for d in data for r in d['zero_controls']]
    summary['zero_controls']=dict(n=len(zeros),max_error=max(r['error'] for r in zeros),
                                 label_disagreements=sum(not r['label_equal'] for r in zeros))
    for d in data:
        for r in d['grid']:
            if r['axis']=='zero' and r['admitted']:
                baseline=next(n['metrics'] for n in d['nominal'] if n['mode']=='pd_joint_delta_pos' and n['seed']==r['seed'])
                dif=max(max(abs(x['distance']-y['distance']),abs(x['robot_speed']-y['robot_speed'])) for x,y in zip(r['trajectory'],baseline[r['anchor']+1:]))
                stored=next(z for z in d['zero_controls'] if z['seed']==r['seed'] and z['anchor']==r['anchor'])
                assert dif==stored['error']
    summary['failures']=[{k:r[k] for k in ['seed','anchor','axis','radius','nominal_success_once','success_once','success_at_end','action_drift','critic_value']}
                         for r in admitted if not r['success_once'] or not r['success_at_end']]
name='cold_verification.json' if prefix=='cold' else 'verification.json'
with (root/name).open('x') as f: json.dump(summary,f,indent=2,allow_nan=False)
print(json.dumps(summary,indent=2))
