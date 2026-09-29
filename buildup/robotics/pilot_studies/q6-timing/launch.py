"""Detached, recorded Docker-only execution; host uses standard library only."""
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
stage = sys.argv[1]
assert stage in ("schema", "preflight", "readiness", "repeat", "verify")
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
out = ROOT / "runs/q6/readiness"
out.mkdir(parents=True, exist_ok=True)
image = json.loads(subprocess.check_output(["docker", "image", "inspect", "research3-q6-readiness:v1"]))[0]
assert image["Size"] < 12 * 1024**3
cpus = ",".join(map(str, sorted(os.sched_getaffinity(0))[:8]))
name = f"research3-q6-{stage}-{stamp}"
script = "readiness.py" if stage == "repeat" else stage + ".py"
command = ["docker", "run", "--name", name, "--cpus=8", f"--cpuset-cpus={cpus}",
           "--memory=24g", "--memory-swap=24g", "--network=none", "--pids-limit=512",
           "--user", f"{os.getuid()}:{os.getgid()}", "--entrypoint", "timeout",
           "-v", f"{ROOT / 'external/q6'}:/source:ro", "-v", f"{ROOT / 'datasets/q6'}:/data:ro",
           "-v", f"{HERE}:/study:ro", "-v", f"{out}:/output:rw",
           image["Id"], "7200s", "python", "-B", "-u", f"/study/{script}"]
if stage == "repeat":
    command.append("--repeat")
log = ROOT / "logs" / f"{stamp}_q6_{stage}.log"
exit_path = log.with_suffix(".exit")
record = {"stage": stage, "status": "launched", "launched_at": stamp, "container": name,
          "working_directory": str(ROOT), "command": command, "image_id": image["Id"],
          "image_size_bytes": image["Size"], "image_repo_digests": image.get("RepoDigests"),
          "output": str(out), "log": str(log.relative_to(ROOT)), "exit": str(exit_path.relative_to(ROOT))}
record_path = out / f"{stage}_launch.json"
assert not record_path.exists(), "Preserve earlier attempt; use an explicit new attempt record"
record_path.write_text(json.dumps(record, indent=2) + "\n")
worker = "import subprocess,pathlib,sys; r=subprocess.run(sys.argv[2:]); pathlib.Path(sys.argv[1]).write_text(str(r.returncode)+'\\n')"
with log.open("xb") as stream:
    p = subprocess.Popen([sys.executable, "-c", worker, str(exit_path), *command],
                         cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                         stdin=subprocess.DEVNULL, start_new_session=True)
print(json.dumps({"pid": p.pid, **record}, indent=2))
