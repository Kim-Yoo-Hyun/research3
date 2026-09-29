"""Remove only completed, inspected Q16 compatibility containers from job records."""
import datetime
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def cleanup(device):
    if device not in ('cpu', 'gpu'):
        raise ValueError(device)
    out = ROOT / f'runs/q16/compat_{device}'
    label = f'q16-compat-{device}'
    removed = []
    for record in sorted((out / 'jobs').glob('*.json')):
        rec = json.loads(record.read_text())
        if rec.get('stage') == 'build' or rec.get('status') not in ('completed', 'failed'):
            continue
        name = rec['container']
        result = subprocess.run(['docker', 'inspect', name], capture_output=True, text=True)
        if result.returncode != 0:
            continue
        info = json.loads(result.stdout)[0]
        mounts = {m['Destination']: m['Source'] for m in info['Mounts']}
        checks = [not info['State']['Running'], info['State']['Status'] == 'exited',
                  info['Name'] == '/' + name, info['Id'] == rec['inspection']['Id'],
                  info['Image'] == rec['image_id'],
                  info['Config']['Labels'].get('research3.workspace') == str(ROOT),
                  info['Config']['Labels'].get('research3.study') == label,
                  mounts.get('/output') == str(out),
                  mounts.get('/study') == rec['source_snapshot'],
                  Path(rec['log']).exists(), Path(rec['exit']).exists()]
        if not all(checks):
            raise RuntimeError(f'Ownership or preservation mismatch: {name}: {checks}')
        subprocess.run(['docker', 'rm', info['Id']], check=True, capture_output=True)
        removed.append(dict(name=name, id=info['Id'], record=str(record)))
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log = ROOT / 'logs' / f'{stamp}_q16_compat_{device}_cleanup.log'
    log.write_text(json.dumps(dict(device=device, removed=removed), indent=2) + '\n')
    print(json.dumps(dict(count=len(removed), log=str(log)), indent=2))


if __name__ == '__main__':
    cleanup(sys.argv[1])
