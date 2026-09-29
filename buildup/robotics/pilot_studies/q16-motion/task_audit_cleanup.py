"""Hash Q16 task-audit artifacts and remove only its verified exited containers."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT / 'runs/q16/task_audit'


def main():
    result = json.loads((OUT / 'verify2/verification.json').read_text())
    assert result['status'] == 'passed' and result['trace_checks'] == 48
    assert result['paired_seeds'] == 8
    records = []
    all_rows = []
    for path in sorted((OUT / 'jobs').glob('*.json')):
        row = json.loads(path.read_text())
        assert row['status'] in ('completed', 'failed')
        assert Path(row['log']).is_file()
        assert Path(row['exit']).is_file()
        assert int(Path(row['exit']).read_text().strip()) == row['returncode']
        all_rows.append(row)
        if row['stage'] != 'build':
            assert Path(row['source_snapshot']).is_relative_to(OUT / 'jobs')
            records.append((path, row))
    stages = {row['stage'] for _, row in records if row['status'] == 'completed'}
    assert {'smoke', 'verify'} <= stages
    assert sum(row['stage'] == 'smoke' and row['status'] == 'completed' for _, row in records) >= 4
    assert sum(row['stage'] == 'demo' and row['status'] == 'completed' for _, row in records) == 2
    assert (OUT / 'demo2/demo.json').is_file()
    assert (OUT / 'demos/PushT-v1.zip').stat().st_size == 35715188
    assert hashlib.sha256((OUT / 'demos/PushT-v1.zip').read_bytes()).hexdigest() == 'c2960e5d5dcc99d04fb4506b8a6bb8d8232b54f75e9f4fd0462189256f84e851'
    paths = [p for p in OUT.rglob('*') if p.is_file() and 'cache' not in p.relative_to(OUT).parts
             and p.name != 'preservation.json']
    paths += [Path(row[key]) for row in all_rows for key in ('log', 'exit')]
    preservation = []
    for path in paths:
        preservation.append(dict(path=str(path.relative_to(ROOT)), bytes=path.stat().st_size,
                                 sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    manifest = OUT / 'preservation.json'
    assert not manifest.exists()
    manifest.write_text(json.dumps(dict(external_backup_verified=False, files=preservation), indent=2) + '\n')
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log = ROOT / 'logs' / f'{stamp}_q16_task_audit_cleanup.log'
    with log.open('x') as stream:
        stream.write(json.dumps(dict(preserved_files=len(preservation), manifest=str(manifest))) + '\n')
        stream.flush()
        for path, row in records:
            cid = row['inspection']['Id']
            current = json.loads(subprocess.check_output(['docker', 'inspect', cid]))[0]
            assert current['Name'] == '/' + row['container']
            assert current['Config']['Labels']['research3.workspace'] == str(ROOT)
            assert current['Config']['Labels']['research3.study'] == 'q16-task-audit'
            assert current['State']['Status'] == 'exited'
            assert current['Image'] == row['image_id']
            mounts = {item['Destination']: item['Source'] for item in current['Mounts']}
            assert mounts['/study'] == row['source_snapshot']
            assert mounts['/output'] == str(OUT)
            assert mounts['/home/research'] == str(OUT / 'cache')
            deleted = subprocess.run(['docker', 'rm', cid], capture_output=True, text=True, check=True)
            stream.write(json.dumps(dict(record=str(path.relative_to(ROOT)), container=cid,
                                         removed=deleted.stdout.strip())) + '\n')
            stream.flush()
    print(json.dumps(dict(log=str(log), preserved_files=len(preservation),
                          removed_containers=len(records)), indent=2))


if __name__ == '__main__':
    main()
