#!/bin/sh
set -eu
cd /home/yoohyun/research3
docker image inspect research3-q11-readiness:v1 --format '{{json .}}' > runs/q11_v1/image.json
timeout 7200 docker run --rm --name research3-q11-readiness --network none --cpus 4 --memory 8g \
  --runtime=nvidia --gpus device=0 -e NVIDIA_DRIVER_CAPABILITIES=graphics,utility,compute \
  -e VK_ICD_FILENAMES=/opt/ManiSkill/docker/nvidia_icd.json \
  -e HF_HOME=/outputs/cache/huggingface -e HF_HUB_OFFLINE=1 -e TRANSFORMERS_OFFLINE=1 \
  -e MPLCONFIGDIR=/outputs/cache/mpl -e XDG_CACHE_HOME=/outputs/cache -e PYTHONDONTWRITEBYTECODE=1 \
  -v "$PWD/buildup/robotics/pilot_studies/q11-action-compression:/work:ro" \
  -v "$PWD/datasets/q11:/inputs:ro" -v "$PWD/runs/q11_v1:/outputs" -v "$PWD/logs:/logs" \
  research3-q11-readiness:v1 python job.py
