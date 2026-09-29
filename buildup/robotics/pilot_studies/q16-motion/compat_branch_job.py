"""Host stdlib-only launcher for the continuous Q16 CUDA diagnostic workload."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT / 'runs/q16/branches'
PREVIOUS = ROOT / 'runs/q16/compat_gpu'
DEMOS = ROOT / 'runs/q16/task_audit/demos/extracted'
NATIVE = ROOT / 'external/q16/ManiSkill-baab60ede2e89167c1b7aaed41a9aa8e690a9d1e'
IMAGE = 'research3-q16-compat-gpu:v1'
EXPECTED_ID = 'sha256:8dc6f2ae072476b71d03cb5c26e9f6500bcb6e6dfd41e45d77d5848595785d39'
FILES = ('compat_branches.py', 'compat_bc.py', 'compat_env.py', 'compat_branch_job.py',
         'Dockerfile.compat_gpu', 'requirements.compat.lock', 'installed.compat_gpu.lock')


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def worker(path):
    path = Path(path)
    rec = json.loads(path.read_text())
    rec['status'] = 'running'
    write(path, rec)
    try:
        code = subprocess.run(rec['command'], cwd=ROOT).returncode
    except Exception as exc:
        code = 125
        rec['exception'] = repr(exc)
    Path(rec['exit']).write_text(str(code) + '\n')
    rec['returncode'] = code
    rec['status'] = 'completed' if code == 0 else 'failed'
    inspected = subprocess.run(['docker', 'inspect', rec['container']], capture_output=True, text=True)
    if inspected.returncode == 0:
        info = json.loads(inspected.stdout)[0]
        rec['inspection'] = {key: info.get(key) for key in ('Id', 'State', 'Image', 'Config', 'HostConfig', 'Mounts')}
    write(path, rec)


def launch(stage, attempt='branch2'):
    if stage not in ('fit', 'diagnose', 'validate'):
        raise ValueError(stage)
    if not attempt.replace('_', '').isalnum():
        raise ValueError(attempt)
    stage_output = OUT / ('fit1' if stage == 'fit' else attempt)
    if stage == 'fit' and stage_output.exists():
        raise FileExistsError(stage_output)
    if stage == 'diagnose' and stage_output.exists():
        raise FileExistsError(stage_output)
    if stage == 'validate' and not (stage_output / 'branches.json').exists():
        raise FileNotFoundError(stage_output / 'branches.json')
    image = json.loads(subprocess.check_output(['docker', 'image', 'inspect', IMAGE]))[0]
    if image['Id'] != EXPECTED_ID:
        raise ValueError('Pinned Q16 workspace image identity changed')
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    jobs = OUT / 'jobs'
    jobs.mkdir(parents=True, exist_ok=True)
    source = jobs / f'{stamp}_source'
    source.mkdir()
    for name in FILES:
        shutil.copy2(HERE / name, source / name)
    hashes = {name: hashlib.sha256((source / name).read_bytes()).hexdigest() for name in FILES}
    container = f'research3-q16-branches-{stage}-{stamp}'
    command = ['docker', 'run', '--name', container,
               '--label', f'research3.workspace={ROOT}', '--label', 'research3.study=q16-branches',
               '--gpus', 'all', '--cpus=6', '--memory=16g', '--memory-swap=16g', '--pids-limit=256',
               '--user', f'{os.getuid()}:{os.getgid()}', '--network', 'none',
               '-e', 'NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics',
               '-e', 'MPLCONFIGDIR=/home/research/mpl',
               '-e', 'PYTHONPATH=/opt/ManiSkillNative:/study',
               '-v', f'{source}:/study:ro', '-v', f'{OUT}:/output:rw',
               '-v', f'{PREVIOUS}:/previous:ro', '-v', f'{DEMOS}:/demos:ro',
               '-v', f'{NATIVE}:/opt/ManiSkillNative:ro',
               '-v', f'{PREVIOUS / "cache"}:/home/research:rw', EXPECTED_ID,
               'timeout', '3600s', 'python', '-B', '-u', '/study/compat_branches.py', stage,
               '--attempt', attempt]
    log = ROOT / 'logs' / f'{stamp}_q16_branches_{stage}.log'
    record = jobs / f'{stamp}_{stage}.json'
    write(record, dict(stage=stage, attempt=attempt, status='launched', command=command, container=container,
                       image_id=EXPECTED_ID, source_snapshot=str(source), source_sha256=hashes,
                       working_directory=str(ROOT), output=str(stage_output),
                       log=str(log), exit=str(log.with_suffix('.exit')), device='gpu'))
    with log.open('xb') as stream:
        proc = subprocess.Popen([sys.executable, str(HERE / 'compat_branch_job.py'), '_worker', str(record)],
                                cwd=ROOT, stdin=subprocess.DEVNULL, stdout=stream,
                                stderr=subprocess.STDOUT, start_new_session=True)
    print(json.dumps(dict(pid=proc.pid, record=str(record), log=str(log)), indent=2))


if __name__ == '__main__':
    if sys.argv[1] == '_worker':
        worker(sys.argv[2])
    else:
        launch(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'branch2')
