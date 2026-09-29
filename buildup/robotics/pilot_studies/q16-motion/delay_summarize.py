"""Compact stdlib-only summary of verified delayed-observation Q16 metadata."""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT / 'runs/q16/delay'


def read(path):
    return json.loads(path.read_text())


def paired(rows, condition, method, baseline):
    left = {r['seed']: r['native_success'] for r in rows if r['condition'] == condition and r['route'] == baseline}
    right = {r['seed']: r['native_success'] for r in rows if r['condition'] == condition and r['route'] == method}
    assert set(left) == set(right) and len(left) == 16
    return dict(rescued=sum(right[k] and not left[k] for k in left),
                harmed=sum(left[k] and not right[k] for k in left),
                unchanged=sum(left[k] == right[k] for k in left))


def main():
    collection = read(OUT / 'collect1/collection.json')
    teacher = collection['records']
    assert len(teacher) == 160
    splits = {}
    for name in ('nominal_train', 'nominal_val', 'extra_train', 'extra_val'):
        items = [r for r in teacher if r['split'] == name]
        splits[name] = dict(n=len(items), native_success=sum(r['native_success'] for r in items))
    assert [splits[name]['n'] for name in splits] == [96, 24, 32, 8]
    payload = read(OUT / 'eval1/episodes.json')
    rows = payload['records']
    verification = read(OUT / 'verify1/verification.json')
    fit = read(OUT / 'fit1/fit.json')
    assert len(rows) == verification['evaluation_episodes'] == 192
    assert verification['lag_steps'] == 4
    assert {r['seed'] for r in rows}.isdisjoint(set(range(40000, 40120)) | set(range(41000, 41040))
                                             | set(range(45000, 45008)))
    pair = {condition: {route: paired(rows, condition, route, 'frozen')
                        for route in payload['routes'] if route != 'frozen'}
            for condition in ('nominal', 'low_friction')}
    summary = dict(study='Q16 delayed object observation on collision-only PushCube',
                   status='verified exploratory observation', source_commit='a4a4f9272ad64b1564035874b605ceb687b63ed8',
                   image_id=read(sorted((OUT / 'jobs').glob('*_build.json'))[0])['inspection']['Id'],
                   lag_steps=4, lag_seconds=0.2, native_goal_radius_m=0.1, episode_steps=50,
                   teacher=splits, model_fit={name: {key: fit[name][key] for key in
                            ('train_windows', 'val_windows', 'parameters', 'best_epoch')}
                            for name in ('frozen_policy', 'updated_policy', 'dynamics')},
                   dynamics_val_object_rmse_m=fit['dynamics']['val_object_rmse_m'],
                   evaluation=dict(seed_start=payload['seed_start'], seed_count=payload['seed_count'],
                                   routes=payload['routes'], groups=verification['groups'],
                                   paired_vs_frozen=pair, episodes=len(rows), states=verification['states'],
                                   checked_checksums=verification['checked_checksum_count']),
                   claim_boundary='Constructed exact-state 0.2 s latency; clean feedback is privileged reference. No visual, real-world, multi-object or paper-level claim.')
    (HERE / 'delay_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    columns = ('seed', 'condition', 'route', 'native_success', 'final_xy_error_m',
               'cube_x_progress_m', 'first_success_s', 'mean_latency_ms', 'mean_prediction_error_m')
    with (HERE / 'delay_episodes.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows({key: row[key] for key in columns} for row in rows)
    print(json.dumps(dict(episodes=len(rows), states=verification['states'], teacher=len(teacher)), indent=2))


if __name__ == '__main__':
    main()
