"""Check official demonstration keypoints and live keypoint pose inversion in Docker."""
import hashlib
import json
from pathlib import Path

import numpy as np
import zarr

from dp_observation import ObservationGeometry, wrap

ROOT=Path('/output')
OUT=ROOT/'observation1'
ZIP=Path('/previous/demos/pusht.zip')


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    OUT.mkdir(exist_ok=False)
    geo=ObservationGeometry()
    store=zarr.ZipStore(str(ZIP),mode='r')
    try:
        group=zarr.open_group(store=store,path='pusht/pusht_cchi_v7_replay.zarr',mode='r')
        states=group['data/state']
        keypoints=group['data/keypoint']
        actions=group['data/action']
        ends=np.asarray(group['meta/episode_ends'][:],np.int64)
        assert states.shape==(25650,5) and keypoints.shape==(25650,9,2)
        assert actions.shape==(25650,2) and ends.shape==(206,)
        indices=np.unique(np.linspace(0,int(ends[179])-1,24,dtype=np.int64))
        dataset_errors=[]
        decode_errors=[]
        for idx in indices:
            state=np.asarray(states[idx],np.float64)
            observed=np.r_[np.asarray(keypoints[idx]).flatten(),state[:2]]
            forward=geo.from_state(state)
            recovered=geo.decode(observed)
            dataset_errors.append(float(np.max(np.abs(forward-observed))))
            decode_errors.append(float(max(np.max(np.abs(recovered[:4]-state[:4])),
                                           abs(wrap(recovered[4]-state[4])))))
    finally:
        store.close()
    live_errors=[]; overlap_errors=[]
    for seed in range(49000,49008):
        with np.load(ROOT/'eval1'/f'released_dp_{seed}.npz',allow_pickle=False) as saved:
            states=saved['observation']
            obs=saved['policy_observation']
            coverage=saved['coverage']
            for i in np.unique(np.linspace(0,len(states)-1,12,dtype=int)):
                recovered=geo.decode(obs[i])
                live_errors.append(float(max(np.max(np.abs(recovered[:4]-states[i,:4])),
                                             abs(wrap(recovered[4]-states[i,4])))))
                overlap_errors.append(abs(geo.overlap(recovered)-float(coverage[i])))
    maximum=max(dataset_errors+decode_errors+live_errors+overlap_errors)
    result=dict(status='passed' if maximum<=1e-5 else 'incompatible',
                dataset_zip_sha256=digest(ZIP),
                source_checkpoint_sha256=digest(Path('/checkpoint/model.ckpt')),
                source_eval_verification_sha256=digest(ROOT/'eval1/verification.json'),
                dataset_rows=25650,episodes=206,sampled_dataset_rows=len(indices),
                sampled_live_states=len(live_errors),
                max_dataset_keypoint_px=float(max(dataset_errors)),
                max_dataset_inverse_pose_px_or_rad=float(max(decode_errors)),
                max_live_inverse_pose_px_or_rad=float(max(live_errors)),
                max_live_native_overlap_difference=float(max(overlap_errors)),
                local_keypoints=geo.local.tolist(),goal_pose=geo.goal.tolist(),
                train_episode_ids=[0,159],validation_episode_ids=[160,179],
                unused_episode_ids=[180,205])
    (OUT/'assessment.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ('status','sampled_dataset_rows','sampled_live_states',
                    'max_dataset_keypoint_px','max_live_inverse_pose_px_or_rad',
                    'max_live_native_overlap_difference')},indent=2),flush=True)
    assert maximum<=1e-5, f'Observation/data contract drift: {maximum}'


if __name__=='__main__':
    main()
