"""Synthetic implementation controls, without any YCB asset or model mounted."""
import argparse
import copy
import json
import gzip
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import numpy as np
import pybullet as pb

from scene import camera, digest, mesh_body, physics_labels, prepare_mesh, render, run_case, save_json
from verify import geometry_label, inside_by_rays, triangle_box_intersects, verify_case


def cube():
    v = np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]], dtype=float)
    f = np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]])
    return v, f


def must_reject(call):
    try:
        call()
    except (AssertionError, ValueError, IndexError):
        return
    raise AssertionError('tampering was not rejected')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    cfg = json.loads(Path('/study/protocol.json').read_text())
    client = pb.connect(pb.DIRECT)
    controls = {}
    try:
        v, f = cube()
        v, f, info = prepare_mesh(v, f, cfg['asset_scale'])
        assert info['closed_oriented_edges'] and info['inverse_max_error'] < 1e-12
        _, _, bad = prepare_mesh(v, f[:-1], cfg['asset_scale'])
        assert not bad['closed_oriented_edges']
        controls['closed_mesh_and_missing_face_rejection'] = 'PASS'
        body = mesh_body(v, f)
        tri = v[f]
        rows = []
        for offset in ([.1,0,0], [.055,0,0], [0,0,0]):
            rows.append({'id': len(rows), 'rotation': np.eye(3).tolist(),
                         'boxes': [{'center': (np.array([0,0,.1])+offset).tolist(), 'half': [.01,.01,.01]}]})
        actual = physics_labels(body, tri, rows, cfg['tolerances']['near_contact_m'])
        assert [r['collision'] for r in actual] == [False, True, True]
        assert [geometry_label(tri, row) for row in rows] == [False, True, True]
        assert inside_by_rays(np.array([0,0,.1]), tri)
        # A box entirely inside a solid has no intersecting surface triangles: retain containment.
        assert not triangle_box_intersects(tri-[0,0,.1], np.array([.01,.01,.01]))
        assert actual[2]['boxes'][0]['center_inside']
        controls['analytic_clear_surface_and_containment'] = 'PASS'
        pb.resetSimulation()
        shape = pb.createCollisionShape(pb.GEOM_BOX, halfExtents=[.2,.2,.001])
        vis = pb.createVisualShape(pb.GEOM_BOX, halfExtents=[.2,.2,.001])
        plane = pb.createMultiBody(baseMass=0, baseCollisionShapeIndex=shape, baseVisualShapeIndex=vis, basePosition=[0,0,.079])
        cc = copy.deepcopy(cfg['camera'])
        cc.update(eyes_m=[[0,0,.3]], target_m=[0,0,0], up=[0,1,0])
        obs = render(plane, camera(cc, 0))
        central = obs['depth'][96:160, 96:160]
        assert obs['repeat_equal'] and np.max(np.abs(central-.22)) < 1e-6
        controls['analytic_plane_depth_and_repeat'] = 'PASS'
        case_controls = []
        with tempfile.TemporaryDirectory() as temp:
            for view in range(2):
                path = Path(temp)/str(view)
                run_case(v, f, cfg, view, path, cfg['sampling']['area_uniform_seed']+view)
                result = verify_case(path, cfg)
                assert not result['collision_mismatch_ids']
                case_controls.append({k: result[k] for k in ('verified_camera','max_ray_depth_error_m','ray_sentinels','candidate_count','collision_mismatch_ids')})
            path = Path(temp)/'0'
            npz = path/'observation.npz'
            original = npz.read_bytes()
            with np.load(npz, allow_pickle=False) as data:
                changed = dict(data)
            changed['normalized'] = changed['normalized'].copy()
            changed['normalized'][0,0] += .01
            np.savez_compressed(npz, **changed)
            must_reject(lambda: verify_case(path, cfg))
            npz.write_bytes(original)
            rows = json.loads((path/'candidates.json').read_text())
            rows[0]['center'][0] += .01
            save_json(path/'candidates.json', rows)
            result = json.loads((path/'result.json').read_text())
            result['candidate_sha256'] = digest(path/'candidates.json')
            save_json(path/'result.json', result)
            must_reject(lambda: verify_case(path, cfg))
        controls['two_view_synthetic_pipeline_and_independent_geometry'] = case_controls
        controls['normalized_point_and_rehashed_candidate_tamper_rejection'] = 'PASS'
        # Exercise the real entry points with synthetic assets and a separate synthetic freeze.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            study, assets = root/'study', root/'assets'
            study.mkdir()
            assets.mkdir()
            for source in Path('/study').glob('*.py'):
                shutil.copy2(source, study/source.name)
            spec = copy.deepcopy(cfg)
            spec['objects'] = ['synthetic_a', 'synthetic_b']
            save_json(study/'protocol.json', spec)
            manifest = []
            for i, name in enumerate(spec['objects']):
                verts, faces = cube()
                verts[:, 1] *= (1.0 if i == 0 else .8)
                obj = ''.join('v '+' '.join(map(str,row))+'\n' for row in verts)
                obj += ''.join('f '+' '.join(str(int(x)+1) for x in row)+'\n' for row in faces)
                mesh, archive = assets/(name+'.obj'), assets/(name+'.gz')
                mesh.write_text(obj)
                archive.write_bytes(gzip.compress(obj.encode(), mtime=0))
                manifest.append({'id': name,'mesh_path':mesh.name,'mesh_bytes':mesh.stat().st_size,'mesh_sha256':digest(mesh),
                                 'archive_path':archive.name,'bytes':archive.stat().st_size,'archive_sha256':digest(archive)})
            save_json(study/'assets.json', {'objects':manifest})
            save_json(study/'freeze.json', {'files':{p.name:digest(p) for p in sorted(study.iterdir()) if p.is_file()}})
            audit_command = [sys.executable, str(study/'audit.py'), '--study', str(study), '--assets', str(assets), '--output', str(root/'data')]
            subprocess.run(audit_command, check=True, capture_output=True, text=True)
            verifier_command = [sys.executable, str(study/'verify.py'), '--study', str(study), '--assets', str(assets), '--input', str(root/'data'), '--output', str(root/'audit')]
            subprocess.run(verifier_command, check=True, capture_output=True, text=True)
            result = json.loads((root/'audit/verification.json').read_text())
            assert len(result['cases']) == 4 and not result['errors'], result
            assert all(not c['collision_mismatch_ids'] for c in result['cases'])
            controls['synthetic_four_case_entrypoints_and_independent_verifier'] = {
                'cases':4,'errors':0,'decision':result['decision'],
                'case_support':[{'id':c['id'],'collision':c['robust_collision'],'clear':c['robust_clear'],
                                 'near_contact':c['near_contact_count'],'oracle_mismatches':c['oracle_mismatches']} for c in result['cases']]}
            assert subprocess.run(audit_command, capture_output=True).returncode != 0
            # Runtime must reject a source mutation even when the output root is fresh.
            (study/'scene.py').write_text((study/'scene.py').read_text()+'\n# tamper\n')
            changed_command = audit_command[:-1]+[str(root/'second_data')]
            assert subprocess.run(changed_command, capture_output=True).returncode != 0
            controls['output_overwrite_and_frozen_source_rejection'] = 'PASS'
    finally:
        pb.disconnect(client)
    out = {'status': 'PASS', 'controls': controls, 'actual_ycb_assets_mounted': False,
           'checkpoint_or_completion_mounted': False, 'claim': 'implementation controls only; no actual readiness outcome'}
    save_json(args.output, out)
    print(json.dumps(out), flush=True)


if __name__ == '__main__':
    main()
