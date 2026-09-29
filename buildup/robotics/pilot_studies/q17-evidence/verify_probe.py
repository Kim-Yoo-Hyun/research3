"""Independently check the paired offline policy outputs inside Q17 Docker."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            value.update(chunk)
    return value.hexdigest()


input_path = Path("/input/probe_inputs.json")
policy_path = Path("/policy/probe.json")
inputs = json.loads(input_path.read_text())
record = json.loads(policy_path.read_text())
assert record["input_sha256"] == sha256(input_path)
assert record["episodes"].keys() == inputs.keys() == {"0", "2"}
assert record["model_sha256"] == "537f9a70e2ee88f04c0b98deb67e0975bb00897b48d4ac218ea5ae09fc8ca67c"

manifest = {"input_sha256": sha256(input_path), "policy_json_sha256": sha256(policy_path), "episodes": {}}
for episode_id, selection in inputs.items():
    episode = record["episodes"][episode_id]
    current = int(selection["current_row"])
    indices = selection["frame_indices"]
    assert episode["current_row"] == current == indices[-1]
    assert all(b - a == 16 for a, b in zip(indices, indices[1:]))
    table = pq.read_table(Path("/dataset/data/chunk-000") / f"episode_{int(episode_id):06d}.parquet")
    assert table["subtask_index"][current].as_py() == 4
    assert table["stage"][current].as_py() == 2
    current_image = table["observation.images.camera_head"][current].as_py()["bytes"]
    current_state = np.asarray(table["observation.state"][current].as_py(), dtype=np.float32)
    assert episode["current_image_sha256"] == hashlib.sha256(current_image).hexdigest()
    assert episode["current_state_sha256"] == hashlib.sha256(current_state.tobytes()).hexdigest()
    assert selection["frames"][-1]["sha256"] == episode["current_image_sha256"]
    expert = np.asarray([table["action"][row].as_py() for row in range(current, current + 16)], dtype=np.float32)
    assert expert.shape == (16, 18)
    outputs = {}
    file_hashes = {}
    for condition, metrics in episode["conditions"].items():
        path = Path("/policy") / f"episode_{int(episode_id):06d}_{condition}.npy"
        actions = np.load(path, allow_pickle=False)
        assert actions.shape == (16, 18) and np.isfinite(actions).all()
        assert metrics["frame_indices"][-1] == current
        assert np.isclose(np.mean(np.abs(actions[0] - expert[0])), metrics["first_step_l1_to_demo"], rtol=1e-5, atol=1e-7)
        assert np.isclose(np.mean(np.abs(actions - expert)), metrics["chunk_l1_to_demo"], rtol=1e-5, atol=1e-7)
        outputs[condition] = actions
        file_hashes[condition] = sha256(path)
    assert len(outputs) == 4
    assert np.array_equal(outputs["generic_full_history"], outputs["explicit_subtask_full_history"])
    assert episode["conditions"]["generic_current_only"]["frame_indices"] == [current]
    assert episode["conditions"]["generic_full_history"]["frame_indices"] == indices
    assert episode["conditions"]["explicit_task_full_history"]["frame_indices"] == indices
    assert episode["conditions"]["explicit_subtask_full_history"]["frame_indices"] == indices
    manifest["episodes"][episode_id] = {
        "current_row": current,
        "history_length": len(indices),
        "current_image_sha256": episode["current_image_sha256"],
        "output_sha256": file_hashes,
        "chunk_l1_to_expert": {key: float(np.mean(np.abs(value - expert))) for key, value in outputs.items()},
    }

Path("/verification/verification.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps({"verified_episodes": len(manifest["episodes"]), "verified_action_chunks": sum(len(item["output_sha256"]) for item in manifest["episodes"].values())}))
