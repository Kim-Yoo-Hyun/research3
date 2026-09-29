"""Independent source/Fraction reconstruction. No imports from the study runner."""
import ast
import csv
import hashlib
import json
import math
import struct
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

import pandas as pd

OUT, INPUT = Path('/output'), Path('/input')
cfg = json.loads((OUT/'source/protocol.json').read_text())
norm = json.loads((OUT/'normalized.json').read_text())
checks = 0


def check(condition, message):
    global checks
    checks += 1
    if not condition:
        raise AssertionError(message)


def close(a, b, label='number'):
    if b is None:
        check(a is None, label)
    else:
        check(a is not None and math.isclose(float(a), float(b), rel_tol=1e-10, abs_tol=1e-11), (label, a, b))


def mean(xs):
    return sum(xs)/len(xs) if xs else None


def quant(xs, q):
    a = sorted(xs)
    at = (len(a)-1)*q
    i = int(at)
    return a[i]*(1-(at-i)) + a[min(i+1,len(a)-1)]*(at-i)


def state(value, ref):
    if value is None:
        return 'missing'
    if ref == 0:
        return 'reference_tie'
    if value == 0:
        return 'predicted_tie'
    return 'correct' if value*ref > 0 else 'reversed'


def npy(path):
    data = path.read_bytes()
    check(data[:8] == b'\x93NUMPY\x01\x00', path)
    size = int.from_bytes(data[8:10], 'little')
    header = ast.literal_eval(data[10:10+size].decode('latin1'))
    check(header == {'descr':'<f8','fortran_order':False,'shape':(50,2)}, path)
    check(len(data) == 10+size+800, path)
    numbers = struct.unpack('<100d', data[10+size:])
    return [numbers[c::2] for c in range(2)]


for file in cfg['input_files']:
    b = (INPUT/file['path']).read_bytes()
    check(len(b) == file['bytes'] and hashlib.sha256(b).hexdigest() == file['sha256'], file['path'])
df = pd.read_pickle(INPUT/'nscore/data/LBM/lbm_data.pkl')[cfg['key']]
check(len(df) == 10, 'source row count')
values = {}
for metric in cfg['metrics']:
    values[metric] = {p: [] for p in cfg['policies']}
    for task in cfg['tasks']:
        # Both release directories contain progress, as established by the saved diagnosis.
        exports = [npy(INPUT/f'nscore/data/{folder}/Part2/{task}.npy') for folder in ['LBM','PC_LBM']] if metric == 'progress' else []
        for policy in cfg['policies']:
            rows = df[(df.policy_type == policy) & (df.skill == task)]
            check(len(rows) == 1, (policy,task))
            row = rows.iloc[0]
            original = row['success' if metric == 'success' else 'task_progress']
            check(len(original) == row['num_rollouts'] == 50, 'source count')
            k = 1 if metric == 'success' else int(row['n_questions'])
            rational = [F(round(float(x)*k), k) for x in original]
            for x,y in zip(original, rational): close(x,y,'source grid')
            for cols in exports:
                check(any(all(abs(x-float(y)) < 1e-12 for x,y in zip(col,rational)) for col in cols), 'NPY source column')
            if metric == 'success': check(all(x in (False, True) for x in original), 'binary source labels')
            cell = norm['data'][policy][task]
            check(cell['num_rollouts'] == 50 and cell['n_questions'] == int(row['n_questions']), 'normalized metadata')
            for x,y in zip(cell[metric], rational): close(x,y,'normalized outcome')
            if metric == 'progress':
                check(cell['progress_steps'] == [int(x*k) for x in rational], 'normalized progress steps')
            values[metric][policy].extend(rational)

refs = {}
saved_ref = json.loads((OUT/'reference.json').read_text())
for metric in cfg['metrics']:
    r = {p: [mean(values[metric][p][i*50:(i+1)*50]) for i in range(5)] for p in cfg['policies']}
    refs[metric] = r
    for p in cfg['policies']:
        for a,b in zip(saved_ref[metric]['task_means'][p],r[p]): close(a,b,'task reference')
        close(saved_ref[metric]['global_means'][p],mean(r[p]),'global reference')
    gs = [b-a for a,b in zip(r[cfg['policies'][0]],r[cfg['policies'][1]])]
    for a,b in zip(saved_ref[metric]['task_gaps'],gs): close(a,b,'task gap reference')
    close(saved_ref[metric]['global_gap'],mean(gs),'global gap reference')

def jsonl(name):
    return [json.loads(line) for line in (OUT/f'{name}.jsonl').read_text().splitlines()]

subsets, scores, gaps = jsonl('subsets'), jsonl('scores'), jsonl('gaps')
check((len(subsets),len(scores),len(gaps)) == (1600,6400,3200), 'counts')
sub = {(r['method'],r['seed'],r['n']):r['indices'] for r in subsets}
check(len(sub) == 1600, 'unique sampling keys')
reconstructed = {}
for row in scores:
    method,seed,n,metric,p = [row[k] for k in ['method','seed','n','metric','policy']]
    ids = sub[method,seed,n][p]
    check(len(ids) == len(set(ids)) == 5*n and all(0 <= i < 250 for i in ids), 'indices')
    counts = [sum(i//50 == t for i in ids) for t in range(5)]
    check(counts == row['task_counts'], 'task counts')
    if method == 'stratified': check(counts == [n]*5, 'allocation')
    series = values[metric][p]
    taskref = refs[metric][p]
    estimate = sum(series[i] for i in ids)/len(ids)
    oracle = sum(taskref[i//50] for i in ids)/len(ids)
    globalref = mean(taskref)
    taskest = [mean([series[i] for i in ids if i//50 == t]) for t in range(5)]
    taskerr = [None if a is None else a-b for a,b in zip(taskest,taskref)]
    for field,expected in [('estimate',estimate),('reference',globalref),('error',estimate-globalref),
                           ('oracle_estimate',oracle),('mix_error',oracle-globalref),('within_error',estimate-oracle)]:
        close(row[field],expected,field)
    for field,xs in [('task_estimates',taskest),('task_errors',taskerr)]:
        for a,b in zip(row[field],xs): close(a,b,field)
    abs_errors = [abs(x) for x in taskerr if x is not None]
    check(row['observed_tasks'] == len(abs_errors), 'coverage')
    close(row['partial_profile_mae'],mean(abs_errors))
    close(row['full_profile_mae'],mean(abs_errors) if len(abs_errors)==5 else None)
    close(row['full_profile_max_error'],max(abs_errors) if len(abs_errors)==5 else None)
    check(estimate-globalref == (oracle-globalref)+(estimate-oracle), 'exact decomposition')
    if method == 'stratified': check(oracle == globalref, 'stratified oracle identity')
    if n == 50: check(estimate == globalref and all(x==0 for x in taskerr), 'full budget')
    reconstructed[method,seed,n,metric,p] = (estimate,oracle,taskest)
check(len(reconstructed) == len(scores), 'unique scores')
# Nested prefixes are a design property, independently checked without relying on RNG replay.
for method in cfg['methods']:
    for seed in cfg['seeds']:
        for p in cfg['policies']:
            previous = set()
            for n in cfg['n_per_cell']:
                current = set(sub[method,seed,n][p]); check(previous <= current, 'nested budgets'); previous=current

for row in gaps:
    method,seed,n,metric = [row[k] for k in ['method','seed','n','metric']]
    p0,p1 = cfg['policies']
    a,b = [reconstructed[method,seed,n,metric,p] for p in cfg['policies']]
    taskref = [y-x for x,y in zip(refs[metric][p0],refs[metric][p1])]
    ref,est = mean(taskref),b[0]-a[0]
    te = [None if x is None or y is None else y-x for x,y in zip(a[2],b[2])]
    errors = [None if x is None else x-y for x,y in zip(te,taskref)]
    for field,expected in [('reference',ref),('estimate',est),('error',est-ref),
                           ('mix_error',b[1]-a[1]-ref),('within_error',(b[0]-a[0])-(b[1]-a[1]))]:
        close(row[field],expected,field)
    check(row['status'] == state(est,ref),'gap sign')
    for field,xs in [('task_estimates',te),('task_errors',errors)]:
        for x,y in zip(row[field],xs): close(x,y,field)
    check(row['task_status'] == [state(x,y) for x,y in zip(te,taskref)], 'task signs')
    ae = [abs(x) for x in errors if x is not None]
    check(row['observed_tasks'] == len(ae),'gap coverage')
    close(row['partial_profile_mae'],mean(ae))
    close(row['full_profile_mae'],mean(ae) if len(ae)==5 else None)
    close(row['full_profile_max_error'],max(ae) if len(ae)==5 else None)

summary = json.loads((OUT/'summary.json').read_text())
check(len(summary)==16,'summary rows')
for row in summary:
    def belongs(r): return all(r[k]==row[k] for k in ['n','method','metric'])
    ss,gg = [r for r in scores if belongs(r)], [r for r in gaps if belongs(r)]
    fs,fg = [r for r in ss if r['observed_tasks']==5], [r for r in gg if r['observed_tasks']==5]
    for key,v in [('draws',len(gg)),('policy_draws',len(ss)),('complete_policy_draws',len(fs)),
                  ('complete_gap_draws',len(fg)),('record_budget',row['n']*10),
                  ('missing_task_policy_pairs',sum(5-r['observed_tasks'] for r in ss))]: close(row[key],v,key)
    for key,records,field,absolute in [
        ('global_mae_pp',ss,'error',True),('gap_mae_pp',gg,'error',True),
        ('task_mean_mae_pp',fs,'full_profile_mae',False),('task_gap_mae_pp',fg,'full_profile_mae',False),
        ('max_task_gap_error_mean_pp',fg,'full_profile_max_error',False),
        ('gap_mix_mae_pp',gg,'mix_error',True),('gap_within_mae_pp',gg,'within_error',True)]:
        close(row[key],100*mean([abs(r[field]) if absolute else r[field] for r in records]),key)
    close(row['global_gap_abs_error_p95_pp'],100*quant([abs(r['error']) for r in gg],.95))
    close(row['max_task_gap_error_p95_pp'],100*quant([r['full_profile_max_error'] for r in fg],.95))
    states = Counter(r['status'] for r in gg)
    for s in ['correct','reversed','predicted_tie','reference_tie']: close(row[f'global_{s}'],states[s],s)
tasks = json.loads((OUT/'task_summary.json').read_text())
check(len(tasks)==80,'task summary count')
for row in tasks:
    i=cfg['tasks'].index(row['task'])
    rows=[r for r in gaps if all(r[k]==row[k] for k in ['n','method','metric'])]
    valid=[r['task_errors'][i] for r in rows if r['task_errors'][i] is not None]
    close(row['gap_mae_pp'],100*mean([abs(x) for x in valid]))
    close(row['gap_error_p05_pp'],100*quant(valid,.05)); close(row['gap_error_p95_pp'],100*quant(valid,.95))
    check(row['observed_draws']==len(valid) and row['draws']==200,'task summary denominator')
    states=Counter(r['task_status'][i] for r in rows)
    for s in ['correct','reversed','predicted_tie','reference_tie','missing']: check(row[s]==states[s],s)
for name, expected in [('summary',summary),('task_summary',tasks)]:
    csv_rows=list(csv.DictReader((OUT/f'{name}.csv').open()))
    check(len(csv_rows)==len(expected),'CSV length')
    for a,b in zip(csv_rows,expected):
        for k,v in b.items():
            if isinstance(v,str): check(a[k]==v,'CSV label')
            else: close(a[k],v,'CSV number')
execution=json.loads((OUT/'execution.json').read_text())
for name,record in execution['artifacts'].items():
    content=(OUT/name).read_bytes()
    check(len(content)==record['bytes'] and hashlib.sha256(content).hexdigest()==record['sha256'],name)
receipt={'status':'passed','checks':checks,'records':500,'subsets':len(subsets),'scores':len(scores),'gaps':len(gaps),
         'scope':'Independent pickle/NPY identities, rational outcome/grid and all score/profile/gap/decomposition calculations, summary/CSV and nesting checks',
         'boundary':'Engineering checks are not independent scientific trials; no population inference',
         'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
Path('/verification/receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
