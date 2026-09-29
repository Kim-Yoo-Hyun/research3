#!/usr/bin/env bash
set -eu
cd /home/yoohyun/research3
mode=${1:?prepare or score or verify or aggregate}
stamp=$(date +%Y%m%d_%H%M%S)
owner=/home/yoohyun/research3/buildup/robotics/pilot_studies/q7-failure-source
name=research3-q7-${mode}-${stamp}
log=logs/${stamp}_q7_${mode}.log
mkdir -p runs/q7
args=()
case "$mode" in
  prepare) args=(/study/observe.py prepare --output /output/prepared) ;;
  score) args=(/study/observe.py score --prepared /output/prepared --output /output/scored) ;;
  aggregate) args=(/study/aggregate.py) ;;
  verify) args=(/study/verify.py --prepared /output/prepared --scored /output/scored --output /output/verification.json) ;;
  *) exit 2 ;;
esac
command=(timeout 300s docker run --name "$name" --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 2 --memory 2g --pids-limit 64 --user "$(id -u):$(id -g)" --mount "type=bind,src=$owner,dst=/study,readonly" --mount type=bind,src=/home/yoohyun/research3/datasets/q7-ur5,dst=/input,readonly --mount type=bind,src=/home/yoohyun/research3/external/q7-sources,dst=/metadata,readonly --mount type=bind,src=/home/yoohyun/research3/runs/q7,dst=/output research3-q7-failure-source:v1 "${args[@]}")
{
  printf '\nRuntime `%s`: `%s`; log `%s`.\n\n```bash\n' "$mode" "$name" "$log"
  printf '%q ' "${command[@]}"
  printf '\n```\n'
} >> "$owner/README.md"
set +e
"${command[@]}" > "$log" 2>&1
code=$?
set -e
printf '%s\n' "$code" > "${log%.log}.exit"
printf '\nRuntime `%s` exit `%s`; status `%s`.\n' "$name" "$code" "$([ "$code" = 0 ] && printf 'completed; needs interpretation' || printf 'failed')" >> "$owner/README.md"
tail -c 6000 "$log"
exit "$code"
