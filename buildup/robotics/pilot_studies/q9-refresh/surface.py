"""Exploratory observed-surface comparison. Run only in the Q9 CPU container."""
import argparse
import hashlib
import io
import json
import platform
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from inspect_input import CpuUnpickler
from observe import write_png


def geometry(points, pose, intrinsics, shape, limits):
    homogeneous = np.c_[points, np.ones(len(points))]
    camera = (np.linalg.inv(pose) @ homogeneous.T).T[:, :3]
    z = camera[:, 2]
    projected = (intrinsics @ camera.T).T
    uv = np.full((len(points), 2), np.nan)
    positive = z > 0
    uv[positive] = projected[positive, :2] / z[positive, None]
    h, w = shape
    inside = positive & (uv[:, 0] >= 1) & (uv[:, 0] < w - 1)
    inside &= (uv[:, 1] >= 1) & (uv[:, 1] < h - 1)
    eligible = inside & (z > limits[0]) & (z <= limits[1])
    return {"uv": uv, "z": z, "inside": inside, "eligible": eligible}


def evaluate(points, pose, intrinsics, depth, config):
    g = geometry(points, pose, intrinsics, depth.shape, config['depth_limits_m'])
    states, residuals = [], []
    for idx in range(len(points)):
        residual = None
        if not g['eligible'][idx]:
            state = 'unknown_geometry'
        else:
            u, v = np.rint(g['uv'][idx]).astype(int)
            patch = depth[v-1:v+2, u-1:u+2]
            lo, hi = config['depth_limits_m']
            valid = np.isfinite(patch) & (patch > lo) & (patch <= hi)
            if valid.sum() < 5:
                state = 'unknown_depth'
            else:
                residual = float(np.median(patch[valid]) - g['z'][idx])
                margin = config['residual_margin_m']
                state = 'free_space' if residual > margin else 'occluded' if residual < -margin else 'consistent'
        states.append(state)
        residuals.append(residual)
    counts = dict(Counter(states))
    threshold = config['minimum_support_points']
    region = 'contradicted' if counts.get('free_space', 0) >= threshold else (
        'consistent' if counts.get('consistent', 0) >= threshold else 'unknown')
    return {'region_state': region, 'counts': counts, 'point_states': states,
            'residuals_m': residuals, 'geometrically_eligible': int(g['eligible'].sum())}


def visibility_schedule(points, poses, intrinsics, shape, config):
    """No RGB, depth, annotation or result-trace argument is available here."""
    selected, decisions = [], []
    interval = config['interval_indices']
    budget = config['depth_read_budget']
    for offset, idx in enumerate(interval):
        if len(selected) == budget:
            break
        count = int(geometry(points, poses[idx], intrinsics[idx], shape,
                             config['depth_limits_m'])['eligible'].sum())
        forced = len(interval) - offset == budget - len(selected)
        read = count >= config['minimum_support_points'] or forced
        decisions.append({'index': idx, 'eligible_points': count, 'read_depth': read,
                          'reason': 'deadline' if forced else 'geometry' if read else 'skip'})
        if read:
            selected.append(idx)
    assert len(selected) == budget
    return selected, decisions


def controls():
    config = {'depth_limits_m': [0.1, 2.], 'residual_margin_m': 0.05, 'minimum_support_points': 5,
              'interval_indices': list(range(10)), 'depth_read_budget': 2}
    k = np.array([[20., 0., 10.], [0., 20., 10.], [0., 0., 1.]])
    points = np.array([[x, y, 1.] for x in [-0.05, 0., 0.05] for y in [-0.05, 0., 0.05]])
    passed = []
    for value, expected in [(1., 'consistent'), (1.2, 'contradicted'), (0.8, 'unknown'), (np.nan, 'unknown')]:
        result = evaluate(points, np.eye(4), k, np.full((21, 21), value), config)
        assert result['region_state'] == expected
        passed.append(str(value) + ':' + expected)
    poses = [np.eye(4) for _ in range(10)]
    away = points + np.array([3., 0., 0.])
    selected, decisions = visibility_schedule(away, poses, [k]*10, (21, 21), config)
    assert selected == [8, 9] and len(decisions) == 10
    passed.append('out_of_view_deadline_exact_budget')
    selected, _ = visibility_schedule(points, poses, [k]*10, (21, 21), config)
    assert selected == [0, 1]
    # Perturb unseen future camera metadata: a causal selector's already completed decisions stay fixed.
    poses[9] = np.diag([-1., 1., -1., 1.])
    assert visibility_schedule(points, poses, [k]*10, (21, 21), config)[0] == selected
    passed.append('causal_geometry_only_selection')
    return passed


def render(data, points, case, indices, output, config):
    panels = []
    for idx in indices:
        rgb = data['rgb'][idx].copy()
        if np.nanmax(rgb) <= 1:
            rgb *= 255
        g = geometry(points, data['camera_poses'][idx], data['camera_K'][idx], rgb.shape[:2], config['depth_limits_m'])
        for uv, inside in zip(g['uv'], g['inside']):
            if inside:
                u, v = np.rint(uv).astype(int)
                rgb[v-1:v+2, u-1:u+2] = [255, 0, 255]
        panels.append(rgb)
    write_png(output / (case['name'].replace(' ', '_') + '_surface.png'), np.concatenate(panels, axis=1))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--regions', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    self_checks = controls()
    config_bytes = args.regions.read_bytes()
    config = json.loads(config_bytes)
    raw = args.input.read_bytes()
    input_hash = hashlib.sha256(raw).hexdigest()
    assert input_hash == config['input_sha256']
    payload = CpuUnpickler(io.BytesIO(raw)).load()
    data = {key: [x.detach().cpu().numpy().astype(np.float64) if isinstance(x, torch.Tensor)
                   else np.asarray(x, dtype=np.float64) for x in values] for key, values in payload.items()}
    n = len(data['depth'])
    assert all(len(values) == n for values in data.values())
    shape = data['depth'][0].shape
    assert all(d.shape == shape for d in data['depth'])
    args.output.mkdir(parents=True, exist_ok=False)
    cases, traces = {}, []
    for case in config['cases']:
        initial = case['initial_frame']
        pixels = np.array(case['pixels_uv'])
        x0, y0, x1, y1 = case['region_xyxy']
        assert ((pixels[:, 0] >= x0) & (pixels[:, 0] < x1) & (pixels[:, 1] >= y0) & (pixels[:, 1] < y1)).all()
        depth = data['depth'][initial]
        z = depth[pixels[:, 1], pixels[:, 0]]
        lo, hi = config['depth_limits_m']
        assert np.isfinite(z).all() and ((z > lo) & (z <= hi)).all(), 'invalid initial seed depth; retain region and diagnose'
        rays = np.linalg.solve(data['camera_K'][initial], np.c_[pixels, np.ones(len(pixels))].T).T
        camera = rays * z[:, None]
        pose = data['camera_poses'][initial]
        world = (pose @ np.c_[camera, np.ones(len(camera))].T).T[:, :3]
        check = geometry(world, pose, data['camera_K'][initial], shape, config['depth_limits_m'])
        roundtrip = float(np.max(np.abs(check['uv'] - pixels)))
        assert roundtrip < 1e-5
        # Decide first. The selector cannot read trace values or unselected depth.
        selected, decisions = visibility_schedule(world, data['camera_poses'], data['camera_K'], shape, config)
        schedules = []
        interval, budget = config['interval_indices'], config['depth_read_budget']
        period = len(interval) // budget
        assert len(interval) % budget == 0
        plans = [(f'periodic_phase_{phase}', interval[phase::period], None) for phase in range(period)]
        plans.append(('visibility_first', selected, decisions))
        for name, plan, decision_log in plans:
            readings = []
            for idx in plan:
                reading = evaluate(world, data['camera_poses'][idx], data['camera_K'][idx], data['depth'][idx], config)
                readings.append({'index': idx, **reading})
            assert len(readings) == budget
            hits = [r['index'] for r in readings if r['region_state'] == 'contradicted']
            schedules.append({'name': name, 'selected': plan, 'depth_frame_reads': len(readings),
                              'pose_checks': len(decision_log) if decision_log is not None else len(plan),
                              'surface_point_tests': len(readings)*len(world),
                              'depth_patch_reads': sum(r['geometrically_eligible'] for r in readings),
                              'contradiction_indices': hits,
                              'first_contradiction': hits[0] if hits else None,
                              'readings': readings, 'decisions': decision_log})
        # Full trace is evaluator-only and is produced after all schedule decisions.
        rows = [{'case': case['name'], 'index': idx,
                 **evaluate(world, data['camera_poses'][idx], data['camera_K'][idx], data['depth'][idx], config)}
                for idx in range(n)]
        traces.extend(rows)
        cases[case['name']] = {'initial_frame': initial, 'pixels_uv': pixels.tolist(),
                              'initial_depth_m': z.tolist(), 'world_points': world.tolist(),
                              'roundtrip_max_pixel_error': roundtrip,
                              'initial_control_indices': list(range(initial, 14)),
                              'initial_control_states': dict(Counter(r['region_state'] for r in rows[initial:14])),
                              'interior_states': dict(Counter(rows[idx]['region_state'] for idx in interval)),
                              'all_frame_reference_contradictions': [idx for idx in interval if rows[idx]['region_state'] == 'contradicted'],
                              'schedules': schedules}
        render(data, world, case, [initial, 17, 19, 22], args.output, config)
        control_case = {**case, 'name': case['name'] + '_control'}
        render(data, world, control_case, [initial, 9 if case['name'] == 'orange' else 4], args.output, config)
    result = {'status': 'EXPLORATORY_SURFACE_COMPARISON', 'input_sha256': input_hash,
              'regions_sha256': hashlib.sha256(config_bytes).hexdigest(),
              'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'python': platform.python_version(), 'numpy': np.__version__, 'torch': torch.__version__,
              'device': 'cpu', 'seed': None, 'self_checks': self_checks, 'cases': cases,
              'cost_boundary': 'Two depth-frame reads per schedule plus one shared initial RGB-D frame; pose checks separate. Full-trace diagnostics and pickle loading are offline setup, not claimed compute savings.',
              'interpretation': 'Initial sampled surface contradiction only; no whole-object absence or localization success.'}
    (args.output/'result.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    (args.output/'trace.jsonl').write_text(''.join(json.dumps(r, allow_nan=False)+'\n' for r in traces))
    print(json.dumps({name: {'initial': c['initial_control_states'], 'interior': c['interior_states'],
                      'schedules': [{k:r[k] for k in ['name','selected','depth_frame_reads','pose_checks','contradiction_indices']}
                                    for r in c['schedules']]} for name, c in cases.items()}, indent=2))


if __name__ == '__main__':
    main()
