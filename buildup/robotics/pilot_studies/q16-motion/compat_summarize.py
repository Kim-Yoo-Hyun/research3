"""Host stdlib-only reduction of completed Q16 compatibility manifests."""
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CPU = ROOT / 'runs/q16/compat_cpu'
GPU = ROOT / 'runs/q16/compat_gpu'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def counts(rows):
    return dict(final=sum(x['replay_final_success'] for x in rows),
                any=sum(x['replay_any_success'] for x in rows), total=len(rows))


def main():
    cpu = read(CPU / 'replay4/replay.json')
    native = read(GPU / 'native_replay1/replay.json')
    collision = read(GPU / 'collision_replay1/replay.json')
    for root, attempt in ((CPU, 'verify4'), (GPU, 'native_verify1'),
                          (GPU, 'collision_verify1'), (GPU, 'verify1'),
                          (GPU, 'verify_full1')):
        check = read(root / attempt / 'verification.json')
        assert check['status'] == 'passed'
    assert cpu['source_commit'] == native['source_commit'] == collision['source_commit']
    assert len(cpu['rows']) == len(native['rows']) == 8
    assert native['rows'] == collision['rows']
    official_log = (ROOT / 'logs/20260925_131132_212281_q16_compat_gpu_official.log').read_text(errors='replace')
    skipped = [int(value) for value in re.findall(r'Episode (\d+) is not replayed successfully', official_log)]
    assert skipped == [3, 4, 5, 7, 8, 9]
    data1 = read(GPU / 'data1/extraction.json')
    full = read(GPU / 'data_full1/extraction.json')
    fit1 = read(GPU / 'fit1/fit.json')
    fit_full = read(GPU / 'fit_full1/fit.json')
    eval1 = read(GPU / 'verify1/verification.json')
    eval_full = read(GPU / 'verify_full1/verification.json')
    assert fit1['data_sha256'] == data1['dataset_sha256']
    assert fit_full['data_sha256'] == full['dataset_sha256']
    assert data1['source_h5_sha256'] == full['source_h5_sha256'] == native['demo_h5_sha256']
    assert len(full['split']['train']) == 792 and len(full['split']['valid']) == 88
    demo_seeds = {item['episode_seed'] for item in read(
        ROOT / 'runs/q16/task_audit/demos/extracted/trajectory.none.pd_ee_delta_pos.physx_cuda.json')['episodes']}
    assert not demo_seeds.intersection(read(GPU / 'eval1/evaluation.json')['seeds'])
    assert not demo_seeds.intersection(read(GPU / 'eval_full1/evaluation.json')['seeds'])
    result = dict(status='verified exploratory study', date='2026-09-25',
                  source_commit=cpu['source_commit'],
                  demo_h5_sha256=native['demo_h5_sha256'],
                  cpu_image_id='sha256:48d17bb6a8df489b03d32ccdf22c64b1432caafa3ca8ee0df85d4fdcce0de6fc',
                  gpu_image_id='sha256:8dc6f2ae072476b71d03cb5c26e9f6500bcb6e6dfd41e45d77d5848595785d39',
                  installed_locks={name: sha(HERE / name) for name in
                                   ('installed.compat_cpu.lock', 'installed.compat_gpu.lock')},
                  demo_replay=dict(cpu=counts(cpu['rows']),
                                   native_cuda=counts(native['rows']),
                                   collision_cuda=counts(collision['rows']),
                                   native_collision_traces_identical=True,
                                   official_skipped_episode_ids=skipped),
                  state_observation=dict(dim=31, action_dim=3,
                                         dev_audit_episodes=8,
                                         train_episodes=full['train_episodes'],
                                         valid_episodes=full['valid_episodes'],
                                         train_rows=full['rows']['train'],
                                         valid_rows=full['rows']['valid']),
                  small_bc=dict(train_episodes=len(data1['split']['train']),
                                valid_episodes=len(data1['split']['valid']),
                                best_valid_action_mse=fit1['best_valid_mse'],
                                new_seed_count=8, final_success=eval1['final_success'],
                                mean_final_overlap=eval1['mean_final_metric']),
                  full_bc=dict(train_episodes=full['train_episodes'],
                               valid_episodes=full['valid_episodes'],
                               best_valid_action_mse=fit_full['best_valid_mse'],
                               new_seed_count=16, final_success=eval_full['final_success'],
                               mean_final_overlap=eval_full['mean_final_metric']),
                  claim_boundary='Action replay is not reliable for all source-success episodes; '
                                 'PPO is pretrained with different interaction data; '
                                 'full BC evaluation followed exploratory small-BC inspection; '
                                 'no prediction-correction or paper claim.')
    target = HERE / 'compat_summary.json'
    target.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(target)


if __name__ == '__main__':
    main()
