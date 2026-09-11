#!/bin/sh
set -eu
cd /home/yoohyun/research3
docker build --pull --no-cache -f buildup/robotics/pilot_studies/q1-predicate-stability/Dockerfile -t research3-q1-predicate:v3 .
docker image inspect research3-q1-predicate:v3 --format '{{.Id}}' > runs/q1_v3/image.txt
