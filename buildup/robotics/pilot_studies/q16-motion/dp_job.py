"""Host stdlib-only background Docker launcher for released Push-T policy audit."""
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
OUT = ROOT / 'runs/q16/dp_reference'
COMMIT = '5ba07ac6661db573af695b419a7947ecb704690f'
SOURCE = ROOT / 'external/q16' / f'diffusion_policy-{COMMIT}'
CHECKPOINT = OUT / 'checkpoint/epoch=0550-test_mean_score=0.969.ckpt'
TAG = 'research3-q16-dp-reference:v2'
BASE_FILES = ('Dockerfile.dp_reference', 'Dockerfile.dp_reference_patch',
              'requirements.dp.lock', 'dp_job.py', 'repeat_bc.py')
STAGE_FILE = {'inspect': 'dp_inspect.py', 'parity': 'dp_parity.py',
              'evaluate': 'dp_evaluate.py', 'verify': 'dp_verify.py',
              'branch': 'dp_branch.py', 'branchverify': 'dp_branch_verify.py',
              'lock': 'dp_lock.py', 'obsaudit': 'dp_obs_audit.py',
              'obsresolve': 'dp_obs_resolve.py',
              'traincontract': 'dp_train_contract.py',
              'finetune': 'dp_finetune.py', 'compare': 'dp_compare.py',
              'compareverify': 'dp_compare_verify.py',
              'chunk': 'dp_chunk.py', 'chunkverify': 'dp_chunk_verify.py'}


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
        code = subprocess.run(job['command'], cwd=ROOT).returncode
    except Exception as exc:
        code = 125
        job['exception'] = repr(exc)
    Path(job['exit']).write_text(str(code) + '\n')
    job['returncode'] = code
    job['status'] = 'completed' if code == 0 else 'failed'
    command = ['docker', 'image', 'inspect', TAG] if job['stage'] in ('build', 'build_patch') else ['docker', 'inspect', job['container']]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        info = json.loads(result.stdout)[0]
        job['inspection'] = {key: info.get(key) for key in
                             ('Id', 'Image', 'State', 'Config', 'HostConfig', 'Mounts', 'RepoDigests')}
    write(record, job)


def launch(stage):
    if stage not in ('build_patch', 'inspect', 'parity', 'evaluate', 'verify',
                     'branch', 'branchverify', 'lock', 'obsaudit', 'finetune',
                     'compare', 'compareverify', 'chunk', 'chunkverify',
                     'obsresolve', 'traincontract'):
        raise ValueError(stage)
    if stage != 'build_patch':
        assert SOURCE.is_dir() and CHECKPOINT.is_file()
        assert CHECKPOINT.stat().st_size == 1044185793
        if stage in ('parity', 'evaluate', 'verify'):
            assert (OUT / 'inspect1/config.json').exists()
        if stage in ('evaluate', 'verify'):
            assert (OUT / 'parity1/assessment.json').exists()
        if stage == 'verify':
            assert (OUT / 'eval1/evaluation.json').exists()
        if stage in ('branch', 'branchverify'):
            assert (OUT / 'eval1/verification.json').exists()
        if stage == 'branchverify':
            assert (OUT / 'branch1/assessment.json').exists()
        if stage in ('obsresolve','finetune','compare','compareverify'):
            assert (OUT / 'observation1/assessment.json').exists()
        if stage in ('traincontract','finetune','compare','compareverify'):
            assert (OUT / 'observation2/assessment.json').exists()
        if stage in ('finetune','compare','compareverify'):
            assert (OUT / 'traincontract1/assessment.json').exists()
        if stage in ('compare','compareverify'):
            assert (OUT / 'finetune1/checkpoint.pt').exists()
        if stage == 'compareverify':
            assert (OUT / 'compare1/evaluation.json').exists()
        if stage == 'chunkverify':
            assert (OUT / 'chunk1/evaluation.json').exists()
    stage_dirs = {'inspect': 'inspect1', 'parity': 'parity1', 'evaluate': 'eval1',
                  'branch': 'branch1', 'obsaudit':'observation1',
                  'obsresolve':'observation2','traincontract':'traincontract1',
                  'finetune':'finetune1','compare':'compare1','chunk':'chunk1'}
    if stage in stage_dirs and (OUT / stage_dirs[stage]).exists():
        raise FileExistsError(OUT / stage_dirs[stage])
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    jobs = OUT / 'jobs'
    jobs.mkdir(parents=True, exist_ok=True)
    snapshot = jobs / f'{stamp}_{stage}_source'
    snapshot.mkdir()
    files = BASE_FILES + ('dp_observation.py','repeat_action_model.py') + tuple(
        x for x in STAGE_FILE.values() if (HERE / x).exists())
    for name in files:
        shutil.copy2(HERE / name, snapshot / name)
    source_hashes = {name: digest(snapshot / name) for name in files}
    image_id = None
    container = f'research3-q16-dp-reference-{stage}-{stamp}'
    if stage == 'build_patch':
        parent_id = json.loads(subprocess.check_output([
            'docker', 'image', 'inspect', 'research3-q16-dp-reference:v1']))[0]['Id']
        assert parent_id == 'sha256:0aa82464b3bff8483621c2a432305dcc5e7b486d1e460052c7b579a2291f96c0'
        command = ['docker', 'build', '--no-cache', '--progress=plain', '-t', TAG,
                   '-f', str(HERE / 'Dockerfile.dp_reference_patch'), str(HERE)]
    else:
        image_id = json.loads(subprocess.check_output(['docker', 'image', 'inspect', TAG]))[0]['Id']
        command = ['docker', 'run', '--name', container,
                   '--label', f'research3.workspace={ROOT}', '--label', 'research3.study=q16-dp-reference',
                   '--cpus=8', '--memory=16g', '--memory-swap=16g', '--pids-limit=256',
                   '--shm-size=2g', '--user', f'{os.getuid()}:{os.getgid()}', '--network', 'none',
                   '-e', 'PYTHONPATH=/source', '-e', 'SDL_VIDEODRIVER=dummy',
                   '-v', f'{snapshot}:/study:ro', '-v', f'{SOURCE}:/source:ro',
                   '-v', f'{CHECKPOINT}:/checkpoint/model.ckpt:ro',
                   '-v', f'{ROOT / "runs/q16/pusht_repeat"}:/previous:ro',
                   '-v', f'{OUT}:/output:rw']
        if stage in ('evaluate', 'branch', 'finetune', 'compare', 'chunk'):
            command += ['--gpus', 'all']
        command += [image_id, 'timeout', '7200s' if stage == 'chunk' else '1800s',
                    'python', '-B', '-u', f'/study/{STAGE_FILE[stage]}']
    log = ROOT / 'logs' / f'{stamp}_q16_dp_reference_{stage}.log'
    record = jobs / f'{stamp}_{stage}.json'
    write(record, dict(stage=stage, status='launched', command=command,
                       container=container if stage != 'build_patch' else None,
                       image_tag=TAG, image_id=image_id, source_commit=COMMIT,
                       parent_image_id=parent_id if stage == 'build_patch' else None,
                       source_archive_sha256=digest(ROOT / 'external/q16' / f'diffusion_policy-{COMMIT}.tar.gz')
                       if (ROOT / 'external/q16' / f'diffusion_policy-{COMMIT}.tar.gz').exists() else None,
                       checkpoint_sha256=digest(CHECKPOINT) if stage != 'build_patch' else None,
                       source_snapshot=str(snapshot), source_sha256=source_hashes,
                       working_directory=str(ROOT), output=str(OUT),
                       expected=dict(build_patch=TAG, inspect=str(OUT/'inspect1/config.json'),
                                     parity=str(OUT/'parity1/assessment.json'),
                                     evaluate=str(OUT/'eval1/evaluation.json'),
                                     verify=str(OUT/'eval1/verification.json'),
                                     branch=str(OUT/'branch1/assessment.json'),
                                     branchverify=str(OUT/'branch1/verification.json'),
                                     lock=str(OUT/'installed.v2.lock'),
                                     obsaudit=str(OUT/'observation1/assessment.json'),
                                     obsresolve=str(OUT/'observation2/assessment.json'),
                                     traincontract=str(OUT/'traincontract1/assessment.json'),
                                     finetune=str(OUT/'finetune1/checkpoint.pt'),
                                     compare=str(OUT/'compare1/evaluation.json'),
                                     compareverify=str(OUT/'compare1/verification.json'),
                                     chunk=str(OUT/'chunk1/evaluation.json'),
                                     chunkverify=str(OUT/'chunk1/verification.json'))[stage],
                       device='gpu' if stage in ('evaluate', 'branch', 'finetune', 'compare', 'chunk') else 'cpu',
                       log=str(log), exit=str(log.with_suffix('.exit'))))
    with log.open('xb') as stream:
        proc = subprocess.Popen([sys.executable, str(snapshot/'dp_job.py'), '_worker', str(record)],
                                cwd=ROOT, stdin=subprocess.DEVNULL, stdout=stream,
                                stderr=subprocess.STDOUT, start_new_session=True)
    print(json.dumps(dict(pid=proc.pid, record=str(record), log=str(log)), indent=2))


if __name__ == '__main__':
    if sys.argv[1] == '_worker':
        worker(sys.argv[2])
    else:
        launch(sys.argv[1])
