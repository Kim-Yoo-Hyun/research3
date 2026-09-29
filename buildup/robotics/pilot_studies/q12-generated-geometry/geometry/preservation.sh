#!/usr/bin/env bash
set -euo pipefail
cd /home/yoohyun/research3
study=buildup/robotics/pilot_studies/q12-generated-geometry/geometry
output=runs/q12_mesh_preservation_v1
test ! -e "$output"
stamp=$(date +%Y%m%d_%H%M%S)
log="logs/${stamp}_q12_preservation.log"
mkdir -p logs
exec >"$log" 2>&1
trap 'rc=$?; echo "$rc" > "${log%.log}.exit"' EXIT
mkdir -p "$output/data" "$output/audit"
image=$(cat "$study/image_id.txt")
started=$(date -u +%Y-%m-%dT%H:%M:%SZ)
common=(--rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges
  --user "$(id -u):$(id -g)" --cpus 4 --memory 4g --memory-swap 4g
  --tmpfs /tmp:rw,noexec,nosuid,size=128m
  --mount "type=bind,src=$PWD/$study,dst=/study,readonly"
  --mount "type=bind,src=$PWD/datasets/q12/geometry,dst=/assets,readonly")
deadline=$((SECONDS + 1800))
timeout "$((deadline - SECONDS))" docker run --name "research3-q12-preservation-data-$stamp" "${common[@]}" \
  --mount "type=bind,src=$PWD/runs/q12_geometry_v1,dst=/old,readonly" \
  --mount "type=bind,src=$PWD/$output/data,dst=/output" "$image" preserve.py
remaining=$((deadline - SECONDS))
test "$remaining" -gt 0
timeout "$remaining" docker run --name "research3-q12-preservation-audit-$stamp" "${common[@]}" \
  --mount "type=bind,src=$PWD/$output/data,dst=/input,readonly" \
  --mount "type=bind,src=$PWD/$output/audit,dst=/output" "$image" verify_preservation.py
python3 - "$study" "$output" "$image" "$log" "$started" <<'PY'
import datetime
import hashlib
import json
from pathlib import Path
import sys
study, output = map(Path, sys.argv[1:3])
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
files = {str(p.relative_to(output)): {'bytes': p.stat().st_size, 'sha256': digest(p)}
         for p in sorted(output.rglob('*')) if p.is_file()}
total = sum(x['bytes'] for x in files.values())
assert total <= 134217728
receipt = {'id': 'q12-mesh-preservation-v1', 'image_id': sys.argv[3], 'device': 'cpu',
           'started_at_utc': sys.argv[5], 'completed_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'log': sys.argv[4], 'working_directory': str(Path.cwd()),
           'launcher': str(study/'preservation.sh'), 'launcher_sha256': digest(study/'preservation.sh'),
           'freeze_sha256': digest(study/'preservation_freeze.json'),
           'resources': {'cpus': 4, 'ram_bytes': 4294967296, 'runtime_seconds_cap': 1800, 'network': 'none'},
           'files': files, 'total_bytes_before_execution_receipt': total,
           'decision': json.loads((output/'audit/verification.json').read_text())['decision']}
(output/'execution.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps({'decision': receipt['decision'], 'files': len(files), 'bytes': total}))
PY
