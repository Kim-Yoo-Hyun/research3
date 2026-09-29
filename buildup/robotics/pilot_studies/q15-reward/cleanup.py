"""Host-only cleanup of stopped containers with this workspace's exact launch provenance."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
OUT=ROOT/'runs/q15/reward'
now=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
record={'removed':[],'skipped':[],'preserved_files':[]}
jobs=[json.loads(p.read_text()) for p in (OUT/'jobs').glob('*.json')]
running_outputs={Path(r['output']) for r in jobs if r.get('stage') in ('ready','run','verify','cases') and r['status'] not in ('completed','failed')}
for p in sorted(OUT.rglob('*')):
    if any(p.is_relative_to(root) for root in running_outputs): continue
    if p.is_file():
        record['preserved_files'].append(dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,
                                            sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
for path in sorted((OUT/'jobs').glob('*.json')):
    r=json.loads(path.read_text())
    if r.get('stage') not in ('ready','run','verify','cases') or r['status'] not in ('completed','failed'): continue
    saved=r.get('container_inspect')
    if not saved: continue
    assert r['working_directory']==str(ROOT)
    assert Path(r['log']).is_file() and Path(r['exit']).is_file()
    q=subprocess.run(['docker','inspect',saved['Id']],capture_output=True,text=True)
    if q.returncode: continue
    c=json.loads(q.stdout)[0]
    if c['State']['Status'] not in ('exited','created'):
        record['skipped'].append(dict(id=c['Id'],reason='not stopped')); continue
    assert c['Id']==saved['Id'] and c['Image']==r['image_id'] and c['Config']['Cmd']==saved['Config']['Cmd']
    assert c['Name'].lstrip('/')==r['container']
    assert c['Config']['Labels']['research3.workspace']==str(ROOT)
    assert c['Config']['Labels']['research3.study']=='q15-reward'
    assert any(m['Source']==str(HERE) and m['Destination']=='/study' and not m['RW'] for m in c['Mounts'])
    assert any(m['Source']==str(OUT) and m['Destination']=='/output' and m['RW'] for m in c['Mounts'])
    item=dict(id=c['Id'],name=c['Name'],job_record=str(path.relative_to(ROOT)),inspection=c,
              log_sha256=hashlib.sha256(Path(r['log']).read_bytes()).hexdigest())
    record['removed'].append(item)
    # Save preservation and inspection evidence before the irreversible container metadata removal.
    log=ROOT/'logs'/f'{now}_q15_cleanup.log'
    log.write_text(json.dumps(record,indent=2)+'\n')
    subprocess.run(['docker','rm',c['Id']],check=True,capture_output=True,text=True)
    item['removed']=True
    log.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'removed':[r['name'] for r in record['removed']],
                  'preserved_files':len(record['preserved_files']),'skipped':record['skipped']}))
