#!/bin/sh
set -eu
cd /home/yoohyun/research3
q11_output=${1:?Supply a new absolute output directory}
case "$q11_output" in /*) ;; *) exit 2 ;; esac
if [ -e "$q11_output" ]; then echo 'Refusing existing output' >&2; exit 2; fi
q11_log_dir="$PWD/logs/q11_v3_$(date -u +%Y%m%d_%H%M%S)"
mkdir -p "$q11_output" "$q11_log_dir"
docker image inspect sha256:fb9c530b6d664536b7665a3647c28459c729b250e5b1300cc47494820c388b5f --format '{{json .}}' > "$q11_output/image.json"
printf '%s\n' "$q11_log_dir" > "$q11_output/log_path.txt"
timeout 7200 docker run --rm --name research3-q11-v3-pilot --network none --cpus 4 --memory 8g \
 --runtime=nvidia --gpus device=0 -e NVIDIA_DRIVER_CAPABILITIES=graphics,utility,compute \
 -e VK_ICD_FILENAMES=/opt/ManiSkill/docker/nvidia_icd.json \
 -e HF_HOME=/outputs/cache/huggingface -e HF_HUB_OFFLINE=1 -e TRANSFORMERS_OFFLINE=1 \
 -e MPLCONFIGDIR=/outputs/cache/mpl -e XDG_CACHE_HOME=/outputs/cache -e PYTHONDONTWRITEBYTECODE=1 \
 -v "$PWD/buildup/robotics/pilot_studies/q11-action-compression/v3:/work:ro" \
 -v "$PWD/buildup/robotics/pilot_studies/q11-action-compression:/baseline:ro" \
 -v "$PWD/datasets/q11:/inputs:ro" -v "$q11_output:/outputs" -v "$q11_log_dir:/logs" \
 sha256:fb9c530b6d664536b7665a3647c28459c729b250e5b1300cc47494820c388b5f python job.py
