#!/usr/bin/env bash
set -euo pipefail
cd /home/yoohyun/research3
study=buildup/robotics/pilot_studies/q12-generated-geometry/geometry
output=runs/q12_geometry_v1_mesh_audit
test ! -e "$output"
stamp=$(date +%Y%m%d_%H%M%S)
log="logs/${stamp}_q12_mesh_audit.log"
mkdir -p logs
exec >"$log" 2>&1
trap 'rc=$?; echo "$rc" > "${log%.log}.exit"' EXIT
mkdir "$output"
image=$(cat "$study/image_id.txt")
timeout 300 docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges \
  --user "$(id -u):$(id -g)" --cpus 2 --memory 1g --memory-swap 1g \
  --tmpfs /tmp:rw,noexec,nosuid,size=32m \
  --mount "type=bind,src=$PWD/$study,dst=/study,readonly" \
  --mount "type=bind,src=$PWD/datasets/q12/geometry,dst=/assets,readonly" \
  --mount "type=bind,src=$PWD/runs/q12_geometry_v1,dst=/input,readonly" \
  --mount "type=bind,src=$PWD/$output,dst=/output" \
  "$image" verify_mesh.py
