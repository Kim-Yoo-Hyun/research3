#!/usr/bin/env bash
set -eu
cd /home/yoohyun/research3
mode=${1:?prepare, infer or review}
case "$mode" in prepare|infer|review) ;; *) exit 2 ;; esac
stamp=$(date +%Y%m%d_%H%M%S)
owner=/home/yoohyun/research3/buildup/robotics/pilot_studies/q7-failure-source
log=logs/${stamp}_q7_repeat_${mode}.log
name=research3-q7-repeat-${mode}-${stamp}
image=research3-q7-vlm@sha256:0ceebb0f0fabbbfe4ab1d0ee7a29326ac99a210b51cc12faf0c6aa567d3f015e
gpu=()
if [ "$mode" = infer ]; then
  free_mib=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
  if [ "$free_mib" -lt 8192 ]; then
    printf 'Insufficient free GPU memory for unchanged BF16 comparison: %s MiB\n' "$free_mib" > "$log"
    printf '1\n' > "${log%.log}.exit"
    exit 1
  fi
  gpu=(--gpus device=GPU-90cacfcf-72fe-4b1c-1bd4-cffb389ff9ea)
fi
mkdir -p runs/q7/end_repeat
command=(timeout 1200s docker run --name "$name" "${gpu[@]}" --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 4 --memory 16g --memory-swap 16g --pids-limit 128 --user "$(id -u):$(id -g)" --tmpfs /tmp:rw,size=512m --mount "type=bind,src=$owner,dst=/study,readonly" --mount type=bind,src=/home/yoohyun/research3/runs/q7/prepared,dst=/prepared,readonly --mount type=bind,src=/home/yoohyun/research3/runs/q7/vlm,dst=/previous,readonly --mount type=bind,src=/home/yoohyun/research3/checkpoints/q7/smolvlm2-2.2b,dst=/model,readonly --mount type=bind,src=/home/yoohyun/research3/runs/q7/end_repeat,dst=/output "$image" /study/repeat_end.py "$mode")
{
  printf '\nEND repetition `%s` launched: `%s`; log/exit prefix `%s`.\n\n```bash\n' "$mode" "$name" "${log%.log}"
  printf '%q ' "${command[@]}"
  printf '\n```\n'
} >> "$owner/README.md"
set +e
"${command[@]}" > "$log" 2>&1
code=$?
set -e
printf '%s\n' "$code" > "${log%.log}.exit"
printf '\nEND repetition `%s` exit `%s`.\n' "$name" "$code" >> "$owner/README.md"
tail -n 5 "$log"
exit "$code"
