"""Explore visibility of known old points; not an object-localization evaluator."""
import argparse
import csv
import hashlib
import io
import json
import platform
import struct
import zlib
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from inspect_input import CpuUnpickler


def write_png(path, rgb):
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    height, width, _ = rgb.shape
    def chunk(kind, content):
        return struct.pack('!I', len(content)) + kind + content + struct.pack('!I', zlib.crc32(kind + content))
    rows = b''.join(b'\x00' + row.tobytes() for row in rgb)
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!2I5B', width, height, 8, 2, 0, 0, 0))
                     + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b''))


def project(point, pose, intrinsics, depth):
    camera = np.linalg.solve(pose, np.r_[point, 1.])[:3]
    z = float(camera[2])
    row = {"camera_z": z, "uv": None, "depth_median": None, "residual": None}
    if z <= 0:
        return row | {"state": "behind_camera"}
    pixel = intrinsics @ camera
    u, v = pixel[:2] / pixel[2]
    row["uv"] = [float(u), float(v)]
    h, w = depth.shape
    if not (1 <= u < w - 1 and 1 <= v < h - 1):
        return row | {"state": "outside_view"}
    if not (0.1 < z <= 2.0):
        return row | {"state": "outside_range"}
    x, y = int(np.rint(u)), int(np.rint(v))
    patch = depth[y-1:y+2, x-1:x+2]
    valid = np.isfinite(patch) & (patch > 0.1) & (patch <= 2.0)
    row["valid_depth_pixels"] = int(valid.sum())
    if valid.sum() < 5:
        return row | {"state": "insufficient_depth"}
    median = float(np.median(patch[valid]))
    residual = median - z
    row.update(depth_median=median, residual=residual)
    return row | {"state": "free_space" if residual > 0.05 else
                  "occluded" if residual < -0.05 else "surface_consistent"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    raw = (args.input / 'env.pkl').read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == '9b4f894a63556563fe7bc856d32131948b2b5df495d1aab5b88a2dc1834b1897'
    data = CpuUnpickler(io.BytesIO(raw)).load()
    required = ['rgb', 'depth', 'camera_poses', 'camera_K']
    lengths = {key: len(data[key]) for key in required}
    assert len(set(lengths.values())) == 1
    n = lengths['depth']
    arrays = {key: [v.detach().cpu().numpy() if isinstance(v, torch.Tensor) else np.asarray(v)
                    for v in data[key]] for key in required}
    for idx in range(n):
        pose, k = arrays['camera_poses'][idx], arrays['camera_K'][idx]
        depth, rgb = arrays['depth'][idx], arrays['rgb'][idx]
        assert pose.shape == (4, 4) and k.shape == (3, 3)
        assert np.isfinite(pose).all() and np.isfinite(k).all()
        assert np.allclose(pose[3], [0, 0, 0, 1], atol=1e-4)
        assert np.allclose(pose[:3, :3].T @ pose[:3, :3], np.eye(3), atol=1e-3)
        assert abs(np.linalg.det(pose[:3, :3]) - 1) < 1e-3
        assert k[0, 0] > 0 and k[1, 1] > 0
        assert np.allclose(k[2], [0, 0, 1], atol=1e-5)
        assert depth.shape == rgb.shape[:2] and depth.ndim == 2
    with (args.input / '14.csv').open() as handle:
        labels = {row['query']: row for row in csv.DictReader(handle)}
    points = {name: [float(labels[name][axis]) for axis in ['x', 'y', 'z']]
              for name in ['metal bowl', 'orange']}
    # Interior of checkpoints 14 and 26 under common index/count conventions. No official timing claim.
    interval = list(range(15, 25))
    trace, summaries = [], {}
    worst_projection_error = 0.
    for name, point in points.items():
        rows = []
        for idx in range(n):
            pose, k, depth = arrays['camera_poses'][idx], arrays['camera_K'][idx], arrays['depth'][idx]
            row = {"query": name, "array_index": idx, **project(point, pose, k, depth)}
            # Independent rigid-transform expression for the projective calculation.
            camera2 = pose[:3, :3].T @ (np.asarray(point) - pose[:3, 3])
            camera1 = np.linalg.solve(pose, np.r_[point, 1.])[:3]
            worst_projection_error = max(worst_projection_error, float(np.max(np.abs(camera1 - camera2))))
            rows.append(row)
        trace.extend(rows)
        interior = [rows[idx] for idx in interval]
        phases = []
        for phase in range(5):
            selected = interval[phase::5]
            phases.append({"phase": phase, "selected": selected,
                           "free_space_hits": sum(rows[idx]['state'] == 'free_space' for idx in selected)})
        # Causal control scans each frame until the first positive geometric contradiction; at most one write.
        first = next((idx for idx in interval if rows[idx]['state'] == 'free_space'), None)
        selected = [] if first is None else [first]
        summaries[name] = {"oracle_initial_point": point,
                           "initial_states_0_to_13": dict(Counter(r['state'] for r in rows[:14])),
                           "interior_states": dict(Counter(r['state'] for r in interior)),
                           "free_space_indices": [r['array_index'] for r in interior if r['state'] == 'free_space'],
                           "periodic_phases_two_reads_each": phases,
                           "causal_first_evidence": {"selected": selected, "point_updates": len(selected),
                               "depth_frames_read": len(interval) if first is None else interval.index(first) + 1},
                           "claim": "point-evidence coverage only; different read costs, no equal-compute gain"}
        for idx in [10, 15, 20, 24]:
            rgb = arrays['rgb'][idx].copy()
            if np.nanmax(rgb) <= 1.0:
                rgb *= 255
            uv = rows[idx]['uv']
            if uv is not None:
                u, v = [int(round(x)) for x in uv]
                h, w = rgb.shape[:2]
                if 0 <= u < w and 0 <= v < h:
                    rgb[max(0,v-3):min(h,v+4), max(0,u-3):min(w,u+4)] = [255, 0, 255]
            write_png(args.output / f"{name.replace(' ', '_')}_{idx}.png", rgb)
    assert worst_projection_error < 1e-3
    with (args.output / 'trace.jsonl').open('w') as handle:
        for row in trace:
            handle.write(json.dumps(row, allow_nan=False) + '\n')
    result = {"status": "EXPLORATORY_POINT_TRACE", "input_sha256": digest, "frame_count": n,
              "raw_keys": list(data), "timestamp_present": False,
              "timing_boundary": "array-index diagnostic; official annotation/index convention unresolved",
              "interval_indices": interval, "depth_limits_m": [0.1, 2.0], "residual_margin_m": 0.05,
              "patch": "3x3 median with at least 5 valid pixels", "seed": None, "device": "cpu",
              "python": platform.python_version(), "numpy": np.__version__, "torch": torch.__version__,
              "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "rigid_projection_max_abs_difference": worst_projection_error, "cases": summaries}
    (args.output / 'result.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
