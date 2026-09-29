"""Bounded Q14 exploratory regression. Execute only in the study Docker image."""
import argparse
import hashlib
import json
import math
import os
import platform
from pathlib import Path
import time

import numpy as np
import torch
from torch import nn


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def rotation(theta):
    c, s = np.cos(theta), np.sin(theta)
    return np.stack((c, -s, s, c), axis=-1).reshape((*np.shape(theta), 2, 2))


def apply(r, v):
    return np.einsum("...ij,...j->...i", r, v)


def layouts(rng, n, cfg):
    angle = rng.uniform(-np.pi, np.pi, n)
    radius = rng.uniform(cfg["ee_radius_min"], cfg["ee_radius_max"], n)
    ee = radius[:, None] * np.stack((np.cos(angle), np.sin(angle)), axis=-1)
    action = rng.uniform(-cfg["action_bound"], cfg["action_bound"], (n, 2))
    offset = rng.uniform(-cfg["offset_bound"], cfg["offset_bound"], (n, 2))
    return ee, action, offset


def observations(ee, base, offset, theta, noise):
    inv = rotation(-theta)
    points = np.stack((offset, apply(inv, ee) + offset,
                       apply(inv, ee + base) + offset), axis=1)
    x = np.concatenate(((points + noise).reshape(-1, 6), ee), axis=-1)
    return x, apply(inv, base), points


def generate(cfg):
    rng = np.random.default_rng(cfg["train_seed"])
    n = cfg["train_count"]
    ee, base, offset = layouts(rng, n, cfg)
    theta = np.deg2rad(rng.uniform(cfg["train_angle_min_deg"], cfg["train_angle_max_deg"], n))
    noise = rng.normal(0, cfg["noise_sigma"], (n, 3, 2))
    x, action, points = observations(ee, base, offset, theta, noise)
    data = dict(train_x=x, train_action=action, train_base=base, train_theta=theta,
                train_ee=ee, train_offset=offset, train_noise=noise, train_points=points)
    ee, base, offset = layouts(np.random.default_rng(cfg["layout_seed"]), cfg["layout_count"], cfg)
    rng = np.random.default_rng(cfg["noise_seed"])
    rows = {k: [] for k in ("x", "action", "base", "theta", "ee", "offset", "noise",
                            "points", "scene", "layout", "replica")}
    scene = 0
    for k in range(cfg["layout_count"]):
        for angle in cfg["eval_angles_deg"]:
            count = cfg["replicas"] + 1
            e = np.repeat(ee[k:k+1], count, axis=0)
            b = np.repeat(base[k:k+1], count, axis=0)
            t = np.repeat(offset[k:k+1], count, axis=0)
            th = np.full(count, np.deg2rad(angle))
            noise = np.concatenate((np.zeros((1, 3, 2)),
                                    rng.normal(0, cfg["noise_sigma"], (count-1, 3, 2))))
            x, a, p = observations(e, b, t, th, noise)
            values = dict(x=x, action=a, base=b, theta=th, ee=e, offset=t, noise=noise,
                          points=p, scene=np.full(count, scene), layout=np.full(count, k),
                          replica=np.arange(-1, count-1))
            for key, val in values.items():
                rows[key].append(val)
            scene += 1
    data.update({"eval_" + key: np.concatenate(val) for key, val in rows.items()})
    return data


def network(cfg, mode):
    width = cfg["hidden_width"]
    return nn.Sequential(nn.Linear(8, width), nn.Tanh(), nn.Linear(width, width),
                         nn.Tanh(), nn.Linear(width, 4 if mode == "joint" else 2))


def fit(cfg, data, mode, seed, output):
    torch.manual_seed(seed)
    model = network(cfg, mode)
    x = torch.tensor(data["train_x"], dtype=torch.float32)
    if mode == "joint":
        theta = data["train_theta"]
        target = np.concatenate((data["train_action"],
                                 np.stack((np.cos(theta), np.sin(theta)), axis=-1)), axis=-1)
    else:
        target = data["train_base"]
    y = torch.tensor(target, dtype=torch.float32)
    def loss(pred, ref):
        if mode == "joint":
            return ((pred[:, :2]-ref[:, :2])**2).mean() + ((pred[:, 2:]-ref[:, 2:])**2).mean()
        return ((pred-ref)**2).mean()
    optimizer = torch.optim.Adam(model.parameters(), lr=cfg["learning_rate"])
    batches = np.random.default_rng(10000 + seed)
    history = []
    started = time.monotonic()
    with torch.no_grad():
        initial = float(loss(model(x), y))
    for step in range(cfg["updates"]):
        idx = batches.integers(0, len(x), cfg["batch_size"])
        optimizer.zero_grad(set_to_none=True)
        current = loss(model(x[idx]), y[idx])
        if not torch.isfinite(current):
            raise RuntimeError("Nonfinite training loss")
        current.backward()
        optimizer.step()
        if step % 100 == 0 or step == cfg["updates"] - 1:
            history.append({"update": step + 1, "batch_loss": float(current.detach())})
    model.eval()
    with torch.no_grad():
        final = float(loss(model(x), y))
        raw = model(torch.tensor(data["eval_x"], dtype=torch.float32)).numpy().astype(np.float64)
    name = f"{mode}_{seed}"
    torch.save(model.state_dict(), output / f"{name}.pt")
    record = dict(model=name, mode=mode, seed=seed, updates=cfg["updates"],
                  batch_size=cfg["batch_size"], parameter_count=sum(p.numel() for p in model.parameters()),
                  initial_training_loss=initial, final_training_loss=final,
                  seconds=time.monotonic()-started, history=history)
    print(json.dumps({k: v for k, v in record.items() if k != "history"}), flush=True)
    return raw, record


def decomposition(theta_hat, action_hat, theta, action):
    rh = rotation(theta_hat)
    base = apply(rotation(theta), action)
    g = apply(rh, action) - base
    a = apply(rh, action_hat - action)
    err = apply(rh, action_hat) - base
    gbar, abar = g.mean(axis=0), a.mean(axis=0)
    cross = float(2 * (g*a).sum(axis=-1).mean())
    return dict(mse=float((err*err).sum(axis=-1).mean()),
                g2=float((g*g).sum(axis=-1).mean()), a2=float((a*a).sum(axis=-1).mean()),
                cross=cross, bias_cross=float(2 * (gbar*abar).sum()),
                centered_cross=float(2 * ((g-gbar)*(a-abar)).sum(axis=-1).mean()))


def summarize(cfg, data, pred):
    rows = []
    for model in ("geometry", "joint_0", "joint_1"):
        for scene in range(cfg["layout_count"] * len(cfg["eval_angles_deg"])):
            for condition in ("noisy", "noiseless"):
                mask = (data["eval_scene"] == scene) & ((data["eval_replica"] >= 0) if condition == "noisy" else (data["eval_replica"] == -1))
                th = pred[model + "_theta"][mask]
                ah = pred[model + "_action"][mask]
                theta = float(data["eval_theta"][mask][0])
                action = data["eval_action"][mask][0]
                n = len(th)
                paired = decomposition(th, ah, theta, action)
                product = decomposition(np.repeat(th, n), np.tile(ah, (n, 1)), theta, action)
                oracle = apply(rotation(theta), ah) - data["eval_base"][mask]
                delta = np.arctan2(np.sin(th-theta), np.cos(th-theta))
                rows.append(dict(model=model, scene=scene, layout=int(data["eval_layout"][mask][0]),
                                 angle_deg=float(np.rad2deg(theta)), condition=condition, observations=n,
                                 paired=paired, product=product,
                                 product_minus_paired=product["mse"]-paired["mse"],
                                 oracle_mse=float((oracle*oracle).sum(axis=-1).mean()),
                                 angular_mse=float((delta*delta).mean())))
    direct = []
    for model in ("direct_0", "direct_1", "zero"):
        for scene in range(cfg["layout_count"] * len(cfg["eval_angles_deg"])):
            for condition in ("noisy", "noiseless"):
                mask = (data["eval_scene"] == scene) & ((data["eval_replica"] >= 0) if condition == "noisy" else (data["eval_replica"] == -1))
                output = pred[model + "_base"][mask] if model != "zero" else np.zeros_like(data["eval_base"][mask])
                err = output-data["eval_base"][mask]
                direct.append(dict(model=model, scene=scene, angle_deg=float(np.rad2deg(data["eval_theta"][mask][0])),
                                   condition=condition, mse=float((err*err).sum(axis=-1).mean())))
    return dict(composition=rows, direct=direct)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text())
    output = args.output
    output.mkdir(parents=True, exist_ok=False)
    torch.set_num_threads(cfg["threads"])
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    started = time.monotonic()
    dump(output / "config.json", cfg)
    dump(output / "environment.json", dict(python=platform.python_version(), numpy=np.__version__,
         torch=torch.__version__, device="cpu", threads=torch.get_num_threads(),
         parent_commit=os.environ.get("Q14_PARENT_COMMIT"), image=os.environ.get("Q14_IMAGE")))
    (output / "dependencies.lock").write_text(Path("/opt/dependencies.lock").read_text())
    data = generate(cfg)
    np.savez_compressed(output / "inputs.npz", **data)
    x = data["eval_x"]
    direction = x[:, 2:4]-x[:, 0:2]
    if np.any(np.linalg.norm(direction, axis=1) <= cfg["rotation_min_norm"]):
        raise RuntimeError("Degenerate geometric direction; preserve case and stop")
    pred = {"geometry_theta": np.arctan2(x[:, 7], x[:, 6])-np.arctan2(direction[:, 1], direction[:, 0]),
            "geometry_action": x[:, 4:6]-x[:, 2:4]}
    records = []
    for seed in cfg["fit_seeds"]:
        for mode in ("joint", "direct"):
            raw, record = fit(cfg, data, mode, seed, output)
            name = record["model"]
            records.append(record)
            pred[name + "_raw"] = raw
            if mode == "joint":
                norms = np.linalg.norm(raw[:, 2:], axis=1)
                record["rotation_min_norm"] = float(norms.min())
                if np.any(norms <= cfg["rotation_min_norm"]):
                    raise RuntimeError("Undefined learned rotation; preserve case and stop")
                pred[name + "_theta"] = np.arctan2(raw[:, 3], raw[:, 2])
                pred[name + "_action"] = raw[:, :2]
            else:
                pred[name + "_base"] = raw
    np.savez_compressed(output / "predictions.npz", **pred)
    dump(output / "fits.json", records)
    dump(output / "metrics.json", summarize(cfg, data, pred))
    dump(output / "completion.json", dict(status="completed; needs verification", fits=len(records),
         eval_observations=len(x), scene_count=cfg["layout_count"] * len(cfg["eval_angles_deg"]),
         elapsed_seconds=time.monotonic()-started, invalid_cases=0))
    manifest = {p.name: dict(bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                for p in sorted(output.iterdir()) if p.is_file()}
    dump(output / "manifest.json", manifest)
    print(json.dumps({"status": "completed; needs verification", "seconds": time.monotonic()-started}))


if __name__ == "__main__":
    main()
