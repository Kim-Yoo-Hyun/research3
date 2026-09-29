"""Hash this study's local inputs/results/logs before owned-container cleanup."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT / 'runs/q16/pusht_repeat'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    paths = sorted(p for p in OUT.rglob('*') if p.is_file() and p.name != 'preservation.json')
    paths += sorted((ROOT / 'logs').glob('*_q16_pusht_repeat_*.log'))
    paths += sorted((ROOT / 'logs').glob('*_q16_pusht_repeat_*.exit'))
    rows = [dict(path=str(p.relative_to(ROOT)), bytes=p.stat().st_size, sha256=digest(p)) for p in paths]
    for row in rows:
        path = ROOT / row['path']
        assert path.stat().st_size == row['bytes'] and digest(path) == row['sha256']
    out = OUT / 'preservation.json'
    out.write_text(json.dumps(dict(status='verified_local_only', file_count=len(rows),
                                   entries=rows), indent=2) + '\n')
    print(json.dumps(dict(status='verified_local_only', count=len(rows),
                          bytes=sum(row['bytes'] for row in rows), manifest=str(out)), indent=2))


if __name__ == '__main__':
    main()
