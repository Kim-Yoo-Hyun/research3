"""Matched fixed-seed replay and one prompt-only oracle diagnostic in Docker.

The oracle condition preserves the policy client's visual/state history and
changes only the text passed to its inference request at step 80 onward.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import traceback

import imageio.v2 as imageio
import numpy as np

from count_case_rollout import (
    SEED,
    TASK,
    TASK_CONFIG,
    button_qpos,
    native_config,
    policy_config,
)
from generate_episode_instructions import generate_episode_descriptions
from envs.count_color_kinds_press_button import count_color_kinds_press_button
from policy.oft_subtask_action_12_ws.deploy_policy import get_model, reset_model, eval as policy_eval


DEFAULT_DECISION_STEP = 80
ORACLE_SUFFIX = " There are exactly three distinct block colors; press button 3."


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def frame_equal(left_dir: Path, right_dir: Path, left: dict, right: dict) -> bool:
    left_history = left["request"]["image_history"]
    right_history = right["request"]["image_history"]
    if len(left_history) != len(right_history):
        return False
    for a, b in zip(left_history, right_history):
        if a["frame_step"] != b["frame_step"]:
            return False
        a_file = left_dir / "request_images" / Path(a["path"]).name
        b_file = right_dir / "request_images" / Path(b["path"]).name
        if hashlib.sha256(a_file.read_bytes()).digest() != hashlib.sha256(b_file.read_bytes()).digest():
            return False
    return True


def prefix_matches(reference: Path, candidate: Path, decision_step: int) -> tuple[bool, dict]:
    old_requests = [r for r in read_jsonl(reference / "requests.jsonl") if r["env_step"] < decision_step]
    new_requests = [r for r in read_jsonl(candidate / "requests.jsonl") if r["env_step"] < decision_step]
    old_steps = read_jsonl(reference / "steps.jsonl")[:decision_step]
    new_steps = read_jsonl(candidate / "steps.jsonl")[:decision_step]
    checks = {
        "request_steps": [r["env_step"] for r in old_requests] == [r["env_step"] for r in new_requests],
        "step_count": len(old_steps) == len(new_steps) == decision_step,
        "step_records": old_steps == new_steps,
        "instruction": all(a["instruction"] == b["instruction"] for a, b in zip(old_requests, new_requests)),
        "state_histories": all(a["request"]["state_history"] == b["request"]["state_history"] for a, b in zip(old_requests, new_requests)),
        "action_chunks": all(a["response"]["actions"] == b["response"]["actions"] for a, b in zip(old_requests, new_requests)),
        "image_histories": len(old_requests) == len(new_requests) and all(
            frame_equal(reference, candidate, a, b) for a, b in zip(old_requests, new_requests)
        ),
    }
    return bool(all(checks.values())), checks


def decision_state(env, model, observation: dict, prior: Path, decision_step: int) -> dict:
    raw_image = np.asarray(observation["observation"]["camera_head"]["rgb"])
    resized_image = model._resize_images([raw_image])[0]
    originals = [r for r in read_jsonl(prior / "requests.jsonl") if r["env_step"] == decision_step]
    if len(originals) != 1:
        raise RuntimeError("the original case has no unique request at the selected decision step")
    original = originals[0]
    expected_path = prior / "request_images" / Path(original["request"]["image_history"][-1]["path"]).name
    expected_image = np.asarray(imageio.imread(expected_path))
    return {
        "step": int(env.take_action_cnt),
        "raw_image_sha256": hashlib.sha256(raw_image.tobytes()).hexdigest(),
        "resized_image_sha256": hashlib.sha256(resized_image.tobytes()).hexdigest(),
        "resized_matches_prior_request": bool(np.array_equal(resized_image, expected_image)),
        "robot_joint_vector": np.asarray(observation["joint_action"]["vector"]).tolist(),
        "button_qpos": button_qpos(env),
        "block_poses": {key: np.asarray(block.get_pose().p).tolist() for key, block in env.blocks.items()},
    }


def run(mode: str, output: Path, prior: Path, parity: Path | None, decision_step: int) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    original = json.loads((prior / "case.json").read_text())
    manifest = json.loads(Path(f"/sim/eval_seed_lists/{TASK_CONFIG}/{TASK}.json").read_text())
    entry = manifest["entries"][0]
    if entry["seed"] != SEED or original["seed"] != SEED or original["target_count"] != 3:
        raise RuntimeError("the committed seed or original target changed")
    if mode == "oracle" and parity is None:
        raise ValueError("oracle mode requires a completed parity replay")
    if decision_step not in {r["env_step"] for r in read_jsonl(prior / "requests.jsonl")}:
        raise ValueError("decision step must be an original policy request step")

    model = get_model(policy_config(output))
    env = count_color_kinds_press_button()
    env.suc = 0
    env.test_num = 0
    record = {"seed": SEED, "task": TASK, "mode": mode, "decision_step": decision_step, "status": "running", "runtime": "exploratory_bridge"}
    try:
        env.setup_demo(now_ep_num=0, seed=SEED, is_test=True, **native_config(output))
        env.eval_seed = SEED
        choices = generate_episode_descriptions(TASK, [entry.get("info", {}) or {}], 50)[0]["unseen"]
        sampled = str(np.random.choice(choices))
        instruction = str(original["instruction"])
        if instruction not in choices:
            raise ValueError("original text is absent from the official unseen pool")
        env.set_instruction(instruction=instruction)
        record.update(
            instruction=instruction,
            instruction_selection="replay_from_prior_case_after_normal_sample",
            unforced_sample=sampled,
            target_count=int(env.target_count),
            block_color_labels=dict(env.block_color_labels),
            initial_head_image_sha256=None,
            step_limit=int(env.step_lim),
            oracle_request_text=instruction + ORACLE_SUFFIX if mode == "oracle" else None,
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
                imageio.imwrite(output / "initial_head.png", image)
            if env.take_action_cnt == decision_step:
                record["pre_decision_state"] = decision_state(env, model, observation, prior, decision_step)
                if mode == "oracle":
                    matched, checks = prefix_matches(prior, output, decision_step)
                    record["prefix_checks_before_intervention"] = checks
                    replay = json.loads((parity / "case.json").read_text())
                    if replay.get("status") != "completed" or not all(replay.get("prefix_checks", {}).values()):
                        raise RuntimeError("the parity replay did not pass its recorded checks")
                    record["pre_decision_matches_parity"] = record["pre_decision_state"] == replay["pre_decision_state"]
                    if not (matched and record["pre_decision_matches_parity"] and record["pre_decision_state"]["resized_matches_prior_request"]):
                        raise RuntimeError("pre-intervention parity failed; oracle request was not sent")
                    native_request = model._request_actions
                    oracle_text = record["oracle_request_text"]

                    def request_with_oracle_text(records, current_instruction, camera_key, subtask_instruction):
                        return native_request(records, oracle_text, camera_key, subtask_instruction)

                    # Avoid the adapter's language-change reset: only the
                    # outgoing text changes, with identical image/state history.
                    model._request_actions = request_with_oracle_text
                    record["intervention_step"] = decision_step
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
        if mode == "replay":
            matched, checks = prefix_matches(prior, output, decision_step)
            record["prefix_checks"] = checks
            if not (matched and record.get("pre_decision_state", {}).get("resized_matches_prior_request")):
                record["status"] = "parity_failed"
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("replay", "oracle"), required=True)
    parser.add_argument("--output", type=Path, default=Path("/output"))
    parser.add_argument("--prior", type=Path, default=Path("/prior"))
    parser.add_argument("--parity", type=Path)
    parser.add_argument("--decision-step", type=int, default=DEFAULT_DECISION_STEP)
    args = parser.parse_args()
    result = run(args.mode, args.output, args.prior, args.parity, args.decision_step)
    print(json.dumps({key: value for key, value in result.items() if key != "traceback"}, default=str), flush=True)
    if result["status"] != "completed":
        raise RuntimeError(result.get("error", result["status"]))
