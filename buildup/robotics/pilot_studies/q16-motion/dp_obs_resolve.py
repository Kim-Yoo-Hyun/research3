"""Resolve stored-vs-current keypoint map drift before a state-derived adapter."""
import hashlib
import json
from pathlib import Path

import numpy as np
import zarr

from dp_observation import ObservationGeometry, wrap

ROOT=Path('/output')
OUT=ROOT/'observation2'
ZIP=Path('/previous/demos/pusht.zip')


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    OUT.mkdir(exist_ok=False)
    prior=json.loads((ROOT/'observation1/assessment.json').read_text())
    assert prior['status']=='incompatible'
    geo=ObservationGeometry()
    store=zarr.ZipStore(str(ZIP),mode='r')
    try:
        group=zarr.open_group(store=store,path='pusht/pusht_cchi_v7_replay.zarr',mode='r')
        state=np.asarray(group['data/state'][:],np.float64)
        keypoints=np.asarray(group['data/keypoint'][:],np.float64)
        actions=np.asarray(group['data/action'][:],np.float64)
        ends=np.asarray(group['meta/episode_ends'][:],np.int64)
    finally:
        store.close()
    assert state.shape==(25650,5) and keypoints.shape==(25650,9,2)
    assert actions.shape==(25650,2) and ends.shape==(206,) and ends[-1]==len(state)
    assert np.isfinite(state).all() and np.isfinite(keypoints).all() and np.isfinite(actions).all()
    angle=state[:,4]
    rot=np.empty((len(state),2,2),np.float64)
    rot[:,0,0]=np.cos(angle);rot[:,0,1]=np.sin(angle)
    rot[:,1,0]=-np.sin(angle);rot[:,1,1]=np.cos(angle)
    regenerated=np.einsum('ki,nij->nkj',geo.local,rot)+state[:,None,2:4]
    raw_error=np.linalg.norm(regenerated-keypoints,axis=2)
    derived_local=np.einsum('nki,nji->nkj',keypoints-state[:,None,2:4],rot)
    median_local=np.median(derived_local,axis=0)
    variation=np.linalg.norm(derived_local-median_local,axis=2)
    map_difference=np.linalg.norm(median_local-geo.local,axis=1)
    roundtrip=[]
    for idx in np.unique(np.linspace(0,len(state)-1,128,dtype=int)):
        derived=np.r_[regenerated[idx].flatten(),state[idx,:2]]
        decoded=geo.decode(derived)
        roundtrip.append(max(float(np.max(np.abs(decoded[:4]-state[idx,:4]))),
                             abs(wrap(decoded[4]-state[idx,4]))))
    live_error=[]
    for seed in range(49000,49008):
        with np.load(ROOT/'eval1'/f'released_dp_{seed}.npz',allow_pickle=False) as data:
            obs=data['policy_observation']; truth=data['observation']
            for idx in np.unique(np.linspace(0,len(obs)-1,12,dtype=int)):
                decoded=geo.decode(obs[idx])
                live_error.append(max(float(np.max(np.abs(decoded[:4]-truth[idx,:4]))),
                                      abs(wrap(decoded[4]-truth[idx,4]))))
    status='passed' if max(roundtrip+live_error)<=1e-5 and np.quantile(variation,.999)<=.01 else 'incompatible'
    result=dict(status=status,source_zip_sha256=digest(ZIP),
                previous_assessment_sha256=digest(ROOT/'observation1/assessment.json'),
                rows=len(state),episodes=len(ends),training_episodes=160,validation_episodes=20,
                stored_vs_current_keypoint_px=dict(p50=float(np.quantile(raw_error,.5)),
                    p99=float(np.quantile(raw_error,.99)),max=float(np.max(raw_error))),
                inferred_stored_map_variation_px=dict(p50=float(np.quantile(variation,.5)),
                    p999=float(np.quantile(variation,.999)),max=float(np.max(variation))),
                stored_vs_current_local_map_px=dict(mean=float(np.mean(map_difference)),
                                                     max=float(np.max(map_difference))),
                regenerated_roundtrip_max=float(max(roundtrip)),
                live_inverse_pose_max=float(max(live_error)),
                adapter='Use recorded state and current pinned source local map; ignore stored keypoint values for policy update.',
                local_current=geo.local.tolist(),local_stored_estimate=median_local.tolist())
    (OUT/'assessment.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ('status','rows','stored_vs_current_keypoint_px',
                       'inferred_stored_map_variation_px','stored_vs_current_local_map_px',
                       'regenerated_roundtrip_max','live_inverse_pose_max')},indent=2),flush=True)
    assert status=='passed', 'Recorded state/keypoint relationship is not stable.'


if __name__=='__main__':
    main()
