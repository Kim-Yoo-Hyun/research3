#!/usr/bin/env bash
set -euo pipefail
task_root=/home/yoohyun/research3
study_dir="$task_root/buildup/robotics/pilot_studies/q10-contact-observability"
task_stamp=$(date +%Y%m%d_%H%M%S)
task_prefix="$task_root/logs/${task_stamp}_q10_v5"
mkdir -p "$task_root/logs" "$task_root/runs/q10_v5" "$study_dir/artifacts_v5"
printf '%s\n' "$task_prefix" > "$task_root/logs/q10_v5_latest.txt"
trap 'task_exit=$?; printf "%s\n" "$task_exit" > "${task_prefix}.exit"; if [ "$task_exit" -ne 0 ]; then printf "failed\n" > "${task_prefix}.status"; fi' EXIT
printf 'running\n' > "${task_prefix}.status"

docker build --pull --no-cache -t research3-q10-baselines:v5 \
  -f "$study_dir/Dockerfile_v5" "$study_dir" > "${task_prefix}_build.log" 2>&1
docker image inspect research3-q10-baselines:v5 --format '{{json .}}' > "$study_dir/artifacts_v5/image.json"

# Host-side provenance inspection only: no method dependencies are imported or executed.
python3 - "$study_dir" <<'PY'
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
base = Path(sys.argv[1])
names = ['manifest_v5.md', 'baselines.py', 'test_baselines.py', 'verify_v5.py', 'run_v5.sh',
         'Dockerfile_v5', 'requirements_v2.txt', 'selection_v4.json', 'artifacts_v4/segments.tsv']
record = {'frozen_at_utc': datetime.now(timezone.utc).isoformat(),
          'source_sha256': {name: hashlib.sha256((base/name).read_bytes()).hexdigest() for name in names}}
with (base/'artifacts_v5/freeze.json').open('x') as stream:
    json.dump(record, stream, indent=2)
    stream.write('\n')
PY

docker run --rm --network none --name research3-q10-tests-v5 \
  -v "$study_dir:/workspace:ro" --entrypoint python \
  research3-q10-baselines:v5 -B -m unittest -v test_baselines > "${task_prefix}_tests.log" 2>&1

docker run --rm --network none --name research3-q10-baselines-v5 \
  -v "$task_root/datasets/q10_reassemble/v2:/input-v2:ro" \
  -v "$task_root/datasets/q10_reassemble/v4:/input-v4:ro" \
  -v "$study_dir:/workspace:ro" \
  -v "$task_root/runs/q10_v5:/output:rw" \
  -v "$study_dir/artifacts_v5:/artifacts:rw" \
  research3-q10-baselines:v5 --input-dir /input-v2 --input-dir /input-v4 \
  > "${task_prefix}_run.log" 2>&1

printf 'needs verification\n' > "${task_prefix}.status"
docker run --rm --network none --name research3-q10-verify-v5 \
  -v "$study_dir:/workspace:ro" \
  -v "$task_root/runs/q10_v5:/output:ro" \
  -v "$study_dir/artifacts_v5:/artifacts:rw" \
  --entrypoint python research3-q10-baselines:v5 /workspace/verify_v5.py \
  > "${task_prefix}_verify.log" 2>&1
printf 'completed\n' > "${task_prefix}.status"
