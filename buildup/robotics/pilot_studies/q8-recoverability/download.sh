#!/bin/sh
set -eu
cd /home/yoohyun/research3
base=https://huggingface.co/datasets/haosulab/ManiSkill_Demonstrations/resolve/d674485bbffdd533914e52d272fdda34c0515608/demos/PickCube-v1
for name in ppo_pd_joint_delta_pos_ckpt.pt ppo_pd_ee_delta_pos_ckpt.pt; do
  curl -fL --retry 3 -C - -o datasets/q8/$name "$base/rl/$name"
done
curl -fL --retry 3 -C - -o datasets/q8/trajectory.h5 "$base/motionplanning/trajectory.h5"
curl -fL --retry 3 -C - -o datasets/q8/trajectory.json "$base/motionplanning/trajectory.json"
sha256sum datasets/q8/* > runs/q8/inputs.sha256
