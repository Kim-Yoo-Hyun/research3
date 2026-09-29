"""Fixed nearest-neighbor action-conditioned object transition model; Docker only."""
import hashlib
import json
from pathlib import Path
import time

import numpy as np
from scipy.spatial import cKDTree

from repeat_bc import data_arrays

ROOT = Path('/output')
OUT = ROOT / 'fit_model1'
K = 32


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def wrap(angle):
    return np.arctan2(np.sin(angle), np.cos(angle))


def features(state, action):
    state = np.asarray(state, np.float64).reshape(-1, 5)
    action = np.asarray(action, np.float64).reshape(-1, 2)
    assert len(state) == len(action)
    return np.column_stack(((state[:, :2] - state[:, 2:4]) / 100.0,
                            np.sin(state[:, 4]), np.cos(state[:, 4]),
                            (action - state[:, :2]) / 100.0,
                            state[:, 2:4] / 256.0))


def episode_transition_indices(ends, start, stop):
    begins = np.r_[0, ends[:-1]]
    return np.concatenate([np.arange(int(begins[i]), int(ends[i])-1)
                           for i in range(start, stop)]).astype(np.int64)


def targets(states, indices):
    current = states[indices, 2:5]
    following = states[indices+1, 2:5]
    delta = following - current
    delta[:, 2] = wrap(delta[:, 2])
    return delta


def predict(tree, training_targets, state, action):
    x = features(state, action)
    distance, neighbors = tree.query(x, k=K, workers=1)
    weights = 1.0 / np.maximum(distance, 1e-6) ** 2
    weights /= weights.sum(axis=1, keepdims=True)
    delta = np.sum(training_targets[neighbors] * weights[..., None], axis=1)
    return delta, distance[:, 0], np.sum(weights * distance, axis=1)


def errors(predicted, true, mask):
    if not np.any(mask):
        return dict(rows=0, xy_rmse_px=None, yaw_rmse_rad=None)
    error = predicted[mask] - true[mask]
    error[:, 2] = wrap(error[:, 2])
    return dict(rows=int(mask.sum()),
                xy_rmse_px=float(np.sqrt(np.mean(np.sum(error[:, :2] ** 2, axis=1)))),
                yaw_rmse_rad=float(np.sqrt(np.mean(error[:, 2] ** 2))))


def main():
    OUT.mkdir(exist_ok=False)
    started = time.perf_counter()
    states, actions, ends = data_arrays()
    train = episode_transition_indices(ends, 0, 160)
    valid = episode_transition_indices(ends, 160, 180)
    assert train[-1] < ends[159] and valid[0] >= ends[159] and valid[-1] < ends[179]
    x_train = features(states[train], actions[train])
    y_train = targets(states, train)
    x_valid = features(states[valid], actions[valid])
    y_valid = targets(states, valid)
    tree = cKDTree(x_train)
    prediction, near, weighted_near = predict(tree, y_train, states[valid], actions[valid])
    moving = np.linalg.norm(y_valid[:, :2], axis=1) > 1.0
    path = OUT / 'model.npz'
    np.savez_compressed(path, features=x_train, targets=y_train, train_indices=train)
    doc = dict(status='completed', model='32-neighbor inverse-square-weighted transition regression',
               k=K, source_zip_sha256=digest(ROOT / 'demos/pusht.zip'),
               train_episode_ids=[0, 159], validation_episode_ids=[160, 179],
               unused_episode_ids=[180, 205], train_transitions=len(train),
               validation_transitions=len(valid), features=8, target='next object XY/yaw delta',
               all_validation=errors(prediction, y_valid, np.ones(len(valid), bool)),
               moving_validation=errors(prediction, y_valid, moving),
               validation_nearest_distance=dict(p50=float(np.quantile(near, .5)),
                                                p90=float(np.quantile(near, .9)),
                                                p99=float(np.quantile(near, .99))),
               validation_weighted_distance_p90=float(np.quantile(weighted_near, .9)),
               fit_and_validation_seconds=time.perf_counter()-started,
               checkpoint=path.name, checkpoint_sha256=digest(path))
    (OUT / 'fit.json').write_text(json.dumps(doc, indent=2, allow_nan=False) + '\n')
    print(json.dumps({key: doc[key] for key in ('train_transitions', 'validation_transitions',
                                              'all_validation', 'moving_validation',
                                              'fit_and_validation_seconds')}, indent=2), flush=True)


if __name__ == '__main__':
    main()
