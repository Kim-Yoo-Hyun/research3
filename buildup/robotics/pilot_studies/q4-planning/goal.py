"""One pre-specified goal-conditioned b0 follow-up. Execute only in Docker."""
import argparse
from collections import defaultdict, Counter
from functools import lru_cache
from itertools import product, permutations
import json
from pathlib import Path
import shutil
import statistics
import time

from pddl import problem, dump, read_plan, actions
from run import closure, distances, mapping, select, sha, state_counts, write_json, process
from verify import replay, witnesses

OUT = Path('/output/observation')
REF = Path('/reference')
TAG = 'taskographyv4tiny5'


def catalog(p):
    targets = defaultdict(list)
    for pred, ic, rc in sorted(p['goal']):
        assert pred == 'classrelation'
        targets[ic].append(rc)
    items, recs = defaultdict(list), defaultdict(list)
    for obj, cls in sorted(mapping(p['init'], 'itemclass').items()):
        items[cls].append(obj)
    for obj, cls in sorted(mapping(p['init'], 'receptacleclass').items()):
        recs[cls].append(obj)
    return dict(targets), dict(items), dict(recs)


def choose(p):
    targets, items, recs = catalog(p)
    rclasses = sorted({rc for rcs in targets.values() for rc in rcs})
    locations = mapping(p['init'], 'itematlocation') | mapping(p['init'], 'receptacleatlocation')
    start = next(f[2] for f in p['init'] if f[0] == 'atlocation')
    sources = {start} | {locations[i] for ic in targets for i in items[ic]}
    ds = {s: distances(p, s) for s in sorted(sources)}
    assert all(len(items[ic]) >= len(rcs) for ic, rcs in targets.items())

    @lru_cache(None)
    def assignment(ic, dests):
        # Each item is visited once; the bitmask describes assigned goal slots.
        k = len(dests)
        dp = {0: (0, ('',) * k)}
        for obj in items[ic]:
            updated = dict(dp)
            for mask, (cost, bound) in dp.items():
                for j, rec in enumerate(dests):
                    if mask & (1 << j):
                        continue
                    distance = ds[start][locations[obj]] + ds[locations[obj]][locations[rec]]
                    values = list(bound)
                    values[j] = obj
                    candidate = (cost + distance, tuple(values))
                    key = mask | (1 << j)
                    if key not in updated or candidate < updated[key]:
                        updated[key] = candidate
            dp = updated
        return dp[(1 << k) - 1]

    best, count = None, 0
    for rtuple in product(*(recs[rc] for rc in rclasses)):
        rmap = dict(zip(rclasses, rtuple))
        parts = [assignment(ic, tuple(rmap[rc] for rc in rcs)) for ic, rcs in targets.items()]
        candidate = (sum(c for c, _ in parts), rtuple, tuple(i for _, group in parts for i in group))
        if best is None or candidate < best:
            best = candidate
        count += 1
    score, rtuple, ituple = best
    rmap = dict(zip(rclasses, rtuple))
    bindings, cursor = [], 0
    for ic, rcs in targets.items():
        for rc in rcs:
            obj, rec = ituple[cursor], rmap[rc]
            a, b = ds[start][locations[obj]], ds[locations[obj]][locations[rec]]
            bindings.append({'item_class': ic, 'receptacle_class': rc, 'item': obj, 'receptacle': rec,
                             'agent_item_distance': a, 'item_receptacle_distance': b})
            cursor += 1
    selected = set(ituple) | set(rtuple)
    q, keep = closure(p, selected)
    quotas = {'item:' + ic: {'requested': len(rcs), 'available': len(items[ic]),
              'selected': sorted(b['item'] for b in bindings if b['item_class'] == ic)} for ic, rcs in targets.items()}
    quotas.update({'receptacle:' + rc: {'requested': 1, 'available': len(recs[rc]), 'selected': [rmap[rc]]} for rc in rclasses})
    return q, {'method': 'goal', 'budget': 0, 'proxy_score': score, 'bindings': bindings,
               'receptacle_combinations': count, 'assignment_cache': assignment.cache_info()._asdict(),
               'quota': quotas, 'selected_before_closure': sorted(selected), 'retained_objects': sorted(keep),
               'added_by_closure': sorted(keep - selected)}


def verify_manifest(root):
    manifest = json.loads((root / 'output_manifest.json').read_text())
    for f in manifest['files']:
        path = root / f['path']
        assert path.stat().st_size == f['bytes'] and sha(path) == f['sha256'], f['path']
    return len(manifest['files'])


def prepare():
    OUT.mkdir(parents=True, exist_ok=False)
    # No reference plans/results enter choose(). Reference is used only for later audits.
    rows = []
    for n in range(40, 46):
        original = Path('/data/pddlgym/pddl') / (TAG + '_test') / f'problem{n}.pddl'
        domain = Path('/data/pddlgym/pddl') / (TAG + '.pddl')
        full = problem(original)
        start = time.perf_counter()
        q, selection = choose(full)
        select_time = time.perf_counter() - start
        dest = OUT / 'cases' / f'{TAG}_{n}_goal_b0'
        dest.mkdir(parents=True)
        (dest / 'problem.pddl').write_text(dump(q))
        equivalent = json.loads(json.dumps(q))
        equivalent['init'].reverse()
        equivalent['objects'] = dict(reversed(list(equivalent['objects'].items())))
        (dest / 'roundtrip.pddl').write_text(dump(equivalent))
        shutil.copyfile(original, dest / 'full.pddl')
        shutil.copyfile(domain, dest / 'domain.pddl')
        write_json(dest / 'selection.json', selection)
        rows.append({'id': dest.name, 'domain': TAG, 'problem_id': n, 'condition': 'goal_b0', 'role': 'primary',
                     'counts': state_counts(q), 'full_counts': state_counts(full), 'selection_seconds': select_time,
                     'preprocess_seconds': time.perf_counter() - start, 'input_sha256': sha(original),
                     'domain_sha256': sha(domain), 'problem_sha256': sha(dest / 'problem.pddl'),
                     'roundtrip_sha256': sha(dest / 'roundtrip.pddl'), 'source_scrub_sha256': None})
        print('PREPARED', n, 'proxy', selection['proxy_score'], 'combinations', selection['receptacle_combinations'], flush=True)
    write_json(OUT / 'cases.json', rows)
    shutil.copytree('/opt/environment', OUT / 'environment')
    (OUT / 'code').mkdir()
    for path in Path('/study').iterdir():
        if path.is_file():
            shutil.copyfile(path, OUT / 'code' / path.name)
    write_json(OUT / 'protocol.json', {'mode': 'exploratory reuse of six previously observed problems',
        'condition': 'goal_b0', 'quota': 'one receptacle per target class; distinct item per item-class/receptacle-class goal',
        'objective': 'sum d(initial agent,item) + d(item,receptacle); additive proxy, not whole-route plan cost',
        'tie_break': 'lexicographic (receptacle tuple by class, item tuple by sorted goal)',
        'planner': 'unchanged run.py lama-first random_seed=0, 60s wall, 3900M',
        'device': 'cpu', 'cpus': 1, 'memory_gib': 4, 'new_planner_calls': 6,
        'reference_run': '20260918_v2', 'reference_manifest_sha256': sha(REF / 'output_manifest.json'),
        'hypothesis': 'goal-conditioned selection may shorten plans relative to initial-distance-only selection',
        'disconfirmation': 'lower proxy without shorter valid plans limits this proxy; transfers distinguish excluded particular plans from search behavior'})


def independent_distances(p):
    # Alternative computation: Floyd-Warshall on rooms and a closed-form center route.
    fs = p['init']
    lp, pr = mapping(fs, 'locationinplace'), mapping(fs, 'placeinroom')
    pc = {pl: loc for loc, pl in mapping(fs, 'placelocation').items()}
    rc = {r: pl for pl, r in mapping(fs, 'roomplace').items()}
    rooms = sorted(rc)
    rd = {(a, b): (0 if a == b else 10**6) for a in rooms for b in rooms}
    for f in fs:
        if f[0] == 'roomsconnected':
            rd[f[1], f[2]] = 1
    for k in rooms:
        for a in rooms:
            for b in rooms:
                rd[a, b] = min(rd[a, b], rd[a, k] + rd[k, b])
    def distance(a, b):
        ap, bp = lp[a], lp[b]
        ar, br = pr[ap], pr[bp]
        if ap == bp:
            return int(a != b)
        if ar == br:
            return int(a != pc[ap]) + 1 + int(b != pc[bp])
        return int(a != pc[ap]) + int(ap != rc[ar]) + rd[ar, br] + int(bp != rc[br]) + int(b != pc[bp])
    return distance


def exhaustive(p, distance, allowed=None):
    targets, items, recs = catalog(p)
    if allowed is not None:
        items = {c: [x for x in xs if x in allowed] for c, xs in items.items()}
        recs = {c: [x for x in xs if x in allowed] for c, xs in recs.items()}
    loc = mapping(p['init'], 'itematlocation') | mapping(p['init'], 'receptacleatlocation')
    start = next(f[2] for f in p['init'] if f[0] == 'atlocation')
    rclasses = sorted({rc for rcs in targets.values() for rc in rcs})
    checks = 0
    @lru_cache(None)
    def best_assignment(ic, dests):
        nonlocal checks
        options = []
        for its in permutations(items[ic], len(dests)):
            cost = sum(distance(start, loc[i]) + distance(loc[i], loc[r]) for i, r in zip(its, dests))
            options.append((cost, its))
            checks += 1
        return min(options)
    results = []
    for rs in product(*(recs[rc] for rc in rclasses)):
        rm = dict(zip(rclasses, rs))
        parts = [best_assignment(ic, tuple(rm[rc] for rc in rcs)) for ic, rcs in targets.items()]
        results.append((sum(x[0] for x in parts), rs, tuple(i for _, its in parts for i in its)))
    return min(results), checks


def verify():
    preserved = verify_manifest(REF)
    inputs = json.loads(Path('/study/inputs.json').read_text())
    for f in inputs['files']:
        path = Path('/data') / f['path']
        assert path.stat().st_size == f['bytes'] and sha(path) == f['sha256']
    assert json.loads((OUT / 'planner_options.json').read_text()) == json.loads((REF / 'planner_options.json').read_text())
    rows = json.loads((OUT / 'results.json').read_text())
    assert len(rows) == 6 and sorted(r['problem_id'] for r in rows) == list(range(40, 46))
    evidence, transitions, distance_checks, assignment_checks, parity = [], 0, 0, 0, 0
    for r in rows:
        case = OUT / 'cases' / r['id']
        full, pruned = problem(case / 'full.pddl'), problem(case / 'problem.pddl')
        s = json.loads((case / 'selection.json').read_text())
        assert sha(case / 'full.pddl') == r['input_sha256']
        assert sha(case / 'domain.pddl') == r['domain_sha256']
        assert sha(case / 'problem.pddl') == r['problem_sha256'] == sha(case / 'roundtrip.pddl') == r['roundtrip_sha256']
        assert dump(problem(case / 'roundtrip.pddl')) == dump(pruned)
        assert set(pruned['objects']) <= set(full['objects']) and set(pruned['init']) <= set(full['init'])
        assert pruned['goal'] == full['goal'] and state_counts(pruned) == r['counts']
        assert dump(closure(full, set(s['selected_before_closure']))[0]) == dump(pruned)
        for method in ['lexical', 'nearest']:
            for b in [0, 1]:
                old = REF / 'cases' / f'{TAG}_{r["problem_id"]}_{method}_b{b}'
                q, meta = select(full, method, b)
                assert dump(q) == (old / 'problem.pddl').read_text()
                assert meta == json.loads((old / 'selection.json').read_text())
                parity += 1
        old = REF / 'cases' / f'{TAG}_{r["problem_id"]}_nearest_b0'
        oldsel = json.loads((old / 'selection.json').read_text())
        for key, quota in s['quota'].items():
            assert quota['requested'] == oldsel['quota'][key]['requested'] == len(set(quota['selected']))
        assert set(s['quota']) == set(oldsel['quota'])
        formula = independent_distances(full)
        locations = mapping(full['init'], 'itematlocation') | mapping(full['init'], 'receptacleatlocation')
        start = next(f[2] for f in full['init'] if f[0] == 'atlocation')
        for source in sorted({start} | set(locations.values())):
            bfs = distances(full, source)
            for target in sorted(set(locations.values())):
                assert bfs[target] == formula(source, target)
                distance_checks += 1
        best, count = exhaustive(full, formula)
        assignment_checks += count
        binding_recs = {b['receptacle_class']: b['receptacle'] for b in s['bindings']}
        actual = (s['proxy_score'], tuple(binding_recs[c] for c in sorted(binding_recs)), tuple(b['item'] for b in s['bindings']))
        assert actual == best
        assert len(set(b['item'] for b in s['bindings'])) == len(full['goal'])
        oldscore, count = exhaustive(full, formula, set(oldsel['selected_before_closure']))
        assignment_checks += count
        result = {'problem_id': r['problem_id'], 'goal_proxy': best[0], 'nearest_proxy': oldscore[0], 'status': r['status']}
        if 'plan_file' in r:
            plan = read_plan(case / r['plan_file'])
            assert len(plan) == r['plan_length']
            for label, p in [('full', full), ('problem', pruned)]:
                valid, diag, state, checks = replay(p, actions(case / 'domain.pddl'), plan)
                transitions += checks
                assert valid == r['val_' + label]['valid'], diag
                ws = witnesses(p, state, full)
                assert all(w['symbolic_truth'] == w['instance_truth'] for w in ws)
                result[label] = {'valid': valid, 'witnesses': ws}
            assert (r['status'] == 'valid') == (result['full']['valid'] and result['problem']['valid'])
        else:
            assert r['status'] in {'timeout', 'unsolvable', 'search_incomplete', 'memory_limit', 'time_limit', 'memory_and_time_limit'}
        evidence.append(result)
    result = {'status': 'PASS', 'cases': 6, 'prior_files_unchanged': preserved, 'source_hash_checks': len(inputs['files']),
              'old_selection_parity_cases': parity, 'navigation_distance_checks': distance_checks,
              'exhaustive_assignment_checks': assignment_checks, 'transition_goal_checks': transitions, 'evidence': evidence,
              'boundary': 'Independent assignment enumeration and distance formula; separate transition replay plus external VAL. Shared PDDL tokenizer. No physical semantics claim.'}
    write_json(OUT / 'verification.json', result)
    print(json.dumps({k: v for k, v in result.items() if k != 'evidence'}), flush=True)


def transfer(srcroot, source, dstroot, target, label):
    src, dst = srcroot / 'cases' / source['id'], dstroot / 'cases' / target['id']
    p = problem(dst / 'problem.pddl')
    plan = read_plan(src / source['plan_file'])
    valid, diagnostic, _, checks = replay(p, actions(dst / 'domain.pddl'), plan)
    log = OUT / 'diagnostics' / (label + '.log')
    run = process(['validate', '-v', str(dst / 'domain.pddl'), str(dst / 'problem.pddl'), str(src / source['plan_file'])], OUT, log, 20)
    assert not run['timeout'] and valid == ('Plan valid' in log.read_text())
    return {'label': label, 'source': source['condition'], 'target': target['condition'],
            'source_length': source['plan_length'], 'target_length': target.get('plan_length'),
            'valid': valid, 'missing_objects': sorted({v for call in plan for v in call[1:]} - set(p['objects'])),
            'diagnostic': diagnostic, 'transition_checks': checks, 'val_returncode': run['returncode']}


def analyze():
    verify_manifest(REF)
    verification = json.loads((OUT / 'verification.json').read_text())
    assert verification['status'] == 'PASS'
    old = {(r['problem_id'], r['condition']): r for r in json.loads((REF / 'results.json').read_text()) if r['role'] == 'primary'}
    rows = json.loads((OUT / 'results.json').read_text())
    (OUT / 'diagnostics').mkdir(exist_ok=True)
    table, transfers = [], []
    for row, ev in zip(rows, verification['evidence']):
        n = row['problem_id']
        case = OUT / 'cases' / row['id']
        entry = {'problem_id': n, 'status': row['status'], 'goal_b0': row.get('plan_length'),
                 'goal_proxy': ev['goal_proxy'], 'nearest_proxy': ev['nearest_proxy'], 'objects': row['counts']['objects'],
                 'selection_seconds': row['selection_seconds'], 'planning_seconds': row['planner']['wall_seconds']}
        if 'plan_file' in row:
            entry['action_counts'] = dict(Counter(x[0] for x in read_plan(case / row['plan_file'])))
        for cond in ['full', 'scrub', 'lexical_b0', 'nearest_b0']:
            prior = old[n, cond]
            entry[cond] = prior.get('plan_length', prior['status'])
        for cond in ['nearest_b0', 'scrub']:
            prior = old[n, cond]
            if 'plan_file' in row and 'plan_file' in prior:
                transfers.append(transfer(REF, prior, OUT, row, f'{n}_{cond}_to_goal'))
                transfers.append(transfer(OUT, row, REF, prior, f'{n}_goal_to_{cond}'))
        table.append(entry)
    valid = [r for r in rows if r['status'] == 'valid']
    comparisons = {}
    for cond in ['nearest_b0', 'scrub', 'lexical_b0']:
        paired = [(r, old[r['problem_id'], cond]) for r in valid if old[r['problem_id'], cond]['status'] == 'valid']
        comparisons[cond] = {'paired_valid': len(paired), 'shorter': sum(a['plan_length'] < b['plan_length'] for a, b in paired),
                             'equal': sum(a['plan_length'] == b['plan_length'] for a, b in paired),
                             'longer': sum(a['plan_length'] > b['plan_length'] for a, b in paired),
                             'mean_difference': statistics.mean(a['plan_length'] - b['plan_length'] for a, b in paired) if paired else None}
    result = {'mode': 'single exploratory follow-up, reused six problems; no new held-out evidence',
              'attempts': len(rows), 'valid': len(valid), 'mean_plan_length_valid': statistics.mean(r['plan_length'] for r in valid) if valid else None,
              'mean_objects': statistics.mean(r['counts']['objects'] for r in rows),
              'mean_selection_seconds': statistics.mean(r['selection_seconds'] for r in rows),
              'mean_preprocess_seconds': statistics.mean(r['preprocess_seconds'] for r in rows),
              'mean_planning_seconds': statistics.mean(r['planner']['wall_seconds'] for r in rows),
              'comparisons': comparisons, 'table': table, 'transfers': transfers,
              'timing_boundary': 'Descriptive single-pass CPU wall time. Prior baselines reused; not a repeated latency or total system comparison.',
              'interpretation_boundary': 'Proxy optimum is not plan optimum. Rejected plan transfer excludes only that particular plan.'}
    write_json(OUT / 'summary.json', result)
    manifest = [{'path': str(p.relative_to(OUT)), 'bytes': p.stat().st_size, 'sha256': sha(p)}
                for p in sorted(OUT.rglob('*')) if p.is_file() and p.name != 'output_manifest.json']
    write_json(OUT / 'output_manifest.json', {'files': manifest})
    print(json.dumps({k: v for k, v in result.items() if k != 'transfers'}, indent=2), flush=True)
    print('SEALED', len(manifest), 'files', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['prepare', 'verify', 'analyze'])
    args = parser.parse_args()
    {'prepare': prepare, 'verify': verify, 'analyze': analyze}[args.stage]()
