"""Container-only study helpers. No installation or runtime on the host."""
import dataclasses
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np
import torch

SOURCE = Path('/opt/ManiSkill/examples/baselines/ppo/ppo.py')
SOURCE_HASH = '3fa4818861d428480244aae889bc679b2c8e89b59d6289014003c266a84dbab0'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def array(x):
    return x.detach().cpu().numpy().copy()

def serialize(x):
    if isinstance(x, np.ndarray): return x.tolist()
    if isinstance(x, np.generic): return x.item()
    if isinstance(x, torch.Tensor): return array(x).tolist()
    if isinstance(x, Path): return str(x)
    raise TypeError(type(x).__name__)

def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, default=serialize, allow_nan=False)+'\n')

def official_ppo():
    assert sha(SOURCE) == SOURCE_HASH
    spec = importlib.util.spec_from_file_location('pinned_ppo', SOURCE)
    module = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def body_materials(body):
    result=[]
    for shape in body.collision_shapes:
        m=shape.physical_material
        item={k:float(getattr(m,k)) for k in ['static_friction','dynamic_friction','restitution']}
        for key in ['friction_combine_mode','restitution_combine_mode']:
            item[key]=str(getattr(m,key)) if hasattr(m,key) else 'not exposed by SAPIEN 3.0.2'
        result.append(item)
    return result

def physical(e):
    cubes=[]
    for b in e.cube._bodies:
        cubes.append(dict(mass=float(b.mass), inertia=np.asarray(b.inertia).tolist(),
                          com_pose=np.concatenate([b.cmass_local_pose.p,b.cmass_local_pose.q]).tolist(),
                          materials=body_materials(b)))
    links={}
    for link in e.agent.robot.links:
        if link.name in ('panda_leftfinger','panda_rightfinger'):
            links[link.name]=[body_materials(b) for b in link._bodies]
    table=[body_materials(b) for b in e.table_scene.table._bodies]
    return dict(cube=cubes,fingers=links,table=table)

def configuration(e):
    return dict(sim_config=dataclasses.asdict(e.sim_config),
                controllers={k:dataclasses.asdict(c.config) for k,c in e.agent.controller.controllers.items()},
                physical=physical(e), cube_half_size=float(e.cube_half_size),goal_threshold=float(e.goal_thresh),
                device=str(e.device),gpu=torch.cuda.get_device_name(),torch_version=torch.__version__,
                source_commit='a4a4f9272ad64b1564035874b605ceb687b63ed8')

def snapshot(e, obs):
    return dict(obs=array(obs),qpos=array(e.agent.robot.qpos),qvel=array(e.agent.robot.qvel),
                cube_pose=array(e.cube.pose.raw_pose),cube_velocity=array(e.cube.linear_velocity),
                cube_angular_velocity=array(e.cube.angular_velocity),goal=array(e.goal_site.pose.p),
                tcp_pose=array(e.agent.tcp.pose.raw_pose))
