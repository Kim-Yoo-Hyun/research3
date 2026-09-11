#!/bin/sh
set -eu
cd /home/yoohyun/research3
q11_check_output=${1:?New absolute output directory required}
case "$q11_check_output" in /*) ;; *) exit 2 ;; esac
if [ -e "$q11_check_output" ]; then echo 'Refusing existing output' >&2; exit 2; fi
mkdir -p "$q11_check_output"
set --
for q11_cal_seed in 1000 1001 1002 1003 1004 1005 1006 1007; do
 set -- "$@" -v "$PWD/runs/q11_v2/seed_${q11_cal_seed}:/calibration/seed_${q11_cal_seed}:ro"
done
docker run --rm --name research3-q11-v3-check --network none --cpus 2 --memory 4g \
 -e PYTHONDONTWRITEBYTECODE=1 -e HF_HOME=/outputs/cache -e HF_HUB_OFFLINE=1 -e TRANSFORMERS_OFFLINE=1 \
 -v "$PWD/buildup/robotics/pilot_studies/q11-action-compression/v3:/work:ro" \
 -v "$PWD/datasets/q11:/inputs:ro" -v "$q11_check_output:/outputs" "$@" \
 sha256:fb9c530b6d664536b7665a3647c28459c729b250e5b1300cc47494820c388b5f python precheck.py
