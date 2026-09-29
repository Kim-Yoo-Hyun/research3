#!/usr/bin/env bash
set -euo pipefail
cd /home/yoohyun/research3
stamp=$(date +%Y%m%d_%H%M%S)
log="logs/${stamp}_q12_geometry_assets.log"
mkdir -p logs
exec >"$log" 2>&1
trap 'rc=$?; echo "$rc" > "${log%.log}.exit"' EXIT
timeout 900 python buildup/robotics/pilot_studies/q12-generated-geometry/geometry/acquire.py
