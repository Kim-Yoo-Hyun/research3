"""Host stdlib-only background launcher for Q16 contact-task audit."""
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
OUT = ROOT / 'runs/q16/task_audit'
TAG = 'research3-q16-task-audit:v2'
BUILD_FILES = ('Dockerfile.task_audit', 'requirements.lock', 'task_audit_env.py', 'task_audit_job.py')
STAGES = ('build', 'smoke', 'diagnose', 'verify', 'demo')


def write(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def worker(record_path):
    path = Path(record_path)
    rec = json.loads(path.read_text())
    rec['status'] = 'running'
    write(path, rec)
    try:
        code = subprocess.run(rec['command'], cwd=ROOT).returncode
    except Exception as exc:
        code = 125
        rec['exception'] = repr(exc)
    Path(rec['exit']).write_text(str(code) + '\n')
    rec.update(status='completed' if code == 0 else 'failed', returncode=code)
    command = ['docker', 'image', 'inspect', TAG] if rec['stage'] == 'build' else ['docker', 'inspect', rec['container']]
    inspection = subprocess.run(command, capture_output=True, text=True)
    if inspection.returncode == 0:
        info = json.loads(inspection.stdout)[0]
        rec['inspection'] = {k: info.get(k) for k in ('Id', 'State', 'Image', 'Config', 'HostConfig', 'Mounts')}
    write(path, rec)


def launch(stage, attempt, extra):
    if stage not in STAGES:
        raise ValueError(stage)
    if not attempt.replace('_', '').isalnum():
        raise ValueError(attempt)
    if stage != 'build' and (OUT / attempt).exists() and any((OUT / attempt).iterdir()):
        raise FileExistsError(OUT / attempt)
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    for name in ('jobs', 'cache', attempt):
        (OUT / name).mkdir(parents=True, exist_ok=True)
    source = OUT / 'jobs' / (stamp + '_source')
    source.mkdir()
    for name in BUILD_FILES + (() if stage == 'build' else ('task_audit.py',)):
        shutil.copy2(HERE / name, source / name)
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir()}
    container = f'research3-q16-task-audit-{stage}-{stamp}'
    image_id = None
    if stage == 'build':
        command = ['docker', 'build', '--no-cache', '--progress=plain', '-t', TAG,
                   '-f', str(HERE / 'Dockerfile.task_audit'), str(ROOT)]
    else:
        image_id = json.loads(subprocess.check_output(['docker', 'image', 'inspect', TAG]))[0]['Id']
        command = ['docker', 'run', '--name', container,
                   '--label', f'research3.workspace={ROOT}', '--label', 'research3.study=q16-task-audit',
                   '--cpus=6', '--memory=12g', '--memory-swap=12g', '--pids-limit=256',
                   '--user', f'{os.getuid()}:{os.getgid()}', '--network', 'none',
                   '-e', 'CUDA_VISIBLE_DEVICES=', '-e', 'MPLCONFIGDIR=/home/research/mpl',
                   '-v', f'{source}:/study:ro', '-v', f'{OUT}:/output:rw',
                   '-v', f'{OUT / "cache"}:/home/research:rw', image_id,
                   'timeout', '3600s', 'python', '-B', '-u', '/study/task_audit.py',
                   stage, '--attempt', attempt, *extra]
    log = ROOT / 'logs' / f'{stamp}_q16_task_audit_{stage}.log'
    rec = dict(stage=stage, status='launched', attempt=attempt, command=command,
               container=container, working_directory=str(ROOT), output=str(OUT / attempt),
               log=str(log), exit=str(log.with_suffix('.exit')), image_id=image_id,
               source_snapshot=str(source), source_sha256=hashes, device='cpu')
    record_path = OUT / 'jobs' / f'{stamp}_{stage}.json'
    write(record_path, rec)
    with log.open('xb') as stream:
        proc = subprocess.Popen([sys.executable, str(HERE / 'task_audit_job.py'), '_worker', str(record_path)],
                                cwd=ROOT, stdin=subprocess.DEVNULL, stdout=stream,
                                stderr=subprocess.STDOUT, start_new_session=True)
    print(json.dumps(dict(pid=proc.pid, record=str(record_path), log=str(log)), indent=2))


if __name__ == '__main__':
    if sys.argv[1] == '_worker':
        worker(sys.argv[2])
    else:
        launch(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'v1', sys.argv[3:])
