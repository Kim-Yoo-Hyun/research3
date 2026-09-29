"""Host-allowed download/byte inspection only; no method or numerical imports."""
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path('/home/yoohyun/research3')
DEST = ROOT / 'datasets/q14/dream'
REV = '3360f2aa45f66a58eaa70d0d40f2c46c2682c0bb'
ITEMS = [
    ('source.zip', f'https://codeload.github.com/NVlabs/DREAM/zip/{REV}'),
    ('panda_dream_vgg_q.yaml', 'https://drive.usercontent.google.com/download?id=1MKDiknxDzXErd4Gwdv0uMoL65IYjxO0Q&export=download&confirm=t'),
    ('panda_dream_vgg_q.pth', 'https://drive.usercontent.google.com/download?id=1zS-kQ73dOYMXS8Wku_OUN0q7MvEUm2fZ&export=download&confirm=t'),
    ('panda-3cam_realsense.archive', 'https://drive.usercontent.google.com/download?id=1FFAFpJFwzsjD83S9-Y1ODwDWiWlh1X6P&export=download&confirm=t'),
]

def main():
    DEST.mkdir(parents=True, exist_ok=True)
    manifest = {'revision': REV, 'files': []}
    for name, url in ITEMS:
        path = DEST / name
        cmd = ['curl', '--fail', '--location', '--retry', '2', '--max-time', '900',
               '--continue-at', '-', '--output', str(path), url]
        print('Downloading', name, flush=True)
        result = subprocess.run(cmd)
        row = {'name': name, 'url': url, 'command': cmd, 'exit_code': result.returncode}
        if path.exists():
            digest = hashlib.sha256()
            with path.open('rb') as f:
                head = f.read(256); digest.update(head)
                for block in iter(lambda: f.read(1 << 20), b''): digest.update(block)
            row.update(bytes=path.stat().st_size, sha256=digest.hexdigest(), head_hex=head[:16].hex())
            row['html_response'] = b'<html' in head.lower() or b'<!doctype html' in head.lower()
        manifest['files'].append(row)
        (DEST / 'acquisition.json').write_text(json.dumps(manifest, indent=2)+'\n')
        if result.returncode or row.get('html_response'):
            raise SystemExit('Acquisition failed; see manifest. No method execution.')
        if name == 'source.zip':
            out = ROOT/'external/q14-dream'
            out.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(path) as z:
                for info in z.infolist():
                    rel = Path(info.filename).relative_to(f'DREAM-{REV}')
                    assert '..' not in rel.parts
                    if not info.is_dir():
                        target = out/rel
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(z.read(info))
    print('Acquisition completed', flush=True)

if __name__ == '__main__': main()
