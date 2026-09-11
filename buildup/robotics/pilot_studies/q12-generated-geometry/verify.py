"""Independent standard-library verification, run inside the same Docker read-only."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
    return h.hexdigest()


def points(path):
    return [tuple(float(v) for v in line.split()) for line in path.read_text().splitlines() if line.strip() and not line.startswith('#')]


def valid(p,n):
    return len(p)==n and all(len(x)==3 and all(math.isfinite(v) for v in x) for x in p) and len(set(p))>=2


def f32(x):
    return struct.unpack('f',struct.pack('f',x))[0]


def main():
    p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,required=True);p.add_argument('--result',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); base=Path(__file__).parent
    if a.output.exists():raise RuntimeError('refuse overwrite')
    manifest=json.loads((base/'inputs.json').read_text()); protocol=json.loads((base/'protocol.json').read_text()); result=json.loads((a.result/'results.json').read_text())
    frozen=json.loads((base/'freeze.json').read_text())
    for name,h in frozen['files'].items():assert sha(base/name)==h,name
    assert result['protocol_sha256']==sha(base/'protocol.json')
    assert result['inputs_sha256']==sha(base/'inputs.json')
    for f in manifest['selected_files']:
        path=a.inputs/f['path'];assert path.stat().st_size==f['bytes'] and sha(path)==f['sha256']
    assert len(result['pairs'])==len(manifest['selected_pairs'])==4
    verified=[]
    for i,(pair,row) in enumerate(zip(manifest['selected_pairs'],result['pairs'])):
        assert row['index']==i
        for name in ['object','partial_member','gt_member']:assert pair[name]==row[name]
        partial=points(a.inputs/'subset'/pair['partial_member']);gt=points(a.inputs/'subset'/pair['gt_member'])
        shape_ok=valid(partial,protocol['partial_points']) and valid(gt,protocol['gt_points'])
        if not shape_ok:
            assert row['status']=='schema_failure'
            verified.append({'index':i,'schema_failure_confirmed':True});continue
        if row['status']=='schema_failure':
            # Sample loss/other schema failures require a distinct audit rather than silently accepting them.
            raise AssertionError('schema failure needs case-specific verification: '+str(row.get('error')))
        sampled_path=a.result/f'{i}_sampled.xyz';assert sha(sampled_path)==result['output_hashes'][sampled_path.name]
        sample=points(sampled_path)
        assert len(sample)==protocol['partial_points'] and set(sample)==set(partial)
        center=[math.fsum(v[j] for v in sample)/len(sample) for j in range(3)]
        radius=max(math.dist(v,center) for v in sample)
        scale=max(radius,max(abs(x) for v in sample for x in v),1.)
        assert max(abs(x-y) for x,y in zip(center,row['centroid']))<=1e-12*scale
        assert abs(radius-row['radius'])<=1e-12*scale
        err64=0.;err32=0.;online_error=0.
        for v in sample:
            for j in range(3):
                z=(v[j]-center[j])/radius
                exact=z*radius+center[j]
                restored=f32(f32(f32(z)*f32(radius))+f32(center[j]))
                online=f32(f32(f32(z)*f32(radius+radius/6))+f32(center[j]))
                err64=max(err64,abs(exact-v[j])/scale)
                err32=max(err32,abs(restored-v[j])/scale)
                online_error=max(online_error,abs(online-(v[j]+(v[j]-center[j])/6))/scale)
        assert err64<=protocol['tolerance64'] and err32<=protocol['tolerance32'] and online_error<=protocol['tolerance32']
        assert row['status']=='pass'
        # Independent nearest-neighbor sentinel queries; statistics remain diagnostics, not gates.
        sentinels=[]
        for j in [0,len(partial)//2,len(partial)-1]:
            d=min(math.dist(partial[j],v) for v in gt)
            reported=row['supplied_frame_distances']['partial_to_gt']['sentinels'][str(j)]
            assert abs(d-reported)<=1e-12*scale
            sentinels.append({'query_index':j,'distance':d})
        verified.append({'index':i,'input_set_preserved':True,'controls_pass':True,'distance_sentinels':sentinels})
    expected='REFINE_INPUT_SCHEMA' if any(row['status']=='schema_failure' for row in result['pairs']) else 'INPUT_CONTROLS_VALID_PHYSICAL_FRAME_UNRESOLVED'
    assert result['decision']==expected
    assert not any(result[k] for k in ['model_loaded','generated_output_verified','physical_frame_verified','camera_rays_verified'])
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps({'status':'VERIFIED','decision':expected,'result_sha256':sha(a.result/'results.json'),'pairs':verified},indent=2)+'\n')
    print('VERIFIED',expected)

if __name__=='__main__':main()
