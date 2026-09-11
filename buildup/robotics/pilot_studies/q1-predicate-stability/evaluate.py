"""Unchanged official PPO entrypoint with a passive pre-auto-reset HDF5 recorder."""
import hashlib
import json
import runpy
import sys
from pathlib import Path
import gymnasium as gym
import h5py
import numpy as np
import torch
import mani_skill.envs

mode=sys.argv[1]
assert mode in ['pd_ee_delta_pos','pd_joint_delta_pos']
tag='ee' if mode=='pd_ee_delta_pos' else 'joint'
out=Path('/outputs')/tag
out.mkdir(exist_ok=False)
checkpoint=Path('/inputs')/f'ppo_{mode}_ckpt.pt'
expected={'ee':'0b17b5ed9690ccf83111d0f09af8d1599f69ee7ba0077e1aac48814ac78ce99c',
          'joint':'78959417279892d73e4ed5930a6d8de8626a24eee0ec553dfc6af61391b0b356'}
assert hashlib.sha256(checkpoint.read_bytes()).hexdigest()==expected[tag]
records=[]

def array(x): return x.detach().cpu().numpy().copy()

class Trace(gym.Wrapper):
    def __init__(self,env):
        super().__init__(env)
        self.resets=[]; self.snapshots=[]; self.actions=[]; self.official=[]; self.complete=False
        records.append(self)

    def snapshot(self,obs):
        e=self.unwrapped
        def tree(d): return {k:tree(v) if isinstance(v,dict) else array(v) for k,v in d.items()}
        return dict(state=tree(e.get_state_dict()),obs=array(obs),cube=array(e.cube.pose.p),
                    goal=array(e.goal_site.pose.p),qpos=array(e.agent.robot.qpos),qvel=array(e.agent.robot.qvel))

    def reset(self,**kwargs):
        obs,info=self.env.reset(**kwargs)
        self.resets.append(dict(seed=kwargs.get('seed'),after_steps=len(self.actions)))
        if not self.complete:
            assert not self.actions
            self.snapshots=[self.snapshot(obs)]
        return obs,info

    def step(self,action):
        assert not self.complete and len(self.snapshots)==len(self.actions)+1
        self.actions.append(array(action))
        obs,rew,term,trunc,info=self.env.step(action)
        self.snapshots.append(self.snapshot(obs))
        self.official.append({k:array(info[k]) for k in ['success','is_robot_static','is_obj_placed','is_grasped']})
        if len(self.actions)==50:
            assert np.all(array(trunc))
            self.complete=True
            self.save()
        return obs,rew,term,trunc,info

    def save(self):
        with h5py.File(out/'trajectory.h5','x') as f:
            def write(group,rows):
                for k in rows[0]:
                    if isinstance(rows[0][k],dict): write(group.create_group(k),[r[k] for r in rows])
                    else: group.create_dataset(k,data=np.stack([r[k] for r in rows]))
            write(f.create_group('snapshots'),self.snapshots)
            write(f.create_group('official'),self.official)
            f.create_dataset('actions',data=np.stack(self.actions))

original_make=gym.make
def make(*args,**kwargs):
    env=original_make(*args,**kwargs)
    return Trace(env) if kwargs.get('num_envs')==8 else env
gym.make=make
source=Path('/opt/ManiSkill/examples/baselines/ppo/ppo.py')
argv=[str(source),'--evaluate','--checkpoint',str(checkpoint),'--control-mode',mode,
      '--seed','1','--num-eval-envs','8','--num-eval-steps','50','--no-capture-video']
sys.argv=argv
runpy.run_path(str(source),run_name='__main__')
assert len(records)==1 and records[0].complete
initial_hashes=[]
for episode in range(8):
    digest=hashlib.sha256()
    for family,entries in sorted(records[0].snapshots[0]['state'].items()):
        for name,value in sorted(entries.items()):
            sample=np.ascontiguousarray(value[episode])
            digest.update(f'{family}/{name}:{sample.dtype}:{sample.shape}'.encode())
            digest.update(sample.tobytes())
    initial_hashes.append(digest.hexdigest())
metadata=dict(mode=mode,tag=tag,checkpoint_sha256=expected[tag],argv=argv,
              source_commit='a4a4f9272ad64b1564035874b605ceb687b63ed8',
              dataset_revision='d674485bbffdd533914e52d272fdda34c0515608',
              official_script_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
              resets=records[0].resets,steps=50,episodes=8,backend='physx_cuda',
              initial_state_sha256=initial_hashes,
              trajectory_sha256=hashlib.sha256((out/'trajectory.h5').read_bytes()).hexdigest())
with (out/'trajectory.json').open('x') as f: json.dump(metadata,f,indent=2)
print('Recorded',tag,50,'steps x',8,'episodes',flush=True)
