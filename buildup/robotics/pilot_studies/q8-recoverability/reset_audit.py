"""Isolate the field behind v1 physical-state/observation disagreement."""
import copy
import json
from pathlib import Path
import torch
from audit import environment, policy, action, error

env=environment(); agent=policy(env,'pd_joint_delta_pos')
obs,_=env.reset(seed=101,options={'reconfigure':True})
fresh_obs=obs.clone(); fresh_state=copy.deepcopy(env.get_state_dict())
fresh_grasp=bool(env.evaluate()['is_grasped'].item())
for _ in range(50): obs,*_=env.step(action(env,agent,obs))
warm_obs,_=env.reset(seed=101)
warm_grasp=bool(env.evaluate()['is_grasped'].item())
warm_state_error=error(env.get_state_dict(),fresh_state)
cold_obs,_=env.reset(seed=101,options={'reconfigure':True})
result=dict(fresh_grasp=fresh_grasp,warm_reset_grasp=warm_grasp,
    cold_reset_grasp=bool(env.evaluate()['is_grasped'].item()),
    warm_physical_state_error=warm_state_error,
    changed_observation_indices=torch.where((warm_obs-fresh_obs).abs()[0]>1e-5)[0].tolist(),
    warm_observation_error=error(warm_obs,fresh_obs),cold_observation_error=error(cold_obs,fresh_obs))
env.close()
with Path('/outputs/reset_audit.json').open('x') as f: json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
