#!/usr/bin/env python3
"""Range-fetch and verify a frozen subset of members from REASSEMBLE data.zip."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
import urllib.error
import urllib.request
import zlib
import zipfile
from pathlib import Path

from inspect_artifacts import HTTPRangeReader, local_data_offset


ARCHIVE_URL = "https://researchdata.tuwien.ac.at/api/records/0ewrv-8cb44/files/data.zip/content"
ARCHIVE_SIZE = 58_881_334_586


def load_frozen_members(path: Path) -> dict[str, dict[str, int | str]]:
    entries = {}
    with path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            if not row["name"].endswith(".h5"):
                continue
            entries[Path(row["name"]).stem] = {
                "name": row["name"],
                "compressed_bytes": int(row["compressed_bytes"]),
                "uncompressed_bytes": int(row["uncompressed_bytes"]),
                "header_offset": int(row["header_offset"]),
                "crc32": row["crc32"],
            }
    return entries


def open_range(start: int, end: int):
    request = urllib.request.Request(
        ARCHIVE_URL, headers={"Range": f"bytes={start}-{end}"}
    )
    for attempt in range(5):
        try:
            response = urllib.request.urlopen(request, timeout=120)
            if response.status != 206:
                response.close()
                raise RuntimeError(
                    f"range request returned HTTP {response.status}; refusing full response"
                )
            return response
        except urllib.error.HTTPError as error:
            if error.code not in {429, 500, 502, 503, 504} or attempt == 4:
                raise
            time.sleep(min(2**attempt, 30))
    raise RuntimeError("unreachable")


def fetch_member(info: zipfile.ZipInfo, data_offset: int, output_path: Path) -> dict[str, object]:
    if output_path.exists() or output_path.with_suffix(output_path.suffix + ".part").exists():
        raise FileExistsError(f"refusing to overwrite {output_path}")
    part_path = output_path.with_suffix(output_path.suffix + ".part")
    crc = 0
    digest = hashlib.sha256()
    output_bytes = 0
    decompressor = zlib.decompressobj(-zlib.MAX_WBITS) if info.compress_type == zipfile.ZIP_DEFLATED else None
    if info.compress_type not in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}:
        raise RuntimeError(f"unsupported ZIP method {info.compress_type} for {info.filename}")

    try:
        with open_range(data_offset, data_offset + info.compress_size - 1) as response:
            with part_path.open("xb") as output:
                while True:
                    compressed = response.read(1024 * 1024)
                    if not compressed:
                        break
                    plain = decompressor.decompress(compressed) if decompressor else compressed
                    if plain:
                        output.write(plain)
                        crc = zlib.crc32(plain, crc)
                        digest.update(plain)
                        output_bytes += len(plain)
                if decompressor:
                    plain = decompressor.flush()
                    if plain:
                        output.write(plain)
                        crc = zlib.crc32(plain, crc)
                        digest.update(plain)
                        output_bytes += len(plain)
        if output_bytes != info.file_size:
            raise RuntimeError(
                f"size mismatch for {info.filename}: {output_bytes} != {info.file_size}"
            )
        if (crc & 0xFFFFFFFF) != info.CRC:
            raise RuntimeError(f"CRC mismatch for {info.filename}")
        part_path.replace(output_path)
    except Exception:
        if part_path.exists():
            part_path.unlink()
        raise

    return {
        "recording_id": Path(info.filename).stem,
        "archive_member": info.filename,
        "compressed_bytes_transferred": info.compress_size,
        "extracted_bytes": output_bytes,
        "crc32": f"{crc & 0xFFFFFFFF:08x}",
        "sha256": digest.hexdigest(),
        "output": output_path.name,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--archive-members", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    selection = json.loads(args.selection.read_text(encoding="utf-8"))
    frozen = load_frozen_members(args.archive_members)
    args.output_dir.mkdir(parents=True, exist_ok=False)

    remote = HTTPRangeReader(ARCHIVE_URL, ARCHIVE_SIZE)
    with zipfile.ZipFile(remote) as archive:
        remote_infos = {Path(info.filename).stem: info for info in archive.infolist() if info.filename.endswith(".h5")}
        results = []
        for selected in selection["members"]:
            recording_id = selected["recording_id"]
            info = remote_infos[recording_id]
            expected = frozen[recording_id]
            if info.filename != expected["name"]:
                raise RuntimeError(f"member-name drift for {recording_id}")
            if info.compress_size != selected["compressed_bytes"] or info.compress_size != expected["compressed_bytes"]:
                raise RuntimeError(f"compressed-size drift for {recording_id}")
            if info.file_size != selected["uncompressed_bytes"] or info.file_size != expected["uncompressed_bytes"]:
                raise RuntimeError(f"uncompressed-size drift for {recording_id}")
            if info.header_offset != expected["header_offset"] or f"{info.CRC:08x}" != expected["crc32"]:
                raise RuntimeError(f"ZIP metadata drift for {recording_id}")
            offset = local_data_offset(remote, info)
            results.append(fetch_member(info, offset, args.output_dir / f"{recording_id}.h5"))

    manifest = {
        "archive_url": ARCHIVE_URL,
        "archive_size": ARCHIVE_SIZE,
        "selection": args.selection.name,
        "central_directory_range_requests": remote.requests,
        "central_directory_bytes_transferred": remote.bytes_transferred,
        "members": results,
        "total_compressed_bytes_transferred": sum(item["compressed_bytes_transferred"] for item in results),
        "total_extracted_bytes": sum(item["extracted_bytes"] for item in results),
    }
    with (args.output_dir / "download_manifest.json").open("x", encoding="utf-8") as stream:
        json.dump(manifest, stream, indent=2)
        stream.write("\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
