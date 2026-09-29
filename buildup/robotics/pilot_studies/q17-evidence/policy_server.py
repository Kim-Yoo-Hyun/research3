"""Minimal websocket bridge for the released Q17 checkpoint, inside Docker only.

The official server imports PyTorch3D through its data-transform registry.
This bridge keeps the official websocket protocol and released model, but uses
the checkpoint's single 18D min/max statistics directly. It is an exploratory
compatibility route, not a byte-for-byte official server reproduction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
import torch

from starVLA.model.framework.VLM4A.QwenOFTState import Qwenvl_OFT_State  # noqa: F401
import starVLA.model.framework.base_framework as framework_module
from starVLA.model.framework.base_framework import baseframework
from starVLA.model.framework.share_tools import read_mode_config
from deployment.model_server.tools.websocket_policy_server import WebsocketPolicyServer


CHECKPOINT = "/models/policy/checkpoints/steps_100000_pytorch_model.pt"


def minmax_forward(state: np.ndarray, stats: dict) -> np.ndarray:
    low = np.asarray(stats["min"], dtype=np.float32)
    high = np.asarray(stats["max"], dtype=np.float32)
    result = np.zeros_like(state, dtype=np.float32)
    mask = high != low
    result[..., mask] = 2 * (state[..., mask] - low[mask]) / (high[mask] - low[mask]) - 1
    return result


def minmax_inverse(action: np.ndarray, stats: dict) -> np.ndarray:
    low = np.asarray(stats["min"], dtype=np.float32)
    high = np.asarray(stats["max"], dtype=np.float32)
    return (action + 1) / 2 * (high - low) + low


class ReleasedOFTBridge:
    def __init__(self):
        if not torch.cuda.is_available():
            raise RuntimeError("the released checkpoint requires a GPU")
        torch.manual_seed(1729)
        np.random.seed(1729)
        framework_module._FRAMEWORKS_IMPORTED = True
        cfg, all_stats = read_mode_config(CHECKPOINT)
        if len(all_stats) != 1:
            raise RuntimeError("expected one normalization key")
        self.key, self.stats = next(iter(all_stats.items()))
        if len(self.stats["state"]["min"]) != 18 or len(self.stats["action"]["min"]) != 18:
            raise RuntimeError("expected 18D Astribot state and action")
        self.model = baseframework.from_pretrained(CHECKPOINT).to("cuda").eval()
        self.metadata = {
            "action_chunk_size": int(cfg["framework"]["action_model"]["action_horizon"]),
            "available_unnorm_keys": [self.key],
            "default_unnorm_key": self.key,
            "state_keys": ["state.astribot"],
            "action_keys": ["action.astribot"],
            "bridge": "direct_minmax_exploratory",
        }
        self.request_count = 0
        print(json.dumps({"event": "ready", "metadata": self.metadata}), flush=True)

    def predict_action(self, examples: list[dict], unnorm_key: str | None = None, **kwargs) -> dict:
        if unnorm_key not in (None, self.key):
            raise ValueError(f"unexpected normalization key: {unnorm_key}")
        prepared = []
        for item in examples:
            images = [Image.fromarray(np.asarray(image, dtype=np.uint8), "RGB") for image in item["image"]]
            raw_state = np.asarray(item.get("state_history", item.get("state")), dtype=np.float32)
            if raw_state.shape != (len(images), 18):
                raise ValueError(f"image/state history shape mismatch: {len(images)}, {raw_state.shape}")
            state = minmax_forward(raw_state, self.stats["state"])
            prepared.append({**item, "image": images, "state_history": state, "state": state})
        result = self.model.predict_action(prepared, **kwargs)
        normalized = np.asarray(result["normalized_actions"], dtype=np.float32)
        actions = np.stack([minmax_inverse(row, self.stats["action"]) for row in normalized])
        if actions.ndim != 3 or actions.shape[2] != 18 or not np.isfinite(actions).all():
            raise RuntimeError(f"invalid model action shape or values: {actions.shape}")
        self.request_count += 1
        print(json.dumps({
            "event": "inference",
            "request_count": self.request_count,
            "instruction": [str(x.get("lang")) for x in examples],
            "num_frames": [len(x["image"]) for x in examples],
            "actions_sha256": hashlib.sha256(actions.tobytes()).hexdigest(),
        }), flush=True)
        output = {"actions": actions}
        if "vlm_text" in result:
            output["vlm_text"] = result["vlm_text"]
        return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=7980)
    args = parser.parse_args()
    bridge = ReleasedOFTBridge()
    WebsocketPolicyServer(
        policy=bridge,
        host="0.0.0.0",
        port=args.port,
        idle_timeout=-1,
        metadata=bridge.metadata,
    ).serve_forever()


if __name__ == "__main__":
    main()
