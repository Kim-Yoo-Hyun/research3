"""Sequential bounded conditions in fresh Python processes inside the new GPU container."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

parser = argparse.ArgumentParser()
parser.add_argument('--attempt', required=True)
args = parser.parse_args()
out = Path('/output') / args.attempt
assert not (out / 'run_status.json').exists(), 'Use a new attempt; never overwrite a prior run'
for filename in ['installed.lock', 'os-packages.lock', 'requirements.lock']:
    shutil.copyfile(Path('/recipe') / filename, out / filename)
for filename in ['observe.py', 'run.py', 'verify.py', 'Dockerfile', 'job.py']:
    shutil.copyfile(Path('/study') / filename, out / filename)
started = time.monotonic()
# Establish reference, same-condition repeat and reference replay before changed frequencies.
conditions = [('closed', 100, 0), ('closed', 100, 1), ('replay', 100, 0), ('replay', 100, 1)]
conditions += [(mode, freq, repeat) for freq in [200, 400] for mode in ['closed', 'replay'] for repeat in [0, 1]]
status = {'status': 'running', 'conditions': [], 'seed': 20260918}
for mode, freq, repeat in conditions:
    command = ['python', '-B', '-u', '/study/observe.py', '--attempt', args.attempt,
               '--mode', mode, '--frequency', str(freq), '--repeat', str(repeat)]
    result = subprocess.run(command, timeout=300)
    status['conditions'].append({'mode': mode, 'frequency': freq, 'repeat': repeat, 'exit': result.returncode})
    status['seconds'] = time.monotonic() - started
    status['status'] = 'running' if result.returncode == 0 else 'failed'
    (out / 'run_status.json').write_text(json.dumps(status, indent=2) + '\n')
    if result.returncode:
        raise SystemExit(result.returncode)
status['status'] = 'completed'
status['runtime_cache'] = []
for path in Path('/cache').rglob('*PhysX*.so'):
    status['runtime_cache'].append({'path': str(path), 'bytes': path.stat().st_size,
                                  'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
(out / 'run_status.json').write_text(json.dumps(status, indent=2) + '\n')
print(json.dumps(status), flush=True)
