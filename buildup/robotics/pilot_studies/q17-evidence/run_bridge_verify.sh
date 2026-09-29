#!/usr/bin/env bash
set -Eeuo pipefail

workspace=/home/yoohyun/research3
study="${workspace}/buildup/robotics/pilot_studies/q17-evidence"
mkdir -p "${workspace}/runs/q17/evidence_20260928_server_verify"
docker run --rm \
    --name research3_q17_bridge_verify_20260928 \
    --label com.research3.study=q17-evidence \
    --gpus device=0 --network none --cpus 8 --memory 32g \
    -e ACTIVEARENA_VLA_BASE_VLM=/models/Qwen3-VL-2B-Instruct \
    -v "${workspace}/external/q17-activearena-vla:/source:ro" \
    -v "${study}:/work:ro" \
    -v "${workspace}/datasets/q17/activearena/check_block_color:/dataset:ro" \
    -v "${workspace}/datasets/q17/model/qwen3-vl-2b:/models/Qwen3-VL-2B-Instruct:ro" \
    -v "${workspace}/datasets/q17/model/oft_subtask_action_12_ws:/models/policy:ro" \
    -v "${workspace}/runs/q17/evidence_20260928_decision_inputs_v2:/input:ro" \
    -v "${workspace}/runs/q17/evidence_20260928_policy:/reference:ro" \
    -v "${workspace}/runs/q17/evidence_20260928_server_verify:/output" \
    research3-q17-policy:v3 /work/verify_policy_server.py
