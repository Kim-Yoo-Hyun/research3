"""Paired fresh-seed Push-T comparison using identical live 20D keypoint inputs."""
import collections
import hashlib
import json
from pathlib import Path
import time

import dill
import hydra
import numpy as np
from omegaconf import OmegaConf
from scipy.spatial import cKDTree
import torch

from diffusion_policy.env.pusht.pusht_keypoints_env import PushTKeypointsEnv
from dp_evaluate import coverage,full,state5
from dp_observation import ObservationGeometry,feedback_target
from repeat_action_model import predict,wrap

ROOT=Path('/output')
OUT=ROOT/'compare1'
CHECKPOINT=Path('/checkpoint/model.ckpt')
MODEL=Path('/previous/fit_model1/model.npz')
UPDATED=ROOT/'finetune1/checkpoint.pt'
SEEDS=tuple(range(49100,49116))
ROUTES=('frozen','feedback','prediction','updated')
MAX_STEPS=300
NEAR_P90=.4234414344


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):
            h.update(chunk)
    return h.hexdigest()


def candidates(original,state):
    shifts=((40.,0.),(-40.,0.),(0.,40.),(0.,-40.))
    return np.vstack([original,feedback_target(state),
                     *(np.clip(original+np.asarray(shift),0.,512.) for shift in shifts)])


def model_choice(geo,state,actions,tree,targets):
    batch_state=np.repeat(state[None],len(actions),axis=0)
    delta,nearest,weighted=predict(tree,targets,batch_state,actions)
    predicted=batch_state.copy()
    predicted[:,2:4]+=delta[:,:2]
    predicted[:,4]=np.mod(predicted[:,4]+delta[:,2],2*np.pi)
    predicted_overlap=np.asarray([geo.overlap(x) for x in predicted])
    best=int(np.argmax(predicted_overlap))
    advantage=float(predicted_overlap[best]-predicted_overlap[0])
    chosen=best if advantage>=.005 and nearest[best]<=NEAR_P90 else 0
    reason=('selected' if chosen else
            ('no_predicted_gain' if advantage<.005 else 'out_of_distribution'))
    return chosen,dict(predicted_delta=delta.tolist(),
                       predicted_overlap=predicted_overlap.tolist(),
                       nearest_distance=nearest.tolist(),
                       weighted_distance=weighted.tolist(),
                       best_index=best,predicted_advantage=advantage,
                       selected_index=chosen,decision_reason=reason)


def load_policies():
    OmegaConf.register_new_resolver('eval',eval,replace=True)
    payload=torch.load(CHECKPOINT,map_location='cpu',pickle_module=dill,weights_only=False)
    policy=hydra.utils.instantiate(payload['cfg'].policy)
    policy.load_state_dict(payload['state_dicts']['ema_model'],strict=True)
    policy.to('cuda:0').eval()
    updated=hydra.utils.instantiate(payload['cfg'].policy)
    checkpoint=torch.load(UPDATED,map_location='cpu',weights_only=False)
    assert checkpoint['source_checkpoint_sha256']==digest(CHECKPOINT)
    assert checkpoint['data_sha256']==digest(ROOT/'traincontract1/dataset.npz')
    updated.load_state_dict(checkpoint['policy_state_dict'],strict=True)
    updated.to('cuda:0').eval()
    return policy,updated


def rollout(seed,route,policy,geo,tree,targets):
    env=PushTKeypointsEnv(legacy=True,keypoint_visible_rate=1.0,
                           agent_keypoints=False,render_action=False)
    try:
        env.seed(seed)
        obs=env.reset()
        history=collections.deque([obs],maxlen=2)
        torch.manual_seed(seed);torch.cuda.manual_seed_all(seed)
        policy.reset()
        states=[state5(env)];policy_obs=[np.asarray(obs,np.float64)]
        physical=[full(env)];covers=[coverage(env)]
        contacts=[];actions=[];chunks=[]
        attempted=False;decision=None
        policy_seconds=0.;selection_seconds=0.
        started=time.perf_counter()
        done=False
        while len(actions)<MAX_STEPS and not done:
            recent=list(history)
            if len(recent)==1: recent=[recent[0],recent[0]]
            raw=np.stack(recent,axis=0)
            input_obs=raw[:,:20].astype(np.float32)
            input_mask=raw[:,20:]>.5
            assert input_obs.shape==input_mask.shape==(2,20) and input_mask.all()
            t0=time.perf_counter()
            with torch.inference_mode():
                result=policy.predict_action({'obs':torch.from_numpy(input_obs[None]).cuda(),
                                              'obs_mask':torch.from_numpy(input_mask[None]).cuda()})
            plan=result['action'][0].detach().cpu().numpy()
            torch.cuda.synchronize()
            policy_seconds+=time.perf_counter()-t0
            assert plan.shape==(8,2) and np.isfinite(plan).all()
            chunks.append(len(actions))
            if route in ('feedback','prediction') and not attempted and len(actions)<=268:
                t0=time.perf_counter()
                estimated=geo.decode(obs)
                estimated_overlap=geo.overlap(estimated)
                if .90<=estimated_overlap<.95:
                    attempted=True
                    original=np.asarray(plan[0],np.float64).copy()
                    action_set=candidates(original,estimated)
                    if route=='feedback':
                        selected=1;model_record=None
                    else:
                        selected,model_record=model_choice(geo,estimated,action_set,tree,targets)
                    target=action_set[selected].astype(np.float32)
                    plan[0]=target
                    decision=dict(step=len(actions),estimated_state=estimated.tolist(),
                                  estimated_overlap=float(estimated_overlap),
                                  candidates=action_set.tolist(),selected_index=selected,
                                  executed_target=target.astype(np.float64).tolist(),
                                  model=model_record)
                selection_seconds+=time.perf_counter()-t0
            for target in plan:
                if len(actions)>=MAX_STEPS: break
                obs,_,done,info=env.step(np.asarray(target,np.float64))
                history.append(obs)
                states.append(state5(env));policy_obs.append(np.asarray(obs,np.float64))
                physical.append(full(env));covers.append(coverage(env))
                contacts.append(int(info['n_contacts']))
                actions.append(np.asarray(target,np.float64))
                if decision is not None and len(actions)==decision['step']+1:
                    after=geo.decode(obs)
                    before=np.asarray(decision['estimated_state'])
                    actual=after[2:5]-before[2:5]
                    actual[2]=wrap(actual[2])
                    decision['observed_next_object_delta']=actual.tolist()
                    decision['observed_next_overlap']=float(geo.overlap(after))
                if done: break
        elapsed=time.perf_counter()-started
        trace=dict(observation=np.asarray(states),policy_observation=np.asarray(policy_obs),
                   full=np.asarray(physical),coverage=np.asarray(covers),
                   contact=np.asarray(contacts),action=np.asarray(actions),
                   chunk_start=np.asarray(chunks,np.int64))
        return trace,decision,elapsed,policy_seconds,selection_seconds
    finally:
        env.close()


def main():
    OUT.mkdir(exist_ok=False)
    torch.set_num_threads(4)
    fit=json.loads((ROOT/'finetune1/fit.json').read_text())
    dataset=json.loads((ROOT/'traincontract1/assessment.json').read_text())
    original=json.loads((ROOT/'observation1/assessment.json').read_text())
    resolved=json.loads((ROOT/'observation2/assessment.json').read_text())
    assert fit['status']=='completed' and dataset['status']=='passed'
    assert original['status']==resolved['status']=='incompatible'
    assert fit['checkpoint_sha256']==digest(UPDATED)
    model_fit=json.loads(Path('/previous/fit_model1/fit.json').read_text())
    assert model_fit['checkpoint_sha256']==digest(MODEL)
    assert model_fit['source_zip_sha256']==dataset['source_zip_sha256']
    with np.load(MODEL,allow_pickle=False) as saved:
        x=saved['features'].copy();y=saved['targets'].copy();train_indices=saved['train_indices'].copy()
    assert len(x)==len(y)==len(train_indices)==19378
    tree=cKDTree(x)
    geo=ObservationGeometry()
    frozen,updated=load_policies()
    rows=[]
    for seed in SEEDS:
        initials=[]
        for route in ROUTES:
            policy=updated if route=='updated' else frozen
            trace,decision,elapsed,policy_seconds,selection_seconds=rollout(
                seed,route,policy,geo,tree,y)
            path=OUT/f'{seed}_{route}.npz'
            np.savez_compressed(path,**trace)
            initials.append(trace['full'][0])
            row=dict(seed=seed,route=route,steps=len(trace['action']),
                     any_success=bool(np.any(trace['coverage']>.95)),
                     final_success=bool(trace['coverage'][-1]>.95),
                     max_coverage=float(np.max(trace['coverage'])),
                     final_coverage=float(trace['coverage'][-1]),
                     any_contact=bool(np.any(trace['contact']>0)),
                     contact_steps=int(np.sum(trace['contact']>0)),
                     intervention_attempted=decision is not None,
                     intervention_changed=bool(decision and decision['selected_index']!=0),
                     decision=decision,rollout_seconds=elapsed,
                     policy_inference_seconds=policy_seconds,
                     correction_selection_seconds=selection_seconds,
                     trace=path.name,sha256=digest(path))
            rows.append(row)
            print(json.dumps({k:row[k] for k in ('seed','route','any_success','max_coverage',
                               'intervention_attempted','intervention_changed',
                               'rollout_seconds')}),flush=True)
        assert max(float(np.max(np.abs(initials[0]-x))) for x in initials[1:])<=1e-8
    result=dict(status='completed',source_commit='5ba07ac6661db573af695b419a7947ecb704690f',
                source_checkpoint_sha256=digest(CHECKPOINT),
                updated_checkpoint_sha256=digest(UPDATED),
                dataset_sha256=digest(ROOT/'traincontract1/dataset.npz'),
                transition_model_sha256=digest(MODEL),
                input_audit_sha256=digest(ROOT/'observation2/assessment.json'),
                policy_input='identical 2x20 live keypoint+agent XY, all masks 1',
                online_correction='one first-target change at first 0.90<=estimated overlap<0.95 chunk, step<=268',
                candidate_set=['original','feedback','x+40','x-40','y+40','y-40'],
                prediction_rule=dict(overlap_advantage_min=.005,nearest_distance_max=NEAR_P90),
                training_episodes=[0,159],validation_episodes=[160,179],
                seeds=list(SEEDS),horizon=MAX_STEPS,native_success='coverage >0.95',
                device='cuda:0',rows=rows)
    (OUT/'evaluation.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')


if __name__=='__main__':
    main()
