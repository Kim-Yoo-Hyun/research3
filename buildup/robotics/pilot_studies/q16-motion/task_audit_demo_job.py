"""Host stdlib-only resumable dataset download launcher; no method execution."""
import datetime
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TARGET = ROOT / 'runs/q16/task_audit/demos/PushT-v1.zip'
URL = ('https://huggingface.co/datasets/haosulab/ManiSkill_Demonstrations/resolve/'
       'bedb31208d5a03f343c2fbe329744856d7869724/demos/PushT-v1.zip?download=true')


def main():
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    log = ROOT / 'logs' / f'{stamp}_q16_task_audit_demo.log'
    exit_path = log.with_suffix('.exit')
    with log.open('xb') as stream:
        child = subprocess.Popen([sys.executable, str(__file__), '_worker', str(exit_path)],
                                 cwd=ROOT, stdin=subprocess.DEVNULL, stdout=stream,
                                 stderr=subprocess.STDOUT, start_new_session=True)
    print(dict(pid=child.pid, command=['wget', '-c', '--tries=3', '--timeout=30',
                                       '-O', str(TARGET), URL], working_directory=str(ROOT),
               output=str(TARGET), log=str(log), exit=str(exit_path)))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '_worker':
        command = ['wget', '-c', '--tries=3', '--timeout=30', '-O', str(TARGET), URL]
        code = subprocess.run(command, cwd=ROOT).returncode
        Path(sys.argv[2]).write_text(str(code) + '\n')
    else:
        main()
