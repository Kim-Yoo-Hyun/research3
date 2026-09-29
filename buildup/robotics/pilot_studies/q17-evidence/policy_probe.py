"""Exploratory paired offline inference; run inside the Q17 policy Docker only."""

from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
import torch
from PIL import Image

from starVLA.model.framework.VLM4A.QwenOFTState import Qwenvl_OFT_State  # noqa: F401; register only this framework
import starVLA.model.framework.base_framework as framework_module
from starVLA.model.framework.base_framework import baseframework
from starVLA.model.framework.share_tools import read_mode_config


DATA = Path("/dataset")
INPUT = Path("/input/probe_inputs.json")
OUTPUT = Path("/output")
CHECKPOINT = "/models/policy/checkpoints/steps_100000_pytorch_model.pt"
GENERIC_TASK = "Place the gray block on the pad matching its back-side color."


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_state(state: np.ndarray, stats: dict) -> np.ndarray:
    minimum = np.asarray(stats["min"], dtype=np.float32)
    maximum = np.asarray(stats["max"], dtype=np.float32)
    result = np.zeros_like(state)
    mask = maximum != minimum
    result[..., mask] = 2 * (state[..., mask] - minimum[mask]) / (maximum[mask] - minimum[mask]) - 1
    return result


def unnormalize_actions(actions: np.ndarray, stats: dict) -> np.ndarray:
    minimum = np.asarray(stats["min"], dtype=np.float32)
    maximum = np.asarray(stats["max"], dtype=np.float32)
    return (actions + 1) / 2 * (maximum - minimum) + minimum


def example(table, indices: list[int], task_text: str, subtask_text: str | None, state_stats: dict) -> dict:
    images = [Image.open(io.BytesIO(table["observation.images.camera_head"][row].as_py()["bytes"])).convert("RGB") for row in indices]
    states = np.asarray([table["observation.state"][row].as_py() for row in indices], dtype=np.float32)
    states = normalize_state(states, state_stats)
    item = {
        "image": images,
        "lang": task_text,
        "task_lang": task_text,
        "state_history": states,
        "state": states,
        "num_frames": len(indices),
        "num_history_frames": len(indices) - 1,
        "history_frame_indices": indices,
        "history_mode": "action_keyframe",
        "robot_tag": "activearena_astribot",
    }
    if subtask_text is not None:
        item["subtask_lang"] = subtask_text
        item["subtask_instruction"] = subtask_text
    return item


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    assert torch.cuda.is_available(), "GPU runtime unavailable"
    torch.manual_seed(1729)
    np.random.seed(1729)
    # The release's generic loader imports all framework families. Registering the
    # released QwenOFTState directly keeps this single-checkpoint probe isolated.
    framework_module._FRAMEWORKS_IMPORTED = True
    _, all_stats = read_mode_config(CHECKPOINT)
    assert len(all_stats) == 1
    stats = next(iter(all_stats.values()))
    assert len(stats["state"]["min"]) == len(stats["action"]["min"]) == 18
    model = baseframework.from_pretrained(CHECKPOINT).to("cuda").eval()
    selected = json.loads(INPUT.read_text())
    results = {
        "purpose": "paired offline action sensitivity; no simulator rollout or success claim",
        "model_sha256": sha256(Path(CHECKPOINT)),
        "source_commit": os.environ.get("Q17_VLA_COMMIT", "unknown"),
        "input_sha256": sha256(INPUT),
        "gpu": torch.cuda.get_device_name(0),
        "episodes": {},
    }
    for episode_id, choice in selected.items():
        table = pq.read_table(DATA / "data/chunk-000" / f"episode_{int(episode_id):06d}.parquet")
        current = int(choice["current_row"])
        indices = choice["frame_indices"]
        assert indices[-1] == current
        expert = np.asarray([table["action"][row].as_py() for row in range(current, min(current + 16, table.num_rows))], dtype=np.float32)
        conditions = {
            "generic_full_history": (indices, GENERIC_TASK, None),
            "generic_current_only": ([current], GENERIC_TASK, None),
            "explicit_task_full_history": (indices, choice["task_instruction"], None),
            "explicit_subtask_full_history": (indices, GENERIC_TASK, choice["subtask_instruction_at_current"]),
        }
        current_image = table["observation.images.camera_head"][current].as_py()["bytes"]
        current_state = np.asarray(table["observation.state"][current].as_py(), dtype=np.float32)
        episode_output = {
            "current_row": current,
            "current_image_sha256": hashlib.sha256(current_image).hexdigest(),
            "current_state_sha256": hashlib.sha256(current_state.tobytes()).hexdigest(),
            "target_color_in_training_task_instruction": choice["task_instruction"],
            "frame_indices": indices,
            "expert_length": len(expert),
            "conditions": {},
        }
        for name, (frame_indices, task_text, subtask_text) in conditions.items():
            prediction = model.predict_action([example(table, frame_indices, task_text, subtask_text, stats["state"])])
            normalized_actions = np.asarray(prediction["normalized_actions"], dtype=np.float32)[0]
            actions = unnormalize_actions(normalized_actions, stats["action"])
            assert actions.shape == (16, 18) and np.isfinite(actions).all()
            assert expert.shape == actions.shape, (expert.shape, actions.shape)
            episode_output["conditions"][name] = {
                "task_instruction": task_text,
                "subtask_instruction": subtask_text,
                "frame_indices": frame_indices,
                "first_action": actions[0].tolist(),
                "first_step_l1_to_demo": float(np.mean(np.abs(actions[0] - expert[0]))),
                "chunk_l1_to_demo": float(np.mean(np.abs(actions - expert))),
            }
            np.save(OUTPUT / f"episode_{int(episode_id):06d}_{name}.npy", actions)
            print(json.dumps({"episode": episode_id, "condition": name, "first_step_l1": episode_output["conditions"][name]["first_step_l1_to_demo"], "chunk_l1": episode_output["conditions"][name]["chunk_l1_to_demo"]}), flush=True)
        results["episodes"][episode_id] = episode_output
        full = np.load(OUTPUT / f"episode_{int(episode_id):06d}_generic_full_history.npy")
        no_history = np.load(OUTPUT / f"episode_{int(episode_id):06d}_generic_current_only.npy")
        explicit_task = np.load(OUTPUT / f"episode_{int(episode_id):06d}_explicit_task_full_history.npy")
        explicit_subtask = np.load(OUTPUT / f"episode_{int(episode_id):06d}_explicit_subtask_full_history.npy")
        episode_output["comparisons"] = {
            "first_action_l1_full_vs_current_only": float(np.mean(np.abs(full[0] - no_history[0]))),
            "first_action_l1_generic_vs_explicit_task": float(np.mean(np.abs(full[0] - explicit_task[0]))),
            "first_action_l1_generic_vs_explicit_subtask": float(np.mean(np.abs(full[0] - explicit_subtask[0]))),
        }
        (OUTPUT / "probe.json").write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
