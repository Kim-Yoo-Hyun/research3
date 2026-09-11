"""Docker-only source/runtime inspection; no research score is produced."""
import ast
import hashlib
import json
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
from torch.distributions.normal import Normal
import gymnasium as gym
import mani_skill.envs
import h5py

torch.set_num_threads(1)

def policy(env, mode):
    source = Path('/opt/ManiSkill/examples/baselines/ppo/ppo.py').read_text()
    tree = ast.parse(source)
    nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))
             and n.name in ('layer_init', 'Agent')]
    assert len(nodes) == 2
    ns = dict(np=np, torch=torch, nn=nn, Normal=Normal)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), 'official_ppo_agent', 'exec'), ns)
    agent = ns['Agent'](env)
    path = Path('/inputs') / f'ppo_{mode}_ckpt.pt'
    expected = {'pd_joint_delta_pos':'78959417279892d73e4ed5930a6d8de8626a24eee0ec553dfc6af61391b0b356',
                'pd_ee_delta_pos':'0b17b5ed9690ccf83111d0f09af8d1599f69ee7ba0077e1aac48814ac78ce99c'}
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected[mode]
    agent.load_state_dict(torch.load(path, map_location='cpu', weights_only=True))
    agent.eval()
    return agent

def environment(mode='pd_joint_delta_pos'):
    return gym.make('PickCube-v1', num_envs=1, obs_mode='state', control_mode=mode,
                    sim_backend='physx_cpu', render_backend='gpu', reward_mode='none').unwrapped

if __name__ == '__main__':
    env = environment()
    obs, info = env.reset(seed=101)
    agent = policy(env, 'pd_joint_delta_pos')
    print('env', env.device, obs.shape, env.action_space, flush=True)
    with torch.no_grad():
        for _ in range(50):
            obs, _, _, _, info = env.step(agent.get_action(obs, deterministic=True))
    print('final', info, 'state keys', env.get_state_dict().keys(), flush=True)
    with h5py.File('/inputs/trajectory.h5') as f:
        print('demo_count', len(f), 'first_keys', list(f['traj_0'].keys()))
        print('demo_env_states', list(f['traj_0/env_states'].keys()))
    env.close()
