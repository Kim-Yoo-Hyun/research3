#!/usr/bin/env python3
"""Frozen Q10 v5 threshold library. Execute only in the project Docker image."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import h5py
import numpy as np

ACTIONS = ("pick", "insert", "remove")
SEED = 20260907
STATE = sorted([f"pose_{part}_{axis}" for part in ("terminal", "change") for axis in "xyz"] +
               ["pose_displacement", "pose_rotation"] +
               [f"gripper_{part}_{axis}" for part in ("terminal", "change") for axis in ("left", "right", "sum")])
FORCE = sorted([f"{signal}_{stat}" for signal in ("measured", "relative", "compensated")
                for stat in ("peak", "impulse", "duration_2", "duration_5", "duration_10", "duration_20")])
FEATURES = {"duration": ["duration"], "state": STATE, "force": FORCE,
            "combined": sorted(STATE + FORCE + ["duration"])}
CANDIDATES = ["family_prior", "text_prior"] + [f"{kind}_d{depth}" for kind in FEATURES for depth in (1, 2)]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data):
    with Path(path).open("x") as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write("\n")


def write_rows(path, rows):
    with Path(path).open("x") as stream:
        for row in rows:
            stream.write(json.dumps(row, allow_nan=False) + "\n")


def write_tsv(path, rows):
    with Path(path).open("x", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def signal_window(handle, signal, start, end, width):
    t = np.asarray(handle[f"timestamps/{signal}"][...]).reshape(-1)
    d = handle[f"robot_state/{signal}"]
    if len(t) != len(d) or d.ndim != 2 or d.shape[1] != width:
        raise ValueError(f"INVALID_FEATURES: shape {signal}")
    if not np.isfinite(t).all() or np.any(np.diff(t) < 0):
        raise ValueError(f"INVALID_FEATURES: timestamps {signal}")
    left, right = np.searchsorted(t, start, side="left"), np.searchsorted(t, end, side="right")
    values = np.asarray(d[left:right], dtype=float)
    if not len(values) or not np.isfinite(values).all():
        raise ValueError(f"INVALID_FEATURES: empty/nonfinite {signal}")
    return t[left:right], values


def features_for_segment(handle, start, end):
    if not np.isfinite([start, end]).all() or end <= start:
        raise ValueError("INVALID_FEATURES: segment bounds")
    _, pose = signal_window(handle, "pose", start, end, 7)
    _, grip = signal_window(handle, "gripper_positions", start, end, 2)
    t, force = signal_window(handle, "measured_force", start, end, 3)
    ct, compensated = signal_window(handle, "compensated_base_force", start, end, 3)
    result = {"duration": end - start}
    change = pose[-1, :3] - pose[0, :3]
    for i, axis in enumerate("xyz"):
        result[f"pose_terminal_{axis}"] = pose[-1, i]
        result[f"pose_change_{axis}"] = change[i]
    result["pose_displacement"] = np.linalg.norm(change)
    quats = pose[[0, -1], 3:]
    norms = np.linalg.norm(quats, axis=1)
    if np.any(norms <= 1e-12):
        raise ValueError("INVALID_FEATURES: zero quaternion")
    quats = quats / norms[:, None]
    result["pose_rotation"] = 2 * np.arccos(np.clip(abs(np.dot(*quats)), 0, 1))
    for i, finger in enumerate(("left", "right")):
        result[f"gripper_terminal_{finger}"] = grip[-1, i]
        result[f"gripper_change_{finger}"] = grip[-1, i] - grip[0, i]
    result["gripper_terminal_sum"] = grip[-1].sum()
    result["gripper_change_sum"] = (grip[-1] - grip[0]).sum()
    for name, times, vectors in (("measured", t, force), ("relative", t, force - force[0]),
                                  ("compensated", ct, compensated)):
        norm = np.linalg.norm(vectors, axis=1)
        result[f"{name}_peak"] = norm.max()
        result[f"{name}_impulse"] = np.trapezoid(norm, times)
        for cutoff in (2, 5, 10, 20):
            result[f"{name}_duration_{cutoff}"] = np.trapezoid((norm > cutoff).astype(float), times)
    if set(result) != set(FEATURES["combined"]) or not np.isfinite(list(result.values())).all():
        raise ValueError("INVALID_FEATURES: feature schema")
    return {k: float(v) for k, v in result.items()}


def extract(rows, roots):
    results = []
    for recording in sorted({r["recording_id"] for r in rows}):
        matches = [root / f"{recording}.h5" for root in roots if (root / f"{recording}.h5").exists()]
        if len(matches) != 1:
            raise ValueError(f"INVALID_FEATURES: input resolution {recording}")
        with h5py.File(matches[0], "r") as handle:
            for row in rows:
                if row["recording_id"] != recording:
                    continue
                # Outcome is evaluator metadata, never passed to the signal extractor.
                features = features_for_segment(handle, float(row["start"]), float(row["end"]))
                results.append({"id": f'{recording}:{row["segment_index"]}',
                                "recording_id": recording, "segment_index": row["segment_index"],
                                "action": row["action_family"], "text": row["text"],
                                "success": row["success"] == "True", "features": features})
        print(f"extracted {recording}", flush=True)
    return results


def fit_tree(x, y, names, depth, min_leaf=5):
    y = np.asarray(y, dtype=int)
    counts = np.bincount(y, minlength=2)
    weights = np.array([0.5 / counts[v] if counts[v] else 0 for v in y])

    def node(indices, remaining):
        local_y, w = y[indices], weights[indices]
        masses = np.bincount(local_y, weights=w, minlength=2)
        result = {"n": len(indices), "success": int(local_y.sum()),
                  "p": float((local_y.sum() + 1) / (len(indices) + 2)),
                  "pred": bool(masses[1] >= masses[0])}
        if remaining == 0 or min(masses) == 0 or len(indices) < 2 * min_leaf:
            return result
        total = masses.sum()
        parent = total - np.dot(masses, masses) / total
        best = None
        # names are sorted; strict improvement preserves feature/threshold tie order.
        for j, name in enumerate(names):
            order = np.argsort(x[indices, j], kind="stable")
            values = x[indices[order], j]
            wy = w[order] * local_y[order]
            positive = np.cumsum(wy)[:-1]
            mass = np.cumsum(w[order])[:-1]
            negative = mass - positive
            right_mass = total - mass
            valid = ((values[:-1] < values[1:]) &
                     (np.arange(1, len(indices)) >= min_leaf) &
                     (np.arange(len(indices) - 1, 0, -1) >= min_leaf))
            cost = mass - (positive**2 + negative**2) / mass
            cost += right_mass - ((masses[1] - positive)**2 + (masses[0] - negative)**2) / right_mass
            gain = np.where(valid, parent - cost, -np.inf)
            k = int(np.argmax(gain))
            if gain[k] > 1e-12 and (best is None or gain[k] > best[0] + 1e-12):
                threshold = float(values[k] + (values[k + 1] - values[k]) / 2)
                best = (float(gain[k]), j, name, threshold)
        if best is None:
            return result
        _, j, name, threshold = best
        left = x[indices, j] <= threshold
        result.update(feature=name, threshold=threshold,
                      left=node(indices[left], remaining - 1), right=node(indices[~left], remaining - 1))
        return result

    return node(np.arange(len(y)), depth)


def fit(rows, candidate):
    if not rows:
        raise ValueError("INVALID_FEATURES: no training rows for family")
    y = np.array([r["success"] for r in rows], dtype=int)
    prior = float((y.sum() + 1) / (len(y) + 2))
    if candidate.endswith("prior"):
        texts = {}
        if candidate == "text_prior":
            for text in sorted({r["text"] for r in rows}):
                outcomes = [r["success"] for r in rows if r["text"] == text]
                texts[text] = (sum(outcomes) + 1) / (len(outcomes) + 2)
        return {"candidate": candidate, "p": prior, "texts": texts}
    kind, depth = candidate.rsplit("_d", 1)
    names = sorted(FEATURES[kind])
    x = np.array([[r["features"][name] for name in names] for r in rows])
    return {"candidate": candidate, "tree": fit_tree(x, y, names, int(depth))}


def predict(model, row):
    if "tree" not in model:
        p = model["texts"].get(row["text"], model["p"])
        return bool(p >= 0.5), float(p)
    node = model["tree"]
    while "feature" in node:
        node = node["left" if row["features"][node["feature"]] <= node["threshold"] else "right"]
    return node["pred"], node["p"]


def metrics(y, pred, p):
    y, pred, p = np.asarray(y, bool), np.asarray(pred, bool), np.asarray(p, float)
    if not len(y) or y.all() or not y.any():
        raise ValueError("both classes required for balanced accuracy")
    tp, tn = int((y & pred).sum()), int((~y & ~pred).sum())
    fp, fn = int((~y & pred).sum()), int((y & ~pred).sum())
    bins = np.minimum((p * 5).astype(int), 4)
    ece = sum(np.mean(bins == i) * abs(p[bins == i].mean() - y[bins == i].mean())
              for i in range(5) if (bins == i).any())
    clipped = np.clip(p, 1e-12, 1 - 1e-12)
    return {"n": len(y), "success": int(y.sum()), "failure": int((~y).sum()),
            "tp": tp, "tn": tn, "fp": fp, "fn": fn,
            "success_recall": tp / (tp + fn), "failure_recall": tn / (tn + fp),
            "balanced_accuracy": 0.5 * (tp / (tp + fn) + tn / (tn + fp)),
            "brier": float(np.mean((p - y)**2)),
            "log_loss": float(-np.mean(y * np.log(clipped) + (~y) * np.log(1 - clipped))),
            "ece_5": float(ece)}


def measure(rows):
    return metrics([r["success"] for r in rows], [r["pred"] for r in rows], [r["p"] for r in rows])


def selection_key(candidate, score):
    if candidate.endswith("prior"):
        depth, width = 0, 0
    else:
        kind, suffix = candidate.rsplit("_d", 1)
        depth, width = int(suffix), len(FEATURES[kind])
    return (-score["balanced_accuracy"], score["brier"], depth, width, candidate)


def train(rows):
    selected, cv, fitted = {}, {}, {}
    for action in ACTIONS:
        subset = [r for r in rows if r["action"] == action]
        cv[action], fitted[action] = {}, {}
        for candidate in CANDIDATES:
            heldout = []
            for group in sorted({r["recording_id"] for r in rows}):
                model = fit([r for r in subset if r["recording_id"] != group], candidate)
                for row in subset:
                    if row["recording_id"] == group:
                        pred, p = predict(model, row)
                        heldout.append({"success": row["success"], "pred": pred, "p": p})
            cv[action][candidate] = measure(heldout)
            fitted[action][candidate] = fit(subset, candidate)
        selected[action] = min(CANDIDATES, key=lambda c: selection_key(c, cv[action][c]))
        print(f"train CV complete: {action} selected={selected[action]}", flush=True)
    return {"selected": selected, "cv": cv, "fitted": fitted}


def evaluate(rows, training):
    predictions, table, scores = [], [], {}
    for candidate in CANDIDATES + ["selected"]:
        scores[candidate] = {}
        for action in ACTIONS:
            name = training["selected"][action] if candidate == "selected" else candidate
            group = []
            for row in rows:
                if row["action"] == action:
                    pred, p = predict(training["fitted"][action][name], row)
                    record = {k: row[k] for k in ("id", "recording_id", "segment_index", "action", "text", "success")}
                    record.update(candidate=candidate, fitted_candidate=name, pred=pred, p=p)
                    group.append(record)
            predictions.extend(group)
            score = measure(group)
            table.append({"candidate": candidate, "action": action, **score})
            scores[candidate][action] = score
        scores[candidate]["macro"] = {key: float(np.mean([scores[candidate][a][key] for a in ACTIONS]))
                                        for key in ("balanced_accuracy", "brier", "log_loss", "ece_5")}
    return predictions, table, scores


def bootstrap(predictions):
    indexed = {c: {r["id"]: r for r in predictions if r["candidate"] == c}
               for c in ("selected", "family_prior")}
    selected = list(indexed["selected"].values())
    groups = sorted({r["recording_id"] for r in selected})
    rng = np.random.default_rng(SEED)
    draws, invalid = [], 0
    for _ in range(2000):
        sampled = rng.choice(groups, size=len(groups), replace=True)
        ids = [r["id"] for group in sampled for r in selected if r["recording_id"] == group]
        values = {}
        try:
            for candidate in indexed:
                values[candidate] = float(np.mean([
                    measure([indexed[candidate][key] for key in ids if indexed[candidate][key]["action"] == action])["balanced_accuracy"]
                    for action in ACTIONS]))
        except ValueError:
            invalid += 1
            continue
        draws.append({"macro_ba": values["selected"], "gain": values["selected"] - values["family_prior"]})
    intervals = {key: np.quantile([r[key] for r in draws], [0.025, 0.975]).tolist()
                 for key in ("macro_ba", "gain")} if draws else {"macro_ba": None, "gain": None}
    return {"seed": SEED, "requested": 2000, "valid": len(draws), "invalid": invalid,
            "intervals": intervals, "draws": draws}


def decision_for(scores, uncertainty):
    selected, prior = scores["selected"], scores["family_prior"]
    checks = {
        "macro_ba_ge_085": selected["macro"]["balanced_accuracy"] >= 0.85,
        "gain_ge_010": selected["macro"]["balanced_accuracy"] - prior["macro"]["balanced_accuracy"] >= 0.10,
        "all_action_ba_ge_075": all(selected[a]["balanced_accuracy"] >= 0.75 for a in ACTIONS),
        "all_failure_recall_ge_075": all(selected[a]["failure_recall"] >= 0.75 for a in ACTIONS),
        "brier_within_002": selected["macro"]["brier"] <= prior["macro"]["brier"] + 0.02,
    }
    if all(checks.values()):
        decision = "SIMPLE_RULE_SUFFICIENT"
    elif uncertainty["valid"] >= 1000 and uncertainty["intervals"]["gain"][0] > 0:
        decision = "RESIDUAL_REQUIRES_PROBE"
    else:
        decision = "UNCERTAIN_RESIDUAL"
    return decision, checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", action="append", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path("/workspace"))
    parser.add_argument("--output", type=Path, default=Path("/output"))
    parser.add_argument("--artifacts", type=Path, default=Path("/artifacts"))
    args = parser.parse_args()
    if any(args.output.iterdir()):
        raise ValueError("output must be empty")
    frozen = json.loads((args.artifacts / "freeze.json").read_text())
    for name, digest in frozen["source_sha256"].items():
        if sha(args.workspace / name) != digest:
            raise ValueError(f"source changed after freeze: {name}")
    with (args.workspace / "artifacts_v4/segments.tsv").open() as stream:
        rows = [r for r in csv.DictReader(stream, delimiter="\t")
                if r["target_action"] == "True" and r["action_family"] in ACTIONS]
    selection = json.loads((args.workspace / "selection_v4.json").read_text())
    membership = {r["recording_id"]: r["split"] for r in selection["denominator_members"]}
    assert len(rows) == 413 and len({(r["recording_id"], r["segment_index"]) for r in rows}) == 413
    assert all(r["split"] == membership[r["recording_id"]] for r in rows)
    subsets = {split: [r for r in rows if r["split"] == f"{split}_split1.txt"] for split in ("train", "test")}
    assert set(r["recording_id"] for r in subsets["train"]).isdisjoint(r["recording_id"] for r in subsets["test"])
    for split, expected in (("train", (309, 40, 15)), ("test", (104, 10, 5))):
        subset = subsets[split]
        assert (len(subset), sum(r["success"] == "False" for r in subset), len({r["recording_id"] for r in subset})) == expected
    train_rows = extract(subsets["train"], args.input_dir)
    write_rows(args.output / "train_features.jsonl", train_rows)
    training = train(train_rows)
    training.update(sealed_at_utc=datetime.now(timezone.utc).isoformat(),
                    train_features_sha256=sha(args.output / "train_features.jsonl"),
                    freeze_sha256=sha(args.artifacts / "freeze.json"))
    write_json(args.artifacts / "training.json", training)
    training_digest = sha(args.artifacts / "training.json")
    print(f"training sealed before test extraction: {training_digest}", flush=True)
    test_started = datetime.now(timezone.utc).isoformat()
    test_rows = extract(subsets["test"], args.input_dir)
    write_rows(args.output / "test_features.jsonl", test_rows)
    predictions, table, scores = evaluate(test_rows, training)
    write_rows(args.output / "predictions.jsonl", predictions)
    errors = [r for r in predictions if r["candidate"] == "selected" and r["pred"] != r["success"]]
    write_rows(args.output / "errors.jsonl", errors)
    uncertainty = bootstrap(predictions)
    write_json(args.output / "bootstrap.json", uncertainty)
    decision, checks = decision_for(scores, uncertainty)
    error_counts = []
    for action in ACTIONS:
        for recording in sorted({r["recording_id"] for r in test_rows}):
            subset = [r for r in predictions if r["candidate"] == "selected" and r["action"] == action and r["recording_id"] == recording]
            error_counts.append({"action": action, "recording_id": recording, "n": len(subset),
                                 "failure": sum(not r["success"] for r in subset),
                                 "false_success": sum(r["pred"] and not r["success"] for r in subset),
                                 "false_failure": sum(not r["pred"] and r["success"] for r in subset)})
    overlap = {}
    fixed = ("state_d2", "force_d2", "combined_d2")
    sets = {c: {r["id"] for r in predictions if r["candidate"] == c and r["pred"] != r["success"]} for c in fixed}
    for first in fixed:
        for second in fixed:
            overlap[f"{first}&{second}"] = len(sets[first] & sets[second])
    summary = {"decision": decision, "practical_checks": checks,
               "denominator": {"train": 309, "train_failure": 40, "test": 104, "test_failure": 10},
               "selected": training["selected"], "scores": scores,
               "uncertainty": {k: v for k, v in uncertainty.items() if k != "draws"},
               "error_overlap": overlap, "selected_errors": len(errors),
               "training_sha256": training_digest, "test_extraction_started_at_utc": test_started,
               "device": "cpu", "seed": SEED}
    assert sha(args.artifacts / "training.json") == training_digest
    write_tsv(args.artifacts / "metrics.tsv", table)
    write_tsv(args.artifacts / "error_counts.tsv", error_counts)
    write_json(args.artifacts / "summary.json", summary)
    write_json(args.output / "provenance.json", {"freeze_sha256": sha(args.artifacts / "freeze.json"),
                                                "training_sha256": training_digest, "device": "cpu",
                                                "numpy": np.__version__, "h5py": h5py.__version__})
    print(json.dumps({"decision": decision, "selected": training["selected"],
                      "macro": scores["selected"]["macro"], "checks": checks,
                      "uncertainty": summary["uncertainty"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
