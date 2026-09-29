"""Check the bridge against the independently verified offline probe."""

import hashlib
import io
import json
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
from PIL import Image

from policy_server import ReleasedOFTBridge


def main():
    selected = json.loads(Path("/input/probe_inputs.json").read_text())
    bridge = ReleasedOFTBridge()
    checks = {}
    for episode_id in ("0", "2"):
        table = pq.read_table(Path("/dataset/data/chunk-000") / f"episode_{int(episode_id):06d}.parquet")
        indices = selected[episode_id]["frame_indices"]
        images = [
            np.asarray(Image.open(io.BytesIO(table["observation.images.camera_head"][row].as_py()["bytes"])).convert("RGB"))
            for row in indices
        ]
        states = np.asarray([table["observation.state"][row].as_py() for row in indices], dtype=np.float32)
        example = {
            "image": images,
            "lang": "Place the gray block on the pad matching its back-side color.",
            "task_lang": "Place the gray block on the pad matching its back-side color.",
            "state_history": states,
            "state": states,
            "num_frames": len(indices),
            "num_history_frames": len(indices) - 1,
            "history_frame_indices": indices,
            "history_mode": "action_keyframe",
            "robot_tag": "activearena_astribot",
        }
        actual = bridge.predict_action([example])["actions"][0]
        reference = np.load(Path("/reference") / f"episode_{int(episode_id):06d}_generic_full_history.npy")
        max_abs = float(np.max(np.abs(actual - reference)))
        checks[episode_id] = {
            "max_abs_action_difference": max_abs,
            "actual_sha256": hashlib.sha256(actual.tobytes()).hexdigest(),
            "reference_sha256": hashlib.sha256(reference.tobytes()).hexdigest(),
            "shape": list(actual.shape),
        }
        if actual.shape != (16, 18) or max_abs > 1e-5:
            raise RuntimeError(f"bridge mismatch for episode {episode_id}: {max_abs}")
    output = Path("/output/verification.json")
    output.write_text(json.dumps(checks, indent=2) + "\n")
    print(json.dumps(checks, indent=2), flush=True)


if __name__ == "__main__":
    main()
