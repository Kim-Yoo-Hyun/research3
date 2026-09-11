#!/bin/sh
set -eu
cd /home/yoohyun/research3
docker build --pull --no-cache --progress plain -t research3-q11-pilot:v2 -f buildup/robotics/pilot_studies/q11-action-compression/v2/Dockerfile .
