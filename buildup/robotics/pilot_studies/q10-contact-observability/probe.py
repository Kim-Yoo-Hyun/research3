#!/usr/bin/env python3
"""Frozen v6 logistic study. Docker-only train/evaluate entrypoints."""
import argparse
import csv
import hashlib
import json
import time
import warnings
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

import baselines as v5

BASE = Path('/workspace')
ART = Path('/artifacts')
RAW = Path('/output')
PROTOCOL_HASH = '0fa06e424870090b8fc46f205aaaa0748c3a04ca4aaedcfff5e214903c465dd4'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines()]


def append(stream, row):
    stream.write(json.dumps(row, allow_nan=False) + '\n')


def now():
    return datetime.now(timezone.utc).isoformat()


def row_digest(rows):
    return hashlib.sha256('\n'.join(sorted(r['id'] for r in rows)).encode()).hexdigest()


def load_protocol():
    assert sha(BASE/'protocol_v6.json') == PROTOCOL_HASH
    p = json.loads((BASE/'protocol_v6.json').read_text())
    for name, digest in p['source_sha256'].items():
        assert sha(BASE/name) == digest, name
    execution = json.loads((ART/'execution.json').read_text())
    for name, digest in execution['source_sha256'].items():
        assert sha(BASE/name) == digest, name
    return p


def load_rows(path, split, protocol):
    assert sha(path) == protocol['input_sha256'][f'runs/q10_v5/{split}_features.jsonl']
    rows = read_jsonl(path)
    with (BASE/'artifacts_v4/segments.tsv').open() as stream:
        expected = {r['recording_id']+':'+r['segment_index']: r for r in csv.DictReader(stream, delimiter='\t')
                    if r['target_action']=='True' and r['action_family'] in v5.ACTIONS and r['split']==f'{split}_split1.txt'}
    assert len(rows) == len(expected) == (309 if split=='train' else 104)
    assert len({r['id'] for r in rows}) == len(rows) and {r['id'] for r in rows} == set(expected)
    for row in rows:
        source = expected[row['id']]
        assert row['success'] == (source['success']=='True') and row['action']==source['action_family']
        assert row['recording_id']==source['recording_id'] and row['text']==source['text']
        assert set(row['features']) == set(protocol['feature_groups']['state_force_duration'])
        assert np.isfinite(list(row['features'].values())).all()
    return rows


def fit_logistic(rows, names, c, params):
    x = np.array([[r['features'][name] for name in names] for r in rows], dtype=np.float64)
    y = np.array([r['success'] for r in rows], dtype=int)
    if set(y) != {0,1}:
        raise ValueError('INVALID_PROTOCOL: fitting partition lacks a class')
    scaler = StandardScaler(with_mean=True, with_std=True)
    z = scaler.fit_transform(x)
    kwargs = {k:v for k,v in params.items() if k not in ('implementation','C_grid')}
    model = LogisticRegression(C=c, **kwargs)
    with warnings.catch_warnings():
        warnings.simplefilter('error', ConvergenceWarning)
        model.fit(z, y)
    if int(model.n_iter_.max()) >= params['max_iter'] or not np.isfinite(model.coef_).all() or not np.isfinite(model.intercept_).all():
        raise ValueError('INVALID_PROTOCOL: convergence/coefficients')
    record = {'names':names,'C':c,'mean':scaler.mean_.tolist(),'scale':scaler.scale_.tolist(),
              'variance':scaler.var_.tolist(),'coef':model.coef_[0].tolist(),
              'intercept':float(model.intercept_[0]),'iterations':int(model.n_iter_.max()),
              'constant_features':[name for name,var in zip(names,scaler.var_) if var==0],
              'fit_groups':sorted({r['recording_id'] for r in rows}), 'fit_n':len(rows),
              'fit_failures':int((y==0).sum()),'fit_rows_sha256':row_digest(rows),
              'coefficient_norm':float(np.linalg.norm(model.coef_))}
    return record, scaler, model


def score_pair(y, probabilities, threshold):
    y = np.asarray(y, bool)
    pred = np.asarray(probabilities) >= threshold
    if y.all() or not y.any():
        raise ValueError('INVALID_PROTOCOL: pooled selection lacks a class')
    ba = .5 * (pred[y].mean() + (~pred[~y]).mean())
    return float(ba), float(np.mean((probabilities-y)**2))


def select_pair(candidates, tolerance=1e-12):
    best = None
    for item in candidates:
        if best is None:
            best = item
            continue
        if item['ba'] > best['ba'] + tolerance:
            best = item
        elif abs(item['ba']-best['ba']) <= tolerance:
            if item['brier'] < best['brier'] - tolerance:
                best = item
            elif abs(item['brier']-best['brier']) <= tolerance:
                if (item['C'],abs(item['threshold']-.5),item['threshold']) < (best['C'],abs(best['threshold']-.5),best['threshold']):
                    best = item
    return best


class Fitter:
    def __init__(self, protocol, models, inner, tuning):
        self.protocol, self.models, self.inner, self.tuning = protocol, models, inner, tuning
        self.count = 0

    def fit(self, rows, group, action, c, outer, inner):
        self.count += 1
        names = self.protocol['feature_groups'][group]
        record, scaler, model = fit_logistic(rows,names,c,self.protocol['model'])
        record.update(model_id=f'fit{self.count:05d}',group=group,action=action,outer=outer,inner=inner)
        append(self.models,record)
        return record, scaler, model

    def tune(self, rows, groups, group, action, outer):
        candidates=[]
        action_rows=[r for r in rows if r['action']==action]
        names=self.protocol['feature_groups'][group]
        for c in self.protocol['model']['C_grid']:
            pooled=[]
            for inner in groups:
                fitting=[r for r in action_rows if r['recording_id']!=inner]
                heldout=[r for r in action_rows if r['recording_id']==inner]
                record,scaler,model=self.fit(fitting,group,action,c,outer,inner)
                if not heldout:
                    continue
                x=np.array([[r['features'][n] for n in names] for r in heldout])
                probabilities=model.predict_proba(scaler.transform(x))[:,1]
                for row,p in zip(heldout,probabilities):
                    item={'id':row['id'],'success':row['success'],'p':float(p),'model_id':record['model_id'],
                          'group':group,'action':action,'outer':outer,'inner':inner,'C':c}
                    append(self.inner,item)
                    pooled.append(item)
            assert len(pooled)==len(action_rows) and {r['id'] for r in pooled}=={r['id'] for r in action_rows}
            y=np.array([r['success'] for r in pooled]); probabilities=np.array([r['p'] for r in pooled])
            for threshold in self.protocol['threshold_grid']:
                ba,brier=score_pair(y,probabilities,threshold)
                candidates.append({'C':c,'threshold':threshold,'ba':ba,'brier':brier})
        chosen=select_pair(candidates,self.protocol['metric_tie_tolerance'])
        record,scaler,model=self.fit(action_rows,group,action,chosen['C'],outer,None)
        record['threshold']=chosen['threshold']
        append(self.tuning,{'outer':outer,'group':group,'action':action,'chosen':chosen,
                            'model_id':record['model_id'],'candidates':candidates})
        return record,scaler,model


def prediction(row, method, pred, probability, **extra):
    return {'id':row['id'],'recording_id':row['recording_id'],'action':row['action'],
            'success':row['success'],'method':method,'pred':bool(pred),'p':float(probability),**extra}


def evaluate_metrics(rows):
    results={}
    for method in sorted({r['method'] for r in rows}):
        results[method]={action:v5.measure([r for r in rows if r['method']==method and r['action']==action]) for action in v5.ACTIONS}
        results[method]['macro']={key:float(np.mean([results[method][a][key] for a in v5.ACTIONS]))
                                   for key in ('balanced_accuracy','brier','log_loss','ece_5')}
    return results


def bootstrap(rows, protocol):
    methods=sorted({r['method'] for r in rows}); groups=sorted({r['recording_id'] for r in rows})
    counts=np.zeros((len(methods),len(groups),3,4))
    for row in rows:
        cell=0 if row['success'] and row['pred'] else 1 if row['success'] else 2 if not row['pred'] else 3
        counts[methods.index(row['method']),groups.index(row['recording_id']),v5.ACTIONS.index(row['action']),cell]+=1
    rng=np.random.default_rng(protocol['seed']); draws=[]; invalid=0
    refs=['v5_selected','v5_family_prior','duration','state']
    for _ in range(protocol['bootstrap']['draws']):
        sample=rng.integers(len(groups),size=len(groups))
        total=counts[:,sample].sum(axis=1)
        success=total[:,:,0]+total[:,:,1]; failure=total[:,:,2]+total[:,:,3]
        if (success==0).any() or (failure==0).any():
            invalid+=1
            continue
        ba=(.5*(total[:,:,0]/success+total[:,:,2]/failure)).mean(axis=1)
        primary=ba[methods.index('state_force')]
        values={'primary_ba':float(primary)}
        values.update({f'gain_{ref}':float(primary-ba[methods.index(ref)]) for ref in refs})
        draws.append({'groups':sample.tolist(),**values})
    keys=['primary_ba']+[f'gain_{ref}' for ref in refs]
    intervals={key:np.quantile([d[key] for d in draws],[.025,.975]).tolist() if draws else None for key in keys}
    return {'seed':protocol['seed'],'requested':2000,'valid':len(draws),'invalid':invalid,
            'groups':groups,'intervals':intervals,'draws':draws}


def decide(scores, boot, protocol):
    get=lambda name:scores[name]['macro']['balanced_accuracy']
    support=protocol['signal_support']; gain=support['min_gain_over_v5_prior_duration']
    checks={'primary_ba':get('state_force')>=support['min_primary_macro_ba'],
            **{f'gain_{ref}':get('state_force')-get(ref)>=gain for ref in ('v5_selected','v5_family_prior','duration')},
            'positive_interval':boot['intervals']['gain_v5_selected'] is not None and boot['intervals']['gain_v5_selected'][0]>0,
            'two_actions':sum(scores['state_force'][a]['balanced_accuracy']-scores['v5_selected'][a]['balanced_accuracy']>=support['min_action_gain_over_v5'] for a in v5.ACTIONS)>=2,
            'brier':scores['state_force']['macro']['brier']<=scores['v5_family_prior']['macro']['brier']+.02}
    useful={m:(get(m)-get('v5_selected')>=gain and get(m)-get('duration')>=gain) for m in ('state','force','state_force')}
    if boot['valid']<1000:decision='UNCERTAIN_PROBE'
    elif all(checks.values()):decision='SUMMARY_SIGNAL_SUPPORTED'
    elif not any(useful.values()):decision='NO_USEFUL_SUMMARY_GAIN'
    else:decision='MIXED_OR_UNSTABLE'
    return {'decision':decision,'support_checks':checks,'useful_by_group':useful}


def practical(scores):
    s=scores['state_force']; p=scores['v5_family_prior']['macro']
    return {'macro_ba':s['macro']['balanced_accuracy']>=.85,
            'prior_gain':s['macro']['balanced_accuracy']-p['balanced_accuracy']>=.10,
            'each_action_ba':all(s[a]['balanced_accuracy']>=.75 for a in v5.ACTIONS),
            'each_failure_recall':all(s[a]['failure_recall']>=.75 for a in v5.ACTIONS),
            'brier':s['macro']['brier']<=p['brier']+.02}


def train():
    assert not Path('/input/test_features.jsonl').exists(), 'test feature mounted in train'
    protocol=load_protocol(); rows=load_rows('/input/train_features.jsonl','train',protocol)
    assert not any(RAW.iterdir()), 'exclusive output required'
    audit_path=Path('/input/audit_predictions.jsonl')
    assert sha(audit_path)==protocol['input_sha256']['runs/q10_validation_v6/nested_predictions.jsonl']
    audited={r['id']:r for r in read_jsonl(audit_path)}
    groups=sorted({r['recording_id'] for r in rows}); all_predictions=[]; final={}; baselines={}
    started=time.monotonic()
    with (RAW/'models.jsonl').open('x') as models,(RAW/'inner.jsonl').open('x') as inner,(RAW/'tuning.jsonl').open('x') as tuning:
        fitter=Fitter(protocol,models,inner,tuning)
        for outer in groups+[None]:
            fitting=[r for r in rows if r['recording_id']!=outer]
            heldout=[r for r in rows if r['recording_id']==outer]
            remaining=[g for g in groups if g!=outer]
            baseline=v5.train(fitting)
            baselines[outer or 'final']=baseline
            if outer is not None:
                for row in heldout:
                    for candidate in v5.CANDIDATES+['selected']:
                        name=baseline['selected'][row['action']] if candidate=='selected' else candidate
                        pred,p=v5.predict(baseline['fitted'][row['action']][name],row)
                        if candidate=='selected':
                            assert pred==audited[row['id']]['pred'] and abs(p-audited[row['id']]['p'])<1e-12
                            assert name==audited[row['id']]['selected']
                        all_predictions.append(prediction(row,'v5_'+candidate,pred,p,selected=name,outer=outer))
            for group,names in protocol['feature_groups'].items():
                for action in v5.ACTIONS:
                    record,scaler,model=fitter.tune(fitting,remaining,group,action,outer)
                    if outer is None:
                        final.setdefault(group,{})[action]=record
                    else:
                        subset=[r for r in heldout if r['action']==action]
                        if subset:
                            x=np.array([[r['features'][n] for n in names] for r in subset])
                            probabilities=model.predict_proba(scaler.transform(x))[:,1]
                            for row,p in zip(subset,probabilities):
                                all_predictions.append(prediction(row,group,p>=record['threshold'],p,
                                     model_id=record['model_id'],threshold=record['threshold'],outer=outer))
            print(f'completed outer={outer or "final"} fits={fitter.count} elapsed={time.monotonic()-started:.1f}s',flush=True)
    assert len(all_predictions)==309*17
    v5.write_rows(RAW/'nested_predictions.jsonl',all_predictions)
    v5.write_json(RAW/'baseline_models.json',baselines)
    scores=evaluate_metrics(all_predictions); boot=bootstrap(all_predictions,protocol)
    v5.write_json(RAW/'bootstrap.json',boot)
    summary={**decide(scores,boot,protocol),'scores':scores,
             'uncertainty':{k:v for k,v in boot.items() if k!='draws'},'practical':practical(scores),
             'fit_count':fitter.count,'wall_seconds':time.monotonic()-started,'device':'cpu'}
    v5.write_json(ART/'nested.json',summary)
    bundle={'models':final,'baselines':baselines['final'],'sealed_at_utc':now(),
            'protocol_sha256':sha(BASE/'protocol_v6.json'),'execution_sha256':sha(ART/'execution.json'),
            'train_features_sha256':sha('/input/train_features.jsonl'),'fit_count':fitter.count,
            'raw_sha256':{p.name:sha(p) for p in sorted(RAW.iterdir())},'nested_sha256':sha(ART/'nested.json')}
    v5.write_json(ART/'training.json',bundle)
    print(json.dumps({'decision':summary['decision'],'primary':scores['state_force']['macro'],
                      'v5':scores['v5_selected']['macro'],'sealed':sha(ART/'training.json')},indent=2),flush=True)


def evaluate():
    protocol=load_protocol(); bundle=json.loads((ART/'training.json').read_text())
    seal=json.loads((ART/'train_seal.json').read_text())
    assert sha(ART/'training.json')==seal['training_sha256'] and sha(ART/'nested.json')==bundle['nested_sha256']
    assert bundle['protocol_sha256']==sha(BASE/'protocol_v6.json')
    rows=load_rows('/input/test_features.jsonl','test',protocol)
    assert not any(RAW.iterdir())
    started=now(); predictions=[]
    for row in rows:
        for group in protocol['feature_groups']:
            m=bundle['models'][group][row['action']]
            z=(np.array([row['features'][n] for n in m['names']])-m['mean'])/m['scale']
            score=float(np.dot(z,m['coef'])+m['intercept'])
            p=float(np.exp(-np.logaddexp(0,-score)))
            predictions.append(prediction(row,group,p>=m['threshold'],p,threshold=m['threshold'],model_id=m['model_id']))
        for candidate in v5.CANDIDATES+['selected']:
            name=bundle['baselines']['selected'][row['action']] if candidate=='selected' else candidate
            pred,p=v5.predict(bundle['baselines']['fitted'][row['action']][name],row)
            predictions.append(prediction(row,'v5_'+candidate,pred,p,selected=name))
    assert len(predictions)==104*17
    scores=evaluate_metrics(predictions); boot=bootstrap(predictions,protocol)
    v5.write_rows(RAW/'predictions.jsonl',predictions)
    v5.write_rows(RAW/'errors.jsonl',[r for r in predictions if r['method']=='state_force' and r['pred']!=r['success']])
    v5.write_json(RAW/'bootstrap.json',boot)
    v5.write_json(ART/'test.json',{'role':'exploratory_only','scores':scores,
        'uncertainty':{k:v for k,v in boot.items() if k!='draws'},'practical':practical(scores),
        'training_sha256':seal['training_sha256'],'started_at_utc':started})
    assert sha(ART/'training.json')==seal['training_sha256']
    print(json.dumps({'role':'exploratory','primary':scores['state_force']['macro']},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('stage',choices=['train','evaluate'])
    args=parser.parse_args()
    train() if args.stage=='train' else evaluate()
