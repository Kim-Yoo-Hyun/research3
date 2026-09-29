"""Compact stdlib-only publication of verified Q16 push metadata; no simulator imports."""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT / 'runs/q16/push'


def read(path):
    return json.loads(path.read_text())


def paired(rows, condition, compared, base='frozen'):
    baseline = {r['seed']: r['native_success'] for r in rows if r['condition'] == condition and r['route'] == base}
    method = {r['seed']: r['native_success'] for r in rows if r['condition'] == condition and r['route'] == compared}
    assert set(baseline) == set(method) and len(baseline) == 16
    return dict(rescued=sum(method[s] and not baseline[s] for s in baseline),
                harmed=sum(baseline[s] and not method[s] for s in baseline),
                unchanged=sum(baseline[s] == method[s] for s in baseline))


def main():
    teacher = read(OUT / 'collect1/collection.json')['records']
    assert len(teacher) == 160
    splits = {}
    for name in ('nominal_train', 'nominal_val', 'extra_train', 'extra_val'):
        rows = [r for r in teacher if r['split'] == name]
        splits[name] = dict(n=len(rows), native_success=sum(r['native_success'] for r in rows))
    assert [splits[n]['n'] for n in splits] == [96, 24, 32, 8]
    first = read(OUT / 'verify1/verification.json')
    revision = read(OUT / 'verify2/verification.json')
    assert first['evaluation_episodes'] == 192 and revision['evaluation_episodes'] == 256
    fit = read(OUT / 'fit1/fit.json')
    results = {}
    csv_rows = []
    for run, expected in (('eval1', 192), ('eval2', 256)):
        data = read(OUT / run / 'episodes.json')
        rows = data['records']
        assert len(rows) == expected
        assert {r['seed'] for r in rows}.isdisjoint(set(range(40000, 40120)) | set(range(41000, 41040)))
        results[run] = dict(seed_start=data['seed_start'], seed_count=data['seed_count'],
                            groups=(first if run == 'eval1' else revision)['groups'],
                            paired={condition: {route: paired(rows, condition, route)
                                                 for route in data['routes'] if route != 'frozen'}
                                    for condition in ('nominal', 'low_friction')})
        for row in rows:
            csv_rows.append(dict(run=run, **{k: row[k] for k in ('seed', 'condition', 'route',
                              'native_success', 'final_xy_error_m', 'cube_x_progress_m',
                              'first_success_s', 'mean_latency_ms', 'mean_prediction_error_m')}))
    summary = dict(study='Q16 collision-only PushCube feasibility', status='verified exploratory observation',
                   source_commit='a4a4f9272ad64b1564035874b605ceb687b63ed8',
                   native_goal_radius_m=0.1, episode_steps=50,
                   image_id=read(sorted((OUT / 'jobs').glob('*_build.json'))[0])['inspection']['Id'],
                   teacher=splits,
                   model_fit={k: {key: fit[k][key] for key in ('train_windows', 'val_windows', 'parameters', 'best_epoch')}
                              for k in ('frozen_policy', 'updated_policy', 'dynamics')},
                   dynamics_val_object_rmse_m=fit['dynamics']['val_object_rmse_m'],
                   verification=dict(first=dict(episodes=first['evaluation_episodes'], states=first['states'],
                                                checked_checksums=first['checked_checksum_count']),
                                     revision=dict(episodes=revision['evaluation_episodes'], states=revision['states'],
                                                   checked_checksums=revision['checked_checksum_count'])),
                   evaluation=results,
                   claim_boundary='Full-state single-shape feasibility only; no positive prediction-correction, data-efficiency, visual or generality claim.')
    (HERE / 'push_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    with (HERE / 'push_episodes.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(csv_rows[0]))
        writer.writeheader()
        writer.writerows(csv_rows)
    print(json.dumps(dict(episodes=len(csv_rows), teacher=len(teacher), runs=list(results)), indent=2))


if __name__ == '__main__':
    main()
