#!/usr/bin/env bash
set -Eeuo pipefail

workspace=/home/yoohyun/research3
study="${workspace}/buildup/robotics/pilot_studies/q17-evidence"
output="${workspace}/runs/q17/evidence_20260928_scene_smoke"
mkdir -p "${output}"
docker run --rm \
    --name research3_q17_scene_smoke_20260928 \
    --label com.research3.study=q17-evidence \
    --gpus device=0 --network none --cpus 8 --memory 28g --shm-size 4g \
    -e NVIDIA_DRIVER_CAPABILITIES=all \
    -e VK_ICD_FILENAMES=/work/nvidia_egl_icd.json \
    -e ACTIVEARENA_DEBUG_TIMING=1 \
    -v "${workspace}/datasets/q17/sim_assets:/sim/assets" \
    -v "${study}/nvidia_egl_icd.json:/work/nvidia_egl_icd.json:ro" \
    -v "${study}/sim_scene_smoke.py:/work/sim_scene_smoke.py:ro" \
    -v "${output}:/output" \
    research3-q17-sim:v3 \
    python /work/sim_scene_smoke.py --seed 100000 --output /output
