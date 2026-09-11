"""Frozen six-predicate evaluation from immutable trajectories, no policy/simulator imports."""
import csv
import hashlib
import json
from pathlib import Path
import h5py
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root=Path('/outputs')
data={}; matching={}
for tag in ['ee','joint']:
    meta=json.loads((root/tag/'trajectory.json').read_text())
    assert meta['trajectory_sha256']==hashlib.sha256((root/tag/'trajectory.h5').read_bytes()).hexdigest()
    with h5py.File(root/tag/'trajectory.h5') as f:
        def read(group): return {k:read(v) if isinstance(v,h5py.Group) else v[:] for k,v in group.items()}
        data[tag]=read(f)
    d=data[tag]
    assert d['actions'].shape[0:2]==(50,8)
    assert d['snapshots']['qvel'].shape==(51,8,9)
for name in ['cube','goal','qpos','qvel']:
    a=data['ee']['snapshots'][name][0]; b=data['joint']['snapshots'][name][0]
    matching[name]=dict(exact=bool(np.array_equal(a,b)),max_error=float(np.max(np.abs(a-b))))
for family,entries in data['ee']['snapshots']['state'].items():
    for name,states in entries.items():
        b=data['joint']['snapshots']['state'][family][name][0]
        matching[family+'/'+name]=dict(exact=bool(np.array_equal(states[0],b)),max_error=float(np.max(np.abs(states[0]-b))))
with (root/'matching.json').open('x') as f: json.dump(matching,f,indent=2)
assert all(v['exact'] for v in matching.values()), 'Initial states do not match: REFINE, no paired relabeling'
rows=[]; signals={}
for tag,d in data.items():
    s=d['snapshots']
    delta=s['cube'][1:].astype(np.float64)-s['goal'][1:].astype(np.float64)
    distance=np.sqrt((delta**2).sum(axis=-1))
    speed=np.abs(s['qvel'][1:,:,:7]).max(axis=-1)
    static=speed<=.2
    assert np.array_equal(static,d['official']['is_robot_static'])
    assert np.array_equal(distance<=.025,d['official']['is_obj_placed'])
    assert np.array_equal((distance<=.025)&static,d['official']['success'])
    signals[tag]=distance,speed
    for i in range(8):
        row=dict(policy=tag,episode=i,minimum_distance_m=float(distance[:,i].min()),
                 final_distance_m=float(distance[-1,i]),final_arm_max_speed=float(speed[-1,i]),
                 official_success_steps=int(d['official']['success'][:,i].sum()))
        for mm in [20,25,30]:
            success=(distance[:,i]<=mm/1000)&static[:,i]
            row[f'{mm}_once']=int(success.any()); row[f'{mm}_end']=int(success[-1])
        rows.append(row)
with (root/'labels.csv').open('x') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
rates={}
for mm in [20,25,30]:
    for aggregation in ['once','end']:
        key=f'{mm}_{aggregation}'
        rates[key]={tag:sum(r[key] for r in rows if r['policy']==tag)/8 for tag in data}
        rates[key]['difference']=rates[key]['ee']-rates[key]['joint']
ref=rates['25_once']['difference']
sign_changes=[k for k,v in rates.items() if np.sign(v['difference'])!=np.sign(ref)]
strict_reversals=[k for k,v in rates.items() if v['difference']*ref<0]
changed=[dict(policy=r['policy'],episode=r['episode']) for r in rows
         if len({r[f'{mm}_{a}'] for mm in [20,25,30] for a in ['once','end']})>1]
summary=dict(episodes=16,labels=96,matched_initialization=True,rates=rates,
             changed_trajectories=changed,sign_changes=sign_changes,strict_reversals=strict_reversals,
             exact_static_boundary_count=sum(int((s==.2).sum()) for _,s in signals.values()))
summary['protocol_outcome']='ORDERING_CHANGE_REPEAT_FEASIBILITY' if sign_changes else ('LABEL_CHANGES_NO_ORDERING_CHANGE' if changed else 'NO_LABEL_CHANGES_UNINFORMATIVE')
with (root/'summary.json').open('x') as f: json.dump(summary,f,indent=2)
fig,axes=plt.subplots(1,2,figsize=(10,4),sharey=True)
for ax,(tag,(distance,speed)) in zip(axes,signals.items()):
    for i in range(8): ax.plot(range(1,51),distance[:,i]*1000,alpha=.65,lw=1,label=str(i))
    for mm,ls in [(20,':'),(25,'--'),(30,':')]: ax.axhline(mm,color='black',ls=ls,lw=.8)
    ax.set(title='PPO-'+tag.upper(),xlabel='Control step',yscale='log')
axes[0].set_ylabel('Cube–goal distance (mm, log scale)')
fig.suptitle('Frozen Q1 v3 trajectories; success also requires static arm')
fig.tight_layout();fig.savefig(root/'distance.png',dpi=180);fig.savefig(root/'distance.pdf');plt.close(fig)
print(json.dumps(summary,indent=2))
