"""Fix an unused full-point reprojection diagnostic when predictions are absent.

Original observation stays intact. ADD, input-point residuals, poses and selection
results are unchanged. Check the repaired metric on saved observations only.
"""
import json
import hashlib
from pathlib import Path
import numpy as np
import cv2
from observe import metrics

root=Path('/result');out=Path('/output');rows=json.loads((root/'records.json').read_text())
corrected=[];checks=0
for row in rows:
    a=np.load(root/'arrays'/f"{row['id']}.npz");X,gt,pred,K=[a[k] for k in ['X','gt','pred','K']]
    for kind,s in row['solvers'].items():
        if not s['success']:continue
        target=gt if kind.startswith('oracle') else pred
        ids=np.array(s['input_ids']);m=metrics(s,X,target,K,ids)
        for key in ['add_all','add_input','angle_deg','translation_norm','reprojection_input_mean_px','nonpositive_depth_count']:
            assert np.isclose(m[key],s['metrics'][key],atol=1e-12);checks+=1
        uv,_=cv2.projectPoints(X,cv2.Rodrigues(np.array(s['R']))[0],np.array(s['t']),K,None)
        valid=np.all(target>-999.,axis=1)
        independent=float(np.linalg.norm(uv[valid,0,:]-target[valid],axis=1).mean())
        assert np.isclose(independent,m['reprojection_available_mean_px'],atol=1e-8);checks+=1
        assert (m['reprojection_all_mean_px'] is None)==(not valid.all())
        corrected.append({'id':row['id'],'solver':kind,'metrics':m})
payload={'status':'pass','numeric_checks':checks,'new_model_inferences':0,
 'reason':'Original unused reprojection_all_mean_px included missing-point sentinels in 002583 official/robust; use null when full-point reprojection is unavailable and separately report available-point residual.',
 'unchanged':'All poses, ADD, input-point residuals, oracle comparisons and post hoc selection.',
 'corrected_metrics':corrected}
(out/'metrics.json').write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
(out/'output_manifest.json').write_text(json.dumps({'metrics.json':hashlib.sha256((out/'metrics.json').read_bytes()).hexdigest()},indent=2)+'\n')
print(json.dumps({k:v for k,v in payload.items() if k!='corrected_metrics'}))
