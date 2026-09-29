"""Descriptive interpretation for eight fixed Taskography problems; Docker only."""
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import shutil
from statistics import mean, median
from pddl import read_plan

OUT = Path('/output/observation')


def main():
    rows = json.loads((OUT / 'results.json').read_text())
    verification = json.loads((OUT / 'verification.json').read_text())
    assert verification['status'] == 'PASS'
    groups = defaultdict(list)
    for r in rows:
        groups[(r['role'], r['condition'])].append(r)
    summaries = []
    for (role, condition), group in sorted(groups.items()):
        valid = [r for r in group if r['status'] == 'valid']
        lengths = [r['plan_length'] for r in valid]
        summaries.append({'role': role, 'condition': condition, 'attempts': len(group), 'valid': len(valid),
            'statuses': dict(Counter(r['status'] for r in group)),
            'plan_length_mean': mean(lengths) if lengths else None,
            'plan_length_median': median(lengths) if lengths else None,
            'planning_wall_mean': mean(r['planner']['wall_seconds'] for r in group),
            'planning_wall_median': median(r['planner']['wall_seconds'] for r in group),
            'preprocess_mean': mean(r['preprocess_seconds'] for r in group),
            'retained_objects_mean': mean(r['counts']['objects'] for r in group),
            'retained_facts_mean': mean(r['counts']['facts'] for r in group)})
    keyed = {(r['domain'], r['problem_id'], r['condition']): r for r in rows}
    pairs = []
    for r in rows:
        if r['role'] != 'primary' or r['condition'] == 'full':
            continue
        for reference in ['full', 'scrub']:
            if r['condition'] == reference:
                continue
            ref = keyed[(r['domain'], r['problem_id'], reference)]
            pair = {'problem_id': r['problem_id'], 'condition': r['condition'], 'reference': reference,
                'both_valid': r['status'] == ref['status'] == 'valid',
                'object_fraction': r['counts']['objects'] / ref['counts']['objects'],
                'fact_fraction': r['counts']['facts'] / ref['counts']['facts'],
                'wall_ratio': r['planner']['wall_seconds'] / ref['planner']['wall_seconds']}
            if pair['both_valid']:
                pair['length_difference'] = r['plan_length'] - ref['plan_length']
                pair['length_ratio'] = r['plan_length'] / ref['plan_length']
            pairs.append(pair)
    plan_details = []
    for r in rows:
        if r['status'] != 'valid':
            continue
        case = OUT / 'cases' / r['id']
        plan = read_plan(case / r['plan_file'])
        freq = Counter(a[0] for a in plan)
        details = {'id': r['id'], 'plan_length': len(plan), 'operator_counts': dict(freq),
            'navigation_actions': sum(v for k, v in freq.items() if k in {'gotoroom', 'gotoplace', 'gotolocation'}),
            'pickup_actions': sum(v for k, v in freq.items() if k.startswith('pickupitem')),
            'put_actions': sum(v for k, v in freq.items() if k.startswith('putitem')),
            'put_bindings': [a for a in plan if a[0].startswith('putitem')]}
        plan_details.append(details)
    witness_disagreements = []
    for e in verification['cases_evidence']:
        for label in ['full', 'problem']:
            for w in e.get(label, {}).get('terminal_goal_witnesses', []):
                if w['symbolic_truth'] != w['instance_truth']:
                    witness_disagreements.append({'id': e['id'], 'state': label, **w})
    budget_comparisons = []
    for n in range(40, 46):
        for method in ['lexical', 'nearest']:
            a, b = [keyed[('taskographyv4tiny5', n, f'{method}_b{i}')] for i in [0, 1]]
            budget_comparisons.append({'problem_id': n, 'method': method,
                'both_valid': a['status'] == b['status'] == 'valid',
                'b0_length': a.get('plan_length'), 'b1_length': b.get('plan_length')})
    prior = Path('/prior/observation/results.json')
    prior_rows = json.loads(prior.read_text()) if prior.exists() else []
    result = {'interpretation_scope': 'Descriptive fixed eight-problem symbolic slice; one deterministic satisficing planner; no optimum, physical success, population or latency significance claim.',
        'groups': summaries, 'pairs': pairs, 'plan_details': plan_details, 'budget_comparisons': budget_comparisons,
        'terminal_goal_witness_disagreements': witness_disagreements,
        'total_planning_wall_seconds': sum(r['planner']['wall_seconds'] for r in rows),
        'prior_failed_run': {'completed_case_records': len(prior_rows),
            'statuses': dict(Counter(r['status'] for r in prior_rows)),
            'recorded_planner_wall_seconds': sum(r['planner']['wall_seconds'] for r in prior_rows),
            'note': 'Unsupported global seed option before search; stopped. Any interrupted final attempt lacks result row; retained log is authoritative.'}}
    (OUT / 'analysis.json').write_text(json.dumps(result, indent=2) + '\n')
    cols = ['role', 'condition', 'attempts', 'valid', 'plan_length_mean', 'planning_wall_mean', 'retained_objects_mean', 'retained_facts_mean']
    with (OUT / 'summary.csv').open('w') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader(); w.writerows(summaries)
    compact = {'groups': summaries, 'total_planning_wall_seconds': result['total_planning_wall_seconds'],
               'terminal_goal_witness_disagreements': len(witness_disagreements),
               'prior_failed_run': result['prior_failed_run'],
               'verification': {k: v for k, v in verification.items() if k not in {'cases_evidence', 'negative_controls'}},
               'boundary': result['interpretation_scope']}
    (OUT / 'summary.json').write_text(json.dumps(compact, indent=2) + '\n')
    shutil.copyfile('/study/analyze.py', OUT / 'code/analyze.py')
    hashes = []
    for p in sorted(OUT.rglob('*')):
        if p.is_file() and p.name != 'output_manifest.json':
            hashes.append({'path': str(p.relative_to(OUT)), 'bytes': p.stat().st_size,
                           'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
    (OUT / 'output_manifest.json').write_text(json.dumps({'files': hashes}, indent=2) + '\n')
    print(json.dumps(compact, indent=2), flush=True)


if __name__ == '__main__':
    main()
