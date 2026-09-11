#!/usr/bin/env python3
"""Create the pre-fixed, label-blind Q10 v4 selection from v1 metadata."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


SEED = "q10-v4-20260906"
TAKE = {"train_split1.txt": 12, "test_split1.txt": 4}
ISSUE_IDS = {
    "2025-01-10-15-28-50", "2025-01-10-16-17-40", "2025-01-10-17-10-38",
    "2025-01-10-17-54-09", "2025-01-11-14-22-09", "2025-01-11-14-45-48",
    "2025-01-11-15-27-19", "2025-01-11-15-35-08", "2025-01-13-11-16-17",
    "2025-01-13-11-18-57",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive-members", type=Path, required=True)
    parser.add_argument("--split-members", type=Path, required=True)
    parser.add_argument("--anchors", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite {args.output}")

    with args.archive_members.open(newline="", encoding="utf-8") as stream:
        archive = {
            Path(row["name"]).stem: row for row in csv.DictReader(stream, delimiter="\t")
            if row["name"].endswith(".h5")
        }
    with args.split_members.open(newline="", encoding="utf-8") as stream:
        split = {row["filename"]: row["split"] for row in csv.DictReader(stream, delimiter="\t")}
    anchor_config = json.loads(args.anchors.read_text(encoding="utf-8"))["members"]
    anchor_ids = {item["recording_id"] for item in anchor_config}

    members = []
    for split_name, count in TAKE.items():
        candidates = [
            recording_id for recording_id, observed_split in split.items()
            if observed_split == split_name and recording_id not in anchor_ids and recording_id not in ISSUE_IDS
        ]
        ranked = sorted(
            candidates,
            key=lambda recording_id: (
                hashlib.sha256(f"{SEED}:{recording_id}".encode()).hexdigest(), recording_id
            ),
        )
        for recording_id in ranked[:count]:
            row = archive[recording_id]
            members.append({
                "recording_id": recording_id,
                "split": split_name,
                "condition": "no documented issue",
                "archive_member": row["name"],
                "compressed_bytes": int(row["compressed_bytes"]),
                "uncompressed_bytes": int(row["uncompressed_bytes"]),
                "header_offset": int(row["header_offset"]),
                "crc32": row["crc32"],
                "selection_hash": hashlib.sha256(f"{SEED}:{recording_id}".encode()).hexdigest(),
            })

    denominator_members = [
        {
            "recording_id": item["recording_id"], "split": item["split"],
            "condition": item["condition"], "source": "v2_anchor",
        }
        for item in anchor_config
    ] + [
        {
            "recording_id": item["recording_id"], "split": item["split"],
            "condition": item["condition"], "source": "v4_new",
        }
        for item in members
    ]
    result = {
        "version": "v4",
        "created_kst": "2026-09-06",
        "archive_url": "https://researchdata.tuwien.ac.at/api/records/0ewrv-8cb44/files/data.zip/content",
        "seed": SEED,
        "algorithm": (
            "Within each official split, exclude v2 anchors and every official issue-listed ID; "
            "sort remaining IDs by SHA256(seed + colon + recording_id), then take 12 train and 4 test."
        ),
        "members": members,
        "anchors": denominator_members[:len(anchor_config)],
        "denominator_members": denominator_members,
        "expected_new_compressed_bytes": sum(item["compressed_bytes"] for item in members),
        "expected_new_uncompressed_bytes": sum(item["uncompressed_bytes"] for item in members),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")


if __name__ == "__main__":
    main()
