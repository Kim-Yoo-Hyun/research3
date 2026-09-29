"""Post-failure detail on immutable paired artifacts; independent of scene/PyBullet; Docker only."""
from collections import Counter, defaultdict
import json
from pathlib import Path

from verify_preservation import cross, load, pair_check, read_exact, sha, surface_proof


def main():
    study, assets, root, out = map(Path, ('/study', '/assets', '/input', '/output'))
    assert not any(out.iterdir())
    plan = load(study/'inspection_plan.json')
    for manifest in (load(study/'freeze.json'), load(study/'preservation_freeze.json'), load(study/'inspection_freeze.json')):
        for name, digest in manifest['files'].items():
            assert sha(study/name) == digest
    execution = load(root/'execution.json')
    for name, item in execution['files'].items():
        assert sha(root/name) == item['sha256'] and (root/name).stat().st_size == item['bytes']
    assert sha(root/'execution.json') == sha(study/'preservation_execution.json')
    cfg = load(study/'protocol.json')
    audit = load(root/'audit/verification.json')
    assert len(audit['errors']) == 1 and audit['errors'][0]['object'] == '025_mug'
    data = root/'data'
    assets_manifest = load(study/'assets.json')
    oi = cfg['objects'].index('025_mug')
    asset = assets_manifest['objects'][oi]
    raw_path = assets/Path(asset['mesh_path']).name
    assert sha(raw_path) == asset['mesh_sha256']
    rv, rf = read_exact(raw_path)
    nv, nf = read_exact(data/'meshes/025_mug.obj')
    proof, kept = surface_proof(rv, rf, nv, nf)
    edge_faces, signed = defaultdict(list), Counter()
    triangles = [tuple(nv[i] for i in f) for f in nf]
    for fi, f in enumerate(nf):
        for a, b in ((f[0], f[1]), (f[1], f[2]), (f[2], f[0])):
            edge = tuple(sorted((a, b)))
            edge_faces[edge].append(fi)
            signed[edge] += 1 if a < b else -1
    bad = []
    for edge, faces in sorted(edge_faces.items()):
        if len(faces) != 2 or signed[edge] != 0:
            bad.append({'derived_vertex_ids': edge,
                        'exact_coordinates': [[str(x) for x in nv[i]] for i in edge],
                        'degree': len(faces), 'orientation_sum': signed[edge],
                        'incident_faces': [{'derived_id': i, 'raw_id': kept[i], 'derived_vertex_ids': nf[i],
                                            'exact_coordinates': [[str(x) for x in p] for p in triangles[i]],
                                            'positive_area_exact': any(cross(*triangles[i]))} for i in faces]})
    duplicates = Counter(tuple(sorted(t)) for t in triangles)
    duplicate_groups = []
    for tri, count in duplicates.items():
        if count > 1:
            ids = [i for i, t in enumerate(triangles) if tuple(sorted(t)) == tri]
            duplicate_groups.append({'multiplicity': count, 'derived_face_ids': ids, 'raw_face_ids': [kept[i] for i in ids]})
    extent = max(max(v[k] for v in rv)-min(v[k] for v in rv) for k in range(3))
    scale = cfg['asset_scale']['longest_aabb_extent_m']/float(extent)
    area_min = min(sum(float(x)**2 for x in cross(*tri))*scale**4/4 for tri in triangles)**0.5
    bad_count = sum(len(f) != 2 for f in edge_faces.values())
    orientation_count = sum(x != 0 for x in signed.values())
    producer = load(data/'result.json')['objects'][oi]['derived']
    assert producer['bad_edge_count'] == bad_count and producer['bad_orientation_count'] == orientation_count
    assert bad_count > 0, 'do not silently change the failed gate'
    cases, errors = [], []
    for vi in (0, 1):
        case_id = f'025_mug_v{vi}'
        try:
            cases.append(pair_check(data, case_id, rv, rf, nv, nf, kept, cfg, oi, vi))
        except Exception as e:
            error = f'{type(e).__name__}: {e}'
            errors.append({'id': case_id, 'error': error})
            cases.append({'id': case_id, 'verified': False, 'error': error})
    result = {'id': plan['id'], 'status': 'COMPLETED', 'decision': 'DEFER_CURRENT_ASSET_ROUTE',
              'object': '025_mug', 'exact_surface_proof': proof,
              'derived_edge_degree_histogram': dict(sorted(Counter(len(x) for x in edge_faces.values()).items())),
              'bad_edge_count': bad_count, 'orientation_failures': orientation_count,
              'minimum_triangle_area_m2': area_min, 'original_area_gate_pass': area_min >= cfg['tolerances']['mesh_area_min_m2'],
              'remaining_bad_edges': bad, 'duplicate_unoriented_positive_triangle_groups': duplicate_groups,
              'mug_query_cases': cases, 'query_errors': errors,
              'box_query_cases': 'verified in immutable first audit; not reexecuted',
              'study_denominator': 4, 'readiness_v1_decision_unchanged': 'REFINE_LINKAGE',
              'producer_and_original_audit_modified': False, 'further_mesh_modification': False,
              'paired_execution_sha256': sha(root/'execution.json'),
              'inspection_freeze_sha256': sha(study/'inspection_freeze.json'),
              'boundary': 'surface set equality and finite-query agreement do not resolve non-two-incidence edges; no readiness/completion promotion'}
    (out/'verification.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'decision': result['decision'], 'bad_edges': bad_count, 'duplicate_groups': len(duplicate_groups), 'query_errors': errors}))


if __name__ == '__main__':
    main()
