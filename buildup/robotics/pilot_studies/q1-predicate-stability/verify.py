"""Independent raw-state reconstruction of all 96 labels and source constituent checks."""
import csv
import hashlib
import json
import math
from pathlib import Path
import h5py

root=Path('/outputs')
with (root/'labels.csv').open() as f: rows=list(csv.DictReader(f))
assert len(rows)==16 and len({(r['policy'],r['episode']) for r in rows})==16
reconstructed={};boundary=0
initial={}
for tag in ['ee','joint']:
    with h5py.File(root/tag/'trajectory.h5') as f:
        state=f['snapshots/state']
        cube=state['actors/cube'][:]; goal=state['actors/goal_site'][:]
        robot=state['articulations/panda'][:]
        static_threshold=float(robot.dtype.type(.2))
        assert cube.shape[:2]==(51,8) and robot.shape==(51,8,31)
        initial[tag]=(cube[0].tolist(),goal[0].tolist(),robot[0].tolist())
        for i in range(8):
            row=next(r for r in rows if r['policy']==tag and int(r['episode'])==i)
            success={mm:[] for mm in [20,25,30]}; ds=[]
            for t in range(1,51):
                distance=math.sqrt(sum((float(cube[t,i,j])-float(goal[t,i,j]))**2 for j in range(3)))
                qvel=robot[t,i,22:29]
                static=all(abs(float(v))<=static_threshold for v in qvel)
                boundary+=sum(abs(float(v))==static_threshold for v in qvel)
                ds.append(distance)
                assert static==bool(f['official/is_robot_static'][t-1,i])
                assert (distance<=.025 and static)==bool(f['official/success'][t-1,i])
                for mm in success: success[mm].append(distance<=mm/1000 and static)
            pred={}
            for mm,seq in success.items():
                for name,value in [('once',any(seq)),('end',seq[-1])]:
                    key=f'{mm}_{name}';assert int(row[key])==value;pred[key]=int(value)
            assert abs(float(row['minimum_distance_m'])-min(ds))<1e-12
            assert abs(float(row['final_distance_m'])-ds[-1])<1e-12
            reconstructed[tag,i]=pred
assert initial['ee']==initial['joint']
summary=json.loads((root/'summary.json').read_text())
rates={}
for key in next(iter(reconstructed.values())):
    rates[key]={tag:sum(r[key] for (tag2,i),r in reconstructed.items() if tag2==tag)/8 for tag in ['ee','joint']}
    rates[key]['difference']=rates[key]['ee']-rates[key]['joint']
assert summary['rates']==rates
sign=lambda x:(x>0)-(x<0)
ref=rates['25_once']['difference']
assert summary['sign_changes']==[k for k,v in rates.items() if sign(v['difference'])!=sign(ref)]
assert summary['strict_reversals']==[k for k,v in rates.items() if ref*v['difference']<0]
receipt=dict(status='VERIFIED',episodes=16,labels=96,official_step_labels=800,
             raw_initialization_exact=True,static_boundary_values=boundary,
             files={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in [root/'ee/trajectory.h5',root/'joint/trajectory.h5',root/'labels.csv',root/'summary.json']})
with (root/'verification.json').open('x') as f: json.dump(receipt,f,indent=2)
print(json.dumps(receipt,indent=2))
