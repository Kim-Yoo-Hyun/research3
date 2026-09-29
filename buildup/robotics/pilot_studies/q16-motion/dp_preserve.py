"""Verify local source/checkpoint/outputs/logs before owned-container cleanup."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT / 'runs/q16/dp_reference'
COMMIT = '5ba07ac6661db573af695b419a7947ecb704690f'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    files = [p for p in OUT.rglob('*') if p.is_file() and p.name!='preservation.json']
    files += [ROOT/'external/q16'/f'diffusion_policy-{COMMIT}.tar.gz']
    files += [HERE/'dp_reference_summary.json']
    continuation = HERE/'dp_continuation_summary.json'
    if continuation.is_file():
        files += [continuation]
    files += list((ROOT/'logs').glob('*_q16_dp_reference_*.log'))
    files += list((ROOT/'logs').glob('*_q16_dp_reference_*.exit'))
    files = sorted(set(files))
    rows = [dict(path=str(path.relative_to(ROOT)), bytes=path.stat().st_size,
                 sha256=digest(path)) for path in files]
    for row in rows:
        path = ROOT/row['path']
        assert path.stat().st_size==row['bytes'] and digest(path)==row['sha256']
    output = OUT/'preservation.json'
    output.write_text(json.dumps(dict(status='verified_local_only', file_count=len(rows),
                                      entries=rows),indent=2)+'\n')
    print(json.dumps(dict(status='verified_local_only', files=len(rows),
                          bytes=sum(row['bytes'] for row in rows), manifest=str(output)),indent=2))


if __name__ == '__main__':
    main()
