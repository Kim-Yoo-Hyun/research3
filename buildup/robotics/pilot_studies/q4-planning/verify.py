"""Independent transition replay against original PDDL, cross-checked with VAL. Docker only."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from pddl import problem, actions, read_plan, dump

OUT = Path('/output/observation')


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def grounded(expr, binding):
    return tuple(binding.get(x, x) for x in expr)


def conjuncts(expr):
    return expr[1:] if expr[0] == 'and' else [expr]


def replay(p, operators, plan):
    state = set(p['init'])
    checks = 0
    for step, call in enumerate(plan):
        if call[0] not in operators:
            return False, {'step': step, 'unknown_operator': call[0]}, state, checks
        op = operators[call[0]]
        if len(call) - 1 != len(op['parameters']) or any(o not in p['objects'] for o in call[1:]):
            return False, {'step': step, 'invalid_parameters': call}, state, checks
        binding = dict(zip(op['parameters'], call[1:]))
        unmet = []
        for expr in conjuncts(op['precondition']):
            checks += 1
            if expr[0] == 'not':
                fact = grounded(expr[1], binding)
                if fact in state:
                    unmet.append(['not', list(fact)])
            else:
                fact = grounded(expr, binding)
                if fact not in state:
                    unmet.append(list(fact))
        if unmet:
            return False, {'step': step, 'action': call, 'unmet_preconditions': unmet}, state, checks
        adds, deletes = set(), set()
        for expr in conjuncts(op['effect']):
            if expr[0] == 'not':
                deletes.add(grounded(expr[1], binding))
            else:
                adds.add(grounded(expr, binding))
        state = (state - deletes) | adds
    missing = sorted(set(p['goal']) - state)
    checks += len(p['goal'])
    return not missing, {'missing_goals': missing}, state, checks


def witnesses(p, state, reference=None):
    if not any(g[0] == 'classrelation' for g in p['goal']):
        return []
    # Diagnostic only: SCRUB can drop non-goal class symbols for retained ancestors.
    catalog = set((reference or p)['init'])
    itemcls = {f[1]: f[2] for f in catalog if f[0] == 'itemclass'}
    reccls = {f[1]: f[2] for f in catalog if f[0] == 'receptacleclass'}
    pairs = {}
    for f in state:
        if f[0] == 'inreceptacle':
            key = (itemcls[f[1]], reccls[f[2]])
            pairs.setdefault(key, []).append((f[1], f[2]))
    result = []
    for goal in p['goal']:
        if goal[0] == 'classrelation':
            ws = sorted(pairs.get(goal[1:], []))
            result.append({'goal': goal, 'symbolic_truth': goal in state, 'instance_truth': bool(ws), 'witnesses': ws})
    return result


def verify():
    inputs = json.loads(Path('/study/inputs.json').read_text())
    for f in inputs['files']:
        path = Path('/data') / f['path']
        assert path.stat().st_size == f['bytes'] and digest(path) == f['sha256'], f
    rows = json.loads((OUT / 'results.json').read_text())
    assert len(rows) == 40 and len({r['id'] for r in rows}) == 40
    assert sum(r['role'] == 'primary' for r in rows) == 36
    assert sum(r['role'] == 'sanity' for r in rows) == 4
    checked, cases = 0, []
    for r in rows:
        case = OUT / 'cases' / r['id']
        full, pruned = problem(case / 'full.pddl'), problem(case / 'problem.pddl')
        assert digest(case / 'full.pddl') == r['input_sha256']
        assert digest(case / 'domain.pddl') == r['domain_sha256']
        assert digest(case / 'problem.pddl') == r['problem_sha256'] == r['roundtrip_sha256']
        assert dump(problem(case / 'roundtrip.pddl')) == dump(pruned)
        assert set(pruned['objects']) <= set(full['objects'])
        assert set(pruned['init']) <= set(full['init']) and pruned['goal'] == full['goal']
        assert len(pruned['objects']) == r['counts']['objects'] and len(pruned['init']) == r['counts']['facts']
        classes = {}
        for v in pruned['objects'].values():
            classes[v] = classes.get(v, 0) + 1
        assert classes == r['counts']['by_type']
        evidence = {'id': r['id'], 'status': r['status'], 'initial_full_witnesses': witnesses(full, set(full['init'])),
                    'initial_pruned_witnesses': witnesses(pruned, set(pruned['init']), full)}
        if 'plan_file' in r:
            operators = actions(case / 'domain.pddl')
            plan = read_plan(case / r['plan_file'])
            assert len(plan) == r['plan_length']
            for label, p in [('full', full), ('problem', pruned)]:
                valid, diagnostic, terminal, count = replay(p, operators, plan)
                checked += count
                assert valid == r['val_' + label]['valid'], (r['id'], label, diagnostic)
                assert r['val_' + label]['returncode'] == 0 if valid else True
                evidence[label] = {'valid': valid, 'diagnostic': diagnostic,
                    'terminal_sha256': hashlib.sha256(json.dumps(sorted(terminal)).encode()).hexdigest(),
                    'terminal_goal_witnesses': witnesses(p, terminal, full)}
            assert (r['status'] == 'valid') == (evidence['full']['valid'] and evidence['problem']['valid'])
        else:
            assert r['status'] in {'timeout', 'unsolvable', 'search_incomplete', 'memory_limit', 'time_limit', 'memory_and_time_limit'}, r['status']
        cases.append(evidence)
    # Validate a false precondition and an unmet goal using an actual grounded case.
    reference = next(r for r in rows if r['role'] == 'sanity' and r['status'] == 'valid' and r['plan_length'] > 0)
    case = OUT / 'cases' / reference['id']
    p = problem(case / 'full.pddl')
    original_plan = read_plan(case / reference['plan_file'])
    negatives = {'last_action_only': [original_plan[-1]], 'empty_plan': []}
    negdir = OUT / 'negative_controls'
    negdir.mkdir(exist_ok=True)
    negresults = []
    for label, plan in negatives.items():
        path = negdir / (label + '.plan')
        path.write_text('\n'.join('(' + ' '.join(a) + ')' for a in plan) + '\n')
        valid, diag, _, count = replay(p, actions(case / 'domain.pddl'), plan)
        proc = subprocess.run(['validate', '-v', str(case / 'domain.pddl'), str(case / 'full.pddl'), str(path)], capture_output=True, text=True, timeout=20)
        (negdir / (label + '.log')).write_text(proc.stdout + proc.stderr)
        val_valid = 'Plan valid' in proc.stdout
        assert not valid and not val_valid, (label, diag)
        checked += count
        negresults.append({'control': label, 'replay_valid': valid, 'val_valid': val_valid, 'diagnostic': diag})
    report = {'status': 'PASS', 'source_files_verified': len(inputs['files']), 'cases': len(rows),
              'transition_and_goal_checks': checked, 'cases_evidence': cases, 'negative_controls': negresults,
              'witness_class_catalog': 'Original full-state classes for diagnostic decoding only; not supplied to planner for pruned problems.',
              'boundary': 'Independent transition implementation plus external VAL; shared small PDDL tokenizer, no physical semantics guarantee.'}
    (OUT / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    shutil.copyfile('/study/verify.py', OUT / 'code/verify.py')
    (OUT / 'verification_code.sha256').write_text(digest('/study/verify.py') + '  verify.py\n')
    print('PASS', len(rows), 'cases;', checked, 'transition/goal checks; two rejected controls', flush=True)


if __name__ == '__main__':
    verify()
