#!/usr/bin/env bash
set -u
cd /home/yoohyun/research3
if docker image inspect research3-q4-planning:v1 >/dev/null 2>&1; then
    echo 'Image tag already exists. For a rebuild use the Dockerfile with a new project-specific tag.' >&2
    exit 2
fi
stamp=$(date +%Y%m%d_%H%M%S)
log="logs/${stamp}_q4_build"
docker build --pull --progress plain -t research3-q4-planning:v1 buildup/robotics/pilot_studies/q4-planning > "${log}.log" 2>&1
code=$?
printf '%s\n' "$code" > "${log}.exit"
exit "$code"
