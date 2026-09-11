"""Read-only v3 audit: early support stops and completed interventions.
Reuses only the frozen analytical v1 label reconstruction. No simulator,
collector, planner, v3 support/evaluator, or official processor imports.
"""
import hashlib,importlib.util,json,math,struct
from collections import Counter
from pathlib import Path
import numpy as np
from scipy.fft import dct,idct
from tokenizers import Tokenizer
O=Path('/outputs');W=Path('/work');B=Path('/baseline')
def js(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def close(a,b):assert np.allclose(a,b,atol=1e-12,rtol=0),(a,b)
P=js(O/'protocol.json');C=js(O/'calibration.json');J=js(O/'job.json');G=js(O/'support.json')
assert J['status']=='completed'
assert sha(O/'protocol.json')==sha(W/'protocol.json') and sha(O/'freeze.json')==sha(W/'freeze.json')
assert js(O/'image.json')['Id']==js(W/'environment.json')['image']
for name in ['dependencies.lock','os-packages.lock']:assert sha(O/name)==sha(B/'v2'/name)
freeze=js(O/'freeze.json');inventory=js(O/'outputs.sha256.json');plans=js(O/'plans.sha256.json')
for name,h in freeze['files'].items():assert sha(W/name)==h,name
for name,h in freeze['baseline_files'].items():assert sha(B/name)==h,name
for name,h in inventory.items():assert sha(O/name)==h,name
for name,h in plans.items():assert sha(O/name)==h,name
assert sha(O/'calibration.json')==sha(W/'calibration.json')==(O/'calibration.sha256').read_text().strip()==J['calibration_sha256']
spec=importlib.util.spec_from_file_location('physical_labels','/baseline/verify.py');labels=importlib.util.module_from_spec(spec);spec.loader.exec_module(labels)
def data(seed,mode):return dict(np.load(O/f'seed_{seed}/{mode}.npz'))
workers=J['workers'];keys=[(w['seed'],w['mode']) for w in workers]
assert len(keys)==len(set(keys)) and len(keys)<=P['max_trajectories']
assert [w['seed'] for w in workers if w['mode']=='generation']==P['heldout_seeds']
assert not set(P['heldout_seeds'])&set(P['excluded_previous_seeds'])
assert all(w['returncode']==0 for w in workers)
assert (O/'calibration.sha256').stat().st_mtime_ns<min((O/f'seed_{s}/generation.json').stat().st_mtime_ns for s in P['heldout_seeds'])
source={s:data(s,'generation') for s in P['heldout_seeds']}
valid=[r['seed'] for r in J['eligibility'] if r['status']=='replay_valid']
assert len(valid)==len(set(valid))
measured=0;actions=0;full_diff=0.;initial_diff=0.;success={};attempts=Counter();checked=0;failure_cases=[]
for seed,mode in keys:
    receipt=js(O/f'seed_{seed}/{mode}.json');d=data(seed,mode);a=d['actions'];n=len(a)
    attempts[receipt['status']]+=1
    assert hashlib.sha256(a.tobytes()).hexdigest()==receipt['action_sha256']
    assert n<=P['max_steps'] and all(np.isfinite(v).all() for v in d.values())
    if receipt['status']!='completed':
        assert mode=='generation' and seed not in valid;continue
    assert 0<n and all(len(v)==n+1 for k,v in d.items() if k!='actions')
    for k,v in labels.labels_from_arrays(d).items():assert np.array_equal(d[k],v);measured+=len(v)
    checked+=1;actions+=n;success[seed,mode]=bool(d['success'][-1])
    if mode in P['codec_variants'] and not success[seed,mode]:
        failure_cases.append({'seed':seed,'method':mode,'original_success':bool(source[seed]['success'][-1]),'final_on':bool(d['is_cubeA_on_cubeB'][-1]),'final_static':bool(d['is_cubeA_static'][-1]),'final_grasped':bool(d['is_cubeA_grasped'][-1]),'ever_grasped':bool(d['is_cubeA_grasped'].any())})
    if mode=='generation':assert seed in valid;continue
    src=source[seed];expected=src['actions'] if mode.startswith('replay_') else np.load(O/f'seed_{seed}/planned/{mode}.npy')
    assert a.dtype==expected.dtype and a.tobytes()==expected.tobytes()
    for k in src:
        if k in labels.LABELS+['actions'] or 'force' in k:continue
        diff=float(np.max(np.abs(src[k][0]-d[k][0])));initial_diff=max(initial_diff,diff);assert diff<=P['initial_state_atol']
        if mode.startswith('replay_'):full_diff=max(full_diff,float(np.max(np.abs(src[k]-d[k]))))
    if mode.startswith('replay_'):
        for k in labels.LABELS:assert np.array_equal(src[k],d[k])
for seed in valid:
    assert all((seed,f'replay_{j}') in keys for j in range(P['replay_repeats']))
tok=Tokenizer.from_file('/inputs/fast/tokenizer.json');cfg=js(Path('/inputs/fast/processor_config.json'))
def unpack(raw,bits,count):
    packed=int.from_bytes(raw,'little');return np.array([(packed>>(i*bits))&((1<<bits)-1) for i in range(count)])
width=np.array(C['joint']['half_range']);center=np.array(C['joint']['center']);low=center-width;high=center+width
metrics={k:{'n':0,'bytes':128,'chunks':0,'sse':0.,'steps':0} for k in P['codec_variants']}
events=Counter();planned_modes=[];all_manifests={};decoded_chunks=0;decode_diff=0.;energy_diff=0.;unavailable=[]
for seed in valid:
    src=source[seed];a=src['actions'];root=O/f'seed_{seed}/planned';m=js(root/'manifest.json');all_manifests[seed]=m
    assert m['seed']==seed and m['steps']==len(a)
    for kind,r in m['methods'].items():
        if r['status']!='planned':unavailable.append({'seed':seed,'kind':kind,**r});continue
        planned_modes.append((seed,kind));back=np.load(root/(kind+'.npy'))
        assert back.shape==a.shape and np.isfinite(back).all()
        assert hashlib.sha256(back.tobytes()).hexdigest()==r['array_sha256']
        assert np.array_equal(back[:,7],a[:,7])
        mse=float(np.mean(((back[:,:7]-a[:,:7])/width[:7])**2));close(mse,r['arm_mse'])
        assert np.all(back[:,:7]>=low[:7]) and np.all(back[:,:7]<=high[:7])
        if kind not in P['codec_variants']:continue
        assert r['gripper_mse']==0 and r['gripper_controller_clip_values']==0
        expected_stats=C['quantile'] if 'quantile' in kind else C['joint'];assert r['normalization']==expected_stats
        assert r['param']==({'bits':6,'knots':3} if kind=='linear_gripper' else {})
        raw=(root/(kind+'.bin')).read_bytes();count=struct.unpack_from('<I',raw)[0];pos=4;result=[]
        assert len(raw)==r['bytes'] and count==r['chunks']==math.ceil(len(a)/20)
        c=np.array(r['normalization']['center']);w=np.array(r['normalization']['half_range'])
        for chunk in range(count):
            size=struct.unpack_from('<I',raw,pos)[0];pos+=4;blob=raw[pos:pos+size];pos+=size
            magic,code,dim,flags,n,k,num=struct.unpack_from('<4sBBBBHH',blob);bits=flags&127
            assert magic==b'Q11P' and dim==7 and n==min(20,len(a)-20*chunk)
            end=12+math.ceil(num*bits/8);q=unpack(blob[12:end],bits,num)
            if kind.startswith('fast'):
                assert code==0
                coef=(np.array([ord(x) for x in tok.decode(q.tolist())])+cfg['min_token']).reshape(20,7)
                normed=(a[20*chunk:20*chunk+n,:7]-c[:7])/w[:7];normed=np.pad(normed,((0,20-n),(0,0)),mode='edge')
                assert np.array_equal(coef,np.rint(dct(normed,axis=0,norm='ortho')*cfg['scale']))
                val=idct(coef/cfg['scale'],axis=0,norm='ortho')
            else:
                assert code==2 and k==3 and bits==6
                val=q*2./63-1
                if flags&128:
                    stop=end+math.ceil(num/8);mask=unpack(blob[end:stop],1,num).astype(bool);end=stop;stop=end+8*int(mask.sum())
                    val[mask]=np.frombuffer(blob[end:stop],dtype='<f8');end=stop
                knots=val.reshape(k,7);locations=np.array([0,10,19])
                val=np.stack([np.interp(np.arange(20),locations,knots[:,j]) for j in range(7)],axis=1)
            grip=unpack(blob[end:end+3],1,20)*2.-1;end+=3;assert end==len(blob)
            result.append(np.column_stack((val[:n]*w[:7]+c[:7],grip[:n])));decoded_chunks+=1
        assert pos==len(raw)
        diff=float(np.max(np.abs(np.concatenate(result)-back)));decode_diff=max(decode_diff,diff);assert diff<=1e-12
        t=metrics[kind];t['n']+=1;t['bytes']+=len(raw);t['chunks']+=count;t['sse']+=mse*len(a);t['steps']+=len(a)
    # Independently enumerate every possible noncontact location, including absent matches.
    ref_path=root/(P['mechanism_reference']+'.npy')
    if not ref_path.exists():assert m['events']=={'status':'reference_unavailable'};continue
    residual=np.load(ref_path)[:,:7]-a[:,:7];g=src['is_cubeA_grasped'];trans=np.flatnonzero(g[1:]!=g[:-1])+1
    grasp=[int(i) for i in trans if g[i]];release=[int(i) for i in trans if not g[i] and grasp and i>grasp[0]]
    indexes={'grasp':grasp[0] if grasp else None,'release':release[0] if release else -1}
    speed=np.linalg.norm(np.diff(a[:,:7]/width[:7],axis=0),axis=1)
    for name,e in indexes.items():
        r=m['events'][name];assert e==r['event_state_index'];events[name+':'+r['status']]+=1
        if e is None or e<0:assert r['status']=='no_event';continue
        st=e-3;L=5;stop=st+L
        if st<1 or stop>len(a):assert r['status']=='boundary';continue
        delta=residual[st:stop];energy=np.sum((delta/width[:7])**2)
        if energy<=P['mse_absolute_floor']:assert r['status']=='no_residual';continue
        es=float(speed[st-1:stop-1].mean());pool=[]
        for f in range(1,len(a)-4):
            if not(f+5<=st or f>=stop):continue
            if any(f-3<=i<=f+8 for i in trans):continue
            if g[f:f+6].any():continue
            if any(np.any(np.linalg.norm(src[f'finger{i}_force'][f:f+6],axis=1)>=.5) for i in range(2)):continue
            if not np.all(a[f:f+5,7]==a[f,7]):continue
            fs=float(speed[f-1:f+4].mean())
            if min(es,fs)<1e-6:
                if max(es,fs)>=1e-6:continue
                distance=abs(es-fs)
            else:
                if max(es,fs)/min(es,fs)>2:continue
                distance=abs(np.log(es/fs))
            test=a.copy();test[f:f+5,:7]+=delta
            if np.any(test[:,:7]<low[:7]) or np.any(test[:,:7]>high[:7]):continue
            pool.append((distance,f,fs))
        if not pool:assert r['status']=='no_speed_matched_noncontact';continue
        _,f,fs=min(pool);test=a.copy();test[st:stop,:7]+=delta
        if np.any(test[:,:7]<low[:7]) or np.any(test[:,:7]>high[:7]):assert r['status']=='event_joint_limit';continue
        assert r['status']=='eligible' and r['event_action_start']==st and r['free_action_start']==f and r['length']==5
        close(es,r['event_speed']);close(fs,r['free_speed']);errs=[]
        for mode,start in [('event',st),('free',f)]:
            expected=a.copy();expected[start:start+5,:7]+=delta;actual=np.load(root/(name+'_'+mode+'.npy'))
            assert np.array_equal(actual,expected);errs.append(float(np.mean(((actual[:,:7]-a[:,:7])/width[:7])**2)))
        diff=abs(errs[0]-errs[1]);energy_diff=max(energy_diff,diff);assert diff<=P['identity_atol']
        close(errs[0],r['normalized_arm_mse'])
for k,t in metrics.items():
    assert t['n']==G['available'][k]
    if t['n']:
        t['bytes_per_chunk']=t['bytes']/t['chunks'];t['arm_mse']=t.pop('sse')/t['steps']
        close(t['bytes_per_chunk'],G['metrics'][k]['bytes_per_chunk']);close(t['arm_mse'],G['metrics'][k]['arm_mse'])
assert G['originals']==len(valid)
assert (O/'support.json').stat().st_mtime_ns>=max((O/f'seed_{s}/{m}.json').stat().st_mtime_ns for s,m in keys if m in ['generation','replay_0','replay_1'])
for k in P['event_types']:assert events[k+':eligible']==G['eligible_events'][k]
complete=bool(valid) and all(t['n']==len(valid) for t in metrics.values());rate=mse_ok=False
if complete:
    ref=metrics['fast_joint_gripper'];linear=metrics['linear_gripper']
    rate=abs(linear['bytes_per_chunk']-ref['bytes_per_chunk'])<=.1*ref['bytes_per_chunk']
    mse_ok=abs(linear['arm_mse']-ref['arm_mse'])<=max(1e-12,.2*ref['arm_mse'])
assert rate==G['joint_linear_rate_overlap'] and mse_ok==G['joint_linear_mse_overlap']
if len(valid)<16:decision='STOP_INSUFFICIENT_DENOMINATOR'
elif not(complete and rate and mse_ok):decision='STOP_NO_COMPARISON_SUPPORT'
elif any(events[k+':eligible']<8 for k in P['event_types']):decision='STOP_NO_EVENT_SUPPORT'
else:decision='READY_FOR_INTERVENTION'
assert decision==G['decision']
interventions=[k for k in keys if k[1] not in ['generation','replay_0','replay_1']]
outcome={};localization={}
if decision!='READY_FOR_INTERVENTION':
    assert not interventions and not (O/'analysis.json').exists()
else:
    assert interventions==planned_modes
    first=min(keys.index(k) for k in interventions)
    assert all(m not in ['generation','replay_0','replay_1'] for _,m in keys[first:])
    assert (O/'plans.sha256.json').stat().st_mtime_ns<min(js(O/f'seed_{s}/{m}.json')['started']*1e9 for s,m in interventions)
    A=js(O/'analysis.json')
    for kind in P['codec_variants']:
        delta=np.array([int(success[s,kind])-int(success[s,'generation']) for s in valid]);t=A['codec_table'][kind]
        count=sum(success[s,kind] for s in valid);assert count==t['codec_success']
        assert int((delta<0).sum())==t['lost_success'] and int((delta>0).sum())==t['gained_success']
        rng=np.random.default_rng(P['bootstrap_seed']);means=[float(delta[rng.integers(len(delta),size=len(delta))].mean()) for _ in range(P['bootstrap_resamples'])]
        close(np.quantile(means,[.025,.975]),t['paired_bootstrap_95'])
        outcome[kind]={'n':len(valid),'success':count,'lost':int((delta<0).sum()),'gained':int((delta>0).sum())}
    r=A['linear_vs_joint'];deltas=np.array([int(success[s,'linear_gripper'])-int(success[s,'fast_joint_gripper']) for s in valid])
    assert r['episodes']==len(valid) and r['lost']==int((deltas<0).sum()) and r['gained']==int((deltas>0).sum())
    close(float(deltas.mean()),r['linear_minus_joint_success'])
    rng=np.random.default_rng(P['bootstrap_seed']);means=[float(deltas[rng.integers(len(deltas),size=len(deltas))].mean()) for _ in range(P['bootstrap_resamples'])]
    close(np.quantile(means,[.025,.975]),r['bootstrap_95'])
    for event in P['event_types']:
        seeds=[s for s in valid if (s,event+'_event') in interventions];x=[success[s,event+'_event'] for s in seeds];y=[success[s,event+'_free'] for s in seeds]
        lost=sum(not a and b for a,b in zip(x,y));opposite=sum(a and not b for a,b in zip(x,y));n=lost+opposite
        p=min(1.,2*sum(math.comb(n,i) for i in range(min(lost,opposite)+1))/2**n) if n else 1.
        r=A['localization'][event];assert lost==r['event_fails_free_succeeds'] and opposite==r['event_succeeds_free_fails'];close(p,r['exact_paired_two_sided_p'])
        signal=len(seeds)>=8 and lost>opposite and p<=.025;assert signal==r['diagnostic_signal']
        localization[event]={'n':len(seeds),'event_success':sum(x),'free_success':sum(y),'lost':lost,'opposite':opposite,'p':p,'signal':signal}
    if outcome['fast_joint_gripper']['lost']<1:decision='STOP_NO_FAILURE_LINK'
    elif not any(r['signal'] for r in localization.values()):decision='STOP_NO_CONTACT_LOCALIZATION_SIGNAL'
    else:decision='LOCALIZED_DIFFERENCE_REQUIRES_REVIEW'
    assert decision==A['decision']
assert decision==J['decision'] and len(interventions)==J['intervention_workers']
R={'status':'PASS','decision':decision,'source_sha256':sha(B/'audit_v3.py'),'output_hashes':len(inventory),'plan_hashes':len(plans),'workers':len(workers),'verified_trajectories':checked,'attempt_status':dict(attempts),'valid_originals':len(valid),'original_success':sum(success[s,'generation'] for s in valid),'control_actions':actions,'physical_labels':measured,'initial_state_max_abs':initial_diff,'replay_full_state_max_abs':full_diff,'planned_codec_chunks':decoded_chunks,'decode_max_abs':decode_diff,'paired_error_difference_max':energy_diff,'planned_metrics':metrics,'planned_events':dict(events),'unavailable':unavailable,'intervention_workers':len(interventions),'codec_outcomes':outcome,'failure_cases':failure_cases,'localization_outcomes':localization,'scientific_reruns':0,'calibration_and_plan_hashes_valid':True}
Path('/audit/verification.json').write_text(json.dumps(R,indent=2,allow_nan=False)+'\n');print(json.dumps(R,indent=2))
