"""Docker-only schema and normalization controls. No completion model is run."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys
import numpy as np


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(4*1024**2),b''):
            h.update(b)
    return h.hexdigest()


def original_fps(path):
    # Execute only this audited pure-NumPy function, inside Docker; no upstream module import.
    tree=ast.parse(path.read_text())
    fn=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='farthest_point_sample']
    if len(fn)!=1:
        raise ValueError('FPS source function count')
    scope={'np':np}
    exec(compile(ast.Module(body=fn,type_ignores=[]),str(path),'exec'),scope)
    return scope['farthest_point_sample']


def validate_array(points, expected):
    if points.shape!=(expected,3):
        raise ValueError(f'shape {points.shape}; expected {(expected,3)}')
    if not np.isfinite(points).all():
        raise ValueError('nonfinite coordinates')
    if len(np.unique(points,axis=0))<2:
        raise ValueError('degenerate coordinates')


def normalize_controls(points, tol64, tol32):
    c=points.mean(axis=0)
    radius=float(np.linalg.norm(points-c,axis=1).max())
    if radius<=0 or not np.isfinite(radius):
        raise ValueError('invalid radius')
    z=(points-c)/radius
    inverse64=z*radius+c
    # Upstream network input/output precision is float32, restoration follows the same precision.
    z32=z.astype(np.float32)
    inverse32=z32*np.float32(radius)+c.astype(np.float32)
    online32=z32*np.float32(radius+radius/6)+c.astype(np.float32)
    analytic=points+(points-c)/6
    scale=max(radius,float(np.abs(points).max()),1.0)
    errs={'roundtrip_float64':float(np.abs(inverse64-points).max()/scale),
          'roundtrip_float32':float(np.abs(inverse32-points).max()/scale),
          'online_analytic_float32':float(np.abs(online32-analytic).max()/scale)}
    ok=(errs['roundtrip_float64']<=tol64 and errs['roundtrip_float32']<=tol32
        and errs['online_analytic_float32']<=tol32)
    return {'centroid':c.tolist(),'radius':radius,'error_scale':scale,
            'errors':errs,'controls_pass':ok,
            'supplied_centroid_norm':float(np.linalg.norm(c)),
            'supplied_radius_minus_one':radius-1,
            'online_mean_displacement':float(np.linalg.norm(online32-points,axis=1).mean())}


def nearest_summary(query, reference):
    distances=[]
    for start in range(0,len(query),64):
        delta=query[start:start+64,None,:]-reference[None,:,:]
        distances.extend(np.sqrt(np.sum(delta*delta,axis=2).min(axis=1)).tolist())
    return {'mean':float(np.mean(distances)), 'p95':float(np.quantile(distances,.95)),
            'max':float(np.max(distances)),
            'sentinels':{str(i):distances[i] for i in [0,len(query)//2,len(query)-1]}}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--inputs',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    base=Path(__file__).parent
    frozen=json.loads((base/'freeze.json').read_text())
    for name,expected in frozen['files'].items():
        if sha(base/name)!=expected:
            raise RuntimeError(f'freeze mismatch: {name}')
    protocol=json.loads((base/'protocol.json').read_text())
    manifest=json.loads((base/'inputs.json').read_text())
    if args.output.exists():
        raise RuntimeError('refuse existing output directory')
    args.output.mkdir(parents=True)
    results={'protocol_sha256':sha(base/'protocol.json'),'inputs_sha256':sha(base/'inputs.json'),
             'device':'cpu','numpy_version':np.__version__,'python_version':sys.version,
             'pairs':[],'model_loaded':False,'generated_output_verified':False,
             'physical_frame_verified':False,'camera_rays_verified':False}
    try:
        for entry in manifest['selected_files']:
            p=args.inputs/entry['path']
            if p.stat().st_size!=entry['bytes'] or sha(p)!=entry['sha256']:
                raise RuntimeError(f'input integrity failure: {entry["path"]}')
        fps=original_fps(base/'upstream/runner.py')
        for index,pair in enumerate(manifest['selected_pairs']):
            item={'index':index,'object':pair['object'],'partial_member':pair['partial_member'],
                  'gt_member':pair['gt_member'],'status':'pending'}
            results['pairs'].append(item)
            try:
                partial_path=Path(pair['partial_member']); gt_path=Path(pair['gt_member'])
                if partial_path.parts[1:3]!=gt_path.parts[1:3] or partial_path.stem[:-1]+'y'!=gt_path.stem:
                    raise ValueError('pair naming mismatch')
                partial=np.loadtxt(args.inputs/'subset'/partial_path,dtype=np.float64)
                gt=np.loadtxt(args.inputs/'subset'/gt_path,dtype=np.float64)
                validate_array(partial,protocol['partial_points'])
                validate_array(gt,protocol['gt_points'])
                item.update({'partial_shape':list(partial.shape),'gt_shape':list(gt.shape),
                             'partial_unique_points':len(np.unique(partial,axis=0)),
                             'gt_unique_points':len(np.unique(gt,axis=0)),
                             'byte_identical_pair':sha(args.inputs/'subset'/partial_path)==sha(args.inputs/'subset'/gt_path)})
                if item['byte_identical_pair']:
                    raise ValueError('identical partial and GT files')
                np.random.seed(protocol['seed']+index)
                sampled=fps(partial,protocol['partial_points'])
                c=normalize_controls(sampled,protocol['tolerance64'],protocol['tolerance32'])
                item.update(c)
                item['sampled_unique_points']=len(np.unique(sampled,axis=0))
                if item['sampled_unique_points']!=item['partial_unique_points']:
                    raise ValueError('FPS lost unique points at full input count')
                # GT uses the very same partial-derived transform; no fitting/registration to GT.
                center=np.asarray(c['centroid']); radius=c['radius']
                normalized_gt=(gt-center)/radius
                gt_error=float(np.abs(normalized_gt*radius+center-gt).max()/max(c['error_scale'],float(np.abs(gt).max())))
                item['gt_common_transform_roundtrip']=gt_error
                # No alignment/quality threshold; this cannot verify camera or physical units.
                item['supplied_frame_distances']={
                    'partial_to_gt':nearest_summary(partial,gt),
                    'gt_to_partial':nearest_summary(gt,partial),
                    'interpretation':'diagnostic_only_alignment_unverified'}
                np.savetxt(args.output/f'{index}_sampled.xyz',sampled,fmt='%.17g')
                item['status']='pass' if c['controls_pass'] and gt_error<=protocol['tolerance64'] else 'control_failure'
            except (ValueError,OSError) as error:
                item['status']='schema_failure';item['error']=str(error)
        if any(p['status']=='schema_failure' for p in results['pairs']):
            results['decision']='REFINE_INPUT_SCHEMA'
        elif any(p['status']!='pass' for p in results['pairs']):
            results['decision']='REFINE_COORDINATE_IMPLEMENTATION'
        else:
            results['decision']='INPUT_CONTROLS_VALID_PHYSICAL_FRAME_UNRESOLVED'
    except Exception as error:
        results['decision']='INVALID_INPUT_OR_SOURCE_INTEGRITY';results['error']=str(error)
    results['output_hashes']={p.name:sha(p) for p in sorted(args.output.glob('*.xyz'))}
    (args.output/'results.json').write_text(json.dumps(results,indent=2,allow_nan=False)+'\n')
    if sum(p.stat().st_size for p in args.output.iterdir() if p.is_file())>protocol['output_cap_mib']*1024**2:
        raise RuntimeError('output size cap exceeded')
    print(json.dumps({'decision':results['decision'],'pairs':len(results['pairs'])}))
    if results['decision']=='INVALID_INPUT_OR_SOURCE_INTEGRITY':
        raise SystemExit(2)


if __name__=='__main__':
    main()
