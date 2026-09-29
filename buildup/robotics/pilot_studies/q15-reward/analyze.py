"""Descriptive paired outcome analysis, not an independent-trial significance test."""
import csv
import itertools
import json
from pathlib import Path
import numpy as np

def analyze(out):
    out=Path(out)
    raw=list(csv.DictReader((out/'episodes.csv').open()))
    data={}
    for r in raw:
        for k in ['training_seed','update','initial_state','success_at_end','success_once']:
            r[k]=int(r[k])
        for k in ['density','friction','final_goal_distance_mm','final_arm_speed_rad_s','final_arm_max_abs_velocity_rad_s','grasp_fraction']:
            r[k]=float(r[k])
        key=(r['variant'],r['training_seed'],r['update'],r['density'],r['friction'],r['initial_state'])
        assert key not in data
        data[key]=r
    conditions=[(1.,1.),(2.,1.),(1.,0.5),(2.,0.5)]
    units=list(itertools.product([101,202,303],range(32)))
    comparisons=[]
    for v,it,(density,friction) in itertools.product(['native','no_grasp','half'],[97,195],conditions[1:]):
        paired=[(data[v,s,it,1.,1.,i],data[v,s,it,density,friction,i]) for s,i in units]
        comparisons.append(dict(kind='shift_vs_nominal',variant=v,update=it,density=density,friction=friction,
            n=96,lost=sum(l['success_at_end'] and not r['success_at_end'] for l,r in paired),
            gained=sum(r['success_at_end'] and not l['success_at_end'] for l,r in paired),
            lost_units=[dict(seed=l['training_seed'],state=l['initial_state'],failure=r['failure'],
                             final_goal_distance_mm=r['final_goal_distance_mm'],final_arm_speed_rad_s=r['final_arm_speed_rad_s'],final_arm_max_abs_velocity_rad_s=r['final_arm_max_abs_velocity_rad_s'])
                        for l,r in paired if l['success_at_end'] and not r['success_at_end']]))
    for alt,it,(density,friction) in itertools.product(['no_grasp','half'],[97,195],conditions):
        paired=[(data['native',s,it,density,friction,i],data[alt,s,it,density,friction,i]) for s,i in units]
        comparisons.append(dict(kind='reward_vs_native',variant=alt,update=it,density=density,friction=friction,
            n=96,native_only=sum(l['success_at_end'] and not r['success_at_end'] for l,r in paired),
            alternative_only=sum(r['success_at_end'] and not l['success_at_end'] for l,r in paired),
            same_both_fail=sum(not l['success_at_end'] and not r['success_at_end'] for l,r in paired)))
    behavior=[]
    for v,it,(density,friction) in itertools.product(['native','no_grasp','half'],[97,195],conditions):
        rr=[data[v,s,it,density,friction,i] for s,i in units]
        behavior.append(dict(variant=v,update=it,density=density,friction=friction,
            grasp_fraction_mean=float(np.mean([r['grasp_fraction'] for r in rr])),
            final_distance_median_mm=float(np.median([r['final_goal_distance_mm'] for r in rr])),
            final_arm_speed_median_rad_s=float(np.median([r['final_arm_speed_rad_s'] for r in rr]))))
    value=dict(boundary='Descriptive matched evaluation states with only three independent training seeds per reward; no population significance claim.',
               comparisons=comparisons,behavior=behavior)
    (out/'analysis.json').write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
    return value
