#!/usr/bin/env bash
set -Eeuo pipefail

# Download only the robot embodiment used by check_block_color. The source
# manifest pins the same revision and SHA-256 in download_activearena_assets.py.
workspace=/home/yoohyun/research3
asset_root="${workspace}/datasets/q17/sim_assets"
archive="${asset_root}/.downloads/astribot_descriptions_texture_20260630_174911.zip"
expected=49be39c500e763d6d0194d4449751967bff16df5a2c044f1f53f7e9b7adffcb7
url=https://huggingface.co/datasets/leeibo/ActiveArena-Assets/resolve/819632dfd545b569657e195cc47aae3af7fce5f1/astribot_descriptions_texture_20260630_174911.zip
mkdir -p "$(dirname "${archive}")"
if [[ -f "${archive}" ]] && echo "${expected}  ${archive}" | sha256sum -c -; then
    exit 0
fi
curl --location --fail --retry 5 --retry-all-errors --continue-at - \
    --output "${archive}" "${url}"
echo "${expected}  ${archive}" | sha256sum -c -
