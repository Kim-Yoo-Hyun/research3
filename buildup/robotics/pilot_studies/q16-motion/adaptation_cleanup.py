"""Preserve Q16 adaptation artifacts, then remove only this run's exited containers."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT / 'runs/q16/adaptation'


def main():
    for name in ('verify1', 'verify2', 'verify3'):
        verification = json.loads((OUT / name / 'summary.json').read_text())
        assert verification['verification']['status'] == 'passed'
    expected = {'collect1': 'collect', 'fit1': 'fit', 'eval1': 'evaluate', 'verify1': 'verify',
                'diagnosis1': 'diagnose', 'fit2': 'fit', 'eval2': 'evaluate',
                'verify2': 'verify', 'diagnosis2': 'diagnose',
                'eval3': 'evaluate', 'verify3': 'verify'}
    records = []
    build_records = []
    for path in sorted((OUT / 'jobs').glob('*.json')):
        row = json.loads(path.read_text())
        if row['stage'] == 'build':
            assert row['status'] == 'completed' and row['returncode'] == 0
            assert Path(row['log']).is_file() and Path(row['exit']).read_text().strip() == '0'
            build_records.append((path, row))
            continue
        assert row['stage'] == expected[row['attempt']]
        assert row['status'] == 'completed' and row['returncode'] == 0
        assert Path(row['log']).is_file() and Path(row['exit']).read_text().strip() == '0'
        assert Path(row['source_snapshot']).is_relative_to(OUT / 'jobs')
        records.append((path, row))
    assert len(build_records) == 1 and len(records) == len(expected)
    preserved = []
    files = [p for p in OUT.rglob('*') if p.is_file() and 'cache' not in p.relative_to(OUT).parts
             and p.name != 'preservation.json']
    files += [Path(row[key]) for _, row in build_records + records for key in ('log', 'exit')]
    for path in files:
        preserved.append(dict(path=str(path.relative_to(ROOT)), bytes=path.stat().st_size,
                              sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    manifest = OUT / 'preservation.json'
    assert not manifest.exists()
    manifest.write_text(json.dumps(dict(external_backup_verified=False, files=preserved), indent=2) + '\n')
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log = ROOT / 'logs' / f'{stamp}_q16_adaptation_cleanup.log'
    with log.open('x') as stream:
        stream.write(json.dumps(dict(preserved_files=len(preserved), manifest=str(manifest))) + '\n')
        stream.flush()
        for path, row in records:
            cid = row['inspection']['Id']
            current = json.loads(subprocess.check_output(['docker', 'inspect', cid]))[0]
            assert current['Name'] == '/' + row['container']
            assert current['Config']['Labels']['research3.workspace'] == str(ROOT)
            assert current['Config']['Labels']['research3.study'] == 'q16-adaptation'
            assert current['State']['Status'] == 'exited'
            assert current['Image'] == row['image_id']
            mounts = {item['Destination']: item['Source'] for item in current['Mounts']}
            assert mounts['/study'] == row['source_snapshot']
            assert mounts['/output'] == str(OUT)
            assert mounts['/home/research'] == str(OUT / 'cache')
            result = subprocess.run(['docker', 'rm', cid], capture_output=True, text=True, check=True)
            stream.write(json.dumps(dict(record=str(path.relative_to(ROOT)), container=cid,
                                         name=row['container'], removed=result.stdout.strip())) + '\n')
            stream.flush()
    print(json.dumps(dict(log=str(log), preserved_files=len(preserved),
                          removed_containers=len(records)), indent=2))


if __name__ == '__main__':
    main()
