"""Freeze the official ZIP's stored low-dimensional policy input and split."""
import hashlib
import json
from pathlib import Path

import numpy as np
import zarr

ROOT=Path('/output')
OUT=ROOT/'traincontract1'
ZIP=Path('/previous/demos/pusht.zip')
SOURCE=Path('/source/diffusion_policy/dataset/pusht_dataset.py')


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    OUT.mkdir(exist_ok=False)
    previous=json.loads((ROOT/'observation2/assessment.json').read_text())
    assert previous['status']=='incompatible'
    assert SOURCE.is_file()
    store=zarr.ZipStore(str(ZIP),mode='r')
    try:
        group=zarr.open_group(store=store,path='pusht/pusht_cchi_v7_replay.zarr',mode='r')
        keypoint=np.asarray(group['data/keypoint'][:],np.float32)
        state=np.asarray(group['data/state'][:],np.float32)
        action=np.asarray(group['data/action'][:],np.float32)
        ends=np.asarray(group['meta/episode_ends'][:],np.int64)
    finally:
        store.close()
    assert keypoint.shape==(25650,9,2) and state.shape==(25650,5)
    assert action.shape==(25650,2) and ends.shape==(206,) and ends[-1]==25650
    assert np.all(np.diff(ends)>0)
    assert all(np.isfinite(x).all() for x in (keypoint,state,action))
    assert np.all((action>=0)&(action<=512))
    # This is PushTLowdimDataset._sample_to_data, not pose regeneration.
    obs=np.concatenate((keypoint.reshape(len(keypoint),18),state[:,:2]),axis=1)
    assert obs.shape==(25650,20)
    assert np.array_equal(obs[:,18:20],state[:,:2])
    path=OUT/'dataset.npz'
    np.savez_compressed(path,obs=obs,action=action,ends=ends)
    result=dict(status='passed',source_zip_sha256=digest(ZIP),
                source_dataset_code_sha256=digest(SOURCE),
                prior_full_data_audit_sha256=digest(ROOT/'observation2/assessment.json'),
                data_contract='keypoint.reshape(T,18) concatenated with state[:,0:2]; paired action at same row',
                stored_keypoint_observations=True,regenerated_keypoints=False,
                rows=len(obs),episodes=len(ends),train_episodes=[0,159],
                validation_episodes=[160,179],unused_episodes=[180,205],
                train_rows=int(ends[159]),validation_rows=int(ends[179]-ends[159]),
                observation_shape=list(obs.shape),action_shape=list(action.shape),
                dataset=path.name,dataset_sha256=digest(path))
    (OUT/'assessment.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','rows','train_rows','validation_rows',
                                            'dataset_sha256')},indent=2),flush=True)


if __name__=='__main__':
    main()
