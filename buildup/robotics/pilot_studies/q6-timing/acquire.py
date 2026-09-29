"""Host-safe byte acquisition; never imports a model or simulator."""
import base64
import hashlib
import io
import json
from pathlib import Path
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[4]
STUDY = Path(__file__).resolve().parent
REPOS = {
    "rtc": ("Physical-Intelligence/real-time-chunking-kinetix", "9296f31d62d5bfeb5779dcb2f9bcf71ca37f448b"),
    "kinetix": ("FlairOx/Kinetix", "cf7453ea103fa0b77348af1a39f689c658161613"),
    "jaxued": ("DramaCow/jaxued", "62d155ae772aa2a0ecac9541d498df7ae88e6def"),
}


def fetch(url, cap=128 * 1024**2):
    req = urllib.request.Request(url, headers={"User-Agent": "research3-q6-readiness"})
    with urllib.request.urlopen(req, timeout=120) as response:
        data = response.read(cap + 1)
    if len(data) > cap:
        raise ValueError("download cap exceeded")
    return data


def identity(data):
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def crc32c(data):
    table = []
    for i in range(256):
        for _ in range(8):
            i = (i >> 1) ^ (0x82F63B78 if i & 1 else 0)
        table.append(i)
    c = 0xFFFFFFFF
    for b in data:
        c = table[(c ^ b) & 255] ^ (c >> 8)
    return base64.b64encode((c ^ 0xFFFFFFFF).to_bytes(4, "big")).decode()


def main():
    receipt = {"repositories": [], "weights": []}
    for name, (repo, commit) in REPOS.items():
        destination = ROOT / "external/q6" / name
        destination.mkdir(parents=True, exist_ok=True)
        tree_url = f"https://api.github.com/repos/{repo}/git/trees/{commit}?recursive=1"
        tree = json.loads(fetch(tree_url))
        assert not tree["truncated"]
        entries = {x["path"]: x for x in tree["tree"] if x["type"] == "blob"}
        archive_url = f"https://codeload.github.com/{repo}/tar.gz/{commit}"
        archive = fetch(archive_url)
        files = []
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
            for member in tar:
                if member.isdir():
                    continue
                assert member.isfile(), member.name
                rel = Path(*Path(member.name).parts[1:])
                assert not rel.is_absolute() and ".." not in rel.parts
                data = tar.extractfile(member).read()
                blob = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
                expected = entries[rel.as_posix()]
                assert blob == expected["sha"] and len(data) == expected["size"], rel
                path = destination / rel
                if path.exists():
                    assert path.read_bytes() == data, path
                else:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(data)
                files.append({"path": rel.as_posix(), "git_blob_sha1": blob, **identity(data)})
        assert {f["path"] for f in files} == set(entries)
        receipt["repositories"].append({"name": name, "repo": repo, "commit": commit,
            "tree_url": tree_url, "archive_url": archive_url, "archive": identity(archive), "files": files})
        (STUDY / "assets.json").write_text(json.dumps(receipt, indent=2) + "\n")
        print(name, "verified files", len(files), flush=True)
    prior = json.loads((STUDY.parent.parent / "related_work/q6_sources.json").read_text())
    destination = ROOT / "datasets/q6/policies"
    destination.mkdir(parents=True, exist_ok=True)
    for row in prior["checkpoints"]:
        path = destination / f"{row['level']}.pkl"
        data = path.read_bytes() if path.exists() else fetch(row["url"], 13 * 1024**2)
        assert len(data) == row["bytes"]
        assert base64.b64encode(hashlib.md5(data).digest()).decode() == row["listed_md5_base64"]
        assert crc32c(data) == row["listed_crc32c_base64"]
        if not path.exists():
            path.write_bytes(data)
        receipt["weights"].append({**row, **identity(data), "path": str(path.relative_to(ROOT)),
            "verified_scope": "payload bytes, MD5, CRC32c, SHA256; loading not yet tested"})
        print(row["level"], "weight verified", flush=True)
    assert sum(x["bytes"] for x in receipt["weights"]) <= 25 * 1024**2
    (STUDY / "assets.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("ACQUISITION_VERIFIED", flush=True)


if __name__ == "__main__":
    main()
