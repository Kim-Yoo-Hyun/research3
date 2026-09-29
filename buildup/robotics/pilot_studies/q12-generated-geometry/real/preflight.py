"""Synthetic contract checks only; execute in Docker without real dataset mounts."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import zlib

import numpy as np


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def read(path):
    return json.loads(Path(path).read_text())


def fixture(root, cfg, selection):
    from PIL import Image
    from plyfile import PlyData, PlyElement
    model = root/'models'; model.mkdir(parents=True)
    scene = root/f'test/{selection["scene"]:06d}'
    for kind in ('rgb', 'depth', 'mask', 'mask_visib'): (scene/kind).mkdir(parents=True)
    v = np.array([[-30,-40,-50],[30,-40,-50],[30,40,-50],[-30,40,-50],
                  [-30,-40,50],[30,-40,50],[30,40,50],[-30,40,50]], dtype=float)+[5,-3,2]
    f = np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],
                  [3,7,6],[3,6,2],[0,4,7],[0,7,3],[1,2,6],[1,6,5]])
    vertices = np.array([tuple(p) for p in v], dtype=[(k,'f4') for k in 'xyz'])
    faces = np.empty(len(f), dtype=[('vertex_indices','i4',(3,))]); faces['vertex_indices'] = f
    metadata = {**{'min_'+k:float(v[:,i].min()) for i,k in enumerate('xyz')},
                **{'size_'+k:float(np.ptp(v[:,i])) for i,k in enumerate('xyz')}}
    for i,obj in enumerate(selection['objects']):
        PlyData([PlyElement.describe(vertices,'vertex'),PlyElement.describe(faces,'face')],
                text=i%3==0, byte_order='<' if i%3==1 else '>').write(model/f'obj_{obj:06d}.ply')
    write(model/'models_info.json', {str(o):metadata for o in selection['objects']})
    cfg['image']['width'], cfg['image']['height'] = 160,96
    h,w=96,160; yy,xx=np.indices((h,w)); K=np.array([[120.,0,79.],[0,120.,47.],[0,0,1.]])
    directions=np.stack(((xx-79)/120,(yy-47)/120,np.ones_like(xx)),axis=-1)
    camera,gt,infos={},{},{}
    for fi,frame in enumerate(selection['frames']):
        scale=.5 if fi==0 else 2.
        camera[str(frame)]={'cam_K':K.ravel().tolist(),'depth_scale':scale,
                            'cam_R_w2c':[0.,-1.,0.,1.,0.,0.,0.,0.,1.],'cam_t_w2c':[30.,-10.,15.]}
        gt[str(frame)],infos[str(frame)]=[],[]
        raw=np.zeros((h,w),dtype=np.uint16)
        for gi,obj in enumerate(selection['objects']):
            R=np.eye(3) if fi==0 else np.array([[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]])
            t=np.array([(gi-2)*130.,fi*20.,800.])
            transformed=(v@R.T+t)/1000; lo,hi=transformed.min(0),transformed.max(0)
            # Analytic axis-aligned box slab intersection, no triangle implementation.
            near=np.full((h,w),-np.inf);far=np.full((h,w),np.inf)
            for k in range(3):
                nonzero=directions[:,:,k]!=0
                a=np.divide(lo[k],directions[:,:,k],out=np.full((h,w),-np.inf),where=nonzero)
                b=np.divide(hi[k],directions[:,:,k],out=np.full((h,w),np.inf),where=nonzero)
                near=np.maximum(near,np.minimum(a,b));far=np.minimum(far,np.maximum(a,b))
                if not lo[k]<=0<=hi[k]: far[~nonzero]=-np.inf
            visible=(far>=near)&(near>0)
            assert visible.sum()>32 and not np.any(visible & (raw>0))
            raw[visible]=np.rint(near[visible]*1000/scale).astype(np.uint16)
            missing=tuple(np.argwhere(visible)[0]);raw[missing]=0
            for kind in ('mask','mask_visib'):
                Image.fromarray(visible.astype(np.uint8)*255).save(scene/kind/f'{frame:06d}_{gi:06d}.png')
            gt[str(frame)].append({'obj_id':obj,'cam_R_m2c':R.ravel().tolist(),'cam_t_m2c':t.tolist()})
            infos[str(frame)].append({'px_count_visib':int(visible.sum())})
        rgb=np.stack((xx%256,yy%256,(xx+yy)%256),axis=-1).astype(np.uint8)
        Image.fromarray(rgb).save(scene/'rgb'/f'{frame:06d}.png')
        Image.fromarray(raw).save(scene/'depth'/f'{frame:06d}.png')
    for name,value in [('scene_camera.json',camera),('scene_gt.json',gt),('scene_gt_info.json',infos)]: write(scene/name,value)


def png_controls(root):
    from PIL import Image
    from verify import png
    checks=[]
    for bits,color in [(8,2),(16,0)]:
        h,w=10,13;channels=3 if color==2 else 1;bpp=channels*bits//8
        values=(np.arange(h*w*channels).reshape((h,w,channels))*137)%(65536 if bits==16 else 256)
        rows=values.astype('>u2' if bits==16 else 'u1').tobytes();stride=w*bpp;encoded=bytearray()
        for y in range(h):
            current=rows[y*stride:(y+1)*stride];prev=rows[(y-1)*stride:y*stride] if y else bytes(stride)
            filt=y%5;encoded.append(filt)
            for x,v in enumerate(current):
                a=current[x-bpp] if x>=bpp else 0;b=prev[x];c=prev[x-bpp] if x>=bpp else 0
                candidates=(a,b,c);p=a+b-c
                predictor=[0,a,b,(a+b)//2,min(candidates,key=lambda n:abs(p-n))][filt]
                encoded.append((v-predictor)%256)
        def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data))
        payload=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,bits,color,0,0,0))+chunk(b'IDAT',zlib.compress(encoded))+chunk(b'IEND',b'')
        path=root/f'filters_{bits}_{color}.png';path.write_bytes(payload)
        decoded,_=png(path)
        with Image.open(path) as im:assert np.array_equal(decoded,np.asarray(im))
        assert np.array_equal(decoded,values[:,:,0] if channels==1 else values)
        damaged=bytearray(payload);damaged[-1]^=1;path.write_bytes(damaged)
        try:png(path)
        except AssertionError:pass
        else:raise AssertionError('CRC corruption accepted')
        checks.append({'bits':bits,'color':color,'filters':[0,1,2,3,4],'CRC_corruption_rejected':True})
    return checks


def worker(phase, root):
    cfg,selection=read(root/'protocol.json'),read(root/'selection.json')
    if phase=='produce':
        from audit import run
        run(root/'input',root/'output',cfg,selection)
    else:
        from verify import verify
        assert all(name not in sys.modules for name in ('audit','PIL','plyfile')), 'verifier process dependency isolation'
        write(root/'verification.json',verify(root/'input',root/'output',cfg,selection))


def main(root):
    from plyfile import PlyData, PlyElement
    root.mkdir(parents=True,exist_ok=True);assert not any(root.iterdir())
    study=Path(__file__).resolve().parent
    cfg=read(study/'protocol.json');selection=read(study/'selection.json')
    good=root/'positive';good.mkdir()
    fixture(good/'input',cfg,selection)
    write(good/'protocol.json',cfg);write(good/'selection.json',selection)
    def execute(p,phase,expected_success=True):
        done=subprocess.run([sys.executable,'-B',__file__,'--phase',phase,'--root',str(p)],capture_output=True,text=True)
        (p/f'{phase}.log').write_text(done.stdout+done.stderr)
        assert (done.returncode==0)==expected_success, (p.name,phase,done.stdout,done.stderr)
    execute(good,'produce');execute(good,'verify')
    result=read(good/'output/result.json');assert result['decision']==cfg['decisions']['numerical_pass']
    assert all(c['visible_missing_depth_pixels']==1 for c in result['cases'])
    checks=[{'name':'positive_10_cases_three_PLY_encodings_two_scales_nonidentity_pose_missing_depth','passed':True}]
    checks.append({'name':'PNG_filters_and_CRC','passed':True,'details':png_controls(root)})
    for label in ('open_mesh','reflected_pose','shifted_pose_no_rays','half_pixel_output','residual_output','case_identity_output','invented_input_failure'):
        dest=root/label;shutil.copytree(good,dest)
        if label in ('open_mesh','reflected_pose','shifted_pose_no_rays'):
            shutil.rmtree(dest/'output')
            if label=='open_mesh':
                p=dest/'input/models/obj_000001.ply';data=PlyData.read(p)
                PlyData([data['vertex'],PlyElement.describe(data['face'].data[:-1],'face')],text=True).write(p)
            else:
                p=dest/'input/test/000048/scene_gt.json';data=read(p)
                if label=='reflected_pose':data['1'][0]['cam_R_m2c']=[-1.,0.,0.,0.,1.,0.,0.,0.,1.]
                else:data['1'][0]['cam_t_m2c'][0]+=2000.
                write(p,data)
            execute(dest,'produce');execute(dest,'verify')
            outcome=read(dest/'output/result.json')
            assert len(outcome['cases'])==10
            key={'open_mesh':'mesh','reflected_pose':'schema_or_coordinate','shifted_pose_no_rays':'missing_ray_support'}[label]
            assert outcome['decision']==cfg['decisions'][key]
        else:
            p=dest/'output/result.json';data=read(p)
            if label=='half_pixel_output':
                p2=dest/'output'/f'{data["cases"][0]["id"]}.npz'
                with np.load(p2,allow_pickle=False) as a:payload={k:a[k].copy() for k in a.files}
                payload['camera_points_m'][:,0]+=.5*payload['camera_points_m'][:,2]/payload['K'][0,0]
                np.savez_compressed(p2,**payload)
            elif label=='residual_output':data['cases'][0]['residual_m'][0]+=.001
            elif label=='case_identity_output':data['cases'][0]['gt_index']=1
            else:
                data['cases'][0]['input_error']='fabricated failure';data['decision']=cfg['decisions']['schema_or_coordinate']
            write(p,data);execute(dest,'verify',expected_success=False)
        checks.append({'name':label,'passed':True})
    source_names=['audit.py','verify.py','preflight.py','check.sh']
    receipt={'status':'PASS','synthetic_only':True,'real_data_mounted':False,'independent_verifier_process':True,'checks':checks,
             'positive_verification':read(good/'verification.json'),
             'tested_source_sha256':{n:hashlib.sha256((study/n).read_bytes()).hexdigest() for n in source_names},
             'image_id':(study/'image_id.txt').read_text().strip()}
    write(root/'preflight.json',receipt)
    print(json.dumps({'status':'PASS','groups':len(checks),'positive_cases':10}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',required=True);parser.add_argument('--phase',choices=['produce','verify'])
    args=parser.parse_args()
    if args.phase:worker(args.phase,Path(args.root))
    else:main(Path(args.root))
