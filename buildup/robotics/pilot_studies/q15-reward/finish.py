"""Host stdlib background handoff: evaluation completion -> Docker verification -> preservation."""
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
OUT=ROOT/'runs/q15/reward/v1'
JOBS=OUT.parent/'jobs'
def read_json(path):
    while True:
        try: return json.loads(path.read_text())
        except json.JSONDecodeError: time.sleep(0.1)

while True:
    status=read_json(OUT/'run_status.json')
    if status['status'] in ('completed','failed'): break
    time.sleep(10)
assert status['status']=='completed',status.get('error')
# Wait for the host launch record to preserve the completed container inspection.
run_record=JOBS/'20260918_140535_277414_run.json'
while read_json(run_record)['status']=='running': time.sleep(1)
existing=set(JOBS.glob('*_verify.json'))
subprocess.run(['python3',str(HERE/'job.py'),'verify','v1'],check=True,cwd=ROOT)
new=set(JOBS.glob('*_verify.json'))-existing
assert len(new)==1
record=new.pop()
while True:
    state=read_json(record)
    if state['status'] in ('completed','failed'): break
    time.sleep(5)
assert state['status']=='completed',state.get('log')
assert json.loads((OUT/'verification.json').read_text())['status']=='passed'
for entry in json.loads((OUT/'manifest.json').read_text()):
    p=OUT/entry['path']
    assert p.stat().st_size==entry['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256']
for name in ['summary.json','verification.json','episodes.csv','analysis.json','runtime.json','installed.lock','os-packages.lock']:
    shutil.copyfile(OUT/name,HERE/name)
subprocess.run(['python3',str(HERE/'cleanup.py')],check=True,cwd=ROOT)
print('FULL RUN VERIFIED, COMPACT RESULTS COPIED, OWN STOPPED CONTAINERS CLEANED',flush=True)
