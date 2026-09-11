"""Post-result descriptive diagnosis on frozen trajectories; no new labels or policy runs."""
import json
from pathlib import Path
import h5py
import numpy as np

root=Path('/outputs');rows=[]
for tag in ['ee','joint']:
    with h5py.File(root/tag/'trajectory.h5') as f:
        d=np.linalg.norm(f['snapshots/cube'][1:].astype(float)-f['snapshots/goal'][1:].astype(float),axis=-1)
        v=np.abs(f['snapshots/qvel'][1:,:,:7]).max(axis=-1)
        for i in range(8):
            static=v[:,i]<=.2
            mask=(d[:,i]<=.025)&static
            near=np.where(d[:,i]<=.03)[0]
            rows.append(dict(policy=tag,episode=i,minimum_distance_mm=float(d[:,i].min()*1000),
                minimum_distance_while_static_mm=float(d[static,i].min()*1000) if static.any() else None,
                steps_within_30mm=(near+1).tolist(),
                speeds_within_30mm=v[near,i].astype(float).tolist(),
                first_official_success_step=int(np.where(mask)[0][0]+1) if mask.any() else None,
                final_distance_mm=float(d[-1,i]*1000),final_static=bool(static[-1]),
                success_retained_after_first=bool(mask[np.where(mask)[0][0]:].all()) if mask.any() else None))
with (root/'diagnosis.json').open('x') as f: json.dump(rows,f,indent=2)
for r in rows:
    if r['policy']=='ee' and r['first_official_success_step'] is None: print(json.dumps(r))
