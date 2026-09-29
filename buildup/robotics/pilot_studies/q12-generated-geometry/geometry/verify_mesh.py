"""Post-run audit of failed mesh gates; standard library only, executed in CPU Docker.

Does not import the producer, NumPy or PyBullet, repair inputs, or execute scene rendering.
"""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def topology(faces):
    incidence, directions = Counter(), Counter()
    for a, b, c in faces:
        for u, v in ((a, b), (b, c), (c, a)):
            edge = (min(u, v), max(u, v))
            incidence[edge] += 1
            directions[edge] += 1 if u < v else -1
    return incidence, directions


def main():
    study, assets, data, out = map(Path, ('/study', '/assets', '/input', '/output'))
    assert not any(out.iterdir())
    frozen = json.loads((study/'freeze.json').read_text())
    for name, h in frozen['files'].items():
        assert sha(study/name) == h
    protocol = json.loads((study/'protocol.json').read_text())
    manifest = json.loads((study/'assets.json').read_text())
    execution = json.loads((data/'execution.json').read_text())
    for name, item in execution['files'].items():
        path = data/name
        assert path.stat().st_size == item['bytes'] and sha(path) == item['sha256']
    source = json.loads((data/'data/result.json').read_text())
    expected_ids = [f'{obj}_v{vi}' for obj in protocol['objects'] for vi in range(2)]
    assert [r['id'] for r in source['cases']] == expected_ids and source['denominator'] == 4
    records = []
    for item in manifest['objects']:
        mesh = assets/Path(item['mesh_path']).name
        assert sha(mesh) == item['mesh_sha256'] and mesh.stat().st_size == item['mesh_bytes']
        vertices, faces = [], []
        for line in mesh.read_text().splitlines():
            fields = line.split()
            if fields and fields[0] == 'v':
                vertices.append(tuple(map(float, fields[1:4])))
            elif fields and fields[0] == 'f':
                faces.append(tuple(int(x.partition('/')[0])-1 for x in fields[1:]))
        assert all(len(v) == 3 and all(math.isfinite(x) for x in v) for v in vertices)
        assert all(len(f) == 3 and min(f) >= 0 and max(f) < len(vertices) for f in faces)
        canonical = {v: i for i, v in enumerate(sorted(set(vertices)))}
        welded = [tuple(canonical[vertices[i]] for i in f) for f in faces]
        edges, orientation = topology(welded)
        raw_edges, raw_orientation = topology(faces)
        lo = [min(v[k] for v in vertices) for k in range(3)]
        hi = [max(v[k] for v in vertices) for k in range(3)]
        scale = protocol['asset_scale']['longest_aabb_extent_m']/max(b-a for a, b in zip(lo, hi))
        areas = []
        for a, b, c in faces:
            u = [vertices[b][k]-vertices[a][k] for k in range(3)]
            v = [vertices[c][k]-vertices[a][k] for k in range(3)]
            cross = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
            areas.append(math.sqrt(sum(x*x for x in cross))*scale*scale/2)
        bad = sorted(e for e, n in edges.items() if n != 2)
        bad_orientation = sorted(e for e, n in orientation.items() if n != 0)
        below = [i for i, a in enumerate(areas) if a < protocol['tolerances']['mesh_area_min_m2']]
        repeated_faces = [i for i, f in enumerate(welded) if len(set(f)) < 3]
        producer = json.loads((data/'data'/f"{item['id']}_mesh.json").read_text())
        expected = producer['geometry']
        assert expected['raw_vertices'] == len(vertices)
        assert expected['exact_unique_vertices'] == len(canonical)
        assert expected['triangles'] == len(faces)
        assert expected['bad_edge_count'] == len(bad)
        assert expected['bad_orientation_count'] == len(bad_orientation)
        assert expected['closed_oriented_edges'] == (not bad and not bad_orientation)
        assert math.isclose(expected['minimum_triangle_area_m2'], min(areas), rel_tol=1e-8, abs_tol=1e-20)
        failed = bool(bad or bad_orientation or below)
        case_rows = [r for r in source['cases'] if r['object'] == item['id']]
        assert len(case_rows) == 2 and all(bool(r.get('error')) == failed for r in case_rows)
        if failed:
            assert all(not (data/'data'/r['id']).exists() for r in case_rows)
        records.append({'object': item['id'], 'raw_vertices': len(vertices), 'exact_unique_vertices': len(canonical),
                        'faces': len(faces), 'raw_index_edge_degree_histogram': dict(sorted(Counter(raw_edges.values()).items())),
                        'welded_edge_degree_histogram': dict(sorted(Counter(edges.values()).items())),
                        'raw_index_orientation_failures': sum(n != 0 for n in raw_orientation.values()),
                        'bad_welded_edges': len(bad), 'bad_welded_orientation': len(bad_orientation),
                        'minimum_triangle_area_m2': min(areas), 'below_area_threshold_face_ids_zero_based': below,
                        'repeated_coordinate_face_ids_zero_based': repeated_faces,
                        'bad_edge_samples': [{'canonical_vertex_ids': list(e), 'degree': edges[e], 'orientation_sum': orientation[e]} for e in bad[:12]],
                        'mesh_sha256': sha(mesh), 'producer_receipt_sha256': sha(data/'data'/f"{item['id']}_mesh.json"),
                        'gate_failure_independently_confirmed': failed})
    final = json.loads((data/'audit/verification.json').read_text())
    assert final['decision'] == 'REFINE_LINKAGE' and len(final['errors']) == 2
    assert [r['object'] for r in records if r['gate_failure_independently_confirmed']] == ['025_mug']
    receipt = {'status': 'VERIFIED', 'decision': final['decision'], 'denominator': 4, 'objects': records,
               'source': 'independent scalar tuple/Counter/triangle-area calculation; no scene.py/NumPy/PyBullet import',
               'inputs_repaired': False, 'rendering_or_collision_reexecuted': False,
               'frozen_digest': sha(study/'freeze.json'), 'execution_digest': sha(data/'execution.json'),
               'verifier_digest': sha(data/'audit/verification.json'), 'audit_script_sha256': sha(Path(__file__))}
    (out/'verification.json').write_text(json.dumps(receipt, indent=2, allow_nan=False)+'\n')
    print(json.dumps(receipt, allow_nan=False))


if __name__ == '__main__':
    main()
