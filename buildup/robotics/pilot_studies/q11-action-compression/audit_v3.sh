#!/bin/sh
set -eu
cd /home/yoohyun/research3
q11_audit_output=${1:?Supply a new absolute audit output directory}
case "$q11_audit_output" in /*) ;; *) exit 2 ;; esac
if [ -e "$q11_audit_output" ]; then echo 'Refusing existing audit output' >&2; exit 2; fi
mkdir -p "$q11_audit_output"
docker run --rm --name research3-q11-v3-audit --network none --cpus 2 --memory 4g \
 -e PYTHONDONTWRITEBYTECODE=1 \
 -v "$PWD/buildup/robotics/pilot_studies/q11-action-compression/v3:/work:ro" \
 -v "$PWD/buildup/robotics/pilot_studies/q11-action-compression:/baseline:ro" \
 -v "$PWD/datasets/q11:/inputs:ro" -v "$PWD/runs/q11_v3:/outputs:ro" \
 -v "$q11_audit_output:/audit" \
 sha256:fb9c530b6d664536b7665a3647c28459c729b250e5b1300cc47494820c388b5f python /baseline/audit_v3.py
