"""Frozen statistics, fresh originals, sealed support gate, then one bounded intervention."""
import hashlib,json,shutil,subprocess,sys,time
from pathlib import Path
W=Path('/work');O=Path('/outputs');P=json.loads((W/'protocol.json').read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def run(seed,mode):
    with (Path('/logs')/f'seed_{seed}_{mode}.log').open('w') as log:
        try:rc=subprocess.run([sys.executable,'/work/collect.py','--seed',str(seed),'--mode',mode],stdout=log,stderr=subprocess.STDOUT,timeout=150).returncode
        except subprocess.TimeoutExpired:rc=124
    return {'seed':seed,'mode':mode,'returncode':rc}
def main():
    assert not (O/'job.json').exists()
    freeze=json.loads((W/'freeze.json').read_text())
    for name,h in freeze['files'].items():assert sha(W/name)==h,name
    for name,h in freeze['baseline_files'].items():assert sha(Path('/baseline')/name)==h,name
    inputs=json.loads(Path('/baseline/inputs.json').read_text())
    for r in inputs['fast']:assert sha(Path('/inputs/fast')/r['name'])==r['sha256']
    for r in inputs['maniskill_files']:
        relative=r['path'].split(inputs['maniskill_commit']+'/',1)[1]
        assert sha(Path('/opt/ManiSkill')/relative)==r['sha256']
    for name in ['protocol.json','freeze.json','calibration.json']:shutil.copyfile(W/name,O/name)
    for name in ['dependencies.lock','os-packages.lock']:
        assert sha(Path('/opt')/name)==sha(Path('/baseline/v2')/name)
        shutil.copyfile(Path('/opt')/name,O/name)
    calhash=sha(O/'calibration.json');(O/'calibration.sha256').write_text(calhash+'\n')
    import prepare,evaluate,support
    start=time.time();workers=[];eligibility=[];valid=[];ph={}
    def receipt(status,**extra):
        (O/'job.json').write_text(json.dumps({'status':status,'workers':workers,'eligibility':eligibility,'elapsed_seconds':time.time()-start,'calibration_sha256':calhash,**extra},indent=2))
    def worker(seed,mode):
        assert len(workers)<P['max_trajectories']
        workers.append(run(seed,mode));receipt('running')
        assert workers[-1]['returncode']==0,f'worker process failure: {workers[-1]}'
    try:
        for seed in P['heldout_seeds']:
            worker(seed,'generation');r=json.loads((O/f'seed_{seed}/generation.json').read_text())
            if r['status']=='error':raise RuntimeError(f'collector error seed {seed}: '+r.get('error',''))
            if r['status']!='completed':eligibility.append({'seed':seed,'status':r['status']});continue
            assert evaluate.record(seed,'generation')['valid'],'independent original verification failed'
            for repeat in range(P['replay_repeats']):
                mode=f'replay_{repeat}';worker(seed,mode)
                assert evaluate.record(seed,mode)['valid'],'original replay mismatch'
            valid.append(seed);eligibility.append({'seed':seed,'status':'replay_valid'})
        cal=json.loads((O/'calibration.json').read_text());planned={s:prepare.plans(s,cal) for s in valid}
        manifests=[json.loads((O/f'seed_{s}/planned/manifest.json').read_text()) for s in valid]
        gate=support.assess(manifests);(O/'support.json').write_text(json.dumps(gate,indent=2))
        for seed in valid:
            for path in sorted((O/f'seed_{seed}/planned').iterdir()):ph[str(path.relative_to(O))]=sha(path)
        ph['support.json']=sha(O/'support.json')
        (O/'plans.sha256.json').write_text(json.dumps(ph,indent=2))
        # Stop before any compressed/localized action if source-only support is insufficient.
        if gate['decision']!='READY_FOR_INTERVENTION':
            receipt('completed',decision=gate['decision'],intervention_workers=0);return 0
        for seed,names in planned.items():
            for name in names:
                worker(seed,name)
                assert evaluate.record(seed,name)['valid'],'variant measurement failure'
        assert sha(O/'calibration.json')==calhash
        for name,h in ph.items():assert sha(O/name)==h,name
        result=evaluate.summarize(valid)
        receipt('completed',decision=result['decision'],intervention_workers=sum(len(names) for names in planned.values()))
    except Exception as exc:
        receipt('failed',decision='MEASUREMENT_INVALID',error=type(exc).__name__+': '+str(exc));raise
    finally:
        hashes={str(path.relative_to(O)):sha(path) for path in O.rglob('*') if path.is_file() and 'cache' not in path.relative_to(O).parts and path.name!='outputs.sha256.json'}
        (O/'outputs.sha256.json').write_text(json.dumps(hashes,indent=2))
    return 0
if __name__=='__main__':sys.exit(main())
