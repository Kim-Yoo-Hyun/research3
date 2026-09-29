"""Fixed candidate branches at two previously inspected PushT BC contact failures."""
import hashlib
import json
from pathlib import Path
import time

import numpy as np
from scipy.spatial import cKDTree

from repeat_action_model import predict, wrap
from repeat_bc import action_from_model
from repeat_failure_probe import branch_once

ROOT = Path('/output')
OUT = ROOT / 'contrast1'
SEEDS = (48007, 48010)
GOAL_XY = np.array([256.0, 256.0])
GOAL_ANGLE = np.pi / 4
TOL = 1e-8


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def score(pose):
    return float(-np.linalg.norm(np.asarray(pose[:2])-GOAL_XY)/100.0 -
                 0.25*(1.0-np.cos(pose[2]-GOAL_ANGLE)))


def candidates(state, bc):
    error = GOAL_XY - state[2:4]
    direction = error * min(1.0, 60.0 / max(np.linalg.norm(error), 1e-12))
    feedback = np.clip(state[:2] + direction, 0, 512)
    return [('bc', bc), ('feedback', feedback),
            ('x_plus', bc + [60., 0.]), ('x_minus', bc + [-60., 0.]),
            ('y_plus', bc + [0., 60.]), ('y_minus', bc + [0., -60.])]


def main():
    OUT.mkdir(exist_ok=False)
    previous = json.loads((ROOT / 'failure_branch1/assessment.json').read_text())
    verification = json.loads((ROOT / 'failure_branch1/verification.json').read_text())
    model_meta = json.loads((ROOT / 'fit_model1/fit.json').read_text())
    assert previous['selected_seeds'] == list(SEEDS) and verification['status'] == 'passed'
    assert verification['assessment_sha256'] == digest(ROOT / 'failure_branch1/assessment.json')
    assert model_meta['source_zip_sha256'] == digest(ROOT / 'demos/pusht.zip')
    assert model_meta['checkpoint_sha256'] == digest(ROOT / 'fit_model1/model.npz')
    with np.load(ROOT / 'fit_model1/model.npz', allow_pickle=False) as data:
        tree = cKDTree(data['features'])
        model_targets = data['targets'].copy()
    with np.load(ROOT / 'bc_fit1/ridge.npz', allow_pickle=False) as data:
        mean, std, coef = (data[key].copy() for key in ('mean', 'std', 'coef'))
    rows = []
    for seed in SEEDS:
        source_row = next(x for x in previous['cases'] if x['seed'] == seed)
        assert source_row['status'] == 'repeatable'
        source_file = ROOT / 'bc_eval1' / source_row['source_trace']
        assert source_row['source_sha256'] == digest(source_file)
        with np.load(source_file, allow_pickle=False) as data:
            original = {key: data[key].copy() for key in data.files}
        step = source_row['selected_step']
        state = original['observation'][step]
        bc = action_from_model(state, mean, std, coef)
        assert np.allclose(bc, source_row['baseline_action'], atol=1e-6)
        choices = [(name, np.clip(action, 0, 512).astype(np.float32))
                   for name, action in candidates(state, bc)]
        started = time.perf_counter()
        predicted_delta, nearest, weighted = predict(tree, model_targets,
                                                      np.repeat(state[None], len(choices), 0),
                                                      [action for _, action in choices])
        query_ms = (time.perf_counter() - started)*1000.0
        choice_rows = []
        traces = {}
        for i, (name, action) in enumerate(choices):
            predicted_pose = state[2:5] + predicted_delta[i]
            predicted_pose[2] = predicted_pose[2] % (2*np.pi)
            started = time.perf_counter()
            trace, prefix_drift = branch_once(seed, original, step, action, mean, std, coef)
            elapsed = time.perf_counter() - started
            file = OUT / f'{seed}_{name}.npz'
            np.savez_compressed(file, **trace)
            actual_delta = trace['observation'][1, 2:5] - trace['observation'][0, 2:5]
            actual_delta[2] = wrap(actual_delta[2])
            error = predicted_delta[i] - actual_delta
            error[2] = wrap(error[2])
            one_step_pose = trace['observation'][1, 2:5]
            row = dict(name=name, action=action.tolist(), predicted_delta=predicted_delta[i].tolist(),
                       predicted_pose=predicted_pose.tolist(), predicted_score=score(predicted_pose),
                       nearest_distance=float(nearest[i]), weighted_distance=float(weighted[i]),
                       actual_delta=actual_delta.tolist(), prediction_xy_error_px=float(np.linalg.norm(error[:2])),
                       prediction_yaw_error_rad=float(abs(error[2])),
                       actual_one_step_score=score(one_step_pose),
                       one_step_coverage=float(trace['coverage'][1]),
                       final_coverage=float(trace['coverage'][-1]),
                       one_step_contact=int(trace['contact'][0]),
                       contact_steps=int(np.sum(trace['contact'] > 0)),
                       final_object_motion_px=float(np.linalg.norm(trace['full'][-1, 4:6]-trace['full'][0, 4:6])),
                       prefix_drift=prefix_drift, branch_seconds=elapsed,
                       trace=file.name, sha256=digest(file))
            traces[name] = trace
            choice_rows.append(row)
        # Repeated BC is a validity control, never a seventh candidate for selection.
        started = time.perf_counter()
        repeat, repeat_prefix = branch_once(seed, original, step, bc, mean, std, coef)
        repeat_elapsed = time.perf_counter() - started
        repeat_file = OUT / f'{seed}_bc_repeat.npz'
        np.savez_compressed(repeat_file, **repeat)
        drift = max(float(np.max(np.abs(traces['bc'][key]-repeat[key]))) for key in repeat)
        selected = max(choice_rows, key=lambda row: row['predicted_score'])['name']
        row = dict(seed=seed, selected_step=step, source_trace=source_row['source_trace'],
                   source_sha256=source_row['source_sha256'], split_state=state.tolist(),
                   candidate_names=[r['name'] for r in choice_rows], model_selected=selected,
                   predictor_query_ms=query_ms, baseline_repeat_max_drift=drift,
                   repeat_prefix_drift=repeat_prefix, repeat_branch_seconds=repeat_elapsed,
                   bc_repeat=dict(trace=repeat_file.name, sha256=digest(repeat_file)),
                   candidates=choice_rows)
        row['status'] = 'repeatable' if max(drift, repeat_prefix,
                                           *(x['prefix_drift'] for x in choice_rows)) <= TOL else 'invalid_repeat'
        rows.append(row)
        print(json.dumps(dict(seed=seed, status=row['status'], model_selected=selected,
                              baseline_repeat_max_drift=drift,
                              outcomes={x['name']: round(x['final_coverage'], 4) for x in choice_rows})), flush=True)
    (OUT / 'assessment.json').write_text(json.dumps(dict(status='completed',
             purpose='exploratory development on previously selected BC contact failures',
             seeds=list(SEEDS), tolerance=TOL, horizon=11,
             source_evaluation_sha256=digest(ROOT / 'bc_eval1/evaluation.json'),
             previous_branch_sha256=digest(ROOT / 'failure_branch1/assessment.json'),
             bc_checkpoint_sha256=digest(ROOT / 'bc_fit1/ridge.npz'),
             predictor_fit_sha256=digest(ROOT / 'fit_model1/fit.json'),
             predictor_checkpoint_sha256=digest(ROOT / 'fit_model1/model.npz'),
             candidate_rule='BC, agent+clipped(goal-object, 60px), BC +/-60px independently in x/y',
             predicted_score='-next-object goal XY distance/100 - 0.25*(1-cos(next yaw - pi/4))',
             cases=rows), indent=2, allow_nan=False) + '\n')


if __name__ == '__main__':
    main()
