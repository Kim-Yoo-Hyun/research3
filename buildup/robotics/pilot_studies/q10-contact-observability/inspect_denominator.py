#!/usr/bin/env python3
"""Inspect the pre-fixed Q10 v4 denominator without decoding media."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import h5py
import numpy as np


CORE_ACTIONS = ("pick", "insert", "remove", "place")


def scalar(group: h5py.Group, name: str):
    value = group[name][...]
    if isinstance(value, np.ndarray) and value.shape == ():
        value = value.item()
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if isinstance(value, np.generic):
        return value.item()
    return value


def count_in_window(values: np.ndarray, start: float, end: float) -> int:
    values = np.asarray(values).reshape(-1)
    left = int(np.searchsorted(values, start, side="left"))
    right = int(np.searchsorted(values, end, side="right"))
    return max(0, right - left)


def parse_action(text: str) -> tuple[str, str]:
    normalized = text.strip().rstrip(".")
    if normalized.lower() == "no action":
        return "no_action", ""
    parts = normalized.split(maxsplit=1)
    return parts[0].lower(), parts[1] if len(parts) == 2 else ""


def resolve_file(input_dirs: list[Path], recording_id: str) -> Path:
    matches = [path for root in input_dirs if (path := root / f"{recording_id}.h5").exists()]
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one input for {recording_id}, found {matches}")
    return matches[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, action="append", required=True)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        raise RuntimeError(f"output directory is not empty: {args.output_dir}")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    selection = json.loads(args.selection.read_text(encoding="utf-8"))
    configs = selection["denominator_members"]
    if len(configs) != 20 or len({item["recording_id"] for item in configs}) != 20:
        raise RuntimeError("v4 requires exactly 20 unique frozen recordings")

    files = []
    rows = []
    for config in configs:
        recording_id = config["recording_id"]
        path = resolve_file(args.input_dir, recording_id)
        with h5py.File(path, "r") as handle:
            paths = set()
            handle.visititems(lambda name, obj: paths.add(name) if isinstance(obj, h5py.Dataset) else None)
            timestamp_paths = {
                "external_rgb": "timestamps/hama1",
                "force": "timestamps/measured_force",
                "proprioception": "timestamps/pose",
            }
            required = {
                "external_rgb_data": "hama1" in paths,
                "external_rgb_timestamp": timestamp_paths["external_rgb"] in paths,
                "force_data": any(name.startswith("robot_state/") and "force" in name for name in paths),
                "force_timestamp": timestamp_paths["force"] in paths,
                "proprioception_data": any(
                    name.startswith("robot_state/") and any(key in name for key in ("pose", "joint_positions", "gripper_positions"))
                    for name in paths
                ),
                "proprioception_timestamp": timestamp_paths["proprioception"] in paths,
                "segments_info": "segments_info" in handle,
            }
            timestamps = {
                name: np.asarray(handle[dataset][...]).reshape(-1)
                for name, dataset in timestamp_paths.items() if dataset in paths
            }
            segment_group = handle["segments_info"]
            keys = sorted(segment_group.keys(), key=int)
            for position, segment_key in enumerate(keys):
                group = segment_group[segment_key]
                start, end = float(scalar(group, "start")), float(scalar(group, "end"))
                text = str(scalar(group, "text"))
                action, object_name = parse_action(text)
                excluded = config["condition"] == "force/torque not valid for last action" and position == len(keys) - 1
                counts = {
                    name: count_in_window(values, start, end) for name, values in timestamps.items()
                }
                matched = (
                    not excluded
                    and all(name in counts and counts[name] > 0 for name in timestamp_paths)
                )
                rows.append({
                    "recording_id": recording_id,
                    "source": config["source"],
                    "split": config["split"],
                    "condition": config["condition"],
                    "segment_index": segment_key,
                    "start": start,
                    "end": end,
                    "duration_s": end - start,
                    "success": bool(scalar(group, "success")),
                    "text": text,
                    "action_family": action,
                    "object_name": object_name,
                    "external_rgb_samples": counts.get("external_rgb", 0),
                    "force_samples": counts.get("force", 0),
                    "proprioception_samples": counts.get("proprioception", 0),
                    "excluded_official_issue": excluded,
                    "matched_usable": matched,
                    "target_action": matched and action in CORE_ACTIONS,
                })
            files.append({
                "recording_id": recording_id,
                "source": config["source"],
                "split": config["split"],
                "condition": config["condition"],
                "bytes": path.stat().st_size,
                "segment_count": len(keys),
                "top_level_keys": sorted(handle.keys()),
                "required_fields": required,
            })

    with (args.output_dir / "segments.tsv").open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader(); writer.writerows(rows)
    with (args.output_dir / "files.json").open("x", encoding="utf-8") as stream:
        json.dump(files, stream, indent=2); stream.write("\n")

    target = [row for row in rows if row["target_action"]]
    action_counts = []
    for split in ("train_split1.txt", "test_split1.txt", "all"):
        split_rows = target if split == "all" else [row for row in target if row["split"] == split]
        for action in CORE_ACTIONS:
            action_rows = [row for row in split_rows if row["action_family"] == action]
            action_counts.append({
                "split": split,
                "action_family": action,
                "total": len(action_rows),
                "success": sum(bool(row["success"]) for row in action_rows),
                "failure": sum(not bool(row["success"]) for row in action_rows),
                "objects": len({row["object_name"] for row in action_rows}),
            })
    with (args.output_dir / "action_counts.tsv").open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(action_counts[0]), delimiter="\t")
        writer.writeheader(); writer.writerows(action_counts)

    combined = {row["action_family"]: row for row in action_counts if row["split"] == "all"}
    train = {row["action_family"]: row for row in action_counts if row["split"] == "train_split1.txt"}
    test = {row["action_family"]: row for row in action_counts if row["split"] == "test_split1.txt"}
    train_failures = sum(row["failure"] for row in train.values())
    test_failures = sum(row["failure"] for row in test.values())
    eligible_families = [action for action, row in combined.items() if row["success"] >= 3 and row["failure"] >= 3]
    cross_split_failure_families = [
        action for action in CORE_ACTIONS if train[action]["failure"] >= 2 and test[action]["failure"] >= 2
    ]
    text_outcomes: dict[str, set[bool]] = {}
    text_splits: dict[str, set[str]] = {}
    for row in target:
        text_outcomes.setdefault(row["text"], set()).add(bool(row["success"]))
        text_splits.setdefault(row["text"], set()).add(row["split"])
    all_schema_ok = all(all(item["required_fields"].values()) for item in files)
    total_failures = sum(not bool(row["success"]) for row in target)
    if not all_schema_ok or len(files) != 20:
        decision = "REJECT_ROUTE"
    elif (
        len(target) >= 300 and total_failures >= 30 and train_failures >= 20 and test_failures >= 8
        and len(eligible_families) >= 3 and len(cross_split_failure_families) >= 2
    ):
        decision = "PASS_DENOMINATOR"
    elif (
        len(target) >= 300 and total_failures >= 20 and train_failures >= 5 and test_failures >= 5
        and len(eligible_families) >= 2
    ):
        decision = "REFINE_ACTIONS"
    else:
        decision = "EXPAND_FIXED"

    summary = {
        "decision": decision,
        "files_expected": 20,
        "files_openable": len(files),
        "all_required_schema_ok": all_schema_ok,
        "segments_total": len(rows),
        "segments_matched_usable": sum(bool(row["matched_usable"]) for row in rows),
        "segments_excluded_official_issue": sum(bool(row["excluded_official_issue"]) for row in rows),
        "target_action_segments": len(target),
        "target_success": sum(bool(row["success"]) for row in target),
        "target_failure": total_failures,
        "train_failure": train_failures,
        "test_failure": test_failures,
        "eligible_action_families": eligible_families,
        "cross_split_failure_families": cross_split_failure_families,
        "exact_action_texts": len(text_outcomes),
        "exact_action_texts_with_both_outcomes": sorted(text for text, outcomes in text_outcomes.items() if len(outcomes) == 2),
        "exact_action_texts_shared_across_splits": sorted(text for text, splits in text_splits.items() if len(splits) == 2),
    }
    with (args.output_dir / "summary.json").open("x", encoding="utf-8") as stream:
        json.dump(summary, stream, indent=2); stream.write("\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
