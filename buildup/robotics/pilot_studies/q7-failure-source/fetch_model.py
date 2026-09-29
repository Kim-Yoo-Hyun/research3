"""Host-permitted resumable model download and byte verification; imports no model library."""
import concurrent.futures
import hashlib
import json
import subprocess
from pathlib import Path

root = Path('/home/yoohyun/research3')
owner = root/'buildup/robotics/pilot_studies/q7-failure-source'
spec = json.loads((owner/'model.json').read_text())
output = root/spec['local_path']
output.mkdir(parents=True, exist_ok=True)


def fetch(row):
    path = output/row['path']
    command = ['wget', '-c', '--quiet', '--timeout=30', '--tries=5', '-O', str(path), row['url']]
    subprocess.run(command, check=True)
    assert path.stat().st_size == row['bytes'], row['path']
    sha = hashlib.sha256()
    blob = hashlib.sha1(('blob '+str(row['bytes'])+'\0').encode())
    with path.open('rb') as stream:
        while chunk := stream.read(8*1024*1024):
            sha.update(chunk); blob.update(chunk)
    if row.get('lfs_sha256'):
        assert sha.hexdigest() == row['lfs_sha256'], row['path']
    else:
        assert blob.hexdigest() == row['git_blob_sha1'], row['path']
    print('verified', row['path'], row['bytes'], flush=True)
    return {'path': row['path'], 'bytes': row['bytes'], 'sha256': sha.hexdigest()}


with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    results = list(pool.map(fetch, spec['files']))
(output/'download.json').write_text(json.dumps({'status':'completed','revision':spec['revision'],'files':results},indent=2)+'\n')
print('COMPLETED',len(results),'files',sum(x['bytes'] for x in results),'bytes',flush=True)
