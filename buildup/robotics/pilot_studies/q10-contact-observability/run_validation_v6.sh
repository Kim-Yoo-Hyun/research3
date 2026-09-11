#!/usr/bin/env bash
set -euo pipefail
task_root=/home/yoohyun/research3
study_dir="$task_root/buildup/robotics/pilot_studies/q10-contact-observability"
task_stamp=$(date +%Y%m%d_%H%M%S)
task_prefix="$task_root/logs/${task_stamp}_q10_validation_v6"
mkdir -p "$task_root/logs" "$task_root/runs/q10_validation_v6" "$study_dir/artifacts_validation_v6"
printf '%s\n' "$task_prefix" > "$task_root/logs/q10_validation_v6_latest.txt"
trap 'task_exit=$?; printf "%s\n" "$task_exit" > "${task_prefix}.exit"; if [ "$task_exit" -ne 0 ]; then printf "failed\n" > "${task_prefix}.status"; fi' EXIT
printf 'running\n' > "${task_prefix}.status"
docker build --pull --no-cache -t research3-q10-validation:v6 \
  -f "$study_dir/Dockerfile_validation_v6" "$study_dir" > "${task_prefix}_build.log" 2>&1
docker image inspect research3-q10-validation:v6 --format '{{json .}}' > "$study_dir/artifacts_validation_v6/image.json"
python3 - "$study_dir" "$task_root" <<'PY'
import hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
base,root=map(Path,sys.argv[1:])
names=['audit_validation.py','run_validation_v6.sh','Dockerfile_validation_v6','requirements_v2.txt',
       'baselines.py','artifacts_v4/segments.tsv','artifacts_v5/training.json','artifacts_v5/checksums.json']
record={'frozen_at_utc':datetime.now(timezone.utc).isoformat(),
        'source_sha256':{name:hashlib.sha256((base/name).read_bytes()).hexdigest() for name in names},
        'train_features_sha256':hashlib.sha256((root/'runs/q10_v5/train_features.jsonl').read_bytes()).hexdigest()}
with (base/'artifacts_validation_v6/freeze.json').open('x') as stream:
    json.dump(record,stream,indent=2);stream.write('\n')
PY
docker run --rm --network none --name research3-q10-validation-v6 \
  -v "$study_dir:/workspace:ro" \
  -v "$task_root/runs/q10_v5/train_features.jsonl:/input/train_features.jsonl:ro" \
  -v "$task_root/runs/q10_validation_v6:/output:rw" \
  -v "$study_dir/artifacts_validation_v6:/artifacts:rw" \
  research3-q10-validation:v6 > "${task_prefix}_run.log" 2>&1
printf 'needs verification\n' > "${task_prefix}.status"
docker run --rm --network none --name research3-q10-validation-verify-v6 \
  -v "$study_dir:/workspace:ro" \
  -v "$task_root/runs/q10_v5/train_features.jsonl:/input/train_features.jsonl:ro" \
  -v "$task_root/runs/q10_validation_v6:/output:ro" \
  -v "$study_dir/artifacts_validation_v6:/artifacts:rw" \
  research3-q10-validation:v6 --verify > "${task_prefix}_verify.log" 2>&1
printf 'completed\n' > "${task_prefix}.status"
