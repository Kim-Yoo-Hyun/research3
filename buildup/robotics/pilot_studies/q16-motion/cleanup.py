"""Preserve local artifacts, then remove only containers recorded by this study launcher."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
OUT=ROOT/'runs/q16/motion'


def main():
    verification=json.loads((OUT/'verify1/summary.json').read_text())
    assert verification['verification']['status']=='passed'
    assert (OUT/'diagnosis1/diagnosis.json').exists()
    expected={'dev1':'failed','dev2':'completed','train1':'completed','fit1':'completed',
              'eval1':'completed','verify1':'completed','diagnosis1':'completed'}
    records=[]
    for p in sorted((OUT/'jobs').glob('*.json')):
        r=json.loads(p.read_text())
        if r['stage']=='build':continue
        assert r['attempt'] in expected and r['status']==expected[r['attempt']]
        assert Path(r['log']).is_file() and Path(r['exit']).is_file()
        assert Path(r['source_snapshot']).is_relative_to(OUT/'jobs')
        records.append((p,r))
    assert len(records)==7
    preserved=[]
    paths=[p for p in OUT.rglob('*') if p.is_file() and 'cache' not in p.relative_to(OUT).parts and p.name!='preservation.json']
    paths += [Path(r[key]) for _,r in records for key in ('log','exit')]
    for p in paths:
        data=p.read_bytes();preserved.append(dict(path=str(p.relative_to(ROOT)),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
    manifest=OUT/'preservation.json'
    assert not manifest.exists()
    manifest.write_text(json.dumps(dict(external_backup_verified=False,files=preserved),indent=2)+'\n')
    stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log=ROOT/'logs'/f'{stamp}_q16_cleanup.log'
    with log.open('x') as f:
        f.write(json.dumps(dict(preserved_files=len(preserved),manifest=str(manifest)))+'\n');f.flush()
        for p,r in records:
            cid=r['inspection']['Id']
            current=json.loads(subprocess.check_output(['docker','inspect',cid]))[0]
            assert current['Name']=='/'+r['container']
            assert current['Config']['Labels']['research3.workspace']==str(ROOT)
            assert current['Config']['Labels']['research3.study']=='q16-motion'
            assert current['State']['Status']=='exited'
            assert current['Image']==r['image_id']
            mounts={m['Destination']:m['Source'] for m in current['Mounts']}
            assert mounts['/study']==r['source_snapshot'] and mounts['/output']==str(OUT)
            assert mounts['/home/research']==str(OUT/'cache')
            # No force, no prune, no name-prefix inference, no image/data deletion.
            result=subprocess.run(['docker','rm',cid],capture_output=True,text=True,check=True)
            f.write(json.dumps(dict(record=str(p.relative_to(ROOT)),container=cid,name=r['container'],
                                   removed=result.stdout.strip()))+'\n');f.flush()
    print(json.dumps(dict(log=str(log),preserved_files=len(preserved),removed_containers=len(records)),indent=2))


if __name__=='__main__':main()
