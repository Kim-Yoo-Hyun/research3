"""Independent action replay, observation-only gate and model-selection verification."""
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

from dp_compare import candidates,model_choice,ROUTES,SEEDS
from dp_observation import ObservationGeometry
from dp_verify import check_replay
from repeat_action_model import wrap

ROOT=Path('/output')
OUT=ROOT/'compare1'
MODEL=Path('/previous/fit_model1/model.npz')


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):
            h.update(chunk)
    return h.hexdigest()


def load(path):
    with np.load(path,allow_pickle=False) as data:
        return {k:data[k].copy() for k in data.files}


def maxdiff(a,b):
    return float(np.max(np.abs(np.asarray(a)-np.asarray(b))))


def main():
    evaluation=json.loads((OUT/'evaluation.json').read_text())
    assert evaluation['status']=='completed' and evaluation['seeds']==list(SEEDS)
    assert len(evaluation['rows'])==len(ROUTES)*len(SEEDS)
    assert evaluation['source_checkpoint_sha256']==digest(Path('/checkpoint/model.ckpt'))
    assert evaluation['updated_checkpoint_sha256']==digest(ROOT/'finetune1/checkpoint.pt')
    assert evaluation['transition_model_sha256']==digest(MODEL)
    geo=ObservationGeometry()
    with np.load(MODEL,allow_pickle=False) as data:
        tree=cKDTree(data['features']);targets=data['targets'].copy()
    result_rows=[]
    for seed in SEEDS:
        rows=[r for r in evaluation['rows'] if r['seed']==seed]
        assert [r['route'] for r in rows]==list(ROUTES)
        initials=[]
        frozen_trace=None
        for row in rows:
            path=OUT/row['trace']
            assert digest(path)==row['sha256']
            trace=load(path)
            n=row['steps']
            assert 1<=n<=300
            assert trace['action'].shape==(n,2) and trace['observation'].shape==(n+1,5)
            assert trace['policy_observation'].shape==(n+1,40)
            assert trace['full'].shape==(n+1,10) and trace['coverage'].shape==(n+1,)
            assert trace['contact'].shape==(n,)
            assert all(np.isfinite(x).all() for x in trace.values())
            initials.append(trace['full'][0])
            drift=check_replay(seed,'released_dp',trace)
            assert drift<=1e-8
            assert row['any_success']==bool(np.any(trace['coverage']>.95))
            assert row['final_success']==bool(trace['coverage'][-1]>.95)
            assert abs(row['max_coverage']-np.max(trace['coverage']))<=1e-10
            assert abs(row['final_coverage']-trace['coverage'][-1])<=1e-10
            assert row['any_contact']==bool(np.any(trace['contact']>0))
            assert row['contact_steps']==int(np.sum(trace['contact']>0))
            assert row['rollout_seconds']>=row['policy_inference_seconds']>=0
            assert row['correction_selection_seconds']>=0
            decision=row['decision']
            assert row['intervention_attempted']==(decision is not None)
            if row['route']=='frozen':
                frozen_trace=trace
            if row['route'] in ('frozen','updated'):
                assert decision is None and not row['intervention_changed']
            else:
                assert frozen_trace is not None
                if not row['intervention_changed']:
                    assert trace['action'].shape==frozen_trace['action'].shape
                    assert maxdiff(trace['action'],frozen_trace['action'])<=1e-8
                    assert maxdiff(trace['full'],frozen_trace['full'])<=1e-8
                eligible=[]
                for t in trace['chunk_start']:
                    if t>268: continue
                    score=geo.overlap(geo.decode(trace['policy_observation'][t]))
                    if .90<=score<.95: eligible.append(int(t))
                if decision is None:
                    assert not eligible
                else:
                    step=decision['step']
                    assert eligible and eligible[0]==step and step in trace['chunk_start']
                    state=geo.decode(trace['policy_observation'][step])
                    assert maxdiff(state,decision['estimated_state'])<=1e-8
                    assert abs(geo.overlap(state)-decision['estimated_overlap'])<=1e-8
                    set_from_obs=candidates(np.asarray(decision['candidates'][0]),state)
                    assert maxdiff(set_from_obs,decision['candidates'])<=1e-8
                    index=decision['selected_index']
                    assert 0<=index<6
                    executed=np.asarray(decision['candidates'][index],np.float32).astype(np.float64)
                    assert maxdiff(executed,decision['executed_target'])<=1e-8
                    assert maxdiff(executed,trace['action'][step])<=1e-8
                    assert row['intervention_changed']==(index!=0)
                    assert maxdiff(trace['full'][:step+1],frozen_trace['full'][:step+1])<=1e-8
                    if step:
                        assert maxdiff(trace['action'][:step],frozen_trace['action'][:step])<=1e-8
                    assert maxdiff(np.asarray(decision['candidates'][0],np.float32),
                                   frozen_trace['action'][step])<=1e-8
                    if row['route']=='feedback':
                        assert index==1 and decision['model'] is None
                    else:
                        chosen,model=model_choice(geo,state,set_from_obs,tree,targets)
                        assert chosen==index and decision['model']['decision_reason']==model['decision_reason']
                        for key in ('predicted_delta','predicted_overlap','nearest_distance',
                                    'weighted_distance'):
                            assert maxdiff(decision['model'][key],model[key])<=1e-8
                        assert abs(decision['model']['predicted_advantage']-model['predicted_advantage'])<=1e-8
                    after=geo.decode(trace['policy_observation'][step+1])
                    actual=after[2:5]-state[2:5];actual[2]=wrap(actual[2])
                    assert maxdiff(actual,decision['observed_next_object_delta'])<=1e-8
                    assert abs(geo.overlap(after)-decision['observed_next_overlap'])<=1e-8
            result_rows.append(dict(seed=seed,route=row['route'],replay_max_drift=drift,
                                    intervention_attempted=row['intervention_attempted'],
                                    any_success=row['any_success'],
                                    one_step_overlap_gain_vs_frozen=(
                                        float(trace['coverage'][decision['step']+1]-
                                              frozen_trace['coverage'][decision['step']+1])
                                        if row['intervention_changed'] else None)))
        assert max(maxdiff(initials[0],x) for x in initials[1:])<=1e-8
    result=dict(status='passed',evaluation_sha256=digest(OUT/'evaluation.json'),
                checked_traces=len(result_rows),checked_seeds=len(SEEDS),
                max_replay_drift=max(r['replay_max_drift'] for r in result_rows),rows=result_rows)
    (OUT/'verification.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ('status','checked_traces','checked_seeds',
                                           'max_replay_drift')},indent=2),flush=True)


if __name__=='__main__':
    main()
