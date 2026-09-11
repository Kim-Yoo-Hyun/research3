"""Container-only environment and public demonstration schema receipt."""
import hashlib
import json
import shutil
from pathlib import Path
import h5py
import mani_skill

root=Path('/outputs')
shutil.copyfile('/opt/dependencies.lock',root/'dependencies.lock')
shutil.copyfile('/opt/os-packages.lock',root/'os-packages.lock')
result=dict(inputs={},source={},schema={})
for p in Path('/inputs').iterdir():
    if p.is_file(): result['inputs'][p.name]=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
for name in ['envs/sapien_env.py','envs/scene.py','envs/tasks/tabletop/pick_cube.py',
             'agents/controllers/pd_joint_pos.py','agents/controllers/pd_ee_pose.py']:
    src=Path('/opt/ManiSkill/mani_skill')/name
    installed=Path(mani_skill.__file__).parent/name
    assert src.read_bytes()==installed.read_bytes(), name
    result['source'][name]=hashlib.sha256(src.read_bytes()).hexdigest()
meta=json.loads(Path('/inputs/trajectory.json').read_text())
result['demo_metadata']=dict(env_info=meta['env_info'],commit_info=meta['commit_info'],episodes=len(meta['episodes']))
with h5py.File('/inputs/trajectory.h5') as f:
    result['schema']['trajectories']=len(f)
    fields={}
    f['traj_0'].visititems(lambda name,x: fields.update({name:dict(shape=list(x.shape),dtype=str(x.dtype))}) if isinstance(x,h5py.Dataset) else None)
    result['schema']['traj_0']=fields
with (root/'provenance.json').open('x') as f: json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
