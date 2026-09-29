"""Hash the bounded Q16 branch attempts and their logs without importing model code."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT / 'runs/q16/branches'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    files = sorted(p for p in OUT.rglob('*') if p.is_file() and p.name != 'preservation.json')
    files += sorted((ROOT / 'logs').glob('*_q16_branches_*.log'))
    files += sorted((ROOT / 'logs').glob('*_q16_branches_*.exit'))
    entries = [dict(path=str(p.relative_to(ROOT)), bytes=p.stat().st_size, sha256=digest(p)) for p in files]
    for item in entries:
        path = ROOT / item['path']
        assert path.stat().st_size == item['bytes'] and digest(path) == item['sha256']
    path = OUT / 'preservation.json'
    path.write_text(json.dumps(dict(status='verified_local_only', file_count=len(entries),
                                    entries=entries), indent=2) + '\n')
    print(json.dumps(dict(status='verified_local_only', file_count=len(entries),
                          total_bytes=sum(x['bytes'] for x in entries), manifest=str(path)), indent=2))


if __name__ == '__main__':
    main()
