"""Validate and extract the pinned RoboTwin objects archive inside Docker."""

import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import tempfile
import zipfile


ASSETS = Path("/sim/assets")
ARCHIVE = ASSETS / ".downloads/objects.zip"
EXPECTED_SHA256 = "6aa56b3cf1e1064f7c809308144da36b00815f8b137fef2d7e4de856f8becf27"
EXPECTED_SIZE = 3737778549


def main():
    if ARCHIVE.stat().st_size != EXPECTED_SIZE:
        raise RuntimeError("objects.zip byte size does not match the pinned manifest")
    digest = hashlib.sha256()
    with ARCHIVE.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != EXPECTED_SHA256:
        raise RuntimeError("objects.zip SHA256 does not match the pinned manifest")

    target = ASSETS / "objects"
    if target.exists():
        raise RuntimeError("refusing to overwrite an existing objects directory")
    with tempfile.TemporaryDirectory(prefix=".objects-stage-", dir=ASSETS) as tmp:
        stage = Path(tmp)
        with zipfile.ZipFile(ARCHIVE) as bundle:
            members = bundle.infolist()
            for member in members:
                name = PurePosixPath(member.filename)
                if (
                    name.is_absolute()
                    or ".." in name.parts
                    or "\\" in member.filename
                    or stat.S_ISLNK(member.external_attr >> 16)
                    or not name.parts
                    or name.parts[0] != "objects"
                ):
                    raise RuntimeError(f"unsafe or unexpected archive member: {member.filename}")
            for member in members:
                bundle.extract(member, stage)
        extracted = stage / "objects"
        files = [file for file in extracted.rglob("*") if file.is_file()]
        if not files:
            raise RuntimeError("objects archive extracted no files")
        extracted.rename(target)

    manifest = {
        "dataset": "TianxingChen/RoboTwin2.0",
        "revision": "3dc3b798668feb99ac61cc9086d84cbcc3d79186",
        "archive_size": EXPECTED_SIZE,
        "archive_sha256": EXPECTED_SHA256,
        "extracted_file_count": len(files),
        "target": str(target),
    }
    (ASSETS / ".downloads/objects_install.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2), flush=True)


if __name__ == "__main__":
    main()
