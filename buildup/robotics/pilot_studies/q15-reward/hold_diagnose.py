"""Post hoc case inspection of verified traces; no new rollout or thresholds."""
import hashlib
import json
from pathlib import Path
import shutil
import numpy as np

out=Path('/output')
assert json.loads((out/'verification.json').read_text())['status']=='passed'
target=out/'diagnosis'
target.mkdir()
shutil.copyfile('/study/hold_diagnose.py',target/'hold_diagnose.py')
cases=json.loads((out/'cases.json').read_text())
selected={(p['variant'],p['training_seed'],p['initial_state']):p
          for p in cases['changed']+cases['remaining_failures']}
rows=[]
for (variant,seed,i),pair in sorted(selected.items()):
    paths={route:out/'evaluation'/f'{variant}_{seed}_{route}.npz' for route in ['continued','hold']}
    traces={route:dict(np.load(path,allow_pickle=False)) for route,path in paths.items()}
    h=traces['hold']; first=pair['hold']['first_success_step']
    row=dict(variant=variant,training_seed=seed,initial_state=i,
             improved=pair['improved'],worsened=pair['worsened'],first_success_step=first,
             source_sha256={r:hashlib.sha256(p.read_bytes()).hexdigest() for r,p in paths.items()})
    if first is not None:
        row['at_first_success']=dict(goal_distance_mm=float(np.linalg.norm(h['cube_pose'][first,i,:3]-h['goal'][first,i])*1000),
            max_arm_velocity_rad_s=float(np.max(np.abs(h['qvel'][first,i,:7]))),
            grasp=bool(h['is_grasped'][first-1,i]),cube_velocity_m_s=h['cube_velocity'][first,i].tolist(),
            cube_angular_velocity_rad_s=h['cube_angular_velocity'][first,i].tolist())
        row['routes']={}
        for route,d in traces.items():
            row['routes'][route]=dict(
                end_success=bool(d['success'][-1,i]),end_grasp=bool(d['is_grasped'][-1,i]),
                end_static=bool(d['is_robot_static'][-1,i]),
                end_goal_distance_mm=float(np.linalg.norm(d['cube_pose'][-1,i,:3]-d['goal'][-1,i])*1000),
                cube_displacement_mm=((d['cube_pose'][-1,i,:3]-d['cube_pose'][first,i,:3])*1000).tolist(),
                tcp_displacement_mm=((d['tcp_pose'][-1,i,:3]-d['tcp_pose'][first,i,:3])*1000).tolist(),
                max_arm_displacement_rad=float(np.max(np.abs(d['qpos'][first:,i,:7]-d['qpos'][first,i,:7]))),
                grasp_false_post_success_steps=int((~d['is_grasped'][first:,i]).sum()))
    rows.append(row)
value=dict(exploratory_post_hoc=True,new_rollouts=0,cases=rows,
           boundary='State/kinematic descriptions, not contact-force or causal training-mechanism identification.')
(target/'diagnosis.json').write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
manifest=[dict(path=p.name,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
          for p in sorted(target.iterdir()) if p.is_file()]
(target/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(dict(cases=len(rows),new_rollouts=0)))
