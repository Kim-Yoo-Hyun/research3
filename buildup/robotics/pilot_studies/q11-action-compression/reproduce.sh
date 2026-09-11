#!/bin/sh
# Reproduce the frozen v1 into a new directory without changing the original bundle.
set -eu
cd /home/yoohyun/research3
q11_output=${1:?Supply a new absolute output directory}
case "$q11_output" in /*) ;; *) echo 'Output must be absolute' >&2; exit 2 ;; esac
if [ -e "$q11_output" ]; then echo 'Output already exists; refusing overwrite' >&2; exit 2; fi
q11_log_dir="$PWD/logs/q11_$(date -u +%Y%m%d_%H%M%S)"
mkdir -p "$q11_output" "$q11_log_dir"
docker image inspect research3-q11-readiness:v1 --format '{{json .}}' > "$q11_output/image.json"
timeout 7200 docker run --rm --name research3-q11-reproduction --network none --cpus 4 --memory 8g \
  --runtime=nvidia --gpus device=0 -e NVIDIA_DRIVER_CAPABILITIES=graphics,utility,compute \
  -e VK_ICD_FILENAMES=/opt/ManiSkill/docker/nvidia_icd.json \
  -e HF_HOME=/outputs/cache/huggingface -e HF_HUB_OFFLINE=1 -e TRANSFORMERS_OFFLINE=1 \
  -e MPLCONFIGDIR=/outputs/cache/mpl -e XDG_CACHE_HOME=/outputs/cache -e PYTHONDONTWRITEBYTECODE=1 \
  -v "$PWD/buildup/robotics/pilot_studies/q11-action-compression:/work:ro" \
  -v "$PWD/datasets/q11:/inputs:ro" -v "$q11_output:/outputs" -v "$q11_log_dir:/logs" \
  research3-q11-readiness:v1 python job.py
