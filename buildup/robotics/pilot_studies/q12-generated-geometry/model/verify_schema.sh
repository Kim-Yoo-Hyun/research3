#!/usr/bin/env bash
set -euo pipefail
cd /home/yoohyun/research3
study=/home/yoohyun/research3/buildup/robotics/pilot_studies/q12-generated-geometry/model
output=${1:-/home/yoohyun/research3/runs/q12_model_schema_audit_recheck}
[[ ! -e "$output" ]]
mkdir -p "$output"
stamp=$(date +%Y%m%d_%H%M%S)
log="logs/${stamp}_q12_schema_verify_recheck.log"
set +e
timeout --signal=TERM --kill-after=20 120 docker run --rm --name research3-q12-schema-verify-recheck --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 4 --memory 4g --memory-swap 4g --pids-limit 128 --user "$(id -u):$(id -g)" --tmpfs /tmp:rw,size=64m -v "$study:/study/model:ro" -v /home/yoohyun/research3/datasets/q12/3dsgrasp_model.pth:/checkpoint/model.pth:ro -v /home/yoohyun/research3/runs/q12_model_schema/data:/result:ro -v "$output:/verification:rw" "$(cat "$study/image_id.txt")" /study/model/verify_schema.py > "$log" 2>&1
q12_exit=$?
printf '%s\n' "$q12_exit" > "${log%.log}.exit"
exit "$q12_exit"
