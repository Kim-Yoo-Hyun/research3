"""Independent source, candidate, prediction and paired-trace checks for the contrast."""
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

from repeat_action_model import episode_transition_indices, features, targets, wrap
from repeat_bc import action_from_model, data_arrays

ROOT = Path('/output')
OUT = ROOT / 'contrast1'
NAMES = ('bc', 'feedback', 'x_plus', 'x_minus', 'y_plus', 'y_minus')


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def check_close(actual, expected, tol=1e-9):
    assert np.max(np.abs(np.asarray(actual)-np.asarray(expected))) <= tol


def main():
    doc = json.loads((OUT / 'assessment.json').read_text())
    meta = json.loads((ROOT / 'fit_model1/fit.json').read_text())
    prior = json.loads((ROOT / 'failure_branch1/assessment.json').read_text())
    assert doc['status'] == 'completed' and doc['seeds'] == [48007, 48010] and doc['horizon'] == 11
    assert doc['source_evaluation_sha256'] == digest(ROOT / 'bc_eval1/evaluation.json')
    assert doc['previous_branch_sha256'] == digest(ROOT / 'failure_branch1/assessment.json')
    assert doc['bc_checkpoint_sha256'] == digest(ROOT / 'bc_fit1/ridge.npz')
    assert doc['predictor_fit_sha256'] == digest(ROOT / 'fit_model1/fit.json')
    assert doc['predictor_checkpoint_sha256'] == digest(ROOT / 'fit_model1/model.npz')
    assert meta['source_zip_sha256'] == digest(ROOT / 'demos/pusht.zip')
    states, actions, ends = data_arrays()
    training = episode_transition_indices(ends, 0, 160)
    validation = episode_transition_indices(ends, 160, 180)
    assert meta['train_transitions'] == len(training) and meta['validation_transitions'] == len(validation)
    assert training[-1] < validation[0] and validation[-1] < ends[179]
    with np.load(ROOT / 'fit_model1/model.npz', allow_pickle=False) as saved:
        x_train, y_train, ids = (saved[key].copy() for key in ('features', 'targets', 'train_indices'))
    assert np.array_equal(ids, training)
    check_close(x_train, features(states[training], actions[training]))
    check_close(y_train, targets(states, training))
    tree = cKDTree(x_train)
    with np.load(ROOT / 'bc_fit1/ridge.npz', allow_pickle=False) as saved:
        mean, std, coef = (saved[key].copy() for key in ('mean', 'std', 'coef'))
    result = []
    for case in doc['cases']:
        seed = case['seed']
        earlier = next(x for x in prior['cases'] if x['seed'] == seed)
        assert case['selected_step'] == earlier['selected_step']
        assert case['source_trace'] == earlier['source_trace']
        assert case['source_sha256'] == earlier['source_sha256']
        assert digest(ROOT / 'bc_eval1' / case['source_trace']) == case['source_sha256']
        with np.load(ROOT / 'bc_eval1' / case['source_trace'], allow_pickle=False) as saved:
            original = {key: saved[key].copy() for key in saved.files}
        step = case['selected_step']
        split_obs, split_full, split_coverage = (original[key][step] for key in
                                                 ('observation', 'full', 'coverage'))
        check_close(case['split_state'], split_obs)
        assert case['candidate_names'] == list(NAMES)
        assert [row['name'] for row in case['candidates']] == list(NAMES)
        bc = action_from_model(split_obs, mean, std, coef)
        direction = np.array([256., 256.]) - split_obs[2:4]
        feedback = split_obs[:2] + direction * min(1., 60. / max(np.linalg.norm(direction), 1e-12))
        expected = (bc, feedback, bc+[60., 0.], bc+[-60., 0.], bc+[0., 60.], bc+[0., -60.])
        traces = {}
        for row, target in zip(case['candidates'], expected):
            action = np.clip(target, 0, 512).astype(np.float32)
            check_close(row['action'], action, 1e-5)
            assert digest(OUT / row['trace']) == row['sha256']
            with np.load(OUT / row['trace'], allow_pickle=False) as saved:
                trace = {key: saved[key].copy() for key in saved.files}
            traces[row['name']] = trace
            assert trace['observation'].shape == (12, 5) and trace['full'].shape == (12, 10)
            assert trace['coverage'].shape == (12,) and trace['action'].shape == (11, 2)
            assert trace['contact'].shape == (11,)
            assert all(np.isfinite(value).all() for value in trace.values())
            check_close(trace['action'][0], action, 1e-6)
            split_drift = max(float(np.max(np.abs(trace[key][0] - original[key][step])))
                              for key in ('observation', 'full', 'coverage'))
            assert split_drift <= row['prefix_drift'] + 1e-9
            assert row['prefix_drift'] <= doc['tolerance']
            check_close(trace['observation'][:, :4], trace['full'][:, [0, 1, 4, 5]], 1e-8)
            actual_delta = trace['observation'][1, 2:5] - trace['observation'][0, 2:5]
            actual_delta[2] = wrap(actual_delta[2])
            check_close(actual_delta, row['actual_delta'])
            x = features(split_obs, action)
            distances, neighbors = tree.query(x, k=32, workers=1)
            weights = 1. / np.maximum(distances, 1e-6) ** 2
            weights /= weights.sum(axis=1, keepdims=True)
            predicted_delta = np.sum(y_train[neighbors] * weights[..., None], axis=1)[0]
            predicted_pose = split_obs[2:5] + predicted_delta
            predicted_pose[2] %= 2*np.pi
            predicted_score = (-np.linalg.norm(predicted_pose[:2]-[256., 256.])/100.
                               - .25*(1-np.cos(predicted_pose[2]-np.pi/4)))
            check_close(row['predicted_delta'], predicted_delta)
            check_close(row['predicted_pose'], predicted_pose)
            assert abs(row['predicted_score'] - predicted_score) < 1e-10
            assert abs(row['nearest_distance'] - distances[0, 0]) < 1e-10
            assert abs(row['weighted_distance'] - np.sum(weights*distances)) < 1e-10
            error = predicted_delta-actual_delta
            error[2] = wrap(error[2])
            assert abs(row['prediction_xy_error_px']-np.linalg.norm(error[:2])) < 1e-10
            assert abs(row['prediction_yaw_error_rad']-abs(error[2])) < 1e-10
            assert abs(row['one_step_coverage']-trace['coverage'][1]) < 1e-10
            assert abs(row['final_coverage']-trace['coverage'][-1]) < 1e-10
            assert row['one_step_contact'] == int(trace['contact'][0])
            assert row['contact_steps'] == int(np.sum(trace['contact'] > 0))
            motion = np.linalg.norm(trace['full'][-1, 4:6]-trace['full'][0, 4:6])
            assert abs(row['final_object_motion_px']-motion) < 1e-10
        assert case['model_selected'] == max(case['candidates'], key=lambda x:x['predicted_score'])['name']
        repeated = case['bc_repeat']
        assert digest(OUT / repeated['trace']) == repeated['sha256']
        with np.load(OUT / repeated['trace'], allow_pickle=False) as saved:
            bc_repeat = {key: saved[key].copy() for key in saved.files}
        repeat_drift = max(float(np.max(np.abs(traces['bc'][key]-bc_repeat[key])))
                           for key in bc_repeat)
        assert abs(repeat_drift-case['baseline_repeat_max_drift']) < 1e-10
        assert case['repeat_prefix_drift'] <= doc['tolerance']
        assert repeat_drift <= doc['tolerance'] and case['status'] == 'repeatable'
        result.append(dict(seed=seed, selected=case['model_selected'], repeat_drift=repeat_drift,
                           bc=float(traces['bc']['coverage'][-1]),
                           feedback=float(traces['feedback']['coverage'][-1]),
                           model=float(traces[case['model_selected']]['coverage'][-1])))
    output = dict(status='passed', assessment_sha256=digest(OUT / 'assessment.json'),
                  cases=result, checked_candidates=12, checked_traces=14)
    (OUT / 'verification.json').write_text(json.dumps(output, indent=2, allow_nan=False)+'\n')
    print(json.dumps(output, indent=2), flush=True)


if __name__ == '__main__':
    main()
