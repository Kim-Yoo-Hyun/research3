#!/usr/bin/env bash
set -Eeuo pipefail

# RoboTwin2.0 base objects are required by ActiveArena's official ID clutter.
workspace=/home/yoohyun/research3
asset_root="${workspace}/datasets/q17/sim_assets"
archive="${asset_root}/.downloads/objects.zip"
expected=6aa56b3cf1e1064f7c809308144da36b00815f8b137fef2d7e4de856f8becf27
url=https://huggingface.co/datasets/TianxingChen/RoboTwin2.0/resolve/3dc3b798668feb99ac61cc9086d84cbcc3d79186/objects.zip
mkdir -p "$(dirname "${archive}")"
if [[ -f "${archive}" ]] && echo "${expected}  ${archive}" | sha256sum -c -; then
    exit 0
fi
for attempt in $(seq 1 15); do
    echo "objects.zip attempt ${attempt}, current_bytes=$(stat -c %s "${archive}" 2>/dev/null || echo 0)"
    if curl --http1.1 --silent --show-error --location --fail \
        --connect-timeout 30 --max-time 1800 --continue-at - \
        --output "${archive}" "${url}"; then
        break
    fi
    if [[ "${attempt}" -eq 15 ]]; then
        echo "objects.zip download exhausted 15 resumable attempts" >&2
        exit 1
    fi
    sleep 3
done
echo "${expected}  ${archive}" | sha256sum -c -
