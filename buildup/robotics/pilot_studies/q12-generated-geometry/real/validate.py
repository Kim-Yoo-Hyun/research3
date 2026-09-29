"""Host-allowed byte/manifest/source-syntax validation; no numerical method imports."""
import ast
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import zlib


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def main():
    study=Path(__file__).resolve().parent;root=study.parents[4]
    old=['freeze.json','model/schema_freeze.json','model/completion_freeze.json',
         'geometry/freeze.json','geometry/preservation_freeze.json','geometry/inspection_freeze.json']
    freezes={}
    for p in [study.parent/n for n in old]+[study/'preparation_freeze.json']+([study/'freeze.json'] if (study/'freeze.json').exists() else []):
        frozen=load(p)
        for name,h in frozen['files'].items():assert sha(p.parent/name)==h, ('freeze changed',str(p),name)
        freezes[str(p.relative_to(study.parent))]={'sha256':sha(p),'entries':len(frozen['files'])}
    for path in study.glob('*.py'):ast.parse(path.read_text(),filename=str(path))
    for path in study.glob('*.json'):load(path)
    for path in study.glob('*.sh'):subprocess.run(['bash','-n',str(path)],check=True)
    assets,selection=load(study/'assets.json'),load(study/'selection.json')
    data=root/'datasets/q12/bop_v1';state=load(data/'download_state.json')
    assert sha(data/'download_state.json')==assets['download_state_sha256']
    assert state['selection_sha256']==assets['selection_sha256']==sha(study/'selection.json')
    assert assets['preparation_freeze_sha256']==sha(study/'preparation_freeze.json')
    assert len(selection['cases'])==10 and selection['frames']==[1,36] and selection['objects']==[1,6,14,19,20]
    assert len(selection['members'])==len(assets['files'])==37
    for request in state['requests']:
        assert request['completed'] and request['http_status']==206
        p=data/'transfers'/f'{request["archive"]}.{request["start"]}.{request["count"]}.bin'
        assert p.stat().st_size==request['count'] and sha(p)==request['sha256']
        size=selection['archives'][request['archive']]['bytes']
        assert request['content_range']==f'bytes {request["start"]}-{request["start"]+request["count"]-1}/{size}'
    for expected,record in zip(selection['members'],assets['files']):
        assert all(record[k]==v for k,v in expected.items())
        raw=(data/record['destination']).read_bytes()
        assert len(raw)==record['bytes'] and hashlib.sha256(raw).hexdigest()==record['sha256']
        assert zlib.crc32(raw)==record['crc32'] and record['crc_verified']
        header=(data/'transfers'/f'{record["archive"]}.{record["local_header_offset"]}.30.bin').read_bytes()
        fields=struct.unpack('<4s5H3I2H',header);namesize,extrasize=fields[-2:]
        count=namesize+extrasize+record['compressed_bytes']
        tail=(data/'transfers'/f'{record["archive"]}.{record["local_header_offset"]+30}.{count}.bin').read_bytes()
        assert tail[:namesize].decode()==record['member']
        assert hashlib.sha256(tail[namesize+extrasize:]).hexdigest()==record['compressed_sha256']
        if 'png_header' in record:
            assert list(record['png_header'].values())==list(struct.unpack('>IIBBBBB',raw[16:29]))
    network=sum(r['count'] for r in state['requests']);unpacked=sum(r['bytes'] for r in assets['files'])
    assert network==state['response_body_bytes']==assets['charged_response_body_bytes']<=selection['limits']['body_bytes']
    assert unpacked==assets['unpacked_bytes']<=selection['limits']['unpacked_bytes']
    preflight=load(study/'preflight.json')
    assert preflight['status']=='PASS' and preflight['synthetic_only'] and not preflight['real_data_mounted']
    assert preflight['independent_verifier_process'] and len(preflight['checks'])==9
    for name,h in preflight['tested_source_sha256'].items():assert sha(study/name)==h, ('untested source',name)
    assert all(c['passed'] for c in preflight['checks']) and preflight['positive_verification']['denominator']==10
    assert preflight['image_id']==(study/'image_id.txt').read_text().strip()
    image_bytes=int((study/'image_bytes.txt').read_text());assert image_bytes<=4294967296
    print(json.dumps({'status':'PASS','freezes':freezes,'members':37,'range_responses':len(state['requests']),
        'response_bytes':network,'unpacked_bytes':unpacked,'synthetic_groups':9,'image_bytes':image_bytes,
        'real_images_decoded_by_this_check':False,'real_mesh_coordinates_inspected_by_this_check':False,
        'byte_validation_only':True},indent=2))


if __name__=='__main__':main()
