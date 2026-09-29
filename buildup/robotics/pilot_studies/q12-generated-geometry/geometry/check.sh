#!/usr/bin/env bash
set -euo pipefail
cd /home/yoohyun/research3
study=buildup/robotics/pilot_studies/q12-generated-geometry/geometry
test ! -e "$study/freeze.json"
stamp=$(date +%Y%m%d_%H%M%S)
log="logs/${stamp}_q12_geometry_preflight.log"
mkdir -p logs
exec >"$log" 2>&1
trap 'rc=$?; echo "$rc" > "${log%.log}.exit"' EXIT
image=$(cat "$study/image_id.txt")
receipt="$PWD/runs/q12_geometry_preflight/$stamp"
mkdir -p "$receipt"
timeout 600 docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges \
  --user "$(id -u):$(id -g)" --cpus 4 --memory 4g --memory-swap 4g \
  --tmpfs /tmp:rw,noexec,nosuid,size=128m \
  --mount "type=bind,src=$PWD/$study,dst=/study,readonly" \
  --mount "type=bind,src=$receipt,dst=/receipt" \
  "$image" preflight.py --output /receipt/preflight.json
cp "$receipt/preflight.json" "$study/preflight.json"
