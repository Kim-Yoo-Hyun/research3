#!/usr/bin/env bash
set -euo pipefail

root=/home/yoohyun/research3
directory="$root/runs/q16/can_audit/data"
revision=74fa018461f479cd9fd15b924a16103012096203
expected=3f2eb92e0a5025d0095e866ac16cc8092d6a762abe27dec90dbaff9027282962
url="https://huggingface.co/datasets/robomimic/robomimic_datasets/resolve/$revision/v1.5/can/ph/low_dim_v15.hdf5"

mkdir -p "$directory"
curl --location --fail --retry 3 --continue-at - --output "$directory/low_dim_v15.hdf5.part" "$url"
test "$(stat -c %s "$directory/low_dim_v15.hdf5.part")" = 46889752
printf '%s  %s\n' "$expected" "$directory/low_dim_v15.hdf5.part" | sha256sum --check
mv "$directory/low_dim_v15.hdf5.part" "$directory/low_dim_v15.hdf5"
