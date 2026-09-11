#!/usr/bin/env python3
"""Inspect a frozen REASSEMBLE HDF5 subset without decoding media payloads."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import h5py
import numpy as np


def scalar(group: h5py.Group, name: str):
    value = group[name][...]
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if isinstance(value, np.ndarray) and value.shape == ():
        value = value.item()
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if isinstance(value, np.generic):
        return value.item()
    return value


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dataset_index(handle: h5py.File) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}

    def visitor(name: str, obj) -> None:
        if isinstance(obj, h5py.Dataset):
            result[name] = {
                "shape": list(obj.shape),
                "dtype": str(obj.dtype),
                "storage_bytes": int(obj.id.get_storage_size()),
            }

    handle.visititems(visitor)
    return result


def find_path(paths: set[str], prefixes: tuple[str, ...], needles: tuple[str, ...]) -> str | None:
    for exact in prefixes:
        if exact in paths:
            return exact
    candidates = sorted(
        path for path in paths if path.startswith("timestamps/") and any(needle in path for needle in needles)
    )
    return candidates[0] if candidates else None


def count_in_window(values: np.ndarray, start: float, end: float) -> int:
    flat = np.asarray(values).reshape(-1)
    if len(flat) == 0:
        return 0
    left = int(np.searchsorted(flat, start, side="left"))
    right = int(np.searchsorted(flat, end, side="right"))
    return max(0, right - left)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    selection = json.loads(args.selection.read_text(encoding="utf-8"))
    selected = {item["recording_id"]: item for item in selection["members"]}
    output_files = sorted(args.output_dir.iterdir()) if args.output_dir.exists() else []
    if output_files:
        raise RuntimeError(f"output directory is not empty: {args.output_dir}")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    file_results = []
    segment_rows = []
    openable = 0
    for recording_id, config in selected.items():
        path = args.input_dir / f"{recording_id}.h5"
        result = {
            "recording_id": recording_id,
            "split": config["split"],
            "condition": config["condition"],
            "bytes": path.stat().st_size,
            "sha256": file_sha256(path),
        }
        with h5py.File(path, "r") as handle:
            openable += 1
            datasets = dataset_index(handle)
            paths = set(datasets)
            result["top_level_keys"] = sorted(handle.keys())
            result["datasets"] = datasets

            rgb_ts = find_path(paths, ("timestamps/hama1",), ("hama1",))
            hand_ts = find_path(paths, ("timestamps/hand",), ("hand",))
            force_ts = find_path(
                paths,
                ("timestamps/measured_force", "timestamps/compensated_base_force"),
                ("measured_force", "compensated_base_force"),
            )
            proprio_ts = find_path(
                paths,
                ("timestamps/pose", "timestamps/joint_positions", "timestamps/gripper_positions"),
                ("pose", "joint_positions", "gripper_positions"),
            )
            result["representative_timestamps"] = {
                "external_rgb": rgb_ts,
                "hand_rgb": hand_ts,
                "force": force_ts,
                "proprioception": proprio_ts,
            }

            required = {
                "external_rgb_data": "hama1" in paths,
                "external_rgb_timestamp": rgb_ts is not None,
                "force_data": any(path.startswith("robot_state/") and ("force" in path or "torque" in path) for path in paths),
                "force_timestamp": force_ts is not None,
                "proprioception_data": any(path.startswith("robot_state/") and any(key in path for key in ("pose", "joint_positions", "gripper_positions")) for path in paths),
                "proprioception_timestamp": proprio_ts is not None,
                "segments_info": "segments_info" in handle,
            }
            result["required_fields"] = required

            segment_group = handle["segments_info"]
            segment_keys = sorted(segment_group.keys(), key=lambda value: int(value))
            for position, segment_key in enumerate(segment_keys):
                group = segment_group[segment_key]
                start = float(scalar(group, "start"))
                end = float(scalar(group, "end"))
                success = bool(scalar(group, "success"))
                text = str(scalar(group, "text"))
                excluded = (
                    config["condition"] == "force/torque not valid for last action"
                    and position == len(segment_keys) - 1
                )
                counts = {
                    "external_rgb": count_in_window(handle[rgb_ts][...], start, end) if rgb_ts else 0,
                    "hand_rgb": count_in_window(handle[hand_ts][...], start, end) if hand_ts else 0,
                    "force": count_in_window(handle[force_ts][...], start, end) if force_ts else 0,
                    "proprioception": count_in_window(handle[proprio_ts][...], start, end) if proprio_ts else 0,
                }
                matched = not excluded and counts["external_rgb"] > 0 and counts["force"] > 0 and counts["proprioception"] > 0
                segment_rows.append(
                    {
                        "recording_id": recording_id,
                        "split": config["split"],
                        "condition": config["condition"],
                        "segment_index": segment_key,
                        "start": start,
                        "end": end,
                        "success": success,
                        "text": text,
                        **{f"{key}_samples": value for key, value in counts.items()},
                        "excluded_official_issue": excluded,
                        "matched_usable": matched,
                    }
                )
            result["segment_count"] = len(segment_keys)
        file_results.append(result)

    fieldnames = list(segment_rows[0])
    with (args.output_dir / "segments.tsv").open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(segment_rows)
    with (args.output_dir / "files.json").open("x", encoding="utf-8") as stream:
        json.dump(file_results, stream, indent=2, ensure_ascii=False)
        stream.write("\n")

    matched_rows = [row for row in segment_rows if row["matched_usable"]]
    success_counts = Counter(bool(row["success"]) for row in matched_rows)
    clean_results = [item for item in file_results if item["condition"] == "no documented issue"]
    all_files_open = openable == len(selected)
    clean_schema_ok = all(all(item["required_fields"].values()) for item in clean_results)
    excluded_count = sum(bool(row["excluded_official_issue"]) for row in segment_rows)
    if not all_files_open or not clean_schema_ok:
        decision = "REJECT_ROUTE"
    elif not matched_rows:
        decision = "REFINE_TARGET"
    elif not success_counts[True] or not success_counts[False]:
        decision = "REFINE_DENOMINATOR"
    elif excluded_count != 1:
        decision = "REFINE_TARGET"
    else:
        decision = "PASS_SCHEMA"

    summary = {
        "decision": decision,
        "files_selected": len(selected),
        "files_openable": openable,
        "clean_schema_ok": clean_schema_ok,
        "segments_total": len(segment_rows),
        "segments_matched_usable": len(matched_rows),
        "segments_excluded_official_issue": excluded_count,
        "matched_success": success_counts[True],
        "matched_failure": success_counts[False],
        "matched_action_text_counts": Counter(row["text"] for row in matched_rows),
    }
    summary["matched_action_text_counts"] = dict(summary["matched_action_text_counts"])
    with (args.output_dir / "summary.json").open("x", encoding="utf-8") as stream:
        json.dump(summary, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
