"""Host standard-library orchestration only; all method execution is in Docker."""
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT / 'runs/q3/timestep'
TAG = 'research3-q3-timestep:v1'


def worker(record_path):
    path = Path(record_path)
    record = json.loads(path.read_text())
    record['status'] = 'running'
    path.write_text(json.dumps(record, indent=2) + '\n')
    result = subprocess.run(record['command'], cwd=ROOT)
    Path(record['exit']).write_text(str(result.returncode) + '\n')
    record['status'] = 'completed' if result.returncode == 0 else 'failed'
    record['returncode'] = result.returncode
    if result.returncode == 0 and record['stage'] == 'build':
        record['image'] = json.loads(subprocess.check_output(['docker', 'image', 'inspect', TAG]))[0]
    if record['stage'] != 'build':
        inspection = subprocess.run(['docker', 'inspect', record['container']], capture_output=True, text=True)
        if inspection.returncode == 0:
            record['container_inspect'] = json.loads(inspection.stdout)[0]
    path.write_text(json.dumps(record, indent=2) + '\n')


def launch(stage, attempt):
    assert stage in ('build', 'run', 'verify')
    assert attempt.replace('_', '').isalnum()
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    (OUT / 'jobs').mkdir(parents=True, exist_ok=True)
    (OUT / 'cache').mkdir(exist_ok=True)
    (OUT / attempt).mkdir(exist_ok=True)
    name = f'research3-q3-{stage}-{stamp}'
    if stage == 'build':
        command = ['docker', 'build', '--no-cache', '--progress=plain', '-t', TAG,
                   '-f', str(HERE / 'Dockerfile'), str(ROOT)]
        image = None
    else:
        image = json.loads(subprocess.check_output(['docker', 'image', 'inspect', TAG]))[0]
        command = ['docker', 'run', '--name', name, '--label', f'research3.workspace={ROOT}',
                   '--label', 'research3.study=q3-timestep', '--cpus=4', '--memory=12g',
                   '--memory-swap=12g', '--pids-limit=512', '--user', f'{os.getuid()}:{os.getgid()}',
                   '--network', 'bridge' if stage == 'run' else 'none',
                   '-e', 'HOME=/cache', '-e', 'MPLCONFIGDIR=/cache/mpl',
                   '-v', f'{HERE}:/study:ro', '-v', f'{ROOT / "datasets/q8"}:/inputs:ro',
                   '-v', f'{OUT}:/output:rw', '-v', f'{OUT / "cache"}:/cache:rw']
        if stage == 'run':
            command += ['--runtime=nvidia', '--gpus', 'device=0',
                        '-e', 'NVIDIA_DRIVER_CAPABILITIES=graphics,utility,compute',
                        '-e', 'VK_ICD_FILENAMES=/opt/ManiSkill/docker/nvidia_icd.json',
                        '-e', 'CUDA_VISIBLE_DEVICES=0']
        command += [image['Id'], 'timeout', '3600s', 'python', '-B', '-u',
                    f'/study/{"run.py" if stage == "run" else "verify.py"}', '--attempt', attempt]
    log = ROOT / 'logs' / f'{stamp}_q3_{stage}.log'
    record = dict(stage=stage, status='launched', attempt=attempt, container=name,
                  command=command, working_directory=str(ROOT), output=str(OUT / attempt),
                  log=str(log), exit=str(log.with_suffix('.exit')), image_id=image['Id'] if image else None)
    path = OUT / 'jobs' / f'{stamp}_{stage}.json'
    path.write_text(json.dumps(record, indent=2) + '\n')
    with log.open('xb') as stream:
        proc = subprocess.Popen([sys.executable, str(HERE / 'job.py'), '_worker', str(path)],
                                cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL, start_new_session=True)
    print(json.dumps(dict(pid=proc.pid, record=str(path), log=str(log)), indent=2))


if __name__ == '__main__':
    if sys.argv[1] == '_worker':
        worker(sys.argv[2])
    else:
        launch(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'v1')
