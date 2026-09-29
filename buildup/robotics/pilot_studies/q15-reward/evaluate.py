"""One fresh-process evaluation condition, with all 50 post-step states retained."""
import argparse
import random
import time
from pathlib import Path
from types import SimpleNamespace
import gymnasium as gym
import numpy as np
import torch
import task
from common import array, configuration, official_ppo, sha, snapshot, write_json

p=argparse.ArgumentParser()
p.add_argument('--output',required=True)
p.add_argument('--checkpoint')
p.add_argument('--variant',default='native')
p.add_argument('--density',type=float,default=1)
p.add_argument('--friction',type=float,default=1)
p.add_argument('--official',action='store_true')
a=p.parse_args()
started=time.monotonic()
random.seed(2026091901); np.random.seed(2026091901); torch.manual_seed(2026091901)
kwargs=dict(num_envs=32,obs_mode='state',control_mode='pd_joint_delta_pos',sim_backend='physx_cuda',
            reward_mode='normalized_dense',render_mode=None)
if not a.official:
    kwargs.update(reward_variant=a.variant,density_multiplier=a.density,friction_multiplier=a.friction)
env=gym.make('PickCube-v1' if a.official else 'Q15PickCube-v1',**kwargs)
e=env.unwrapped
obs,_=env.reset(seed=2026091901)
config=configuration(e)
assert config['sim_config']['sim_freq']==100 and config['sim_config']['control_freq']==20
assert float(e.scene.px.timestep)==np.float32(0.01)
if a.checkpoint:
    policy=official_ppo().Agent(SimpleNamespace(single_observation_space=e.single_observation_space,
                                              single_action_space=e.single_action_space)).to(e.device)
    policy.load_state_dict(torch.load(a.checkpoint,map_location=e.device,weights_only=True))
    policy.eval()
records={k:[v] for k,v in snapshot(e,obs).items()}
physical_steps=0
native_after=e._after_simulation_step

def after():
    global physical_steps
    physical_steps+=1
    native_after()
e._after_simulation_step=after
with torch.inference_mode():
    for step in range(50):
        if a.checkpoint:
            action=policy.get_action(obs,deterministic=True)
        else:
            action=torch.sin(torch.arange(8,device=e.device).float()+step/10).repeat(32,1)*0.2
        # Match the action clipping used in official training; native controller also clips its normalized action.
        action=torch.clamp(action,torch.as_tensor(e.single_action_space.low,device=e.device),
                           torch.as_tensor(e.single_action_space.high,device=e.device))
        obs,reward,terminated,truncated,info=env.step(action)
        for k,v in snapshot(e,obs).items(): records[k].append(v)
        for k in ['success','is_obj_placed','is_robot_static','is_grasped']:
            records.setdefault(k,[]).append(array(info[k]))
        for k,v in dict(action=action,reward=reward,terminated=terminated,truncated=truncated,
                        elapsed_steps=e.elapsed_steps).items():
            records.setdefault(k,[]).append(array(v))
        assert physical_steps==(step+1)*5
out=Path(a.output)
assert not Path(str(out)+'.npz').exists()
np.savez_compressed(Path(str(out)+'.npz'),**{k:np.stack(v) for k,v in records.items()})
write_json(Path(str(out)+'.json'),dict(config=config,variant=a.variant,density=a.density,friction=a.friction,
           official=a.official,seed=2026091901,num_envs=32,steps=50,physical_steps=physical_steps,
           checkpoint=a.checkpoint,checkpoint_sha256=sha(a.checkpoint) if a.checkpoint else None,
           trace_sha256=sha(Path(str(out)+'.npz')),seconds=time.monotonic()-started,
           cuda_peak_bytes=torch.cuda.max_memory_allocated()))
print(out.name,'end',array(info['success']).sum(),'once',np.stack(records['success']).any(axis=0).sum(),flush=True)
env.close()
