"""Bounded raw-input inspection. Execute only inside the study Docker image."""
import argparse
import hashlib
import io
import json
import pickle
import pickletools
import platform
from pathlib import Path

import numpy as np
import torch


class CpuUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == "torch.storage" and name == "_load_from_bytes":
            return lambda data: torch.load(io.BytesIO(data), map_location="cpu", weights_only=True)
        return super().find_class(module, name)


def describe(value):
    if isinstance(value, torch.Tensor):
        return {"type": "tensor", "shape": list(value.shape), "dtype": str(value.dtype),
                "device": str(value.device)}
    if isinstance(value, np.ndarray):
        return {"type": "ndarray", "shape": list(value.shape), "dtype": str(value.dtype)}
    if isinstance(value, (list, tuple)):
        return {"type": type(value).__name__, "length": len(value),
                "first": describe(value[0]) if value else None}
    if isinstance(value, dict):
        return {str(k): describe(v) for k, v in value.items()}
    if value is None or isinstance(value, (str, int, float, bool)):
        return {"type": type(value).__name__, "value": value}
    return {"type": type(value).__module__ + "." + type(value).__name__}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.input.read_bytes()
    expected = "9b4f894a63556563fe7bc856d32131948b2b5df495d1aab5b88a2dc1834b1897"
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected or len(raw) != 54700824:
        raise ValueError("Input identity differs from the selected dataset revision")
    result = {"input_sha256": digest, "input_bytes": len(raw),
              "python": platform.python_version(), "numpy": np.__version__, "torch": torch.__version__,
              "device": "cpu", "seed": None,
              "purpose": "exploratory input inspection; no method result"}
    result["explicit_globals"] = sorted({arg for op, arg, _ in pickletools.genops(raw)
                                          if op.name == "GLOBAL"})
    try:
        data = CpuUnpickler(io.BytesIO(raw)).load()
        result["schema"] = describe(data)
        result["status"] = "INPUT_DESERIALIZED"
    except Exception as exc:
        result["status"] = "INPUT_DEPENDENCY_UNRESOLVED"
        result["error"] = f"{type(exc).__name__}: {exc}"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps(result, indent=2))
    if result["status"] != "INPUT_DESERIALIZED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
