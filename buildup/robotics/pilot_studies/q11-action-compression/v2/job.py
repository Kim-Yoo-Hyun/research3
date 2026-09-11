"""Calibration is sealed before any held-out generation; no outcome-adaptive retries."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
W=Path('/work');O=Path('/outputs');P=json.loads((W/'protocol.json').read_text())


def run(seed,mode):
    log=Path('/logs')/f'seed_{seed}_{mode}.log'
    with log.open('w') as f:
        try:
            rc=subprocess.run([sys.executable,'/work/collect.py','--seed',str(seed),'--mode',mode],stdout=f,stderr=subprocess.STDOUT,timeout=150).returncode
        except subprocess.TimeoutExpired:rc=124
    return {'seed':seed,'mode':mode,'returncode':rc}


def main():
    assert not (O/'job.json').exists(),'refuse existing outcome bundle'
    freeze=json.loads((W/'freeze.json').read_text())
    for name,h in freeze['files'].items():assert hashlib.sha256((W/name).read_bytes()).hexdigest()==h,name
    for name,h in freeze['baseline_files'].items():assert hashlib.sha256((Path('/baseline')/name).read_bytes()).hexdigest()==h,name
    inputs=json.loads(Path('/baseline/inputs.json').read_text())
    for r in inputs['fast']:assert hashlib.sha256((Path('/inputs/fast')/r['name']).read_bytes()).hexdigest()==r['sha256']
    for r in inputs['maniskill_files']:
        relative=r['path'].split(inputs['maniskill_commit']+'/',1)[1]
        assert hashlib.sha256((Path('/opt/ManiSkill')/relative).read_bytes()).hexdigest()==r['sha256']
    for name in ['protocol.json','freeze.json']:shutil.copy(W/name,O/name)
    for name in ['dependencies.lock','os-packages.lock']:shutil.copy('/opt/'+name,O/name)
    # These import the frozen offline analysis and unchanged v1 label reconstruction only.
    import evaluate
    import prepare
    start=time.time();workers=[];eligibility=[]
    def receipt(status,**extra):
        (O/'job.json').write_text(json.dumps({'status':status,'workers':workers,'eligibility':eligibility,'elapsed_seconds':time.time()-start,**extra},indent=2))
    def generate(seeds):
        valid=[]
        for seed in seeds:
            w=run(seed,'generation');workers.append(w);receipt('running')
            if w['returncode']!=0:raise RuntimeError(f'generation process {seed}: {w}')
            r=json.loads((O/f'seed_{seed}'/'generation.json').read_text())
            if r['status']!='completed':eligibility.append({'seed':seed,'status':r['status']});continue
            assert evaluate.record(seed,'generation')['valid'],'independent original label failure'
            for j in range(P['replay_repeats']):
                mode=f'replay_{j}';w=run(seed,mode);workers.append(w);receipt('running')
                if w['returncode']!=0:raise RuntimeError(f'replay process {seed}: {w}')
                assert evaluate.record(seed,mode)['valid'],'original replay mismatch'
            eligibility.append({'seed':seed,'status':'replay_valid'});valid.append(seed)
        return valid
    try:
        cal=generate(P['calibration_seeds'])
        if len(cal)<P['calibration_min_completed']:receipt('INSUFFICIENT_CALIBRATION');return 0
        calibration=prepare.calibration(cal)
        calhash=hashlib.sha256((O/'calibration.json').read_bytes()).hexdigest()
        (O/'calibration.sha256').write_text(calhash+'\n')
        heldout=generate(P['heldout_seeds'])
        planned={seed:prepare.plans(seed,calibration) for seed in heldout}
        planhash={str(seed):hashlib.sha256((O/f'seed_{seed}'/'planned/manifest.json').read_bytes()).hexdigest() for seed in heldout}
        (O/'plans.sha256.json').write_text(json.dumps(planhash,indent=2))
        # All plans frozen before the first compressed-action rollout.
        for seed,names in planned.items():
            for name in names:
                assert len(workers)<P['max_trajectories']
                workers.append(run(seed,name));receipt('running',calibration_sha256=calhash)
                if workers[-1]['returncode']!=0:raise RuntimeError(f'variant process: {workers[-1]}')
        assert hashlib.sha256((O/'calibration.json').read_bytes()).hexdigest()==calhash
        for seed,h in planhash.items():assert hashlib.sha256((O/f'seed_{seed}'/'planned/manifest.json').read_bytes()).hexdigest()==h
        result=evaluate.summarize(heldout)
        receipt('completed',decision=result['decision'],calibration_sha256=calhash)
    except Exception as exc:
        receipt('failed',error=type(exc).__name__+': '+str(exc));raise
    finally:
        # Caches and logs are not scientific payload; they remain on disk but outside this manifest.
        files={str(p.relative_to(O)):hashlib.sha256(p.read_bytes()).hexdigest() for p in O.rglob('*') if p.is_file() and 'cache' not in p.relative_to(O).parts and p.name!='outputs.sha256.json'}
        (O/'outputs.sha256.json').write_text(json.dumps(files,indent=2))
    return 0


if __name__=='__main__':sys.exit(main())
