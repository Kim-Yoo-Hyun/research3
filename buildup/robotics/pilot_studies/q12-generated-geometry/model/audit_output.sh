#!/usr/bin/env bash
set -euo pipefail
cd /home/yoohyun/research3
study=/home/yoohyun/research3/buildup/robotics/pilot_studies/q12-generated-geometry/model
output=/home/yoohyun/research3/runs/q12_completion_reference_v1_audit
[[ ! -e "$output" ]]
mkdir -p "$output"
stamp=$(date +%Y%m%d_%H%M%S)
log="logs/${stamp}_q12_output_bytes.log"
set +e
timeout --signal=TERM --kill-after=10 60 docker run --rm --name research3-q12-output-byte-audit --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 1 --memory 512m --memory-swap 512m --pids-limit 64 --user "$(id -u):$(id -g)" --tmpfs /tmp:rw,size=16m -v "$study:/study/model:ro" -v /home/yoohyun/research3/runs/q12_completion_reference_v1:/result:ro -v "$output:/audit:rw" "$(cat "$study/image_id.txt")" /study/model/audit_output.py > "$log" 2>&1
q12_exit=$?
printf '%s\n' "$q12_exit" > "${log%.log}.exit"
exit "$q12_exit"
