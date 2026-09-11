"""Synthetic interface tests only; does not import a simulator or load an episode."""
import json
from pathlib import Path
import numpy as np
from transformers import AutoProcessor
from codecs_impl import pack,unpack,encode_episode,join_packets,read_packets,depacket
p=json.loads(Path('/work/protocol.json').read_text())
assert set(p['calibration_seeds']).isdisjoint(p['heldout_seeds'])
assert set(p['seeds']).isdisjoint(p['excluded_readiness_seeds'])
assert len(p['seeds'])==24 and p['max_trajectories']==24*3+16*10
proc=AutoProcessor.from_pretrained('/inputs/fast',trust_remote_code=True,local_files_only=True)
rng=np.random.default_rng(741)
checks=[]
for b in [1,2,3,4,5,6,8,10,11,12]:
 values=rng.integers(0,2**b,137);raw=pack(values,b)
 assert np.array_equal(values,unpack(raw,b,len(values)))
 assert len(raw)==(len(values)*b+7)//8
checks.append('bit packing boundaries including non-byte-aligned tails')
a=np.zeros((43,8));a[:,:7]=np.sin(np.arange(43)[:,None]/9+np.arange(7)[None,:])*.8
a[:,7]=1;a[17:31,7]=-1
stats={'center':[0]*8,'half_range':[1]*8}
for kind in p['codec_variants']:
 param={'bits':8,'knots':5}
 decoded,blobs=encode_episode(a,kind,param,stats,proc)
 assert decoded.shape==a.shape
 if kind not in ['fast_joint','fast_quantile']:assert np.array_equal(decoded[:,7],a[:,7])
 raw=join_packets(blobs);back=read_packets(raw)
 assert back==blobs and len(raw)==4+sum(4+len(b) for b in blobs)
 assert sum(depacket(b,proc)[1] for b in blobs)==43
checks.append('six codecs, exact gripper side channel, partial chunk and charged packet framing')
b=a.copy();b[0,0]=2.25;b[-1,1]=-2.75
for kind in ['uniform_gripper','linear_gripper']:
 decoded,_=encode_episode(b,kind,{'bits':8,'knots':20},stats,proc)
 assert decoded[0,0]==2.25 and decoded[-1,1]==-2.75
checks.append('lossless scalar escapes preserve normalization tails')
# Full-knot interpolation and scalar quantization coincide at identical precision.
x,b1=encode_episode(a,'uniform_gripper',{'bits':6},stats,proc)
y,b2=encode_episode(a,'linear_gripper',{'bits':6,'knots':20},stats,proc)
assert np.array_equal(x,y) and sum(map(len,b1))==sum(map(len,b2))
checks.append('interpolation identity at full knot density')
# Exercise the actual event selector using a synthetic contact trace.
import prepare
trace=np.zeros((60,8));trace[:,7]=1;trace[20:40,7]=-1
contact=np.zeros(61,dtype=bool);contact[21:41]=True
forces=np.zeros((61,3));forces[21:41,1]=2
fake={'actions':trace,'is_cubeA_grasped':contact,'finger0_force':forces,'finger1_force':-forces}
reference=trace.copy();reference[:,:7]+=.001
plans,events=prepare.event_windows(fake,reference,stats)
assert len(plans)==4 and all(row['status']=='eligible' for row in events.values())
for event in ['grasp','release']:
 left=plans[event+'_event'];right=plans[event+'_free']
 assert np.array_equal(left[:,7],trace[:,7]) and np.array_equal(right[:,7],trace[:,7])
 assert np.isclose(np.sum((left-trace)**2),np.sum((right-trace)**2),rtol=0,atol=1e-12)
 assert np.count_nonzero(np.any(left!=trace,axis=1))==5
bad=dict(fake);bad['finger0_force']=np.ones((61,3))
rejected,reason=prepare.event_windows(bad,reference,stats)
assert not rejected and all(row['status']=='no_speed_matched_noncontact' for row in reason.values())
checks.append('actual event selector: equal residual energy, fixed gripper, reject absent free windows')
# Parameter selection is exercised on fabricated arrays, never on pilot observations.
import tempfile
with tempfile.TemporaryDirectory() as directory:
 prepare.O=Path(directory)
 for seed in p['calibration_seeds'][:4]:
  root=prepare.O/f'seed_{seed}';root.mkdir()
  np.savez(root/'generation.npz',actions=a)
  (root/'generation.json').write_text(json.dumps({'schema':{'action_low':[-1]*8,'action_high':[1]*8}}))
 selected=prepare.calibration(p['calibration_seeds'][:4])
 assert selected['success_labels_used_for_parameter_selection'] is False
 for family,row in selected['chosen'].items():
  if row:
   assert row['mean_bytes']<=selected['reference']['mean_bytes']
   allowed=[r for r in selected['candidates'] if r['kind']==family and r['mean_bytes']<=selected['reference']['mean_bytes']]
   assert row['arm_mse']==min(r['arm_mse'] for r in allowed)
checks.append('actual calibration selector obeys byte cap using synthetic action-only inputs')
print(json.dumps({'status':'passed','checks':checks,'synthetic_only':True,'simulator_imported':False},indent=2))
