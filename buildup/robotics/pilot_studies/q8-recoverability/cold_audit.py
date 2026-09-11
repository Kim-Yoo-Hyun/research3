"""V2: reconstruct scene before every nominal start/action-prefix replay."""
import copy
import json
import os
import time
from pathlib import Path
import audit as a

def main():
    start=time.monotonic()
    result=dict(repetition=os.environ.get('Q8_REPEAT','0'),restore=[],grid=[],nominal=[],zero_controls=[])
    for mode in ['pd_joint_delta_pos','pd_ee_delta_pos']:
        env=a.environment(mode)
        reset=env.reset
        def cold_reset(seed=None): return reset(seed=seed,options={'reconfigure':True})
        env.reset=cold_reset
        agent=a.policy(env,mode)
        for seed in range(101,109) if mode=='pd_joint_delta_pos' else [101,102]:
            base=a.nominal(env,agent,seed)
            states,observations,actions,metrics=base
            result['nominal'].append(dict(mode=mode,seed=seed,metrics=metrics))
            restore=[]
            for t in [0,5,10,20,35]:
                for repeat in range(3):
                    obs=a.prefix(env,seed,actions,t)
                    state_error=a.error(env.get_state_dict(),states[t]); obs_error=a.error(obs,observations[t])
                    act=a.action(env,agent,obs)
                    nxt,*_=env.step(act)
                    row=dict(mode=mode,seed=seed,anchor=t,repeat=repeat,route='prefix',
                        pre_state_error=state_error,pre_obs_error=obs_error,
                        action_error=a.error(act,actions[t]),next_obs_error=a.error(nxt,observations[t+1]),
                        next_state_error=a.error(env.get_state_dict(),states[t+1]),
                        success=a.measures(env)['success'],reference_success=metrics[t+1]['success'])
                    row['pass']=max(row[k] for k in ['pre_state_error','pre_obs_error','action_error','next_obs_error','next_state_error'])<=1e-5
                    restore.append(row)
            result['restore'].extend(restore)
            if mode=='pd_joint_delta_pos':
                rows=a.grid(env,agent,seed,base,restore)
                result['grid'].extend(rows)
                for row in rows:
                    if row['axis']=='zero' and row['admitted']:
                        dif=max(max(abs(m['distance']-n['distance']),abs(m['robot_speed']-n['robot_speed']))
                            for m,n in zip(row['trajectory'],metrics[row['anchor']+1:]))
                        result['zero_controls'].append(dict(seed=seed,anchor=row['anchor'],error=dif,
                            label_equal=row['success_once']==row['nominal_success_once'] and
                                        row['success_at_end']==row['nominal_success_at_end']))
            print(mode,seed,'cold restore',sum(r['pass'] for r in restore),'/',len(restore),flush=True)
        env.close()
    result['seconds']=time.monotonic()-start
    out=Path('/outputs')/f"cold_{result['repetition']}.json"
    with out.open('x') as f: json.dump(result,f,allow_nan=False)
    print('completed',out,'seconds',result['seconds'],flush=True)

if __name__=='__main__': main()
