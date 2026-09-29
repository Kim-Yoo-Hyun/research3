"""Host-only bounded public transfer, archive metadata/extraction and hashes; no method imports."""
import gzip
import hashlib
import json
from pathlib import Path
import tarfile
import urllib.request

ROOT = Path('/home/yoohyun/research3')
STUDY = ROOT / 'buildup/robotics/pilot_studies/q12-generated-geometry/geometry'
DEST = ROOT / 'datasets/q12/geometry'
SOURCE = STUDY.parent / 'linkage_sources.json'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def main():
    assert not (STUDY / 'assets.json').exists(), 'preserve existing receipt'
    probes = json.loads(SOURCE.read_text())['asset_access_probes']
    assert len(probes) == 2
    DEST.mkdir(parents=True, exist_ok=True)
    selection = [{'id': p['url'].split('/')[-1].replace('_google_16k.tgz', ''),
                  'url': p['url'], 'bytes': int(p['content_length']), 'etag': p['etag']}
                 for p in probes]
    selected = DEST / 'selection.json'
    if selected.exists():
        assert json.loads(selected.read_text()) == selection
    else:
        selected.write_text(json.dumps(selection, indent=2) + '\n')
    transferred = 0
    rows = []
    for item in selection:
        archive = DEST / (item['id'] + '.tgz')
        partial = archive.with_suffix('.tgz.part')
        if not archive.exists():
            for attempt in range(3):
                offset = partial.stat().st_size if partial.exists() else 0
                if offset == item['bytes']:
                    break
                headers = {'Range': f'bytes={offset}-', 'If-Range': item['etag'],
                           'User-Agent': 'research3-q12-geometry'}
                try:
                    with urllib.request.urlopen(urllib.request.Request(item['url'], headers=headers), timeout=30) as r:
                        assert r.status == 206 or (offset == 0 and r.status == 200)
                        if r.status == 206:
                            assert r.headers['Content-Range'] == f"bytes {offset}-{item['bytes']-1}/{item['bytes']}"
                        assert r.headers.get('ETag') == item['etag'], 'asset changed since HEAD'
                        with partial.open('ab') as f:
                            for b in iter(lambda: r.read(1024 * 1024), b''):
                                transferred += len(b)
                                assert transferred <= 64 * 1024**2, 'network body cap'
                                assert f.tell() + len(b) <= item['bytes']
                                f.write(b)
                    assert partial.stat().st_size == item['bytes']
                    break
                except (OSError, TimeoutError):
                    if attempt == 2:
                        raise
            assert partial.stat().st_size == item['bytes']
            partial.rename(archive)
        assert archive.stat().st_size == item['bytes']
        uncompressed = 0
        with gzip.open(archive, 'rb') as f:
            for b in iter(lambda: f.read(1024 * 1024), b''):
                uncompressed += len(b)
                assert uncompressed <= 128 * 1024**2, 'per-archive decompression cap'
        with tarfile.open(archive, 'r:gz') as tf:
            members = tf.getmembers()
            assert all(not m.issym() and not m.islnk() and not Path(m.name).is_absolute()
                       and '..' not in Path(m.name).parts for m in members)
            targets = [m for m in members if m.isfile() and m.name.endswith('/google_16k/textured.obj')]
            assert len(targets) == 1, [(m.name, m.size) for m in members]
            member = targets[0]
            mesh = DEST / (item['id'] + '.obj')
            data = tf.extractfile(member).read()
            assert len(data) == member.size
            if mesh.exists():
                assert mesh.read_bytes() == data
            else:
                mesh.write_bytes(data)
            rows.append({**item, 'archive_path': str(archive.relative_to(ROOT)),
                         'archive_sha256': sha(archive), 'gzip_crc_verified': True,
                         'tar_uncompressed_bytes': uncompressed,
                         'members': [{'name': m.name, 'bytes': m.size, 'regular_file': m.isfile()} for m in members],
                         'mesh_member': member.name, 'mesh_path': str(mesh.relative_to(ROOT)),
                         'mesh_bytes': len(data), 'mesh_sha256': sha(mesh)})
        print('ACQUIRED', item['id'], item['bytes'], 'mesh bytes', len(data), flush=True)
    assert sum(r['tar_uncompressed_bytes'] for r in rows) <= 256 * 1024**2
    receipt = {'id': 'q12-geometry-assets-v1', 'selection_before_payload_inspection': True,
               'license': 'YCB dataset index states CC BY 4.0; code MIT. Google mesh provenance retained; no relicense.',
               'license_url': 'https://ycb-benchmarks.s3.amazonaws.com/index.html',
               'geometry_units_topology_and_runtime_unverified': True,
               'publisher_checksum_available': False, 'successful_transfer_bytes_this_invocation': transferred,
               'objects': rows}
    (STUDY / 'assets.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('ACQUISITION_COMPLETE', flush=True)


if __name__ == '__main__':
    main()
