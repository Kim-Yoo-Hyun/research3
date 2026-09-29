"""Inspect fixed offline policy-probe inputs inside the Q17 audit container."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pyarrow.parquet as pq

data = Path("/dataset")
output = Path("/output")
output.mkdir(parents=True, exist_ok=True)
metadata = json.loads((data / "meta/astribot_subtask_metadata.json").read_text())["episodes"]

result = {}
for episode_id in (0, 2):
    path = data / "data/chunk-000" / f"episode_{episode_id:06d}.parquet"
    table = pq.read_table(path)
    subtask = table["subtask_index"].to_pylist()
    stage = table["stage"].to_pylist()
    choices = [i for i, (s, g) in enumerate(zip(subtask, stage)) if s == 4 and g == 2]
    assert choices
    current = choices[0]
    history_count = min(12, current // 16)
    history = list(range(current - history_count * 16, current, 16))
    frame_indices = history + [current]
    assert len(frame_indices) <= 13 and all(b - a == 16 for a, b in zip(frame_indices, frame_indices[1:]))
    frames = []
    for row in frame_indices:
        payload = table["observation.images.camera_head"][row].as_py()["bytes"]
        assert payload[:8] == b"\x89PNG\r\n\x1a\n"
        image_path = output / f"episode_{episode_id:06d}_row_{row:04d}.png"
        image_path.write_bytes(payload)
        frames.append({
            "row": row,
            "subtask": subtask[row],
            "stage": stage[row],
            "image": str(image_path),
            "sha256": hashlib.sha256(payload).hexdigest(),
        })
    item = metadata[episode_id]
    result[str(episode_id)] = {
        "current_row": current,
        "frame_indices": frame_indices,
        "frames": frames,
        "task_instruction": item["task_instruction"],
        "subtask_instruction_at_current": item["subtask_instruction_map"][str(table["subtask_instruction_index"][current].as_py())],
        "state_dim": len(table["observation.state"][current].as_py()),
        "action_dim": len(table["action"][current].as_py()),
        "current_state": table["observation.state"][current].as_py(),
        "expert_action": table["action"][current].as_py(),
    }

(output / "probe_inputs.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({key: {"current": value["current_row"], "frames": value["frame_indices"], "state_dim": value["state_dim"], "action_dim": value["action_dim"]} for key, value in result.items()}))
