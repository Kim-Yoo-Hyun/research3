"""Frozen v1 feasibility checks. Run only through the Docker entrypoint."""
import copy
import json
import os
import time
from pathlib import Path
import numpy as np
import torch
from smoke import environment, policy
from mani_skill.utils.geometry.trimesh_utils import get_component_mesh
from mani_skill.utils.structs.pose import Pose

torch.set_num_threads(1)
torch.manual_seed(0)
torch.use_deterministic_algorithms(True)

def simple(x):
    if isinstance(x, torch.Tensor): return x.detach().cpu().tolist()
    if isinstance(x, np.ndarray): return x.tolist()
    if isinstance(x, dict): return {k:simple(v) for k,v in x.items()}
    if isinstance(x, (list, tuple)): return [simple(v) for v in x]
    return x

def error(a,b):
    if isinstance(a,dict):
        assert a.keys() == b.keys()
        return max([error(a[k], b[k]) for k in a] or [0.0])
    return float(torch.max(torch.abs(a-b))) if a.numel() else 0.0

@torch.no_grad()
def action(env, agent, obs):
    raw = agent.get_action(obs, deterministic=True)
    return raw.clamp(torch.as_tensor(env.single_action_space.low),
                     torch.as_tensor(env.single_action_space.high))

def measures(env):
    return dict(distance=float(torch.linalg.norm(env.cube.pose.p-env.goal_site.pose.p)),
                robot_speed=float(torch.max(torch.abs(env.agent.robot.qvel[:,:-2]))),
                success=bool(env.evaluate()['success'].item()),
                grasped=bool(env.evaluate()['is_grasped'].item()))

def nominal(env,agent,seed):
    obs,_=env.reset(seed=seed)
    states=[]; observations=[]; actions=[]; metrics=[]
    for t in range(51):
        states.append(copy.deepcopy(env.get_state_dict()))
        observations.append(obs.clone())
        metrics.append(measures(env))
        if t<50:
            a=action(env,agent,obs); actions.append(a.clone())
            obs,*_=env.step(a)
    return states,observations,actions,metrics

def prefix(env,seed,actions,t):
    obs,_=env.reset(seed=seed)
    for a in actions[:t]: obs,*_=env.step(a)
    return obs

def restore_checks(env,agent,seed,base):
    states,observations,actions,metrics=base
    rows=[]
    for t in [0,5,10,20,35]:
        for route in ['direct','reset_state','prefix']:
            for repeat in range(3):
                # Standardized stale history for direct-state tests.
                prefix(env,seed,actions,50)
                if route=='prefix': obs=prefix(env,seed,actions,t)
                else:
                    if route=='reset_state': env.reset(seed=seed)
                    env.set_state_dict(copy.deepcopy(states[t]))
                    if route=='reset_state':
                        if 'controller' in states[t]:
                            env.agent.set_controller_state(copy.deepcopy(states[t]['controller']))
                        env._elapsed_steps[:]=t
                    obs=env.get_obs()
                pre_state=error(env.get_state_dict(),states[t])
                pre_obs=error(obs,observations[t])
                a=action(env,agent,obs)
                action_error=error(a,actions[t])
                nxt,*_=env.step(a)
                row=dict(seed=seed,anchor=t,route=route,repeat=repeat,
                         pre_state_error=pre_state,pre_obs_error=pre_obs,
                         action_error=action_error,next_obs_error=error(nxt,observations[t+1]),
                         next_state_error=error(env.get_state_dict(),states[t+1]),
                         elapsed_steps=int(env.elapsed_steps.item()),
                         success=measures(env)['success'],reference_success=metrics[t+1]['success'])
                row['pass']=max(row[k] for k in ['pre_state_error','pre_obs_error','action_error',
                                                'next_obs_error','next_state_error'])<=1e-5
                rows.append(row)
    return rows

def bounds(env):
    cube=env.cube.get_first_collision_mesh().bounds
    links=[]
    for link in env.agent.robot.links:
        mesh=get_component_mesh(link._objs[0],to_world_frame=True)
        if mesh is not None: links.append((link.name,mesh.bounds))
    return cube,links

def validity(env):
    p=env.cube.pose.p[0].numpy()
    cube,links=bounds(env)
    # For a cube, the world z extent plus bottom plane bounds tilt conservatively.
    rotation=env.cube.pose.sp.to_transformation_matrix()[:3,:3]
    tilt=float(np.arccos(np.clip(rotation[2,2],-1,1)))
    overlap=[name for name,b in links if np.all(cube[1]+.001>=b[0]) and np.all(b[1]+.001>=cube[0])]
    q=env.agent.robot.qpos[0]; lim=env.agent.robot.get_qlimits()[0]
    checks=dict(spawn=bool(np.all(np.abs(p[:2])<=.1)),
                support=bool(abs(cube[0,2])<=.001 and tilt<.01),
                ungrasped=not bool(env.evaluate()['is_grasped'].item()),
                slow=bool(torch.linalg.norm(env.cube.linear_velocity)<.02 and
                          torch.linalg.norm(env.cube.angular_velocity)<.1),
                limits=bool(torch.all((q>=lim[:,0]) & (q<=lim[:,1]))),
                collision_free=not overlap)
    return dict(valid=all(checks.values()),checks=checks,cube_bounds=cube.tolist(),
                robot_bounds={n:b.tolist() for n,b in links},tilt=tilt,
                cube_position=p.tolist(),linear_speed=float(torch.linalg.norm(env.cube.linear_velocity)),
                angular_speed=float(torch.linalg.norm(env.cube.angular_velocity)),overlap=overlap)

def grid(env,agent,seed,base,restore_rows):
    states,observations,actions,metrics=base
    variants=[('zero',0.,0,0)]
    for r in [.01,.03,.06]:
        variants.extend([(axis,r,dx*r,dy*r) for axis,dx,dy in
                         [('x+',1,0),('x-',-1,0),('y+',0,1),('y-',0,-1)]])
    rows=[]
    for t in [0,5,10]:
        route_ok=all(r['pass'] for r in restore_rows if r['anchor']==t and r['route']=='prefix')
        for axis,r,dx,dy in variants:
            obs=prefix(env,seed,actions,t)
            anchor_validity=validity(env)
            before=copy.deepcopy(env.get_state_dict())
            p=env.cube.pose.p.clone(); p[:,0]+=dx; p[:,1]+=dy
            env.cube.set_pose(Pose.create_from_pq(p,env.cube.pose.q))
            v=validity(env)
            after=env.get_state_dict()
            # Invariance check on all saved fields except the intended cube x/y intervention.
            undo=copy.deepcopy(after)
            undo['actors']['cube'][:,:2]=before['actors']['cube'][:,:2]
            invariant=error(undo,before)
            row=dict(seed=seed,anchor=t,axis=axis,radius=r,dx=dx,dy=dy,
                     validity=v,anchor_validity=anchor_validity,restore_ok=route_ok,
                     invariant_error=invariant,nominal_success_once=any(m['success'] for m in metrics[t+1:]),
                     nominal_success_at_end=metrics[-1]['success'])
            row['admitted']=v['valid'] and anchor_validity['valid'] and route_ok and invariant<=1e-5
            if row['admitted']:
                obs=env.get_obs()
                row['action_drift']=float(torch.linalg.norm(action(env,agent,obs)-actions[t]))
                with torch.no_grad(): row['critic_value']=float(agent.get_value(obs))
                trajectory=[]
                for step in range(t+1,51):
                    obs,*_=env.step(action(env,agent,obs))
                    trajectory.append(dict(step=step,**measures(env)))
                row.update(trajectory=trajectory,success_once=any(m['success'] for m in trajectory),
                           success_at_end=trajectory[-1]['success'])
            rows.append(row)
    return rows

def main():
    start=time.monotonic()
    result=dict(repetition=os.environ.get('Q8_REPEAT','0'),restore=[],grid=[],nominal=[])
    for mode in ['pd_joint_delta_pos','pd_ee_delta_pos']:
        env=environment(mode); agent=policy(env,mode)
        for seed in range(101,109) if mode=='pd_joint_delta_pos' else [101,102]:
            base=nominal(env,agent,seed)
            result['nominal'].append(dict(mode=mode,seed=seed,metrics=base[3]))
            restore=restore_checks(env,agent,seed,base)
            result['restore'].extend([dict(mode=mode,**r) for r in restore])
            if mode=='pd_joint_delta_pos': result['grid'].extend(grid(env,agent,seed,base,restore))
            print(mode,seed,'restore',sum(r['pass'] for r in restore),'/',len(restore),flush=True)
        env.close()
    result['seconds']=time.monotonic()-start
    out=Path('/outputs')/f"audit_{result['repetition']}.json"
    with out.open('x') as f: json.dump(result,f,allow_nan=False)
    print('completed',out,'seconds',result['seconds'],flush=True)

if __name__=='__main__': main()
