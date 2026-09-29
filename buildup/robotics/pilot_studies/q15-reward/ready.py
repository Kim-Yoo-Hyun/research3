"""Bounded runtime parity, material and formula checks, followed by two PPO updates."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
from common import write_json, sha

p=argparse.ArgumentParser(); p.add_argument('--attempt',required=True); a=p.parse_args()
out=Path('/output')/a.attempt
assert not (out/'ready.json').exists()
commands=[]
for name,options in [('official',['--official']),('native',[]),('no_grasp',['--variant','no_grasp']),
                     ('half',['--variant','half']),('mass',['--density','2']),
                     ('friction',['--friction','0.5']),('joint',['--density','2','--friction','0.5'])]:
    cmd=[sys.executable,'-B','/study/evaluate.py','--output',str(out/name),*options]
    commands.append(cmd)
    if (out/f'{name}.npz').exists():
        meta=json.loads((out/f'{name}.json').read_text())
        assert sha(out/f'{name}.npz')==meta['trace_sha256']
    else:
        subprocess.run(cmd,check=True,timeout=180)
original=dict(np.load(out/'official.npz'))
for name in ['native','no_grasp','half']:
    d=dict(np.load(out/f'{name}.npz'))
    for key in original:
        if key!='reward': assert np.array_equal(d[key],original[key]),(name,key)
assert np.array_equal(np.load(out/'native.npz')['reward'],original['reward'])
from verify import check_materials, check_reward
metas={name:json.loads((out/f'{name}.json').read_text()) for name in ['official','native','no_grasp','half','mass','friction','joint']}
for name,meta in metas.items(): check_materials(meta['config'],metas['official']['config'],meta['density'],meta['friction'])
subprocess.run([sys.executable,'-B','/study/formula.py','--output',str(out/'formula.npz')],check=True,timeout=30)
f=dict(np.load(out/'formula.npz'))
for variant in ['native','no_grasp','half']: check_reward(f,variant,f[variant])
fit=out/'training_smoke'; fit.mkdir()
with (fit/'stdout.log').open('x') as stream:
    cmd=[sys.executable,'-B','-u','/study/train.py','--variant','native','--seed','909','--updates','2']
    commands.append(cmd); subprocess.run(cmd,cwd=fit,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=300)
assert (fit/'checkpoint_2.pt').exists()
write_json(out/'ready.json',dict(status='passed',commands=commands,parity_variants=3,material_conditions=7,
                                constructed_formula_cases=24,training_smoke_updates=2,
                                smoke_seed=909,smoke_not_in_analysis=True))
print('READY PASSED',flush=True)
