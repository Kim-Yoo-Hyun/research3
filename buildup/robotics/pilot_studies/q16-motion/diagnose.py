"""Case-level motion/selection diagnosis and state-only scientific visualization."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter


def run_diagnose(root,out):
    summary=json.loads((root/'verify1/summary.json').read_text())
    stats=[];cases=[]
    selections={m:np.zeros(9,dtype=int) for m in ('history','action')}
    for mode in ('servo','cv','history','action','fast'):
        records=[]
        for seed in range(20000,20024):
            p=root/'eval1'/f'{seed}_1_{mode}.npz';d=dict(np.load(p))
            j=json.loads(p.with_suffix('.json').read_text())
            forces=np.linalg.norm(d['contact_forces'],axis=2)
            touched=forces.max(1)>0.05
            idx=np.where(touched)[0];first=int(idx[0]) if len(idx) else None
            pre=max(0,first-1) if first is not None else 0
            grasp=np.where(d['grasp'])[0]
            dec=j['decisions'];learned=[v for v in dec if 'predictions' in v]
            for v in learned:selections[mode][v['selected']]+=1
            record=dict(seed=seed,mode=mode,first_contact_step=first,
                speed_before_first_contact_m_s=float(np.linalg.norm(d['velocity'][pre,:2])),
                distance_slid_before_contact_m=float(np.linalg.norm(d['cube'][pre,:2]-d['cube'][0,:2])),
                first_grasp_step=int(grasp[0]) if len(grasp) else None,
                modeled_contact_decisions=sum(bool(touched[v['t']:v['t']+2+1].any()) for v in learned),
                predicted_decisions=len(learned),
                decision_indices=[v['selected'] for v in learned])
            records.append(record);cases.append(record)
        stats.append(dict(mode=mode,episodes=len(records),
            speed_before_contact_median=float(np.median([r['speed_before_first_contact_m_s'] for r in records])),
            speed_before_contact_range=[float(min(r['speed_before_first_contact_m_s'] for r in records)),
                                        float(max(r['speed_before_first_contact_m_s'] for r in records))],
            median_slide_before_contact_m=float(np.median([r['distance_slid_before_contact_m'] for r in records])),
            modeled_contact_decisions=sum(r['modeled_contact_decisions'] for r in records)))
    pairs=[]
    for seed in range(20000,20024):
        dh=np.load(root/'eval1'/f'{seed}_1_history.npz');da=np.load(root/'eval1'/f'{seed}_1_action.npz')
        pairs.append(dict(seed=seed,action_difference_rms=float(np.sqrt(np.mean((dh['actions']-da['actions'])**2))),
                          cube_trajectory_rms_m=float(np.sqrt(np.mean(np.sum((dh['cube'][:,:3]-da['cube'][:,:3])**2,1))))))
    result=dict(dynamic_contact=stats,selected_candidate_counts={k:v.tolist() for k,v in selections.items()},
                dynamic_paired_trajectories=pairs,cases=cases,
                interpretation='Prediction accuracy and executed actions differ, but all tested routes succeed; no closed-loop success benefit established.')
    (out/'diagnosis.json').write_text(json.dumps(result,indent=2)+'\n')
    fig,axes=plt.subplots(1,3,figsize=(12,3.5),layout='constrained')
    modes=['cv','history','action'];colors=['#6b7280','#2563eb','#dc2626']
    for i,phase in enumerate(['approach_closing','transport']):
        vals=[next(r['rmse_m'] for r in summary['validation_prediction'] if r['phase']==phase and r['mode']==m)*1000 for m in modes]
        axes[i].bar(modes,vals,color=colors);axes[i].set_ylabel('Validation position RMSE (mm)')
        axes[i].set_title(phase.replace('_',' / '))
    vals=[next(r['success'] for r in summary['results'] if r['moving'] and r['mode']==m) for m in ['servo','cv','history','action','fast']]
    axes[2].bar(['servo','cv','history','action','fast'],vals,color=['#9ca3af',*colors,'#16a34a'])
    axes[2].set_ylim(0,26);axes[2].set_ylabel('Dynamic task success (of 24)');axes[2].set_title('Closed-loop outcome')
    fig.savefig(out/'comparison.png',dpi=160);plt.close(fig)
    # Fixed first evaluation seed: selection is independent of model advantage.
    seed=20000;fig,axes=plt.subplots(1,2,figsize=(8,3.3),layout='constrained')
    trajectories={m:dict(np.load(root/'eval1'/f'{seed}_1_{m}.npz')) for m in ('servo','history','action')}
    for m,col in zip(trajectories,['#6b7280','#2563eb','#dc2626']):
        d=trajectories[m];axes[0].plot(d['cube'][:,0],d['cube'][:,1],label=m,color=col)
        axes[1].plot(np.arange(81)*0.05,d['cube'][:,2],label=m,color=col)
    axes[0].set(xlabel='World x (m)',ylabel='World y (m)',title=f'State trajectory: seed {seed}')
    axes[1].set(xlabel='Time (s)',ylabel='Cube height (m)',title='Grasp and transport')
    axes[1].legend();fig.savefig(out/'case.png',dpi=160);plt.close(fig)
    d=trajectories['action'];fig,ax=plt.subplots(figsize=(4,4))
    ax.set(xlim=(-0.1,0.16),ylim=(0,0.22),xlabel='World x (m)',ylabel='World z (m)',
           title='State-only animation (not camera rendering)')
    obj,=ax.plot([],[],'rs',markersize=16,label='cube center')
    tcp,=ax.plot([],[],'bo',markersize=6,label='TCP')
    ax.plot([0.08],[0.16],'g*',markersize=12,label='goal');ax.legend(loc='upper left',fontsize=7)
    label=ax.text(.03,.04,'',transform=ax.transAxes)
    def frame(t):
        obj.set_data([d['cube'][t,0]],[d['cube'][t,2]])
        tcp.set_data([d['tcp'][t,0]],[d['tcp'][t,2]])
        label.set_text(f't={t*0.05:.2f}s; grasp={bool(d["grasp"][t])}')
        return obj,tcp,label
    anim=FuncAnimation(fig,frame,frames=81,interval=50)
    anim.save(out/'state.gif',writer=PillowWriter(fps=20));plt.close(fig)
    print(json.dumps(dict(dynamic_contact=stats,paired_cases=len(pairs)),indent=2))
