"""Remove only stopped containers recorded by this study, after local preservation checks."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT / 'runs/q3/timestep'
records = []
for path in sorted((OUT / 'jobs').glob('*.json')):
    record = json.loads(path.read_text())
    if record['stage'] == 'build' or record.get('container_removed'):
        continue
    assert record['status'] in ('completed', 'failed')
    assert record['returncode'] != 125, 'Creation error needs explicit ownership review'
    saved = record['container_inspect']
    current = json.loads(subprocess.check_output(['docker', 'inspect', saved['Id']]))[0]
    assert current['Id'] == saved['Id'] and current['Name'] == '/' + record['container']
    assert current['State']['Status'] == 'exited' and not current['State']['Running']
    assert current['Image'] == record['image_id']
    assert current['Config']['Labels']['research3.workspace'] == str(ROOT)
    assert current['Config']['Labels']['research3.study'] == 'q3-timestep'
    mounts = {m['Destination']: m for m in current['Mounts']}
    assert mounts['/study']['Source'] == str(HERE) and not mounts['/study']['RW']
    assert mounts['/output']['Source'] == str(OUT) and mounts['/output']['RW']
    index = record['command'].index(record['image_id'])
    assert current['Config']['Cmd'] == record['command'][index+1:]
    assert Path(record['log']).is_file() and Path(record['exit']).is_file()
    attempt = OUT / record['attempt']
    assert attempt.is_dir() and (attempt / 'observe.py').is_file()
    verification = attempt / 'verification.json'
    if record['status'] == 'completed':
        assert json.loads(verification.read_text())['status'] == 'PASS'
        for line in (attempt / 'checksums.txt').read_text().splitlines():
            expected, filename = line.split('  ', 1)
            assert hashlib.sha256((attempt / filename).read_bytes()).hexdigest() == expected
    # Log and inspect remain on the host; no raw outputs are stored solely in the container.
    files = [p for p in attempt.iterdir() if p.is_file()]
    preserved = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    subprocess.run(['docker', 'rm', current['Id']], check=True)
    record['container_removed'] = True
    record['preserved_files_at_cleanup'] = preserved
    path.write_text(json.dumps(record, indent=2) + '\n')
    records.append({'container': record['container'], 'id': current['Id'], 'files': len(files)})
print(json.dumps({'removed': records}, indent=2))
