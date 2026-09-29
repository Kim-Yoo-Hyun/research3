"""Run the selected nine fits and fixed evaluation matrix; never select by performance."""
import argparse
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from common import sha, write_json

p=argparse.ArgumentParser(); p.add_argument('--attempt',required=True); a=p.parse_args()
out=Path('/output')/a.attempt
assert not (out/'run_status.json').exists(), 'Use a fresh attempt; do not overwrite observations'
readiness=[p for p in Path('/output').glob('ready_*/ready.json') if json.loads(p.read_text())['status']=='passed']
assert readiness,'Run technical readiness first'
(out/'fits').mkdir(); (out/'evaluation').mkdir(); (out/'source').mkdir()
for f in Path('/study').iterdir():
    if f.is_file(): shutil.copyfile(f,out/'source'/f.name)
for name in ['installed.lock','os-packages.lock','requirements.lock']:
    shutil.copyfile(Path('/recipe')/name,out/name)
status=dict(status='running',training=[],evaluation=[],readiness=str(sorted(readiness)[-1]),
            readiness_sha256=sha(sorted(readiness)[-1]))
write_json(out/'run_status.json',status)
train_start=time.monotonic()
try:
    for seed,variant in itertools.product([101,202,303],['native','no_grasp','half']):
        fit=out/'fits'/f'{variant}_{seed}'; fit.mkdir()
        cmd=[sys.executable,'-B','-u','/study/train.py','--variant',variant,'--seed',str(seed)]
        start=time.monotonic()
        print('TRAIN',variant,seed,flush=True)
        with (fit/'stdout.log').open('x') as stream:
            result=subprocess.run(cmd,cwd=fit,stdout=stream,stderr=subprocess.STDOUT,timeout=min(1200,10800-(start-train_start)))
        status['training'].append(dict(variant=variant,seed=seed,seconds=time.monotonic()-start,exit=result.returncode,command=cmd))
        write_json(out/'run_status.json',status)
        assert result.returncode==0,(variant,seed,result.returncode)
        assert (fit/'checkpoint_97.pt').exists() and (fit/'checkpoint_195.pt').exists()
        print('TRAIN COMPLETE',variant,seed,status['training'][-1]['seconds'],flush=True)
    eval_start=time.monotonic()
    for variant,seed,iteration,(density,friction) in itertools.product(['native','no_grasp','half'],[101,202,303],[97,195],[(1.,1.),(2.,1.),(1.,0.5),(2.,0.5)]):
        name=f'{variant}_{seed}_u{iteration}_d{density:g}_f{friction:g}'
        cmd=[sys.executable,'-B','-u','/study/evaluate.py','--output',str(out/'evaluation'/name),
             '--checkpoint',str(out/'fits'/f'{variant}_{seed}'/f'checkpoint_{iteration}.pt'),
             '--variant',variant,'--density',str(density),'--friction',str(friction)]
        start=time.monotonic()
        with (out/'evaluation'/f'{name}.log').open('x') as stream:
            result=subprocess.run(cmd,stdout=stream,stderr=subprocess.STDOUT,timeout=min(180,3600-(start-eval_start)))
        status['evaluation'].append(dict(name=name,seconds=time.monotonic()-start,exit=result.returncode,command=cmd))
        write_json(out/'run_status.json',status)
        assert result.returncode==0,name
        print('EVALUATED',name,flush=True)
    status['status']='completed'
except BaseException as error:
    status['status']='failed'; status['error']=repr(error)
    raise
finally:
    write_json(out/'run_status.json',status)
