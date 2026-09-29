"""Verify preservation and extend the artifact manifest after diagnostics. Docker only."""
import hashlib
import json
from pathlib import Path
import shutil

out = Path('/output/observation')
previous = json.loads((out / 'output_manifest.json').read_text())
for row in previous['files']:
    data = (out / row['path']).read_bytes()
    assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256'], row['path']
assert json.loads((out / 'verification.json').read_text())['status'] == 'PASS'
assert len(json.loads((out / 'results.json').read_text())) == 40
shutil.copyfile(out / 'output_manifest.json', out / 'output_manifest_before_diagnosis.json')
shutil.copyfile('/study/finalize.py', out / 'code/finalize.py')
shutil.copyfile('/study/orchestrate.py', out / 'code/orchestrate_after_diagnosis.py')
(out / 'preservation.json').write_text(json.dumps({'previous_files_unchanged': len(previous['files']),
    'results': '40 cases with primary/sanity roles retained; planning, validation and diagnosis logs on output mount',
    'source': 'Run-specific code snapshot, original PDDL per case, pinned input manifest and image environment inventory preserved',
    'boundary': 'Local preservation verified. This is not an off-host backup of raw results.'}, indent=2) + '\n')
files = []
for p in sorted(out.rglob('*')):
    if p.is_file() and p.name != 'output_manifest.json':
        b = p.read_bytes()
        files.append({'path': str(p.relative_to(out)), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()})
(out / 'output_manifest.json').write_text(json.dumps({'files': files}, indent=2) + '\n')
print('Preserved', len(files), 'files;', len(previous['files']), 'earlier files unchanged;', sum(r['bytes'] for r in files), 'bytes', flush=True)
