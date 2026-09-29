"""Execute pinned official PPO with explicit environment/reward and recording-only hooks."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import task
from common import SOURCE, SOURCE_HASH, sha, write_json

p=argparse.ArgumentParser()
p.add_argument('--variant',required=True,choices=['native','no_grasp','half'])
p.add_argument('--seed',type=int,required=True)
p.add_argument('--updates',type=int,default=195)
a=p.parse_args()
assert sha(SOURCE)==SOURCE_HASH
source=SOURCE.read_text()
replacements=[
('env_kwargs = dict(obs_mode="state", render_mode="rgb_array", sim_backend="physx_cuda")',
 'env_kwargs = dict(obs_mode="state", render_mode="rgb_array", sim_backend="physx_cuda", reward_mode="normalized_dense", reward_variant='+repr(a.variant)+')'),
('    optimizer = optim.Adam(agent.parameters(), lr=args.learning_rate, eps=1e-5)',
 '    optimizer = optim.Adam(agent.parameters(), lr=args.learning_rate, eps=1e-5)\n    from record import begin, after_update\n    begin(args, envs, agent)'),
('        update_time = time.time() - update_time',
 '        update_time = time.time() - update_time\n        after_update(args, envs, agent, optimizer, iteration, global_step, rollout_time, update_time)'),
]
for old,new in replacements:
    assert source.count(old)==1,old
    source=source.replace(old,new)
Path('executed_ppo.py').write_text(source)
write_json('adapter.json',dict(source_sha256=SOURCE_HASH,executed_sha256=sha('executed_ppo.py'),
                             replacements=replacements,variant=a.variant,seed=a.seed,updates=a.updates))
sys.argv=[str(SOURCE),'--env-id=Q15PickCube-v1','--num-envs=1024','--num-steps=50',
          '--update-epochs=8','--num-minibatches=32',f'--total-timesteps={a.updates*51200}',
          f'--seed={a.seed}','--exp-name=fit','--no-capture-video','--no-save-model','--no-track']
exec(compile(source,str(SOURCE),'exec'),{'__name__':'__main__','__file__':str(SOURCE)})
