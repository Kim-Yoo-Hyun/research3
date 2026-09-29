"""Host stdlib-only background orchestration. Method execution stays in Docker."""
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
OUT = ROOT / 'runs/q16/motion'
TAG = 'research3-q16-motion:v1'


def write(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def worker(path):
    path = Path(path)
    rec = json.loads(path.read_text())
    rec['status'] = 'running'
    write(path, rec)
    proc = subprocess.run(rec['command'], cwd=ROOT)
    Path(rec['exit']).write_text(str(proc.returncode) + '\n')
    rec.update(status='completed' if proc.returncode == 0 else 'failed', returncode=proc.returncode)
    cmd = ['docker', 'image', 'inspect', TAG] if rec['stage'] == 'build' else ['docker', 'inspect', rec['container']]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        rec['inspection'] = json.loads(result.stdout)[0]
    write(path, rec)


def launch(stage, attempt, extra):
    assert stage in ('build', 'develop', 'collect', 'fit', 'evaluate', 'verify', 'diagnose')
    assert attempt.replace('_', '').isalnum()
    if stage != 'build' and (OUT / attempt).exists() and any((OUT / attempt).iterdir()):
        raise FileExistsError(f'Choose a fresh output attempt: {OUT / attempt}')
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    for d in ['jobs', 'cache', attempt]:
        (OUT / d).mkdir(parents=True, exist_ok=True)
    source = OUT / 'jobs' / (stamp + '_source')
    source.mkdir()
    for f in HERE.iterdir():
        if f.is_file():
            shutil.copy2(f, source / f.name)
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir()}
    name = f'research3-q16-{stage}-{stamp}'
    image_id = None
    if stage == 'build':
        command = ['docker', 'build', '--no-cache', '--progress=plain', '-t', TAG, '-f', str(HERE / 'Dockerfile'), str(ROOT)]
    else:
        image_id = json.loads(subprocess.check_output(['docker', 'image', 'inspect', TAG]))[0]['Id']
        command = ['docker', 'run', '--name', name, '--label', f'research3.workspace={ROOT}',
                   '--label', 'research3.study=q16-motion', '--cpus=4', '--memory=8g',
                   '--memory-swap=8g', '--pids-limit=256', '--user', f'{os.getuid()}:{os.getgid()}',
                   '--network', 'bridge' if stage == 'develop' else 'none',
                   '-e', 'MPLCONFIGDIR=/home/research/mpl', '-e', 'CUDA_VISIBLE_DEVICES=',
                   '-v', f'{source}:/study:ro', '-v', f'{OUT}:/output:rw',
                   '-v', f'{OUT / "cache"}:/home/research:rw', image_id,
                   'timeout', '14400s', 'python', '-B', '-u', '/study/main.py',
                   stage, '--attempt', attempt, *extra]
    log = ROOT / 'logs' / f'{stamp}_q16_{stage}.log'
    rec = dict(stage=stage, status='launched', attempt=attempt, command=command, container=name,
               working_directory=str(ROOT), output=str(OUT / attempt), log=str(log),
               exit=str(log.with_suffix('.exit')), image_id=image_id,
               source_snapshot=str(source), source_sha256=hashes, device='cpu')
    path = OUT / 'jobs' / f'{stamp}_{stage}.json'
    write(path, rec)
    with log.open('xb') as stream:
        proc = subprocess.Popen([sys.executable, str(HERE / 'job.py'), '_worker', str(path)],
                                cwd=ROOT, stdin=subprocess.DEVNULL, stdout=stream,
                                stderr=subprocess.STDOUT, start_new_session=True)
    print(json.dumps(dict(pid=proc.pid, record=str(path), log=str(log)), indent=2))


if __name__ == '__main__':
    if sys.argv[1] == '_worker':
        worker(sys.argv[2])
    else:
        launch(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'v1', sys.argv[3:])
