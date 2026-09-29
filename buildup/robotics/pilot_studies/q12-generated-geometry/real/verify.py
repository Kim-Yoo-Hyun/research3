"""Independent PNG/PLY, scalar edge/area, affine and plane/barycentric audit. Docker only.

No audit.py, Pillow, plyfile, BOP toolkit or simulator import.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
import zlib

import numpy as np


def load(p):
    return json.loads(Path(p).read_text())


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def png(p):
    b = Path(p).read_bytes(); assert b[:8] == b'\x89PNG\r\n\x1a\n'
    pos, chunks, header, ended = 8, [], None, False
    while pos < len(b):
        size = struct.unpack('>I', b[pos:pos+4])[0]; kind = b[pos+4:pos+8]
        data = b[pos+8:pos+8+size]
        assert zlib.crc32(kind+data) == struct.unpack('>I', b[pos+8+size:pos+12+size])[0]
        if kind == b'IHDR':
            assert header is None; header = struct.unpack('>IIBBBBB', data)
        if kind == b'IDAT': chunks.append(data)
        pos += size+12
        if kind == b'IEND':
            assert size == 0
            ended = True
            break
    assert pos == len(b) and header is not None and ended
    w, h, bits, color, compression, filtering, interlace = header
    assert 0 < w <= 640 and 0 < h <= 480
    assert bits in (8, 16) and color in (0, 2) and compression == filtering == interlace == 0
    channels = 1 if color == 0 else 3
    stride, bpp = w*channels*(bits//8), channels*(bits//8)
    dec = zlib.decompressobj(); raw = dec.decompress(b''.join(chunks), (stride+1)*h+1)
    assert len(raw) == (stride+1)*h and dec.eof and not dec.unconsumed_tail
    rows = np.empty((h, stride), dtype=np.uint8)
    for y in range(h):
        filt = raw[y*(stride+1)]; encoded = raw[y*(stride+1)+1:(y+1)*(stride+1)]
        prior = rows[y-1] if y else np.zeros(stride, dtype=np.uint8)
        row = bytearray(encoded)
        assert filt in range(5)
        if filt:
            for x in range(stride):
                left = row[x-bpp] if x >= bpp else 0
                up = int(prior[x]); corner = int(prior[x-bpp]) if x >= bpp else 0
                if filt == 1: predictor = left
                elif filt == 2: predictor = up
                elif filt == 3: predictor = (left+up)//2
                else:
                    estimate = left+up-corner
                    a, c, d = abs(estimate-left), abs(estimate-up), abs(estimate-corner)
                    predictor = left if a <= c and a <= d else up if c <= d else corner
                row[x] = (row[x]+predictor) & 255
        rows[y] = np.frombuffer(row, dtype=np.uint8)
    result = np.frombuffer(rows.tobytes(), dtype='>u2' if bits == 16 else np.uint8).astype(np.uint16 if bits == 16 else np.uint8)
    return result.reshape((h, w) if channels == 1 else (h, w, channels)), header


TYPES = {'char':'b', 'int8':'b', 'uchar':'B', 'uint8':'B', 'short':'h', 'int16':'h',
         'ushort':'H', 'uint16':'H', 'int':'i', 'int32':'i', 'uint':'I', 'uint32':'I',
         'float':'f', 'float32':'f', 'double':'d', 'float64':'d'}


def ply(p):
    vertices, faces, elements = [], [], []
    with Path(p).open('rb') as stream:
        assert stream.readline().strip() == b'ply'
        fmt = None
        for _ in range(1000):
            line = stream.readline().decode('ascii').split()
            assert line
            if line[0] == 'format': fmt = line[1]
            elif line[0] == 'element': elements.append([line[1], int(line[2]), []])
            elif line[0] == 'property': elements[-1][2].append(line[1:])
            elif line[0] == 'end_header': break
        else: raise AssertionError('missing PLY end_header')
        assert fmt in ('ascii', 'binary_little_endian', 'binary_big_endian')
        endian = '<' if fmt == 'binary_little_endian' else '>'
        for kind, count, properties in elements:
            assert 0 <= count <= 2000000
            for _ in range(count):
                tokens = iter(stream.readline().decode('ascii').split()) if fmt == 'ascii' else None
                def scalar(t):
                    code = TYPES[t]
                    if tokens is not None:
                        value = float(next(tokens)) if code in 'fd' else int(next(tokens))
                        return struct.unpack('<'+code, struct.pack('<'+code, value))[0]
                    size = struct.calcsize(code)
                    return struct.unpack(endian+code, stream.read(size))[0]
                values = {}
                for prop in properties:
                    if prop[0] == 'list':
                        n = scalar(prop[1]); assert 0 <= n <= 1000
                        values[prop[3]] = [scalar(prop[2]) for _ in range(n)]
                    else: values[prop[1]] = scalar(prop[0])
                if kind == 'vertex': vertices.append(tuple(float(values[k])*.001 for k in 'xyz'))
                if kind == 'face':
                    f = values.get('vertex_indices', values.get('vertex_index')); assert len(f) == 3
                    faces.append(tuple(f))
        assert not stream.read().strip()
    assert len(vertices) >= 4 and len(faces) >= 4
    assert all(np.isfinite(v).all() for v in vertices)
    assert all(min(f) >= 0 and max(f) < len(vertices) for f in faces)
    return vertices, faces


def topology(v, f, info, cfg):
    index = {p: i for i, p in enumerate(sorted(set(v)))}
    counts, sign, areas = Counter(), Counter(), []
    for face in f:
        ids = [index[v[i]] for i in face]
        for a, b in zip(ids, ids[1:]+ids[:1]):
            edge = tuple(sorted((a, b))); counts[edge] += 1; sign[edge] += 1 if a < b else -1
        a, b, c = [v[i] for i in face]
        u, w = [b[k]-a[k] for k in range(3)], [c[k]-a[k] for k in range(3)]
        cross = (u[1]*w[2]-u[2]*w[1], u[2]*w[0]-u[0]*w[2], u[0]*w[1]-u[1]*w[0])
        areas.append(sum(x*x for x in cross)**.5/2)
    lo = [min(p[k] for p in v) for k in range(3)]; hi = [max(p[k] for p in v) for k in range(3)]
    error = max([abs(lo[k]-info['min_'+s]*.001) for k, s in enumerate('xyz')]+
                [abs(hi[k]-lo[k]-info['size_'+s]*.001) for k, s in enumerate('xyz')])
    assert error <= cfg['tolerances']['model_bbox_m']
    result = {'raw_vertices': len(v), 'exact_coordinate_classes': len(index), 'triangles': len(f),
              'bad_edges': sum(x != 2 for x in counts.values()), 'orientation_failures': sum(x != 0 for x in sign.values()),
              'zero_area_face_ids': [i for i, a in enumerate(areas) if a == 0],
              'below_area_face_ids': [i for i, a in enumerate(areas) if a < cfg['tolerances']['triangle_area_min_m2']],
              'minimum_area_m2': min(areas), 'bbox_error_m': error}
    result['mesh_gate'] = not (result['bad_edges'] or result['orientation_failures'] or result['below_area_face_ids'])
    return result


def ray(direction, triangles):
    a, u, v = triangles[:, 0], triangles[:, 1]-triangles[:, 0], triangles[:, 2]-triangles[:, 0]
    normal = np.cross(u, v); denom = normal@direction
    valid = np.abs(denom) > 1e-14
    z = np.zeros(len(a)); z[valid] = np.sum(normal[valid]*a[valid], axis=1)/denom[valid]
    q = z[:, None]*direction-a
    uu, uv, vv = np.sum(u*u, axis=1), np.sum(u*v, axis=1), np.sum(v*v, axis=1)
    qu, qv = np.sum(q*u, axis=1), np.sum(q*v, axis=1)
    determinant = uu*vv-uv*uv; valid &= determinant > 0
    x, y = np.zeros(len(a)), np.zeros(len(a))
    x[valid] = (vv[valid]*qu[valid]-uv[valid]*qv[valid])/determinant[valid]
    y[valid] = (uu[valid]*qv[valid]-uv[valid]*qu[valid])/determinant[valid]
    good = valid & (z > 1e-10) & (x >= -1e-10) & (y >= -1e-10) & (x+y <= 1+1e-10)
    return float(min(z[good])) if np.any(good) else None


def verify(data, output, cfg, selection):
    data, output = Path(data), Path(output)
    produced = load(output/'result.json')
    assert produced['id'] == cfg['id'] and produced['denominator'] == len(selection['cases']) == cfg['denominator']
    assert [c['id'] for c in produced['cases']] == [c['id'] for c in selection['cases']]
    assert [m['object'] for m in produced['models']] == selection['objects']
    info = load(data/'models/models_info.json'); models, meshes = [], {}
    for obj, expected in zip(selection['objects'], produced['models']):
        try:
            vertices, faces = ply(data/f'models/obj_{obj:06d}.ply')
            record = topology(vertices, faces, info[str(obj)], cfg)
        except Exception as e:
            assert expected.get('error') and not expected['mesh_gate'], 'unconfirmed producer mesh error'
            models.append({'object': obj, 'mesh_gate': False, 'independent_error': f'{type(e).__name__}: {e}'})
            continue
        assert not expected.get('error')
        for k in ('raw_vertices','exact_coordinate_classes','triangles','bad_edges','orientation_failures','zero_area_face_ids','below_area_face_ids','mesh_gate'):
            assert expected[k] == record[k], ('mesh mismatch', obj, k)
        assert np.isclose(record['minimum_area_m2'], expected['minimum_area_m2'], atol=1e-20, rtol=1e-8)
        assert abs(record['bbox_error_m']-expected['bbox_error_m']) <= cfg['tolerances']['numeric_m']
        with np.load(output/f'model_{obj:06d}.npz', allow_pickle=False) as payload:
            assert np.array_equal(payload['vertices_m'], vertices) and np.array_equal(payload['faces'], faces)
        meshes[obj] = (np.asarray(vertices), np.asarray(faces))
        models.append({'object': obj, **record})
    folder = data/f'test/{selection["scene"]:06d}'
    cams, gt, infos = [load(folder/n) for n in ('scene_camera.json', 'scene_gt.json', 'scene_gt_info.json')]
    images = {}
    for frame in selection['frames']:
        for kind in ('rgb', 'depth'):
            try:
                images[(frame, kind)] = png(folder/f'{kind}/{frame:06d}.png')
            except Exception as e:
                images[(frame, kind)] = e
    cases = []
    for expected, p in zip(selection['cases'], produced['cases']):
        try:
            result = check_case(folder, output, cfg, selection, expected, p, cams, gt, infos, images, meshes, models)
        except (AssertionError, KeyError, ValueError, IndexError) as e:
            # Reproduce input checks separately; an output mismatch must not masquerade as input failure.
            if p.get('input_error') and str(e).startswith('INPUT:'):
                cases.append({'id': p['id'], 'input_error_confirmed': True, 'error': str(e)})
                continue
            raise
        assert not p.get('input_error'), 'unconfirmed producer input failure'
        cases.append(result)
    d = cfg['decisions']
    decision = d['schema_or_coordinate'] if any(c.get('input_error_confirmed') for c in cases) else d['mesh'] if not all(m['mesh_gate'] for m in models) else d['missing_ray_support'] if not all(c['ray_support'] for c in cases) else d['numerical_pass']
    assert decision == produced['decision'] and not produced['physical_admission']
    assert produced['calibration_status'] == 'UNRESOLVED_BEFORE_EXECUTION'
    return {'status': 'VERIFIED', 'decision': decision, 'denominator': len(cases), 'models': models, 'cases': cases,
            'physical_admission': False, 'source_result_sha256': sha(output/'result.json')}


def check_case(folder, output, cfg, selection, expected, p, cams, gt, infos, images, meshes, models):
    assert all(p[k] == value for k, value in expected.items()), 'case identity mismatch'
    frame, obj, gi = expected['frame'], expected['object'], expected['gt_index']
    def require(condition, message):
        assert condition, 'INPUT: '+message
    try:
        record, cam = gt[str(frame)][gi], cams[str(frame)]
        require(record['obj_id'] == obj and len(gt[str(frame)]) == len(infos[str(frame)]), 'annotation association')
        require([x['obj_id'] for x in gt[str(frame)]] == [c['object'] for c in selection['cases'] if c['frame'] == frame], 'all object records')
        arrays = {}
        for kind in ('rgb', 'depth', 'mask', 'mask_visib'):
            try:
                decoded = images[(frame, kind)] if kind in ('rgb','depth') else png(folder/f'{kind}/{frame:06d}_{gi:06d}.png')
                if isinstance(decoded, Exception): raise decoded
                image, header = decoded
            except Exception as e:
                raise AssertionError('INPUT: PNG decode '+str(e)) from e
            role = kind if kind in ('rgb','depth') else 'mask'
            require(list(header[:4]) == [cfg['image']['width'], cfg['image']['height'], cfg['image'][role+'_bit_depth'], cfg['image'][role+'_color_type']], 'PNG schema')
            arrays[kind] = image
        raw, visible, full = arrays['depth'], arrays['mask_visib'] > 0, arrays['mask'] > 0
        require(all(set(np.unique(arrays[k])).issubset({0,255}) for k in ('mask','mask_visib')), 'binary mask')
        require(not np.any(visible & ~full), 'visible outside full mask')
        K = np.array(cam['cam_K'], dtype=float).reshape(3,3)
        require(np.isfinite(K).all() and K[0,0] > 0 and K[1,1] > 0, 'camera matrix')
        require(max(abs(K[0,1]),abs(K[1,0]),abs(K[2,0]),abs(K[2,1]),abs(K[2,2]-1)) <= cfg['tolerances']['camera_structure'], 'camera structure')
        require(0 <= K[0,2] < cfg['image']['width'] and 0 <= K[1,2] < cfg['image']['height'], 'principal point')
        scale = float(cam['depth_scale']); require(np.isfinite(scale) and scale > 0, 'depth scale')
        transforms = [(record['cam_R_m2c'], record['cam_t_m2c'])]
        if 'cam_R_w2c' in cam or 'cam_t_w2c' in cam: transforms.append((cam['cam_R_w2c'], cam['cam_t_w2c']))
        for rs, ts in transforms:
            R = np.array(rs).reshape(3,3); t = np.array(ts).reshape(3)*.001
            require(np.isfinite(R).all() and np.isfinite(t).all(), 'nonfinite pose')
            require(np.max(np.abs(R@R.T-np.eye(3))) <= cfg['tolerances']['rotation_orthogonality'], 'nonrigid pose')
            require(abs(np.linalg.det(R)-1) <= cfg['tolerances']['rotation_determinant'], 'reflected/scaled pose')
        R = np.array(record['cam_R_m2c']).reshape(3,3); t = np.array(record['cam_t_m2c']).reshape(3)*.001
        pixels_all = np.argwhere(visible & (raw != 0)); require(len(pixels_all) > 0, 'no valid observed pixels')
    except (KeyError, ValueError, IndexError, struct.error, zlib.error) as e:
        raise AssertionError('INPUT: '+str(e)) from e
    n = min(cfg['diagnostic']['rays_per_instance'], len(pixels_all))
    # Scalar integer quotient, independent of vectorized producer indexing.
    ids = np.array([divmod(i*(len(pixels_all)-1), n-1)[0] for i in range(n)]) if n > 1 else np.array([0])
    pixels = pixels_all[ids]
    z = raw[pixels[:,0],pixels[:,1]].astype(float)*scale/1000
    pixel_h = np.column_stack((pixels[:,1],pixels[:,0],np.ones(n)))
    direction = pixel_h@np.linalg.inv(K).T
    points = direction*z[:,None]
    T = np.eye(4); T[:3,:3] = R; T[:3,3] = t
    object_points = np.column_stack((points,np.ones(n)))@np.linalg.inv(T).T
    with np.load(output/f'{p["id"]}.npz', allow_pickle=False) as saved:
        for key, value in [('pixels',pixels),('selected_indices',ids)]: assert np.array_equal(saved[key],value), key
        for key,value in [('camera_points_m',points),('object_points_m',object_points[:,:3]),('K',K),('R_m2c',R),('t_m2c_m',t)]:
            assert np.max(np.abs(saved[key]-value)) <= cfg['tolerances']['numeric_m'], key
    projected = points@K.T; error_px=float(np.max(np.abs(projected[:,:2]/projected[:,2,None]-pixels[:,::-1])))
    inverse=float(np.max(np.abs(object_points@T.T-np.column_stack((points,np.ones(n))))))
    require(error_px <= cfg['tolerances']['projection_px'] and inverse <= cfg['tolerances']['numeric_m'], 'coordinate roundtrip')
    assert p.get('input_pass') and not p.get('input_error'), 'unconfirmed producer input failure'
    assert 0 <= p['projection_error_px'] <= cfg['tolerances']['projection_px']
    assert 0 <= p['inverse_error_m'] <= cfg['tolerances']['numeric_m']
    assert abs(p['projection_error_px']-error_px) <= cfg['tolerances']['projection_px']
    assert abs(p['inverse_error_m']-inverse) <= cfg['tolerances']['numeric_m']
    assert p['valid_pixels']==len(pixels_all) and p['visible_pixels']==int(visible.sum())
    assert p['visible_missing_depth_pixels']==int(np.sum(visible & (raw==0))) and p['full_mask_pixels']==int(full.sum())
    assert p['supports_2048_observed_pixels']==(len(pixels_all)>=2048)
    assert p['diagnostic_pixels']==pixels.tolist() and np.max(np.abs(np.array(p['observed_depth_m'])-z)) <= cfg['tolerances']['numeric_m']
    mesh_gate = next(m['mesh_gate'] for m in models if m['object']==obj)
    assert p['mesh_gate']==mesh_gate
    support=False; max_error=None
    if mesh_gate:
        v,f=meshes[obj]; hom=np.column_stack((v,np.ones(len(v))))@T.T; triangles=hom[f,:3]
        model_z=[ray(d,triangles) for d in direction]
        assert len(model_z)==len(p['ray_model_depth_m'])==len(p['residual_m'])
        errors=[]
        for i,(a,b) in enumerate(zip(model_z,p['ray_model_depth_m'])):
            assert (a is None)==(b is None), 'ray hit/miss differs'
            if a is not None:
                errors.append(abs(a-b)); assert abs(a-b)<=cfg['tolerances']['ray_intersection_m']
                assert abs((z[i]-a)-p['residual_m'][i])<=cfg['tolerances']['ray_intersection_m']
            else: assert p['residual_m'][i] is None
        residual=[abs(z[i]-v) for i,v in enumerate(model_z) if v is not None]
        for key,value in [('median_absolute_residual_m',float(np.median(residual)) if residual else None),('maximum_absolute_residual_m',max(residual) if residual else None)]:
            assert (p[key] is None)==(value is None)
            if value is not None: assert abs(p[key]-value)<=cfg['tolerances']['ray_intersection_m']
        assert p['missing_model_rays']==model_z.count(None)
        support=len(pixels_all)>=cfg['diagnostic']['rays_per_instance'] and None not in model_z
        max_error=max(errors,default=0)
    else:
        assert p.get('residual_skipped') and not p['ray_model_depth_m'] and not p['residual_m']
    assert p['ray_support']==support
    return {'id': p['id'], 'input_verified': True, 'mesh_gate': mesh_gate, 'ray_support': support,
            'ray_comparison_max_error_m': max_error, 'valid_pixels': len(pixels_all)}


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--data',required=True); parser.add_argument('--input',required=True); parser.add_argument('--output',required=True)
    a=parser.parse_args(); study=Path(__file__).resolve().parent
    for name,h in load(study/'freeze.json')['files'].items(): assert sha(study/name)==h, ('INVALID_INTEGRITY',name)
    for item in load(study/'assets.json')['files']:
        f=Path(a.data)/item['destination']; assert f.stat().st_size==item['bytes'] and sha(f)==item['sha256'], ('INVALID_INTEGRITY',str(f))
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True);assert not any(out.iterdir())
    receipt=verify(a.data,a.input,load(study/'protocol.json'),load(study/'selection.json'))
    (out/'verification.json').write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'decision':receipt['decision'],'denominator':receipt['denominator']}))


if __name__=='__main__': main()
