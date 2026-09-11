#!/usr/bin/env bash
set -euo pipefail
cd /home/yoohyun/research3
stamp=$(date +%Y%m%d_%H%M%S)
log="logs/${stamp}_q12_inputs.log"
set +e
timeout 1800 python3 buildup/robotics/pilot_studies/q12-generated-geometry/prepare_inputs.py > "$log" 2>&1
status=$?
printf '%s\n' "$status" > "${log%.log}.exit"
exit "$status"
