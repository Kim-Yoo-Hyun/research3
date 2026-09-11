"""Independent physical labels, planned-action checks, and paired episode summaries."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import numpy as np
from codecs_impl import read_packets,depacket
from transformers import AutoProcessor
spec=importlib.util.spec_from_file_location('readiness_labels','/baseline/verify.py')
reference=importlib.util.module_from_spec(spec);spec.loader.exec_module(reference)
P=json.loads(Path('/work/protocol.json').read_text());O=Path('/outputs')
LABELS=reference.LABELS


def record(seed,mode):
    root=O/f'seed_{seed}';receipt=json.loads((root/(mode+'.json')).read_text())
    d=dict(np.load(root/(mode+'.npz')));n=len(d['actions'])
    checks={'completed':receipt['status']=='completed','finite':all(np.isfinite(v).all() for v in d.values()),
            'action_hash':hashlib.sha256(d['actions'].tobytes()).hexdigest()==receipt['action_sha256'],
            'shapes':n>0 and all(len(v)==n+1 for k,v in d.items() if k!='actions')}
    checks['independent_labels']=checks['shapes'] and all(np.array_equal(d[k],v) for k,v in reference.labels_from_arrays(d).items())
    if mode!='generation':
        original=dict(np.load(root/'generation.npz'))
        expected=original['actions'] if mode.startswith('replay_') else np.load(root/'planned'/(mode+'.npy'))
        checks['actions_exact']=d['actions'].dtype==expected.dtype and d['actions'].tobytes()==expected.tobytes()
        physical=[k for k in original if k not in LABELS+['actions'] and 'force' not in k]
        checks['initial_state']=checks['shapes'] and max(float(np.max(np.abs(d[k][0]-original[k][0]))) for k in physical)<=P['initial_state_atol']
        if mode.startswith('replay_'):checks['original_labels_exact']=all(np.array_equal(d[k],original[k]) for k in LABELS)
    return {'valid':all(checks.values()),'checks':checks,'steps':n,'success':bool(d['success'][-1]) if n else None}


def bootstrap(values):
    x=np.array(values,dtype=float)
    if not len(x):return None
    rng=np.random.default_rng(P['bootstrap_seed'])
    samples=x[rng.integers(0,len(x),(P['bootstrap_resamples'],len(x)))].mean(axis=1)
    return np.quantile(samples,[.025,.975]).tolist()


def summarize(seeds):
    cal=json.loads((O/'calibration.json').read_text());proc=AutoProcessor.from_pretrained('/inputs/fast',trust_remote_code=True,local_files_only=True)
    rows=[];codec_valid=True
    for seed in seeds:
        root=O/f'seed_{seed}';source=dict(np.load(root/'generation.npz'));manifest=json.loads((root/'planned/manifest.json').read_text())
        episode={'seed':seed,'source_success':bool(source['success'][-1]),'methods':{},'events':manifest['events']}
        for name,m in manifest['methods'].items():
            if m['status']!='planned':episode['methods'][name]={'status':m['status']};continue
            verified=record(seed,name);back=np.load(root/'planned'/(name+'.npy'))
            assert hashlib.sha256(back.tobytes()).hexdigest()==m['array_sha256']
            if name in P['codec_variants']:
                raw=(root/'planned'/(name+'.bin')).read_bytes();assert len(raw)==m['bytes']
                reconstructed=[];stats=m['normalization'];c=np.array(stats['center']);w=np.array(stats['half_range'])
                for blob in read_packets(raw):
                    normalized,n=depacket(blob,proc);a=normalized[:n]*w+c
                    if name not in ['fast_joint','fast_quantile']:a[:,7]=normalized[:n,7]
                    reconstructed.append(a)
                assert np.array_equal(np.concatenate(reconstructed),back)
            else:
                event,location=name.rsplit('_',1);meta=manifest['events'][event]
                start=meta['event_action_start'] if location=='event' else meta['free_action_start']
                residual=np.load(root/'planned'/(P['mechanism_reference']+'.npy'))-source['actions']
                expected=source['actions'].copy();e=meta['event_action_start'];L=meta['length']
                expected[start:start+L,:7]+=residual[e:e+L,:7]
                assert np.array_equal(expected,back)
            episode['methods'][name]={'status':'verified' if verified['valid'] else 'measurement_invalid','verification':verified,**{k:m[k] for k in ['bytes','chunks','arm_mse'] if k in m}}
            codec_valid &= verified['valid']
        rows.append(episode)
    tables={}
    for name in P['codec_variants']:
        usable=[r for r in rows if r['methods'].get(name,{}).get('status')=='verified']
        delta=[int(r['methods'][name]['verification']['success'])-int(r['source_success']) for r in usable]
        tables[name]={'eligible_originals':len(rows),'verified_variants':len(usable),'unavailable_or_invalid':len(rows)-len(usable),
                      'source_success':sum(r['source_success'] for r in usable),'codec_success':sum(r['methods'][name]['verification']['success'] for r in usable),
                      'paired_success_delta':float(np.mean(delta)) if delta else None,'paired_bootstrap_95':bootstrap(delta),
                      'lost_success':sum(d<0 for d in delta),'gained_success':sum(d>0 for d in delta)}
    comparisons={}
    ref='fast_joint_gripper'
    for name in P['codec_variants']:
        common=[r for r in rows if all(r['methods'].get(k,{}).get('status')=='verified' for k in [ref,name])]
        if not common:comparisons[name]={'status':'NO_COMMON_VERIFIED_INPUTS'};continue
        def metrics(k):
            chunks=sum(r['methods'][k]['chunks'] for r in common)
            cost=(128+sum(r['methods'][k]['bytes'] for r in common))/chunks
            weighted=sum(r['methods'][k]['arm_mse']*r['methods'][k]['verification']['steps'] for r in common)
            count=sum(r['methods'][k]['verification']['steps'] for r in common)
            return cost,weighted/count
        a,b=metrics(ref),metrics(name)
        comparisons[name]={'reference':ref,'episodes':len(common),'reference_bytes':a[0],'control_bytes':b[0],
                           'reference_arm_mse':a[1],'control_arm_mse':b[1],
                           'rate_matched':abs(b[0]-a[0])<=P['rate_support_relative_tolerance']*a[0],
                           'error_matched':abs(b[1]-a[1])<=max(P['mse_absolute_floor'],P['mse_support_relative_tolerance']*a[1])}
    localization={}
    for event in P['event_types']:
        a=event+'_event';b=event+'_free'
        common=[r for r in rows if all(r['methods'].get(k,{}).get('status')=='verified' for k in [a,b])]
        lost=sum(not r['methods'][a]['verification']['success'] and r['methods'][b]['verification']['success'] for r in common)
        opposite=sum(r['methods'][a]['verification']['success'] and not r['methods'][b]['verification']['success'] for r in common)
        n=lost+opposite;pval=min(1.,2*sum(math.comb(n,k) for k in range(min(lost,opposite)+1))/2**n) if n else 1.
        localization[event]={'eligible_pairs':len(common),'event_fails_free_succeeds':lost,'event_succeeds_free_fails':opposite,
                             'exact_paired_two_sided_p':pval,'bonferroni_alpha':P['localization_two_sided_alpha_per_event'],
                             'diagnostic_signal':len(common)>=P['localization_min_pairs'] and lost>opposite and pval<=P['localization_two_sided_alpha_per_event'],
                             'remaining_confounding':'robot configuration, clearance and acceleration are not randomized; this is not contact causality proof'}
    if not codec_valid:decision='MEASUREMENT_INVALID'
    elif len(seeds)<P['heldout_min_valid']:decision='INSUFFICIENT_DENOMINATOR'
    elif not all(t['verified_variants']==len(seeds) for t in tables.values()):decision='INCOMPLETE_CODEC_SUPPORT'
    elif all(t['lost_success']==0 and t['gained_success']==0 for t in tables.values()):decision='NO_TASK_OUTCOME_CHANGES'
    else:decision='OUTCOME_CHANGES_REQUIRE_STAGE7_REVIEW'
    result={'decision':decision,'heldout_eligible':len(seeds),'rows':rows,'codec_table':tables,'rate_error_support':comparisons,'localization':localization,
            'no_automatic_hypothesis_selection':True}
    (O/'analysis.json').write_text(json.dumps(result,indent=2,allow_nan=False));return result
