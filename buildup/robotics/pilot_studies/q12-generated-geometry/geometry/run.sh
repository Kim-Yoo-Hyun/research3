#!/usr/bin/env bash
set -euo pipefail
cd /home/yoohyun/research3
study=buildup/robotics/pilot_studies/q12-generated-geometry/geometry
output=runs/q12_geometry_v1
test ! -e "$output"
test -f "$study/freeze.json"
stamp=$(date +%Y%m%d_%H%M%S)
log="logs/${stamp}_q12_geometry_v1.log"
mkdir -p logs
exec >"$log" 2>&1
trap 'rc=$?; echo "$rc" > "${log%.log}.exit"' EXIT
image=$(cat "$study/image_id.txt")
docker image inspect "$image" --format '{{.Id}}'
python - <<'PY'
from pathlib import Path
import hashlib,json
p=Path('buildup/robotics/pilot_studies/q12-generated-geometry/geometry')
r=json.loads((p/'freeze.json').read_text())
for name,h in r['files'].items():
    assert hashlib.sha256((p/name).read_bytes()).hexdigest()==h, name
assert not Path('runs/q12_geometry_v1').exists()
print('Frozen source identity verified')
PY
mkdir -p "$output"
started=$(date +%s)
common=(--rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges
  --user "$(id -u):$(id -g)" --cpus 4 --memory 4g --memory-swap 4g
  --tmpfs /tmp:rw,noexec,nosuid,size=128m
  --mount "type=bind,src=$PWD/$study,dst=/study,readonly"
  --mount "type=bind,src=$PWD/datasets/q12/geometry,dst=/assets,readonly")
timeout 1800 docker run "${common[@]}" --mount "type=bind,src=$PWD/$output,dst=/output" \
  "$image" audit.py --output /output/data
remaining=$((1800-$(date +%s)+started))
test "$remaining" -gt 0
mkdir "$output/audit"
timeout "$remaining" docker run "${common[@]}" \
  --mount "type=bind,src=$PWD/$output/data,dst=/input,readonly" \
  --mount "type=bind,src=$PWD/$output/audit,dst=/output" \
  "$image" verify.py --input /input --output /output
python - "$log" <<'PY'
from pathlib import Path
import hashlib,json,sys,datetime
out=Path('runs/q12_geometry_v1'); study=Path('buildup/robotics/pilot_studies/q12-generated-geometry/geometry')
files={str(p.relative_to(out)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.rglob('*')) if p.is_file()}
total=sum(r['bytes'] for r in files.values()); assert total <= 128*1024**2
r={'completed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':'bash '+str(study/'run.sh'),
   'cwd':'/home/yoohyun/research3','image_id':(study/'image_id.txt').read_text().strip(),
   'freeze_sha256':hashlib.sha256((study/'freeze.json').read_bytes()).hexdigest(),
   'log':sys.argv[1],'output_bytes_before_receipt':total,'files':files}
(out/'execution.json').write_text(json.dumps(r,indent=2)+'\n')
print('Verification decision:',json.loads((out/'audit/verification.json').read_text())['decision'])
PY
