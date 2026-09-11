#!/usr/bin/env bash
set -euo pipefail
cd /home/yoohyun/research3
study=/home/yoohyun/research3/buildup/robotics/pilot_studies/q12-generated-geometry
image_id=$(cat "$study/model/image_id.txt")
output=/home/yoohyun/research3/runs/q12_model_schema
[[ ! -e "$output" ]]
mkdir -p "$output"
stamp=$(date +%Y%m%d_%H%M%S)
log="logs/${stamp}_q12_model_schema.log"
set +e
(
  set -e
  timeout 120 docker run --rm --name research3-q12-model-schema-preflight --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 4 --memory 4g --pids-limit 128 --tmpfs /tmp:rw,size=64m -v "$study:/study:ro" "$image_id" /study/model/selftest.py
  timeout 300 docker run --rm --name research3-q12-model-schema-v1 --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 4 --memory 4g --pids-limit 128 --user "$(id -u):$(id -g)" --tmpfs /tmp:rw,size=64m -v "$study:/study:ro" -v /home/yoohyun/research3/datasets/q12/3dsgrasp_model.pth:/checkpoint/model.pth:ro -v "$output:/output:rw" "$image_id" /study/model/schema.py --checkpoint /checkpoint/model.pth --output /output/data
) > "$log" 2>&1
status=$?
printf '%s\n' "$status" > "${log%.log}.exit"
exit "$status"
