"""Calibration-only feasibility check. No simulator or old held-out outcomes."""
import hashlib,json
from pathlib import Path
import numpy as np
from scipy.fft import dct,idct
import prepare,support
from codecs_impl import encode_episode,join_packets
P=prepare.P;C=json.loads(Path('/work/calibration.json').read_text());root=Path('/calibration')
proc=prepare.processor();rows=[];inputs={};chunks=0;max_error=0.;energies=[]
w=np.array(C['joint']['half_range']);c=np.array(C['joint']['center'])
for seed in P['calibration_seeds']:
    file=root/f'seed_{seed}/generation.npz';inputs[str(seed)]=hashlib.sha256(file.read_bytes()).hexdigest()
    with np.load(file) as raw:
        # Only action, grasp and sampled-force fields are read; no task outcome or variant data.
        d={k:raw[k] for k in ['actions','is_cubeA_grasped','finger0_force','finger1_force']}
    a=d['actions'];methods={};decoded={}
    for kind in P['codec_variants']:
        stats=C['quantile'] if 'quantile' in kind else C['joint'];param=C['chosen'].get(kind,{}).get('param',{})
        back,blobs=encode_episode(a,kind,param,stats,proc);chunks+=len(blobs)
        assert np.array_equal(back[:,7],a[:,7]) and np.all(back[:,:7]>=(c-w)[:7]) and np.all(back[:,:7]<=(c+w)[:7])
        cen=np.array(stats['center']);width=np.array(stats['half_range']);normalized=(a[:,:7]-cen[:7])/width[:7];independent=[]
        for start in range(0,len(a),20):
            part=normalized[start:start+20];n=len(part);part=np.pad(part,((0,20-n),(0,0)),mode='edge')
            if kind.startswith('fast'):
                out=idct(np.rint(dct(part,axis=0,norm='ortho')*10)/10,axis=0,norm='ortho')
            else:
                ix=np.array([0,10,19]);samples=part[ix];q=np.rint((np.clip(samples,-1,1)+1)*63/2);rec=q*2/63-1
                mask=(samples<-1)|(samples>1);rec[mask]=samples[mask]
                out=np.stack([np.interp(np.arange(20),ix,rec[:,j]) for j in range(7)],axis=1)
            independent.append(out[:n]*width[:7]+cen[:7])
        diff=float(np.max(np.abs(np.concatenate(independent)-back[:,:7])));max_error=max(max_error,diff);assert diff<=1e-12
        methods[kind]={'status':'planned','bytes':len(join_packets(blobs)),'chunks':len(blobs),'arm_mse':prepare.arm_mse(back,a,w)};decoded[kind]=back
    specs,events=prepare.event_windows(d,decoded[P['mechanism_reference']],C['joint'])
    for event,receipt in events.items():
        if receipt['status']!='eligible':continue
        first=receipt['event_action_start'];free=receipt['free_action_start'];L=receipt['length']
        residual=decoded[P['mechanism_reference']][first:first+L,:7]-a[first:first+L,:7]
        pair=[]
        for mode,start in [('event',first),('free',free)]:
            expected=a.copy();expected[start:start+L,:7]+=residual
            assert np.array_equal(specs[event+'_'+mode],expected)
            pair.append(prepare.arm_mse(expected,a,w))
        assert abs(pair[0]-pair[1])<=1e-12
        energies.append({'seed':seed,'event':event,'event_mse':pair[0],'free_mse':pair[1]})
    rows.append({'seed':seed,'steps':len(a),'methods':methods,'events':events})
check=support.assess(rows,min_originals=len(P['calibration_seeds']),min_pairs=P['preparation_min_pairs_per_event'])
assert len(set(P['heldout_seeds']))==24 and not set(P['heldout_seeds'])&set(P['excluded_previous_seeds'])
assert P['max_trajectories']==24*(1+2+3+4)
result={'status':'PASS' if check['decision']=='READY_FOR_INTERVENTION' else 'DESIGN_NOT_FEASIBLE','support':check,'source_sha256':hashlib.sha256(Path('/work/precheck.py').read_bytes()).hexdigest(),'protocol_sha256':hashlib.sha256(Path('/work/protocol.json').read_bytes()).hexdigest(),'calibration_input_sha256':inputs,'codec_chunks':chunks,'independent_decode_max_abs':max_error,'equal_residual_pairs':energies,'rows':rows,'new_simulator_episodes':0,'old_heldout_read':False,'variant_task_outcomes_read':False,'fresh_confirmation_support_known':False}
Path('/outputs/precheck.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['rows','equal_residual_pairs']},indent=2))
if result['status']!='PASS':raise SystemExit(2)
