"""Constructed formula coverage; flags are stipulated, not physical grasp observations."""
import argparse
import itertools
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import torch
from mani_skill.envs.tasks.tabletop.pick_cube import PickCubeEnv
from task import RewardPickCube
from common import array

p=argparse.ArgumentParser(); p.add_argument('--output',required=True); a=p.parse_args()
cases=list(itertools.product([False,True],repeat=3))
gr,pl,st=[torch.tensor([c[j] for c in cases]) for j in range(3)]
cube=torch.zeros((8,3)); tcp=torch.arange(24).reshape(8,3).float()/100
qvel=torch.zeros((8,9)); qvel[~st,0]=0.3
qvel[:,-2:]=1 # excludes gripper joints from static reward/predicate
# Goal geometry agrees with placed flag.
goal=torch.zeros((8,3)); goal[~pl,0]=0.1
proxy=SimpleNamespace(cube=SimpleNamespace(pose=SimpleNamespace(p=cube)),
                      agent=SimpleNamespace(tcp=SimpleNamespace(pose=SimpleNamespace(p=tcp)), tcp_pose=SimpleNamespace(p=tcp),
                                            robot=SimpleNamespace(get_qvel=lambda:qvel)),
                      goal_site=SimpleNamespace(pose=SimpleNamespace(p=goal)),robot_uids='panda',
                      reward_calls=1,audit_samples=[])
fields=proxy.__dict__.copy()
proxy=RewardPickCube.__new__(RewardPickCube)
proxy.__dict__.update(fields)
proxy.compute_dense_reward=lambda **kw:PickCubeEnv.compute_dense_reward(proxy,**kw)
info=dict(is_grasped=gr,is_obj_placed=pl,is_robot_static=st,success=pl&st)
records=dict(cube=array(cube),tcp=array(tcp),goal=array(goal),qvel=array(qvel),
             **{k:array(v) for k,v in info.items()})
for variant in ['native','no_grasp','half']:
    proxy.reward_variant=variant
    records[variant]=array(RewardPickCube.compute_normalized_dense_reward(proxy,None,None,info))
np.savez_compressed(a.output,**records)
