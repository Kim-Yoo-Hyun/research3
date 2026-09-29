"""Host stdlib launcher for pinned public source/checkpoint downloads only."""
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT / 'runs/q16/dp_reference'
COMMIT = '5ba07ac6661db573af695b419a7947ecb704690f'
SOURCE = ROOT / 'external/q16' / f'diffusion_policy-{COMMIT}.tar.gz'
CHECKPOINT = OUT / 'checkpoint/epoch=0550-test_mean_score=0.969.ckpt'
URLS = {
    'source': f'https://codeload.github.com/real-stanford/diffusion_policy/tar.gz/{COMMIT}',
    'checkpoint': ('https://diffusion-policy.cs.columbia.edu/data/experiments/low_dim/'
                   'pusht/diffusion_policy_cnn/train_0/checkpoints/'
                   'epoch=0550-test_mean_score=0.969.ckpt'),
}


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def worker(record):
    record = Path(record)
    job = json.loads(record.read_text())
    job['status'] = 'running'
    write(record, job)
    try:
        result = subprocess.run(job['command'], cwd=ROOT)
        code = result.returncode
    except Exception as exc:
        code = 125
        job['exception'] = repr(exc)
    if code == 0:
        output = Path(job['output'])
        job['bytes'] = output.stat().st_size
        job['sha256'] = digest(output)
        if job['stage'] == 'source':
            with tarfile.open(output) as archive:
                names = set(archive.getnames())
            prefix = f'diffusion_policy-{COMMIT}/'
            required = [prefix + name for name in
                        ('README.md', 'diffusion_policy/policy/diffusion_unet_lowdim_policy.py',
                         'diffusion_policy/env/pusht/pusht_env.py')]
            job['expected_members'] = {name: name in names for name in required}
            if not all(job['expected_members'].values()):
                code = 2
        elif job['bytes'] != 1044185793:
            code = 2
            job['size_mismatch'] = True
    Path(job['exit']).write_text(str(code) + '\n')
    job['returncode'] = code
    job['status'] = 'completed' if code == 0 else 'failed'
    write(record, job)


def launch(stage):
    if stage not in URLS:
        raise ValueError(stage)
    output = SOURCE if stage == 'source' else CHECKPOINT
    output.parent.mkdir(parents=True, exist_ok=True)
    jobs = OUT / 'jobs'
    jobs.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    snapshot = jobs / f'{stamp}_dp_fetch.py'
    shutil.copy2(__file__, snapshot)
    log = ROOT / 'logs' / f'{stamp}_q16_dp_reference_{stage}.log'
    command = ['curl', '--fail', '--location', '--continue-at', '-', '--retry', '4',
               '--retry-delay', '5', '--output', str(output), URLS[stage]]
    record = jobs / f'{stamp}_{stage}.json'
    write(record, dict(stage=stage, status='launched', command=command, output=str(output),
                       expected_bytes=1044185793 if stage == 'checkpoint' else None,
                       source_commit=COMMIT, working_directory=str(ROOT),
                       launcher_snapshot=str(snapshot), launcher_sha256=digest(snapshot),
                       log=str(log), exit=str(log.with_suffix('.exit'))))
    with log.open('xb') as stream:
        proc = subprocess.Popen([sys.executable, str(snapshot), '_worker', str(record)],
                                cwd=ROOT, stdin=subprocess.DEVNULL, stdout=stream,
                                stderr=subprocess.STDOUT, start_new_session=True)
    print(json.dumps(dict(pid=proc.pid, record=str(record), log=str(log)), indent=2))


if __name__ == '__main__':
    if sys.argv[1] == '_worker':
        worker(sys.argv[2])
    else:
        launch(sys.argv[1])
