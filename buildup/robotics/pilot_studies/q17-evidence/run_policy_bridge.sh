#!/usr/bin/env bash
set -Eeuo pipefail

workspace=/home/yoohyun/research3
study="${workspace}/buildup/robotics/pilot_studies/q17-evidence"
docker run --rm \
    --name research3_q17_policy_bridge_20260928 \
    --label com.research3.study=q17-evidence \
    --network research3_q17_evidence_net_20260928 \
    --gpus device=0 --cpus 8 --memory 32g --shm-size 4g \
    -e ACTIVEARENA_VLA_BASE_VLM=/models/Qwen3-VL-2B-Instruct \
    -v "${workspace}/external/q17-activearena-vla:/source:ro" \
    -v "${study}:/work:ro" \
    -v "${workspace}/datasets/q17/model/qwen3-vl-2b:/models/Qwen3-VL-2B-Instruct:ro" \
    -v "${workspace}/datasets/q17/model/oft_subtask_action_12_ws:/models/policy:ro" \
    research3-q17-policy:v3 /work/policy_server.py --port 7980
