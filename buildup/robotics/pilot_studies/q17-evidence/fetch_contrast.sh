#!/usr/bin/env bash
set -Eeuo pipefail

path=/home/yoohyun/research3/datasets/q17/activearena/check_block_color/data/chunk-000/episode_000002.parquet
url=https://huggingface.co/datasets/leeibo/ActiveArena-Data/resolve/4fc698d7b3c1871c342181a5fa38f837da945a80/check_block_color/data/chunk-000/episode_000002.parquet
mkdir -p "$(dirname "${path}")"
curl --location --fail --retry 5 --continue-at - --silent --show-error --output "${path}" "${url}"
printf '%s\n' '6ed47a0adc84d97f8bb190eb6003494d9be79df317000cf7c7e9ddc26bd74f84  /home/yoohyun/research3/datasets/q17/activearena/check_block_color/data/chunk-000/episode_000002.parquet' | sha256sum --check
stat -c '%n %s bytes' "${path}"
