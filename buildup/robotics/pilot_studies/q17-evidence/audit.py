"""Bounded ActiveArena evidence/label contract audit; run only inside Q17 Docker."""

from __future__ import annotations

import hashlib
import json
import os
import random
import re
import sys
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq


DATASET_ROOT = Path("/dataset")
SOURCE_ROOT = Path("/source")
OUTPUT_ROOT = Path("/output")
TARGET_PATTERN = re.compile(r"with a (\w+) pad on its back side", re.IGNORECASE)
PARQUET_IDS = (0, 1, 2)


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def target_color(text: str) -> str | None:
    match = TARGET_PATTERN.search(text)
    return match.group(1).lower() if match else None


def contains_color_word(text: str, color: str) -> bool:
    return re.search(r"\b" + re.escape(color) + r"\b", text, flags=re.IGNORECASE) is not None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def evaluate_metadata() -> dict:
    meta = DATASET_ROOT / "meta"
    info = json.loads((meta / "info.json").read_text())
    tasks = read_jsonl(meta / "tasks.jsonl")
    episodes = read_jsonl(meta / "episodes.jsonl")
    subtasks = json.loads((meta / "astribot_subtask_metadata.json").read_text())["episodes"]
    assert len(episodes) == len(subtasks) == info["total_episodes"] == 100
    task_colors = {item["task_index"]: target_color(item["task"]) for item in tasks}
    assert len(task_colors) == 6 and None not in task_colors.values()

    task_text_leak = 0
    subtask_text_leak = 0
    mismatches = []
    color_counts = Counter()
    for item, subtask in zip(episodes, subtasks):
        index = item["episode_index"]
        color = task_colors[int(subtask["task_index"])] if "task_index" in subtask else target_color(item["tasks"][0])
        color_counts[color] += 1
        task_instruction = subtask["task_instruction"]
        if contains_color_word(task_instruction, color):
            task_text_leak += 1
        mapping = subtask["subtask_instruction_map"]
        if any(contains_color_word(text, color) for text in mapping.values()):
            subtask_text_leak += 1
        if target_color(task_instruction) != color:
            mismatches.append(index)
    assert not mismatches

    return {
        "episode_count": len(episodes),
        "task_count": len(tasks),
        "color_counts": dict(sorted(color_counts.items())),
        "task_instruction_contains_target_color": task_text_leak,
        "any_subtask_instruction_contains_target_color": subtask_text_leak,
        "task_label_mismatch_episode_indices": mismatches,
        "metadata_files": {path.name: {"bytes": path.stat().st_size, "sha256": sha256(path)} for path in sorted(meta.iterdir()) if path.is_file()},
    }


def evaluate_instruction_route() -> dict:
    sys.path.insert(0, str(SOURCE_ROOT / "description" / "utils"))
    from generate_episode_instructions import generate_episode_descriptions

    random.seed(1729)
    result = {}
    for split in ("info_gathering_demo", "info_gathering_randomized"):
        seed_path = SOURCE_ROOT / "eval_seed_lists" / split / "check_block_color.json"
        payload = json.loads(seed_path.read_text())
        entries = payload["entries"][:50]
        instructions = generate_episode_descriptions("check_block_color", [item["info"] for item in entries], max_descriptions=5)
        assert len(instructions) == len(entries) == 50
        counts = Counter()
        by_seed = []
        for entry, item in zip(entries, instructions):
            color = str(entry["info"]["{C}"]).lower()
            seen = item["seen"]
            unseen = item["unseen"]
            seen_leaks = sum(contains_color_word(text, color) for text in seen)
            unseen_leaks = sum(contains_color_word(text, color) for text in unseen)
            counts["seen_instructions"] += len(seen)
            counts["unseen_instructions"] += len(unseen)
            counts["seen_reveal_target"] += seen_leaks
            counts["unseen_reveal_target"] += unseen_leaks
            by_seed.append({"seed": entry["seed"], "target_color": color, "seen_reveal_target": seen_leaks, "unseen_reveal_target": unseen_leaks})
        result[split] = {"seed_count": len(entries), **dict(counts), "first_three": by_seed[:3], "seed_file_sha256": sha256(seed_path)}
    return result


def image_bytes(value) -> bytes:
    if isinstance(value, dict) and isinstance(value.get("bytes"), bytes):
        return value["bytes"]
    if isinstance(value, bytes):
        return value
    raise TypeError(f"Unexpected image field type: {type(value)}")


def evaluate_episodes() -> dict:
    episodes = {item["episode_index"]: item for item in read_jsonl(DATASET_ROOT / "meta" / "episodes.jsonl")}
    result = {}
    frame_root = OUTPUT_ROOT / "frames"
    frame_root.mkdir(parents=True, exist_ok=True)
    for episode_id in PARQUET_IDS:
        parquet_path = DATASET_ROOT / "data" / "chunk-000" / f"episode_{episode_id:06d}.parquet"
        table = pq.read_table(parquet_path)
        columns = list(table.column_names)
        frame_count = table.num_rows
        assert frame_count == episodes[episode_id]["length"]
        stage_values = table.column("stage").to_pylist()
        subtask_values = table.column("subtask_index").to_pylist()
        counts = Counter(f"{subtask}:{stage}" for subtask, stage in zip(subtask_values, stage_values))
        choices = {"first": 0, "last": frame_count - 1}
        for label, predicate in (
            ("inspect", lambda s, g: s == 2 and g == 3),
            ("restore", lambda s, g: s == 3 and g == 3),
            ("place_start", lambda s, g: s == 4 and g == 1),
            ("place_action", lambda s, g: s == 4 and g == 3),
        ):
            matches = [i for i, (s, g) in enumerate(zip(subtask_values, stage_values)) if predicate(s, g)]
            if matches:
                choices[label] = matches[0] if label not in ("inspect", "place_action") else matches[len(matches) // 2]
        images = table.column("observation.images.camera_head")
        saved = {}
        for label, row_index in choices.items():
            path = frame_root / f"episode_{episode_id:06d}_{label}_{row_index:04d}.png"
            payload = image_bytes(images[row_index].as_py())
            assert payload[:8] == b"\x89PNG\r\n\x1a\n"
            path.write_bytes(payload)
            saved[label] = {"row": row_index, "path": str(path), "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}
        result[str(episode_id)] = {
            "parquet_bytes": parquet_path.stat().st_size,
            "parquet_sha256": sha256(parquet_path),
            "rows": frame_count,
            "columns": columns,
            "subtask_stage_counts": dict(sorted(counts.items())),
            "saved_frames": saved,
        }
    return result


def main() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    result = {
        "purpose": "exploratory data/instruction contract audit; no policy rollouts",
        "dataset_revision": "4fc698d7b3c1871c342181a5fa38f837da945a80",
        "source_commit": os.environ.get("Q17_SOURCE_COMMIT", "unknown"),
        "metadata": evaluate_metadata(),
        "instructions": evaluate_instruction_route(),
        "episodes": evaluate_episodes(),
    }
    path = OUTPUT_ROOT / "audit.json"
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"output": str(path), "metadata": result["metadata"], "instructions": result["instructions"], "episode_rows": {key: value["rows"] for key, value in result["episodes"].items()}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
