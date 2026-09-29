"""Independent raw-state verification and bounded descriptive analysis in Docker."""
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
import torch

GOAL = np.array([0.08,-0.08,0.16])


def check_episode(path):
    payload=json.loads(path.with_suffix('.json').read_text());m=payload['meta']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==m['trace_sha256']
    d=dict(np.load(path));n=len(d['actions']);hold=m['hold']
    assert n==80 and len(d['cube'])==81
    force_norm=np.linalg.norm(d['contact_forces'],axis=2)
    direction_norm=np.linalg.norm(d['finger_directions'],axis=2)
    cos=np.sum(d['contact_forces']*d['finger_directions'],axis=2)/np.maximum(force_norm*direction_norm,1e-20)
    grasp=np.all((force_norm>=0.5)&(cos>=np.cos(np.deg2rad(85))),axis=1)
    assert np.array_equal(grasp,d['grasp']),(path,'grasp predicate')
    distance=np.linalg.norm(d['cube'][:,:3]-GOAL,axis=1)
    success=grasp&(distance<=0.025)
    assert np.array_equal(success,d['success']),(path,'success predicate')
    assert bool(success[-5:].all())==m['success']
    assert bool(success.any())==m['success_once']
    assert bool(grasp.any())==m['grasp_once']
    assert int(np.sum(grasp[:-1]&~grasp[1:]))==m['releases']
    assert np.isclose(distance[-1],m['final_distance'],atol=1e-7)
    assert np.allclose(d['cube'][0,:3],m['initial_position'],atol=1e-7)
    assert np.allclose(d['velocity'][0],m['initial_velocity'],atol=1e-7)
    for i,t in enumerate(d['times']):
        previous=max(0,t-hold)
        expected=np.r_[d['cube'][t],d['velocity'][t],d['omega'][t],d['tcp'][t]-d['cube'][t],
                       d['qpos'][t],d['qvel'][t],(d['cube'][t,:3]-d['cube'][previous,:3])/0.10]
        assert np.allclose(expected,d['features'][i],atol=1e-7),(path,'features',i)
        assert np.array_equal(d['actions'][t:t+hold],np.tile(d['row_action'][i],(hold,1)))
        assert np.allclose(d['delta'][i],d['cube'][t+hold,:3]-d['cube'][t,:3],atol=1e-8)
    assert np.isfinite(np.concatenate([v.ravel() for v in d.values()])).all()
    # These phase facts come from observed positions and stored decisions, not force flags.
    first_contact=np.where(np.max(force_norm,axis=1)>0.05)[0]
    first_grasp=np.where(grasp)[0]
    first_success=np.where(success)[0]
    m.update(first_contact_step=int(first_contact[0]) if len(first_contact) else None,
             first_grasp_step=int(first_grasp[0]) if len(first_grasp) else None,
             first_success_step=int(first_success[0]) if len(first_success) else None,
             first_contact_speed=float(np.linalg.norm(d['velocity'][first_contact[0],:2])) if len(first_contact) else None,
             max_phase=int(d['phase'].max()),trace=path.name)
    return m,d


def summarize(rows):
    results=[]
    for moving in (False,True):
        for mode in ('servo','cv','history','action','fast'):
            group=[r for r in rows if r['moving']==moving and r['mode']==mode]
            assert len(group)==24
            results.append(dict(moving=moving,mode=mode,episodes=len(group),success=sum(r['success'] for r in group),
                once=sum(r['success_once'] for r in group),grasp_once=sum(r['grasp_once'] for r in group),
                releases=sum(r['releases'] for r in group),
                mean_latency_ms=float(np.mean([r['mean_latency_ms'] for r in group])),
                mean_decisions=float(np.mean([r['decisions'] for r in group])),
                mean_first_success_seconds=float(np.mean([r['first_success_step']*0.05 for r in group if r['success']]))
                    if any(r['success'] for r in group) else None))
    paired=[]
    lookup={(r['seed'],r['moving'],r['mode']):r for r in rows}
    for reference in ('servo','cv','history','fast'):
        for moving in (False,True):
            pairs=[(lookup[(s,moving,reference)],lookup[(s,moving,'action')]) for s in range(20000,20024)]
            paired.append(dict(reference=reference,moving=moving,
                improved=[b['seed'] for a,b in pairs if not a['success'] and b['success']],
                harmed=[b['seed'] for a,b in pairs if a['success'] and not b['success']],
                both_success=sum(a['success'] and b['success'] for a,b in pairs),
                both_failure=sum(not a['success'] and not b['success'] for a,b in pairs)))
    return dict(results=results,paired_action=paired,scope='exploratory, one task/model seed; no significance or generality claim')


def prediction_errors(data_dir,model_dir):
    from model import Predictor
    models={m:Predictor(model_dir/(m+'.pt')) for m in ('history','action')}
    grouped={}
    for path in sorted(data_dir.glob('*.npz')):
        meta=json.loads(path.with_suffix('.json').read_text())['meta']
        if meta['seed']<10064:continue
        d=dict(np.load(path));f=d['features'];actions=d['row_action'];y=d['delta']
        preds={'cv':f[:,7:10]*0.1,**{m:net.predict(f,actions) for m,net in models.items()}}
        for phase in ('all','approach_closing','transport'):
            mask=np.ones(len(f),bool) if phase=='all' else d['phase']<3 if phase=='approach_closing' else d['phase']==3
            for mode,pred in preds.items():grouped.setdefault((phase,mode),[]).extend(np.sum((pred[mask]-y[mask])**2,axis=1).tolist())
    return [dict(phase=p,mode=m,rows=len(v),rmse_m=float(np.sqrt(np.mean(v)))) for (p,m),v in grouped.items()]


def run_verify(root,out,data_name,model_name):
    rows=[];initials={};count=0;frame_count=0;row_count=0
    for subset in (data_name,'eval1'):
        for path in sorted((root/subset).glob('*.npz')):
            m,d=check_episode(path);count+=1;frame_count+=len(d['cube']);row_count+=len(d['features'])
            if subset=='eval1':
                assert 20000<=m['seed']<20024
                key=(m['seed'],m['moving'])
                initial=np.r_[d['cube'][0],d['velocity'][0],d['qpos'][0],d['qvel'][0],d['tcp'][0]]
                if key in initials:assert np.allclose(initial,initials[key],rtol=0,atol=1e-7),(key,'paired initial mismatch')
                initials[key]=initial;rows.append(m)
            else:assert 10000<=m['seed']<10080
    assert count==400 and len(rows)==240
    for mode in ('history','action'):
        ckpt=torch.load(root/model_name/(mode+'.pt'),map_location='cpu',weights_only=False)
        assert set(ckpt['train_seeds']).isdisjoint(ckpt['val_seeds'])
        assert not (set(ckpt['train_seeds'])|set(ckpt['val_seeds']))&set(range(20000,20024))
    summary=summarize(rows)
    summary['validation_prediction']=prediction_errors(root/data_name,root/model_name)
    summary['fit']=json.loads((root/model_name/'fit.json').read_text())
    for v in summary['fit'].values():
        if isinstance(v,dict):v.pop('curve',None)
    summary['verification']=dict(status='passed',episodes=count,raw_states=frame_count,decision_rows=row_count,
        paired_initial_conditions=len(initials),checks=['NPZ identity','native grasp from raw forces/directions',
        'goal and sustained success','release count','initial physical state','observation-only features',
        'held action and future displacement','finite values','episode-disjoint fit/validation/evaluation'])
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    keys=['seed','moving','mode','success','success_once','grasp_once','releases','first_contact_step',
          'first_contact_speed','first_grasp_step','first_success_step','max_phase','final_distance','mean_latency_ms','trace']
    with (out/'episodes.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows({k:r[k] for k in keys} for r in rows)
    print(json.dumps(summary,indent=2),flush=True)
