"""Read-only post-run audit; execute in the frozen v2 Docker, never on host.
No collector/prepare/evaluate import. Physical labels reuse the frozen analytical
v1 routine; packet decoding, aggregation and localization checks are separate.
"""
import hashlib, importlib.util, json, math, struct
from collections import Counter
from pathlib import Path
import numpy as np
from scipy.fft import idct, dct
from tokenizers import Tokenizer
O=Path('/outputs'); P=json.loads((O/'protocol.json').read_text())
def js(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def same(a,b): assert np.allclose(a,b,rtol=0,atol=1e-12)
spec=importlib.util.spec_from_file_location('labels','/baseline/verify.py')
labels=importlib.util.module_from_spec(spec);spec.loader.exec_module(labels)
job=js(O/'job.json'); analysis=js(O/'analysis.json'); cal=js(O/'calibration.json')
assert job['status']=='completed'
hashes=js(O/'outputs.sha256.json')
for name,h in hashes.items(): assert sha(O/name)==h,name
freeze=js(O/'freeze.json')
for name,h in freeze['files'].items(): assert sha(Path('/work')/name)==h,name
for name,h in freeze['baseline_files'].items(): assert sha(Path('/baseline')/name)==h,name
assert sha(O/'calibration.json')==(O/'calibration.sha256').read_text().strip()==job['calibration_sha256']
for seed,h in js(O/'plans.sha256.json').items(): assert sha(O/f'seed_{seed}/planned/manifest.json')==h
workers=job['workers']; assert len(workers)<=P['max_trajectories']
assert len({(x['seed'],x['mode']) for x in workers})==len(workers)
assert {x['seed'] for x in workers}==set(P['seeds'])
assert not set(P['seeds'])&set(P['excluded_readiness_seeds'])
assert all(w['returncode']==0 for w in workers)
cal_indices=[i for i,w in enumerate(workers) if w['seed'] in P['calibration_seeds']]
held_indices=[i for i,w in enumerate(workers) if w['seed'] in P['heldout_seeds']]
variant_indices=[i for i,w in enumerate(workers) if w['mode'] not in ['generation','replay_0','replay_1']]
assert max(cal_indices)<min(held_indices)
assert max(i for i,w in enumerate(workers) if w['mode'] in ['generation','replay_0','replay_1'])<min(variant_indices)
assert (O/'calibration.sha256').stat().st_mtime_ns<min((O/f'seed_{s}/generation.json').stat().st_mtime_ns for s in P['heldout_seeds'])
assert (O/'plans.sha256.json').stat().st_mtime_ns<min((O/f"seed_{w['seed']}/{w['mode']}.json").stat().st_mtime_ns for w in workers if w['mode'] in P['codec_variants'])
def data(s,m='generation'): return dict(np.load(O/f'seed_{s}/{m}.npz'))
original={s:data(s) for s in P['seeds']}
full_diff=0.; label_count=0; steps=0; successes={}; failure_cases=[]
for worker in workers:
    s,m=worker['seed'],worker['mode']; d=data(s,m); r=js(O/f'seed_{s}/{m}.json'); a=d['actions']; n=len(a)
    assert r['status']=='completed' and 0<n<=P['max_steps']
    assert all(np.isfinite(v).all() for v in d.values())
    assert all(len(v)==n+1 for k,v in d.items() if k!='actions')
    assert hashlib.sha256(a.tobytes()).hexdigest()==r['action_sha256']
    for k,v in labels.labels_from_arrays(d).items(): assert np.array_equal(d[k],v); label_count+=len(v)
    steps+=n; successes[s,m]=bool(d['success'][-1])
    if m in P['codec_variants'] and not successes[s,m]:
        failure_cases.append(dict(seed=s,method=m,original_success=bool(original[s]['success'][-1]),
            final_on=bool(d['is_cubeA_on_cubeB'][-1]),final_static=bool(d['is_cubeA_static'][-1]),
            final_grasped=bool(d['is_cubeA_grasped'][-1]),ever_grasped=bool(d['is_cubeA_grasped'].any()),
            ever_on=bool(d['is_cubeA_on_cubeB'].any())))
    if m=='generation': continue
    src=original[s]
    planned=src['actions'] if m.startswith('replay_') else np.load(O/f'seed_{s}/planned/{m}.npy')
    assert a.dtype==planned.dtype and a.tobytes()==planned.tobytes()
    for k in src:
        if k in labels.LABELS+['actions'] or 'force' in k: continue
        assert np.max(np.abs(src[k][0]-d[k][0]))<=P['initial_state_atol']
        if m.startswith('replay_'): full_diff=max(full_diff,float(np.max(np.abs(src[k]-d[k]))))
    if m.startswith('replay_'):
        for k in labels.LABELS: assert np.array_equal(src[k],d[k])
ca=np.concatenate([original[s]['actions'] for s in cal['calibration_seeds_used']])
lo,hi=np.quantile(ca,P['quantiles'],axis=0); w=(hi-lo)/2; w[w<P['constant_channel_epsilon']]=1
same(cal['quantile']['center'],(hi+lo)/2); same(cal['quantile']['half_range'],w)
schema=js(O/f"seed_{cal['calibration_seeds_used'][0]}/generation.json")['schema']
lo=np.array(schema['action_low']); hi=np.array(schema['action_high']); width=(hi-lo)/2
same(cal['joint']['center'],(hi+lo)/2); same(cal['joint']['half_range'],width)
for kind,choice in cal['chosen'].items():
    pool=[r for r in cal['candidates'] if r['kind']==kind and r['mean_bytes']<=cal['reference']['mean_bytes']]
    assert choice==(min(pool,key=lambda r:(r['arm_mse'],r['mean_bytes'],r['param']['bits'],r['param'].get('knots',0))) if pool else None)
tok=Tokenizer.from_file('/inputs/fast/tokenizer.json'); cfg=js(Path('/inputs/fast/processor_config.json'))
def ints(raw,bits,n):
    value=int.from_bytes(raw,'little'); return np.array([(value>>(i*bits))&((1<<bits)-1) for i in range(n)])
# Recompute all 45 calibration grid points plus the FAST reference independently.
assert len(cal['candidates'])==len(P['uniform_bits'])+len(P['linear_bits'])*len(P['linear_knots'])
cal_chunks_checked=0
for candidate in [cal['reference']]+cal['candidates']:
    wire_bytes=128; n_chunks=0; squared=0.; values=0
    kind=candidate['kind'];param=candidate['param']
    for seed in cal['calibration_seeds_used']:
        actions=original[seed]['actions']; normed=(actions[:,:7]-np.array(cal['joint']['center'])[:7])/width[:7]
        wire_bytes+=4
        for start in range(0,len(actions),20):
            block=normed[start:start+20];n=len(block); padded=np.pad(block,((0,20-n),(0,0)),mode='edge')
            if kind=='fast_joint_gripper':
                coefficients=np.rint(dct(padded,axis=0,norm='ortho')*cfg['scale'])
                assert np.all(coefficients>=cfg['min_token'])
                token_text=''.join(chr(int(x)-cfg['min_token']) for x in coefficients.flat)
                token_ids=tok.encode(token_text).ids
                bits=(tok.get_vocab_size()-1).bit_length()
                body=math.ceil(len(token_ids)*bits/8)
                restored=idct(coefficients/cfg['scale'],axis=0,norm='ortho')
            else:
                bits=param['bits']; k=param.get('knots',20); indices=np.rint(np.linspace(0,19,k)).astype(int)
                samples=padded[indices]; escapes=(samples<-1)|(samples>1)
                quantized=np.rint((np.clip(samples,-1,1)+1)*((1<<bits)-1)/2)
                reconstructed=quantized*2/((1<<bits)-1)-1;reconstructed[escapes]=samples[escapes]
                body=math.ceil(samples.size*bits/8)
                if escapes.any():body+=math.ceil(samples.size/8)+8*int(escapes.sum())
                restored=np.stack([np.interp(np.arange(20),indices,reconstructed[:,j]) for j in range(7)],axis=1)
            wire_bytes+=4+12+body+3;n_chunks+=1
            decoded=restored[:n]*width[:7]+np.array(cal['joint']['center'])[:7]
            squared+=np.sum(((decoded-actions[start:start+n,:7])/width[:7])**2);values+=n*7
    same(wire_bytes/n_chunks,candidate['mean_bytes']);same(squared/values,candidate['arm_mse']);cal_chunks_checked+=n_chunks
chunks=0; decode_max=0.; table={}; event_counts=Counter(); loc={}; planned_count=0
for s in P['heldout_seeds']:
    src=original[s]; a=src['actions']; root=O/f'seed_{s}/planned'; manifest=js(root/'manifest.json')
    for kind,m in manifest['methods'].items():
        if m['status']!='planned': continue
        planned_count+=1; back=np.load(root/(kind+'.npy'))
        assert hashlib.sha256(back.tobytes()).hexdigest()==m['array_sha256']
        mse=float(np.mean(((back[:,:7]-a[:,:7])/width[:7])**2)); same(mse,m['arm_mse'])
        if kind not in P['codec_variants']: continue
        same(np.mean((back[:,7]-a[:,7])**2),m['gripper_mse'])
        assert int((np.abs(back[:,7])>1).sum())==m['gripper_controller_clip_values']
        if kind not in ['fast_joint','fast_quantile']: assert np.array_equal(back[:,7],a[:,7])
        raw=(root/(kind+'.bin')).read_bytes(); count=struct.unpack_from('<I',raw)[0]; off=4; reconstructed=[]; c=np.array(m['normalization']['center']); w=np.array(m['normalization']['half_range'])
        assert len(raw)==m['bytes'] and count==m['chunks']==math.ceil(len(a)/20)
        for ix in range(count):
            size=struct.unpack_from('<I',raw,off)[0]; off+=4; b=raw[off:off+size]; off+=size
            magic,code,dim,flags,n,k,num=struct.unpack_from('<4sBBBBHH',b); bits=flags&127
            assert magic==b'Q11P' and n==min(20,len(a)-20*ix)
            end=12+math.ceil(num*bits/8); q=ints(b[12:end],bits,num)
            if code==0:
                coefficients=(np.array([ord(t) for t in tok.decode(q.tolist())])+cfg['min_token']).reshape(20,dim)
                normalized=(a[ix*20:ix*20+n]-c)/w; normalized=np.pad(normalized,((0,20-n),(0,0)),mode='edge')
                assert np.array_equal(coefficients,np.rint(dct(normalized[:,:dim],axis=0,norm='ortho')*cfg['scale']))
                val=idct(coefficients/cfg['scale'],axis=0,norm='ortho')
            else:
                val=q*2./((1<<bits)-1)-1
                if flags&128:
                    en=end+math.ceil(num/8); mask=ints(b[end:en],1,num).astype(bool); end=en
                    en=end+8*int(mask.sum()); val[mask]=np.frombuffer(b[end:en],dtype='<f8'); end=en
                knots=val.reshape(k,dim); locations=np.rint(np.linspace(0,19,k)).astype(int)
                val=np.stack([np.interp(np.arange(20),locations,knots[:,j]) for j in range(dim)],axis=1)
            if dim==7: val=np.column_stack((val,ints(b[end:end+3],1,20)*2.-1)); end+=3
            assert end==len(b)
            restored=val[:n]*w+c
            if dim==7: restored[:,7]=val[:n,7]
            reconstructed.append(restored); chunks+=1
        assert off==len(raw)
        delta=float(np.max(np.abs(np.concatenate(reconstructed)-back))); decode_max=max(decode_max,delta); assert delta<=1e-12
        t=table.setdefault(kind,dict(n=0,success=0,lost=0,gained=0,bytes=128,chunks=0,sse=0.,steps=0,gripper_sse=0.,clips=0))
        success=successes[s,kind]; orig=successes[s,'generation']
        t['n']+=1;t['success']+=success;t['lost']+=orig and not success;t['gained']+=success and not orig;t['bytes']+=len(raw);t['chunks']+=count;t['sse']+=mse*len(a);t['steps']+=len(a);t['gripper_sse']+=m['gripper_mse']*len(a);t['clips']+=m['gripper_controller_clip_values']
    # Derive the entire eligible-window search from original arrays, including exclusions.
    g=src['is_cubeA_grasped']; transitions=np.flatnonzero(g[1:]!=g[:-1])+1
    grasps=[int(i) for i in transitions if g[i]]
    releases=[int(i) for i in transitions if not g[i] and grasps and i>grasps[0]]
    event_indices={'grasp':grasps[0] if grasps else None,'release':releases[0] if releases else -1}
    for event,m in manifest['events'].items():
        assert m['event_state_index']==event_indices[event]
        ei=event_indices[event]
        if ei is not None and ei>=0 and ei-3>=1 and ei+2<=len(a) and (root/'fast_quantile_gripper.npy').exists():
            start=ei-3; residual=np.load(root/'fast_quantile_gripper.npy')[start:start+5,:7]-a[start:start+5,:7]
            if np.sum((residual/width[:7])**2)>1e-12:
                speeds=np.linalg.norm(np.diff(a[:,:7]/width[:7],axis=0),axis=1)
                esp=float(speeds[start-1:start+4].mean()); candidates=[]
                for free in range(1,len(a)-4):
                    if not (free+5<=start or free>=start+5): continue
                    if any(free-3<=i<=free+8 for i in transitions): continue
                    if g[free:free+6].any(): continue
                    if any(np.any(np.linalg.norm(src[f'finger{i}_force'][free:free+6],axis=1)>=.5) for i in range(2)): continue
                    if not np.all(a[free:free+5,7]==a[free,7]): continue
                    fsp=float(speeds[free-1:free+4].mean())
                    if min(esp,fsp)<1e-6:
                        if max(esp,fsp)>=1e-6: continue
                        distance=abs(esp-fsp)
                    else:
                        if max(esp,fsp)/min(esp,fsp)>2: continue
                        distance=abs(np.log(esp/fsp))
                    injected=a.copy();injected[free:free+5,:7]+=residual
                    if np.any(injected[:,:7]<lo[:7]) or np.any(injected[:,:7]>hi[:7]): continue
                    candidates.append((distance,free))
                if candidates:
                    assert m['status']=='eligible' and m['free_action_start']==min(candidates)[1]
                else: assert m['status']=='no_speed_matched_noncontact'

        event_counts[event+':'+m['status']]+=1
        if m['status']!='eligible': continue
        e=m['event_state_index']; st=m['event_action_start']; f=m['free_action_start']; L=m['length']; g=src['is_cubeA_grasped']
        assert st==e-3 and L==5
        edges=np.flatnonzero(g[1:]!=g[:-1])+1
        assert not g[f:f+L+1].any()
        assert all(np.all(np.linalg.norm(src[f'finger{i}_force'][f:f+L+1],axis=1)<.5) for i in range(2))
        assert not np.any((edges>=f-3)&(edges<=f+L+3))
        assert np.all(a[f:f+L,7]==a[f,7]) and (f+L<=st or f>=st+L)
        speed=np.linalg.norm(np.diff(a[:,:7]/width[:7],axis=0),axis=1)
        es=float(speed[st-1:st+L-1].mean()); fs=float(speed[f-1:f+L-1].mean())
        same(es,m['event_speed']);same(fs,m['free_speed'])
        assert max(es,fs)<1e-6 or (min(es,fs)>=1e-6 and max(es,fs)/min(es,fs)<=2)
        residual=np.load(root/'fast_quantile_gripper.npy')[st:st+L,:7]-a[st:st+L,:7]
        energy=[]
        for location,start in [('event',st),('free',f)]:
            expected=a.copy();expected[start:start+L,:7]+=residual
            actual=np.load(root/(event+'_'+location+'.npy')); assert np.array_equal(expected,actual)
            assert np.all(actual[:,:7]>=lo[:7]) and np.all(actual[:,:7]<=hi[:7])
            energy.append(float(np.mean(((actual[:,:7]-a[:,:7])/width[:7])**2)))
        same(*energy)
        t=loc.setdefault(event,dict(n=0,event_success=0,free_success=0,lost=0,opposite=0))
        x,y=successes[s,event+'_event'],successes[s,event+'_free'];t['n']+=1;t['event_success']+=x;t['free_success']+=y;t['lost']+=not x and y;t['opposite']+=x and not y
assert planned_count==len(variant_indices)
for kind,t in table.items():
    r=analysis['codec_table'][kind]
    assert (t['n'],t['success'],t['lost'],t['gained'])==(r['verified_variants'],r['codec_success'],r['lost_success'],r['gained_success'])
    delta=np.array([int(successes[seed,kind])-int(successes[seed,'generation']) for seed in P['heldout_seeds'] if (seed,kind) in successes])
    rng=np.random.default_rng(P['bootstrap_seed']); means=[]
    for _ in range(P['bootstrap_resamples']): means.append(float(delta[rng.integers(len(delta),size=len(delta))].mean()))
    same(np.quantile(means,[.025,.975]),r['paired_bootstrap_95']);same(delta.mean(),r['paired_success_delta'])
    t['bytes_per_chunk']=t['bytes']/t['chunks'];t['arm_mse']=t.pop('sse')/t['steps'];t['gripper_mse']=t.pop('gripper_sse')/t['steps']
    comp=analysis['rate_error_support'][kind]
    same(t['bytes_per_chunk'],comp['control_bytes']);same(t['arm_mse'],comp['control_arm_mse'])
for event,t in loc.items():
    n=t['lost']+t['opposite']; p=min(1,2*sum(math.comb(n,j) for j in range(min(t['lost'],t['opposite'])+1))/2**n) if n else 1.
    r=analysis['localization'][event];assert t['n']==r['eligible_pairs'];same(p,r['exact_paired_two_sided_p']);t['p']=p
expected_decision=('INCOMPLETE_CODEC_SUPPORT' if any(table.get(k,{}).get('n',0)!=len(P['heldout_seeds']) for k in P['codec_variants']) else ('OUTCOME_CHANGES_REQUIRE_STAGE7_REVIEW' if any(t['lost'] or t['gained'] for t in table.values()) else 'NO_TASK_OUTCOME_CHANGES'))
assert analysis['decision']==expected_decision
result=dict(status='PASS',failure_cases=failure_cases,original_success={part:sum(successes[seed,'generation'] for seed in P[part+'_seeds']) for part in ['calibration','heldout']},scientific_reruns=0,output_hashes=len(hashes),workers=len(workers),control_actions=steps,physical_labels=label_count,replay_full_state_max_abs=full_diff,independent_decoded_chunks=chunks,calibration_grid_points_checked=46,calibration_chunks_checked=cal_chunks_checked,decode_max_abs=decode_max,calibration_selection_and_split_order=True,planned_before_outcomes=True,codec_table=table,event_eligibility=dict(event_counts),localization=loc,decision=analysis['decision'],audit_source_sha256=sha(Path('/baseline/audit_v2.py')))
Path('/audit/verification.json').write_text(json.dumps(result,indent=2,allow_nan=False))
print(json.dumps(result,indent=2))
