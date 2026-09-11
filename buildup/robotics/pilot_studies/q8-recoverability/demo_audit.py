"""No policy training: fixed public demonstration state-transition replay audit."""
import json
from pathlib import Path
import h5py
import torch
from audit import environment, error

def state(group,t):
    return {k:state(v,t) if isinstance(v,h5py.Group) else torch.as_tensor(v[t]).reshape(1,-1)
            for k,v in group.items()}

env=environment('pd_joint_pos')
rows=[]
meta=json.loads(Path('/inputs/trajectory.json').read_text())
with h5py.File('/inputs/trajectory.h5') as f:
    for index in range(3):
        tr=f[f'traj_{index}']
        for t in [0,5,20]:
            for rep in range(3):
                env.reset(seed=meta['episodes'][index]['episode_seed'],options={'reconfigure':True})
                s=state(tr['env_states'],t); expected=state(tr['env_states'],t+1)
                env.set_state_dict(s); env.agent.controller.reset(); env._elapsed_steps[:]=t
                before=error(env.get_state_dict(),s)
                env.step(torch.as_tensor(tr['actions'][t]).reshape(1,-1))
                after=error(env.get_state_dict(),expected)
                rows.append(dict(trajectory=index,anchor=t,repeat=rep,pre_state_error=before,
                                 next_state_error=after,passed=before<=1e-5 and after<=1e-5))
env.close()
with Path('/outputs/demo_audit.json').open('x') as out: json.dump(rows,out,indent=2)
print('demo transitions',sum(r['passed'] for r in rows),'/',len(rows), 'max error',max(r['next_state_error'] for r in rows))
