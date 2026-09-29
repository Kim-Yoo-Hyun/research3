#!/usr/bin/env bash
set -euo pipefail

workspace=/home/yoohyun/research3
base_dir="$workspace/datasets/q17/model/qwen3-vl-2b"
policy_dir="$workspace/datasets/q17/model/oft_subtask_action_12_ws"
base_revision=89644892e4d85e24eaac8bacfd4f463576704203
policy_revision=c265fe089dc23656e7ff82eb0fe8012adc0644aa
mkdir -p "$base_dir" "$policy_dir/checkpoints"

fetch() {
  local url="$1" destination="$2"
  curl --silent --show-error --location --fail --retry 20 --retry-all-errors \
    --retry-delay 5 --continue-at - \
    --output "$destination" "$url"
}

for name in chat_template.json config.json generation_config.json merges.txt \
  preprocessor_config.json tokenizer.json tokenizer_config.json \
  video_preprocessor_config.json vocab.json model.safetensors; do
  fetch "https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct/resolve/$base_revision/$name" \
    "$base_dir/$name"
done
for name in config.yaml config.full.yaml dataset_statistics.json; do
  fetch "https://huggingface.co/leeibo/ActiveArena-VLA/resolve/$policy_revision/oft_subtask_action_12_ws/$name" \
    "$policy_dir/$name"
done
fetch "https://huggingface.co/leeibo/ActiveArena-VLA/resolve/$policy_revision/oft_subtask_action_12_ws/checkpoints/steps_100000_pytorch_model.pt" \
  "$policy_dir/checkpoints/steps_100000_pytorch_model.pt"

printf '%s  %s\n' \
  7de1838c87a5349b016c26a1c3f7d2bc400a3d485f95ef39a7059ffd734977a0 "$base_dir/model.safetensors" \
  537f9a70e2ee88f04c0b98deb67e0975bb00897b48d4ac218ea5ae09fc8ca67c "$policy_dir/checkpoints/steps_100000_pytorch_model.pt" | sha256sum --check
test "$(stat -c %s "$base_dir/model.safetensors")" = 4255140312
test "$(stat -c %s "$policy_dir/checkpoints/steps_100000_pytorch_model.pt")" = 4967033387
echo 'Q17 model assets verified'
