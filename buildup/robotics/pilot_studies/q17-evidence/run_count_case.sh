#!/usr/bin/env bash
set -Eeuo pipefail

workspace=/home/yoohyun/research3
study="${workspace}/buildup/robotics/pilot_studies/q17-evidence"
output="${workspace}/runs/q17/evidence_20260928_count_case"
mkdir -p "${output}"
docker run --rm \
    --name research3_q17_count_case_20260928 \
    --label com.research3.study=q17-evidence \
    --network research3_q17_evidence_net_20260928 \
    --gpus device=0 --cpus 12 --memory 32g --shm-size 4g \
    -e NVIDIA_DRIVER_CAPABILITIES=all \
    -e VK_ICD_FILENAMES=/work/nvidia_egl_icd.json \
    -e ACTIVEARENA_VLA_ROOT=/vla \
    -v "${workspace}/datasets/q17/sim_assets:/sim/assets" \
    -v "${workspace}/datasets/q17/rmbench_objects/005_button:/sim/assets/objects/005_button:ro" \
    -v "${workspace}/datasets/q17/rmbench_objects/006_check_button:/sim/assets/objects/006_check_button:ro" \
    -v "${workspace}/external/q17-activearena-vla:/vla:ro" \
    -v "${study}/nvidia_egl_icd.json:/work/nvidia_egl_icd.json:ro" \
    -v "${study}/count_case_rollout.py:/work/count_case_rollout.py:ro" \
    -v "${output}:/output" \
    -w /sim \
    research3-q17-sim-eval:v1 \
    python /work/count_case_rollout.py
