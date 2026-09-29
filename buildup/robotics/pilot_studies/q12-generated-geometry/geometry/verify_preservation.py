"""Independent exact OBJ/surface and saved-query audit; no scene/PyBullet import. Docker only."""
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path

import numpy as np

from verify import geometry_label, inside_by_rays


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def read_exact(path):
    vertices, faces = [], []
    for line in path.read_text().splitlines():
        fields = line.split()
        if fields and fields[0] == 'v':
            vertices.append(tuple(Fraction(x) for x in fields[1:4]))
        elif fields and fields[0] == 'f':
            faces.append(tuple(int(x.partition('/')[0])-1 for x in fields[1:]))
    assert all(len(f) == 3 and min(f) >= 0 and max(f) < len(vertices) for f in faces)
    return vertices, faces


def cross(a, b, c):
    u = tuple(y-x for x, y in zip(a, b))
    v = tuple(y-x for x, y in zip(a, c))
    return (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])


def surface_proof(raw_v, raw_f, new_v, new_f):
    unique = list(dict.fromkeys(raw_v))
    assert new_v == unique, 'coordinate classes/order changed'
    raw_tri = [tuple(raw_v[i] for i in f) for f in raw_f]
    positive = [i for i, t in enumerate(raw_tri) if any(cross(*t))]
    removed = [i for i, t in enumerate(raw_tri) if not any(cross(*t))]
    new_tri = [tuple(new_v[i] for i in f) for f in new_f]
    assert new_tri == [raw_tri[i] for i in positive], 'positive oriented triangle sequence changed'
    edges, points = {}, {}
    for i, tri in enumerate(new_tri):
        for v in tri:
            points.setdefault(v, i)
        for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            edges.setdefault(tuple(sorted((a, b))), i)
    witnesses = []
    for i in removed:
        support = sorted(set(raw_tri[i]))
        assert len(support) <= 2, 'three-distinct collinear face outside allowed correction'
        if len(support) == 2:
            key = tuple(support)
            assert key in edges, 'removed segment not a retained triangle edge'
            witness = edges[key]
        else:
            assert support[0] in points, 'removed point not a retained triangle vertex'
            witness = points[support[0]]
        witnesses.append({'removed_raw_face_id': i, 'retained_raw_face_id': positive[witness],
                          'derived_face_id': witness, 'support': 'segment' if len(support) == 2 else 'point'})
    return {'exact_surface_equal': True, 'positive_face_count': len(positive),
            'removed_face_ids': removed, 'removed_support_witnesses': witnesses}, positive


def self_tests():
    v = [tuple(map(Fraction, p)) for p in ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))]
    f = [(0, 2, 1), (0, 1, 3), (1, 2, 3), (2, 0, 3)]
    raw = f+[(0, 0, 1)]
    surface_proof(v, raw, v, f)
    moved = list(v)
    moved[1] = (v[1][0]+Fraction(1, 10**12), v[1][1], v[1][2])
    detached = v+[(Fraction(2), Fraction(2), Fraction(2))]
    variants = [('orientation', v, raw, v, [(0, 1, 2)]+f[1:]),
                ('coordinate_motion', v, raw, moved, f),
                ('positive_face_removal', v, raw, v, f[1:]),
                ('positive_face_duplication', v, raw, v, f+[f[0]]),
                ('uncovered_zero_area_support', detached, f+[(0, 4, 4)], detached, f)]
    rejected = []
    for name, rv, rf, nv, nf in variants:
        try:
            surface_proof(rv, rf, nv, nf)
        except AssertionError:
            rejected.append(name)
        else:
            raise AssertionError(f'negative control not rejected: {name}')
    return {'positive_control_passed': True, 'negative_controls_rejected': rejected}


def topology(vertices, faces, scale, minimum):
    counts, orientations = Counter(), Counter()
    area2 = []
    for face in faces:
        a, b, c = [vertices[i] for i in face]
        area2.append(sum(float(x)**2 for x in cross(a, b, c))*scale**4/4)
        for u, v in ((face[0], face[1]), (face[1], face[2]), (face[2], face[0])):
            edge = tuple(sorted((u, v)))
            counts[edge] += 1
            orientations[edge] += 1 if u < v else -1
    result = {'vertices': len(vertices), 'faces': len(faces),
              'edge_degree_histogram': dict(sorted(Counter(counts.values()).items())),
              'bad_edges': sum(c != 2 for c in counts.values()),
              'orientation_failures': sum(c != 0 for c in orientations.values()),
              'minimum_triangle_area_m2': min(area2)**0.5}
    assert not result['bad_edges'] and not result['orientation_failures'], 'corrected edge gate failed'
    assert min(area2) >= minimum**2, 'corrected original area gate failed'
    return result


def arrays(path):
    with np.load(path, allow_pickle=False) as payload:
        return dict(payload)


def pair_check(data, case_id, rv, rf, nv, nf, kept, cfg, oi, vi):
    roots = [data/variant/case_id for variant in ('raw', 'derived')]
    obs = [arrays(p/'observation.npz') for p in roots]
    geo = [arrays(p/'geometry.npz') for p in roots]
    rows = [load(p/'candidates.json') for p in roots]
    rec = [load(p/'result.json') for p in roots]
    tol = cfg['tolerances']['numeric_roundtrip_m']
    assert rows[0] == rows[1] and (roots[0]/'candidates.json').read_bytes() == (roots[1]/'candidates.json').read_bytes()
    assert set(obs[0]) == set(obs[1])
    for key in obs[0]:
        assert np.array_equal(obs[0][key], obs[1][key]), f'observation mismatch: {key}'
    raw = np.asarray(rv, dtype=np.float64)
    center = (raw.min(0)+raw.max(0))/2
    scale = cfg['asset_scale']['longest_aabb_extent_m']/np.ptp(raw, axis=0).max()
    mapped_triangles = []
    for index, (vertices, faces) in enumerate(((rv, rf), (nv, nf))):
        expected = (np.asarray(vertices, dtype=np.float64)-center)*scale+cfg['asset_scale']['aabb_center_world_m']
        assert np.array_equal(geo[index]['vertices'], expected)
        assert np.array_equal(geo[index]['faces'], faces)
        assert rec[index]['seed'] == cfg['sampling']['area_uniform_seed']+oi*2+vi
        assert rec[index]['view_index'] == vi and rec[index]['camera']['eye'] == cfg['camera']['eyes_m'][vi]
        assert rec[index]['candidate_sha256'] == sha(roots[index]/'candidates.json')
        assert np.array_equal(obs[index]['depth_buffer'], obs[index]['repeat_depth_buffer'])
        assert np.array_equal(obs[index]['segmentation'], obs[index]['repeat_segmentation'])
        mapped_triangles.append(geo[index]['vertices'][geo[index]['faces']])
    assert np.array_equal(mapped_triangles[0][kept], mapped_triangles[1])
    for key in ('oracle_points', 'barycentric'):
        assert np.array_equal(geo[0][key], geo[1][key]), key
    assert np.array_equal(geo[0]['triangle_ids'], np.asarray(kept)[geo[1]['triangle_ids']])
    independent, box_rows, distances, windings, near = [], [], [], [], []
    assert len(rows[0]) == len(rec[0]['labels']) == len(rec[1]['labels']) == cfg['gripper']['candidate_count']
    for row, la, lb in zip(rows[0], rec[0]['labels'], rec[1]['labels'], strict=True):
        truth = [geometry_label(t, row) for t in mapped_triangles]
        assert truth[0] == truth[1], 'independent surface/solid label changed'
        assert all(la[k] == lb[k] for k in ('id', 'collision', 'near_contact', 'oracle_8192_collision', 'oracle_32768_collision'))
        assert row['id'] == la['id'] == len(independent)
        assert len(la['boxes']) == len(lb['boxes']) == len(row['boxes']) == 3
        assert la['near_contact'] == any(x['distance_m'] is not None and abs(x['distance_m']) <= cfg['tolerances']['near_contact_m'] for x in la['boxes'])
        if not la['near_contact']:
            assert truth[0] == la['collision'], 'robust producer/independent mismatch'
        else:
            near.append(row['id'])
        independent.append(truth[0])
        for bi, (box, a, b) in enumerate(zip(row['boxes'], la['boxes'], lb['boxes'], strict=True)):
            inside = [inside_by_rays(np.asarray(box['center']), t) for t in mapped_triangles]
            assert inside[0] == inside[1] == a['center_inside'] == b['center_inside'], 'box-center containment mismatch'
            da, db = a['distance_m'], b['distance_m']
            assert (da is None) == (db is None)
            if da is not None:
                assert np.isfinite(da) and np.isfinite(db) and abs(da-db) <= tol
                distances.append(abs(da-db))
            dw = abs(a['absolute_winding']-b['absolute_winding'])
            assert np.isfinite(dw) and dw <= tol
            windings.append(dw)
            box_rows.append({'candidate_id': row['id'], 'box': bi, 'independent_inside': inside[0]})
    return {'id': case_id, 'verified': True, 'independent_labels': independent, 'box_centers': box_rows,
            'robust_candidates': len(independent)-len(near), 'near_contact_ids': near,
            'max_distance_delta_m': max(distances, default=0), 'max_winding_delta': max(windings, default=0),
            'observations_candidates_oracle_equal': True}


def main():
    study, assets, data, out = map(Path, ('/study', '/assets', '/input', '/output'))
    assert not any(out.iterdir())
    spec, cfg = load(study/'preservation_protocol.json'), load(study/'protocol.json')
    assert sha(study/'freeze.json') == spec['old_freeze_sha256']
    for manifest in (load(study/'freeze.json'), load(study/'preservation_freeze.json')):
        for name, digest in manifest['files'].items():
            assert sha(study/name) == digest
    producer = load(data/'result.json')
    assert producer['freeze_sha256'] == sha(study/'preservation_freeze.json')
    for name, item in producer['files'].items():
        assert sha(data/name) == item['sha256'] and (data/name).stat().st_size == item['bytes']
    expected = [f'{o}_v{i}' for o in spec['objects'] for i in spec['views']]
    assert [r['id'] for r in producer['cases']] == expected and producer['denominator'] == spec['denominator'] == 4
    tests = self_tests()
    proofs, cases, errors = [], [], list(producer['errors'])
    for oi, asset in enumerate(load(study/'assets.json')['objects']):
        name = asset['id']
        try:
            raw_path = assets/Path(asset['mesh_path']).name
            assert sha(raw_path) == asset['mesh_sha256']
            rv, rf = read_exact(raw_path)
            nv, nf = read_exact(data/'meshes'/f'{name}.obj')
            proof, kept = surface_proof(rv, rf, nv, nf)
            mapping = arrays(data/'meshes'/f'{name}.npz')
            canonical = {v: i for i, v in enumerate(nv)}
            first = {}
            for i, vertex in enumerate(rv):
                first.setdefault(vertex, i)
            assert np.array_equal(mapping['raw_to_derived_vertex'], [canonical[v] for v in rv])
            assert np.array_equal(mapping['representatives'], [first[v] for v in nv])
            assert np.array_equal(mapping['kept_face_ids'], kept)
            extent = max(max(v[k] for v in rv)-min(v[k] for v in rv) for k in range(3))
            scale = cfg['asset_scale']['longest_aabb_extent_m']/float(extent)
            proof.update({'object': name, 'derived_sha256': sha(data/'meshes'/f'{name}.obj'),
                          'topology': topology(nv, nf, scale, cfg['tolerances']['mesh_area_min_m2'])})
            proofs.append(proof)
        except Exception as e:
            errors.append({'object': name, 'error': f'{type(e).__name__}: {e}'})
            for vi in spec['views']:
                cases.append({'id': f'{name}_v{vi}', 'verified': False, 'error': 'surface audit failed'})
            continue
        for vi in spec['views']:
            case_id = f'{name}_v{vi}'
            try:
                cases.append(pair_check(data, case_id, rv, rf, nv, nf, kept, cfg, oi, vi))
            except Exception as e:
                error = f'{type(e).__name__}: {e}'
                errors.append({'id': case_id, 'error': error})
                cases.append({'id': case_id, 'verified': False, 'error': error})
    assert [c['id'] for c in cases] == expected
    good = not errors and all(c['verified'] for c in cases) and all(c['paired_pass'] for c in producer['cases']) and all(o['derived_original_mesh_gates_pass'] for o in producer['objects'])
    result = {'status': 'VERIFIED' if good else 'NEEDS_ASSESSMENT', 'decision': spec['success'] if good else spec['failure'],
              'denominator': 4, 'surface_proofs': proofs, 'cases': cases, 'errors': errors, 'self_tests': tests,
              'source_result_sha256': sha(data/'result.json'), 'freeze_sha256': sha(study/'preservation_freeze.json'),
              'readiness_v1_decision_unchanged': 'REFINE_LINKAGE', 'readiness_revision_executed': False,
              'boundary': spec['limits']}
    (out/'verification.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'decision': result['decision'], 'errors': errors}))


if __name__ == '__main__':
    main()
