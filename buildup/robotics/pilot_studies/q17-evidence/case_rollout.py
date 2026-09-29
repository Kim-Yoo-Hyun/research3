"""Exploratory fixed-seed case trace using the released ActiveArena evaluator contract.

Run only inside the workspace-owned simulator Docker with the released model's
websocket endpoint. This records more case detail than the aggregate evaluator;
it does not replace the official benchmark or establish a paper result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import traceback

import numpy as np
import imageio.v2 as imageio
import yaml

sys.path.insert(0, "/sim/description/utils")
from generate_episode_instructions import generate_episode_descriptions
from envs._GLOBAL_CONFIGS import CONFIGS_PATH
from envs.check_block_color import check_block_color
from policy.oft_subtask_action_12_ws.deploy_policy import get_model, reset_model, eval as policy_eval


TASK = "check_block_color"
TASK_CONFIG = "info_gathering_demo"
POLICY = "oft_subtask_action_12_ws"
PRESELECTED_SEEDS = (100000, 100001, 100004)


def native_config(output: Path) -> dict:
    args = yaml.safe_load(Path(f"/sim/task_config/{TASK_CONFIG}.yml").read_text())
    embodiment_map = yaml.safe_load(Path(CONFIGS_PATH, "_embodiment_config.yml").read_text())
    robot_dir = embodiment_map[args["embodiment"][0]]["file_path"]
    robot_config = yaml.safe_load(Path(robot_dir, "config.yml").read_text())
    cameras = yaml.safe_load(Path(CONFIGS_PATH, "_camera_config.yml").read_text())
    head = cameras[args["camera"]["head_camera_type"]]
    args.update(
        task_name=TASK,
        task_config=TASK_CONFIG,
        ckpt_setting=POLICY,
        policy_name=POLICY,
        left_robot_file=robot_dir,
        right_robot_file=robot_dir,
        left_embodiment_config=robot_config,
        right_embodiment_config=robot_config,
        dual_arm_embodied=True,
        head_camera_h=head["h"],
        head_camera_w=head["w"],
        eval_mode=True,
        save_path=str(output),
        live_frame_log_path=str(output / "live_frames.jsonl"),
        eval_video_log=False,
    )
    return args


def policy_config(output: Path, host: str) -> dict:
    args = yaml.safe_load(Path(f"/sim/policy/{POLICY}/deploy_policy.yml").read_text())
    args.update(
        task_name=TASK,
        task_config=TASK_CONFIG,
        ckpt_setting=POLICY,
        host=host,
        request_log_path=str(output / "requests.jsonl"),
        request_image_dir=str(output / "request_images"),
    )
    return args


def distances_to_pads(env) -> dict[str, float]:
    block_xy = np.asarray(env.block.get_pose().p[:2], dtype=np.float64)
    return {
        color: float(np.linalg.norm(block_xy - np.asarray(center[:2], dtype=np.float64)))
        for color, center in env.pad_centers.items()
    }


def run_seed(seed: int, seed_info: dict, root: Path, host: str, forced_instruction: str | None) -> dict:
    output = root / f"seed_{seed}"
    output.mkdir(parents=True, exist_ok=True)
    args = native_config(output)
    usr_args = policy_config(output, host)
    model = get_model(usr_args)
    env = check_block_color()
    env.suc = 0
    env.test_num = 0
    record = {"seed": seed, "status": "running", "runtime": "exploratory_bridge"}
    try:
        env.setup_demo(now_ep_num=0, seed=seed, is_test=True, **args)
        env.eval_seed = seed
        # The official evaluator uses the committed entry's info and
        # test_num=50 when it constructs and samples unseen instructions.
        instructions = generate_episode_descriptions(TASK, [seed_info], 50)[0]["unseen"]
        sampled_instruction = str(np.random.choice(instructions))
        if forced_instruction is not None and forced_instruction not in instructions:
            raise ValueError("the replay instruction is absent from the official unseen pool")
        instruction = forced_instruction if forced_instruction is not None else sampled_instruction
        env.set_instruction(instruction=instruction)
        record.update(
            instruction=instruction,
            instruction_selection="replay_from_prior_case" if forced_instruction is not None else "official_unseen_sample",
            unforced_sample=sampled_instruction if forced_instruction is not None else None,
            target_color=env.target_color_name,
            pad_centers=env.pad_centers,
            subtask_instruction_map=env.subtask_instruction_map,
            step_limit=int(env.step_lim),
            initial_block_pose=np.asarray(env.block.get_pose().p).tolist(),
            initial_robot_qpos=np.asarray(env.robot.left_entity.get_qpos()).tolist(),
            initial_clutter_objects=env.record_cluttered_objects,
        )
        reset_model(model)
        steps = output / "steps.jsonl"
        release_events = []
        seen_closed = {"left": False, "right": False}
        native_take_action = env.take_action

        def traced_take_action(action, action_type="qpos"):
            was_open = {
                "left": bool(env.is_left_gripper_open()),
                "right": bool(env.is_right_gripper_open()),
            }
            native_take_action(action, action_type=action_type)
            is_open = {
                "left": bool(env.is_left_gripper_open()),
                "right": bool(env.is_right_gripper_open()),
            }
            pad_distances = distances_to_pads(env)
            for arm in ("left", "right"):
                if not is_open[arm]:
                    seen_closed[arm] = True
                if seen_closed[arm] and not was_open[arm] and is_open[arm]:
                    ordered = sorted(pad_distances.items(), key=lambda pair: pair[1])
                    selected = None
                    if ordered[0][1] < 0.10 and ordered[1][1] - ordered[0][1] > 0.03:
                        selected = ordered[0][0]
                    release_events.append({
                        "step": int(env.take_action_cnt),
                        "arm": arm,
                        "selected_pad": selected,
                        "pad_distances_xy": pad_distances,
                        "block_center_z": float(env.block.get_pose().p[2]),
                    })
            with steps.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps({
                    "step": int(env.take_action_cnt),
                    "subtask": int(getattr(env, "current_subtask_idx", 0)),
                    "stage": int(getattr(env, "current_stage", 0)),
                    "left_gripper_open": is_open["left"],
                    "right_gripper_open": is_open["right"],
                    "block_pose": np.asarray(env.block.get_pose().p).tolist(),
                    "pad_distances_xy": pad_distances,
                    "native_success": bool(env.eval_success),
                    "eval_failed": bool(env.eval_failed),
                }) + "\n")

        env.take_action = traced_take_action
        while env.take_action_cnt < env.step_lim and not env.eval_done:
            observation = env.get_obs()
            if env.take_action_cnt == 0:
                image = np.asarray(observation["observation"]["camera_head"]["rgb"])
                record["initial_head_image_sha256"] = hashlib.sha256(image.tobytes()).hexdigest()
                record["initial_head_image_shape"] = list(image.shape)
                imageio.imwrite(output / "initial_head.png", image)
            policy_eval(env, model, observation)
        record.update(
            status="completed",
            actions_taken=int(env.take_action_cnt),
            release_events=release_events,
            first_selected_release=next(
                (event for event in release_events if event["selected_pad"] is not None), None
            ),
            native_success=bool(env.eval_success),
            native_failure_reason=env.eval_failure_reason,
            native_failure_detail=env.eval_failure_detail,
            final_pad_distances_xy=distances_to_pads(env),
            final_block_pose=np.asarray(env.block.get_pose().p).tolist(),
        )
        return record
    except Exception as exc:
        record.update(status="failed", error=repr(exc), traceback=traceback.format_exc())
        return record
    finally:
        (output / "case.json").write_text(json.dumps(record, indent=2, default=str) + "\n")
        try:
            model.close()
        except Exception:
            pass
        if getattr(env, "scene", None) is not None:
            try:
                env.close_env()
            except Exception:
                pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--host", default="q17-policy")
    parser.add_argument("--count", type=int, choices=(1, 2, 3), default=1)
    parser.add_argument("--start-index", type=int, choices=(0, 1, 2), default=0)
    parser.add_argument("--instruction-from", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.start_index + args.count > len(PRESELECTED_SEEDS):
        raise ValueError("requested cases exceed the committed three-seed prefix")
    selected = PRESELECTED_SEEDS[args.start_index : args.start_index + args.count]
    seed_manifest = json.loads(Path(f"/sim/eval_seed_lists/{TASK_CONFIG}/{TASK}.json").read_text())
    committed = seed_manifest["entries"]
    if tuple(entry["seed"] for entry in committed[:3]) != PRESELECTED_SEEDS:
        raise RuntimeError("the committed seed prefix changed")
    cases_path = args.output / "cases.json"
    results = json.loads(cases_path.read_text()) if args.start_index and cases_path.exists() else []
    if len(results) != args.start_index:
        raise RuntimeError("existing case count does not match start index")
    for seed, entry in zip(selected, committed[args.start_index : args.start_index + args.count]):
        forced_instruction = None
        if args.instruction_from is not None:
            prior = json.loads((args.instruction_from / f"seed_{seed}" / "case.json").read_text())
            forced_instruction = prior["instruction"]
        result = run_seed(seed, entry.get("info", {}) or {}, args.output, args.host, forced_instruction)
        results.append(result)
        cases_path.write_text(json.dumps(results, indent=2, default=str) + "\n")
        print(json.dumps({k: v for k, v in result.items() if k != "traceback"}, default=str), flush=True)
        if result["status"] != "completed":
            raise RuntimeError(f"rollout failed for seed {seed}: {result.get('error')}")


if __name__ == "__main__":
    main()
