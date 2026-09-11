#!/usr/bin/env bash
set -euo pipefail
cd /home/yoohyun/research3
study=/home/yoohyun/research3/buildup/robotics/pilot_studies/q12-generated-geometry
image_id=$(cat "$study/model/image_id.txt")
output=/home/yoohyun/research3/runs/q12_completion_reference_v1
[[ ! -e "$output" ]]
mkdir -p "$output/predictions" "$output/verification"
stamp=$(date +%Y%m%d_%H%M%S)
log="logs/${stamp}_q12_completion_reference.log"
input_mounts=()
for input_index in 0 1 2 3; do
  input_mounts+=(-v "/home/yoohyun/research3/runs/q12_input_v1/data/${input_index}_sampled.xyz:/inputs/${input_index}_sampled.xyz:ro")
done
active_container=''
cleanup() {
  if [[ -n "$active_container" ]]; then docker stop -t 5 "$active_container" >/dev/null 2>&1 || true; fi
}
trap cleanup EXIT INT TERM
set +e
(
  set -e
  for repeat in 0 1; do
    active_container="research3-q12-completion-reference-$repeat"
    trap cleanup EXIT INT TERM
    timeout --signal=TERM --kill-after=20 600 docker run --rm --name "$active_container" --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 4 --memory 4g --memory-swap 4g --pids-limit 128 --ulimit fsize=16777216:16777216 --user "$(id -u):$(id -g)" --tmpfs /tmp:rw,size=64m -v "$study/model:/study/model:ro" -v /home/yoohyun/research3/datasets/q12/3dsgrasp_model.pth:/checkpoint/model.pth:ro "${input_mounts[@]}" -v "$output/predictions:/output:rw" "$image_id" /study/model/predict.py --repeat "$repeat"
    active_container=''
  done
  active_container=research3-q12-completion-reference-verify
  timeout --signal=TERM --kill-after=20 300 docker run --rm --name "$active_container" --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 4 --memory 4g --memory-swap 4g --pids-limit 128 --ulimit fsize=16777216:16777216 --user "$(id -u):$(id -g)" --tmpfs /tmp:rw,size=64m -v "$study/model:/study/model:ro" "${input_mounts[@]}" -v /home/yoohyun/research3/datasets/q12/subset/gt:/gt:ro -v "$output/predictions:/predictions:ro" -v "$output/verification:/verification:rw" "$image_id" /study/model/verify_completion.py
  active_container=''
) > "$log" 2>&1
q12_exit=$?
printf '%s\n' "$q12_exit" > "${log%.log}.exit"
exit "$q12_exit"
