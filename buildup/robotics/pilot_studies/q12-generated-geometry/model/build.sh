#!/usr/bin/env bash
set -euo pipefail
cd /home/yoohyun/research3
model=buildup/robotics/pilot_studies/q12-generated-geometry/model
[[ ! -e "$model/image_id.txt" ]]
stamp=$(date +%Y%m%d_%H%M%S)
log="logs/${stamp}_q12_model_build.log"
set +e
(
  set -e
  timeout 1200 docker build --pull --no-cache --platform linux/amd64 -t research3-q12-model-schema:v1 "$model"
  docker image inspect research3-q12-model-schema:v1 --format '{{.Id}}' > "$model/image_id.txt"
  image_id=$(cat "$model/image_id.txt")
  docker run --rm --name research3-q12-model-schema-lock --network none --read-only --cap-drop ALL --security-opt no-new-privileges "$image_id" -m pip freeze --all > "$model/environment.txt"
  docker image inspect "$image_id" --format '{{.Size}}' > "$model/image_bytes.txt"
) > "$log" 2>&1
status=$?
printf '%s\n' "$status" > "${log%.log}.exit"
exit "$status"
