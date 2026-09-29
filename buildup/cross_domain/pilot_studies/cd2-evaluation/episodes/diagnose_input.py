"""Container-only diagnosis of pickle versus NPY exports; no source mutation."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

cfg=json.loads(Path('/study/protocol.json').read_text())
df=pd.read_pickle('/input/nscore/data/LBM/lbm_data.pkl')[cfg['key']]
rows=[]
for task in cfg['tasks']:
    for metric,folder,col in [('success','LBM','success'),('progress','PC_LBM','task_progress')]:
        a=np.load(f'/input/nscore/data/{folder}/Part2/{task}.npy',allow_pickle=False)
        source=[np.asarray(df[(df.policy_type==p)&(df.skill==task)].iloc[0][col],dtype=float) for p in cfg['policies']]
        rows.append({'task':task,'metric':metric,'source_means':[float(x.mean()) for x in source],
                     'npy_means':a.mean(axis=0).tolist(), 'source_unique':[np.unique(x).tolist() for x in source],
                     'npy_unique':[np.unique(a[:,c]).tolist() for c in range(2)],
                     'exact_matches':[[bool(np.allclose(x,a[:,c],atol=1e-12,rtol=0)) for c in range(2)] for x in source],
                     'sorted_matches':[[bool(np.allclose(np.sort(x),np.sort(a[:,c]),atol=1e-12,rtol=0)) for c in range(2)] for x in source],
                     'source_prefixes':[x[:8].tolist() for x in source],'npy_prefixes':a[:8].tolist()})
Path('/output/input_diagnosis.json').write_text(json.dumps(rows,indent=2)+'\n')
for row in rows:
    print(json.dumps({k:row[k] for k in ['task','metric','source_means','npy_means','exact_matches','sorted_matches']}))
