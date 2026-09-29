"""Execute frozen four-case geometry readiness; no checkpoint or completion input."""
import argparse
import json
from pathlib import Path
import numpy as np
import pybullet as pb
from scene import digest, prepare_mesh, read_obj, run_case, save_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--study', default='/study')
    parser.add_argument('--assets', default='/assets')
    args = parser.parse_args()
    study, assets, out = Path(args.study), Path(args.assets), Path(args.output)
    assert not out.exists()
    protocol = json.loads((study/'protocol.json').read_text())
    frozen = json.loads((study/'freeze.json').read_text())
    for name, expected in frozen['files'].items():
        assert digest(study/name) == expected, ('frozen file', name)
    manifest = json.loads((study/'assets.json').read_text())
    assert [r['id'] for r in manifest['objects']] == protocol['objects']
    for row in manifest['objects']:
        mesh = assets/Path(row['mesh_path']).name
        archive = assets/Path(row['archive_path']).name
        assert mesh.stat().st_size == row['mesh_bytes'] and digest(mesh) == row['mesh_sha256']
        assert archive.stat().st_size == row['bytes'] and digest(archive) == row['archive_sha256']
    out.mkdir(parents=True)
    client = pb.connect(pb.DIRECT)
    assert client >= 0
    cases = []
    try:
        for oi, row in enumerate(manifest['objects']):
            mesh_error = None
            info = None
            try:
                v, f = read_obj(assets/Path(row['mesh_path']).name)
                world, f, info = prepare_mesh(v, f, protocol['asset_scale'])
                assert info['closed_oriented_edges'], 'mesh solid topology unresolved'
                assert info['minimum_triangle_area_m2'] >= protocol['tolerances']['mesh_area_min_m2'], 'degenerate mesh triangle'
                assert info['inverse_max_error'] <= protocol['tolerances']['numeric_roundtrip_m']
            except Exception as e:
                mesh_error = f'{type(e).__name__}: {e}'
            save_json(out/(row['id']+'_mesh.json'), {'object': row['id'], 'geometry': info, 'error': mesh_error})
            for vi in range(len(protocol['camera']['eyes_m'])):
                case_id = f"{row['id']}_v{vi}"
                record = {'id': case_id, 'object': row['id'], 'view_index': vi}
                if mesh_error:
                    record['error'] = mesh_error
                else:
                    try:
                        run_case(world, f, protocol, vi, out/case_id, protocol['sampling']['area_uniform_seed']+oi*2+vi)
                        save_json(out/case_id/'mesh.json', info)
                    except Exception as e:
                        record['error'] = f'{type(e).__name__}: {e}'
                cases.append(record)
                print(json.dumps(record), flush=True)
    finally:
        pb.disconnect(client)
    save_json(out/'result.json', {'id': protocol['id'], 'denominator': 4, 'cases': cases,
                                'freeze_sha256': digest(study/'freeze.json'),
                                'completion_or_checkpoint_mounted': False})


if __name__ == '__main__':
    main()
