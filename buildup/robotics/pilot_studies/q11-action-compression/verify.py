"""Independent verification from saved arrays; imports no simulator or collector."""
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.fft import dct, idct
from tokenizers import Tokenizer
P=json.loads(Path('/work/protocol.json').read_text())
O=Path('/outputs')
LABELS=['success','is_cubeA_on_cubeB','is_cubeA_static','is_cubeA_grasped']


def norm(x):return np.linalg.norm(x,axis=-1)


def labels_from_arrays(d):
    delta=d['cubeA_pose'][:,:3]-d['cubeB_pose'][:,:3]
    on=(norm(delta[:,:2])<=np.linalg.norm(np.array([.02,.02],dtype=np.float32))+.005)&(np.abs(delta[:,2]-.04)<=.005)
    static=(norm(d['cubeA_linear_velocity'])<=.01)&(norm(d['cubeA_angular_velocity'])<=.5)
    grasp=[]
    for i in range(2):
        q=d[f'finger{i}_pose'][:,3:].astype(np.float64)
        w,x,y,z=q.T
        direction=np.stack([2*(x*y-w*z),w*w-x*x+y*y-z*z,2*(y*z+w*x)],axis=1)/np.sum(q*q,axis=1)[:,None]
        if i==1:direction=-direction
        f=d[f'finger{i}_force'];m=norm(f)
        cosine=np.sum(direction*f,axis=1)/np.maximum(m,1e-6)
        angle=np.rad2deg(np.arccos(np.clip(cosine,-1,1)))
        grasp.append((m>=.5)&(angle<=85))
    g=grasp[0]&grasp[1]
    return dict(success=on&static&~g,is_cubeA_on_cubeB=on,is_cubeA_static=static,is_cubeA_grasped=g)


def main():
    errors=[];rows=[];label_count=0
    for seed in P['seeds']:
        root=O/f'seed_{seed}'
        rec=json.loads((root/'generation.json').read_text())
        d=dict(np.load(root/'generation.npz'))
        n=len(d['actions'])
        row={'seed':seed,'generation_status':rec['status'],'steps':n,'replay_valid':False}
        assert hashlib.sha256(d['actions'].tobytes()).hexdigest()==rec['action_sha256']
        assert n<=P['max_steps']
        if not n or 'success' not in d:
            rows.append(row);continue
        assert all(np.isfinite(v).all() for v in d.values())
        assert all(len(v)==n+1 for k,v in d.items() if k!='actions')
        expected=labels_from_arrays(d)
        independent=all(np.array_equal(d[k],expected[k]) for k in LABELS)
        label_count+=(n+1)*len(LABELS)
        if not independent:errors.append(f'seed {seed} generation labels disagree with raw-state reconstruction')
        row['independent_labels_valid']=independent
        row['final_success']=bool(d['success'][-1])
        row['grasp_onsets']=int(np.sum(~d['is_cubeA_grasped'][:-1]&d['is_cubeA_grasped'][1:]))
        row['grasp_releases']=int(np.sum(d['is_cubeA_grasped'][:-1]&~d['is_cubeA_grasped'][1:]))
        row['noncontact_samples']=int(np.sum((norm(d['finger0_force'])<.5)&(norm(d['finger1_force'])<.5)))
        if rec['status']!='completed':rows.append(row);continue
        comparisons=[]
        for j in range(P['replay_repeats']):
            r=dict(np.load(root/f'replay_{j}.npz'))
            rr=json.loads((root/f'replay_{j}.json').read_text())
            eqactions=(r['actions'].dtype==d['actions'].dtype and r['actions'].tobytes()==d['actions'].tobytes())
            shapeok=all(k in r and r[k].shape==v.shape for k,v in d.items())
            physical=[k for k in d if k not in LABELS+['actions'] and 'force' not in k]
            initial=max(float(np.max(np.abs(d[k][0]-r[k][0]))) for k in physical) if shapeok else float('inf')
            labelseq=shapeok and all(np.array_equal(d[k],r[k]) for k in LABELS)
            reconstructed=shapeok and all(np.array_equal(r[k],v) for k,v in labels_from_arrays(r).items())
            label_count+=sum(len(r[k]) for k in LABELS if k in r)
            stepdiff=max(float(np.max(np.abs(d[k]-r[k]))) for k in physical) if shapeok else float('inf')
            comparisons.append({'repeat':j,'status':rr['status'],'actions_byte_equal':eqactions,
                                'initial_state_max_abs':initial,'full_state_max_abs_diagnostic':stepdiff,
                                'label_sequences_equal':labelseq,'independent_labels_valid':reconstructed,
                                'valid':rr['status']=='completed' and eqactions and initial<=P['initial_state_atol'] and labelseq and reconstructed})
        row['comparisons']=comparisons
        row['replay_valid']=independent and all(r['valid'] for r in comparisons)
        rows.append(row)
    codec=json.loads((O/'codec.json').read_text())
    tokenizer=Tokenizer.from_file('/inputs/fast/tokenizer.json')
    config=json.loads(Path('/inputs/fast/processor_config.json').read_text())
    codec_ok=codec['status']=='completed'
    chunks_checked=0
    for row in codec['rows']:
        if row['status']!='completed':codec_ok=False;continue
        seed=row['seed'];kind=row['normalization']
        a=np.load(O/f'seed_{seed}'/'generation.npz')['actions'].astype(np.float64)
        stem=O/f'codec_{seed}_{kind}'
        d=dict(np.load(str(stem)+'.npz'))
        tokens=json.loads(Path(str(stem)+'.json').read_text())['tokens']
        normed=(a-d['center'])/d['half_range']
        reconstructed=np.concatenate([part[:n] for part,n in zip(d['normalized'],d['valid_lengths'])])
        assert np.allclose(normed,reconstructed,atol=0,rtol=0)
        assert row['normalization_identity_error']<=P['identity_atol']
        assert row['dct_identity_error']<=P['identity_atol']
        coefficients=dct(d['normalized'],axis=1,norm='ortho')
        q=np.rint(coefficients*config['scale'])
        clipped=np.maximum(q,config['min_token'])
        assert np.array_equal(q,d['quantized']) and np.array_equal(clipped,d['clamped'])
        equality=[]
        for ids,expected in zip(tokens,clipped):
            raw=np.array([ord(x) for x in tokenizer.decode(ids)])+config['min_token']
            equality.append(bool(raw.size==expected.size and np.array_equal(raw.reshape(expected.shape),expected)))
        assert equality==row['bpe_equal']
        expected=idct(clipped/config['scale'],axis=1,norm='ortho')
        delta=float(np.max(np.abs(expected-d['decoded'])))
        assert abs(delta-row['official_vs_clamped_error'])<=P['codec_atol']
        assert int((q<config['min_token']).sum())==row['clamped_coefficients']
        codec_ok &= all(equality) and delta<=P['codec_atol'] and row['decode_finite'] and not row['decode_messages']
        chunks_checked+=len(tokens)
    usable=[r['seed'] for r in rows if r['replay_valid'] and r.get('final_success') and r.get('grasp_onsets',0)>0 and r.get('grasp_releases',0)>0 and r.get('noncontact_samples',0)>0]
    measurement_bad=any(r['generation_status']=='completed' and not r['replay_valid'] for r in rows) or bool(errors)
    if measurement_bad or not codec_ok:decision='REPLAY_OR_SCHEMA_INVALID'
    elif not usable:decision='NO_USABLE_EVENT_RECORD'
    else:decision='READY_FOR_CONTROLLED_PILOT'
    out={'decision':decision,'seed_attempts':len(rows),'usable_seeds':usable,'rows':rows,
         'codec_path_valid':bool(codec_ok),'codec_chunks_verified':chunks_checked,
         'independent_labels_checked':label_count,'errors':errors,
         'boundary':'Measurement readiness only; no compressed action executed, no learned policy or generality claim.'}
    (O/'verification.json').write_text(json.dumps(out,indent=2,allow_nan=False))
    print(json.dumps({k:v for k,v in out.items() if k!='rows'}),flush=True)


if __name__=='__main__':main()
