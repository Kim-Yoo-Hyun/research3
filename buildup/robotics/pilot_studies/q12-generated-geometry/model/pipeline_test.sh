#!/usr/bin/env bash
set -uo pipefail
cd /home/yoohyun/research3
study=/home/yoohyun/research3/buildup/robotics/pilot_studies/q12-generated-geometry/model
stamp=$(date +%Y%m%d_%H%M%S)
log=logs/${stamp}_q12_reference_pipeline.log
timeout --signal=TERM --kill-after=20 300 docker run --rm --name research3-q12-reference-pipeline --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 4 --memory 4g --memory-swap 4g --pids-limit 128 --user "$(id -u):$(id -g)" --tmpfs /tmp:rw,size=512m -v "$study:/study/model:ro" -v /home/yoohyun/research3/runs/q12_model_reference_preflight:/output:rw "$(cat "$study/image_id.txt")" /study/model/pipeline_test.py > "$log" 2>&1
q12_exit=$?
printf '%s\n' "$q12_exit" > "${log%.log}.exit"
exit "$q12_exit"
