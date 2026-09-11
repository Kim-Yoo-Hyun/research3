#!/bin/sh
set -eu
cd /home/yoohyun/research3
docker run --rm --name research3-q11-v2-preflight --network none --cpus 2 --memory 2g \
  -e HF_HOME=/tmp/q11-hf -e HF_HUB_OFFLINE=1 -e TRANSFORMERS_OFFLINE=1 -e PYTHONDONTWRITEBYTECODE=1 \
  -v "$PWD/buildup/robotics/pilot_studies/q11-action-compression/v2:/work:ro" \
  -v "$PWD/datasets/q11:/inputs:ro" sha256:fb9c530b6d664536b7665a3647c28459c729b250e5b1300cc47494820c388b5f python preflight.py
