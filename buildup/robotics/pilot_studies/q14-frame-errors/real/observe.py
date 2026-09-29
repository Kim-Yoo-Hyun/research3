"""Docker-only frozen-detector observation; no training or threshold tuning."""
import hashlib
import json
from pathlib import Path
import shutil
import time
import cv2
import numpy as np
from PIL import Image, ImageDraw
from ruamel.yaml import YAML
import torch
import torchvision
import dream

INPUT=Path('/input'); OUT=Path('/output'); SEED=20260916
def write(name,obj): (OUT/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def solve(X,uv,K,ids,kind):
    ids=np.asarray(ids,dtype=int)
    result={'success':False,'input_ids':ids.tolist(),'inlier_ids':None,'status':'too_few_points'}
    if len(ids)<4:return result
    x=np.ascontiguousarray(X[ids],dtype=np.float64); y=np.ascontiguousarray(uv[ids],dtype=np.float64)
    try:
        if kind=='official':
            ok,t,q=dream.geometric_vision.solve_pnp(x,y,K)
            if not ok: result['status']='official_solver_failed';return result
            R=np.asarray(q.matrix33,dtype=float); t=np.asarray(t,dtype=float)
        else:
            cv2.setRNGSeed(SEED)
            ok,rv,tv,inliers=cv2.solvePnPRansac(x,y,K,None,iterationsCount=100,
                reprojectionError=5.0,confidence=0.99,flags=cv2.SOLVEPNP_EPNP)
            if not ok or inliers is None:result['status']='ransac_failed';return result
            ii=inliers.ravel(); result['inlier_ids']=ids[ii].tolist()
            R,_=cv2.Rodrigues(rv); t=tv.ravel()
            result['ransac_pose']={'R':R.tolist(),'t':t.tolist()}
            result['refinement_status']='not_attempted'
            if len(ii)>=4:
                ok2,rv2,tv2=cv2.solvePnP(x[ii],y[ii],K,None,rvec=rv.copy(),tvec=tv.copy(),
                                      useExtrinsicGuess=True,flags=cv2.SOLVEPNP_ITERATIVE)
                if ok2:
                    R,_=cv2.Rodrigues(rv2);t=tv2.ravel();result['refinement_status']='success'
                else:result['refinement_status']='failed_using_ransac'
            else:result['refinement_status']='too_few_inliers_using_ransac'
        if not(np.isfinite(R).all() and np.isfinite(t).all()):
            result['status']='nonfinite_pose';return result
        result.update(success=True,status='success',R=R.tolist(),t=t.tolist())
    except (cv2.error,ValueError,TypeError) as e:
        result['status']='exception';result['exception']=str(e)
    return result

def metrics(pose,X,target,K,ids):
    R=np.array(pose['R']);t=np.array(pose['t']);q=X@R.T+t
    displacement=np.linalg.norm(q-X,axis=1)
    uv=(q@K.T);uv=uv[:,:2]/uv[:,2:]
    rep=np.linalg.norm(uv-target,axis=1)
    available=np.all(np.isfinite(target),axis=1)&np.all(target>-999.,axis=1)
    return {'add_all':float(displacement.mean()),'add_input':float(displacement[ids].mean()),
            'angle_deg':float(np.degrees(np.arccos(np.clip((np.trace(R)-1)/2,-1,1)))),
            'translation_norm':float(np.linalg.norm(t)),
            'reprojection_input_mean_px':float(rep[ids].mean()),
            'reprojection_all_mean_px':float(rep.mean()) if available.all() else None,
            'reprojection_available_mean_px':float(rep[available].mean()) if available.any() else None,
            'nonpositive_depth_count':int((q[:,2]<=0).sum())}

def main():
    start=time.monotonic();torch.set_num_threads(2);torch.manual_seed(SEED)
    np.random.seed(SEED);cv2.setNumThreads(1)
    cfg=YAML(typ='safe').load((INPUT/'panda_dream_vgg_q.yaml').read_text())
    cfg['training']['platform']['gpu_ids']=[]
    net=dream.network.DreamNetwork(cfg)
    state=torch.load(INPUT/'panda_dream_vgg_q.pth',map_location='cpu',weights_only=True)
    load=net.model.load_state_dict(state,strict=True)
    assert not load.missing_keys and not load.unexpected_keys
    net.model.eval()
    assert all(torch.equal(v,state[k]) for k,v in net.model.state_dict().items())
    names=net.keypoint_names
    manifest=json.loads((INPUT/'selected/manifest.json').read_text())
    camera=json.loads((INPUT/'selected/_camera_settings.json').read_text())['camera_settings'][0]
    intr=camera['intrinsic_settings'];K=np.array([[intr['fx'],0,intr['cx']],[0,intr['fy'],intr['cy']],[0,0,1.]])
    records=[];(OUT/'arrays').mkdir();(OUT/'overlays').mkdir()
    write('execution.json',{'seed':SEED,'device':'cpu','torch':torch.__version__,'torchvision':torchvision.__version__,
        'opencv':cv2.__version__,'numpy':np.__version__,'checkpoint_sha256':sha(INPUT/'panda_dream_vgg_q.pth'),
        'config_sha256':sha(INPUT/'panda_dream_vgg_q.yaml'),'manifest_sha256':sha(INPUT/'selected/manifest.json'),
        'checkpoint_strict_load':True,'tensor_count':len(state),'all_loaded_tensors_equal':True,
        'preprocessing':cfg['architecture']['image_preprocessing'],'keypoint_names':names,'K':K.tolist(),
        'ransac':{'threshold_px':5.0,'iterations':100,'confidence':0.99,'seed_per_frame':SEED},
        'units':'native annotation coordinates (metres in DREAM convention); no action labels'})
    shutil.copy2('/opt/dependencies.lock',OUT/'dependencies.lock')
    shutil.copy2('/opt/dream_adaptation.json',OUT/'adaptation.json')
    shutil.copy2(INPUT/'selected/manifest.json',OUT/'input_manifest.json')
    for sample in manifest['samples']:
        sid=sample['id']; rec={'id':sid,'ordinal':sample['ordinal']}
        if not sample['annotation_present']:
            rec['status']='missing_annotation';records.append(rec);continue
        im=Image.open(INPUT/'selected'/sample['image']).convert('RGB');w,h=im.size
        ann=json.loads((INPUT/'selected'/sample['annotation']).read_text())
        obj=next(o for o in ann['objects'] if o['class']=='panda')
        kp={k['name']:k for k in obj['keypoints']}
        X=np.array([kp[n]['location'] for n in names],dtype=float)
        gt=np.array([kp[n]['projected_location'] for n in names],dtype=float)
        t0=time.monotonic()
        result=net.keypoints_from_image(im,debug=True)
        pred=result['detected_keypoints']
        avail=np.flatnonzero(np.any(pred>-999.,axis=1))  # official analysis.py convention
        assert np.array_equal(avail,np.flatnonzero(np.all(pred>-999.,axis=1)))
        inframe=np.flatnonzero((gt[:,0]>=0)&(gt[:,0]<w)&(gt[:,1]>=0)&(gt[:,1]<h))
        pe=np.linalg.norm(pred-gt,axis=1)
        rec.update(status='inferred',inference_seconds=time.monotonic()-t0,
                   available_ids=avail.tolist(),gt_inframe_ids=inframe.tolist(),
                   missing_ids=sorted(set(range(len(names)))-set(avail)),
                   keypoint_errors_px=[float(pe[i]) if i in avail else None for i in range(len(names))],solvers={})
        p0=X@K.T;p0=p0[:,:2]/p0[:,2:]
        rec['annotation_projection_max_px']=float(np.linalg.norm(p0-gt,axis=1).max())
        for label,uv,ids,kind in [('official',pred,avail,'official'),('robust',pred,avail,'robust'),
                                ('oracle_common',gt,avail,'official'),('oracle_all',gt,inframe,'official')]:
            sol=solve(X,uv,K,ids,kind)
            if sol['success']:
                sol['metrics']=metrics(sol,X,uv,K,ids)
                if sol.get('inlier_ids'):
                    sol['inlier_metrics']=metrics(sol,X,uv,K,np.array(sol['inlier_ids']))
                if 'ransac_pose' in sol:sol['ransac_metrics']=metrics(sol['ransac_pose'],X,uv,K,ids)
            rec['solvers'][label]=sol
        np.savez_compressed(OUT/'arrays'/f'{sid}.npz',X=X,gt=gt,pred=pred,K=K,
            belief_maps=result['belief_maps'].detach().cpu().numpy(),
            pred_netout=result['detected_keypoints_net_output'])
        draw=ImageDraw.Draw(im)
        for i,(u,v) in enumerate(gt):
            if 0<=u<w and 0<=v<h:draw.ellipse((u-5,v-5,u+5,v+5),outline='lime',width=2);draw.text((u+6,v),str(i),fill='lime')
        for i in avail:
            u,v=pred[i];draw.line((u-4,v,u+4,v),fill='red',width=2);draw.line((u,v-4,u,v+4),fill='red',width=2)
        draw.rectangle((0,0,520,18),fill='black');draw.text((5,3),f'{sid}: green=GT projection, red=prediction; not visibility labels',fill='white')
        im.save(OUT/'overlays'/f'{sid}.png')
        records.append(rec);write('records.json',records)
        print(sid,'points',len(avail),'ADD',{k:round(s['metrics']['add_all'],6) if s['success'] else s['status'] for k,s in rec['solvers'].items()},flush=True)
    summary={'frames':len(records),'inferred':sum(r['status']=='inferred' for r in records),'elapsed_seconds':time.monotonic()-start,'solvers':{}}
    for kind in ['official','robust','oracle_common','oracle_all']:
        sol=[r['solvers'][kind] for r in records if r['status']=='inferred']; ok=[s for s in sol if s['success']]
        summary['solvers'][kind]={'successes':len(ok),'failures':len(records)-len(ok),
            'mean_add_all_success_only':float(np.mean([s['metrics']['add_all'] for s in ok])) if ok else None,
            'median_add_all_success_only':float(np.median([s['metrics']['add_all'] for s in ok])) if ok else None,
            'max_add_all_success_only':max((s['metrics']['add_all'] for s in ok),default=None)}
    write('summary.json',summary)
    write('output_manifest.json',{str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()})
    print(json.dumps(summary),flush=True)

if __name__=='__main__':main()
