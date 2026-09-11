"""Outcome-free support gates over saved planned actions; no subgroup rescue."""
import json
from pathlib import Path
P=json.loads(Path('/work/protocol.json').read_text())

def assess(rows,min_originals=None,min_pairs=None):
    min_originals=P['heldout_min_valid'] if min_originals is None else min_originals
    min_pairs=P['confirmation_min_pairs_per_event'] if min_pairs is None else min_pairs
    available={k:sum(r['methods'].get(k,{}).get('status')=='planned' for r in rows) for k in P['codec_variants']}
    events={k:sum(r['events'].get(k,{}).get('status')=='eligible' for r in rows) for k in P['event_types']}
    metrics={}
    for k in P['codec_variants']:
        usable=[r for r in rows if r['methods'].get(k,{}).get('status')=='planned']
        if not usable:continue
        metrics[k]={'episodes':len(usable),'bytes_per_chunk':(128+sum(r['methods'][k]['bytes'] for r in usable))/sum(r['methods'][k]['chunks'] for r in usable),
                    'arm_mse':sum(r['methods'][k]['arm_mse']*r['steps'] for r in usable)/sum(r['steps'] for r in usable)}
    complete=bool(rows) and all(n==len(rows) for n in available.values())
    rate=error=False
    if complete:
        ref=metrics['fast_joint_gripper'];control=metrics['linear_gripper']
        rate=abs(control['bytes_per_chunk']/ref['bytes_per_chunk']-1)<=P['rate_support_relative_tolerance']
        error=abs(control['arm_mse']-ref['arm_mse'])<=max(P['mse_absolute_floor'],P['mse_support_relative_tolerance']*ref['arm_mse'])
    if len(rows)<min_originals:decision='STOP_INSUFFICIENT_DENOMINATOR'
    elif not complete or not(rate and error):decision='STOP_NO_COMPARISON_SUPPORT'
    elif not all(n>=min_pairs for n in events.values()):decision='STOP_NO_EVENT_SUPPORT'
    else:decision='READY_FOR_INTERVENTION'
    return {'decision':decision,'originals':len(rows),'available':available,'eligible_events':events,'metrics':metrics,'joint_linear_rate_overlap':rate,'joint_linear_mse_overlap':error,
            'minimum_originals':min_originals,'minimum_pairs_each_event':min_pairs,'success_outcomes_used':False,'subgroup_selection':False}
