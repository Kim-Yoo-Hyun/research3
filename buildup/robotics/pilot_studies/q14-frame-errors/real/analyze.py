"""Docker-only, post hoc saved-pose selection: no extra model inference/fit."""
import hashlib
import json
from pathlib import Path
import numpy as np
import cv2

root=Path('/result');out=Path('/output')
rows=json.loads((root/'records.json').read_text());results=[]
for r in rows:
    a=np.load(root/'arrays'/f"{r['id']}.npz")
    X,pred,K=[a[k] for k in ['X','pred','K']];ids=np.array(r['available_ids'])
    scores={};errors={}
    for name in ['official','robust']:
        s=r['solvers'][name]
        if not s['success']:scores[name]=None;continue
        R=np.array(s['R']);t=np.array(s['t']);q=X@R.T+t
        pix=q@K.T;pix=pix[:,:2]/pix[:,2:]
        score=float(np.square(pix[ids]-pred[ids]).sum(axis=1).mean())
        # Independent library projection check for the new selection score.
        uv,_=cv2.projectPoints(X,cv2.Rodrigues(R)[0],t,K,None)
        score2=sum(float(np.dot(uv[i,0]-pred[i],uv[i,0]-pred[i])) for i in ids)/len(ids)
        assert np.isclose(score,score2,atol=1e-8,rtol=1e-9)
        scores[name]=score
        errors[name]=float(np.linalg.norm(q-X,axis=1).mean())
        assert np.isclose(errors[name],s['metrics']['add_all'],atol=1e-12)
    valid=[k for k,v in scores.items() if v is not None]
    selected=min(valid,key=lambda k:scores[k]) if valid else None
    singular=np.linalg.svd(X[ids]-X[ids].mean(axis=0),compute_uv=False)
    results.append({'id':r['id'],'available_ids':ids.tolist(),'gt_inframe_ids':r['gt_inframe_ids'],
        'all_point_reprojection_mse_px2':scores,'selected':selected,'add_all':errors.get(selected),
        'official_add':errors.get('official'),'robust_add':errors.get('robust'),
        'centered_3d_singular_values':singular.tolist(),
        'smallest_largest_singular_ratio':float(singular[-1]/singular[0])})
v=[r['add_all'] for r in results if r['add_all'] is not None]
summary={'scope':'post hoc saved-pose selection; evaluated on same 24 frames that prompted it',
    'selection_access':['predicted 2D keypoints','privileged camera-frame 3D points','K','two saved pose estimates'],
    'GT_2D_and_ADD_used_for_selection':False,'new_detector_inferences':0,'new_fits':0,
    'successes':len(v),'failures':len(rows)-len(v),'mean_add_all':float(np.mean(v)),
    'median_add_all':float(np.median(v)),'max_add_all':float(max(v)),
    'selected_robust':sum(r['selected']=='robust' for r in results),
    'lower_reprojection_but_higher_add_ids':[r['id'] for r in results if r['add_all']>min(r['official_add'],r['robust_add'])+1e-8],
    'no_missing_inframe_keypoint':all(r['available_ids']==r['gt_inframe_ids'] for r in results)}
(out/'selection.json').write_text(json.dumps({'summary':summary,'frames':results},indent=2)+'\n')
(out/'output_manifest.json').write_text(json.dumps({'selection.json':hashlib.sha256((out/'selection.json').read_bytes()).hexdigest()},indent=2)+'\n')
print(json.dumps(summary),flush=True)
for r in results:
    if r['id'] in ['001033','001808','002583','000516']:print(json.dumps(r))
