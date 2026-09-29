"""Verify that the bilateral-gripper rerun starts from the same case/policy prefix."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


SEEDS = (100000, 100001, 100004)


def values(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def max_difference(left, right):
    if isinstance(left, list):
        if len(left) != len(right):
            raise AssertionError("vector length mismatch")
        return max((max_difference(a, b) for a, b in zip(left, right)), default=0.0)
    return abs(float(left) - float(right))


def same_input_images(old_dir: Path, new_dir: Path, old_requests: list, new_requests: list) -> bool:
    if len(old_requests) != len(new_requests):
        return False
    for old_request, new_request in zip(old_requests, new_requests):
        old_history = old_request["request"]["image_history"]
        new_history = new_request["request"]["image_history"]
        if len(old_history) != len(new_history):
            return False
        for old_image, new_image in zip(old_history, new_history):
            old_path = old_dir / "request_images" / Path(old_image["path"]).name
            new_path = new_dir / "request_images" / Path(new_image["path"]).name
            old_digest = hashlib.sha256(old_path.read_bytes()).digest()
            new_digest = hashlib.sha256(new_path.read_bytes()).digest()
            if old_digest != new_digest:
                return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--old", type=Path, required=True)
    parser.add_argument("--new", type=Path, required=True)
    parser.add_argument("--seeds", nargs="+", type=int, choices=SEEDS, default=SEEDS)
    args = parser.parse_args()
    comparison = []
    for seed in args.seeds:
        old_dir = args.old / f"seed_{seed}"
        new_dir = args.new / f"seed_{seed}"
        old = json.loads((old_dir / "case.json").read_text())
        new = json.loads((new_dir / "case.json").read_text())
        old_requests = values(old_dir / "requests.jsonl")
        new_requests = values(new_dir / "requests.jsonl")
        old_steps = values(old_dir / "steps.jsonl")
        new_steps = values(new_dir / "steps.jsonl")
        row = {
            "seed": seed,
            "same_initial_image_sha256": old["initial_head_image_sha256"] == new["initial_head_image_sha256"],
            "same_instruction": old["instruction"] == new["instruction"],
            "same_all_input_images_sha256": same_input_images(old_dir, new_dir, old_requests, new_requests),
            "initial_block_max_abs": max_difference(old["initial_block_pose"], new["initial_block_pose"]),
            "initial_robot_max_abs": max_difference(old["initial_robot_qpos"], new["initial_robot_qpos"]),
            "first_action_chunk_max_abs": max_difference(
                old_requests[0]["response"]["actions"],
                new_requests[0]["response"]["actions"],
            ),
            "first_16_block_pose_max_abs": max(
                max_difference(a["block_pose"], b["block_pose"])
                for a, b in zip(old_steps[:16], new_steps[:16])
            ),
            "old_request_count": len(old_requests),
            "new_request_count": len(new_requests),
            "old_step_count": len(old_steps),
            "new_step_count": len(new_steps),
        }
        if len(old_requests) == len(new_requests) and len(old_steps) == len(new_steps):
            row["all_action_chunks_max_abs"] = max(
                max_difference(a["response"]["actions"], b["response"]["actions"])
                for a, b in zip(old_requests, new_requests)
            )
            row["all_block_pose_max_abs"] = max(
                max_difference(a["block_pose"], b["block_pose"])
                for a, b in zip(old_steps, new_steps)
            )
        else:
            row["all_action_chunks_max_abs"] = None
            row["all_block_pose_max_abs"] = None
        row["prefix_parity"] = bool(
            row["same_initial_image_sha256"]
            and row["same_instruction"]
            and row["initial_block_max_abs"] < 1e-6
            and row["initial_robot_max_abs"] < 1e-6
            and row["first_action_chunk_max_abs"] < 1e-5
            and row["first_16_block_pose_max_abs"] < 1e-5
        )
        row["full_trajectory_parity"] = bool(
            row["prefix_parity"]
            and row["same_all_input_images_sha256"]
            and row["all_action_chunks_max_abs"] is not None
            and row["all_action_chunks_max_abs"] < 1e-5
            and row["all_block_pose_max_abs"] < 1e-5
        )
        comparison.append(row)
    result = {
        "comparison": comparison,
        "all_prefix_parity": all(row["prefix_parity"] for row in comparison),
        "all_full_trajectory_parity": all(row["full_trajectory_parity"] for row in comparison),
    }
    (args.new / "rerun_verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2), flush=True)
    if not result["all_full_trajectory_parity"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
