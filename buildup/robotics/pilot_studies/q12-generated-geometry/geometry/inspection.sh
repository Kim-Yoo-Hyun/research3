#!/usr/bin/env bash
set -euo pipefail
cd /home/yoohyun/research3
study=buildup/robotics/pilot_studies/q12-generated-geometry/geometry
output=runs/q12_mesh_preservation_v1_inspection
test ! -e "$output"
stamp=$(date +%Y%m%d_%H%M%S)
log="logs/${stamp}_q12_preservation_inspection.log"
mkdir -p logs
exec >"$log" 2>&1
trap 'rc=$?; echo "$rc" > "${log%.log}.exit"' EXIT
mkdir "$output"
image=$(cat "$study/image_id.txt")
timeout 600 docker run --rm --name "research3-q12-preservation-inspection-$stamp" \
  --network none --read-only --cap-drop ALL --security-opt no-new-privileges \
  --user "$(id -u):$(id -g)" --cpus 2 --memory 2g --memory-swap 2g \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --mount "type=bind,src=$PWD/$study,dst=/study,readonly" \
  --mount "type=bind,src=$PWD/datasets/q12/geometry,dst=/assets,readonly" \
  --mount "type=bind,src=$PWD/runs/q12_mesh_preservation_v1,dst=/input,readonly" \
  --mount "type=bind,src=$PWD/$output,dst=/output" "$image" inspect_preservation.py
