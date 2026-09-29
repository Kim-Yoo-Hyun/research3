"""Host stdlib-only manifest for Q16 compatibility results before container cleanup."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TARGET = ROOT / 'runs/q16/compat_gpu/preservation.json'
SOURCE = ROOT / 'external/q16/ManiSkill-baab60ede2e89167c1b7aaed41a9aa8e690a9d1e.tar.gz'
DEMOS = ROOT / 'runs/q16/task_audit/demos'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    paths = [SOURCE, DEMOS / 'PushT-v1.zip']
    paths.extend((DEMOS / 'extracted').glob('*'))
    for name in ('README.md', 'compat_summary.json', 'compat_env.py', 'compat_replay.py',
                 'compat_bc.py', 'compat_job.py', 'compat_gpu_job.py', 'compat_cleanup.py',
                 'compat_summarize.py', 'compat_preserve.py', 'source_job.py',
                 'Dockerfile.compat_cpu', 'Dockerfile.compat_gpu', 'requirements.compat.lock',
                 'installed.compat_cpu.lock', 'installed.compat_gpu.lock'):
        paths.append(HERE / name)
    for device in ('cpu', 'gpu'):
        paths.extend(path for path in (ROOT / f'runs/q16/compat_{device}').rglob('*')
                     if path.is_file() and path != TARGET)
        paths.extend(path for path in (ROOT / 'logs').glob(f'20260925_*_q16_compat_{device}_*')
                     if path.is_file())
    paths.extend(path for path in (ROOT / 'logs').glob('20260925_*_q16_source_*')
                 if path.is_file())
    entries = []
    for path in sorted(set(paths)):
        assert path.is_file(), path
        entries.append(dict(path=str(path.relative_to(ROOT)), bytes=path.stat().st_size,
                            sha256=digest(path)))
    result = dict(status='local hashes verified', date='2026-09-25',
                  external_backup_verified=False, files=len(entries), entries=entries)
    TARGET.write_text(json.dumps(result, indent=2) + '\n')
    assert all(digest(ROOT / item['path']) == item['sha256'] for item in entries)
    print(json.dumps(dict(path=str(TARGET), files=len(entries)), indent=2))


if __name__ == '__main__':
    main()
