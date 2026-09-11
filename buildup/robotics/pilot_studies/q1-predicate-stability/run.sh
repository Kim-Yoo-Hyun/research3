#!/bin/sh
set -eu
cd /home/yoohyun/research3
script=${1:-smoke.py}
shift || true
docker run --rm --name research3-q1-predicate --network "${Q1_NETWORK:-none}" --cpus 4 --memory 12g \
  --runtime=nvidia --gpus device=0 -e NVIDIA_DRIVER_CAPABILITIES=graphics,utility,compute \
  -e VK_ICD_FILENAMES=/opt/ManiSkill/docker/nvidia_icd.json \
  -e HOME=/cache -e MPLCONFIGDIR=/cache/mpl -e CUDA_VISIBLE_DEVICES=0 \
  -v "$PWD/buildup/robotics/pilot_studies/q1-predicate-stability:/work:ro" \
  -v "$PWD/datasets/q8:/inputs:ro" -v "$PWD/runs/q1_v3:/outputs" \
  -v "$PWD/runs/q1_v3/cache:/cache" \
  research3-q1-predicate:v3 python "$script" "$@"
