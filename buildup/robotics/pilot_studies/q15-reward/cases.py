"""Post hoc inspection of all final-checkpoint failures; no new rollout or fitting."""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path
import shutil
import numpy as np

p=argparse.ArgumentParser(); p.add_argument('--attempt',required=True); a=p.parse_args()
out=Path('/output')/a.attempt
assert json.loads((out/'verification.json').read_text())['status']=='passed'
target=out/'case_analysis'; target.mkdir()
shutil.copyfile('/study/cases.py',target/'cases.py')
rows=list(csv.DictReader((out/'episodes.csv').open()))
cases=[]; grouped=collections.defaultdict(collections.Counter)
for r in rows:
    if int(r['update'])!=195 or int(r['success_at_end']): continue
    name=f"{r['variant']}_{r['training_seed']}_u195_d{float(r['density']):g}_f{float(r['friction']):g}"
    path=out/'evaluation'/f'{name}.npz'
    if not path.exists(): path=(out/'evaluation'/name).with_suffix('.npz')
    with np.load(path,allow_pickle=False) as d:
        i=int(r['initial_state'])
        placed=bool(d['is_obj_placed'][-1,i]); static=bool(d['is_robot_static'][-1,i])
        ever=bool(d['success'][:,i].any())
        assert ever==bool(int(r['success_once'])) and not (placed and static)
        cause='nonstatic_only' if placed else ('outside_goal_only' if static else 'outside_goal_and_nonstatic')
        group=f"{r['variant']}:d{float(r['density']):g}:f{float(r['friction']):g}"
        label=('after_success:' if ever else 'never_success:')+cause
        grouped[group][label]+=1
        events=np.flatnonzero(d['success'][:,i])
        cases.append(dict(variant=r['variant'],training_seed=int(r['training_seed']),initial_state=i,
            density=float(r['density']),friction=float(r['friction']),final_failure=label,
            first_success_step=int(events[0]+1) if len(events) else None,
            last_success_step=int(events[-1]+1) if len(events) else None,
            final_goal_distance_mm=float(r['final_goal_distance_mm']),
            final_arm_max_abs_velocity_rad_s=float(r['final_arm_max_abs_velocity_rad_s']),
            final_grasped=bool(d['is_grasped'][-1,i]),
            final_cube_height_m=float(d['cube_pose'][-1,i,2]),
            trace_path=str(path.relative_to(out)),trace_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
value=dict(post_hoc=True,new_rollouts=0,final_failures=len(cases),groups=dict(grouped),cases=cases,
    boundary='Outcome decomposition from existing traces; no causal contact-force or reward-mechanism claim.')
(target/'cases.json').write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
manifest=[dict(path=str(f.relative_to(out)),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest())
          for f in sorted(target.iterdir()) if f.is_file()]
(target/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(dict(final_failures=len(cases),groups=dict(grouped))))
