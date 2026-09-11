"""Bounded public download, archive indexing and raw-file extraction; no method execution."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import time
import urllib.request
import zipfile

ROOT = Path('/home/yoohyun/research3/datasets/q12')
ASSETS = [
    ('3dsgrasp_ycb_train_test_split.zip', '1rnJP3Q2zvcj5uImxRu8yYwgk0O7md8dJ', 1836233634),
    ('3dsgrasp_model.pth', '11vTsY0MQw9pzsqz3MyvCKjQT2rQ9VxVi', 505668417),
]
NETWORK_CAP = 4 * 1024**3
STORAGE_CAP = 6 * 1024**3
START = time.monotonic()
received = 0

def guard():
    if time.monotonic() - START > 1800:
        raise RuntimeError('30-minute acquisition cap reached')
    if received > NETWORK_CAP:
        raise RuntimeError('4-GiB network body cap reached')
    if sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file()) > STORAGE_CAP:
        raise RuntimeError('6-GiB storage cap reached')

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024**2), b''):
            h.update(block)
    return h.hexdigest()

def fetch(name, fid, size):
    global received
    target = ROOT / name
    url = f'https://drive.usercontent.google.com/download?id={fid}&export=download&confirm=t'
    if target.exists():
        if target.stat().st_size != size:
            raise RuntimeError(f'existing completed file has wrong size: {target}')
    else:
        part = target.with_suffix(target.suffix + '.part')
        for attempt in range(3):
            guard()
            offset = part.stat().st_size if part.exists() else 0
            if offset == size:
                break
            if offset > size:
                raise RuntimeError('resume offset exceeds expected size')
            request = urllib.request.Request(url, headers={
                'Range': f'bytes={offset}-{size-1}', 'User-Agent': 'research3-q12-acquisition/1.0'})
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    expected = f'bytes {offset}-{size-1}/{size}'
                    if response.status != 206 or response.headers.get('Content-Range') != expected:
                        raise RuntimeError('server did not honor exact bounded range')
                    with part.open('ab') as out:
                        while offset < size:
                            guard()
                            data = response.read(min(4 * 1024**2, size-offset, NETWORK_CAP-received+1))
                            if not data:
                                raise OSError('truncated body')
                            received += len(data)
                            out.write(data)
                            offset += len(data)
                print(json.dumps({'asset':name,'status':'downloaded','bytes':offset}), flush=True)
                break
            except (OSError, TimeoutError) as error:
                print(json.dumps({'asset':name,'attempt':attempt+1,'error':str(error)}), flush=True)
        if not part.exists() or part.stat().st_size != size:
            raise RuntimeError(f'incomplete download: {name}')
        part.rename(target)
    return {'name':name, 'url':url, 'bytes':size, 'sha256':digest(target),
            'publisher_checksum_available':False}

def copy_member(archive, member, target):
    if target.exists():
        raise RuntimeError(f'refuse overwrite: {target}')
    if member.file_size > STORAGE_CAP:
        raise RuntimeError('member exceeds storage cap')
    target.parent.mkdir(parents=True, exist_ok=True)
    with archive.open(member) as src, target.open('xb') as out:
        while True:
            guard()
            chunk = src.read(4 * 1024**2)
            if not chunk:
                break
            out.write(chunk)
    if target.stat().st_size != member.file_size:
        raise RuntimeError('extracted size mismatch')
    return {'member':member.filename, 'path':str(target.relative_to(ROOT)),
            'bytes':member.file_size, 'zip_crc32':f'{member.CRC:08x}',
            'crc_verified_on_read':True, 'sha256':digest(target)}

def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(ROOT).free < 10 * 1024**3:
        raise RuntimeError('less than 10 GiB free')
    if sum(x[2] for x in ASSETS) > 3 * 1024**3:
        raise RuntimeError('3-GiB payload cap')
    receipt = {'status':'running', 'date':'2026-09-10', 'root':str(ROOT),
               'selection_rule':'lexicographically first two test objects, first two paired partials per object; basename final x -> y',
               'caps':{'network_bytes':NETWORK_CAP,'storage_bytes':STORAGE_CAP,'wall_seconds':1800},
               'assets':[], 'inner_archives':[]}
    def save():
        receipt['network_body_bytes_this_invocation'] = received
        receipt['elapsed_seconds'] = round(time.monotonic()-START, 3)
        (ROOT/'acquisition.json').write_text(json.dumps(receipt,indent=2)+'\n')
    try:
        for item in ASSETS:
            receipt['assets'].append(fetch(*item)); save()
        with zipfile.ZipFile(ROOT/ASSETS[0][0]) as outer:
            if set(outer.namelist()) != {'input.zip','gt.zip'}:
                raise RuntimeError('unexpected outer layout')
            for name in ['input.zip','gt.zip']:
                receipt['inner_archives'].append(copy_member(outer,outer.getinfo(name),ROOT/'archives'/name))
                save()
        with zipfile.ZipFile(ROOT/'archives/input.zip') as inp, zipfile.ZipFile(ROOT/'archives/gt.zip') as gt:
            for archive,name in [(inp,'input'),(gt,'gt')]:
                inventory = [{'name':i.filename,'bytes':i.file_size,'compressed_bytes':i.compress_size,
                              'crc32':f'{i.CRC:08x}'} for i in archive.infolist()]
                (ROOT/f'{name}-index.json').write_text(json.dumps(inventory,indent=2)+'\n')
                receipt[f'{name}_member_count'] = len(inventory)
                receipt[f'{name}_total_uncompressed_bytes'] = sum(i.file_size for i in archive.infolist())
            gt_names = set(gt.namelist()); candidates = {}; unpaired=[]
            for name in sorted(inp.namelist()):
                match = re.fullmatch(r'input/([^/]+)/test/([^/]+)x\.xyz', name)
                if not match:
                    continue
                obj,stem = match.groups(); paired=f'gt/{obj}/test/{stem}y.xyz'
                if paired in gt_names:
                    candidates.setdefault(obj,[]).append((name,paired))
                else:
                    unpaired.append(name)
            eligible=sorted(k for k,v in candidates.items() if len(v)>=2)
            receipt['eligible_objects'] = eligible
            receipt['unpaired_test_partial_count'] = len(unpaired)
            if len(eligible)<2:
                raise RuntimeError('fewer than two eligible paired test objects')
            selected = [(obj,*pair) for obj in eligible[:2] for pair in candidates[obj][:2]]
            # Selection is persisted before inspecting/extracting any XYZ content.
            receipt['selected_pairs']=[{'object':o,'partial_member':p,'gt_member':g} for o,p,g in selected]
            save()
            receipt['selected_files']=[]
            for obj,p,g in selected:
                for archive,name in [(inp,p),(gt,g)]:
                    target=ROOT/'subset'/name
                    receipt['selected_files'].append(copy_member(archive,archive.getinfo(name),target))
            receipt['status']='completed'
            receipt['arrays_evaluated']=False
            receipt['model_loaded']=False
            receipt['metric_frame_verified']=False
            save()
        print(json.dumps({'status':receipt['status'],'selected_pairs':receipt['selected_pairs'],
                          'network_body_bytes':received,'elapsed_seconds':receipt['elapsed_seconds']}),flush=True)
    except Exception as error:
        receipt['status']='failed'; receipt['error']=str(error); save(); raise

if __name__ == '__main__':
    main()
