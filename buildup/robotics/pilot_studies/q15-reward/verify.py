"""Independent CPU reconstruction. Does not import the reward, PPO or evaluation adapters."""
import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np

def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v): Path(p).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')

def check_reward(f,variant,observed):
    x={k:np.asarray(v) for k,v in f.items()}
    reach=1-np.tanh(5*np.linalg.norm(x['cube']-x['tcp'],axis=-1))
    place=1-np.tanh(5*np.linalg.norm(x['cube']-x['goal'],axis=-1))
    static=1-np.tanh(5*np.linalg.norm(x['qvel'][...,:7],axis=-1))
    r=reach+x['is_grasped'].astype(float)*(1+place)+static*x['is_obj_placed']
    r=np.where(x['success'],5,r)/5
    if variant=='no_grasp': r=r-0.2*x['is_grasped']*(~x['success'])
    if variant=='half': r=r*0.5
    assert np.allclose(r,observed,atol=3e-7,rtol=1e-6),(variant,float(np.max(np.abs(r-observed))))
    return int(r.size)

def check_materials(config,ref,density,friction):
    assert config['sim_config']==ref['sim_config']
    assert config['controllers']==ref['controllers']
    assert config['cube_half_size']==ref['cube_half_size']
    assert config['goal_threshold']==ref['goal_threshold']
    p,r=config['physical'],ref['physical']
    assert p['fingers']==r['fingers'] and p['table']==r['table']
    assert set(p['fingers'])=={'panda_leftfinger','panda_rightfinger'}
    for b,rb in zip(p['cube'],r['cube']):
        assert np.isclose(b['mass'],rb['mass']*density,atol=1e-8,rtol=1e-6)
        assert np.allclose(b['inertia'],np.array(rb['inertia'])*density,atol=1e-10,rtol=1e-6)
        assert b['com_pose']==rb['com_pose']
        for m,rm in zip(b['materials'],rb['materials']):
            for key in ['static_friction','dynamic_friction']:
                assert np.isclose(m[key],rm[key]*friction,rtol=1e-6)
            for key in ['restitution','friction_combine_mode','restitution_combine_mode']:
                assert m[key]==rm[key]

def main():
    p=argparse.ArgumentParser(); p.add_argument('--attempt',required=True); a=p.parse_args()
    out=Path('/output')/a.attempt
    import shutil
    archive=out/'verification_source'
    archive.mkdir(exist_ok=True)
    for name in ['verify.py','analyze.py']:
        source=Path('/study')/name
        target=archive/name
        if target.exists(): assert target.read_bytes()==source.read_bytes(), 'Preserve prior verifier before editing'
        else: shutil.copyfile(source,target)
    status=json.loads((out/'run_status.json').read_text())
    assert status['status']=='completed'
    assert len(status['training'])==9 and len(status['evaluation'])==72
    reference=None; refmeta=None; rows=[]; checks={'label_elements':0,'reward_elements':0,'initial_arrays':0,'training_reward_elements':0,'old_l2_static_disagreements_training':0,'old_l2_static_disagreements_evaluation':0,'legacy_fractional_filenames':0}
    fitmeta={}
    for v,s in itertools.product(['native','no_grasp','half'],[101,202,303]):
        fit=out/'fits'/f'{v}_{s}'
        cfg=json.loads((fit/'config.json').read_text())
        args=cfg['args']; fitmeta[v,s]=cfg
        assert args['seed']==s and args['num_iterations']==195 and args['num_envs']==1024
        assert args['num_steps']==50 and args['update_epochs']==8 and args['num_minibatches']==32
        assert args['gamma']==0.8 and args['gae_lambda']==0.9 and args['learning_rate']==3e-4
        assert args['checkpoint'] is None and not args['track'] and not args['capture_video']
        train=[json.loads(l) for l in (fit/'training.jsonl').read_text().splitlines()]
        assert [r['update'] for r in train]==list(range(1,196))
        assert [r['transitions'] for r in train]==[i*51200 for i in range(1,196)]
        assert train[-1]['reward_calls']==9750
        for iteration in [97,195]:
            c=json.loads((fit/f'checkpoint_{iteration}.json').read_text())
            assert c['reward_variant']==v and c['seed']==s
            assert c['sha256']==digest(fit/f'checkpoint_{iteration}.pt')
            assert c['transitions']==iteration*51200 and c['save_timing']=='after optimizer update'
        audits=json.loads((fit/'reward_audit.json').read_text())
        assert [r['call'] for r in audits]==[1,2500,4850,9750]
        for f in audits:
            f={k:np.asarray(val) for k,val in f.items()}
            check_reward(f,'native',f['native'])
            checks['training_reward_elements']+=check_reward(f,v,f['reward'])
            placed=np.linalg.norm(f['cube']-f['goal'],axis=-1)<=0.025
            static=np.max(np.abs(f['qvel'][...,:7]),axis=-1)<=0.2
            checks['old_l2_static_disagreements_training']+=int(np.count_nonzero(static!=(np.linalg.norm(f['qvel'][...,:7],axis=-1)<=0.2)))
            assert np.array_equal(placed,f['is_obj_placed']) and np.array_equal(static,f['is_robot_static'])
            assert np.array_equal(placed&static,f['success'])
    first_env=fitmeta['native',101]['environment']
    for cfg in fitmeta.values():
        assert cfg['environment']==first_env
    for seed in [101,202,303]:
        assert len({fitmeta[v,seed]['initial_model_sha256'] for v in ['native','no_grasp','half']})==1
    conditions=[(1.,1.),(2.,1.),(1.,0.5),(2.,0.5)]
    used_metadata=set()
    for v,s,it,(density,friction) in itertools.product(['native','no_grasp','half'],[101,202,303],[97,195],conditions):
        name=f'{v}_{s}_u{it}_d{density:g}_f{friction:g}'
        metadata=out/'evaluation'/f'{name}.json'
        trace=out/'evaluation'/f'{name}.npz'
        if not metadata.exists():
            # Original v1 writer replaced the decimal .5 as a suffix. Preserve those raw files.
            assert friction==0.5
            base=out/'evaluation'/name
            metadata=base.with_suffix('.json'); trace=base.with_suffix('.npz')
            checks['legacy_fractional_filenames']+=1
        assert metadata not in used_metadata
        used_metadata.add(metadata)
        m=json.loads(metadata.read_text())
        d=dict(np.load(trace,allow_pickle=False))
        assert m['trace_sha256']==digest(trace)
        assert m['checkpoint_sha256']==digest(out/'fits'/f'{v}_{s}'/f'checkpoint_{it}.pt')
        assert m['variant']==v and m['density']==density and m['friction']==friction
        assert m['seed']==2026091901 and m['num_envs']==32 and m['steps']==50 and m['physical_steps']==250
        assert d['qpos'].shape==(51,32,9) and d['success'].shape==(50,32)
        assert np.isfinite(d['action']).all() and np.isfinite(d['reward']).all()
        assert np.array_equal(d['elapsed_steps'],np.repeat(np.arange(1,51)[:,None],32,axis=1))
        assert not d['truncated'][:-1].any() and d['truncated'][-1].all()
        if reference is None: reference=d; refmeta=m
        check_materials(m['config'],refmeta['config'],density,friction)
        for key in ['obs','qpos','qvel','cube_pose','cube_velocity','cube_angular_velocity','goal','tcp_pose']:
            assert np.array_equal(d[key][0],reference[key][0]),(name,key)
            assert np.isfinite(d[key]).all()
            checks['initial_arrays']+=1
        distance=np.linalg.norm(d['cube_pose'][1:,:,:3]-d['goal'][1:],axis=-1)
        speed=np.linalg.norm(d['qvel'][1:,:,:7],axis=-1)
        max_speed=np.max(np.abs(d['qvel'][1:,:,:7]),axis=-1)
        placed=distance<=0.025; static=max_speed<=0.2; success=placed&static
        checks['old_l2_static_disagreements_evaluation']+=int(np.count_nonzero(static!=(speed<=0.2)))
        for key,value in [('is_obj_placed',placed),('is_robot_static',static),('success',success)]:
            assert np.array_equal(value,d[key]),(name,key)
            checks['label_elements']+=value.size
        f={k:d[k] for k in ['is_grasped','is_obj_placed','success']}
        f.update(cube=d['cube_pose'][1:,:,:3],tcp=d['tcp_pose'][1:,:,:3],goal=d['goal'][1:],qvel=d['qvel'][1:])
        checks['reward_elements']+=check_reward(f,v,d['reward'])
        for i in range(32):
            ever=bool(success[:,i].any()); end=bool(success[-1,i]); events=np.flatnonzero(success[:,i])
            failure='success' if end else ('left_after_success' if ever else ('placed_nonstatic' if placed[-1,i] else 'goal_not_reached_at_end'))
            rows.append(dict(variant=v,training_seed=s,update=it,density=density,friction=friction,initial_state=i,
                success_at_end=int(end),success_once=int(ever),failure=failure,
                first_success_step=int(events[0]+1) if len(events) else None,
                final_goal_distance_mm=float(distance[-1,i]*1000),final_arm_speed_rad_s=float(speed[-1,i]),
                final_arm_max_abs_velocity_rad_s=float(max_speed[-1,i]),
                grasp_fraction=float(d['is_grasped'][:,i].mean()),
                grasp_transitions=int(np.count_nonzero(np.diff(d['is_grasped'][:,i].astype(int)))),
                final_cube_height_m=float(d['cube_pose'][-1,i,2])))
    assert len(used_metadata)==72
    with (out/'episodes.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    cells=[]
    for v,it,(density,friction) in itertools.product(['native','no_grasp','half'],[97,195],conditions):
        rr=[r for r in rows if (r['variant'],r['update'],r['density'],r['friction'])==(v,it,density,friction)]
        cells.append(dict(variant=v,update=it,density=density,friction=friction,
            end=sum(r['success_at_end'] for r in rr),once=sum(r['success_once'] for r in rr),episodes=len(rr),
            end_by_seed={str(s):sum(r['success_at_end'] for r in rr if r['training_seed']==s) for s in [101,202,303]},
            failures={k:sum(r['failure']==k for r in rr) for k in ['success','left_after_success','placed_nonstatic','goal_not_reached_at_end']}))
    summary=dict(exploratory=True,training_fits=9,evaluation_episodes=len(rows),initial_states=32,cells=cells,
                 training_seconds=sum(r['seconds'] for r in status['training']),evaluation_seconds=sum(r['seconds'] for r in status['evaluation']))
    save(out/'summary.json',summary)
    save(out/'verification.json',dict(status='passed',**checks,training_fits=9,checkpoints=18,evaluation_conditions=72,
                                    protocol='first observation; no ranking-generalization or real-world claim'))
    from analyze import analyze
    analyze(out)
    manifest=[dict(path=str(p.relative_to(out)),bytes=p.stat().st_size,sha256=digest(p)) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='manifest.json']
    save(out/'manifest.json',manifest)
    print(json.dumps(dict(status='passed',**checks,episodes=len(rows))))
    print(json.dumps(summary))

if __name__=='__main__': main()
