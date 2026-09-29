"""BOP numerical input producer. Execute only in the pinned CPU Docker."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

import numpy as np
from PIL import Image
from plyfile import PlyData


def load(path):
    return json.loads(Path(path).read_text())


def save(path, data):
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False)+'\n')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def png(path, spec, kind):
    raw = Path(path).read_bytes()
    assert raw[:8] == b'\x89PNG\r\n\x1a\n' and raw[12:16] == b'IHDR'
    w, h, bits, color, comp, filt, interlace = struct.unpack('>IIBBBBB', raw[16:29])
    assert [w, h] == [spec['width'], spec['height']]
    assert bits == spec[f'{kind}_bit_depth'] and color == spec[f'{kind}_color_type']
    assert comp == filt == interlace == 0
    with Image.open(path) as im:
        a = np.asarray(im).copy()
    assert a.shape == ((h, w, 3) if kind == 'rgb' else (h, w))
    assert a.dtype.kind in 'ui' and a.min() >= 0 and a.max() <= (65535 if kind == 'depth' else 255)
    if kind == 'mask':
        assert np.isin(a, [0, 255]).all()
    return a


def mesh(path, info, cfg):
    ply = PlyData.read(path, mmap=False)
    v = np.column_stack([ply['vertex'][k] for k in ('x', 'y', 'z')]).astype(np.float64)*cfg['coordinates']['mm_to_m']
    names = ply['face'].data.dtype.names
    key = 'vertex_indices' if 'vertex_indices' in names else 'vertex_index'
    faces = ply['face'][key]
    assert all(len(f) == 3 for f in faces), 'nontriangular PLY face'
    f = np.asarray(list(faces), dtype=np.int64)
    assert len(v) >= 4 and len(f) >= 4 and np.isfinite(v).all() and f.min() >= 0 and f.max() < len(v)
    lo = np.array([info['min_'+k] for k in 'xyz'])*.001
    size = np.array([info['size_'+k] for k in 'xyz'])*.001
    bbox_error = max(float(np.abs(v.min(0)-lo).max()), float(np.abs(np.ptp(v, axis=0)-size).max()))
    assert bbox_error <= cfg['tolerances']['model_bbox_m'], 'model unit/bbox metadata mismatch'
    unique, index = np.unique(v, axis=0, return_inverse=True)
    wf = index[f]
    directed = np.concatenate((wf[:, [0, 1]], wf[:, [1, 2]], wf[:, [2, 0]]))
    _, ids, count = np.unique(np.sort(directed, axis=1), axis=0, return_inverse=True, return_counts=True)
    sign = np.bincount(ids, weights=np.where(directed[:, 0] < directed[:, 1], 1, -1))
    tri = v[f]
    areas = np.linalg.norm(np.cross(tri[:, 1]-tri[:, 0], tri[:, 2]-tri[:, 0]), axis=1)/2
    result = {'raw_vertices': len(v), 'exact_coordinate_classes': len(unique), 'triangles': len(f),
              'bad_edges': int(np.count_nonzero(count != 2)), 'orientation_failures': int(np.count_nonzero(sign)),
              'zero_area_face_ids': np.flatnonzero(areas == 0).tolist(),
              'below_area_face_ids': np.flatnonzero(areas < cfg['tolerances']['triangle_area_min_m2']).tolist(),
              'minimum_area_m2': float(areas.min()), 'bbox_error_m': bbox_error}
    result['mesh_gate'] = not (result['bad_edges'] or result['orientation_failures'] or result['below_area_face_ids'])
    return v, f, result


def rigid(R, t, tol):
    R, t = np.asarray(R, dtype=np.float64).reshape(3, 3), np.asarray(t, dtype=np.float64).reshape(3)*.001
    assert np.isfinite(R).all() and np.isfinite(t).all()
    assert np.max(np.abs(R.T@R-np.eye(3))) <= tol['rotation_orthogonality'], 'nonrigid rotation'
    assert abs(np.linalg.det(R)-1) <= tol['rotation_determinant'], 'rotation reflection/scale'
    return R, t


def rays(K, pixels):
    return np.column_stack(((pixels[:, 1]-K[0, 2])/K[0, 0], (pixels[:, 0]-K[1, 2])/K[1, 1], np.ones(len(pixels))))


def ray_depth(direction, triangles):
    e1, e2 = triangles[:, 1]-triangles[:, 0], triangles[:, 2]-triangles[:, 0]
    h = np.cross(np.broadcast_to(direction, e2.shape), e2)
    det = np.einsum('ij,ij->i', e1, h)
    valid = np.abs(det) > 1e-14
    inv = np.zeros(len(det)); inv[valid] = 1/det[valid]
    s = -triangles[:, 0]
    u = inv*np.einsum('ij,ij->i', s, h)
    q = np.cross(s, e1)
    v = inv*(q@direction)
    depth = inv*np.einsum('ij,ij->i', e2, q)
    good = valid & (u >= -1e-10) & (v >= -1e-10) & (u+v <= 1+1e-10) & (depth > 1e-10)
    return float(depth[good].min()) if good.any() else None


def decision(cfg, models, cases):
    d = cfg['decisions']
    if any(c.get('input_error') for c in cases):
        return d['schema_or_coordinate']
    if not all(m['mesh_gate'] for m in models):
        return d['mesh']
    if any(not c.get('ray_support', False) for c in cases):
        return d['missing_ray_support']
    return d['numerical_pass']


def run(data, out, cfg, selection):
    data, out = Path(data), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    assert not any(out.iterdir())
    source = data/f'test/{selection["scene"]:06d}'
    camera, gt = load(source/'scene_camera.json'), load(source/'scene_gt.json')
    infos, model_infos = load(source/'scene_gt_info.json'), load(data/'models/models_info.json')
    models, meshes = [], {}
    for obj in selection['objects']:
        try:
            v, f, record = mesh(data/f'models/obj_{obj:06d}.ply', model_infos[str(obj)], cfg)
            meshes[obj] = (v, f)
            np.savez_compressed(out/f'model_{obj:06d}.npz', vertices_m=v, faces=f)
            models.append({'object': obj, **record})
        except Exception as e:
            models.append({'object': obj, 'mesh_gate': False, 'error': f'{type(e).__name__}: {e}'})
    model_pass = {m['object']: m['mesh_gate'] for m in models}
    cases = []
    for expected in selection['cases']:
        row = dict(expected)
        frame, obj, gi = expected['frame'], expected['object'], expected['gt_index']
        try:
            record = gt[str(frame)][gi]
            assert record['obj_id'] == obj and len(gt[str(frame)]) == len(infos[str(frame)])
            assert [x['obj_id'] for x in gt[str(frame)]] == [c['object'] for c in selection['cases'] if c['frame'] == frame]
            rgb = png(source/f'rgb/{frame:06d}.png', cfg['image'], 'rgb')
            raw = png(source/f'depth/{frame:06d}.png', cfg['image'], 'depth')
            full = png(source/f'mask/{frame:06d}_{gi:06d}.png', cfg['image'], 'mask') > 0
            visible = png(source/f'mask_visib/{frame:06d}_{gi:06d}.png', cfg['image'], 'mask') > 0
            assert not np.any(visible & ~full), 'visible mask outside full mask'
            cam = camera[str(frame)]
            K = np.asarray(cam['cam_K'], dtype=np.float64).reshape(3, 3)
            assert np.isfinite(K).all() and K[0, 0] > 0 and K[1, 1] > 0
            assert max(abs(K[0, 1]), abs(K[1, 0]), abs(K[2, 0]), abs(K[2, 1]), abs(K[2, 2]-1)) <= cfg['tolerances']['camera_structure']
            assert 0 <= K[0, 2] < cfg['image']['width'] and 0 <= K[1, 2] < cfg['image']['height']
            scale = float(cam['depth_scale']); assert np.isfinite(scale) and scale > 0
            R, t = rigid(record['cam_R_m2c'], record['cam_t_m2c'], cfg['tolerances'])
            if 'cam_R_w2c' in cam or 'cam_t_w2c' in cam:
                rigid(cam['cam_R_w2c'], cam['cam_t_w2c'], cfg['tolerances'])
            depth = raw.astype(np.float64)*scale*.001
            valid = visible & (raw > 0)
            available = np.argwhere(valid)
            assert len(available), 'no observed valid object pixels'
            count = min(cfg['diagnostic']['rays_per_instance'], len(available))
            indices = np.arange(count, dtype=np.int64)*(len(available)-1)//max(count-1, 1)
            pixels = available[indices]
            direction = rays(K, pixels)
            z = depth[pixels[:, 0], pixels[:, 1]]
            points = direction*z[:, None]
            projected = points@K.T; projected = projected[:, :2]/projected[:, 2, None]
            error_px = float(np.abs(projected-pixels[:, ::-1]).max())
            assert error_px <= cfg['tolerances']['projection_px']
            object_points = np.linalg.solve(R, (points-t).T).T
            error_m = float(np.abs(object_points@R.T+t-points).max())
            assert error_m <= cfg['tolerances']['numeric_m']
            np.savez_compressed(out/f'{row["id"]}.npz', pixels=pixels, selected_indices=indices, camera_points_m=points,
                                object_points_m=object_points, K=K, R_m2c=R, t_m2c_m=t)
            row.update({'input_pass': True, 'mesh_gate': model_pass[obj], 'valid_pixels': len(available),
                        'visible_pixels': int(visible.sum()), 'visible_missing_depth_pixels': int((visible & (raw == 0)).sum()),
                        'full_mask_pixels': int(full.sum()), 'supports_2048_observed_pixels': len(available) >= 2048,
                        'projection_error_px': error_px, 'inverse_error_m': error_m, 'diagnostic_pixels': pixels.tolist(),
                        'observed_depth_m': z.tolist(), 'ray_model_depth_m': [], 'residual_m': [], 'ray_support': False})
            if model_pass[obj]:
                v, f = meshes[obj]
                tri = (v@R.T+t)[f]
                depths = [ray_depth(d, tri) for d in direction]
                residual = [float(a-b) if b is not None else None for a, b in zip(z, depths)]
                finite = [abs(x) for x in residual if x is not None]
                row.update({'ray_model_depth_m': depths, 'residual_m': residual,
                            'missing_model_rays': depths.count(None),
                            'median_absolute_residual_m': float(np.median(finite)) if finite else None,
                            'maximum_absolute_residual_m': max(finite) if finite else None,
                            'ray_support': len(available) >= cfg['diagnostic']['rays_per_instance'] and not depths.count(None)})
            else:
                row['residual_skipped'] = 'failed mesh gate; no ray/solid admission'
        except Exception as e:
            row['input_error'] = f'{type(e).__name__}: {e}'
        cases.append(row)
    result = {'id': cfg['id'], 'denominator': len(selection['cases']), 'models': models, 'cases': cases,
              'decision': decision(cfg, models, cases), 'physical_admission': False,
              'calibration_status': cfg['diagnostic']['calibration_status']}
    save(out/'result.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--data', required=True); parser.add_argument('--output', required=True)
    args = parser.parse_args(); study = Path(__file__).resolve().parent
    frozen = load(study/'freeze.json')
    for name, h in frozen['files'].items():
        assert sha(study/name) == h, ('INVALID_INTEGRITY', name)
    for item in load(study/'assets.json')['files']:
        f = Path(args.data)/item['destination']; assert f.stat().st_size == item['bytes'] and sha(f) == item['sha256'], ('INVALID_INTEGRITY', str(f))
    result = run(args.data, args.output, load(study/'protocol.json'), load(study/'selection.json'))
    print(json.dumps({'decision': result['decision'], 'denominator': result['denominator']}))


if __name__ == '__main__':
    main()
