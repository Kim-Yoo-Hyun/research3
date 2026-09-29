"""Docker-only independent geometry/metric checks and saved-output diagnosis."""
import hashlib
import json
import math
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw
import torch
import dream

ROOT=Path('/result');OUT=Path('/output');INPUT=Path('/input')
comparisons=[]
def close(a,b,atol=1e-9):
    aa=np.asarray(a);bb=np.asarray(b)
    assert np.allclose(aa,bb,atol=atol,rtol=1e-8),(aa,bb)
    comparisons.append(float(np.max(np.abs(aa-bb))) if aa.size else 0.)
def dump(name,obj):(OUT/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def direct(X,uv,K):
    ok,rv,t=cv2.solvePnP(X,uv,K,None,flags=cv2.SOLVEPNP_EPNP);assert ok
    ok,rv,t=cv2.solvePnP(X,uv,K,None,rv,t,True,flags=cv2.SOLVEPNP_ITERATIVE);assert ok
    return cv2.Rodrigues(rv)[0],t.ravel()
def independent_metrics(R,t,X,uv,K,ids):
    # Homogeneous column-vector convention, scalar distances and OpenCV projection.
    T=np.eye(4);T[:3,:3]=R;T[:3,3]=t
    moved=(T@np.column_stack([X,np.ones(len(X))]).T).T[:,:3]
    dis=[math.dist(a,b) for a,b in zip(moved,X)]
    rotvec,_=cv2.Rodrigues(R)
    pixels,_=cv2.projectPoints(X,rotvec,t,K,None)
    rep=[math.dist(a,b) for a,b in zip(pixels[:,0,:],uv)]
    return {'add_all':sum(dis)/len(dis),'add_input':sum(dis[i] for i in ids)/len(ids),
        'angle_deg':math.degrees(float(np.linalg.norm(rotvec))),
        'translation_norm':math.sqrt(sum(float(v*v) for v in t)),
        'reprojection_input_mean_px':sum(rep[i] for i in ids)/len(ids),
        'reprojection_all_mean_px':sum(rep)/len(rep),
        'nonpositive_depth_count':int((moved[:,2]<=0).sum())}

def main():
    cv2.setNumThreads(1);torch.set_num_threads(2)
    manifest=json.loads((ROOT/'output_manifest.json').read_text())
    for rel,h in manifest.items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h
    inputs=json.loads((ROOT/'input_manifest.json').read_text())
    for f in inputs['files']:
        assert hashlib.sha256((INPUT/'selected'/f['name']).read_bytes()).hexdigest()==f['sha256']
    ids=[s['id'] for s in inputs['samples']]
    assert [s['ordinal'] for s in inputs['samples']]==[k*(inputs['rgb_population']-1)//23 for k in range(24)]
    rows=json.loads((ROOT/'records.json').read_text());assert [r['id'] for r in rows]==ids
    names=json.loads((ROOT/'execution.json').read_text())['keypoint_names']
    diagnostic=[]
    for row in rows:
        assert row['status']=='inferred'
        a=np.load(ROOT/'arrays'/f"{row['id']}.npz")
        X,gt,pred,K=[a[k] for k in ['X','gt','pred','K']]
        ann=json.loads((INPUT/'selected'/f"{row['id']}.json").read_text())['objects'][0]['keypoints']
        byname={k['name']:k for k in ann}
        close(X,[byname[n]['location'] for n in names],0);close(gt,[byname[n]['projected_location'] for n in names],0)
        close((K@X.T).T[:,:2]/X[:,2,None],gt)
        # Independently check returned resize coordinates from saved network-output points.
        close(a['pred_netout']*np.array([6.4,4.8]),pred)
        peaks=dream.image_proc.peaks_from_belief_maps(torch.from_numpy(a['belief_maps']),offset_due_to_upsampling=.4395)
        restored=[]
        for peak in peaks:
            peak=sorted(peak,key=lambda p:p[2],reverse=True)
            restored.append(peak[0][:2] if len(peak)==1 or (len(peak)>1 and peak[0][2]-peak[1][2]>=.25) else [-999.999,-999.999])
        close(np.asarray(restored,dtype=np.float32),a['pred_netout'],1e-6)
        avail=row['available_ids'];inframe=row['gt_inframe_ids']
        assert avail==np.flatnonzero(np.all(pred>-999.,axis=1)).tolist()
        for i in avail:close(math.dist(pred[i],gt[i]),row['keypoint_errors_px'][i])
        for kind,s in row['solvers'].items():
            assert s['success']
            uv=gt if kind.startswith('oracle') else pred
            expected=inframe if kind=='oracle_all' else avail
            assert s['input_ids']==expected
            R=np.array(s['R']);t=np.array(s['t'])
            close(R.T@R,np.eye(3));close(np.linalg.det(R),1.)
            mm=independent_metrics(R,t,X,uv,K,expected)
            for key,val in mm.items():
                if key=='reprojection_all_mean_px' and s['metrics'][key] is None:
                    assert not np.all(uv>-999.);continue
                close(val,s['metrics'][key],3e-6 if key=='angle_deg' else 1e-9)
            if kind!='robust':
                R2,t2=direct(X[expected].copy(),uv[expected].copy(),K)
                close(R2,R,1e-7);close(t2,t,1e-7)
            else:
                cv2.setRNGSeed(20260916)
                ok,rv,tv,ii=cv2.solvePnPRansac(X[avail],pred[avail],K,None,iterationsCount=100,
                    reprojectionError=5.,confidence=.99,flags=cv2.SOLVEPNP_EPNP)
                assert ok and [avail[i] for i in ii.ravel()]==s['inlier_ids']
                close(cv2.Rodrigues(rv)[0],s['ransac_pose']['R']);close(tv.ravel(),s['ransac_pose']['t'])
                if s['refinement_status']=='success':
                    ids2=np.array(s['inlier_ids']);ok,rv,tv=cv2.solvePnP(X[ids2],pred[ids2],K,None,rv,tv,True,flags=cv2.SOLVEPNP_ITERATIVE)
                    assert ok;close(cv2.Rodrigues(rv)[0],R);close(tv.ravel(),t)
                for tag,pose,subset in [('ransac_metrics',s['ransac_pose'],avail),('inlier_metrics',s,s['inlier_ids'])]:
                    im=independent_metrics(np.array(pose['R']),np.array(pose['t']),X,uv,K,subset)
                    for key,val in im.items():
                        if key=='reprojection_all_mean_px' and s[tag][key] is None:
                            assert not np.all(uv>-999.);continue
                        close(val,s[tag][key],3e-6 if key=='angle_deg' else 1e-9)
        base=row['solvers']['official'];rob=row['solvers']['robust']
        diagnostic.append({'id':row['id'],'available':len(avail),'inliers':rob['inlier_ids'],
            'keypoint_errors_px':row['keypoint_errors_px'],
            'official_add':base['metrics']['add_all'],'robust_add':rob['metrics']['add_all'],
            'ransac_unrefined_add':rob['ransac_metrics']['add_all'],
            'robust_minus_official':rob['metrics']['add_all']-base['metrics']['add_all'],
            'official_angle_deg':base['metrics']['angle_deg'],'robust_angle_deg':rob['metrics']['angle_deg'],
            'official_reprojection':base['metrics']['reprojection_input_mean_px'],
            'robust_all_reprojection':rob['metrics']['reprojection_input_mean_px'],
            'robust_inlier_reprojection':rob['inlier_metrics']['reprojection_input_mean_px']})
    # Known nondegenerate synthetic pose and changed-coordinate comparison.
    rng=np.random.default_rng(20260916);B=rng.uniform(-.3,.3,(12,3)).astype(np.float64)
    Rt=cv2.Rodrigues(np.array([.2,-.3,.1]))[0];tt=np.array([.1,-.2,2.])
    C=B@Rt.T+tt;K=np.array([[600.,0,320],[0,600,240],[0,0,1.]])
    uv=(C@K.T);uv=uv[:,:2]/uv[:,2:]
    Rb,tb=direct(B,uv,K);Rc,tc=direct(C,uv,K)
    close(Rb,Rt,1e-7);close(tb,tt,1e-7);close(Rc,np.eye(3),1e-7);close(tc,np.zeros(3),1e-7)
    noisy=uv+rng.normal(0,.3,uv.shape)
    Rb,tb=direct(B,noisy,K);Rc,tc=direct(C,noisy,K)
    close(Rc@Rt,Rb,1e-6);close(Rc@tt+tc,tb,1e-6)
    close(np.linalg.norm(B@Rb.T+tb-C,axis=1),np.linalg.norm(C@Rc.T+tc-C,axis=1),1e-6)
    summary=json.loads((ROOT/'summary.json').read_text())
    for kind,reported in summary['solvers'].items():
        vals=[r['solvers'][kind]['metrics']['add_all'] for r in rows]
        close(sum(vals)/len(vals),reported['mean_add_all_success_only'])
        close(np.median(vals),reported['median_add_all_success_only']);close(max(vals),reported['max_add_all_success_only'])
        assert reported['successes']==24 and reported['failures']==0
    diagnosis={'scope':'post-observation diagnosis; no new inference/fits','frames':diagnostic,
        'robust_better_1e-8':sum(r['robust_minus_official'] < -1e-8 for r in diagnostic),
        'robust_worse_1e-8':sum(r['robust_minus_official'] > 1e-8 for r in diagnostic),
        'equal_within_1e-8':sum(abs(r['robust_minus_official'])<=1e-8 for r in diagnostic),
        'all_points_available':all(r['available']==7 for r in diagnostic),
        'native_coordinate_units_preserved':True}
    dump('diagnosis.json',diagnosis)
    canvas=Image.new('RGB',(1280,6*262),'white')
    for i,row in enumerate(diagnostic):
        im=Image.open(ROOT/'overlays'/f"{row['id']}.png").resize((320,240))
        x=(i%4)*320;y=(i//4)*262;canvas.paste(im,(x,y))
        ImageDraw.Draw(canvas).text((x+3,y+243),f"ADD {row['official_add']:.4f} -> {row['robust_add']:.4f}, inliers {len(row['inliers'])}",fill='black')
    canvas.save(OUT/'contact_sheet.png')
    dump('verification.json',{'status':'pass','numeric_comparisons':len(comparisons),
        'max_numeric_difference':max(comparisons),'input_hashes':len(inputs['files']),
        'output_hashes':len(manifest),'synthetic_pose_and_frame_composition':'pass',
        'baseline_direct_opencv_reconstruction':'pass','heatmap_peak_and_resize_reconstruction':'pass',
        'ransac_and_refinement_reconstruction':'pass','independent_homogeneous_metric_calculation':'pass',
        'no_new_model_inference':True})
    dump('output_manifest.json',{str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.rglob('*') if p.is_file()})
    print((OUT/'verification.json').read_text());print('robust better/worse/equal',diagnosis['robust_better_1e-8'],diagnosis['robust_worse_1e-8'],diagnosis['equal_within_1e-8'])

if __name__=='__main__':main()
