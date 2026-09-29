"""Independent source/split/trace/metric audit for the small PushT BC route."""
import hashlib
import json
from pathlib import Path

import numpy as np
import zarr

ROOT = Path('/output')
FIT = ROOT / 'bc_fit1'
EVAL = ROOT / 'bc_eval1'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    fit = json.loads((FIT / 'fit.json').read_text())
    ev = json.loads((EVAL / 'evaluation.json').read_text())
    assert fit['status'] == ev['status'] == 'completed'
    assert digest(ROOT / 'demos/pusht.zip') == fit['source_zip_sha256'] == ev['source_zip_sha256']
    assert digest(FIT / fit['checkpoint']) == fit['checkpoint_sha256'] == ev['policy_checkpoint_sha256']
    store = zarr.ZipStore(str(ROOT / 'demos/pusht.zip'), mode='r')
    try:
        group = zarr.open_group(store=store, path='pusht/pusht_cchi_v7_replay.zarr', mode='r')
        ends = np.asarray(group['meta/episode_ends'][:], np.int64)
        states = group['data/state']
        actions = group['data/action']
        assert states.shape == (25650, 5) and actions.shape == (25650, 2)
        assert len(ends) == 206 and ends[-1] == 25650
        assert fit['train_rows'] == ends[159] and fit['validation_rows'] == ends[179]-ends[159]
    finally:
        store.close()
    assert fit['train_episode_ids'] == list(range(160))
    assert fit['validation_episode_ids'] == list(range(160, 180))
    assert fit['unused_episode_ids'] == list(range(180, 206))
    assert {x['alpha'] for x in fit['choices']} == {1.0, 100.0, 1000.0}
    assert fit['selected_alpha'] == min(fit['choices'], key=lambda x: x['validation_action_mse_px2'])['alpha']
    assert ev['seeds'] == list(range(48000, 48016)) and len(ev['rows']) == 32
    counts = {route: dict(success=0, contact_failure=0, contact=0) for route in ('hold', 'ridge_bc')}
    for seed in ev['seeds']:
        rows = [row for row in ev['rows'] if row['seed'] == seed]
        assert {row['route'] for row in rows} == {'hold', 'ridge_bc'}
        initials = []
        for row in rows:
            path = EVAL / row['trace']
            assert digest(path) == row['sha256']
            with np.load(path, allow_pickle=False) as trace:
                n = row['steps']
                assert 1 <= n <= 300
                assert trace['observation'].shape == (n+1, 5)
                assert trace['full'].shape == (n+1, 10)
                assert trace['coverage'].shape == (n+1,)
                assert trace['contact'].shape == (n,)
                assert trace['action'].shape == (n, 2)
                assert all(np.isfinite(trace[key]).all() for key in trace.files)
                assert np.all((trace['coverage'] >= 0) & (trace['coverage'] <= 1))
                assert np.all((trace['action'] >= 0) & (trace['action'] <= 512))
                assert abs(float(trace['coverage'][-1]) - row['final_coverage']) < 1e-9
                assert abs(float(trace['coverage'].max()) - row['max_coverage']) < 1e-9
                assert row['final_success'] == bool(trace['coverage'][-1] > .95)
                assert row['any_contact'] == bool(np.any(trace['contact'] > 0))
                assert row['contact_steps'] == int(np.sum(trace['contact'] > 0))
                assert abs(float(np.linalg.norm(trace['full'][-1, 4:6] - trace['full'][0, 4:6]))-
                           row['object_motion']) < 1e-8
                initials.append(trace['full'][0].copy())
            c = counts[row['route']]
            c['success'] += row['final_success']
            c['contact'] += row['any_contact']
            c['contact_failure'] += row['any_contact'] and not row['final_success']
        assert np.max(np.abs(initials[0]-initials[1])) < 1e-8
    result = dict(status='passed', fit_sha256=digest(FIT / 'fit.json'),
                  evaluation_sha256=digest(EVAL / 'evaluation.json'),
                  dataset_episodes=206, dataset_rows=25650, evaluation_seeds=16,
                  trace_count=32, counts=counts)
    (EVAL / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
