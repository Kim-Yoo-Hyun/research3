"""Host stdlib-only launcher. All simulator and ML imports run in Docker."""
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
OUT = ROOT / 'runs/q16/adaptation'
TAG = 'research3-q16-adaptation:v1'
FILES = ('adaptation.py', 'diffusion.py', 'dynamics.py', 'adaptation_job.py', 'task.py',
         'Dockerfile.adaptation', 'requirements.lock')
STAGES = ('build', 'collect', 'fit', 'evaluate', 'verify', 'diagnose')


def write(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def worker(record_path):
    record_path = Path(record_path)
    rec = json.loads(record_path.read_text())
    rec['status'] = 'running'
    write(record_path, rec)
    try:
        proc = subprocess.run(rec['command'], cwd=ROOT)
        code = proc.returncode
    except Exception as exc:
        code = 125
        rec['exception'] = repr(exc)
    Path(rec['exit']).write_text(str(code) + '\n')
    rec.update(status='completed' if code == 0 else 'failed', returncode=code)
    cmd = ['docker', 'image', 'inspect', TAG] if rec['stage'] == 'build' else ['docker', 'inspect', rec['container']]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        inspection = json.loads(result.stdout)[0]
        rec['inspection'] = {k: inspection.get(k) for k in ('Id', 'State', 'Image', 'Config', 'HostConfig', 'Mounts')}
    write(record_path, rec)


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
    for name in FILES:
        shutil.copy2(HERE / name, source / name)
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir()}
    container = f'research3-q16-adaptation-{stage}-{stamp}'
    image_id = None
    if stage == 'build':
        command = ['docker', 'build', '--no-cache', '--progress=plain', '-t', TAG,
                   '-f', str(HERE / 'Dockerfile.adaptation'), str(ROOT)]
    else:
        image_id = json.loads(subprocess.check_output(['docker', 'image', 'inspect', TAG]))[0]['Id']
        command = ['docker', 'run', '--name', container,
                   '--label', f'research3.workspace={ROOT}', '--label', 'research3.study=q16-adaptation',
                   '--cpus=6', '--memory=12g', '--memory-swap=12g', '--pids-limit=256',
                   '--user', f'{os.getuid()}:{os.getgid()}', '--network', 'none',
                   '-e', 'CUDA_VISIBLE_DEVICES=', '-e', 'MPLCONFIGDIR=/home/research/mpl',
                   '-v', f'{source}:/study:ro', '-v', f'{OUT}:/output:rw',
                   '-v', f'{OUT / "cache"}:/home/research:rw', image_id,
                   'timeout', '14400s', 'python', '-B', '-u', '/study/adaptation.py',
                   stage, '--attempt', attempt, *extra]
    log = ROOT / 'logs' / f'{stamp}_q16_adaptation_{stage}.log'
    rec = dict(stage=stage, status='launched', attempt=attempt, command=command,
               container=container, working_directory=str(ROOT), output=str(OUT / attempt),
               log=str(log), exit=str(log.with_suffix('.exit')), image_id=image_id,
               source_snapshot=str(source), source_sha256=hashes, device='cpu')
    record_path = OUT / 'jobs' / f'{stamp}_{stage}.json'
    write(record_path, rec)
    with log.open('xb') as stream:
        proc = subprocess.Popen([sys.executable, str(HERE / 'adaptation_job.py'), '_worker', str(record_path)],
                                cwd=ROOT, stdin=subprocess.DEVNULL, stdout=stream,
                                stderr=subprocess.STDOUT, start_new_session=True)
    print(json.dumps(dict(pid=proc.pid, record=str(record_path), log=str(log)), indent=2))


if __name__ == '__main__':
    if sys.argv[1] == '_worker':
        worker(sys.argv[2])
    else:
        launch(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'v1', sys.argv[3:])
