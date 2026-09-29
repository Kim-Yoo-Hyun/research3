#!/usr/bin/env bash
set -Eeuo pipefail

dataset_revision=4fc698d7b3c1871c342181a5fa38f837da945a80
dataset_base="https://huggingface.co/datasets/leeibo/ActiveArena-Data/resolve/${dataset_revision}/check_block_color"
dataset_root=/home/yoohyun/research3/datasets/q17/activearena/check_block_color

for relative_path in \
    meta/info.json \
    meta/tasks.jsonl \
    meta/episodes.jsonl \
    meta/episodes_stats.jsonl \
    meta/astribot_subtask_metadata.json \
    data/chunk-000/episode_000000.parquet \
    data/chunk-000/episode_000001.parquet; do
    mkdir -p "${dataset_root}/$(dirname "${relative_path}")"
    curl --location --fail --retry 5 --continue-at - --silent --show-error \
        --output "${dataset_root}/${relative_path}" \
        "${dataset_base}/${relative_path}"
done

printf '%s\n' \
  'af11c70cce54ff818d9d3b0092fa54dbc66c179ff6fa43152b1273c12bbe6d00  /home/yoohyun/research3/datasets/q17/activearena/check_block_color/data/chunk-000/episode_000000.parquet' \
  '154f3646717e31205efc99136ed8279b3ed153a8bf7d7a0192d46d990b63f374  /home/yoohyun/research3/datasets/q17/activearena/check_block_color/data/chunk-000/episode_000001.parquet' \
  | sha256sum --check

find "${dataset_root}" -type f -printf '%P %s bytes\n' | sort
