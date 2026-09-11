#!/usr/bin/env python3
"""Create label-concealed RGB comparison sheets for Q10 v3."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import h5py
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def read_rows(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    return {(row["recording_id"], row["segment_index"]): row for row in rows}


def nearest_index(values: np.ndarray, target: float) -> int:
    position = int(np.searchsorted(values, target))
    candidates = [max(0, position - 1), min(len(values) - 1, position)]
    return min(candidates, key=lambda index: abs(float(values[index]) - target))


def extract_frames(recording: Path, requests: dict[str, list[int]], temporary: Path) -> dict[str, list[Image.Image]]:
    with h5py.File(recording, "r") as handle:
        blob = bytes(handle["hama1"][()].tobytes())
    video = temporary / f"{recording.stem}.mp4"
    video.write_bytes(blob)
    wanted = sorted({index for indices in requests.values() for index in indices})
    expression = "+".join(f"eq(n\\,{index})" for index in wanted)
    frame_dir = temporary / recording.stem
    frame_dir.mkdir()
    pattern = frame_dir / "frame_%04d.png"
    command = [
        imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", str(video),
        "-vf", f"select={expression}", "-vsync", "vfr", str(pattern),
    ]
    subprocess.run(command, check=True)
    decoded = sorted(frame_dir.glob("frame_*.png"))
    if len(decoded) != len(wanted):
        raise RuntimeError(f"decoded {len(decoded)} frames but expected {len(wanted)} for {recording.name}")
    by_index = {index: Image.open(path).convert("RGB") for index, path in zip(wanted, decoded)}
    return {case_id: [by_index[index].copy() for index in indices] for case_id, indices in requests.items()}


def make_strip(frames: list[Image.Image], title: str) -> Image.Image:
    target_width = 320
    resized = []
    for frame in frames:
        height = round(frame.height * target_width / frame.width)
        resized.append(frame.resize((target_width, height), Image.Resampling.LANCZOS))
    header = 42
    canvas = Image.new("RGB", (target_width * len(resized), header + max(im.height for im in resized)), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((10, 8), title, fill="black", font=ImageFont.load_default(size=20))
    for position, frame in enumerate(resized):
        canvas.paste(frame, (position * target_width, header))
        draw.text((position * target_width + 7, header + 7), f"t{position + 1}", fill="yellow", stroke_width=2, stroke_fill="black")
    return canvas


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--segments", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        raise RuntimeError(f"output directory is not empty: {args.output_dir}")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    rows = read_rows(args.segments)
    case_metadata = {}
    requests_by_recording: dict[str, dict[str, list[int]]] = {}
    for pair in protocol["pairs"]:
        for role in ("failure", "control"):
            spec = pair[role]
            key = (spec["recording_id"], spec["segment_index"])
            row = rows[key]
            expected_success = role == "control"
            if row["matched_usable"] != "True" or (row["success"] == "True") != expected_success:
                raise RuntimeError(f"v2 row does not satisfy frozen role: {pair['pair_id']} {role}")
            start, end = float(row["start"]), float(row["end"])
            with h5py.File(args.input_dir / f"{spec['recording_id']}.h5", "r") as handle:
                timestamps = np.asarray(handle["timestamps/hama1"][...]).reshape(-1)
            targets = [start + fraction * (end - start) for fraction in protocol["frame_fractions"]]
            indices = [nearest_index(timestamps, target) for target in targets]
            case_id = f"{pair['pair_id']}_{role}"
            requests_by_recording.setdefault(spec["recording_id"], {})[case_id] = indices
            case_metadata[case_id] = {
                "recording_id": spec["recording_id"],
                "segment_index": spec["segment_index"],
                "action_text": row["text"],
                "frame_indices": indices,
                "target_timestamps": targets,
                "nearest_timestamps": [float(timestamps[index]) for index in indices],
            }

    frames = {}
    with tempfile.TemporaryDirectory(prefix="q10-v3-") as temp_name:
        temporary = Path(temp_name)
        for recording_id, requests in requests_by_recording.items():
            frames.update(extract_frames(args.input_dir / f"{recording_id}.h5", requests, temporary))

    key_rows = []
    annotation_rows = []
    for pair in protocol["pairs"]:
        pair_id = pair["pair_id"]
        swap = hashlib.sha256(f"{protocol['assignment_seed']}:{pair_id}".encode()).digest()[0] % 2 == 1
        roles = ["control", "failure"] if swap else ["failure", "control"]
        assignments = {"A": roles[0], "B": roles[1]}
        strips = []
        for display in ("A", "B"):
            role = assignments[display]
            strips.append(make_strip(frames[f"{pair_id}_{role}"], f"{pair_id} / {display} / {pair['action_family']}"))
        gap = 8
        comparison = Image.new("RGB", (max(im.width for im in strips), sum(im.height for im in strips) + gap), "#444444")
        comparison.paste(strips[0], (0, 0))
        comparison.paste(strips[1], (0, strips[0].height + gap))
        comparison.save(args.output_dir / f"{pair_id}_comparison.png", optimize=True)
        key_rows.append({
            "pair_id": pair_id,
            "action_family": pair["action_family"],
            "A_role": assignments["A"],
            "B_role": assignments["B"],
            "control_rule": pair["control_rule"],
        })
        annotation_rows.append({
            "pair_id": pair_id,
            "action_family": pair["action_family"],
            "judgment": "",
            "confidence_1_to_3": "",
            "visible_cue": "",
            "notes": "",
        })

    with (args.output_dir / "ground_truth_key.tsv").open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(key_rows[0]), delimiter="\t")
        writer.writeheader(); writer.writerows(key_rows)
    with (args.output_dir / "annotation.tsv").open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(annotation_rows[0]), delimiter="\t")
        writer.writeheader(); writer.writerows(annotation_rows)
    with (args.output_dir / "frame_metadata.json").open("x", encoding="utf-8") as stream:
        json.dump(case_metadata, stream, indent=2); stream.write("\n")
    print(json.dumps({"pairs": len(protocol["pairs"]), "comparison_images": len(protocol["pairs"])}, indent=2))


if __name__ == "__main__":
    main()
