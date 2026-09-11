"""Bounded orchestration inside the new Docker image; workers use fresh processes."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
W=Path('/work');O=Path('/outputs')
P=json.loads((W/'protocol.json').read_text())


def run(script,args,log):
    with open('/logs/'+log,'w') as f:
        try:
            r=subprocess.run([sys.executable,str(W/script),*args],stdout=f,stderr=subprocess.STDOUT,timeout=150 if script=='collect.py' else 300)
            return r.returncode
        except subprocess.TimeoutExpired:return 124


def main():
    assert not (O/'job.json').exists(), 'existing attempt bundle must be preserved'
    freeze=json.loads((W/'freeze.json').read_text())
    for name,h in freeze['files'].items():assert hashlib.sha256((W/name).read_bytes()).hexdigest()==h,name
    inputs=json.loads((W/'inputs.json').read_text())
    for r in inputs['fast']:assert hashlib.sha256((Path('/inputs/fast')/r['name']).read_bytes()).hexdigest()==r['sha256']
    for r in inputs['maniskill_files']:
        relative=r['path'].split(inputs['maniskill_commit']+'/',1)[1]
        assert hashlib.sha256((Path('/opt/ManiSkill')/relative).read_bytes()).hexdigest()==r['sha256']
    for f in ['dependencies.lock','os-packages.lock']:shutil.copy('/opt/'+f,O/f)
    for f in ['protocol.json','freeze.json','inputs.json']:shutil.copy(W/f,O/f)
    start=time.time();jobs=[]
    for seed in P['seeds']:
        modes=['generation']
        for mode in modes:
            rc=run('collect.py',['--seed',str(seed),'--mode',mode],f'20260908_q11_seed{seed}_{mode}.log')
            jobs.append({'seed':seed,'mode':mode,'returncode':rc})
            receipt=O/f'seed_{seed}'/(mode+'.json')
            if rc!=0:
                print('worker failed',seed,mode,rc,flush=True)
            if mode=='generation' and rc==0 and json.loads(receipt.read_text())['status']=='completed':
                modes.extend([f'replay_{j}' for j in range(P['replay_repeats'])])
            (O/'job.json').write_text(json.dumps({'status':'running','workers':jobs},indent=2))
    if all(j['returncode']==0 for j in jobs):
        c=run('codec.py',[],'20260908_q11_codec.log')
        v=run('verify.py',[],'20260908_q11_verify.log') if c==0 else None
    else:c=v=None
    status='completed' if c==0 and v==0 else 'failed'
    out={'status':status,'workers':jobs,'codec_exit':c,'verification_exit':v,'elapsed_seconds':time.time()-start}
    (O/'job.json').write_text(json.dumps(out,indent=2))
    hashes={str(p.relative_to(O)):hashlib.sha256(p.read_bytes()).hexdigest() for p in O.rglob('*') if p.is_file() and p.name!='outputs.sha256.json'}
    (O/'outputs.sha256.json').write_text(json.dumps(hashes,indent=2))
    print(json.dumps(out),flush=True)
    return 0 if status=='completed' else 1


if __name__=='__main__':sys.exit(main())
