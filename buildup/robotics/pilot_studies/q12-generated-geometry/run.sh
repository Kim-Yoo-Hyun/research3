#!/usr/bin/env bash
set -euo pipefail
cd /home/yoohyun/research3
study=/home/yoohyun/research3/buildup/robotics/pilot_studies/q12-generated-geometry
image_id=$(cat "$study/image_id.txt")
output=/home/yoohyun/research3/runs/q12_input_v1
verification=/home/yoohyun/research3/runs/q12_input_v1_audit
[[ ! -e "$output" && ! -e "$verification" ]]
mkdir -p "$output" "$verification"
stamp=$(date +%Y%m%d_%H%M%S)
log="logs/${stamp}_q12_input_v1.log"
set +e
(
  set -e
  timeout 600 docker run --rm --name research3-q12-input-v1 --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 2 --memory 2g --pids-limit 128 --user "$(id -u):$(id -g)" --tmpfs /tmp:rw,size=64m -v "$study:/study:ro" -v /home/yoohyun/research3/datasets/q12/subset:/input/subset:ro -v "$output:/output:rw" "$image_id" /study/audit.py --inputs /input --output /output/data
  timeout 600 docker run --rm --name research3-q12-input-verify-v1 --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 2 --memory 2g --pids-limit 128 --user "$(id -u):$(id -g)" --tmpfs /tmp:rw,size=64m -v "$study:/study:ro" -v /home/yoohyun/research3/datasets/q12/subset:/input/subset:ro -v "$output/data:/result:ro" -v "$verification:/verification:rw" "$image_id" /study/verify.py --inputs /input --result /result --output /verification/verification.json
) > "$log" 2>&1
status=$?
printf '%s\n' "$status" > "${log%.log}.exit"
exit "$status"
