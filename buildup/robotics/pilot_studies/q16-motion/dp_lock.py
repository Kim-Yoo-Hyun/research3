"""Export the complete installed dependency lock from the corrected Docker image."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

source=Path('/recipe/installed.dp.lock')
target=Path('/output/installed.v2.lock')
assert source.is_file() and not target.exists()
subprocess.run(['python','-m','pip','check'],check=True)
shutil.copy2(source,target)
sha=hashlib.sha256(target.read_bytes()).hexdigest()
print(json.dumps(dict(path=str(target),bytes=target.stat().st_size,sha256=sha)),flush=True)
