"""Independent readiness verifier: no import of scene.py or PyBullet; container-only NumPy."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def intersections(origin, direction, triangles):
    """Moller-Trumbore ray/triangle distances. Direction need not be unit length."""
    edge1 = triangles[:, 1]-triangles[:, 0]
    edge2 = triangles[:, 2]-triangles[:, 0]
    h = np.cross(np.broadcast_to(direction, edge2.shape), edge2)
    det = np.einsum('ij,ij->i', edge1, h)
    valid = np.abs(det) > 1e-14
    inv = np.zeros_like(det)
    inv[valid] = 1/det[valid]
    s = origin-triangles[:, 0]
    u = inv*np.einsum('ij,ij->i', s, h)
    q = np.cross(s, edge1)
    v = inv*(q @ direction)
    t = inv*np.einsum('ij,ij->i', edge2, q)
    good = valid & (u >= -1e-10) & (v >= -1e-10) & (u+v <= 1+1e-10) & (t > 1e-10)
    values = np.sort(t[good])
    return values[np.r_[True, np.diff(values) > 1e-8]] if len(values) else values


def inside_by_rays(point, triangles):
    parity = [len(intersections(point, np.asarray(d), triangles)) % 2
              for d in ([1, .372, .127], [-.23, 1, .341], [.191, -.267, 1])]
    assert len(set(parity)) == 1, 'ambiguous independent containment rays'
    return bool(parity[0])


def triangle_box_intersects(triangles, half):
    """Clip each candidate triangle against six box half-spaces, after a broad phase."""
    broad = np.all(triangles.max(1) >= -half-1e-12, axis=1) & np.all(triangles.min(1) <= half+1e-12, axis=1)
    for tri in triangles[broad]:
        polygon = list(tri)
        for axis in range(3):
            for sign in (-1, 1):
                if not polygon:
                    break
                clipped = []
                for a, b in zip(polygon, polygon[1:]+polygon[:1]):
                    da, db = sign*a[axis]-half[axis], sign*b[axis]-half[axis]
                    ina, inb = da <= 1e-12, db <= 1e-12
                    if ina:
                        clipped.append(a)
                    if ina != inb:
                        clipped.append(a+(b-a)*(da/(da-db)))
                polygon = clipped
        if polygon:
            return True
    return False


def geometry_label(triangles, candidate):
    rotation = np.asarray(candidate['rotation'])
    for box in candidate['boxes']:
        c, half = np.asarray(box['center']), np.asarray(box['half'])
        if triangle_box_intersects((triangles-c) @ rotation, half) or inside_by_rays(c, triangles):
            return True
    return False


def verify_case(folder, protocol):
    folder = Path(folder)
    receipt = json.loads((folder/'result.json').read_text())
    rows = json.loads((folder/'candidates.json').read_text())
    assert hashlib.sha256((folder/'candidates.json').read_bytes()).hexdigest() == receipt['candidate_sha256']
    with np.load(folder/'observation.npz', allow_pickle=False) as f:
        obs = dict(f)
    with np.load(folder/'geometry.npz', allow_pickle=False) as f:
        geo = dict(f)
    cam, tol = receipt['camera'], protocol['tolerances']
    spec = protocol['camera']
    assert receipt['view_index'] in (0, 1)
    assert cam['eye'] == spec['eyes_m'][receipt['view_index']]
    assert cam['near'] == spec['near_m'] and cam['far'] == spec['far_m']
    forward = np.array(spec['target_m'])-np.array(cam['eye'])
    forward /= np.linalg.norm(forward)
    right = np.cross(forward, spec['up'])
    right /= np.linalg.norm(right)
    expected_rotation = np.column_stack((right, -np.cross(right, forward), forward))
    assert np.max(np.abs(expected_rotation-cam['rotation'])) < tol['numeric_roundtrip_m']
    h, w = obs['depth'].shape
    assert [w, h] == [protocol['camera']['width'], protocol['camera']['height']]
    assert np.array_equal(obs['depth_buffer'], obs['repeat_depth_buffer'])
    assert np.array_equal(obs['segmentation'], obs['repeat_segmentation'])
    depth = cam['near']/(1-obs['depth_buffer'].astype(np.float64)*(1-cam['near']/cam['far']))
    assert np.max(np.abs(depth-obs['depth'])) < tol['numeric_roundtrip_m']
    view = np.array(cam['view']).reshape(4, 4, order='F')
    # Independent camera transform comes from the recorded OpenGL view matrix.
    inv_view = np.linalg.inv(view)
    op_to_world = inv_view[:3, :3] @ np.diag([1., -1., -1.])
    eye = inv_view[:3, 3]
    assert np.linalg.det(op_to_world) > .999999
    assert np.max(np.abs(op_to_world-np.array(cam['rotation']))) < 1e-6
    uu, vv = np.meshgrid(np.arange(w)+.5, np.arange(h)+.5)
    focal = h/(2*np.tan(np.deg2rad(protocol['camera']['fov_y_deg'])/2))
    optical = np.stack([(uu-w/2)*depth/focal, (vv-h/2)*depth/focal, depth], axis=-1)
    assert np.isfinite(optical).all()
    mask = obs['mask']
    expected_mask = (obs['segmentation'] >= 0) & ((obs['segmentation'] & ((1 << 24)-1)) == receipt['object_body_id']) & (obs['depth_buffer'] < 1)
    assert np.array_equal(mask, expected_mask)
    assert mask.dtype == np.bool_ and mask.sum() >= protocol['sampling']['partial_count']
    indices = obs['sampled_indices']
    sampled = optical[mask][indices]
    assert len(np.unique(indices)) == protocol['sampling']['partial_count'] and indices[0] == 0
    assert len(np.unique(obs['partial_optical'], axis=0)) == len(indices)
    assert np.max(np.abs(sampled-obs['partial_optical'])) < tol['numeric_roundtrip_m']
    mean, radius = obs['partial_optical'].mean(0), np.linalg.norm(obs['partial_optical']-obs['partial_optical'].mean(0), axis=1).max()
    assert np.max(np.abs(obs['normalized']*radius+mean-obs['partial_optical'])) < tol['numeric_roundtrip_m']
    assert abs(radius-receipt['normalization']['radius']) < tol['numeric_roundtrip_m']
    assert np.max(np.abs(mean-receipt['normalization']['mean'])) < tol['numeric_roundtrip_m']
    world = optical @ op_to_world.T + eye
    # Ray sentinel set is selected from valid, locally smooth pixels, independent of ray errors.
    stable = mask.copy()
    lo, hi = depth.copy(), depth.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            stable &= np.roll(mask, (dy, dx), axis=(0, 1))
            d = np.roll(depth, (dy, dx), axis=(0, 1))
            lo, hi = np.minimum(lo, d), np.maximum(hi, d)
    stable[[0, -1], :] = False
    stable[:, [0, -1]] = False
    stable &= hi-lo <= tol['sentinel_depth_spread_m']
    available = np.argwhere(stable)
    assert len(available) >= tol['min_ray_sentinels'], 'insufficient stable ray sentinels'
    chosen = available[np.linspace(0, len(available)-1, tol['min_ray_sentinels'], dtype=int)]
    triangles = geo['vertices'][geo['faces']]
    ray_errors = []
    for y, x in chosen:
        direction = op_to_world @ np.array([(x+.5-w/2)/focal, (y+.5-h/2)/focal, 1.])
        distances = intersections(eye, direction, triangles)
        assert len(distances), 'rendered pixel has no independent ray intersection'
        ray_errors.append(abs(float(distances[0]-depth[y, x])))
    assert max(ray_errors) <= tol['ray_depth_m'], ('ray_depth_error_m', max(ray_errors))
    projection = np.array(cam['projection']).reshape(4, 4, order='F')
    probes = np.c_[world[stable], np.ones(int(stable.sum()))]
    clip = probes @ view.T @ projection.T
    xy = clip[:, :2]/clip[:, 3, None]
    u, v = (xy[:, 0]+1)*w/2, (1-xy[:, 1])*h/2
    assert np.max(np.abs(u-uu[stable])) < tol['projection_px'] and np.max(np.abs(v-vv[stable])) < tol['projection_px']
    # The candidate list must derive solely from the full observed optical cloud.
    anchor = optical[mask].mean(0)
    g = protocol['gripper']
    expected_params = [(a, b, c, d) for a in g['widths_m'] for b in g['rolls_deg'] for c in g['z_offsets_m'] for d in g['x_offsets_m']]
    assert len(rows) == g['candidate_count'] == len(receipt['labels'])
    for i, (row, params) in enumerate(zip(rows, expected_params)):
        width, roll, dz, dx = params
        assert row['id'] == i and [row[k] for k in ('width_m', 'roll_deg', 'z_offset_m', 'x_offset_m')] == list(params)
        expected_center = np.array(cam['eye']) + np.array(cam['rotation']) @ (anchor+[dx, 0, dz])
        assert np.max(np.abs(expected_center-row['center'])) < tol['numeric_roundtrip_m']
        angle = np.deg2rad(roll)
        r = np.array(cam['rotation']) @ np.array([[np.cos(angle), -np.sin(angle), 0], [np.sin(angle), np.cos(angle), 0], [0, 0, 1]])
        assert np.max(np.abs(r-row['rotation'])) < tol['numeric_roundtrip_m']
        fx, fy, fz = g['finger_half_extents_m']
        expected_boxes = [([-width/2-fx, 0, 0], [fx, fy, fz]), ([width/2+fx, 0, 0], [fx, fy, fz]),
                          ([0, 0, g['palm_center_z_m']], [width/2+2*fx, fy, g['palm_half_depth_m']])]
        assert len(row['boxes']) == 3
        for box, (offset, half) in zip(row['boxes'], expected_boxes):
            assert np.max(np.abs(box['center']-(expected_center+r@np.array(offset)))) < tol['numeric_roundtrip_m']
            assert box['half'] == half
        assert abs(row['utility_cost']-(dx*dx+dz*dz)) < 1e-15
    ids, bary = geo['triangle_ids'], geo['barycentric']
    assert len(ids) == protocol['sampling']['oracle_dense_count']
    assert ids.min() >= 0 and ids.max() < len(triangles) and np.isfinite(geo['oracle_points']).all()
    assert np.all(bary >= 0) and np.max(np.abs(bary.sum(1)-1)) < 1e-12
    assert np.max(np.abs((triangles[ids]*bary[:, :, None]).sum(1)-geo['oracle_points'])) < tol['numeric_roundtrip_m']
    independent, robust, mismatches, oracle_mismatches = [], [], [], []
    for row, label in zip(rows, receipt['labels']):
        assert row['id'] == label['id']
        truth = geometry_label(triangles, row)
        independent.append(truth)
        derived_ambiguous = any(b['distance_m'] is not None and abs(b['distance_m']) <= tol['near_contact_m'] for b in label['boxes'])
        assert derived_ambiguous == label['near_contact']
        for count, key in [(8192, 'oracle_8192_collision'), (32768, 'oracle_32768_collision')]:
            points = geo['oracle_points'][:count]
            hit = False
            for box in row['boxes']:
                local = (points-np.array(box['center'])) @ np.array(row['rotation'])
                hit |= bool(np.any(np.max(np.abs(local)-np.array(box['half']), axis=1) <= tol['point_in_box_m']))
            assert hit == label[key], 'oracle point membership mismatch'
            if not label['near_contact'] and hit != truth:
                oracle_mismatches.append([row['id'], count])
        if not label['near_contact']:
            robust.append(row['id'])
            if truth != label['collision']:
                mismatches.append(row['id'])
    collisions = sum(independent[i] for i in robust)
    clear = len(robust)-collisions
    return {'verified_camera': True, 'max_ray_depth_error_m': max(ray_errors), 'ray_sentinels': len(chosen),
            'candidate_count': len(rows), 'near_contact_count': len(rows)-len(robust),
            'robust_collision': collisions, 'robust_clear': clear,
            'collision_mismatch_ids': mismatches, 'oracle_mismatches': oracle_mismatches,
            'independent_labels': independent, 'support': bool(collisions and clear)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--study', default='/study')
    parser.add_argument('--assets', default='/assets')
    args = parser.parse_args()
    root, out = Path(args.input), Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    assert not any(out.iterdir()), 'refuse nonempty verification output'
    study = Path(args.study)
    protocol = json.loads((study/'protocol.json').read_text())
    source = json.loads((root/'result.json').read_text())
    expected_ids = [f'{obj}_v{vi}' for obj in protocol['objects'] for vi in range(2)]
    assert [r['id'] for r in source['cases']] == expected_ids and source['denominator'] == 4
    frozen = json.loads((study/'freeze.json').read_text())
    for name, h in frozen['files'].items():
        assert hashlib.sha256((study/name).read_bytes()).hexdigest() == h
    assert source['freeze_sha256'] == hashlib.sha256((study/'freeze.json').read_bytes()).hexdigest()
    assets = json.loads((study/'assets.json').read_text())
    errors, cases = [], []
    for row in source['cases']:
        if row.get('error'):
            errors.append({'id': row['id'], 'error': row['error']})
            continue
        try:
            asset = assets['objects'][protocol['objects'].index(row['object'])]
            raw_path = Path(args.assets)/Path(asset['mesh_path']).name
            assert hashlib.sha256(raw_path.read_bytes()).hexdigest() == asset['mesh_sha256']
            raw, faces = [], []
            for line in raw_path.read_text().splitlines():
                if line.startswith('v '):
                    raw.append([float(x) for x in line.split()[1:4]])
                elif line.startswith('f '):
                    faces.append([int(x.split('/')[0])-1 for x in line.split()[1:]])
            raw = np.array(raw)
            offset = np.array(protocol['asset_scale']['aabb_center_world_m'])
            extent = np.ptp(raw, axis=0).max()
            derived = (raw-(raw.max(0)+raw.min(0))/2)*(protocol['asset_scale']['longest_aabb_extent_m']/extent)+offset
            wf = np.unique(raw, axis=0, return_inverse=True)[1][np.array(faces)]
            edges = np.concatenate([wf[:, [0,1]], wf[:, [1,2]], wf[:, [2,0]]])
            _, edge_ids, counts = np.unique(np.sort(edges,axis=1),axis=0,return_inverse=True,return_counts=True)
            assert np.all(counts == 2)
            assert np.all(np.bincount(edge_ids,weights=np.where(edges[:,0]<edges[:,1],1,-1)) == 0)
            tri = derived[np.array(faces)]
            assert (np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)/2).min() >= protocol['tolerances']['mesh_area_min_m2']
            with np.load(root/row['id']/'geometry.npz', allow_pickle=False) as payload:
                assert np.array_equal(payload['faces'], np.array(faces))
                assert np.max(np.abs(payload['vertices']-derived)) <= protocol['tolerances']['numeric_roundtrip_m']
            receipt = json.loads((root/row['id']/'result.json').read_text())
            assert receipt['view_index'] == row['view_index']
            assert receipt['seed'] == protocol['sampling']['area_uniform_seed'] + protocol['objects'].index(row['object'])*2 + row['view_index']
            cases.append({'id': row['id'], **verify_case(root/row['id'], protocol)})
        except Exception as e:
            errors.append({'id': row['id'], 'error': f'{type(e).__name__}: {e}'})
    if errors or len(cases) != 4 or any(c['collision_mismatch_ids'] for c in cases):
        decision = 'REFINE_LINKAGE'
    elif not all(c['support'] for c in cases):
        decision = 'UNINFORMATIVE_CANDIDATE_SUPPORT'
    elif any(c['oracle_mismatches'] for c in cases):
        decision = 'REFINE_POINT_REPRESENTATION'
    else:
        decision = 'READY_FOR_BOUNDED_COMPLETION_DIAGNOSTIC'
    result = {'id': protocol['id'], 'decision': decision, 'denominator': 4, 'cases': cases, 'errors': errors,
              'source_result_sha256': hashlib.sha256((root/'result.json').read_bytes()).hexdigest(),
              'boundary': 'measurement readiness; no completion effect, policy success or native parity'}
    (out/'verification.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'decision': decision, 'cases': len(cases), 'errors': len(errors)}))


if __name__ == '__main__':
    main()
