"""Resume the two large checkpoint files through validated disjoint HTTP ranges."""
import concurrent.futures
import json
import os
import subprocess
import threading
import time
import urllib.request
from pathlib import Path

root=Path('/home/yoohyun/research3')
owner=root/'buildup/robotics/pilot_studies/q7-failure-source'
spec=json.loads((owner/'model.json').read_text())
cache=root/spec['local_path']
journal=cache/'ranges.json'
lock=threading.Lock()
large=[r for r in spec['files'] if r['bytes']>100_000_000]
if journal.exists():
    state=json.loads(journal.read_text())
else:
    state={'revision':spec['revision'],'files':{r['path']:{'prefix_bytes':(cache/r['path']).stat().st_size,'completed':[]} for r in large}}
    journal.write_text(json.dumps(state,indent=2)+'\n')
assert state['revision']==spec['revision']
fds={}
tasks=[]
chunk_size=64*1024*1024
for r in large:
    fd=os.open(cache/r['path'],os.O_RDWR)
    fds[r['path']]=fd
    progress=state['files'][r['path']]
    os.ftruncate(fd,r['bytes'])
    for start in range(progress['prefix_bytes'],r['bytes'],chunk_size):
        end=min(start+chunk_size,r['bytes'])-1
        if [start,end] not in progress['completed']:tasks.append((r,start,end))


def fetch(task):
    r,start,end=task; fd=fds[r['path']]
    for attempt in range(4):
        try:
            request=urllib.request.Request(r['url'],headers={'Range':f'bytes={start}-{end}'})
            with urllib.request.urlopen(request,timeout=60) as resp:
                assert resp.status==206 and resp.headers.get('Content-Range')==f"bytes {start}-{end}/{r['bytes']}",dict(resp.headers)
                offset=start
                while data:=resp.read(min(1024*1024,end-offset+1)):
                    sent=0
                    while sent<len(data):sent+=os.pwrite(fd,data[sent:],offset+sent)
                    offset+=len(data)
                    if offset>end:break
                assert offset==end+1,(offset,end)
            os.fsync(fd)
            with lock:
                state['files'][r['path']]['completed'].append([start,end])
                temp=journal.with_suffix('.tmp');temp.write_text(json.dumps(state,indent=2)+'\n');temp.replace(journal)
            print('range_complete',r['path'],start,end,flush=True)
            return
        except Exception as error:
            print('range_retry',r['path'],start,attempt,type(error).__name__,str(error)[:200],flush=True)
            if attempt==3:raise
            time.sleep(2)


try:
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:list(pool.map(fetch,tasks))
finally:
    for fd in fds.values():os.close(fd)
# Performs complete upstream hash verification and writes the model completion receipt.
subprocess.run(['python3',str(owner/'fetch_model.py')],check=True)
