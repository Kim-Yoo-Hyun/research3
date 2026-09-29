#!/usr/bin/env bash
# Host orchestration only. All scientific work runs inside the pinned Docker image.
set -euo pipefail
cd /home/yoohyun/research3
run_id="${1:?Pass a new run ID}"
for stage in goal_prepare run goal_verify goal_analyze; do
    python3 buildup/robotics/pilot_studies/q4-planning/orchestrate.py "$stage" --run-id "$run_id"
done
