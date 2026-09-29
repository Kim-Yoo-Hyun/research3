"""Host stdlib launcher for the selected Docker-only hold comparison."""
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = ROOT / 'runs/q15/reward'
IMAGE = 'sha256:3ae1cf37d7c199cf6e78f521e44b2596f834e2c6a4e4e9a136915b18e11cb17a'


def worker(path):
    path = Path(path)
    record = json.loads(path.read_text())
    record['status'] = 'running'
    path.write_text(json.dumps(record, indent=2) + '\n')
    try:
        result = subprocess.run(record['command'], cwd=ROOT)
        record['returncode'] = result.returncode
        record['status'] = 'completed' if result.returncode == 0 else 'failed'
    except BaseException as error:
        record.update(status='failed', error=repr(error), returncode=-1)
        raise
    finally:
        Path(record['exit']).write_text(str(record['returncode']) + '\n')
        inspect = subprocess.run(['docker', 'inspect', record['container']], capture_output=True, text=True)
        if inspect.returncode == 0:
            record['container_inspect'] = json.loads(inspect.stdout)[0]
        path.write_text(json.dumps(record, indent=2) + '\n')


def launch(stage, attempt):
    assert stage in ('run', 'verify', 'diagnose') and attempt.replace('_', '').isalnum()
    assert json.loads(subprocess.check_output(['docker', 'image', 'inspect', IMAGE]))[0]['Id'] == IMAGE
    # The image must have a recorded workspace build, not merely a matching name.
    jobs = [json.loads(p.read_text()) for p in (BASE / 'jobs').glob('*.json')]
    assert any(r.get('stage') == 'build' and r.get('image', {}).get('Id') == IMAGE
               and r.get('working_directory') == str(ROOT) for r in jobs)
    out = BASE / attempt
    if stage == 'run':
        out.mkdir(exist_ok=False)
    else:
        assert (out / 'run_status.json').is_file()
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    name = f'research3-q15-hold-{stage}-{stamp}'
    command = ['docker', 'run', '--name', name, '--label', f'research3.workspace={ROOT}',
               '--label', 'research3.study=q15-hold', '--cpus=8', '--memory=24g',
               '--memory-swap=24g', '--pids-limit=512', '--user', f'{os.getuid()}:{os.getgid()}',
               '--network=none', '-e', 'MPLCONFIGDIR=/home/research/mpl',
               '-v', f'{HERE}:/study:ro', '-v', f'{BASE / "v1"}:/input:ro',
               '-v', f'{out}:/output:rw', '-v', f'{BASE / "cache"}:/home/research:rw']
    if stage == 'run':
        command += ['--runtime=nvidia', '--gpus', 'device=0',
                    '-e', 'NVIDIA_DRIVER_CAPABILITIES=graphics,utility,compute',
                    '-e', 'VK_ICD_FILENAMES=/opt/ManiSkill/docker/nvidia_icd.json',
                    '-e', 'CUDA_VISIBLE_DEVICES=0']
    script = {'run': 'hold.py', 'verify': 'hold_verify.py', 'diagnose': 'hold_diagnose.py'}[stage]
    command += [IMAGE, 'timeout', '900s' if stage == 'run' else '3600s',
                'python', '-B', '-u', '/study/' + script]
    log = ROOT / 'logs' / f'{stamp}_q15_hold_{stage}.log'
    record = dict(stage=f'hold_{stage}', status='launched', attempt=attempt, container=name,
                  command=command, working_directory=str(ROOT), output=str(out),
                  log=str(log), exit=str(log.with_suffix('.exit')), image_id=IMAGE)
    path = BASE / 'jobs' / f'{stamp}_hold_{stage}.json'
    path.write_text(json.dumps(record, indent=2) + '\n')
    with log.open('xb') as stream:
        proc = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '_worker', str(path)],
                                cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL, start_new_session=True)
    print(json.dumps(dict(pid=proc.pid, record=str(path), log=str(log)), indent=2))


if __name__ == '__main__':
    if sys.argv[1] == '_worker':
        worker(sys.argv[2])
    else:
        launch(sys.argv[1], sys.argv[2])
