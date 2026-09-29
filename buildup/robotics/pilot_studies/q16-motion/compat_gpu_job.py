"""Host stdlib-only background launcher for source-matched PhysX CUDA replay."""
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
OUT = ROOT / 'runs/q16/compat_gpu'
DEMOS = ROOT / 'runs/q16/task_audit/demos/extracted'
NATIVE_SOURCE = ROOT / 'external/q16/ManiSkill-baab60ede2e89167c1b7aaed41a9aa8e690a9d1e'
TAG = 'research3-q16-compat-gpu:v1'
FILES = ('Dockerfile.compat_gpu', 'requirements.compat.lock', 'compat_env.py',
         'compat_replay.py', 'compat_bc.py', 'compat_gpu_job.py')
STAGES = ('build', 'replay', 'verify', 'audit', 'official',
          'extract', 'fit', 'evaluate', 'validate')


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
    for name in FILES:
        shutil.copy2(HERE / name, source / name)
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir()}
    container = f'research3-q16-compat-gpu-{stage}-{stamp}'
    image_id = None
    if stage == 'build':
        command = ['docker', 'build', '--no-cache', '--progress=plain', '-t', TAG,
                   '-f', str(HERE / 'Dockerfile.compat_gpu'), str(ROOT)]
    else:
        image_id = json.loads(subprocess.check_output(['docker', 'image', 'inspect', TAG]))[0]['Id']
        native = '--native' in extra or stage in ('official', 'extract', 'fit', 'evaluate', 'validate')
        bootstrap_network = '--bootstrap-network' in extra
        extra = [x for x in extra if x not in ('--native', '--bootstrap-network')]
        command = ['docker', 'run', '--name', container,
                   '--label', f'research3.workspace={ROOT}', '--label', 'research3.study=q16-compat-gpu',
                   '--gpus', 'all', '--cpus=6', '--memory=16g', '--memory-swap=16g', '--pids-limit=256',
                   '--user', f'{os.getuid()}:{os.getgid()}',
                   '--network', 'bridge' if bootstrap_network else 'none',
                   '-e', 'NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics',
                   '-e', 'Q16_COMPAT_DEVICE=gpu', '-e', 'MPLCONFIGDIR=/home/research/mpl',
                   '-e', f'Q16_COMPAT_NATIVE={int(native)}',
                   '-v', f'{source}:/study:ro', '-v', f'{OUT}:/output:rw',
                   '-v', f'{DEMOS}:/demos:ro',
                   '-v', f'{OUT / "cache"}:/home/research:rw', image_id,
                   'timeout', '3600s', 'python', '-B', '-u', '/study/compat_replay.py',
                   stage, '--attempt', attempt, *extra]
        if stage in ('extract', 'fit', 'evaluate', 'validate'):
            command[command.index('/study/compat_replay.py')] = '/study/compat_bc.py'
        if stage == 'official':
            command = command[:command.index('timeout')] + [
                'timeout', '3600s', 'python', '-B', '-u', '-m',
                'mani_skill.trajectory.replay_trajectory',
                '--traj-path', '/demos/trajectory.none.pd_ee_delta_pos.physx_cuda.h5',
                '--num-envs', '1', '--sim-backend', 'physx_cuda',
                '--use-first-env-state', '--count', '8', '--verbose']
        if native:
            pos = command.index(image_id)
            command[pos:pos] = ['-v', f'{NATIVE_SOURCE}:/opt/ManiSkillNative:ro',
                                '-e', 'PYTHONPATH=/opt/ManiSkillNative:/study']
    log = ROOT / 'logs' / f'{stamp}_q16_compat_gpu_{stage}.log'
    rec = dict(stage=stage, status='launched', attempt=attempt, command=command,
               container=container, working_directory=str(ROOT), output=str(OUT / attempt),
               log=str(log), exit=str(log.with_suffix('.exit')), image_id=image_id,
               source_snapshot=str(source), source_sha256=hashes, device='gpu',
               source_commit='baab60ede2e89167c1b7aaed41a9aa8e690a9d1e',
               source_archive_sha256='db7f1fb49038a1a11612876022ba31fdb8c9095e4e3f4a408728abf8b821f49e')
    record_path = OUT / 'jobs' / f'{stamp}_{stage}.json'
    write(record_path, rec)
    with log.open('xb') as stream:
        proc = subprocess.Popen([sys.executable, str(HERE / 'compat_gpu_job.py'), '_worker', str(record_path)],
                                cwd=ROOT, stdin=subprocess.DEVNULL, stdout=stream,
                                stderr=subprocess.STDOUT, start_new_session=True)
    print(json.dumps(dict(pid=proc.pid, record=str(record_path), log=str(log)), indent=2))


if __name__ == '__main__':
    if sys.argv[1] == '_worker':
        worker(sys.argv[2])
    else:
        launch(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'v1', sys.argv[3:])
