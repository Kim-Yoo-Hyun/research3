"""Host-side Docker orchestration only; no research imports or computation."""
import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess

ROOT = Path('/home/yoohyun/research3')
STUDY = ROOT / 'buildup/robotics/pilot_studies/q4-planning'
IMAGE = 'research3-q4-planning:v1'
IMAGE_ID = 'sha256:cf36dd836af9c48a0d96326124b4f13363e8b44ce5c77446cae639ce8fc6db95'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('stage', choices=['prepare', 'run', 'verify', 'analyze', 'diagnose', 'finalize',
                                    'goal_prepare', 'goal_verify', 'goal_analyze'])
    p.add_argument('--run-id', required=True)
    a = p.parse_args()
    assert all(c.isalnum() or c in '_-' for c in a.run_id)
    out = ROOT / 'runs/q4-planning' / a.run_id
    out.mkdir(parents=True, exist_ok=True)
    (out / 'containers').mkdir(exist_ok=True)
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    name = f'research3_q4_{a.stage}_{stamp}'
    log = ROOT / 'logs' / f'{stamp}_q4_{a.stage}.log'
    entry = ['/study/run.py', a.stage] if a.stage in {'prepare', 'run'} else ['/study/' + a.stage + '.py']
    if a.stage.startswith('goal_'):
        entry = ['300s', 'python', '/study/goal.py', a.stage.removeprefix('goal_')]
    cmd = ['docker', 'create', '--name', name, '--label', f'org.research3.workspace={ROOT}',
           '--label', 'org.research3.study=q4-planning', '--label', 'org.research3.run=' + a.run_id,
           '--cpus', '1', '--memory', '4g', '--memory-swap', '4g', '--network', 'none',
           '--user', f'{os.getuid()}:{os.getgid()}', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
           '--pids-limit', '256', '--read-only', '--tmpfs', '/tmp:rw,size=256m',
           '--mount', f'type=bind,src={STUDY},dst=/study,readonly',
           '--mount', f'type=bind,src={ROOT}/runs/reserve_review/20260918/pddlgym,dst=/data,readonly',
           '--mount', f'type=bind,src={out},dst=/output', IMAGE_ID] + entry
    if a.stage == 'analyze':
        ix = cmd.index(IMAGE_ID)
        cmd[ix:ix] = ['--mount', f'type=bind,src={ROOT}/runs/q4-planning/20260918_v1,dst=/prior,readonly']
    if a.stage.startswith('goal_'):
        ix = cmd.index(IMAGE_ID)
        cmd[ix:ix] = ['--mount', f'type=bind,src={ROOT}/runs/q4-planning/20260918_v2/observation,dst=/reference,readonly',
                      '--entrypoint', 'timeout']
        # Bound setup/verification too; SIGTERM exits without hiding logs or outputs.
    receipt = {'stage': a.stage, 'run_id': a.run_id, 'name': name, 'command': cmd, 'log': str(log),
               'status': 'launched', 'image_inspect': json.loads(subprocess.check_output(['docker', 'image', 'inspect', IMAGE_ID]))[0]}
    assert receipt['image_inspect']['Config']['Labels']['org.research3.workspace'] == str(ROOT)
    assert receipt['image_inspect']['Id'] == IMAGE_ID
    rf = out / 'containers' / (name + '.json')
    rf.write_text(json.dumps(receipt, indent=2) + '\n')
    created = subprocess.run(cmd, text=True, capture_output=True)
    receipt['create_returncode'] = created.returncode
    receipt['create_stderr'] = created.stderr
    if created.returncode:
        receipt['status'] = 'failed'
        rf.write_text(json.dumps(receipt, indent=2) + '\n')
        log.write_text(created.stderr)
        print('CREATE FAILED', rf)
        raise SystemExit(created.returncode)
    cid = created.stdout.strip()
    receipt['container_id'] = cid
    receipt['status'] = 'running'
    rf.write_text(json.dumps(receipt, indent=2) + '\n')
    with log.open('w') as f:
        rc = subprocess.run(['docker', 'start', '-a', cid], stdout=f, stderr=subprocess.STDOUT).returncode
    inspect = json.loads(subprocess.check_output(['docker', 'inspect', cid]))[0]
    receipt['inspect'] = inspect
    receipt['attach_returncode'] = rc
    receipt['exit_code'] = inspect['State']['ExitCode']
    receipt['status'] = 'completed' if receipt['exit_code'] == 0 else 'failed'
    rf.write_text(json.dumps(receipt, indent=2) + '\n')
    log.with_suffix('.exit').write_text(str(receipt['exit_code']) + '\n')
    print(receipt['status'], rf, 'log', log, flush=True)
    raise SystemExit(receipt['exit_code'])


if __name__ == '__main__':
    main()
