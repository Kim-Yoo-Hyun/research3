"""Paired representation diagnostic, separate from frozen readiness v1; Docker only."""
import json
from pathlib import Path

import numpy as np
import pybullet as pb

import scene


def load(path):
    return json.loads(Path(path).read_text())


def inventory(root):
    return {str(p.relative_to(root)): {'bytes': p.stat().st_size, 'sha256': scene.digest(p)}
            for p in sorted(root.rglob('*')) if p.is_file()}


def compare(root, case_id, kept, tol):
    a, b = root/'raw'/case_id, root/'derived'/case_id
    ra, rb = load(a/'result.json'), load(b/'result.json')
    result = {'id': case_id, 'observations_equal': {}, 'oracle_equal': {},
              'candidate_bytes_equal': (a/'candidates.json').read_bytes() == (b/'candidates.json').read_bytes()}
    with np.load(a/'observation.npz') as x, np.load(b/'observation.npz') as y:
        assert set(x.files) == set(y.files)
        result['observations_equal'] = {k: bool(np.array_equal(x[k], y[k])) for k in x.files}
    with np.load(a/'geometry.npz') as x, np.load(b/'geometry.npz') as y:
        result['oracle_equal'] = {k: bool(np.array_equal(x[k], y[k])) for k in ('oracle_points', 'barycentric')}
        result['oracle_equal']['mapped_triangle_ids'] = bool(np.array_equal(x['triangle_ids'], kept[y['triangle_ids']]))
    labels_equal, missing_equal, center_equal = True, True, True
    distances, windings = [], []
    for la, lb in zip(ra['labels'], rb['labels'], strict=True):
        labels_equal &= all(la[k] == lb[k] for k in ('id', 'collision', 'near_contact', 'oracle_8192_collision', 'oracle_32768_collision'))
        for ba, bb in zip(la['boxes'], lb['boxes'], strict=True):
            center_equal &= ba['center_inside'] == bb['center_inside']
            da, db = ba['distance_m'], bb['distance_m']
            missing_equal &= (da is None) == (db is None)
            if da is not None and db is not None:
                distances.append(abs(da-db))
            windings.append(abs(ba['absolute_winding']-bb['absolute_winding']))
    result.update({'label_flags_equal': labels_equal, 'distance_presence_equal': missing_equal,
                   'center_inside_equal': center_equal, 'max_distance_delta_m': max(distances, default=0),
                   'max_winding_delta': max(windings, default=0), 'candidate_count': len(ra['labels']),
                   'near_contact_count': sum(x['near_contact'] for x in ra['labels'])})
    result['paired_pass'] = bool(all(result['observations_equal'].values()) and all(result['oracle_equal'].values())
                                 and result['candidate_bytes_equal'] and labels_equal and missing_equal and center_equal
                                 and result['max_distance_delta_m'] <= tol and result['max_winding_delta'] <= tol)
    return result


def main():
    study, assets, old, out = map(Path, ('/study', '/assets', '/old', '/output'))
    assert not any(out.iterdir())
    cfg = load(study/'protocol.json')
    spec = load(study/'preservation_protocol.json')
    freeze = load(study/'preservation_freeze.json')
    assert scene.digest(study/'freeze.json') == spec['old_freeze_sha256']
    for manifest in (freeze, load(study/'freeze.json')):
        for name, sha in manifest['files'].items():
            assert scene.digest(study/name) == sha, name
    assert scene.digest(old/'execution.json') == scene.digest(study/'execution.json')
    previous = load(old/'execution.json')
    for name, item in previous['files'].items():
        assert scene.digest(old/name) == item['sha256'] and (old/name).stat().st_size == item['bytes']
    assert load(old/'audit/verification.json')['decision'] == 'REFINE_LINKAGE'
    assert cfg['objects'] == spec['objects']
    records, cases, errors = [], [], []
    (out/'raw').mkdir()
    (out/'derived').mkdir()
    (out/'meshes').mkdir()
    pb.connect(pb.DIRECT)
    for oi, asset in enumerate(load(study/'assets.json')['objects']):
        name = asset['id']
        path = assets/Path(asset['mesh_path']).name
        assert scene.digest(path) == asset['mesh_sha256']
        v, f = scene.read_obj(path)
        world, _, raw_receipt = scene.prepare_mesh(v, f, cfg['asset_scale'])
        unique, first, inverse = np.unique(v, axis=0, return_index=True, return_inverse=True)
        order = np.argsort(first)
        remap = np.empty(len(order), dtype=np.int64)
        remap[order] = np.arange(len(order))
        representatives, inverse = first[order], remap[inverse]
        tri = v[f]
        zero = np.all(np.cross(tri[:, 1]-tri[:, 0], tri[:, 2]-tri[:, 0]) == 0, axis=1)
        wf = inverse[f]
        repeated = (wf[:, 0] == wf[:, 1]) | (wf[:, 1] == wf[:, 2]) | (wf[:, 0] == wf[:, 2])
        # Three-distinct collinear faces need a different proof, so do not silently remove them.
        assert np.array_equal(zero, repeated), 'unsupported distinct-coordinate degeneracy'
        kept = np.flatnonzero(~zero)
        clean_v, clean_f = v[representatives], wf[kept]
        clean_world = world[representatives]  # use the original transform, not new bounds
        recomputed, _, cleaned_receipt = scene.prepare_mesh(clean_v, clean_f, cfg['asset_scale'])
        assert np.array_equal(recomputed, clean_world)
        assert np.array_equal(world[f[kept]], clean_world[clean_f])
        vertex_lines = [line for line in path.read_text().splitlines() if line.startswith('v ')]
        obj = '\n'.join(vertex_lines[i] for i in representatives) + '\n'
        obj += ''.join('f '+' '.join(str(int(i)+1) for i in face)+'\n' for face in clean_f)
        (out/'meshes'/f'{name}.obj').write_text(obj)
        np.savez_compressed(out/'meshes'/f'{name}.npz', representatives=representatives,
                            raw_to_derived_vertex=inverse, kept_face_ids=kept)
        gate = cleaned_receipt['closed_oriented_edges'] and cleaned_receipt['minimum_triangle_area_m2'] >= cfg['tolerances']['mesh_area_min_m2']
        records.append({'object': name, 'removed_face_ids': np.flatnonzero(zero).tolist(),
                        'raw': raw_receipt, 'derived': cleaned_receipt, 'derived_original_mesh_gates_pass': gate})
        for vi in spec['views']:
            case_id = f'{name}_v{vi}'
            seed = cfg['sampling']['area_uniform_seed']+oi*2+vi
            for variant, vertices, faces in [('raw', world, f), ('derived', clean_world, clean_f)]:
                try:
                    scene.run_case(vertices, faces, cfg, vi, out/variant/case_id, seed)
                except Exception as e:
                    errors.append({'id': case_id, 'variant': variant, 'error': f'{type(e).__name__}: {e}'})
            if any(e['id'] == case_id for e in errors):
                cases.append({'id': case_id, 'paired_pass': False, 'error': 'case execution failed; see errors'})
            else:
                cases.append(compare(out, case_id, kept, cfg['tolerances']['numeric_roundtrip_m']))
    pb.disconnect()
    result = {'id': spec['id'], 'denominator': spec['denominator'], 'objects': records, 'cases': cases,
              'errors': errors, 'independent_verification_required': True, 'readiness_v1_decision': 'REFINE_LINKAGE',
              'freeze_sha256': scene.digest(study/'preservation_freeze.json'),
              'old_execution_sha256': scene.digest(old/'execution.json'), 'files': inventory(out)}
    scene.save_json(out/'result.json', result)
    print(json.dumps({'paired_cases': len(cases), 'paired_passes': sum(c['paired_pass'] for c in cases), 'errors': errors}))


if __name__ == '__main__':
    main()
