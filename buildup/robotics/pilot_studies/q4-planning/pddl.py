"""Small, strict typed STRIPS reader/writer for this Taskography slice; Docker only."""
import re
from pathlib import Path


def parse(text):
    tokens = re.findall(r'\(|\)|[^\s()]+', re.sub(r';[^\n]*', '', text).lower())
    stack, roots = [], []
    for t in tokens:
        if t == '(':
            node = []
            (stack[-1] if stack else roots).append(node)
            stack.append(node)
        elif t == ')':
            if not stack:
                raise ValueError('unbalanced PDDL')
            stack.pop()
        else:
            if not stack:
                raise ValueError('token outside expression')
            stack[-1].append(t)
    if stack or len(roots) != 1:
        raise ValueError('unbalanced or multiple roots')
    return roots[0]


def typed(tokens):
    out, pending, i = {}, [], 0
    while i < len(tokens):
        t = tokens[i]
        if t == '-':
            for name in pending:
                if name in out:
                    raise ValueError('duplicate object')
                out[name] = tokens[i + 1]
            pending, i = [], i + 2
        else:
            pending.append(t)
            i += 1
    out.update({x: 'object' for x in pending})
    return out


def problem(path):
    root = parse(Path(path).read_text())
    sections = {s[0]: s[1:] for s in root[1:]}
    goal = sections[':goal'][0]
    assert goal[0] == 'and'
    return {'name': sections['problem'][0], 'domain': sections[':domain'][0],
            'objects': typed(sections[':objects']),
            'init': sorted(set(tuple(f) for f in sections[':init'])),
            'goal': sorted(set(tuple(f) for f in goal[1:]))}


def dump(p):
    lines = [f"(define (problem {p['name']})", f" (:domain {p['domain']})", ' (:objects']
    for name, typ in sorted(p['objects'].items()):
        lines.append(f'  {name} - {typ}')
    lines += [' )', ' (:init']
    lines += ['  (' + ' '.join(f) + ')' for f in sorted(p['init'])]
    lines += [' )', ' (:goal (and']
    lines += ['  (' + ' '.join(f) + ')' for f in sorted(p['goal'])]
    lines += [' ))', ')']
    return '\n'.join(lines) + '\n'


def actions(path):
    out = {}
    for s in parse(Path(path).read_text())[1:]:
        if s[0] != ':action':
            continue
        d = dict(zip(s[2::2], s[3::2]))
        out[s[1]] = {'parameters': list(typed(d[':parameters'])),
                     'precondition': d[':precondition'], 'effect': d[':effect']}
    return out


def read_plan(path):
    lines = []
    for line in Path(path).read_text().splitlines():
        if line.strip().startswith(';') or not line.strip():
            continue
        m = re.search(r'\(([^()]*)\)', line)
        if not m:
            raise ValueError('invalid plan line: ' + line)
        lines.append(tuple(m.group(1).lower().split()))
    return lines
