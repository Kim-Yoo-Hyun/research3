#!/bin/sh
set -eu
cd /home/yoohyun/research3
script=${1:-smoke.py}
docker run --rm --name research3-q8-audit --network none --cpus 4 --memory 8g \
  --runtime=nvidia --gpus device=0 -e NVIDIA_DRIVER_CAPABILITIES=graphics,utility,compute \
  -e VK_ICD_FILENAMES=/opt/ManiSkill/docker/nvidia_icd.json \
  -e Q8_REPEAT="${Q8_REPEAT:-0}" \
  -e HOME=/tmp -e MPLCONFIGDIR=/tmp/mpl \
  -v "$PWD/buildup/robotics/pilot_studies/q8-recoverability:/work:ro" \
  -v "$PWD/datasets/q8:/inputs:ro" -v "$PWD/runs/q8:/outputs" \
  research3-q8-audit:v1 python "$script"
