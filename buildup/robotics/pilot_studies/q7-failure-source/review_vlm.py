"""Independent output/input review and descriptive counts; execute in Docker."""
import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse(text):
    text = text.strip()
    if text.startswith('```') and text.endswith('```'):
        text = '\n'.join(text.splitlines()[1:-1]).strip()
    try:
        obj = json.loads(text)
    except ValueError:
        return None
    if not isinstance(obj, dict) or set(obj) != {'verdict','evidence'}:
        return None
    if obj.get('verdict') not in ('GOAL_MET','GOAL_NOT_MET','UNCERTAIN') or not isinstance(obj.get('evidence'),str):
        return None
    return obj


def raw_diagnostic(rows, cases, conditions):
    # Added AFTER seeing the 30 raw outputs. Never replaces the frozen JSON endpoint.
    # An explicit verdict is recoverable; a missing evidence sentence is not invented.
    pattern = re.compile(r'The verdict is (GOAL_MET|GOAL_NOT_MET|UNCERTAIN)(?:\.| because ([^\n]+))')
    counts = {c: Counter() for c in conditions}
    strata = {c: defaultdict(Counter) for c in conditions}
    extracted = {}
    for row in rows:
        match = pattern.fullmatch(row['raw_response'].strip())
        verdict = match.group(1) if match else 'UNEXTRACTABLE'
        case = cases[row['case']]
        label = 0 if case['role'] == 'constructed' else case['source_label']
        target = 'GOAL_MET' if label == 1 else 'GOAL_NOT_MET'
        stratum = 'constructed' if case['role'] == 'constructed' else 'source'
        for bucket in (counts[row['condition']], strata[row['condition']][stratum]):
            bucket['total'] += 1
            bucket['reference_agreement'] += int(verdict == target)
            bucket['uncertain'] += int(verdict == 'UNCERTAIN')
            bucket['unextractable'] += int(match is None)
            bucket['false_positive'] += int(verdict == 'GOAL_MET' and label == 0)
            bucket['false_negative'] += int(verdict == 'GOAL_NOT_MET' and label == 1)
            bucket['explicit_reason_present'] += int(bool(match and match.group(2)))
            bucket[verdict] += 1
        extracted[(row['case'], row['condition'])] = {
            'verdict': verdict, 'agrees': verdict == target,
            'explicit_reason': match.group(2) if match else None}
    changes = Counter()
    table = []
    for name, case in cases.items():
        a, b = (extracted[(name, c)] for c in conditions)
        changes['verdict_changed'] += int(a['verdict'] != b['verdict'])
        changes['gained_reference_agreement'] += int(not a['agrees'] and b['agrees'])
        changes['lost_reference_agreement'] += int(a['agrees'] and not b['agrees'])
        label = 0 if case['role'] == 'constructed' else case['source_label']
        table.append({'case': name, 'reference': 'GOAL_MET' if label else 'GOAL_NOT_MET',
                      'end_only': a, 'start_end': b})
    return {'analysis_status': 'post_hoc_diagnostic_only', 'regex': pattern.pattern,
            'counts': counts, 'strata': strata, 'paired_changes': changes, 'cases': table,
            'boundary': 'Explicit verdict extraction after format failure; not a repaired JSON endpoint, independent evidence, held-out accuracy or proof of temporal benefit.'}


def main(args):
    run, prep = Path(args.run), Path(args.prepared)
    dest = run/'review.json'
    assert not dest.exists()
    cfg=read('/study/vlm_config.json')
    cases={case['id']:case for case in read(prep/'cases.json')}
    originals={row['path']:row['sha256'] for row in read(prep/'input.json')['files']}
    initial={row['group']:row['initial_goal_state'] for row in read('/study/annotations.json')['groups']}
    inputs={(j['case'],j['condition']):j for j in read(run/'inputs.json')}
    rows=[json.loads(line) for line in (run/'predictions.jsonl').read_text().splitlines()]
    expected={(name,c) for name in cases for c in cfg['conditions']}
    assert len(rows)==len(expected)==30
    assert len({(r['case'],r['condition']) for r in rows})==len(rows)
    assert {(r['case'],r['condition']) for r in rows}==expected==set(inputs)
    completion=read(run/'completion.json')
    assert completion['status']=='completed' and completion['predictions']==30
    assert completion['predictions_sha256']==sha(run/'predictions.jsonl')
    assert completion['inputs_sha256']==sha(run/'inputs.json')
    counts={c:Counter() for c in cfg['conditions']}
    strata={c:defaultdict(Counter) for c in cfg['conditions']}
    predictions={}
    table=[]
    for r in rows:
        c=cases[r['case']];condition=r['condition'];job=inputs[(r['case'],condition)]
        phase_order=['end'] if condition=='end_only' else ['start','end']
        wanted=[(phase,v,path) for phase in phase_order for v,path in enumerate(c[phase])]
        got=[(d['phase'],d['view_index'],d['relative_path']) for d in job['images']]
        assert got==wanted
        assert all(d['sha256']==originals[d['relative_path']] for d in job['images'])
        assert c['task'] in job['prompt'] and c['subtask'] in job['prompt']
        assert cfg['prompt_question'] in job['prompt']
        assert all(d['relative_path'] not in job['prompt'] for d in job['images'])
        for forbidden in ('source_failure','source_success','failure_reason','source_label','ground_truth'):
            assert forbidden not in job['prompt']
        assert r['prompt_sha256']==hashlib.sha256(job['prompt'].encode()).hexdigest()
        assert r['image_count']==len(wanted) and r['image_tokens']==81*len(wanted)
        assert r['tensor_shapes']['pixel_values'][1]==len(wanted)
        independently_parsed=parse(r['raw_response'])
        assert independently_parsed==r['parsed']
        verdict=independently_parsed['verdict'] if independently_parsed else 'INVALID'
        label=c['source_label']
        if c['role']=='constructed':
            assert initial[c['group']]=='visibly_unmet'
            label=0
        target='GOAL_MET' if label==1 else 'GOAL_NOT_MET'
        stratum='constructed' if c['role']=='constructed' else 'source'
        for bucket in (counts[condition],strata[condition][stratum]):
            bucket['total']+=1
            bucket['reference_agreement']+=int(verdict==target)
            bucket['uncertain']+=int(verdict=='UNCERTAIN')
            bucket['invalid']+=int(verdict=='INVALID')
            bucket['truncated']+=int(not r['terminated_with_eos'])
            bucket['false_positive']+=int(verdict=='GOAL_MET' and label==0)
            bucket['false_negative']+=int(verdict=='GOAL_NOT_MET' and label==1)
            bucket[verdict]+=1
        predictions[(r['case'],condition)]={'verdict':verdict,'reference':target,'agrees':verdict==target,
                                           'evidence':independently_parsed['evidence'] if independently_parsed else r['raw_response']}
    constant=Counter()
    for c in cases.values():
        label=0 if c['role']=='constructed' else c['source_label']
        constant['always_GOAL_MET_reference_agreement']+=int(label==1)
        constant['always_GOAL_NOT_MET_reference_agreement']+=int(label==0)
    constant['total']=len(cases)
    change=Counter()
    for name,c in cases.items():
        a,b=(predictions[(name,x)] for x in cfg['conditions'])
        change['verdict_changed']+=int(a['verdict']!=b['verdict'])
        change['gained_reference_agreement']+=int(not a['agrees'] and b['agrees'])
        change['lost_reference_agreement']+=int(a['agrees'] and not b['agrees'])
        table.append({'case':name,'role':c['role'],'source_row_1based':c['source_row_1based'],
                      'reference':a['reference'],'end_only':a,'start_end':b})
    cost={}
    for cond in cfg['conditions']:
        selected=[r for r in rows if r['condition']==cond]
        cost[cond]={'image_count':selected[0]['image_count'],
                    'input_tokens_range':[min(r['input_tokens'] for r in selected),max(r['input_tokens'] for r in selected)],
                    'generated_tokens_total':sum(r['generated_tokens'] for r in selected),
                    'median_seconds':median(r['elapsed_seconds'] for r in selected),
                    'max_peak_allocated_bytes':max((r['peak_allocated_bytes'] or 0) for r in selected)}
    result={'verification':'PASS','expected_predictions':30,'counts':counts,'strata':strata,
            'paired_changes':change,'constant_label_control':constant,'cost':cost,'cases':table,
            'post_hoc_raw_verdict': raw_diagnostic(rows,cases,cfg['conditions']),
            'runtime':read(run/'runtime.json'),
            'inputs_sha256':sha(run/'inputs.json'),'predictions_sha256':sha(run/'predictions.jsonl'),
            'review_source_sha256':sha(__file__),
            'limitations':['Reference agreement on dependent dev cases, not held-out accuracy.',
                           'Four constructed negatives use agent interpretation of the initial state.',
                           'Image number and token cost differ by condition; shared GPU timings are diagnostic.',
                           'Verifies row mapping, input identities and output parsing; source labels are not independently validated.']}
    dest.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:result[k] for k in ['verification','counts','strata','paired_changes','constant_label_control','cost']},ensure_ascii=False))
    print(json.dumps({k:result['post_hoc_raw_verdict'][k] for k in ['analysis_status','counts','strata','paired_changes']},ensure_ascii=False))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',default='/output/vlm');p.add_argument('--prepared',default='/prepared')
    main(p.parse_args())
