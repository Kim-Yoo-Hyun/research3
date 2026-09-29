"""Host stdlib-only downloader for the ManiSkill revision named by PushT demos."""
import datetime
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
COMMIT = 'baab60ede2e89167c1b7aaed41a9aa8e690a9d1e'
TARGET = ROOT / 'external/q16' / f'ManiSkill-{COMMIT}.tar.gz'
URL = f'https://codeload.github.com/mani-skill/ManiSkill/tar.gz/{COMMIT}'
SOURCE_DIR = TARGET.parent / f'ManiSkill-{COMMIT}'


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else 'download'
    if stage not in ('download', 'extract'):
        raise ValueError(stage)
    if stage == 'extract':
        if SOURCE_DIR.exists():
            raise FileExistsError(SOURCE_DIR)
        if not TARGET.is_file():
            raise FileNotFoundError(TARGET)
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    log = ROOT / 'logs' / f'{stamp}_q16_source_{stage}.log'
    exit_path = log.with_suffix('.exit')
    command = (['wget', '-c', '--tries=3', '--timeout=30', '-O', str(TARGET), URL]
               if stage == 'download' else ['tar', '-xzf', str(TARGET), '-C', str(TARGET.parent)])
    with log.open('xb') as stream:
        child = subprocess.Popen([sys.executable, str(__file__), '_worker', stage, str(exit_path)],
                                 cwd=ROOT, stdin=subprocess.DEVNULL, stdout=stream,
                                 stderr=subprocess.STDOUT, start_new_session=True)
    print(json.dumps(dict(pid=child.pid, command=command, working_directory=str(ROOT),
                          output=str(TARGET if stage == 'download' else SOURCE_DIR),
                          log=str(log), exit=str(exit_path)), indent=2))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '_worker':
        command = (['wget', '-c', '--tries=3', '--timeout=30', '-O', str(TARGET), URL]
                   if sys.argv[2] == 'download' else
                   ['tar', '-xzf', str(TARGET), '-C', str(TARGET.parent)])
        code = subprocess.run(command, cwd=ROOT).returncode
        Path(sys.argv[3]).write_text(str(code) + '\n')
    else:
        main()
