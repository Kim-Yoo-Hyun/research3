#!/usr/bin/env bash
set -euo pipefail
cd /home/yoohyun/research3
study=buildup/robotics/pilot_studies/q12-generated-geometry/real
stamp=$(date +%Y%m%d_%H%M%S)
log="logs/${stamp}_q12_real_preflight.log"
output="runs/q12_real_preflight_${stamp}"
mkdir -p logs
exec >"$log" 2>&1
trap 'rc=$?; echo "$rc" > "${log%.log}.exit"' EXIT
mkdir "$output"
image=$(cat "$study/image_id.txt")
timeout 600 docker run --rm --name "research3-q12-real-preflight-${stamp}" \
  --network none --read-only --cap-drop ALL --security-opt no-new-privileges \
  --cpus 4 --memory 4g --memory-swap 4g --pids-limit 128 --user "$(id -u):$(id -g)" \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  -v "$PWD/$study:/study:ro" -v "$PWD/$output:/output:rw" \
  "$image" /study/preflight.py --root /output
if test ! -e "$study/freeze.json"; then cp "$output/preflight.json" "$study/preflight.json"; fi
echo "SYNTHETIC_ONLY_VERIFIED $output"
