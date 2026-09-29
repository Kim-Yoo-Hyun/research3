"""Bounded resumable selective download/checksum only; never decodes mesh/image arrays."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import struct
import time
import urllib.request
import zlib

STUDY = Path(__file__).resolve().parent
ROOT = Path('/home/yoohyun/research3/datasets/q12/bop_v1')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n')


def main():
    spec = json.loads((STUDY/'selection.json').read_text())
    freeze = json.loads((STUDY/'preparation_freeze.json').read_text())
    for name, h in freeze['files'].items():
        assert sha((STUDY/name).read_bytes()) == h
    assert not (STUDY/'assets.json').exists(), 'refuse existing asset receipt'
    ROOT.mkdir(parents=True, exist_ok=True)
    transfers = ROOT/'transfers'; transfers.mkdir(exist_ok=True)
    progress = ROOT/'download_state.json'
    state = json.loads(progress.read_text()) if progress.exists() else {'selection_sha256': sha((STUDY/'selection.json').read_bytes()), 'response_body_bytes': 0, 'requests': []}
    assert state['selection_sha256'] == sha((STUDY/'selection.json').read_bytes())
    deadline = time.monotonic()+spec['limits']['seconds']

    def fetch(archive, start, count):
        assert count > 0 and time.monotonic() < deadline
        info = spec['archives'][archive]
        end = start+count-1
        url = info['url']+f'?download=true&q12_input_range={start}-{end}'
        cache = transfers/f'{archive}.{start}.{count}.bin'
        key = f'{archive}:{start}:{count}'
        old = next((x for x in state['requests'] if x['key'] == key and x.get('completed')), None)
        if old and cache.exists():
            b = cache.read_bytes(); assert len(b) == count and sha(b) == old['sha256']; return b
        assert state['response_body_bytes']+count <= spec['limits']['body_bytes']
        # Reserve the request budget before I/O; interrupted requests remain charged on resume.
        state['response_body_bytes'] += count
        entry = {'key': key, 'archive': archive, 'start': start, 'count': count, 'completed': False}
        state['requests'].append(entry); save(progress, state)
        req = urllib.request.Request(url, headers={'Range': f'bytes={start}-{end}', 'Accept-Encoding': 'identity', 'User-Agent': 'research3-q12-bop-input'})
        with urllib.request.urlopen(req, timeout=30) as r:
            assert r.status == 206 and r.headers.get('Content-Range') == f'bytes {start}-{end}/{info["bytes"]}', 'range mismatch; no full fallback'
            b = r.read(count+1); assert len(b) == count
        cache.write_bytes(b)
        entry.update({'completed': True, 'http_status': 206, 'content_range': f'bytes {start}-{end}/{info["bytes"]}', 'sha256': sha(b)})
        save(progress, state)
        return b

    files = []
    assert sum(m['bytes'] for m in spec['members']) <= spec['limits']['unpacked_bytes']
    for item in spec['members']:
        relative = PurePosixPath(item['destination'])
        assert not relative.is_absolute() and '..' not in relative.parts
        header = fetch(item['archive'], item['local_header_offset'], 30)
        fields = struct.unpack('<4s5H3I2H', header)
        signature, version, flags, method, mt, md, crc, cs, us, name_len, extra_len = fields
        assert signature == b'PK\x03\x04' and not flags & 1 and method == item['method']
        tail = fetch(item['archive'], item['local_header_offset']+30, name_len+extra_len+item['compressed_bytes'])
        assert tail[:name_len].decode('utf8') == item['member']
        compressed = tail[name_len+extra_len:]
        assert method in (0, 8)
        if method == 8:
            dec = zlib.decompressobj(-15)
            value = dec.decompress(compressed, item['bytes']+1)
            assert dec.eof and not dec.unconsumed_tail and not dec.unused_data
        else:
            value = compressed
        assert len(value) == item['bytes'] and zlib.crc32(value) == item['crc32']
        path = ROOT/relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            assert path.read_bytes() == value, 'refuse changed existing member'
        else:
            path.write_bytes(value)
        receipt = {**item, 'sha256': sha(value), 'crc_verified': True, 'compressed_sha256': sha(compressed)}
        if path.suffix == '.png':
            assert value[:8] == b'\x89PNG\r\n\x1a\n' and value[12:16] == b'IHDR'
            receipt['png_header'] = dict(zip(('width', 'height', 'bit_depth', 'color_type', 'compression', 'filter', 'interlace'), struct.unpack('>IIBBBBB', value[16:29])))
        files.append(receipt)
    receipt = {'id': 'q12-bop-assets-v1', 'dataset_root': str(ROOT), 'selection_sha256': state['selection_sha256'],
               'preparation_freeze_sha256': sha((STUDY/'preparation_freeze.json').read_bytes()),
               'charged_response_body_bytes': state['response_body_bytes'], 'unpacked_bytes': sum(x['bytes'] for x in files),
               'files': files, 'image_decoded': False, 'mesh_coordinates_inspected': False,
               'full_archive_lfs_hash_verified': False, 'download_state_sha256': sha(progress.read_bytes())}
    save(STUDY/'assets.json', receipt)
    print(json.dumps({'files': len(files), 'charged_body_bytes': state['response_body_bytes'], 'unpacked_bytes': receipt['unpacked_bytes']}))


if __name__ == '__main__':
    main()
