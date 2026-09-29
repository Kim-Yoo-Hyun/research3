"""Host stdlib-only background Docker/fetch launcher for the two-case PushT route."""
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
OUT = ROOT / 'runs/q16/pusht_repeat'
TAG = 'research3-q16-pusht-repeat:v1'
DATA_URL = 'https://diffusion-policy.cs.columbia.edu/data/training/pusht.zip'
FILES = ('Dockerfile.repeat', 'requirements.repeat.lock', 'repeat_probe.py',
         'repeat_verify.py', 'repeat_bc.py', 'repeat_bc_verify.py',
         'repeat_failure_probe.py', 'repeat_failure_verify.py',
         'repeat_action_model.py', 'repeat_action_contrast.py', 'repeat_action_verify.py',
         'repeat_job.py')


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
    if rec['stage'] == 'build':
        cmd = ['docker', 'image', 'inspect', TAG]
    elif rec['stage'] == 'fetch':
        cmd = None
    else:
        cmd = ['docker', 'inspect', rec['container']]
    if cmd is not None:
        inspected = subprocess.run(cmd, capture_output=True, text=True)
        if inspected.returncode == 0:
            info = json.loads(inspected.stdout)[0]
            rec['inspection'] = {key: info.get(key) for key in
                                 ('Id', 'State', 'Image', 'Config', 'HostConfig', 'Mounts', 'RepoDigests')}
    write(path, rec)


def launch(stage):
    if stage not in ('build', 'fetch', 'lock', 'probe', 'verify', 'fitbc', 'evalbc', 'verifybc',
                     'failureprobe', 'failureverify', 'model', 'contrast', 'contrastverify'):
        raise ValueError(stage)
    if stage == 'probe' and (OUT / 'probe1').exists():
        raise FileExistsError(OUT / 'probe1')
    if stage == 'verify' and not (OUT / 'probe1/assessment.json').exists():
        raise FileNotFoundError(OUT / 'probe1/assessment.json')
    if stage == 'fitbc' and (OUT / 'bc_fit1').exists():
        raise FileExistsError(OUT / 'bc_fit1')
    if stage == 'evalbc' and not (OUT / 'bc_fit1/fit.json').exists():
        raise FileNotFoundError(OUT / 'bc_fit1/fit.json')
    if stage == 'evalbc' and (OUT / 'bc_eval1').exists():
        raise FileExistsError(OUT / 'bc_eval1')
    if stage == 'verifybc' and not (OUT / 'bc_eval1/evaluation.json').exists():
        raise FileNotFoundError(OUT / 'bc_eval1/evaluation.json')
    if stage == 'failureprobe' and not (OUT / 'bc_eval1/verification.json').exists():
        raise FileNotFoundError(OUT / 'bc_eval1/verification.json')
    if stage == 'failureprobe' and (OUT / 'failure_branch1').exists():
        raise FileExistsError(OUT / 'failure_branch1')
    if stage == 'failureverify' and not (OUT / 'failure_branch1/assessment.json').exists():
        raise FileNotFoundError(OUT / 'failure_branch1/assessment.json')
    if stage == 'model' and (OUT / 'fit_model1').exists():
        raise FileExistsError(OUT / 'fit_model1')
    if stage == 'contrast' and not (OUT / 'fit_model1/fit.json').exists():
        raise FileNotFoundError(OUT / 'fit_model1/fit.json')
    if stage == 'contrast' and not (OUT / 'failure_branch1/verification.json').exists():
        raise FileNotFoundError(OUT / 'failure_branch1/verification.json')
    if stage == 'contrast' and (OUT / 'contrast1').exists():
        raise FileExistsError(OUT / 'contrast1')
    if stage == 'contrastverify' and not (OUT / 'contrast1/assessment.json').exists():
        raise FileNotFoundError(OUT / 'contrast1/assessment.json')
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    jobs = OUT / 'jobs'
    jobs.mkdir(parents=True, exist_ok=True)
    source = jobs / f'{stamp}_source'
    source.mkdir()
    for name in FILES:
        shutil.copy2(HERE / name, source / name)
    source_hashes = {name: hashlib.sha256((source / name).read_bytes()).hexdigest() for name in FILES}
    container = f'research3-q16-pusht-repeat-{stage}-{stamp}'
    image_id = None
    if stage == 'build':
        command = ['docker', 'build', '--no-cache', '--progress=plain', '-t', TAG,
                   '-f', str(HERE / 'Dockerfile.repeat'), str(HERE)]
    elif stage == 'fetch':
        (OUT / 'demos').mkdir(exist_ok=True)
        command = ['curl', '--fail', '--location', '--continue-at', '-', '--output',
                   str(OUT / 'demos/pusht.zip'), DATA_URL]
    else:
        image_id = json.loads(subprocess.check_output(['docker', 'image', 'inspect', TAG]))[0]['Id']
        command = ['docker', 'run', '--name', container,
                   '--label', f'research3.workspace={ROOT}', '--label', 'research3.study=q16-pusht-repeat',
                   '--cpus=4', '--memory=4g', '--memory-swap=4g', '--pids-limit=256',
                   '--user', f'{os.getuid()}:{os.getgid()}', '--network', 'none',
                   '-v', f'{source}:/study:ro', '-v', f'{OUT}:/output:rw', image_id]
        if stage == 'lock':
            command += ['sh', '-c', 'cp /recipe/installed.repeat.lock /output/installed.repeat.lock']
        elif stage == 'fitbc':
            command += ['timeout', '600s', 'python', '-B', '-u', '/study/repeat_bc.py', 'fit']
        elif stage == 'evalbc':
            command += ['timeout', '1200s', 'python', '-B', '-u', '/study/repeat_bc.py', 'evaluate']
        elif stage == 'verifybc':
            command += ['timeout', '600s', 'python', '-B', '-u', '/study/repeat_bc_verify.py']
        elif stage == 'failureprobe':
            command += ['timeout', '600s', 'python', '-B', '-u', '/study/repeat_failure_probe.py']
        elif stage == 'failureverify':
            command += ['timeout', '600s', 'python', '-B', '-u', '/study/repeat_failure_verify.py']
        elif stage == 'model':
            command += ['timeout', '600s', 'python', '-B', '-u', '/study/repeat_action_model.py']
        elif stage == 'contrast':
            command += ['timeout', '600s', 'python', '-B', '-u', '/study/repeat_action_contrast.py']
        elif stage == 'contrastverify':
            command += ['timeout', '600s', 'python', '-B', '-u', '/study/repeat_action_verify.py']
        else:
            command += ['timeout', '600s', 'python', '-B', '-u', f'/study/repeat_{stage}.py']
    log = ROOT / 'logs' / f'{stamp}_q16_pusht_repeat_{stage}.log'
    record = jobs / f'{stamp}_{stage}.json'
    write(record, dict(stage=stage, status='launched', command=command, container=container,
                       image_tag=TAG, image_id=image_id, source_snapshot=str(source),
                       source_sha256=source_hashes, working_directory=str(ROOT),
                       output=str(OUT), expected=dict(build=TAG, fetch=str(OUT / 'demos/pusht.zip'),
                                                       lock=str(OUT / 'installed.repeat.lock'),
                                                       probe=str(OUT / 'probe1/assessment.json'),
                                                       verify=str(OUT / 'probe1/verification.json'),
                                                       fitbc=str(OUT / 'bc_fit1/fit.json'),
                                                       evalbc=str(OUT / 'bc_eval1/evaluation.json'),
                                                       verifybc=str(OUT / 'bc_eval1/verification.json'),
                                                       failureprobe=str(OUT / 'failure_branch1/assessment.json'),
                                                       failureverify=str(OUT / 'failure_branch1/verification.json'),
                                                       model=str(OUT / 'fit_model1/fit.json'),
                                                       contrast=str(OUT / 'contrast1/assessment.json'),
                                                       contrastverify=str(OUT / 'contrast1/verification.json'))[stage],
                       log=str(log), exit=str(log.with_suffix('.exit')), device='cpu'))
    with log.open('xb') as stream:
        proc = subprocess.Popen([sys.executable, str(HERE / 'repeat_job.py'), '_worker', str(record)],
                                cwd=ROOT, stdin=subprocess.DEVNULL, stdout=stream,
                                stderr=subprocess.STDOUT, start_new_session=True)
    print(json.dumps(dict(pid=proc.pid, record=str(record), log=str(log)), indent=2))


if __name__ == '__main__':
    if sys.argv[1] == '_worker':
        worker(sys.argv[2])
    else:
        launch(sys.argv[1])
