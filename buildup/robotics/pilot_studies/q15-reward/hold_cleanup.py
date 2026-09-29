"""Remove only stopped hold-study containers after verifying preserved outputs."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

here=Path(__file__).resolve().parent
root=here.parents[3]
base=root/'runs/q15/reward'
attempt=sys.argv[1]
assert attempt.replace('_','').isalnum()
out=base/attempt
assert json.loads((out/'verification.json').read_text())['status']=='passed'
preserved=[]
for folder in [out,out/'diagnosis']:
    for record in json.loads((folder/'manifest.json').read_text()):
        p=folder/record['path']
        assert p.stat().st_size==record['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==record['sha256']
        preserved.append(dict(path=str(p),sha256=record['sha256']))
log=root/'logs'/f'{datetime.datetime.now():%Y%m%d_%H%M%S}_q15_hold_cleanup.log'
record=dict(preserved_files=preserved,containers=[])
for path in sorted((base/'jobs').glob('*_hold_*.json')):
    job=json.loads(path.read_text())
    if job['attempt']!=attempt: continue
    assert job['stage'] in ('hold_run','hold_verify','hold_diagnose')
    assert job['status'] in ('completed','failed') and job['working_directory']==str(root)
    assert Path(job['log']).is_file() and Path(job['exit']).is_file()
    saved=job.get('container_inspect')
    if not saved: continue
    result=subprocess.run(['docker','inspect',saved['Id']],capture_output=True,text=True)
    if result.returncode: continue
    c=json.loads(result.stdout)[0]
    assert c['State']['Status'] in ('exited','created') and not c['State']['Running']
    assert c['Id']==saved['Id'] and c['Name'].lstrip('/')==job['container']
    assert c['Image']==job['image_id'] and c['Config']['Cmd']==saved['Config']['Cmd']
    assert c['Config']['Labels']['research3.workspace']==str(root)
    assert c['Config']['Labels']['research3.study']=='q15-hold'
    for source,destination,rw in [(here,'/study',False),(base/'v1','/input',False),(out,'/output',True)]:
        assert any(m['Source']==str(source) and m['Destination']==destination and m['RW']==rw for m in c['Mounts'])
    item=dict(job_record=str(path),inspection=c,removed=False,
              log_sha256=hashlib.sha256(Path(job['log']).read_bytes()).hexdigest())
    record['containers'].append(item)
    log.write_text(json.dumps(record,indent=2)+'\n')
    subprocess.run(['docker','rm',c['Id']],check=True,capture_output=True,text=True)
    item['removed']=True
    log.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(dict(log=str(log),verified_files=len(preserved),removed=[c['inspection']['Name'] for c in record['containers'] if c['removed']])))
