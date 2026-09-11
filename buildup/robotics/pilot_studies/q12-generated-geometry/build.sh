#!/usr/bin/env bash
set -euo pipefail
cd /home/yoohyun/research3
study=buildup/robotics/pilot_studies/q12-generated-geometry
if [[ -e "$study/freeze.json" ]]; then
  echo 'Frozen study: use a separate recovery build and runtime receipt.' >&2
  exit 1
fi
stamp=$(date +%Y%m%d_%H%M%S)
log="logs/${stamp}_q12_build.log"
set +e
(
  set -e
  timeout 900 docker build --pull --no-cache --platform linux/amd64 -t research3-q12-input:v1 "$study"
  docker image inspect research3-q12-input:v1 --format '{{.Id}}' > "$study/image_id.txt"
  image_id=$(cat "$study/image_id.txt")
  timeout 120 docker run --rm --name research3-q12-input-preflight-v1 --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 2 --memory 2g --pids-limit 128 --tmpfs /tmp:rw,size=64m -v "/home/yoohyun/research3/$study:/study:ro" "$image_id" /study/selftest.py
  docker run --rm --name research3-q12-input-lock-v1 --network none --read-only --cap-drop ALL --security-opt no-new-privileges "$image_id" -m pip freeze --all > "$study/environment.txt"
) > "$log" 2>&1
status=$?
printf '%s\n' "$status" > "${log%.log}.exit"
exit "$status"
