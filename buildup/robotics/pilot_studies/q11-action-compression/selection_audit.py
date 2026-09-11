"""Stage 7 read-only review of frozen JSON evidence; no imports of methods/simulator."""
import hashlib
import json
from pathlib import Path
O=Path('/inputs'); S=Path('/study'); A=Path('/audit')
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
x=read(O/'analysis.json');c=read(O/'calibration.json');p=read(O/'protocol.json');v=read(S/'verification_v2.json')
assert v['status']=='PASS' and x['decision']=='INCOMPLETE_CODEC_SUPPORT'
assert sha(O/'calibration.json')==(O/'calibration.sha256').read_text().strip()
for name,h in read(S/'results_v2.json')['provenance'].items():assert sha(O/Path(name).name)==h
rows=[]; ref=c['reference']
for r in c['candidates']:
 rate=abs(r['mean_bytes']-ref['mean_bytes'])<=p['rate_support_relative_tolerance']*ref['mean_bytes']
 error=abs(r['arm_mse']-ref['arm_mse'])<=max(p['mse_absolute_floor'],p['mse_support_relative_tolerance']*ref['arm_mse'])
 rows.append({**r,'under_original_cap':r['mean_bytes']<=ref['mean_bytes'],'rate_overlap':rate,'mse_overlap':error,'both':rate and error})
summary={kind:{'candidates':sum(r['kind']==kind for r in rows),'under_cap':sum(r['kind']==kind and r['under_original_cap'] for r in rows),'rate_overlap':sum(r['kind']==kind and r['rate_overlap'] for r in rows),'both':sum(r['kind']==kind and r['both'] for r in rows)} for kind in ['uniform_gripper','linear_gripper']}
flips={}
for base in ['fast_joint','fast_quantile']:
 flips[base]=[]
 for r in x['rows']:
  before=r['methods'][base]['verification']['success'];after=r['methods'][base+'_gripper']['verification']['success']
  if before!=after:flips[base].append({'seed':r['seed'],'before':before,'after':after})
result={'status':'PASS','mode':'post-outcome descriptive review; no fitting, parameter selection or rollouts','input_sha256':{n:sha(O/n) for n in ['calibration.json','analysis.json','protocol.json']},'source_sha256':sha(S/'selection_audit.py'),'calibration_reference':ref,'existing_grid_summary':summary,'existing_grid':rows,'heldout_nonreference_joint_rate_mse_support':[k for k,r in x['rate_error_support'].items() if k!='fast_joint_gripper' and r.get('rate_matched') and r.get('error_matched')],'gripper_case_changes':flips,'localization_reference':p['mechanism_reference'],'localization_reference_full_success':x['codec_table'][p['mechanism_reference']]['codec_success'],'localization_reference_full_verified':x['codec_table'][p['mechanism_reference']]['verified_variants'],'localized_denominators':v['event_eligibility']}
(A/'selection.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:r for k,r in result.items() if k!='existing_grid'},indent=2))
