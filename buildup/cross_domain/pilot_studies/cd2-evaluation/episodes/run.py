"""LBM finite-record sampling study. Execute only in the documented CPU Docker."""
import csv
import hashlib
import itertools
import json
import math
import platform
import random
import shutil
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

ROOT, INPUT, OUT = Path('/study'), Path('/input'), Path('/output')


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def avg(values):
    return math.fsum(values) / len(values) if values else None


def quantile(values, q):
    if not values:
        return None
    a = sorted(values)
    i = (len(a) - 1) * q
    lo = math.floor(i)
    return a[lo] + (a[min(lo + 1, len(a) - 1)] - a[lo]) * (i - lo)


def sign(value):
    return 0 if abs(value) <= 1e-12 else (1 if value > 0 else -1)


def ordering(estimate, reference):
    if estimate is None:
        return 'missing'
    if sign(reference) == 0:
        return 'reference_tie'
    if sign(estimate) == 0:
        return 'predicted_tie'
    return 'correct' if sign(estimate) == sign(reference) else 'reversed'


def normalize(cfg):
    for f in cfg['input_files']:
        data = (INPUT / f['path']).read_bytes()
        assert len(data) == f['bytes']
        assert hashlib.sha256(data).hexdigest() == f['sha256']
    table = pd.read_pickle(INPUT / 'nscore/data/LBM/lbm_data.pkl')[cfg['key']].reset_index()
    assert len(table) == 10 and not table.duplicated(['policy_type', 'skill']).any()
    assert set(table.policy_type) == set(cfg['policies'])
    assert set(table.skill) == set(cfg['tasks'])
    result, mappings = {}, []
    for policy in cfg['policies']:
        result[policy] = {}
        for task in cfg['tasks']:
            row = table[(table.policy_type == policy) & (table.skill == task)].iloc[0]
            success = np.asarray(row['success'], dtype=float)
            progress = np.asarray(row['task_progress'], dtype=float)
            k = int(row['n_questions'])
            assert k == row['n_questions'] and k > 0
            assert row['num_rollouts'] == 50 and success.shape == progress.shape == (50,)
            assert np.isin(success, [0, 1]).all()
            assert np.isfinite(progress).all() and ((0 <= progress) & (progress <= 1)).all()
            steps = np.rint(progress * k).astype(int)
            assert np.allclose(progress, steps / k, rtol=0, atol=1e-12)
            result[policy][task] = {'success': success.astype(int).tolist(),
                                    'progress': progress.tolist(), 'progress_steps': steps.tolist(),
                                    'n_questions': k, 'num_rollouts': 50}
    for task in cfg['tasks']:
        for folder in ['LBM', 'PC_LBM']:
            path = f'nscore/data/{folder}/Part2/{task}.npy'
            a = np.load(INPUT / path, allow_pickle=False)
            assert a.shape == (50, 2) and a.dtype == np.dtype('<f8')
            matches = [{'metric': metric, 'columns': list(cols)}
                       for metric in cfg['metrics'] for cols in itertools.permutations(range(2))
                       if all(np.allclose(a[:, col], result[p][task][metric], rtol=0, atol=1e-12)
                              for p, col in zip(cfg['policies'], cols))]
            assert matches, (path, 'no column mapping matches original pickle')
            mappings.append({'path': path, 'task': task, 'matches': matches})
    return {'policies': cfg['policies'], 'tasks': cfg['tasks'], 'data': result,
            'npy_mappings': mappings, 'record_count': 500,
            'metric_linkage': 'same-position success/progress arrays in each source row; no independent episode IDs',
            'cross_policy_pairing': 'not assumed'}


def reference(normal, cfg):
    ref = {}
    for metric in cfg['metrics']:
        means = {p: [avg(normal['data'][p][t][metric]) for t in cfg['tasks']] for p in cfg['policies']}
        ref[metric] = {'task_means': means, 'global_means': {p: avg(v) for p, v in means.items()},
                       'task_gaps': [b-a for a, b in zip(*[means[p] for p in cfg['policies']])]}
        ref[metric]['global_gap'] = avg(ref[metric]['task_gaps'])
    return ref


def shuffled(seed, method, policy, task, population):
    token = f'cd2-episodes-v1|{seed}|{method}|{policy}|{task}'
    rng = random.Random(int.from_bytes(hashlib.sha256(token.encode()).digest(), 'big'))
    values = list(population)
    rng.shuffle(values)
    return values


def score(values, indices, task_refs, global_ref):
    observed = [[i for i in indices if i // 50 == t] for t in range(5)]
    profile = [avg([values[i] for i in group]) for group in observed]
    errors = [None if x is None else x-r for x, r in zip(profile, task_refs)]
    valid_errors = [abs(x) for x in errors if x is not None]
    estimate = avg([values[i] for i in indices])
    oracle = avg([task_refs[i // 50] for i in indices])
    return {'reference': global_ref, 'estimate': estimate, 'error': estimate-global_ref,
            'oracle_estimate': oracle, 'mix_error': oracle-global_ref,
            'within_error': estimate-oracle, 'task_counts': list(map(len, observed)),
            'task_estimates': profile, 'task_errors': errors, 'observed_tasks': len(valid_errors),
            'partial_profile_mae': avg(valid_errors),
            'full_profile_mae': avg(valid_errors) if len(valid_errors) == 5 else None,
            'full_profile_max_error': max(valid_errors) if len(valid_errors) == 5 else None}


def gap(a, b, ref):
    profile = [None if x is None or y is None else y-x
               for x, y in zip(a['task_estimates'], b['task_estimates'])]
    errors = [None if x is None else x-r for x, r in zip(profile, ref['task_gaps'])]
    valid = [abs(x) for x in errors if x is not None]
    estimate = b['estimate'] - a['estimate']
    return {'reference': ref['global_gap'], 'estimate': estimate,
            'error': estimate-ref['global_gap'], 'status': ordering(estimate, ref['global_gap']),
            'mix_error': b['mix_error']-a['mix_error'], 'within_error': b['within_error']-a['within_error'],
            'task_estimates': profile, 'task_errors': errors,
            'task_status': [ordering(x, r) for x, r in zip(profile, ref['task_gaps'])],
            'observed_tasks': len(valid), 'partial_profile_mae': avg(valid),
            'full_profile_mae': avg(valid) if len(valid) == 5 else None,
            'full_profile_max_error': max(valid) if len(valid) == 5 else None}


def summaries(scores, gaps, cfg):
    summary, tasks = [], []
    for n, method, metric in itertools.product(cfg['n_per_cell'], cfg['methods'], cfg['metrics']):
        ss = [r for r in scores if (r['n'], r['method'], r['metric']) == (n, method, metric)]
        gg = [r for r in gaps if (r['n'], r['method'], r['metric']) == (n, method, metric)]
        states = Counter(r['status'] for r in gg)
        full_s = [r for r in ss if r['full_profile_mae'] is not None]
        full_g = [r for r in gg if r['full_profile_mae'] is not None]
        row = {'n': n, 'record_budget': 10*n, 'method': method, 'metric': metric,
               'draws': len(gg), 'policy_draws': len(ss), 'complete_policy_draws': len(full_s),
               'complete_gap_draws': len(full_g), 'global_mae_pp': 100*avg([abs(r['error']) for r in ss]),
               'gap_mae_pp': 100*avg([abs(r['error']) for r in gg]),
               'task_mean_mae_pp': 100*avg([r['full_profile_mae'] for r in full_s]),
               'task_gap_mae_pp': 100*avg([r['full_profile_mae'] for r in full_g]),
               'max_task_gap_error_mean_pp': 100*avg([r['full_profile_max_error'] for r in full_g]),
               'global_gap_abs_error_p95_pp': 100*quantile([abs(r['error']) for r in gg], .95),
               'max_task_gap_error_p95_pp': 100*quantile([r['full_profile_max_error'] for r in full_g], .95),
               'missing_task_policy_pairs': sum(5-r['observed_tasks'] for r in ss),
               **{f'global_{s}': states[s] for s in ['correct','reversed','predicted_tie','reference_tie']},
               'gap_mix_mae_pp': 100*avg([abs(r['mix_error']) for r in gg]),
               'gap_within_mae_pp': 100*avg([abs(r['within_error']) for r in gg])}
        summary.append(row)
        for i, task in enumerate(cfg['tasks']):
            valid = [r for r in gg if r['task_errors'][i] is not None]
            states = Counter(r['task_status'][i] for r in gg)
            tasks.append({'n': n, 'method': method, 'metric': metric, 'task': task,
                          'draws': len(gg), 'observed_draws': len(valid),
                          'gap_mae_pp': 100*avg([abs(r['task_errors'][i]) for r in valid]),
                          'gap_error_p05_pp': 100*quantile([r['task_errors'][i] for r in valid], .05),
                          'gap_error_p95_pp': 100*quantile([r['task_errors'][i] for r in valid], .95),
                          **{s: states[s] for s in ['correct','reversed','predicted_tie','reference_tie','missing']}})
    return summary, tasks


def main():
    start = time.monotonic()
    assert not (OUT / 'normalized.json').exists(), 'Do not overwrite prior output'
    cfg = json.loads((ROOT / 'protocol.json').read_text())
    normal = normalize(cfg)
    dump(OUT / 'normalized.json', normal)
    ref = reference(normal, cfg)
    dump(OUT / 'reference.json', ref)
    subsets, scores, gaps = [], [], []
    for method, seed in itertools.product(cfg['methods'], cfg['seeds']):
        orders = {}
        for p in cfg['policies']:
            orders[p] = (shuffled(seed, method, p, 'all', range(250)) if method == 'uniform' else
                         [shuffled(seed, method, p, t, range(i*50, (i+1)*50)) for i, t in enumerate(cfg['tasks'])])
        for n in cfg['n_per_cell']:
            selected = {p: orders[p][:5*n] if method == 'uniform' else
                        [i for group in orders[p] for i in group[:n]] for p in cfg['policies']}
            key = {'method': method, 'seed': seed, 'n': n}
            subsets.append({**key, 'indices': selected})
            for metric in cfg['metrics']:
                pair = []
                for p in cfg['policies']:
                    values = [x for t in cfg['tasks'] for x in normal['data'][p][t][metric]]
                    row = {**key, 'metric': metric, 'policy': p,
                           **score(values, selected[p], ref[metric]['task_means'][p], ref[metric]['global_means'][p])}
                    scores.append(row)
                    pair.append(row)
                gaps.append({**key, 'metric': metric, **gap(*pair, ref[metric])})
    summary, task_summary = summaries(scores, gaps, cfg)
    for name, rows in [('subsets', subsets), ('scores', scores), ('gaps', gaps)]:
        with (OUT / f'{name}.jsonl').open('w') as f:
            for row in rows:
                f.write(json.dumps(row, allow_nan=False)+'\n')
    for name, rows in [('summary', summary), ('task_summary', task_summary)]:
        dump(OUT / f'{name}.json', rows)
        with (OUT / f'{name}.csv').open('w') as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    source = OUT / 'source'
    source.mkdir()
    for path in ROOT.iterdir():
        if path.is_file():
            shutil.copy2(path, source / path.name)
    shutil.copy2('/opt/install.json', OUT / 'install.json')
    artifacts = {p.name: {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                 for p in OUT.iterdir() if p.is_file() and p.suffix in {'.json','.jsonl','.csv'}}
    dump(OUT / 'execution.json', {'elapsed_seconds': time.monotonic()-start, 'mode': 'CPU',
         'versions': {'python': platform.python_version(), 'numpy': np.__version__, 'pandas': pd.__version__},
         'source_commit': cfg['source_commit'], 'protocol_sha256': hashlib.sha256((ROOT/'protocol.json').read_bytes()).hexdigest(),
         'counts': {'records': 500, 'subsets': len(subsets), 'scores': len(scores), 'gaps': len(gaps),
                    'summary': len(summary), 'task_summary': len(task_summary)}, 'artifacts': artifacts})
    print(json.dumps({'counts': {'subsets': len(subsets), 'scores': len(scores), 'gaps': len(gaps)},
                      'reference': ref, 'seconds': time.monotonic()-start}, indent=2))


if __name__ == '__main__':
    main()
