#!/bin/sh
set -eu
cd /home/yoohyun/research3
docker build --pull --no-cache -f buildup/robotics/pilot_studies/q8-recoverability/Dockerfile -t research3-q8-audit:v1 .
docker image inspect research3-q8-audit:v1 --format '{{.Id}}' > runs/q8/image.txt
