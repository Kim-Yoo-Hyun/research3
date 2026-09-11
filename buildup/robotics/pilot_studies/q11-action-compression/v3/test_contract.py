"""Safety/decision-boundary tests with fabricated outcomes, no simulation or fitting."""
import copy,hashlib,json,math
from pathlib import Path
import support,evaluate
P=support.P;fixture=json.loads(Path('/work/precheck.json').read_text())['rows'];groups=[]
assert support.assess(fixture,8,2)['decision']=='READY_FOR_INTERVENTION'
assert support.assess(fixture)['decision']=='STOP_INSUFFICIENT_DENOMINATOR'
missing=copy.deepcopy(fixture);missing[0]['methods']['linear_gripper']['status']='CODEC_UNAVAILABLE'
assert support.assess(missing,8,2)['decision']=='STOP_NO_COMPARISON_SUPPORT'
assert support.assess(fixture,8,8)['decision']=='STOP_NO_EVENT_SUPPORT'
# Mean support uses the entire declared population. A bad episode cannot be dropped.
bad=copy.deepcopy(fixture);bad[0]['methods']['linear_gripper']['arm_mse']=1.
assert support.assess(bad,8,2)['decision']=='STOP_NO_COMPARISON_SUPPORT'
groups.append('support gates: count, availability, joint rate/error, event count; no subgroup rescue')
tables={k:{'verified_variants':24,'lost_success':1} for k in P['codec_variants']}
loc={k:{'diagnostic_signal':False} for k in P['event_types']}
assert evaluate.decide(False,24,'READY_FOR_INTERVENTION',tables,loc)=='MEASUREMENT_INVALID'
assert evaluate.decide(True,24,'STOP_NO_COMPARISON_SUPPORT',tables,loc)=='STOP_NO_COMPARISON_SUPPORT'
assert evaluate.decide(True,24,'READY_FOR_INTERVENTION',tables,loc)=='STOP_NO_CONTACT_LOCALIZATION_SIGNAL'
positive=copy.deepcopy(loc);positive['grasp']['diagnostic_signal']=True
assert evaluate.decide(True,24,'READY_FOR_INTERVENTION',tables,positive)=='LOCALIZED_DIFFERENCE_REQUIRES_REVIEW'
tables['fast_joint_gripper']['lost_success']=0
assert evaluate.decide(True,24,'READY_FOR_INTERVENTION',tables,positive)=='STOP_NO_FAILURE_LINK'
groups.append('decision priority: technical/support stops, missing failure link, null and review-only positive')
assert P['localization_two_sided_alpha_per_event']==.025 and P['localization_min_pairs']==8
assert 2/2**6>.025 and 2/2**7<=.025
assert not set(P['heldout_seeds'])&set(P['excluded_previous_seeds']) and len(P['heldout_seeds'])==24
assert P['max_trajectories']==240 and P['max_steps']==400 and P['workload_timeout_seconds']==7200
groups.append('fixed disjoint seeds, trajectory/time budgets and discrete sign-test threshold')
result={'status':'PASS','groups':groups,'simulation_executed':False,'empirical_outcomes_used':False,'source_sha256':hashlib.sha256(Path('/work/test_contract.py').read_bytes()).hexdigest()}
Path('/outputs/contract.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
