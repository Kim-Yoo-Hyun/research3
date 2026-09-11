#!/usr/bin/env bash
set -euo pipefail
task_root=/home/yoohyun/research3
study_dir="$task_root/buildup/robotics/pilot_studies/q10-contact-observability"
task_stamp=$(date +%Y%m%d_%H%M%S)
task_prefix="$task_root/logs/${task_stamp}_q10_probe_v6"
mkdir -p "$task_root/logs" "$task_root/runs/q10_v6/train" "$task_root/runs/q10_v6/test" "$study_dir/artifacts_v6"
printf '%s\n' "$task_prefix" > "$task_root/logs/q10_probe_v6_latest.txt"
trap 'task_exit=$?; printf "%s\n" "$task_exit" > "${task_prefix}.exit"; if [ "$task_exit" -ne 0 ]; then printf "failed\n" > "${task_prefix}.status"; fi' EXIT
printf 'running\n' > "${task_prefix}.status"
# Fresh image was built by the README command; never substitute another existing image.
test "$(cat "$task_root/logs/20260908_q10_probe_v6_build.exit")" = 0
task_image=$(docker image inspect research3-q10-probe:v6 --format '{{.Id}}')
docker image inspect "$task_image" --format '{{json .}}' > "$study_dir/artifacts_v6/image.json"
docker run --rm --network none --memory 4g --cpus 1 --name "research3-q10-test-v6-$task_stamp" \
  -v "$study_dir:/workspace:ro" --entrypoint python "$task_image" -B -m unittest -v test_probe \
  > "${task_prefix}_tests.log" 2>&1
docker run --rm --network none --name "research3-q10-deps-v6-$task_stamp" \
  --entrypoint python "$task_image" -m pip freeze > "$study_dir/artifacts_v6/dependencies.txt"
# Host-side manifest/provenance inspection only; no method imports or evaluation.
python3 - "$study_dir" <<'PY'
import hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
base=Path(sys.argv[1])
names=['probe.py','verify_probe.py','test_probe.py','run_probe_v6.sh','Dockerfile_v6','protocol_v6.json','requirements_v6.txt']
record={'frozen_at_utc':datetime.now(timezone.utc).isoformat(),
        'source_sha256':{n:hashlib.sha256((base/n).read_bytes()).hexdigest() for n in names},
        'device':'cpu','memory_bytes':4294967296,'threads':1,'wall_clock_cap_seconds':1800}
with (base/'artifacts_v6/execution.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
PY
task_start=$(date +%s)
task_remaining() { echo $((1800 - $(date +%s) + task_start)); }
timeout --signal=TERM --kill-after=10s "$(task_remaining)s" \
  docker run --rm --network none --memory 4g --cpus 1 --name "research3-q10-train-v6-$task_stamp" \
  -v "$study_dir:/workspace:ro" \
  -v "$task_root/runs/q10_v5/train_features.jsonl:/input/train_features.jsonl:ro" \
  -v "$task_root/runs/q10_validation_v6/nested_predictions.jsonl:/input/audit_predictions.jsonl:ro" \
  -v "$task_root/runs/q10_v6/train:/output:rw" \
  -v "$study_dir/artifacts_v6:/artifacts:rw" \
  "$task_image" train > "${task_prefix}_train.log" 2>&1
python3 - "$study_dir" <<'PY'
import hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
base=Path(sys.argv[1])
record={'sealed_at_utc':datetime.now(timezone.utc).isoformat(),
        'training_sha256':hashlib.sha256((base/'artifacts_v6/training.json').read_bytes()).hexdigest(),
        'next_stage':'separate exploratory test container; no fit'}
with (base/'artifacts_v6/train_seal.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
PY
test "$(task_remaining)" -gt 0
timeout --signal=TERM --kill-after=10s "$(task_remaining)s" \
  docker run --rm --network none --memory 4g --cpus 1 --name "research3-q10-eval-v6-$task_stamp" \
  -v "$study_dir:/workspace:ro" \
  -v "$task_root/runs/q10_v5/test_features.jsonl:/input/test_features.jsonl:ro" \
  -v "$task_root/runs/q10_v6/test:/output:rw" \
  -v "$study_dir/artifacts_v6:/artifacts:rw" \
  "$task_image" evaluate > "${task_prefix}_evaluate.log" 2>&1
printf 'needs verification\n' > "${task_prefix}.status"
test "$(task_remaining)" -gt 0
timeout --signal=TERM --kill-after=10s "$(task_remaining)s" \
  docker run --rm --network none --memory 4g --cpus 1 --name "research3-q10-verify-v6-$task_stamp" \
  -v "$study_dir:/workspace:ro" \
  -v "$task_root/runs/q10_v5/train_features.jsonl:/input/train_features.jsonl:ro" \
  -v "$task_root/runs/q10_v5/test_features.jsonl:/input/test_features.jsonl:ro" \
  -v "$task_root/runs/q10_v6:/raw:ro" \
  -v "$study_dir/artifacts_v6:/artifacts:rw" \
  --entrypoint python "$task_image" -B /workspace/verify_probe.py > "${task_prefix}_verify.log" 2>&1
printf 'completed\n' > "${task_prefix}.status"
