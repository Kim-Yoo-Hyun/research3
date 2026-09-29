#!/usr/bin/env bash
# Run from tmux for build/execution. Retain containers until evidence-backed cleanup.
set -euo pipefail
cd /home/yoohyun/research3
run_id=${1:?unique run ID}
phase=${2:?build, inspect, diagnose, run, verify, or analyze}
image_tag=${3:-research3-cd2-episodes:v1}
[[ "$run_id" =~ ^[0-9]{8}_[0-9]{6}$ ]]
study=$PWD/buildup/cross_domain/pilot_studies/cd2-evaluation/episodes
input=$PWD/runs/cd2-review/20260917
output=$PWD/runs/cd2-episodes/$run_id
mkdir -p "$output/verification" logs
trap 'code=$?; echo "$code" > "logs/${run_id}_cd2_ep_${phase}.exit"' EXIT
record() {
    printf '%q ' "$@" >> "$output/commands.txt"
    printf '\n' >> "$output/commands.txt"
    "$@"
}
if [[ "$phase" == build ]]; then
    [[ ! -e "$output/image.id" ]]
    if docker image inspect "$image_tag" >/dev/null 2>&1; then
        echo "Refusing existing image tag: $image_tag" >&2
        exit 42
    fi
    record docker build --pull --iidfile "$output/image.id" -t "$image_tag" "$study"
    exit 0
fi
image_id=$(cat "$output/image.id")
docker image inspect "$image_id" > "$output/image.json"
case "$phase" in
    inspect) entry=inspect_input.py ;;
    diagnose) entry=diagnose_input.py ;;
    analyze) entry=analyze.py ;;
    run) entry=run.py ;;
    verify) entry=verify.py ;;
    *) exit 2 ;;
esac
[[ ! -e "$output/$phase.cid" ]]
common=(--user "$(id -u):$(id -g)" --network none --read-only --cap-drop ALL
        --security-opt no-new-privileges --cpus 2 --memory 1g --pids-limit 128
        --label research3.workspace="$PWD" --label research3.study=cd2-episodes
        --label research3.run="$run_id" --label research3.phase="$phase"
        --mount "type=bind,src=$input,dst=/input,readonly"
        --mount "type=bind,src=$study,dst=/study,readonly")
if [[ "$phase" == verify ]]; then
    common+=(--mount "type=bind,src=$output,dst=/output,readonly"
             --mount "type=bind,src=$output/verification,dst=/verification")
else
    common+=(--mount "type=bind,src=$output,dst=/output")
fi
record docker create --name "research3-cd2-ep-${run_id}-${phase}" --cidfile "$output/$phase.cid" \
    "${common[@]}" "$image_id" "/study/$entry"
cid=$(cat "$output/$phase.cid")
code=0
record docker start --attach "$cid" || code=$?
docker inspect "$cid" > "$output/$phase.container.json"
[[ "$code" == 0 ]]
[[ "$(docker inspect --format '{{.State.ExitCode}}' "$cid")" == 0 ]]
