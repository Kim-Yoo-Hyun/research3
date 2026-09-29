"""One-scene simulator setup probe; this is not an official benchmark rollout."""

import argparse
import json
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
import yaml

from envs.check_block_color import check_block_color
from envs._GLOBAL_CONFIGS import CONFIGS_PATH


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=100000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    config = yaml.safe_load(Path("/sim/task_config/info_gathering_demo.yml").read_text())
    robot_key = config["embodiment"][0]
    robot_map = yaml.safe_load(Path(CONFIGS_PATH, "_embodiment_config.yml").read_text())
    robot_dir = robot_map[robot_key]["file_path"]
    robot_config = yaml.safe_load(Path(robot_dir, "config.yml").read_text())
    config.update(
        task_name="check_block_color",
        task_config="info_gathering_demo",
        left_robot_file=robot_dir,
        right_robot_file=robot_dir,
        left_embodiment_config=robot_config,
        right_embodiment_config=robot_config,
        dual_arm_embodied=True,
        eval_mode=True,
        save_path=str(args.output),
        live_frame_log_path=str(args.output / "live_frames.jsonl"),
        eval_video_log=False,
    )
    # Only remove clutter for the initial dependency smoke; doing so changes
    # fixed-seed scenes and must never be called an official evaluation.
    config["domain_randomization"]["cluttered_table"] = False
    env = check_block_color()
    try:
        env.setup_demo(now_ep_num=0, seed=args.seed, is_test=True, **config)
        env.set_instruction("Place the gray block on the pad matching its back-side color.")
        obs = env.get_obs()
        image = np.asarray(obs["observation"]["camera_head"]["rgb"])
        imageio.imwrite(args.output / "initial_head.png", image)
        payload = {
            "seed": args.seed,
            "modified_from_official_id_config": {"domain_randomization.cluttered_table": False},
            "target_color": env.target_color_name,
            "pad_centers": env.pad_centers,
            "subtask_instruction_map": env.subtask_instruction_map,
            "resolved_subtask_instruction_map": getattr(env, "resolved_subtask_instruction_map", None),
            "task_instruction": env.get_instruction(),
            "image_shape": list(image.shape),
            "image_mean": float(image.mean()),
            "observation_keys": list(obs.keys()),
            "native_success_at_initial_state": bool(env.check_success()),
        }
        (args.output / "scene.json").write_text(json.dumps(payload, indent=2) + "\n")
        print(json.dumps(payload, indent=2), flush=True)
    finally:
        if getattr(env, "scene", None) is not None:
            env.close_env()


if __name__ == "__main__":
    main()
