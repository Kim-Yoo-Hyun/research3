#!/usr/bin/env bash
set -Eeuo pipefail

mode="${1:?pass replay or oracle}"
decision_step="${2:-80}"
if [[ "${mode}" != replay && "${mode}" != oracle ]]; then
    echo "invalid mode: ${mode}" >&2
    exit 2
fi
if [[ ! "${decision_step}" =~ ^[0-9]+$ ]]; then
    echo "invalid decision step: ${decision_step}" >&2
    exit 2
fi

workspace=/home/yoohyun/research3
study="${workspace}/buildup/robotics/pilot_studies/q17-evidence"
prior="${workspace}/runs/q17/evidence_20260928_count_case"
if [[ "${decision_step}" == 80 ]]; then
    run_key=""
    container_name="research3_q17_count_decision_${mode}_20260928"
else
    run_key="step${decision_step}_"
    container_name="research3_q17_count_decision_${run_key}${mode}_20260928"
fi
parity="${workspace}/runs/q17/evidence_20260928_count_decision_${run_key}replay"
output="${workspace}/runs/q17/evidence_20260928_count_decision_${run_key}${mode}"
mkdir -p "${output}"
extra_mounts=()
extra_args=()
if [[ "${mode}" == oracle ]]; then
    extra_mounts=(-v "${parity}:/parity:ro")
    extra_args=(--parity /parity)
fi

docker run --rm \
    --name "${container_name}" \
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
    -v "${study}/count_decision_probe.py:/work/count_decision_probe.py:ro" \
    -v "${prior}:/prior:ro" \
    "${extra_mounts[@]}" \
    -v "${output}:/output" \
    -w /sim \
    research3-q17-sim-eval:v1 \
    python /work/count_decision_probe.py --mode "${mode}" --decision-step "${decision_step}" --prior /prior --output /output "${extra_args[@]}"
