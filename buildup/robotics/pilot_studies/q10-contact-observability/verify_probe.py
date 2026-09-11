#!/usr/bin/env python3
"""Independent numerical replay, fold/scaler audit and result arithmetic. Docker only."""
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

BASE,ART,RAW=Path('/workspace'),Path('/artifacts'),Path('/raw')
ACTIONS=('pick','insert','remove')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def jl(path):return [json.loads(line) for line in Path(path).read_text().splitlines()]
def close(x,y):assert math.isclose(float(x),float(y),abs_tol=1e-10,rel_tol=1e-9),(x,y)
def write(name,data):
    with (ART/name).open('x') as f:json.dump(data,f,indent=2,allow_nan=False);f.write('\n')
def table(name,rows):
    with (ART/name).open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)


def numeric(model,row):
    x=np.array([row['features'][name] for name in model['names']])
    value=float(np.dot((x-model['mean'])/model['scale'],model['coef'])+model['intercept'])
    return 1/(1+math.exp(-value)) if value>=0 else math.exp(value)/(1+math.exp(value))


def score(rows):
    n=len(rows); positives=sum(r['success'] for r in rows); negatives=n-positives
    tp=sum(r['success'] and r['pred'] for r in rows)
    tn=sum(not r['success'] and not r['pred'] for r in rows)
    ba=.5*(tp/positives+tn/negatives)
    brier=sum((r['p']-r['success'])**2 for r in rows)/n
    loss=-sum(math.log(min(max(r['p'] if r['success'] else 1-r['p'],1e-12),1-1e-12)) for r in rows)/n
    ece=sum(abs(sum(r['p']-r['success'] for r in rows if min(int(r['p']*5),4)==i))/n for i in range(5))
    return {'n':n,'success':positives,'failure':negatives,'tp':tp,'tn':tn,'fp':negatives-tn,'fn':positives-tp,
            'success_recall':tp/positives,'failure_recall':tn/negatives,'balanced_accuracy':ba,
            'brier':brier,'log_loss':loss,'ece_5':ece}


def main():
    protocol=json.loads((BASE/'protocol_v6.json').read_text())
    assert sha(BASE/'protocol_v6.json')=='0fa06e424870090b8fc46f205aaaa0748c3a04ca4aaedcfff5e214903c465dd4'
    execution=json.loads((ART/'execution.json').read_text())
    for record in (protocol,execution):
        for name,digest in record['source_sha256'].items():assert sha(BASE/name)==digest,name
    bundle=json.loads((ART/'training.json').read_text());seal=json.loads((ART/'train_seal.json').read_text())
    assert sha(ART/'training.json')==seal['training_sha256']
    assert sha(ART/'nested.json')==bundle['nested_sha256']
    for name,digest in bundle['raw_sha256'].items():assert sha(RAW/'train'/name)==digest,name
    splits={s:jl(f'/input/{s}_features.jsonl') for s in ('train','test')}
    for s,rows in splits.items():
        assert sha(f'/input/{s}_features.jsonl')==protocol['input_sha256'][f'runs/q10_v5/{s}_features.jsonl']
        assert len(rows)==len({r['id'] for r in rows})==(309 if s=='train' else 104)
        assert all(set(r['features'])==set(protocol['feature_groups']['state_force_duration']) for r in rows)
    train={r['id']:r for r in splits['train']}; test={r['id']:r for r in splits['test']}
    assert {r['recording_id'] for r in train.values()}.isdisjoint(r['recording_id'] for r in test.values())
    models={m['model_id']:m for m in jl(RAW/'train/models.jsonl')}
    assert len(models)==bundle['fit_count']==16488
    scaler_cache={}
    for model in models.values():
        assert model['names']==protocol['feature_groups'][model['group']]
        key=(model['outer'],model['inner'],model['action'],model['group'])
        if key not in scaler_cache:
            fitting=[r for r in train.values() if r['action']==model['action'] and r['recording_id'] not in (model['outer'],model['inner'])]
            x=np.array([[r['features'][n] for n in model['names']] for r in fitting])
            scaler_cache[key]=(fitting,x.mean(axis=0),x.var(axis=0))
        fitting,mean,var=scaler_cache[key]
        assert model['fit_n']==len(fitting)
        assert model['fit_failures']==sum(not r['success'] for r in fitting)
        assert model['fit_groups']==sorted({r['recording_id'] for r in fitting})
        digest=hashlib.sha256('\n'.join(sorted(r['id'] for r in fitting)).encode()).hexdigest()
        assert model['fit_rows_sha256']==digest
        np.testing.assert_allclose(model['mean'],mean,rtol=1e-10,atol=1e-12)
        np.testing.assert_allclose(model['variance'],var,rtol=1e-8,atol=1e-12)
        # StandardScaler's numerical constant bound, independently checked from raw moments.
        eps=np.finfo(float).eps;constant=var <= len(fitting)*eps*var+(len(fitting)*mean*eps)**2
        expected_scale=np.sqrt(var);expected_scale[constant]=1.
        np.testing.assert_allclose(model['scale'],expected_scale,rtol=1e-8,atol=1e-12)
        assert model['iterations']<2000 and all(math.isfinite(v) for v in model['coef'])
    pooled=defaultdict(list)
    inner=jl(RAW/'train/inner.jsonl')
    for row in inner:
        m=models[row['model_id']];source=train[row['id']]
        assert source['recording_id']==row['inner']==m['inner']
        assert source['recording_id'] not in m['fit_groups'] and m['outer']==row['outer']
        assert row['success']==source['success'] and row['action']==source['action']
        close(numeric(m,source),row['p'])
        pooled[(row['outer'],row['group'],row['action'],row['C'])].append(row)
    tuning=jl(RAW/'train/tuning.jsonl');selection={};selection_table=[]
    assert len(tuning)==16*6*3
    for tune in tuning:
        candidates=tune['candidates'];assert len(candidates)==4*21
        for candidate in candidates:
            rows=pooled[(tune['outer'],tune['group'],tune['action'],candidate['C'])]
            expected={r['id'] for r in train.values() if r['action']==tune['action'] and r['recording_id']!=tune['outer']}
            assert len(rows)==len({r['id'] for r in rows}) and {r['id'] for r in rows}==expected
            p=np.array([r['p'] for r in rows]); y=np.array([r['success'] for r in rows]); pred=p>=candidate['threshold']
            close(candidate['ba'],.5*(pred[y].mean()+(~pred[~y]).mean()))
            close(candidate['brier'],np.mean((p-y)**2))
        top=max(c['ba'] for c in candidates); tied=[c for c in candidates if top-c['ba']<=1e-12]
        brier=min(c['brier'] for c in tied); tied=[c for c in tied if c['brier']-brier<=1e-12]
        chosen=min(tied,key=lambda c:(c['C'],abs(c['threshold']-.5),c['threshold']))
        assert chosen==tune['chosen']
        selection[tune['model_id']]=chosen
        m=models[tune['model_id']]
        assert m['inner'] is None and m['C']==chosen['C']
        selection_table.append({'outer':tune['outer'] or 'final','group':tune['group'],'action':tune['action'],
             'C':chosen['C'],'threshold':chosen['threshold'],'inner_ba':chosen['ba'],
             'inner_brier':chosen['brier'],'coefficient_norm':m['coefficient_norm']})
    for group,actions in bundle['models'].items():
        for action,m in actions.items():
            assert m['outer'] is None and m['inner'] is None
            assert m['threshold']==selection[m['model_id']]['threshold']
            assert {k:v for k,v in m.items() if k!='threshold'}==models[m['model_id']]
    baseline_models=json.loads((RAW/'train/baseline_models.json').read_text())
    reports={'train':json.loads((ART/'nested.json').read_text()),'test':json.loads((ART/'test.json').read_text())}
    assert bundle['sealed_at_utc']<=seal['sealed_at_utc']<=reports['test']['started_at_utc']
    metric_table=[];error_table=[];predictions={}
    for split,filename in [('train','nested_predictions.jsonl'),('test','predictions.jsonl')]:
        predictions[split]=jl(RAW/split/filename);lookup=train if split=='train' else test
        rows=predictions[split]
        assert len(rows)==len({(r['method'],r['id']) for r in rows})==len(lookup)*17
        for row in rows:
            source=lookup[row['id']]
            assert row['success']==source['success'] and row['action']==source['action'] and row['recording_id']==source['recording_id']
            if row['method'].startswith('v5_'):
                baseline=baseline_models[row['recording_id']] if split=='train' else bundle['baselines']
                m=baseline['fitted'][row['action']][row['selected']]
                if 'tree' in m:
                    leaf=m['tree']
                    while 'feature' in leaf:leaf=leaf['left'] if source['features'][leaf['feature']]<=leaf['threshold'] else leaf['right']
                    p,pred=leaf['p'],leaf['pred']
                else:
                    p=m['texts'].get(source['text'],m['p']);pred=p>=.5
            else:
                m=models[row['model_id']]
                if split=='train':assert m['outer']==row['recording_id'] and row['recording_id'] not in m['fit_groups']
                else:assert m['outer'] is None and m['inner'] is None
                p=numeric(m,source);pred=p>=selection[m['model_id']]['threshold']
                assert row['threshold']==selection[m['model_id']]['threshold']
            close(p,row['p']);assert pred==row['pred']
        for method in reports[split]['scores']:
            for action in ACTIONS:
                subset=[r for r in rows if r['method']==method and r['action']==action]
                assert {r['id'] for r in subset}=={r['id'] for r in lookup.values() if r['action']==action}
                measured=score(subset)
                for k,v in measured.items():close(v,reports[split]['scores'][method][action][k])
                metric_table.append({'split':split,'method':method,'action':action,**measured})
            for key in ('balanced_accuracy','brier','log_loss','ece_5'):
                close(sum(r[key] for r in metric_table[-3:])/3,reports[split]['scores'][method]['macro'][key])
        for action in ACTIONS:
            for recording in sorted({r['recording_id'] for r in lookup.values()}):
                subset=[r for r in rows if r['method']=='state_force' and r['action']==action and r['recording_id']==recording]
                error_table.append({'split':split,'action':action,'recording_id':recording,'n':len(subset),
                    'failure':sum(not r['success'] for r in subset),'false_success':sum(r['pred'] and not r['success'] for r in subset),
                    'false_failure':sum(not r['pred'] and r['success'] for r in subset)})
        boot=json.loads((RAW/split/'bootstrap.json').read_text())
        assert boot['valid']+boot['invalid']==2000 and len(boot['draws'])==boot['valid']
        refs=['v5_selected','v5_family_prior','duration','state']
        per_group={method:{g:[r for r in rows if r['method']==method and r['recording_id']==g] for g in boot['groups']}
                   for method in ['state_force']+refs}
        # Replay every recorded bootstrap draw directly from confusion counts, paired across methods.
        confusion={method:{g:{a:Counter((r['success'],r['pred']) for r in subset if r['action']==a) for a in ACTIONS}
                           for g,subset in gm.items()} for method,gm in per_group.items()}
        for draw in boot['draws']:
            multiplicity=Counter(boot['groups'][i] for i in draw['groups']);values={}
            for method in per_group:
                per_action=[]
                for action in ACTIONS:
                    c=Counter()
                    for g,n in multiplicity.items():
                        for key,v in confusion[method][g][action].items():c[key]+=n*v
                    per_action.append(.5*(c[True,True]/(c[True,True]+c[True,False])+c[False,False]/(c[False,False]+c[False,True])))
                values[method]=sum(per_action)/3
            close(draw['primary_ba'],values['state_force'])
            for ref in refs:close(draw['gain_'+ref],values['state_force']-values[ref])
        for key,interval in boot['intervals'].items():
            calculated=np.quantile([d[key] for d in boot['draws']],[.025,.975])
            np.testing.assert_allclose(calculated,interval,atol=1e-12)
            assert reports[split]['uncertainty']['intervals'][key]==interval
    nested=reports['train'];scores=nested['scores'];ba=lambda m:scores[m]['macro']['balanced_accuracy']
    checks=[ba('state_force')>=.75]+[ba('state_force')-ba(m)>=.05 for m in ('v5_selected','v5_family_prior','duration')]
    checks += [nested['uncertainty']['intervals']['gain_v5_selected'][0]>0,
        sum(scores['state_force'][a]['balanced_accuracy']-scores['v5_selected'][a]['balanced_accuracy']>=.05 for a in ACTIONS)>=2,
        scores['state_force']['macro']['brier']<=scores['v5_family_prior']['macro']['brier']+.02]
    any_useful=any(ba(m)-ba('v5_selected')>=.05 and ba(m)-ba('duration')>=.05 for m in ('state','force','state_force'))
    decision='UNCERTAIN_PROBE' if nested['uncertainty']['valid']<1000 else 'SUMMARY_SIGNAL_SUPPORTED' if all(checks) else 'MIXED_OR_UNSTABLE' if any_useful else 'NO_USEFUL_SUMMARY_GAIN'
    assert decision==nested['decision']
    table('metrics.tsv',metric_table);table('selection.tsv',selection_table);table('errors.tsv',error_table)
    variability=[]
    for group in protocol['feature_groups']:
        for action in ACTIONS:
            relevant=[r for r in selection_table if r['group']==group and r['action']==action and r['outer']!='final' and any(s['recording_id']==r['outer'] and s['action']==action for s in train.values())]
            variability.append({'group':group,'action':action,'action_bearing_outer_folds':len(relevant),
                'C_counts':dict(Counter(str(r['C']) for r in relevant)),
                'threshold_counts':dict(Counter(str(r['threshold']) for r in relevant)),
                'coefficient_norm_range':[min(r['coefficient_norm'] for r in relevant),max(r['coefficient_norm'] for r in relevant)]})
            outer_models=[m for m in models.values() if m['group']==group and m['action']==action and m['inner'] is None and m['outer'] in {r['outer'] for r in relevant}]
            variability[-1]['scaler_ranges']={name:{'mean_min':min(m['mean'][i] for m in outer_models),
                'mean_max':max(m['mean'][i] for m in outer_models),'scale_min':min(m['scale'][i] for m in outer_models),
                'scale_max':max(m['scale'][i] for m in outer_models)} for i,name in enumerate(protocol['feature_groups'][group])}
    write('variability.json',variability)
    write('verification.json',{'status':'PASS','fit_models':len(models),'inner_predictions':len(inner),
        'tuning_records':len(tuning),'nested_predictions':len(predictions['train']),'test_predictions':len(predictions['test']),
        'decision':decision,'checks':['immutable protocol/input/source hashes','fold-local scalers and class counts',
        'all inner numeric prediction replay','independent C/threshold choice','sealed final bundle',
        'nested and test numerical replay','independent BA/Brier/logloss/ECE','paired bootstrap arithmetic','decision branches']})
    write('checksums.json',{str(p):sha(p) for folder in (RAW/'train',RAW/'test',ART) for p in sorted(folder.iterdir()) if p.is_file()})
    print(json.dumps(json.loads((ART/'verification.json').read_text()),indent=2))


if __name__=='__main__':main()
