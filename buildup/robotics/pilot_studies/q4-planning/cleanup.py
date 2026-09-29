"""Host-only cleanup of exact containers created by this study's receipts."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path('/home/yoohyun/research3')
STUDY = ROOT / 'buildup/robotics/pilot_studies/q4-planning'
parser = argparse.ArgumentParser()
parser.add_argument('--run-id', help='Clean only this explicitly named run; omitted retains the original v1/v2 cleanup scope.')
args = parser.parse_args()
if args.run_id:
    assert all(c.isalnum() or c in '_-' for c in args.run_id)
runroot = ROOT / 'runs/q4-planning' / (args.run_id or '20260918_v2')
out = runroot / 'observation'
manifest = json.loads((out / 'output_manifest.json').read_text())
for row in manifest['files']:
    b = (out / row['path']).read_bytes()
    assert len(b) == row['bytes'] and hashlib.sha256(b).hexdigest() == row['sha256'], row['path']
assert json.loads((out / 'verification.json').read_text())['status'] == 'PASS'
receipts = [] if args.run_id else sorted((ROOT / 'runs/q4-planning/20260918_v1/containers').glob('research3_q4_*.json'))
receipts += sorted((runroot / 'containers').glob('research3_q4_*.json'))
assert receipts, 'No creation receipts: refuse cleanup'
checks = []
for path in receipts:
    r = json.loads(path.read_text())
    cid = r['container_id']
    state = json.loads(subprocess.check_output(['docker', 'inspect', cid]))[0]
    assert state['Id'] == cid and not state['State']['Running'] and state['State']['Status'] == 'exited'
    assert state['Config']['Labels']['org.research3.workspace'] == str(ROOT)
    assert state['Config']['Labels']['org.research3.study'] == 'q4-planning'
    assert state['Config']['Labels']['org.research3.run'] == r['run_id']
    if args.run_id:
        assert r['run_id'] == args.run_id
    expected_output = ROOT / 'runs/q4-planning' / r['run_id']
    mounts = {m['Destination']: m for m in state['Mounts']}
    assert mounts['/output']['Source'] == str(expected_output) and mounts['/output']['RW']
    assert mounts['/study']['Source'] == str(STUDY) and not mounts['/study']['RW']
    assert mounts['/data']['Source'] == str(ROOT / 'runs/reserve_review/20260918/pddlgym') and not mounts['/data']['RW']
    assert state['Image'] == r['image_inspect']['Id']
    assert state['Config']['Cmd'] == r['command'][-len(state['Config']['Cmd']):]
    assert Path(r['log']).exists()
    assert Path(r['log']).with_suffix('.exit').read_text().strip() == str(state['State']['ExitCode'])
    # Keep the latest inspect and exact creation command, even after docker rm.
    r['inspect_before_cleanup'] = state
    path.write_text(json.dumps(r, indent=2) + '\n')
    checks.append({'container_id': cid, 'name': r['name'], 'stage': r['stage'], 'run_id': r['run_id'],
                   'receipt': str(path.relative_to(ROOT)), 'log': str(Path(r['log']).relative_to(ROOT)),
                   'exit_code': state['State']['ExitCode']})
# Complete all checks before the first deletion. No prune, force, volume or image operation.
for c in checks:
    subprocess.run(['docker', 'rm', c['container_id']], check=True, capture_output=True)
    c['removed'] = True
record = {'time': datetime.datetime.now().astimezone().isoformat(), 'containers': checks,
          'verified_output_files': len(manifest['files']), 'image_retained': 'research3-q4-planning:v1',
          'scope': 'Only exact IDs with creation receipts and verified workspace/run mounts. Other containers/images/data untouched.'}
(runroot / 'cleanup.json').write_text(json.dumps(record, indent=2) + '\n')
stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
log = ROOT / 'logs' / (stamp + '_q4_cleanup.log')
log.write_text(json.dumps(record, indent=2) + '\n')
print('Removed', len(checks), 'verified study-owned exited containers; preserved', len(manifest['files']), 'output files. Log:', log)
