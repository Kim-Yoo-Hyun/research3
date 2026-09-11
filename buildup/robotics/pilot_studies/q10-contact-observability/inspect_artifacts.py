#!/usr/bin/env python3
"""Inspect pinned REASSEMBLE metadata without downloading the full data archive."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import statistics
import struct
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path


EXPECTED_SMALL = {
    "README.txt": "2e1394a2fa65e4ebb6c1fd64136cb0a0",
    "splits.zip": "641882928ef3a8b2c3db41ac7c60b994",
}
EXPECTED_DATA_SIZE = 58_881_334_586
EXPECTED_DATA_MD5 = "812103a652ca9201e87a3bcecfee4ef3"


class HTTPRangeReader(io.RawIOBase):
    def __init__(self, url: str, size: int):
        self.url = url
        self.size = size
        self.pos = 0
        self.bytes_transferred = 0
        self.requests = 0

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.pos

    def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
        if whence == io.SEEK_SET:
            new_pos = offset
        elif whence == io.SEEK_CUR:
            new_pos = self.pos + offset
        elif whence == io.SEEK_END:
            new_pos = self.size + offset
        else:
            raise ValueError(f"unsupported whence: {whence}")
        if new_pos < 0:
            raise ValueError("negative seek")
        self.pos = min(new_pos, self.size)
        return self.pos

    def read(self, size: int = -1) -> bytes:
        if self.pos >= self.size:
            return b""
        if size is None or size < 0:
            size = self.size - self.pos
        end = min(self.pos + size, self.size) - 1
        request = urllib.request.Request(
            self.url, headers={"Range": f"bytes={self.pos}-{end}"}
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            if response.status != 206:
                raise RuntimeError(
                    f"range request returned HTTP {response.status}; refusing full response"
                )
            data = response.read()
        expected = end - self.pos + 1
        if len(data) != expected:
            raise RuntimeError(f"short range response: expected {expected}, got {len(data)}")
        self.pos += len(data)
        self.bytes_transferred += len(data)
        self.requests += 1
        return data


def md5(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean_split_line(line: str) -> str | None:
    value = line.strip()
    if not value or value.startswith("#"):
        return None
    return Path(value).name


def recording_id(value: str) -> str:
    """Normalize official extensionless split IDs and archive .h5 names."""
    return Path(value).stem


def read_splits(path: Path) -> tuple[dict[str, list[str]], list[str]]:
    split_entries: dict[str, list[str]] = {}
    members: list[str] = []
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            members.append(info.filename)
            raw = archive.read(info).decode("utf-8")
            values = [v for line in raw.splitlines() if (v := clean_split_line(line))]
            split_entries[Path(info.filename).name] = values
    return split_entries, members


def find_lines(paths: list[Path], terms: dict[str, tuple[str, ...]]) -> dict[str, list[str]]:
    found = {key: [] for key in terms}
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), start=1):
            lowered = line.lower()
            for key, needles in terms.items():
                if any(needle.lower() in lowered for needle in needles):
                    found[key].append(f"{path.name}:{lineno}:{line.strip()}")
    return found


def local_data_offset(reader: HTTPRangeReader, info: zipfile.ZipInfo) -> int:
    reader.seek(info.header_offset)
    fixed = reader.read(30)
    signature, _, flag_bits, _, _, _, _, _, _, name_len, extra_len = struct.unpack(
        "<IHHHHHIIIHH", fixed
    )
    if signature != 0x04034B50:
        raise RuntimeError("invalid local ZIP header signature")
    if flag_bits & 0x1:
        raise RuntimeError("encrypted ZIP member")
    return info.header_offset + 30 + name_len + extra_len


def write_tsv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with path.open("x", encoding="utf-8") as stream:
        stream.write("\t".join(header) + "\n")
        for row in rows:
            stream.write("\t".join(str(value) for value in row) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=False)
    record = json.loads((args.input_dir / "record.json").read_text(encoding="utf-8"))

    integrity = {}
    for name, expected in EXPECTED_SMALL.items():
        actual = md5(args.input_dir / name)
        integrity[name] = {"expected_md5": expected, "actual_md5": actual, "ok": actual == expected}

    data_entry = record["files"]["entries"]["data.zip"]
    record_ok = (
        record["id"] == "0ewrv-8cb44"
        and record["metadata"]["version"] == "1.0.0"
        and record["access"]["files"] == "public"
        and data_entry["size"] == EXPECTED_DATA_SIZE
        and data_entry["checksum"] == f"md5:{EXPECTED_DATA_MD5}"
    )

    split_entries, split_zip_members = read_splits(args.input_dir / "splits.zip")
    split_names = sorted(split_entries)
    if len(split_names) != 2:
        raise RuntimeError(f"expected two split files, found {split_names}")
    left, right = (split_entries[name] for name in split_names)
    left_counts, right_counts = Counter(left), Counter(right)
    duplicates = {
        split_names[0]: sorted(name for name, count in left_counts.items() if count > 1),
        split_names[1]: sorted(name for name, count in right_counts.items() if count > 1),
    }
    overlap = sorted(set(left) & set(right))

    reader = HTTPRangeReader(data_entry["links"]["content"], data_entry["size"])
    with zipfile.ZipFile(reader) as remote_zip:
        infos = remote_zip.infolist()
        h5_infos = [info for info in infos if not info.is_dir() and info.filename.endswith(".h5")]
        sample_offset = local_data_offset(reader, h5_infos[0]) if h5_infos else None

    archive_by_id = {recording_id(info.filename): info.filename for info in h5_infos}
    assigned = {recording_id(value) for value in left} | {recording_id(value) for value in right}
    split_missing = sorted(assigned - set(archive_by_id))
    archive_unassigned = sorted(set(archive_by_id) - assigned)

    source_paths = sorted((args.input_dir / "source").glob("*.txt"))
    required_terms = {
        "rgb": ("hama1", "hama2", "hand"),
        "timestamps": ("timestamp",),
        "force_torque": ("measured_force", "compensated_base_force", "measured_torque"),
        "proprioception": ("joint_positions", "gripper_positions", "pose"),
        "segments": ("segments_info", "segment"),
        "success": ("success",),
        "start_end": ("start", "end"),
        "text": ("text",),
    }
    schema_evidence = find_lines(source_paths, required_terms)
    schema_ok = all(schema_evidence[key] for key in required_terms)
    split_ok = bool(left) and bool(right) and not overlap and not any(duplicates.values())
    mapping_ok = not split_missing
    range_ok = bool(h5_infos) and sample_offset is not None
    exact_counts_without_h5 = False

    if not all(item["ok"] for item in integrity.values()) or not record_ok:
        decision = "REJECT_ROUTE"
    elif split_ok and mapping_ok and schema_ok and range_ok and exact_counts_without_h5:
        decision = "PASS_METADATA"
    elif split_ok and mapping_ok and schema_ok and range_ok:
        decision = "REFINE_SUBSET"
    elif split_ok and mapping_ok and range_ok:
        decision = "REFINE_TARGET"
    else:
        decision = "REJECT_ROUTE"

    member_rows = [
        [
            info.filename,
            info.compress_type,
            info.compress_size,
            info.file_size,
            info.header_offset,
            f"{info.CRC:08x}",
            info.flag_bits,
        ]
        for info in infos
    ]
    write_tsv(
        args.output_dir / "archive_members.tsv",
        ["name", "compress_type", "compressed_bytes", "uncompressed_bytes", "header_offset", "crc32", "flag_bits"],
        member_rows,
    )
    split_rows = [
        [split_name, index, filename]
        for split_name in split_names
        for index, filename in enumerate(split_entries[split_name])
    ]
    write_tsv(args.output_dir / "split_members.tsv", ["split", "index", "filename"], split_rows)

    result = {
        "decision": decision,
        "record": {
            "id": record["id"],
            "revision_id": record["revision_id"],
            "version": record["metadata"]["version"],
            "license": [right["id"] for right in record["metadata"].get("rights", [])],
            "record_ok": record_ok,
        },
        "integrity": integrity,
        "split_zip_members": split_zip_members,
        "splits": {
            name: {
                "count": len(split_entries[name]),
                "unique_count": len(set(split_entries[name])),
                "duplicates": duplicates[name],
            }
            for name in split_names
        },
        "split_overlap": overlap,
        "archive": {
            "member_count": len(infos),
            "h5_count": len(h5_infos),
            "h5_total_compressed_bytes": sum(info.compress_size for info in h5_infos),
            "h5_total_uncompressed_bytes": sum(info.file_size for info in h5_infos),
            "h5_min_compressed_bytes": min(info.compress_size for info in h5_infos),
            "h5_median_compressed_bytes": statistics.median(info.compress_size for info in h5_infos),
            "h5_max_compressed_bytes": max(info.compress_size for info in h5_infos),
            "split_id_normalization": "Path(value).stem; official split IDs omit .h5",
            "split_missing": split_missing,
            "unassigned_h5": archive_unassigned,
            "sample_h5": h5_infos[0].filename if h5_infos else None,
            "sample_data_offset": sample_offset,
            "range_requests": reader.requests,
            "range_bytes_transferred": reader.bytes_transferred,
            "full_archive_bytes": data_entry["size"],
            "metadata_fraction": reader.bytes_transferred / data_entry["size"],
            "bounded_member_range_derivable": range_ok,
        },
        "schema_evidence": schema_evidence,
        "schema_ok": schema_ok,
        "exact_matched_segment_denominator_without_h5": exact_counts_without_h5,
    }
    with (args.output_dir / "result.json").open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
