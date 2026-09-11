"""CUDA/backend readiness, separate seed from frozen evaluation."""
import hashlib
import json
import shutil
from pathlib import Path
import gymnasium as gym
import torch
import mani_skill.envs

assert torch.cuda.is_available()
assert torch.cuda.get_device_capability()==(12,0)
x=torch.ones((16,16),device='cuda'); assert float((x@x).sum())==4096
env=gym.make('PickCube-v1',num_envs=8,obs_mode='state',control_mode='pd_joint_delta_pos',
             sim_backend='physx_cuda',reconfiguration_freq=1)
obs,_=env.reset(seed=901)
for _ in range(2): obs,*_=env.step(torch.zeros((8,8),device='cuda'))
assert torch.isfinite(obs).all()
result=dict(torch=torch.__version__,cuda=torch.version.cuda,device=torch.cuda.get_device_name(),
            architecture=torch.cuda.get_arch_list(),obs_shape=list(obs.shape),backend=str(env.unwrapped.device),cache={})
env.close()
for p in Path('/cache').rglob('*'):
    if p.is_file() and ('physx' in str(p).lower() or p.suffix=='.so'):
        result['cache'][str(p.relative_to('/cache'))]=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
out=Path('/outputs')
shutil.copyfile('/opt/dependencies.lock',out/'dependencies.lock')
shutil.copyfile('/opt/os-packages.lock',out/'os-packages.lock')
with (out/'runtime.json').open('x') as f: json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
