"""Synthetic preflight only; run in the new Docker with no dataset mounted."""
from pathlib import Path
import numpy as np
from audit import validate_array, normalize_controls, original_fps

points=np.array([[2.,1.,0.],[-1.,2.,1.],[3.,-2.,4.],[0.,0.,-1.]])
validate_array(points,4)
for invalid in [np.zeros((4,3)),np.zeros((3,3)),np.full((4,3),np.nan),np.full((4,3),np.inf)]:
    try:
        validate_array(invalid,4)
    except ValueError:
        pass
    else:
        raise AssertionError('malformed/degenerate input accepted')
checks=normalize_controls(points,1e-12,2e-6)
assert checks['controls_pass']
assert checks['online_mean_displacement']>0.1
# Translation/scale changes the inverse's units, but must preserve round-trip validity.
for variant in [points*0.03+8.,points*5.-3.]:
    assert normalize_controls(variant,1e-12,2e-6)['controls_pass']
fps=original_fps(Path(__file__).parent/'upstream/runner.py')
np.random.seed(12001)
actual=fps(points,4)
np.random.seed(12001)
first=int(np.random.randint(0,4));chosen=[first]
while len(chosen)<4:
    distances=[min(sum((points[i,j]-points[k,j])**2 for j in range(3)) for k in chosen) for i in range(4)]
    chosen.append(max(range(4),key=lambda i:distances[i]))
assert np.array_equal(actual,points[chosen])
assert len(np.unique(actual,axis=0))==4
print('PASS: invalid-input rejection; inverse/7-6 controls; transformation invariance; source FPS against exhaustive reference')

# End-to-end fixtures exercise receipt/freeze enforcement, the output denominator and independent verification.
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

base=Path(__file__).parent
with tempfile.TemporaryDirectory() as temp:
    task=Path(temp)/'study';task.mkdir()
    for name in ['audit.py','verify.py']:
        shutil.copy2(base/name,task/name)
    shutil.copytree(base/'upstream',task/'upstream')
    config=json.loads((base/'protocol.json').read_text());config.update(partial_points=4,gt_points=8)
    (task/'protocol.json').write_text(json.dumps(config))
    input_root=Path(temp)/'input';pairs=[];files=[]
    for i in range(4):
        obj=f'object_{i//2}'
        pair={'object':obj,'partial_member':f'input/{obj}/test/{i}_x.xyz','gt_member':f'gt/{obj}/test/{i}_y.xyz'}
        pairs.append(pair)
        for field,array in [('partial_member',points+i),('gt_member',np.vstack([points+i,points+i+0.2]))]:
            path=input_root/'subset'/pair[field];path.parent.mkdir(parents=True,exist_ok=True)
            np.savetxt(path,array,fmt='%.17g')
            files.append({'path':str(path.relative_to(input_root)),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    def freeze_fixture():
        (task/'inputs.json').write_text(json.dumps({'selected_pairs':pairs,'selected_files':files}))
        frozen={'files':{n:hashlib.sha256((task/n).read_bytes()).hexdigest() for n in ['audit.py','verify.py','inputs.json','protocol.json','upstream/runner.py']}}
        (task/'freeze.json').write_text(json.dumps(frozen))
    freeze_fixture()
    def execute(label):
        out=Path(temp)/label
        subprocess.run([sys.executable,str(task/'audit.py'),'--inputs',str(input_root),'--output',str(out)],check=True)
        subprocess.run([sys.executable,str(task/'verify.py'),'--inputs',str(input_root),'--result',str(out),'--output',str(Path(temp)/(label+'.verified.json'))],check=True)
        return json.loads((out/'results.json').read_text())
    result=execute('valid')
    assert result['decision']=='INPUT_CONTROLS_VALID_PHYSICAL_FRAME_UNRESOLVED'
    assert all(r['supplied_frame_distances']['partial_to_gt']['max']==0 for r in result['pairs'])
    last=input_root/'subset'/pairs[-1]['partial_member'];np.savetxt(last,points[:3]+3,fmt='%.17g')
    for entry in files:
        path=input_root/entry['path'];entry.update(bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    freeze_fixture()
    result=execute('invalid_shape')
    assert result['decision']=='REFINE_INPUT_SCHEMA' and len(result['pairs'])==4
    # Changed raw bytes must fail integrity even if valid XYZ could otherwise be parsed.
    with last.open('a') as f:f.write('0 0 0\n')
    invalid=Path(temp)/'corrupt'
    status=subprocess.run([sys.executable,str(task/'audit.py'),'--inputs',str(input_root),'--output',str(invalid)])
    assert status.returncode==2
    assert json.loads((invalid/'results.json').read_text())['decision']=='INVALID_INPUT_OR_SOURCE_INTEGRITY'
print('PASS: end-to-end four-pair fixture; wrong-shape denominator retained; corrupted-input rejection; independent verification')
