"""Post-hoc checks of observed tradeoffs, without additional planner calls. Docker only."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from pddl import problem, actions, read_plan
from verify import replay

OUT = Path('/output/observation')


def nav_distances(p):
    # Independent closed-form route length through place centers and room graph.
    facts = p['init']
    maps = {}
    for pred in ['locationinplace', 'placeinroom', 'placelocation', 'roomplace', 'itematlocation', 'receptacleatlocation']:
        maps[pred] = {f[1]: f[2] for f in facts if f[0] == pred}
    centers = {pl: loc for loc, pl in maps['placelocation'].items()}
    room_centers = {room: pl for pl, room in maps['roomplace'].items()}
    rooms = sorted(room_centers)
    rd = {(a, b): (0 if a == b else 10**6) for a in rooms for b in rooms}
    for f in facts:
        if f[0] == 'roomsconnected':
            rd[(f[1], f[2])] = 1
    for k in rooms:
        for a in rooms:
            for b in rooms:
                rd[(a, b)] = min(rd[(a, b)], rd[(a, k)] + rd[(k, b)])
    start = next(f[2] for f in facts if f[0] == 'atlocation')
    sp = maps['locationinplace'][start]
    sr = maps['placeinroom'][sp]
    out = {}
    for obj, loc in (maps['itematlocation'] | maps['receptacleatlocation']).items():
        ep = maps['locationinplace'][loc]
        er = maps['placeinroom'][ep]
        if sp == ep:
            value = int(start != loc)
        elif sr == er:
            value = int(start != centers[sp]) + 1 + int(loc != centers[ep])
        else:
            value = int(start != centers[sp]) + int(sp != room_centers[sr]) + rd[(sr, er)] + int(ep != room_centers[er]) + int(loc != centers[ep])
        out[obj] = value if value < 10**6 else None
    return out


def transfer(source, target, label, diagdir):
    src = OUT / 'cases' / source['id']
    dst = OUT / 'cases' / target['id']
    p = problem(dst / 'problem.pddl')
    plan = read_plan(src / source['plan_file'])
    valid, diag, _, count = replay(p, actions(dst / 'domain.pddl'), plan)
    command = ['validate', '-v', str(dst / 'domain.pddl'), str(dst / 'problem.pddl'), str(src / source['plan_file'])]
    proc = subprocess.run(command, capture_output=True, text=True, timeout=20)
    (diagdir / (label + '.log')).write_text(proc.stdout + proc.stderr)
    val_valid = 'Plan valid' in proc.stdout
    assert valid == val_valid, (label, diag)
    mentioned = {v for call in plan for v in call[1:]}
    return {'label': label, 'source': source['id'], 'target': target['id'],
            'source_plan_length': source['plan_length'], 'target_plan_length': target['plan_length'],
            'transferred_plan_valid': valid, 'missing_objects': sorted(mentioned - set(p['objects'])),
            'first_failure': diag if not valid else None, 'transition_checks': count, 'val_returncode': proc.returncode}


def main():
    rows = json.loads((OUT / 'results.json').read_text())
    keyed = {(r['domain'], r['problem_id'], r['condition']): r for r in rows}
    checks = 0
    signatures, initial_signatures = defaultdict(list), defaultdict(list)
    for r in rows:
        case = OUT / 'cases' / r['id']
        full = problem(case / 'full.pddl')
        if r['condition'] == 'full' and r['role'] == 'primary':
            objects = sorted((o, t) for o, t in full['objects'].items() if t in {'room', 'place', 'location', 'receptacle'})
            facts = sorted(f for f in full['init'] if f[0] in {'locationinplace', 'placeinroom', 'placelocation', 'roomplace', 'roomsconnected', 'receptacleatlocation'})
            sig = hashlib.sha256(json.dumps([objects, facts]).encode()).hexdigest()
            signatures[sig].append(r['problem_id'])
            init_sig = hashlib.sha256(json.dumps(full['init']).encode()).hexdigest()
            initial_signatures[init_sig].append(r['problem_id'])
        if r['condition'].startswith('nearest'):
            formula = nav_distances(full)
            selection = json.loads((case / 'selection.json').read_text())
            for candidates in selection['ranked_candidates'].values():
                for c in candidates:
                    assert formula[c['object']] == c['distance'], (r['id'], c, formula[c['object']])
                    checks += 1
    diagdir = OUT / 'diagnostics'
    diagdir.mkdir(exist_ok=True)
    budget_transfers, scrub_transfers, table = [], [], []
    for n in range(40, 46):
        lookup = lambda c: keyed[('taskographyv4tiny5', n, c)]
        table.append({'problem_id': n, **{c: lookup(c).get('plan_length', lookup(c)['status']) for c in ['full', 'scrub', 'lexical_b0', 'lexical_b1', 'nearest_b0', 'nearest_b1']}})
        for method in ['lexical', 'nearest']:
            a, b = lookup(method + '_b0'), lookup(method + '_b1')
            if a['status'] == b['status'] == 'valid' and b['plan_length'] > a['plan_length']:
                budget_transfers.append(transfer(a, b, f'{n}_{method}_b0_to_b1', diagdir))
        a, b = lookup('scrub'), lookup('nearest_b0')
        if a['status'] == b['status'] == 'valid':
            scrub_transfers.append(transfer(a, b, f'{n}_scrub_to_nearest_b0', diagdir))
    result = {'mode': 'post-hoc interpretation; no new planner executions', 'nearest_formula_checks': checks,
              'primary_static_layout_signatures': dict(signatures), 'primary_initial_state_signatures': dict(initial_signatures),
              'length_table': table, 'longer_b1_plan_transfers': budget_transfers, 'scrub_plan_transfers': scrub_transfers,
              'boundary': 'A feasible shorter plan demonstrates search suboptimality, not optimal cost. Rejected transfer shows a particular plan excluded; it does not prove absence of another short plan.'}
    (OUT / 'diagnosis.json').write_text(json.dumps(result, indent=2) + '\n')
    shutil.copyfile('/study/diagnose.py', OUT / 'code/diagnose.py')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
