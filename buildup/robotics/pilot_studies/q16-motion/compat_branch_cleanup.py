"""Delete only completed containers proven to belong to the Q16 branch diagnostic."""
import datetime
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT / 'runs/q16/branches'


def main():
    removed = []
    for record in sorted((OUT / 'jobs').glob('*.json')):
        rec = json.loads(record.read_text())
        if rec.get('stage') not in ('fit', 'diagnose', 'validate') or rec.get('status') not in ('completed', 'failed'):
            continue
        result = subprocess.run(['docker', 'inspect', rec['container']], capture_output=True, text=True)
        if result.returncode != 0:
            continue
        info = json.loads(result.stdout)[0]
        mounts = {m['Destination']: m['Source'] for m in info['Mounts']}
        checks = [info['State']['Status'] == 'exited', not info['State']['Running'],
                  info['Name'] == '/' + rec['container'], info['Id'] == rec['inspection']['Id'],
                  info['Image'] == rec['image_id'],
                  info['Config']['Labels'].get('research3.workspace') == str(ROOT),
                  info['Config']['Labels'].get('research3.study') == 'q16-branches',
                  mounts.get('/study') == rec['source_snapshot'],
                  mounts.get('/output') == str(OUT),
                  mounts.get('/previous') == str(ROOT / 'runs/q16/compat_gpu'),
                  Path(rec['log']).exists(), Path(rec['exit']).exists()]
        if not all(checks):
            raise RuntimeError(f'Ownership/preservation mismatch: {rec["container"]}: {checks}')
        subprocess.run(['docker', 'rm', info['Id']], check=True, capture_output=True)
        removed.append(dict(id=info['Id'], name=rec['container'], job=str(record)))
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    path = ROOT / 'logs' / f'{stamp}_q16_branches_cleanup.log'
    path.write_text(json.dumps(dict(removed=removed), indent=2) + '\n')
    print(json.dumps(dict(count=len(removed), log=str(path)), indent=2))


if __name__ == '__main__':
    main()
