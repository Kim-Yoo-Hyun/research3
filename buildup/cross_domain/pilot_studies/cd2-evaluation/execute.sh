#!/usr/bin/env bash
# Invoke in tmux from the workspace root. Containers are retained for verified cleanup.
set -euo pipefail
cd /home/yoohyun/research3
run_id=${1:?Provide a unique run ID}
[[ "$run_id" =~ ^[0-9]{8}_[0-9]{6}$ ]]
study=$PWD/buildup/cross_domain/pilot_studies/cd2-evaluation
input=$PWD/runs/candidate_review/20260916
output=$PWD/runs/cd2-evaluation/$run_id
image_tag=research3-cd2-evaluation:v1
[[ ! -e "$output" ]]
mkdir -p "$output/verification" logs
trap 'code=$?; echo "$code" > "logs/${run_id}_cd2_job.exit"' EXIT

phase() {
    local name=$1
    shift
    printf '%q ' "$@" >> "$output/commands.txt"
    printf '\n' >> "$output/commands.txt"
    local code=0
    "$@" > "logs/${run_id}_cd2_${name}.log" 2>&1 || code=$?
    echo "$code" > "logs/${run_id}_cd2_${name}.exit"
    return "$code"
}

# Refuse to replace any pre-existing tag. A rerun needs a deliberate fresh recipe/tag.
if docker image inspect "$image_tag" >/dev/null 2>&1; then
    echo "Image tag already exists: $image_tag; use a deliberate new tag for another build." >&2
    exit 1
fi
phase build docker build --pull --no-cache --iidfile "$output/image.id" -t "$image_tag" "$study"
image_id=$(cat "$output/image.id")
docker image inspect "$image_id" > "$output/image.json"
common=(--user "$(id -u):$(id -g)" --network none --read-only --cap-drop ALL
        --security-opt no-new-privileges --cpus 2 --memory 1g --pids-limit 128
        --label research3.workspace="$PWD" --label research3.study=cd2-evaluation
        --label research3.run="$run_id" --mount "type=bind,src=$input,dst=/input,readonly")
phase create_run docker create --name "research3-cd2-${run_id}-run" --cidfile "$output/run.cid" \
    "${common[@]}" --mount "type=bind,src=$output,dst=/output" "$image_id" \
    /study/run.py --input /input --output /output
run_cid=$(cat "$output/run.cid")
run_exit=0
phase run docker start --attach "$run_cid" || run_exit=$?
docker inspect "$run_cid" > "$output/run.container.json"
[[ "$run_exit" == 0 ]]
[[ "$(docker inspect --format '{{.State.ExitCode}}' "$run_cid")" == 0 ]]

phase create_verify docker create --name "research3-cd2-${run_id}-verify" --cidfile "$output/verify.cid" \
    "${common[@]}" --mount "type=bind,src=$output,dst=/output,readonly" \
    --mount "type=bind,src=$output/verification,dst=/verification" "$image_id" \
    /study/verify.py --input /input --output /output --receipt /verification/receipt.json
verify_cid=$(cat "$output/verify.cid")
verify_exit=0
phase verify docker start --attach "$verify_cid" || verify_exit=$?
docker inspect "$verify_cid" > "$output/verify.container.json"
[[ "$verify_exit" == 0 ]]
[[ "$(docker inspect --format '{{.State.ExitCode}}' "$verify_cid")" == 0 ]]
echo "Completed observation and verification: $output"
