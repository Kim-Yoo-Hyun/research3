"""Post-observation analytic finite-population diagnosis; CPU Docker only."""
import hashlib
import json
import math
import shutil
from fractions import Fraction as F
from pathlib import Path

root=Path('/output')
cfg=json.loads((root/'source/protocol.json').read_text())
data=json.loads((root/'normalized.json').read_text())['data']
gaps=[json.loads(x) for x in (root/'gaps.jsonl').read_text().splitlines()]

def mean(xs): return sum(xs)/len(xs)

def variance_of_sample_mean(xs,n):
    mu=mean(xs)
    s2=sum((x-mu)**2 for x in xs)/(len(xs)-1)
    return s2*(F(1,n)-F(1,len(xs)))

def cell(p,t,m):
    d=data[p][t]
    return [F(x) for x in d['success']] if m=='success' else [F(x,d['n_questions']) for x in d['progress_steps']]

variance_rows=[]
exact=[]
checks=0
for metric in cfg['metrics']:
    for n in cfg['n_per_cell']:
        uniform=F(0); stratified=F(0); mix=F(0); within=F(0)
        for policy in cfg['policies']:
            cells=[cell(policy,t,metric) for t in cfg['tasks']]
            flat=sum(cells,[])
            oracle=[mean(xs) for xs in cells for _ in xs]
            residual=[x-y for x,y in zip(flat,oracle)]
            uniform+=variance_of_sample_mean(flat,5*n)
            stratified+=sum(variance_of_sample_mean(xs,n) for xs in cells)/25
            mix+=variance_of_sample_mean(oracle,5*n)
            within+=variance_of_sample_mean(residual,5*n)
            assert sum(residual)==0
            assert sum((x-mean(oracle))*y for x,y in zip(oracle,residual))==0
            checks+=2
        assert uniform==mix+within
        checks+=1
        for method,var in [('uniform',uniform),('stratified',stratified)]:
            errors=[r['error'] for r in gaps if (r['metric'],r['n'],r['method'])==(metric,n,method)]
            variance_rows.append({'metric':metric,'n':n,'method':method,
                                  'expected_gap_sd_pp':100*math.sqrt(var),
                                  'empirical_gap_rmse_pp':100*math.sqrt(sum(e*e for e in errors)/len(errors)),
                                  'variance_exact':str(var),
                                  'uniform_mix_variance_fraction':float(mix/uniform) if uniform else None})

def hypergeom(N,K,n):
    denom=math.comb(N,n)
    return {k:F(math.comb(K,k)*math.comb(N-K,n-k),denom)
            for k in range(max(0,n-(N-K)),min(K,n)+1)}

for task in cfg['tasks']:
    successes=[sum(data[p][task]['success']) for p in cfg['policies']]
    for n in cfg['n_per_cell']:
        pmfs=[hypergeom(50,K,n) for K in successes]
        for K,pmf in zip(successes,pmfs):
            assert sum(pmf.values())==1
            assert sum(k*prob for k,prob in pmf.items())/n==F(K,50)
            xs=[F(1)]*K+[F(0)]*(50-K)
            assert sum((F(k,n)-F(K,50))**2*prob for k,prob in pmf.items())==variance_of_sample_mean(xs,n)
            checks+=3
        probs={s:F(0) for s in ['correct','reversed','predicted_tie','reference_tie']}
        ref=successes[1]-successes[0]
        for a,pa in pmfs[0].items():
            for b,pb in pmfs[1].items():
                status='reference_tie' if ref==0 else 'predicted_tie' if b==a else 'correct' if (b-a)*ref>0 else 'reversed'
                probs[status]+=pa*pb
        assert sum(probs.values())==1
        checks+=1
        observed={s:0 for s in probs}
        ti=cfg['tasks'].index(task)
        for row in gaps:
            if (row['n'],row['method'],row['metric'])==(n,'stratified','success'):
                observed[row['task_status'][ti]]+=1
        exact.append({'task':task,'n':n,'success_counts_in_policy_order':successes,
                      'reference_gap_pp':2*ref, 'probabilities':{k:float(v) for k,v in probs.items()},
                      'exact_probabilities':{k:str(v) for k,v in probs.items()},'observed_counts_out_of_200':observed})
result={'purpose':'post-observation finite-population diagnosis; no population CI or extra rollouts',
        'variance_rows':variance_rows,'binary_stratified_exact_ordering':exact,'analytic_identity_checks':checks,
        'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(root/'diagnostics.json').write_text(json.dumps(result,indent=2)+'\n')
shutil.copy2(__file__,root/'source/analyze.py')
for row in variance_rows:
    if row['n'] in [5,25]: print(json.dumps(row))
for row in exact:
    if row['n']==25 and row['task'] in ['BikeRotorInstall','CleanLitterBox']: print(json.dumps(row))
print('Analytic identity checks:',checks)
