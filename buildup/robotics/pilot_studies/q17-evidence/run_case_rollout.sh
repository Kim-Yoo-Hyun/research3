#!/usr/bin/env bash
set -Eeuo pipefail

workspace=/home/yoohyun/research3
study="${workspace}/buildup/robotics/pilot_studies/q17-evidence"
output="${Q17_OUTPUT:-${workspace}/runs/q17/evidence_20260928_case_rollout}"
mkdir -p "${output}"
replay_mount=()
replay_args=()
if [[ -n "${Q17_INSTRUCTION_FROM:-}" ]]; then
    replay_mount=(-v "${Q17_INSTRUCTION_FROM}:/prior:ro")
    replay_args=(--instruction-from /prior)
fi
docker run --rm \
    --name research3_q17_case_rollout_20260928 \
    --label com.research3.study=q17-evidence \
    --network research3_q17_evidence_net_20260928 \
    --gpus device=0 --cpus 12 --memory 32g --shm-size 4g \
    -e NVIDIA_DRIVER_CAPABILITIES=all \
    -e VK_ICD_FILENAMES=/work/nvidia_egl_icd.json \
    -e ACTIVEARENA_VLA_ROOT=/vla \
    -v "${workspace}/datasets/q17/sim_assets:/sim/assets" \
    -v "${workspace}/external/q17-activearena-vla:/vla:ro" \
    -v "${study}/nvidia_egl_icd.json:/work/nvidia_egl_icd.json:ro" \
    -v "${study}/case_rollout.py:/work/case_rollout.py:ro" \
    "${replay_mount[@]}" \
    -v "${output}:/output" \
    -w /sim \
    research3-q17-sim-eval:v1 \
    python /work/case_rollout.py \
        --output /output \
        --host research3_q17_policy_bridge_20260928 \
        --count "${1:-1}" \
        --start-index "${2:-0}" \
        "${replay_args[@]}"
