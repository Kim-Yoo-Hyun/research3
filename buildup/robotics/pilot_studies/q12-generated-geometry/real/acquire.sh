#!/usr/bin/env bash
set -euo pipefail
cd /home/yoohyun/research3
stamp=$(date +%Y%m%d_%H%M%S)
log="logs/${stamp}_q12_real_assets.log"
mkdir -p logs
exec >"$log" 2>&1
trap 'rc=$?; echo "$rc" > "${log%.log}.exit"' EXIT
timeout 660 python3 buildup/robotics/pilot_studies/q12-generated-geometry/real/acquire.py
