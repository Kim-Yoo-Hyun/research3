"""Q4 bounded observation. Execute only in the study Docker image."""
import argparse
from collections import defaultdict, deque
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
from pddl import problem, dump, read_plan


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')


def mapping(facts, pred):
    return {f[1]: f[2] for f in facts if f[0] == pred}


def distances(p, start=None):
    """Shortest number of navigation actions, not Euclidean distance."""
    fs = p['init']
    loc_place = mapping(fs, 'locationinplace')
    place_room = mapping(fs, 'placeinroom')
    center = {v: k for k, v in mapping(fs, 'placelocation').items()}
    room_center = {r: center[pl] for pl, r in mapping(fs, 'roomplace').items()}
    adjacency = defaultdict(set)
    by_place, by_room = defaultdict(list), defaultdict(list)
    for loc, pl in loc_place.items():
        by_place[pl].append(loc)
    for pl, room in place_room.items():
        by_room[room].append(center[pl])
    for group in list(by_place.values()) + list(by_room.values()):
        for a in group:
            adjacency[a].update(x for x in group if x != a)
    for f in fs:
        if f[0] == 'roomsconnected':
            adjacency[room_center[f[1]]].add(room_center[f[2]])
    starts = [f[2] for f in fs if f[0] == 'atlocation']
    assert len(starts) == 1
    if start is not None:
        starts = [start]
    dist = {starts[0]: 0}
    q = deque(starts)
    while q:
        a = q.popleft()
        for b in sorted(adjacency[a]):
            if b not in dist:
                dist[b] = dist[a] + 1
                q.append(b)
    return dist


def select(p, method, budget):
    fs = p['init']
    targets = defaultdict(set)
    for pred, ic, rc in p['goal']:
        assert pred == 'classrelation'
        targets[ic].add(rc)
    item_classes = mapping(fs, 'itemclass')
    rec_classes = mapping(fs, 'receptacleclass')
    locations = mapping(fs, 'itematlocation') | mapping(fs, 'receptacleatlocation')
    dist = distances(p) if method == 'nearest' else {}
    rank = lambda obj: (dist.get(locations.get(obj), 10**9), obj) if method == 'nearest' else (obj,)
    selected, quotas, ranked = set(), {}, {}
    for typ, classes, requested in [
        ('item', item_classes, {ic: len(rcs) + budget for ic, rcs in targets.items()}),
        ('receptacle', rec_classes, {rc: 1 + budget for rcs in targets.values() for rc in rcs})]:
        for cls, quota in sorted(requested.items()):
            candidates = sorted((obj for obj, c in classes.items() if c == cls), key=rank)
            selected.update(candidates[:quota])
            key = typ + ':' + cls
            quotas[key] = {'requested': quota, 'available': len(candidates), 'selected': candidates[:quota]}
            ranked[key] = [{'object': obj, 'distance': dist.get(locations.get(obj)) if method == 'nearest' else None} for obj in candidates]
    q, keep = closure(p, selected)
    return q, {'method': method, 'budget': budget, 'quota': quotas, 'ranked_candidates': ranked,
               'selected_before_closure': sorted(selected), 'retained_objects': sorted(keep),
               'added_by_closure': sorted(keep - selected)}


def closure(p, selected):
    """Common ancestor closure, unchanged from the original b0/b1 observation."""
    fs = p['init']
    # Deliberately preserve all class symbols and their original classrelation values.
    keep = selected | {o for o, t in p['objects'].items() if t in {'agent', 'room', 'rclass', 'iclass'}}
    parents = {'inreceptacle', 'itematlocation', 'receptacleatlocation', 'locationinplace', 'placeinroom', 'itemclass', 'receptacleclass'}
    for f in fs:
        if f[0] in {'inroom', 'inplace', 'atlocation', 'holds'}:
            keep.update(f[1:])
        if f[0] == 'roomplace':
            keep.add(f[1])
    changed = True
    while changed:
        old = len(keep)
        for f in fs:
            if f[0] in parents and f[1] in keep:
                keep.add(f[2])
            if f[0] == 'placelocation' and f[2] in keep:
                keep.add(f[1])
        changed = len(keep) != old
    q = dict(p, objects={o: t for o, t in p['objects'].items() if o in keep},
             init=[f for f in fs if set(f[1:]) <= keep])
    return q, keep


def state_counts(p):
    d = defaultdict(int)
    for t in p['objects'].values():
        d[t] += 1
    return {'objects': len(p['objects']), 'facts': len(p['init']), 'by_type': dict(sorted(d.items()))}


def prepare(data, output):
    output.mkdir(parents=True, exist_ok=False)
    cases = []
    for tag, ids in [('taskographyv2tiny1', range(40, 42)), ('taskographyv4tiny5', range(40, 46))]:
        for n in ids:
            original = data / 'pddlgym/pddl' / (tag + '_test') / f'problem{n}.pddl'
            scrubpath = data / 'pddlgym/pddl' / (tag + 'scrub_test') / f'problem{n}.pddl'
            full = problem(original)
            domain = data / 'pddlgym/pddl' / f'{tag}.pddl'
            variants = [('full', None, None), ('scrub', None, None)]
            if tag == 'taskographyv4tiny5':
                variants += [(f'{m}_b{b}', m, b) for m in ['lexical', 'nearest'] for b in [0, 1]]
            for name, method, b in variants:
                start = time.perf_counter()
                if method:
                    p, selection = select(full, method, b)
                else:
                    p = full if name == 'full' else problem(scrubpath)
                    p = dict(p, name=full['name'], domain=full['domain'])
                    selection = {'method': name, 'retained_objects': sorted(p['objects'])}
                assert set(p['objects']) <= set(full['objects'])
                assert set(p['init']) <= set(full['init'])
                assert p['goal'] == full['goal']
                assert all(set(f[1:]) <= set(p['objects']) for f in p['init'] + p['goal'])
                text = dump(p)
                # Lossless JSON representation and reverse order control, same canonical PDDL.
                equivalent = json.loads(json.dumps(p))
                equivalent['init'].reverse()
                equivalent['objects'] = dict(reversed(list(equivalent['objects'].items())))
                assert dump(equivalent) == text
                caseid = f'{tag}_{n}_{name}'
                dest = output / 'cases' / caseid
                dest.mkdir(parents=True)
                (dest / 'problem.pddl').write_text(text)
                (dest / 'roundtrip.pddl').write_text(dump(equivalent))
                shutil.copyfile(original, dest / 'full.pddl')
                shutil.copyfile(domain, dest / 'domain.pddl')
                write_json(dest / 'selection.json', selection)
                record = {'id': caseid, 'domain': tag, 'problem_id': n, 'condition': name,
                          'role': 'primary' if tag.endswith('5') else 'sanity',
                          'counts': state_counts(p), 'full_counts': state_counts(full),
                          'preprocess_seconds': time.perf_counter() - start,
                          'input_sha256': sha(original), 'domain_sha256': sha(domain),
                          'problem_sha256': sha(dest / 'problem.pddl'),
                          'roundtrip_sha256': sha(dest / 'roundtrip.pddl'),
                          'source_scrub_sha256': sha(scrubpath) if name == 'scrub' else None}
                cases.append(record)
    write_json(output / 'cases.json', cases)
    shutil.copytree('/opt/environment', output / 'environment')
    code = output / 'code'
    code.mkdir()
    for p in Path('/study').iterdir():
        if p.suffix in {'.py', '.json', '.sh'} or p.name in {'Dockerfile', 'README.md'}:
            shutil.copyfile(p, code / p.name)
    write_json(output / 'protocol.json', {'planning_wall_seconds': 60, 'container_memory_bytes': 4 * 1024**3,
        'fd_memory_limit': '3900M', 'cpus': 1, 'seed': 0, 'alias': 'lama-first',
        'primary_cases': 36, 'sanity_cases': 4,
        'closure': 'all agents/rooms/class symbols; all room centers; selected instances and containment/location ancestors; centers of retained places',
        'roundtrip': 'lossless JSON with reversed fact/object order to same canonical PDDL',
        'mode': 'exploratory', 'device': 'cpu'})
    print(f'PREPARED {len(cases)} cases', flush=True)


def process(command, cwd, log, limit):
    start = time.monotonic()
    timedout = False
    with open(log, 'w') as f:
        p = subprocess.Popen(command, cwd=cwd, stdout=f, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            rc = p.wait(timeout=limit)
        except subprocess.TimeoutExpired:
            timedout = True
            os.killpg(p.pid, signal.SIGKILL)
            rc = p.wait()
    return {'returncode': rc, 'timeout': timedout, 'wall_seconds': time.monotonic() - start, 'command': command}


def run(output):
    sys.path.insert(0, '/opt/downward')
    from driver.aliases import ALIASES
    alias_options = [x.replace(' ', '').replace('\n', '') for x in ALIASES['lama-first']]
    alias_options = [x.replace('reopen_closed=false', 'reopen_closed=false,random_seed=0') for x in alias_options]
    write_json(output / 'planner_options.json', {'alias': 'lama-first', 'expanded': alias_options, 'random_seed': 0})
    records = []
    for case in json.loads((output / 'cases.json').read_text()):
        dest = output / 'cases' / case['id']
        assert not (dest / 'result.json').exists(), 'Refuse to overwrite run'
        command = ['python', '/opt/downward/fast-downward.py', '--overall-memory-limit', '3900M', '--plan-file', str(dest / 'plan'),
                   str(dest / 'domain.pddl'), str(dest / 'problem.pddl')] + alias_options
        result = dict(case, planner=process(command, dest, dest / 'planner.log', 60))
        planfiles = [f for f in dest.glob('plan*') if f.name == 'plan' or f.name[5:].isdigit()]
        if planfiles:
            plan = sorted(planfiles, key=lambda p: int(p.name.split('.')[-1]) if '.' in p.name else 0)[-1]
            result['plan_file'] = plan.name
            result['plan_length'] = len(read_plan(plan))
            for which in ['problem', 'full']:
                log = dest / ('val_' + which + '.log')
                val = process(['validate', '-v', str(dest / 'domain.pddl'), str(dest / (which + '.pddl')), str(plan)], dest, log, 20)
                val['valid'] = not val['timeout'] and 'Plan valid' in log.read_text()
                result['val_' + which] = val
            result['status'] = 'valid' if result['val_problem']['valid'] and result['val_full']['valid'] else 'invalid'
        elif result['planner']['timeout']:
            result['status'] = 'timeout'
        else:
            rc = result['planner']['returncode']
            result['status'] = {10: 'unsolvable', 11: 'search_incomplete', 20: 'memory_limit', 21: 'time_limit', 22: 'memory_and_time_limit'}.get(rc, 'planner_error')
        write_json(dest / 'result.json', result)
        records.append(result)
        write_json(output / 'results.json', records)
        print(case['id'], result['status'], result.get('plan_length'), round(result['planner']['wall_seconds'], 3), flush=True)
        if result['status'] == 'planner_error':
            raise RuntimeError('Planner infrastructure failure; preserve case and stop before remaining cases')
    write_json(output / 'run_complete.json', {'cases': len(records), 'statuses': {s: sum(r['status'] == s for r in records) for s in sorted({r['status'] for r in records})}})


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['prepare', 'run'])
    ap.add_argument('--data', type=Path, default=Path('/data'))
    ap.add_argument('--output', type=Path, default=Path('/output'))
    args = ap.parse_args()
    if args.mode == 'prepare':
        prepare(args.data, args.output / 'observation')
    else:
        run(args.output / 'observation')
