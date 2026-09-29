#!/usr/bin/env bash
set -euo pipefail
cd /home/yoohyun/research3
study=buildup/robotics/pilot_studies/q12-generated-geometry/real
input=datasets/q12/bop_v1
output=runs/q12_real_input_v1
test -f "$study/freeze.json"
test ! -e "$output"
stamp=$(date +%Y%m%d_%H%M%S)
log="logs/${stamp}_q12_real_input.log"
mkdir -p logs
exec >"$log" 2>&1
container="research3-q12-real-input-${stamp}"
finish() {
  rc=$?
  if docker container inspect "$container" >/dev/null 2>&1; then docker stop -t 2 "$container" >/dev/null; fi
  echo "$rc" > "${log%.log}.exit"
}
trap finish EXIT
mkdir -p "$output/data" "$output/audit"
image=$(cat "$study/image_id.txt")
test "$(docker image inspect "$image" --format '{{.Id}}')" = "$image"
limits=(--rm --name "$container" --network none --read-only --cap-drop ALL --security-opt no-new-privileges
  --cpus 4 --memory 4g --memory-swap 4g --pids-limit 128 --ulimit fsize=134217728:134217728
  --user "$(id -u):$(id -g)" --tmpfs /tmp:rw,noexec,nosuid,size=64m)
mounts=(-v "$PWD/$study:/study:ro" -v "$PWD/$input:/input:ro")
SECONDS=0
timeout 1800 docker run "${limits[@]}" "${mounts[@]}" -v "$PWD/$output/data:/output:rw" \
  "$image" /study/audit.py --data /input --output /output
remaining=$((1800-SECONDS))
test "$remaining" -gt 0
timeout "$remaining" docker run "${limits[@]}" "${mounts[@]}" \
  -v "$PWD/$output/data:/producer:ro" -v "$PWD/$output/audit:/output:rw" \
  "$image" /study/verify.py --data /input --input /producer --output /output
elapsed=$SECONDS
python - "$study" "$input" "$output" "$image" "$elapsed" "$log" <<'PY'
import hashlib,json,sys
from pathlib import Path
study,source,output=map(Path,sys.argv[1:4]);image,elapsed,log=sys.argv[4:]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
frozen=json.loads((study/'freeze.json').read_text())
for name,h in frozen['files'].items():assert sha(study/name)==h, ('INVALID_INTEGRITY',name)
assets=json.loads((study/'assets.json').read_text())
for row in assets['files']:
 p=source/row['destination'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'], ('INVALID_INTEGRITY',str(p))
verification=json.loads((output/'audit/verification.json').read_text())
assert verification['status']=='VERIFIED' and verification['denominator']==10
assert int(elapsed)<=1800
inventory=[{'path':str(p.relative_to(output)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(output.rglob('*')) if p.is_file()]
assert sum(x['bytes'] for x in inventory)<=134217728
record={'status':'completed','decision':verification['decision'],'physical_admission':False,'image_id':image,
 'cpu':4,'ram_bytes':4294967296,'device':'cpu','seed':None,'network':'none','elapsed_seconds':int(elapsed),
 'cwd':str(Path.cwd()),'command':'bash '+str(study/'run.sh'),'log':log,
 'source_mount':str(study)+':/study:ro','dataset_mount':str(source)+':/input:ro',
 'producer_mount':str(output/'data')+':/output:rw','verifier_input_mount':str(output/'data')+':/producer:ro',
 'verifier_output_mount':str(output/'audit')+':/output:rw',
 'freeze_sha256':sha(study/'freeze.json'),'assets_sha256':sha(study/'assets.json'),
 'input_hashes_unchanged':True,'files':inventory}
(output/'execution.json').write_text(json.dumps(record,indent=2)+'\n')
assert sum(p.stat().st_size for p in output.rglob('*') if p.is_file())<=134217728
print(json.dumps({'status':'completed','decision':verification['decision'],'files':len(inventory)}))
PY
