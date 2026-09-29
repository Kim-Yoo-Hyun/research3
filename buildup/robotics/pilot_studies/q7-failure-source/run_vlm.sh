#!/usr/bin/env bash
set -eu
cd /home/yoohyun/research3
mode=${1:-infer}
stamp=$(date +%Y%m%d_%H%M%S)
owner=/home/yoohyun/research3/buildup/robotics/pilot_studies/q7-failure-source
log=logs/${stamp}_q7_vlm_${mode}.log
name=research3-q7-vlm-${mode}-${stamp}
args=()
gpu=()
case "$mode" in
 infer)
    free_mib=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
    if [ "$free_mib" -ge 8192 ]; then
      device=cuda
      gpu=(--gpus device=GPU-90cacfcf-72fe-4b1c-1bd4-cffb389ff9ea)
    else
      device=cpu
    fi
    args=(/study/vlm.py --device "$device" --output /output/vlm)
    ;;
 check) args=(/study/check_inputs.py) ;;
 review) args=(/study/review_vlm.py) ;;
 *) exit 2 ;;
esac
command=(timeout 2400s docker run --name "$name" "${gpu[@]}" --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 4 --memory 16g --memory-swap 16g --pids-limit 128 --user "$(id -u):$(id -g)" --tmpfs /tmp:rw,size=512m --mount "type=bind,src=$owner,dst=/study,readonly" --mount type=bind,src=/home/yoohyun/research3/runs/q7/prepared,dst=/prepared,readonly --mount type=bind,src=/home/yoohyun/research3/checkpoints/q7/smolvlm2-2.2b,dst=/model,readonly --mount type=bind,src=/home/yoohyun/research3/runs/q7,dst=/output research3-q7-vlm:v1 "${args[@]}")
{
 printf '\nVLM `%s` launched: `%s`; log/exit prefix `%s`.\n\n```bash\n' "$mode" "$name" "${log%.log}"
 printf '%q ' "${command[@]}"
 printf '\n```\n'
} >> "$owner/README.md"
set +e
"${command[@]}" > "$log" 2>&1
code=$?
set -e
printf '%s\n' "$code" > "${log%.log}.exit"
printf '\nVLM `%s` exit `%s`.\n' "$name" "$code" >> "$owner/README.md"
tail -n 7 "$log"
exit "$code"
