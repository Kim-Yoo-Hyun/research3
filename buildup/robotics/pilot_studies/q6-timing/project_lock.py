"""Text-only projection of the pinned upstream lock to CPython 3.11 Linux CPU."""
from pathlib import Path
import tomllib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
packages = tomllib.loads((ROOT / "external/q6/rtc/uv.lock").read_text())["package"]
lines = ["# Exact upstream versions and allowed distribution hashes; CPU projection.",
         "# CUDA distributions, source checkouts and alternate Python-3.12 ml-dtypes omitted."]
for package in packages:
    name = package["name"]
    if "registry" not in package["source"] or name.startswith(("nvidia-", "jax-cuda")):
        continue
    if name == "ml-dtypes" and package["version"] != "0.4.1":
        continue
    hashes = sorted({x["hash"] for x in package.get("wheels", []) +
                     ([package["sdist"]] if "sdist" in package else [])})
    assert hashes
    line = f"{name}=={package['version']} " + " ".join(f"--hash={h}" for h in hashes)
    lines.append(line)
    if name == "setuptools":
        (HERE / "bootstrap.txt").write_text(line + "\n")
(HERE / "requirements.txt").write_text("\n".join(lines) + "\n")
print("Locked registry distributions:", len(lines) - 2)
