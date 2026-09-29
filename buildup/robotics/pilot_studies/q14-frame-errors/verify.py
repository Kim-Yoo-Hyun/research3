"""Independent complex-coordinate verification; no study implementation imported."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as F


def load(path):
    return json.loads(path.read_text())


def complex2(x):
    return x[..., 0] + 1j*x[..., 1]


class Checks:
    def __init__(self):
        self.count = 0
        self.max_error = 0.0

    def close(self, a, b, atol=1e-11):
        self.count += 1
        if np.size(a):
            self.max_error = max(self.max_error, float(np.max(np.abs(np.asarray(a)-b))))
        np.testing.assert_allclose(a, b, rtol=1e-10, atol=atol)


def independent_terms(h, action, true_h, true_action):
    g = (h-true_h)*true_action
    a = h*(action-true_action)
    err = h*action-true_h*true_action
    # Broadcast fixed/row components to the full product before centering.
    g, a, err = np.broadcast_arrays(g, a, err)
    bias = 2*(g.mean().conjugate()*a.mean()).real
    centered = 2*((g-g.mean()).conjugate()*(a-a.mean())).real.mean()
    return dict(mse=float((abs(err)**2).mean()), g2=float((abs(g)**2).mean()),
                a2=float((abs(a)**2).mean()), cross=float((2*g.conjugate()*a).real.mean()),
                bias_cross=float(bias), centered_cross=float(centered))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--result", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    cfg = load(args.result / "config.json")
    manifest = load(args.result / "manifest.json")
    for name, info in manifest.items():
        payload = (args.result / name).read_bytes()
        assert len(payload) == info["bytes"]
        assert hashlib.sha256(payload).hexdigest() == info["sha256"]
    d = np.load(args.result / "inputs.npz")
    pred = np.load(args.result / "predictions.npz")
    fits = load(args.result / "fits.json")
    metrics = load(args.result / "metrics.json")
    checks = Checks()
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    expected_n = cfg["layout_count"] * len(cfg["eval_angles_deg"]) * (cfg["replicas"]+1)
    assert d["eval_x"].shape == (expected_n, 8)
    assert d["train_x"].shape == (cfg["train_count"], 8)
    for split in ("train", "eval"):
        base, ee = complex2(d[split+"_base"]), complex2(d[split+"_ee"])
        t, h = complex2(d[split+"_offset"]), np.exp(-1j*d[split+"_theta"])
        truth = np.stack((t, ee*h+t, (ee+base)*h+t), axis=1)
        checks.close(complex2(d[split+"_points"]), truth)
        noisy = truth + complex2(d[split+"_noise"])
        checks.close(complex2(d[split+"_x"][:, :6].reshape(-1, 3, 2)), noisy)
        checks.close(d[split+"_x"][:, 6:], d[split+"_ee"])
        checks.close(complex2(d[split+"_action"]), base*h)
        radius = abs(ee)
        assert np.all((radius >= cfg["ee_radius_min"]-1e-12) & (radius <= cfg["ee_radius_max"]+1e-12))
    train_theta = np.rad2deg(d["train_theta"])
    assert train_theta.min() >= cfg["train_angle_min_deg"] and train_theta.max() <= cfg["train_angle_max_deg"]
    train_rows = {row.tobytes() for row in d["train_x"]}
    assert not any(row.tobytes() in train_rows for row in d["eval_x"])
    for layout in range(cfg["layout_count"]):
        mask = d["eval_layout"] == layout
        for key in ("ee", "base", "offset"):
            checks.close(d["eval_"+key][mask], np.broadcast_to(d["eval_"+key][mask][0], d["eval_"+key][mask].shape))
    assert len(fits) == 4 and {f["model"] for f in fits} == {"joint_0", "joint_1", "direct_0", "direct_1"}
    prediction_error = 0.0
    for fit in fits:
        assert fit["updates"] == cfg["updates"] and fit["batch_size"] == cfg["batch_size"]
        state = torch.load(args.result / (fit["model"]+".pt"), map_location="cpu", weights_only=True)
        assert sum(t.numel() for t in state.values()) == fit["parameter_count"]
        with torch.no_grad():
            x = torch.tensor(d["eval_x"], dtype=torch.float32)
            for layer in ("0", "2", "4"):
                x = F.linear(x, state[layer+".weight"], state[layer+".bias"])
                if layer != "4":
                    x = x.tanh()
        raw = x.numpy().astype(np.float64)
        saved = pred[fit["model"]+"_raw"]
        prediction_error = max(prediction_error, float(np.max(abs(raw-saved))))
        checks.close(raw, saved, atol=1e-7)
        if fit["mode"] == "joint":
            assert np.all(np.linalg.norm(raw[:, 2:], axis=1) > cfg["rotation_min_norm"])
            checks.close(np.exp(1j*pred[fit["model"]+"_theta"]), complex2(raw[:, 2:])/np.linalg.norm(raw[:, 2:], axis=1))
            checks.close(raw[:, :2], pred[fit["model"]+"_action"])
        else:
            checks.close(raw, pred[fit["model"]+"_base"])
    x = d["eval_x"]
    v = complex2(x[:, 2:4]-x[:, :2])
    ee = complex2(x[:, 6:])
    geom_h = (ee/abs(ee)) * (v/abs(v)).conjugate()
    checks.close(np.exp(1j*pred["geometry_theta"]), geom_h)
    checks.close(complex2(pred["geometry_action"]), complex2(x[:, 4:6]-x[:, 2:4]))
    for array in pred.values():
        assert np.isfinite(array).all()

    for row in metrics["composition"]:
        noisy = d["eval_replica"] >= 0 if row["condition"] == "noisy" else d["eval_replica"] == -1
        mask = (d["eval_scene"] == row["scene"]) & noisy
        n = cfg["replicas"] if row["condition"] == "noisy" else 1
        assert int(mask.sum()) == row["observations"] == n
        for key in ("theta", "action", "base", "ee", "offset"):
            values = d["eval_"+key][mask]
            checks.close(values, np.broadcast_to(values[0], values.shape))
        h = np.exp(1j*pred[row["model"]+"_theta"][mask])
        ah = complex2(pred[row["model"]+"_action"][mask])
        gt_h = np.exp(1j*d["eval_theta"][mask][0])
        gt_a = complex2(d["eval_action"][mask][0])
        terms = dict(paired=independent_terms(h, ah, gt_h, gt_a),
                     product=independent_terms(h[:, None], ah[None, :], gt_h, gt_a))
        for kind, values in terms.items():
            for key, value in values.items():
                checks.close(value, row[kind][key])
            checks.close(values["mse"], values["g2"]+values["a2"]+values["cross"])
            checks.close(values["cross"], values["bias_cross"]+values["centered_cross"])
        paired, product = terms["paired"], terms["product"]
        checks.close(product["g2"], paired["g2"])
        checks.close(product["a2"], paired["a2"])
        checks.close(product["mse"]-paired["mse"], product["cross"]-paired["cross"])
        checks.close(row["product_minus_paired"], product["mse"]-paired["mse"])
        checks.close(row["oracle_mse"], (abs(gt_h*ah-gt_h*gt_a)**2).mean())
        checks.close(row["oracle_mse"], paired["a2"])
        checks.close(paired["mse"]-row["oracle_mse"], paired["g2"]+paired["cross"])
        checks.close(row["angular_mse"], (np.angle(h/gt_h)**2).mean())
        if row["condition"] == "noiseless" and row["model"] == "geometry":
            assert row["paired"]["mse"] < 1e-26
    for row in metrics["direct"]:
        noisy = d["eval_replica"] >= 0 if row["condition"] == "noisy" else d["eval_replica"] == -1
        mask = (d["eval_scene"] == row["scene"]) & noisy
        estimate = complex2(pred[row["model"]+"_base"][mask]) if row["model"] != "zero" else 0
        checks.close(row["mse"], (abs(estimate-complex2(d["eval_base"][mask]))**2).mean())
    assert len(metrics["composition"]) == 96 and len(metrics["direct"]) == 96

    # Deliberately correlated output errors: known analytic fixture, never a learned result.
    r = np.exp(1j*np.array([0.0, 0.7, -1.2]))
    q = np.exp(1j*np.array([0.2, -0.3, 0.8]))
    a = np.array([0.3+0.2j, -0.4+0.1j, 0.1-0.2j])
    control = independent_terms(r*q, a/q, r, a)
    checks.close(control["mse"], 0.0)
    checks.close(control["g2"]+control["a2"]+control["cross"], 0.0)

    summary = []
    for model in ("geometry", "joint_0", "joint_1"):
        for angle in cfg["eval_angles_deg"]:
            rows = [r for r in metrics["composition"] if r["model"] == model and r["angle_deg"] == angle and r["condition"] == "noisy"]
            summary.append(dict(model=model, angle_deg=angle, scenes=len(rows),
                paired_mse=float(np.mean([r["paired"]["mse"] for r in rows])),
                product_mse=float(np.mean([r["product"]["mse"] for r in rows])),
                oracle_mse=float(np.mean([r["oracle_mse"] for r in rows])),
                product_minus_paired=float(np.mean([r["product_minus_paired"] for r in rows])),
                delta_min=min(r["product_minus_paired"] for r in rows),
                delta_max=max(r["product_minus_paired"] for r in rows),
                paired_better_scenes=sum(r["product_minus_paired"] > 1e-12 for r in rows),
                angular_mse=float(np.mean([r["angular_mse"] for r in rows])),
                g2=float(np.mean([r["paired"]["g2"] for r in rows])),
                a2=float(np.mean([r["paired"]["a2"] for r in rows])),
                cross=float(np.mean([r["paired"]["cross"] for r in rows]))))
    direct_summary = []
    for model in ("direct_0", "direct_1", "zero"):
        for angle in cfg["eval_angles_deg"]:
            rows = [r for r in metrics["direct"] if r["model"] == model and r["angle_deg"] == angle and r["condition"] == "noisy"]
            direct_summary.append(dict(model=model, angle_deg=angle, scenes=len(rows), mse=float(np.mean([r["mse"] for r in rows]))))
    outcome = dict(status="verified", scope="exploratory SO(2) keypoint regression; no VLA/robot claim",
                   fits=4, scenes=16, noisy_observations=1024, noiseless_observations=16,
                   prediction_rows=expected_n*5, composition_metric_rows=len(metrics["composition"]),
                   direct_metric_rows=len(metrics["direct"]), checks=checks.count,
                   max_numeric_difference=checks.max_error, checkpoint_prediction_max_difference=prediction_error,
                   analytic_cancellation_control=control, composition_summary=summary, direct_summary=direct_summary,
                   input_manifest_sha256=hashlib.sha256((args.result/"manifest.json").read_bytes()).hexdigest())
    args.output.write_text(json.dumps(outcome, indent=2, allow_nan=False)+"\n")
    print(json.dumps(outcome, indent=2))


if __name__ == "__main__":
    main()
