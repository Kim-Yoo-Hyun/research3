"""All numerical methods run inside the study Docker container."""
import argparse
import dataclasses
import hashlib
import json
from pathlib import Path
import shutil
import time
import numpy as np
import torch
from task import make_env, initialize, observe, labels, features, Controller, DT, HORIZON, STEPS, GOAL

torch.set_num_threads(1)


def serial(x):
    if isinstance(x,np.ndarray): return x.tolist()
    if isinstance(x,np.generic): return x.item()
    raise TypeError(type(x).__name__)


def write(path, data):
    path.write_text(json.dumps(data,indent=2,default=serial,allow_nan=False)+'\n')


def rollout(env, seed, moving, mode, predictor=None, jitter=0., steps=STEPS):
    meta=initialize(env,seed,moving)
    e=env.unwrapped
    policy=Controller('cv' if mode in ('history','action','fast') else mode,predictor)
    hold=1 if mode=='fast' else HORIZON
    o=observe(e);prev=o
    states=[o];truth=[labels(e)];actions=[];decisions=[];rows=[]
    rng=np.random.default_rng(seed+600000)
    for t in range(0,steps,hold):
        start=time.perf_counter()
        action,debug=policy.action(o,prev,hold)
        latency=time.perf_counter()-start
        if jitter:
            action[:2]=np.clip(action[:2]+rng.uniform(-jitter,jitter,2),-.25,.25)
        f=features(o,prev)
        pos=o['cube'][:3].copy()
        before=o
        for _ in range(min(hold,steps-t)):
            env.step(action)
            o=observe(e)
            states.append(o);truth.append(labels(e));actions.append(action.copy())
        rows.append(dict(features=f,action=action.copy(),delta=o['cube'][:3]-pos,t=t,phase=debug['phase']))
        decisions.append(dict(t=t,latency=latency,**debug))
        prev=before
    grasp=np.array([x['grasp'] for x in truth]);success=np.array([x['success'] for x in truth])
    meta.update(mode=mode,hold=hold,steps=steps,success=bool(np.all(success[-5:])),
                success_once=bool(success.any()),grasp_once=bool(grasp.any()),
                releases=int(np.sum(grasp[:-1]&~grasp[1:])),
                max_height=float(max(o['cube'][2] for o in states)),
                final_distance=truth[-1]['goal_distance'], decisions=len(decisions),
                mean_latency_ms=float(np.mean([d['latency'] for d in decisions])*1000))
    return meta,states,truth,actions,decisions,rows


def save_episode(out, key, result):
    meta,states,truth,actions,decisions,rows=result
    arrays={k:np.stack([s[k] for s in states]) for k in states[0]}
    arrays.update(actions=np.asarray(actions),grasp=np.array([x['grasp'] for x in truth]),
                  success=np.array([x['success'] for x in truth]),
                  contact_forces=np.stack([x['forces'] for x in truth]),
                  finger_directions=np.stack([x['directions'] for x in truth]),
                  features=np.array([x['features'] for x in rows]),
                  row_action=np.array([x['action'] for x in rows]),
                  delta=np.array([x['delta'] for x in rows]),
                  times=np.array([x['t'] for x in rows]),phase=np.array([x['phase'] for x in rows]))
    np.savez_compressed(out/(key+'.npz'),**arrays)
    meta['trace_sha256']=hashlib.sha256((out/(key+'.npz')).read_bytes()).hexdigest()
    write(out/(key+'.json'),dict(meta=meta,decisions=decisions))
    return meta


def runtime(env,out):
    e=env.unwrapped
    materials={}
    for name,actor in [('cube',e.cube),('table',e.table_scene.table)]:
        materials[name]=[dict(mass=float(body.mass) if hasattr(body,'mass') else None,
                             materials=[dict(static_friction=float(s.physical_material.static_friction),
                                             dynamic_friction=float(s.physical_material.dynamic_friction))
                                        for s in body.collision_shapes]) for body in actor._bodies]
    write(out/'runtime.json',dict(device=str(e.device),torch_version=torch.__version__,
        sim_config=dataclasses.asdict(e.sim_config),control_mode=e.control_mode,
        controllers={k:dataclasses.asdict(v.config) for k,v in e.agent.controller.controllers.items()},
        materials=materials,goal=GOAL,dt=DT,steps=STEPS,horizon=HORIZON,
        source_commit='a4a4f9272ad64b1564035874b605ceb687b63ed8',
        allowed_inputs=['cube pose','cube linear/angular velocity','TCP pose','qpos','qvel','past cube displacement'],
        evaluation_only=['contact forces','grasp flag','success flag']))
    for filename in ('installed.lock','os-packages.lock'):
        shutil.copy2(Path('/recipe')/filename,out/filename)


def run_develop(out):
    env=make_env();summary=[]
    for seed in (901,902):
        for moving in (False,True):
            for mode in ('servo','cv'):
                key=f'{seed}_{int(moving)}_{mode}'
                m=save_episode(out,key,rollout(env,seed,moving,mode))
                summary.append(m);print(json.dumps(m),flush=True)
    env.close();write(out/'development.json',summary)


def run_collect(out):
    env=make_env();summary=[]
    runtime(env,out)
    for seed in range(10000,10080):
        for moving in (False,True):
            mode='servo' if seed%2==0 else 'cv'
            key=f'{seed}_{int(moving)}_{mode}'
            assert not (out/(key+'.npz')).exists()
            m=save_episode(out,key,rollout(env,seed,moving,mode,jitter=0.10))
            summary.append(m)
        if seed%10==9:print('collected',len(summary),flush=True)
    env.close();write(out/'collection.json',summary)


def run_evaluate(out,model_dir):
    from model import Predictor
    models={mode:Predictor(model_dir/(mode+'.pt')) for mode in ('history','action')}
    env=make_env();summary=[]
    runtime(env,out)
    for seed in range(20000,20024):
        for moving in (False,True):
            for mode in ('servo','cv','history','action','fast'):
                key=f'{seed}_{int(moving)}_{mode}'
                assert not (out/(key+'.npz')).exists()
                m=save_episode(out,key,rollout(env,seed,moving,mode,models.get(mode)))
                summary.append(m)
        print('evaluated',len(summary),flush=True)
    env.close();write(out/'episodes.json',summary)


def main():
    p=argparse.ArgumentParser();p.add_argument('stage');p.add_argument('--attempt',required=True)
    p.add_argument('--data',default='train1');p.add_argument('--models',default='fit1')
    a=p.parse_args();out=Path('/output')/a.attempt;out.mkdir(exist_ok=True)
    if a.stage=='develop':run_develop(out)
    elif a.stage=='collect':run_collect(out)
    elif a.stage=='fit':
        from model import fit_models
        write(out/'fit.json',fit_models(Path('/output')/a.data,out))
    elif a.stage=='evaluate':run_evaluate(out,Path('/output')/a.models)
    elif a.stage=='verify':
        from verify import run_verify
        run_verify(Path('/output'),out,a.data,a.models)
    elif a.stage=='diagnose':
        from diagnose import run_diagnose
        run_diagnose(Path('/output'),out)
    else:raise ValueError(a.stage)


if __name__=='__main__':main()
