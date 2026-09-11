#!/usr/bin/env python3
"""Train-only v5 selection stability audit. Run inside the v6 audit container."""
import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

from baselines import ACTIONS, CANDIDATES, train, predict, measure, write_json, write_tsv, write_rows

BASE, OUT, RAW = Path('/workspace'), Path('/artifacts'), Path('/output')
TRAIN = Path('/input/train_features.jsonl')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path):
    with path.open() as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def inputs():
    frozen = json.loads((OUT/'freeze.json').read_text())
    for name, digest in frozen['source_sha256'].items():
        assert sha(BASE/name) == digest, name
    assert sha(TRAIN) == frozen['train_features_sha256']
    expected = json.loads((BASE/'artifacts_v5/checksums.json').read_text())
    assert sha(TRAIN) == expected['/output/train_features.jsonl']
    assert sha(BASE/'artifacts_v5/training.json') == expected['/artifacts/training.json']
    train_rows = [json.loads(line) for line in TRAIN.read_text().splitlines()]
    rows = [r for r in read_tsv(BASE/'artifacts_v4/segments.tsv')
            if r['target_action'] == 'True' and r['action_family'] in ACTIONS]
    expected_train = {r['recording_id']+':'+r['segment_index']: r for r in rows if r['split']=='train_split1.txt'}
    assert len(train_rows) == 309 and len(rows) == 413
    assert {r['id'] for r in train_rows} == set(expected_train)
    for row in train_rows:
        source = expected_train[row['id']]
        assert row['success'] == (source['success']=='True') and row['action'] == source['action_family']
    return train_rows, rows


def counts(rows):
    return len(rows), sum(r['success'] for r in rows), sum(not r['success'] for r in rows)


def run():
    assert not any(RAW.iterdir()), 'raw output must be empty'
    rows, metadata = inputs()
    groups = sorted({r['recording_id'] for r in rows})
    coverage, folds, stability, nested = [], [], [], []
    assert len(groups) == 15
    for split in ('train','test'):
        for action in ACTIONS:
            subset = [r for r in metadata if r['split']==f'{split}_split1.txt' and r['action_family']==action]
            failures = Counter(r['recording_id'] for r in subset if r['success']=='False')
            coverage.append({'split': split, 'action': action, 'n':len(subset),
                'success':sum(r['success']=='True' for r in subset), 'failure':sum(failures.values()),
                'recordings':len({r['recording_id'] for r in subset}),
                'success_recordings':len({r['recording_id'] for r in subset if r['success']=='True'}),
                'failure_recordings':len(failures), 'max_failures_in_one_recording':max(failures.values()),
                'max_failure_share':max(failures.values())/sum(failures.values())})
    original = json.loads((BASE/'artifacts_v5/training.json').read_text())
    replay = train(rows)
    assert replay['selected']==original['selected']
    for action in ACTIONS:
        for candidate in CANDIDATES:
            for metric in ('balanced_accuracy','brier'):
                assert math.isclose(replay['cv'][action][candidate][metric],original['cv'][action][candidate][metric],abs_tol=1e-12)
    for omitted in groups:
        outer_train = [r for r in rows if r['recording_id']!=omitted]
        bad = []
        for action in ACTIONS:
            n,s,f = counts([r for r in outer_train if r['action']==action])
            folds.append({'action':action,'outer':omitted,'inner':'','n':n,'success':s,'failure':f})
            if min(s,f)==0: bad.append(action)
            for inner in groups:
                if inner==omitted: continue
                n,s,f = counts([r for r in outer_train if r['action']==action and r['recording_id']!=inner])
                folds.append({'action':action,'outer':omitted,'inner':inner,'n':n,'success':s,'failure':f})
                if min(s,f)==0: bad.append(action)
        if bad:
            raise RuntimeError(f'NOT_ESTIMABLE nested fold {omitted}: {sorted(set(bad))}; no score produced')
        result = train(outer_train)
        for action in ACTIONS:
            chosen = result['selected'][action]
            heldout = [r for r in rows if r['recording_id']==omitted and r['action']==action]
            stability.append({'action':action,'omitted_recording':omitted,'omitted_rows':len(heldout),
                'omitted_failures':sum(not r['success'] for r in heldout),
                'selected':chosen,'original_selected':original['selected'][action],
                'changed':chosen!=original['selected'][action],
                'inner_ba':result['cv'][action][chosen]['balanced_accuracy'],
                'inner_brier':result['cv'][action][chosen]['brier']})
            for row in heldout:
                pred,p = predict(result['fitted'][action][chosen], row)
                nested.append({'id':row['id'],'action':action,'recording_id':omitted,
                               'success':row['success'],'pred':pred,'p':p,'selected':chosen})
    assert len(nested)==309 and len({r['id'] for r in nested})==309
    by_action = {}
    for action in ACTIONS:
        relevant = [r for r in stability if r['action']==action and r['omitted_rows']>0]
        relevant_folds = [r for r in folds if r['action']==action]
        by_action[action] = {'original_selected':original['selected'][action],
            'ordinary_selected_cv':original['cv'][action][original['selected'][action]],
            'nested_cv':measure([r for r in nested if r['action']==action]),
            'selection_counts_all_deletions':dict(Counter(r['selected'] for r in stability if r['action']==action)),
            'selection_counts_action_deletions':dict(Counter(r['selected'] for r in relevant)),
            'changed_action_deletions':sum(r['changed'] for r in relevant),
            'action_deletions':len(relevant),
            'min_outer_failure':min(r['failure'] for r in relevant_folds if not r['inner']),
            'min_inner_failure':min(r['failure'] for r in relevant_folds if r['inner']),
            'min_inner_success':min(r['success'] for r in relevant_folds if r['inner'])}
    summary={'status':'COMPLETED','train_only':True,'test_feature_access':False,'device':'cpu',
             'train_rows':309,'metadata_rows':413,'training_replay':'PASS','coverage':coverage,
             'actions':by_action,'nested_macro_ba':sum(v['nested_cv']['balanced_accuracy'] for v in by_action.values())/3,
             'ordinary_selected_macro_ba':sum(v['ordinary_selected_cv']['balanced_accuracy'] for v in by_action.values())/3}
    write_rows(RAW/'nested_predictions.jsonl',nested)
    write_tsv(OUT/'coverage.tsv',coverage)
    write_tsv(OUT/'folds.tsv',folds)
    write_tsv(OUT/'stability.tsv',stability)
    write_json(OUT/'audit.json',summary)
    print(json.dumps(summary,indent=2))


def verify():
    rows,metadata = inputs()
    audit = json.loads((OUT/'audit.json').read_text())
    nested = [json.loads(line) for line in (RAW/'nested_predictions.jsonl').read_text().splitlines()]
    lookup = {r['id']:r for r in rows}
    assert len(nested)==len({r['id'] for r in nested})==len(lookup)==309
    for r in nested:
        source=lookup[r['id']]
        assert (r['success'],r['action'],r['recording_id'])==(source['success'],source['action'],source['recording_id'])
    for report in audit['coverage']:
        subset=[r for r in metadata if r['split']==report['split']+'_split1.txt' and r['action_family']==report['action']]
        groups={r['recording_id'] for r in subset}
        fail_groups={r['recording_id'] for r in subset if r['success']=='False'}
        assert len(subset)==report['n'] and len(groups)==report['recordings'] and len(fail_groups)==report['failure_recordings']
    for fold in read_tsv(OUT/'folds.tsv'):
        subset=[r for r in rows if r['action']==fold['action'] and r['recording_id'] not in (fold['outer'],fold['inner'])]
        assert counts(subset)==tuple(int(fold[k]) for k in ('n','success','failure'))
    for action in ACTIONS:
        subset=[r for r in nested if r['action']==action]
        s=sum(r['success'] for r in subset); f=len(subset)-s
        tp=sum(r['success'] and r['pred'] for r in subset)
        tn=sum(not r['success'] and not r['pred'] for r in subset)
        brier=sum((r['p']-r['success'])**2 for r in subset)/len(subset)
        score=audit['actions'][action]['nested_cv']
        assert math.isclose((tp/s+tn/f)/2,score['balanced_accuracy'],abs_tol=1e-12)
        assert math.isclose(brier,score['brier'],abs_tol=1e-12)
        stability=[r for r in read_tsv(OUT/'stability.tsv') if r['action']==action]
        assert dict(Counter(r['selected'] for r in stability))==audit['actions'][action]['selection_counts_all_deletions']
    write_json(OUT/'verification.json',{'status':'PASS','coverage_rows':6,'fold_count':len(read_tsv(OUT/'folds.tsv')),
        'selection_records':45,'nested_predictions':309,'checks':['input hashes','train-only row membership',
        'coverage counts','nested training class counts','selection frequencies','independent nested BA/Brier']})
    write_json(OUT/'checksums.json',{str(p):sha(p) for root in (RAW,OUT) for p in sorted(root.iterdir()) if p.is_file()})
    print('Independent validation audit verification: PASS')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--verify',action='store_true')
    args=parser.parse_args()
    verify() if args.verify else run()
