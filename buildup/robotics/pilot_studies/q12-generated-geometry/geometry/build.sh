#!/usr/bin/env bash
set -euo pipefail
cd /home/yoohyun/research3
study=buildup/robotics/pilot_studies/q12-generated-geometry/geometry
test ! -e "$study/freeze.json"
test ! -e "$study/image_id.txt"
stamp=$(date +%Y%m%d_%H%M%S)
log="logs/${stamp}_q12_geometry_build.log"
mkdir -p logs
exec >"$log" 2>&1
trap 'rc=$?; echo "$rc" > "${log%.log}.exit"' EXIT
timeout 1200 docker build --network=default --pull --progress=plain -t research3-q12-geometry:v1 "$study"
docker image inspect research3-q12-geometry:v1 --format '{{.Id}}' > "$study/image_id.txt"
docker image inspect research3-q12-geometry:v1 --format '{{.Size}}' > "$study/image_bytes.txt"
image=$(cat "$study/image_id.txt")
timeout 60 docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 4 --memory 4g --memory-swap 4g --tmpfs /tmp:rw,noexec,nosuid,size=64m "$image" -c 'import importlib.metadata as m, json, sys, pybullet; print(json.dumps({"python":sys.version,"packages":{d.metadata["Name"]:d.version for d in m.distributions()},"pybullet_api":pybullet.getAPIVersion()},indent=2))' > "$study/environment.txt"
echo BUILD_AND_IMPORT_COMPLETE
