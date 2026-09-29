#!/usr/bin/env bash
set -euo pipefail
cd /home/yoohyun/research3
stamp=$(date +%Y%m%d_%H%M%S)
job="research3-q9-surface-${stamp}"
output="runs/q9/surface_${stamp}"
log="logs/${stamp}_q9_surface.log"
mkdir -p "$output" logs
printf 'container=%s\noutput=%s\nlog=%s\n' "$job" "$output" "$log"
set +e
timeout 300s docker run --name "$job" --network none --read-only --cap-drop ALL \
  --security-opt no-new-privileges --cpus 2 --memory 4g --pids-limit 64 \
  --user "$(id -u):$(id -g)" --entrypoint python \
  --mount type=bind,src=/home/yoohyun/research3/datasets/q9/env1,dst=/input,readonly \
  --mount type=bind,src=/home/yoohyun/research3/buildup/robotics/pilot_studies/q9-refresh,dst=/study,readonly \
  --mount "type=bind,src=/home/yoohyun/research3/$output,dst=/output" \
  sha256:7eca5af889f3bd97fb795f74f86bd6832aa3d2b2887ba283ca83503b6f109df5 \
  /study/surface.py --input /input/env.pkl --regions /study/regions.json --output /output/result > "$log" 2>&1
result=$?
set -e
printf '%s\n' "$result" > "logs/${stamp}_q9_surface.exit"
exit "$result"
