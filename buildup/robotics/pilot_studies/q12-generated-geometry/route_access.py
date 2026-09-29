"""Read-only source/ZIP metadata access, standard library only; no method runtime."""
import datetime
import hashlib
import io
import json
from pathlib import Path
import urllib.error
import urllib.request
import zipfile

ROOT = Path('/tmp/research3-q12-routes-20260914')
OWNER = Path('/home/yoohyun/research3/buildup/robotics/pilot_studies/q12-generated-geometry')
REV = '5c2c4aa229800355648cd268040aa814f8dc94f0'
BOP = 'cea62d651c7e395b2e1962b9749e4e89693c6ac4'
CAP = 4*1024*1024
used = {'source': 0, 'range': 0}
records, errors = [], []


def digest(b):
    return hashlib.sha256(b).hexdigest()


def get(url, name, category='source', start=None, count=None, total=None):
    headers = {'User-Agent': 'research3-q12-read-only-access', 'Accept-Encoding': 'identity'}
    request_url = url
    if start is not None:
        end = start+count-1
        headers['Range'] = f'bytes={start}-{end}'
        request_url += f'?download=true&q12_range={start}-{end}'
    budget = CAP-used[category]
    assert budget > 0
    with urllib.request.urlopen(urllib.request.Request(request_url, headers=headers), timeout=20) as response:
        if start is not None:
            expected = f'bytes {start}-{end}/{total}'
            assert response.status == 206 and response.headers.get('Content-Range') == expected, 'exact range unavailable; refuse full fallback'
            assert count <= budget
            data = response.read(count+1)
            assert len(data) == count
        else:
            data = response.read(budget+1)
            assert len(data) <= budget
        rec = {'url': url, 'cache_path': str(ROOT/name), 'http_status': response.status,
               'content_range': response.headers.get('Content-Range'), 'bytes': len(data), 'sha256': digest(data)}
    used[category] += len(data)
    path = ROOT/name
    path.parent.mkdir(parents=True, exist_ok=True)
    assert not path.exists()
    path.write_bytes(data)
    records.append(rec)
    return data


class Remote(io.RawIOBase):
    def __init__(self, url, size, name):
        self.url, self.size, self.name, self.pos, self.calls = url, size, name, 0, 0

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=0):
        self.pos = offset if whence == 0 else (self.pos if whence == 1 else self.size)+offset
        assert 0 <= self.pos <= self.size
        return self.pos

    def read(self, count=-1):
        count = min(self.size-self.pos, count if count >= 0 else self.size-self.pos)
        if not count:
            return b''
        self.calls += 1
        value = get(self.url, f'ranges/{self.name}/{self.calls:03d}_{self.pos}_{count}.bin', 'range', self.pos, count, self.size)
        self.pos += len(value)
        return value


def extract_metadata(archive, member, folder):
    item = archive.getinfo(member)
    assert item.file_size <= 2*1024*1024 and item.compress_size <= 1024*1024
    assert member.endswith(('.json', '.md', '.txt'))
    value = archive.read(member)  # zipfile verifies CRC
    path = ROOT/folder/member
    path.parent.mkdir(parents=True, exist_ok=True)
    assert not path.exists()
    path.write_bytes(value)
    return {'member': member, 'cache_path': str(path), 'bytes': len(value), 'sha256': digest(value), 'crc32': item.CRC, 'crc_verified': True}


def main():
    assert not ROOT.exists() and not (OWNER/'route_sources.json').exists()
    ROOT.mkdir()
    sources = [('https://bop.felk.cvut.cz/datasets/', 'bop-datasets.html'),
               ('https://graspnet.net/datasets.html', 'graspnet-datasets.html'),
               (f'https://huggingface.co/api/datasets/bop-benchmark/ycbv/revision/{REV}', 'hf-revision.json'),
               (f'https://huggingface.co/api/datasets/bop-benchmark/ycbv/tree/{REV}?recursive=true&expand=false', 'hf-tree.json')]
    for path in ('docs/bop_datasets_format.md', 'scripts/calc_gt_masks.py', 'bop_toolkit_lib/visibility.py',
                 'bop_toolkit_lib/dataset_params.py', 'bop_toolkit_lib/inout.py'):
        sources.append((f'https://raw.githubusercontent.com/thodan/bop_toolkit/{BOP}/{path}', f'bop_toolkit/{path}'))
    for url, name in sources:
        try:
            get(url, name)
        except Exception as e:
            errors.append({'source': url, 'error': f'{type(e).__name__}: {e}'})
    archives = []
    tree = json.loads((ROOT/'hf-tree.json').read_text())
    revision = json.loads((ROOT/'hf-revision.json').read_text())
    assert revision['sha'] == REV
    for name in ('ycbv_base.zip', 'ycbv_models.zip', 'ycbv_test_bop19.zip'):
        item = next(x for x in tree if x['path'] == name)
        report = {'file': name, 'archive_bytes': item['size'], 'lfs': item.get('lfs'), 'metadata_members': []}
        url = f'https://huggingface.co/datasets/bop-benchmark/ycbv/resolve/{REV}/{name}'
        try:
            remote = Remote(url, item['size'], name)
            with zipfile.ZipFile(remote) as archive:
                members = [{'path': i.filename, 'bytes': i.file_size, 'compressed_bytes': i.compress_size,
                            'crc32': i.CRC, 'local_header_offset': i.header_offset, 'method': i.compress_type}
                           for i in archive.infolist()]
                target = ROOT/f'{name}.directory.json'
                target.write_text(json.dumps(members, indent=2)+'\n')
                report.update({'directory_verified': True, 'member_count': len(members),
                               'directory_path': str(target), 'directory_sha256': digest(target.read_bytes()),
                               'directory_bytes': target.stat().st_size})
                names = archive.namelist()
                if name == 'ycbv_base.zip':
                    selected = [n for n in names if n.endswith(('dataset_info.md', 'camera_uw.json', 'camera_cmu.json', 'test_targets_bop19.json'))]
                elif name == 'ycbv_models.zip':
                    selected = [n for n in names if n.endswith('models_info.json')]
                else:
                    # Source/schema inspection only: choose the first listed scene, not a mesh/view outcome.
                    cameras = sorted(n for n in names if n.endswith('/scene_camera.json'))
                    scene = cameras[0].rsplit('/', 1)[0]
                    selected = [f'{scene}/{n}' for n in ('scene_camera.json', 'scene_gt.json', 'scene_gt_info.json')]
                for member in selected:
                    report['metadata_members'].append(extract_metadata(archive, member, f'metadata/{name}'))
                report['http_range_reads'] = remote.calls
        except Exception as e:
            report['error'] = f'{type(e).__name__}: {e}'
            errors.append({'archive': name, 'error': report['error']})
        archives.append(report)
    result = {'id': 'q12-alternative-route-source-access-20260914',
              'completed_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'script_sha256': digest(Path(__file__).read_bytes()),
              'scope': 'official source and archive/JSON metadata only; no image/mesh member extraction, numerical geometry, simulator, model or policy execution',
              'repositories': {'bop_dataset': {'repository': 'bop-benchmark/ycbv', 'revision': REV},
                               'bop_toolkit': {'repository': 'thodan/bop_toolkit', 'commit': BOP},
                               'graspnetAPI': {'repository': 'graspnet/graspnetAPI', 'commit': 'eb57dd2092d8dbe05312a29c3d0c22f3226efbfc',
                                              'source_identity': 'unchanged from linkage_sources.json; rechecked GitHub master API'}},
              'cache_root': str(ROOT), 'files': records, 'archives': archives, 'body_bytes': used,
              'per_category_body_cap_bytes': CAP, 'errors': errors,
              'recovery': 'retrieve pinned source/ranges into separate staging; compare bytes/SHA-256, Content-Range and member CRC. ZIP directory and member CRC are not full-archive LFS SHA-256 verification or numerical validity.'}
    (OWNER/'route_sources.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'body_bytes': used, 'archives': [{'file': a['file'], 'directory_verified': a.get('directory_verified', False), 'metadata_members': len(a['metadata_members']), 'error': a.get('error')} for a in archives], 'errors': errors}))


if __name__ == '__main__':
    main()
