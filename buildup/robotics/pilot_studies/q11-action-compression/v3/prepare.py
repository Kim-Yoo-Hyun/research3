"""Label-blind calibration, byte-accounted plans, and source-trajectory event windows."""
import hashlib
import json
from pathlib import Path
import numpy as np
from transformers import AutoProcessor
from codecs_impl import encode_episode,join_packets
P=json.loads(Path('/work/protocol.json').read_text());O=Path('/outputs')


def processor():return AutoProcessor.from_pretrained('/inputs/fast',trust_remote_code=True,local_files_only=True)

def source(seed):return dict(np.load(O/f'seed_{seed}'/'generation.npz'))

def arm_mse(a,b,w):return float(np.mean(((a[:,:7]-b[:,:7])/w[:7])**2))


def event_windows(d,reference,stats):
    a=d['actions'];g=d['is_cubeA_grasped'];n=len(a)
    starts=np.flatnonzero(~g[:-1]&g[1:])+1
    releases=np.flatnonzero(g[:-1]&~g[1:])+1
    events={'grasp':int(starts[0]) if len(starts) else None,
            'release':int(next((x for x in releases if len(starts) and x>starts[0]),-1))}
    force0=np.linalg.norm(d['finger0_force'],axis=1);force1=np.linalg.norm(d['finger1_force'],axis=1)
    w=np.array(stats['half_range']);speed=np.linalg.norm(np.diff(a[:,:7]/w[:7],axis=0),axis=1)
    all_edges=np.flatnonzero(g[1:]!=g[:-1])+1
    specs={};receipts={}
    for name,e in events.items():
        row={'event_state_index':e,'status':'no_event'}
        if e is None or e<0:receipts[name]=row;continue
        start=e-1-P['event_window_before'];L=P['event_window_length'];stop=start+L
        if start<1 or stop>n:row['status']='boundary';receipts[name]=row;continue
        energy=reference[start:stop,:7]-a[start:stop,:7]
        if float(np.sum((energy/w[:7])**2))<=P['mse_absolute_floor']:
            row['status']='no_residual';receipts[name]=row;continue
        event_speed=float(np.mean(speed[start-1:stop-1]));pool=[]
        for f in range(1,n-L+1):
            if not(f+L<=start or f>=stop):continue
            if np.any((all_edges>=f-P['event_exclusion_margin'])&(all_edges<=f+L+P['event_exclusion_margin'])):continue
            if g[f:f+L+1].any() or np.any(force0[f:f+L+1]>=.5) or np.any(force1[f:f+L+1]>=.5):continue
            if not np.all(a[f:f+L,7]==a[f,7]):continue
            free_speed=float(np.mean(speed[f-1:f+L-1]));eps=P['speed_zero_threshold']
            if min(event_speed,free_speed)<eps:
                if max(event_speed,free_speed)>=eps:continue
                distance=abs(event_speed-free_speed)
            else:
                ratio=max(event_speed,free_speed)/min(event_speed,free_speed)
                if ratio>P['speed_ratio_max']:continue
                distance=abs(np.log(event_speed/free_speed))
            test=a.copy();test[f:f+L,:7]+=energy
            low=np.array(stats['center'])-w;high=np.array(stats['center'])+w
            if np.any(test[:,:7]<low[:7]) or np.any(test[:,:7]>high[:7]):continue
            pool.append((distance,f,free_speed))
        if not pool:row['status']='no_speed_matched_noncontact';receipts[name]=row;continue
        _,f,fs=min(pool)
        event=a.copy();free=a.copy();event[start:stop,:7]+=energy;free[f:f+L,:7]+=energy
        low=np.array(stats['center'])-w;high=np.array(stats['center'])+w
        if np.any(event[:,:7]<low[:7]) or np.any(event[:,:7]>high[:7]):
            row['status']='event_joint_limit';receipts[name]=row;continue
        assert abs(arm_mse(event,a,w)-arm_mse(free,a,w))<=P['identity_atol']
        specs[name+'_event']=event;specs[name+'_free']=free
        row.update(status='eligible',event_action_start=start,free_action_start=f,length=L,
                   event_speed=event_speed,free_speed=fs,normalized_arm_mse=arm_mse(event,a,w))
        receipts[name]=row
    return specs,receipts


def plans(seed,cal):
    assert seed in P['heldout_seeds']
    d=source(seed);a=d['actions'];root=O/f'seed_{seed}'/'planned';root.mkdir()
    proc=processor();rows={};decoded={};joint=cal['joint'];w=np.array(joint['half_range']);c=np.array(joint['center'])
    for kind in P['codec_variants']:
        stats=cal['quantile'] if 'quantile' in kind else joint
        choice=cal['chosen'].get(kind,'fixed')
        if choice is None:rows[kind]={'status':'NO_CALIBRATION_RATE_SUPPORT'};continue
        param=choice['param'] if isinstance(choice,dict) else {}
        try:
            back,blobs=encode_episode(a,kind,param,stats,proc)
            wire=join_packets(blobs);(root/(kind+'.bin')).write_bytes(wire)
            if np.any(back[:,:7]<(c-w)[:7]) or np.any(back[:,:7]>(c+w)[:7]):raise ValueError('decoded arm joint target outside limits')
            np.save(root/(kind+'.npy'),back);decoded[kind]=back
            rows[kind]={'status':'planned','bytes':len(wire),'chunks':len(blobs),
                        'arm_mse':arm_mse(back,a,w),'gripper_mse':float(np.mean((back[:,7]-a[:,7])**2)),
                        'gripper_controller_clip_values':int((np.abs(back[:,7])>1).sum()),
                        'normalization':stats,'param':param,'array_sha256':hashlib.sha256(back.tobytes()).hexdigest()}
        except Exception as exc:rows[kind]={'status':'CODEC_UNAVAILABLE','error':str(exc)}
    localized,events=event_windows(d,decoded[P['mechanism_reference']],joint) if P['mechanism_reference'] in decoded else ({},{'status':'reference_unavailable'})
    for name,back in localized.items():
        np.save(root/(name+'.npy'),back)
        rows[name]={'status':'planned','diagnostic_only':True,'array_sha256':hashlib.sha256(back.tobytes()).hexdigest(),'arm_mse':arm_mse(back,a,w)}
    manifest={'seed':seed,'steps':len(a),'methods':rows,'events':events,'selected_before_variant_outcomes':True}
    (root/'manifest.json').write_text(json.dumps(manifest,indent=2))
    return [name for name,r in rows.items() if r['status']=='planned']
