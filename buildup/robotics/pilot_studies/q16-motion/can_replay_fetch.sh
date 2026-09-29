#!/usr/bin/env bash
set -euo pipefail
cd /home/yoohyun/research3
mkdir -p external/q16
for entry in \
  'robomimic ae5799f0fae05c4559ee1f9645b0f77eb5251929' \
  'robosuite 51cc01785bab80ffeed20da15e67d7dd4140e76a'; do
  read -r project commit <<< "$entry"
  target="external/q16/${project}-${commit}.tar.gz"
  if [[ ! -s "$target" ]]; then
    curl --fail --location --retry 4 --retry-delay 2 --output "${target}.part" \
      "https://codeload.github.com/ARISE-Initiative/${project}/tar.gz/${commit}"
    tar -tzf "${target}.part" >/dev/null
    mv "${target}.part" "$target"
  fi
  tar -tzf "$target" >/dev/null
  if [[ ! -d "external/q16/${project}-${commit}" ]]; then
    tar -xzf "$target" -C external/q16
  fi
  sha256sum "$target"
done
