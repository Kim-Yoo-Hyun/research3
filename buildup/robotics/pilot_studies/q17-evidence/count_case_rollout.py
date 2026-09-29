"""One fixed-ID ActiveArena color-count case, run only in the simulator Docker.

Ground-truth labels and button joint positions are written to evaluation files;
the policy receives only the official observation and sampled task instruction.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import traceback

import imageio.v2 as imageio
import numpy as np
import yaml

sys.path.insert(0, "/sim/description/utils")
from generate_episode_instructions import generate_episode_descriptions
from envs._GLOBAL_CONFIGS import CONFIGS_PATH
from envs.count_color_kinds_press_button import count_color_kinds_press_button
from policy.oft_subtask_action_12_ws.deploy_policy import get_model, reset_model, eval as policy_eval


TASK = "count_color_kinds_press_button"
TASK_CONFIG = "info_gathering_demo"
POLICY = "oft_subtask_action_12_ws"
SEED = 100000


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


def policy_config(output: Path) -> dict:
    args = yaml.safe_load(Path(f"/sim/policy/{POLICY}/deploy_policy.yml").read_text())
    args.update(
        task_name=TASK,
        task_config=TASK_CONFIG,
        ckpt_setting=POLICY,
        host="research3_q17_policy_bridge_20260928",
        request_log_path=str(output / "requests.jsonl"),
        request_image_dir=str(output / "request_images"),
    )
    return args


def button_qpos(env) -> dict[str, float]:
    return {str(value): float(env._get_button_qpos(button)) for value, button in env.buttons.items()}


def run(output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(Path(f"/sim/eval_seed_lists/{TASK_CONFIG}/{TASK}.json").read_text())
    entry = manifest["entries"][0]
    if manifest["seeds"][0] != SEED or entry["seed"] != SEED:
        raise RuntimeError("the committed first ID seed changed")
    model = get_model(policy_config(output))
    env = count_color_kinds_press_button()
    env.suc = 0
    env.test_num = 0
    record = {"seed": SEED, "task": TASK, "status": "running", "runtime": "exploratory_bridge"}
    try:
        env.setup_demo(now_ep_num=0, seed=SEED, is_test=True, **native_config(output))
        env.eval_seed = SEED
        choices = generate_episode_descriptions(TASK, [entry.get("info", {}) or {}], 50)[0]["unseen"]
        instruction = str(np.random.choice(choices))
        env.set_instruction(instruction=instruction)
        record.update(
            instruction=instruction,
            instruction_selection="official_unseen_sample",
            step_limit=int(env.step_lim),
            target_count=int(env.target_count),
            appeared_colors=list(env.appeared_colors),
            block_color_labels=dict(env.block_color_labels),
            block_poses={key: np.asarray(block.get_pose().p).tolist() for key, block in env.blocks.items()},
            button_poses={str(value): np.asarray(button.get_pose().p).tolist() for value, button in env.buttons.items()},
            initial_button_qpos=button_qpos(env),
            initial_clutter_objects=env.record_cluttered_objects,
        )
        reset_model(model)
        steps_path = output / "steps.jsonl"
        press_events = []
        prior_pressed = set()
        native_take_action = env.take_action

        def traced_take_action(action, action_type="qpos"):
            nonlocal prior_pressed
            native_take_action(action, action_type=action_type)
            qpos = button_qpos(env)
            pressed = {int(value) for value, pos in qpos.items() if pos < env.BUTTON_PRESS_THRESHOLD}
            for value in sorted(pressed - prior_pressed):
                press_events.append({"step": int(env.take_action_cnt), "button": value, "qpos": qpos[str(value)]})
            prior_pressed = pressed
            with steps_path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps({
                    "step": int(env.take_action_cnt),
                    "subtask": int(getattr(env, "current_subtask_idx", 0)),
                    "stage": int(getattr(env, "current_stage", 0)),
                    "button_qpos": qpos,
                    "physically_pressed": sorted(pressed),
                    "pressed_button_value": getattr(env, "pressed_button_value", None),
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
            physical_press_events=press_events,
            final_button_qpos=button_qpos(env),
            pressed_button_value=getattr(env, "pressed_button_value", None),
            native_success=bool(env.eval_success),
            native_failed=bool(env.eval_failed),
            native_failure_reason=env.eval_failure_reason,
            native_failure_detail=env.eval_failure_detail,
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


if __name__ == "__main__":
    target = Path("/output")
    result = run(target)
    print(json.dumps({k: v for k, v in result.items() if k != "traceback"}, default=str), flush=True)
    if result["status"] != "completed":
        raise RuntimeError(result.get("error", "rollout failed"))
