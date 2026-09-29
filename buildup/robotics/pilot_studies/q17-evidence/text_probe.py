"""Check released checkpoint text readout for fixed hidden-color examples in Docker."""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
import torch

import starVLA.model.framework.base_framework as framework_module
from starVLA.model.framework.VLM4A.QwenOFTState import Qwenvl_OFT_State  # noqa: F401
from starVLA.model.framework.base_framework import baseframework
from starVLA.model.framework.share_tools import read_mode_config

from policy_probe import CHECKPOINT, GENERIC_TASK, example, unnormalize_actions


def color_words(text: str) -> list[str]:
    return [name for name in ("blue", "green", "orange", "purple", "red", "yellow") if re.search(r"\b" + name + r"\b", text.lower())]


torch.manual_seed(1729)
framework_module._FRAMEWORKS_IMPORTED = True
_, stats_map = read_mode_config(CHECKPOINT)
stats = next(iter(stats_map.values()))
model = baseframework.from_pretrained(CHECKPOINT).to("cuda").eval()
selections = json.loads(Path("/input/probe_inputs.json").read_text())
result = {"purpose": "exploratory VLM text readout on two training demonstrations; no held-out or success claim", "episodes": {}}

for episode_id, choice in selections.items():
    table = pq.read_table(Path("/dataset/data/chunk-000") / f"episode_{int(episode_id):06d}.parquet")
    current = int(choice["current_row"])
    selected = choice["frame_indices"]
    target = re.search(r"with a (\w+) pad on its back side", choice["task_instruction"], flags=re.IGNORECASE).group(1).lower()
    entry = {"current_row": current, "target_color": target, "conditions": {}}
    for condition, indices in (("generic_full_history", selected), ("generic_current_only", [current])):
        prediction = model.predict_action([example(table, indices, GENERIC_TASK, None, stats["state"])], return_vlm_text=True, vlm_text_max_new_tokens=64)
        action = unnormalize_actions(np.asarray(prediction["normalized_actions"], dtype=np.float32)[0], stats["action"])
        previous = np.load(Path("/previous") / f"episode_{int(episode_id):06d}_{condition}.npy", allow_pickle=False)
        maximum_action_difference = float(np.max(np.abs(action - previous)))
        match = bool(np.allclose(action, previous, rtol=1e-5, atol=1e-6))
        assert match, (episode_id, condition, maximum_action_difference)
        text = prediction["vlm_text"][0]
        entry["conditions"][condition] = {"text": text, "color_words": color_words(text), "action_matches_prior_run": match, "max_action_difference": maximum_action_difference}
        print(json.dumps({"episode": episode_id, "condition": condition, "text": text, "color_words": color_words(text)}), flush=True)
    result["episodes"][episode_id] = entry
    Path("/output/text.json").write_text(json.dumps(result, indent=2) + "\n")
