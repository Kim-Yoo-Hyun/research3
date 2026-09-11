#!/usr/bin/env python3
"""Independent artifact arithmetic and integrity checks; run in v5 Docker."""
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def close(a, b):
    assert math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-10), (a, b)


def main():
    base, raw, out = Path("/workspace"), Path("/output"), Path("/artifacts")
    summary = json.loads((out / "summary.json").read_text())
    training = json.loads((out / "training.json").read_text())
    freeze = json.loads((out / "freeze.json").read_text())
    for name, value in freeze["source_sha256"].items():
        assert digest(base / name) == value, name
    assert digest(out / "training.json") == summary["training_sha256"]
    assert digest(raw / "train_features.jsonl") == training["train_features_sha256"]
    assert training["sealed_at_utc"] <= summary["test_extraction_started_at_utc"]
    assert digest(out / "freeze.json") == training["freeze_sha256"]
    for action, scores in training["cv"].items():
        def rank(name):
            if name.endswith("prior"):
                depth, width = 0, 0
            else:
                kind, suffix = name.rsplit("_d", 1)
                depth = int(suffix)
                width = {"duration": 1, "state": 14, "force": 18, "combined": 33}[kind]
            return (-scores[name]["balanced_accuracy"], scores[name]["brier"], depth, width, name)
        assert min(scores, key=rank) == training["selected"][action]
    with (base / "artifacts_v4/segments.tsv").open() as stream:
        denominator = {r["recording_id"] + ":" + r["segment_index"]: r for r in csv.DictReader(stream, delimiter="\t")
                       if r["target_action"] == "True" and r["action_family"] in ("pick", "insert", "remove")}
    subsets = {split: jsonl(raw / f"{split}_features.jsonl") for split in ("train", "test")}
    for split, expected, failures in (("train", 309, 40), ("test", 104, 10)):
        rows = subsets[split]
        assert len(rows) == len({r["id"] for r in rows}) == expected
        assert sum(not r["success"] for r in rows) == failures
        for row in rows:
            source = denominator[row["id"]]
            assert source["split"] == f"{split}_split1.txt"
            assert row["success"] == (source["success"] == "True")
            assert row["action"] == source["action_family"]
            assert len(row["features"]) == 33 and all(math.isfinite(x) for x in row["features"].values())
    assert {r["id"] for rows in subsets.values() for r in rows} == set(denominator)
    assert {r["recording_id"] for r in subsets["train"]}.isdisjoint(r["recording_id"] for r in subsets["test"])
    predictions = jsonl(raw / "predictions.jsonl")
    test = {r["id"]: r for r in subsets["test"]}
    candidates = set(summary["scores"])
    assert len(predictions) == 104 * len(candidates) == 1144
    assert len({(r["candidate"], r["id"]) for r in predictions}) == len(predictions)
    recalculated = {}
    for candidate in candidates:
        recalculated[candidate] = {}
        group = [r for r in predictions if r["candidate"] == candidate]
        assert {r["id"] for r in group} == set(test)
        for row in group:
            assert row["success"] == test[row["id"]]["success"]
            assert row["action"] == test[row["id"]]["action"]
            name = training["selected"][row["action"]] if candidate == "selected" else candidate
            model = training["fitted"][row["action"]][name]
            if "tree" in model:
                leaf = model["tree"]
                while "feature" in leaf:
                    value = test[row["id"]]["features"][leaf["feature"]]
                    leaf = leaf["left"] if value <= leaf["threshold"] else leaf["right"]
                pred, probability = leaf["pred"], leaf["p"]
            else:
                probability = model["texts"].get(row["text"], model["p"])
                pred = probability >= .5
            assert row["pred"] == pred
            close(row["p"], probability)
        for action in ("pick", "insert", "remove"):
            rows = [r for r in group if r["action"] == action]
            n_success = sum(r["success"] for r in rows)
            n_failure = len(rows) - n_success
            tp = sum(r["pred"] and r["success"] for r in rows)
            tn = sum(not r["pred"] and not r["success"] for r in rows)
            ba = (tp / n_success + tn / n_failure) / 2
            brier = sum((r["p"] - r["success"])**2 for r in rows) / len(rows)
            logloss = -sum(math.log(r["p"] if r["success"] else 1-r["p"]) for r in rows) / len(rows)
            ece = 0.
            for i in range(5):
                bucket = [r for r in rows if min(int(r["p"] * 5), 4) == i]
                if bucket:
                    ece += abs(sum(r["p"] - r["success"] for r in bucket)) / len(rows)
            values = {"balanced_accuracy": ba, "brier": brier, "log_loss": logloss, "ece_5": ece}
            for key, value in values.items():
                close(summary["scores"][candidate][action][key], value)
            for key, value in {"n": len(rows), "tp": tp, "tn": tn, "fp": n_failure-tn, "fn": n_success-tp}.items():
                assert summary["scores"][candidate][action][key] == value
            recalculated[candidate][action] = values
        for key in ("balanced_accuracy", "brier", "log_loss", "ece_5"):
            close(summary["scores"][candidate]["macro"][key], sum(v[key] for v in recalculated[candidate].values()) / 3)
    errors = jsonl(raw / "errors.jsonl")
    assert {r["id"] for r in errors} == {r["id"] for r in predictions if r["candidate"] == "selected" and r["pred"] != r["success"]}
    assert len(errors) == summary["selected_errors"]
    boot = json.loads((raw / "bootstrap.json").read_text())
    assert boot["valid"] + boot["invalid"] == boot["requested"] == 2000
    assert len(boot["draws"]) == boot["valid"]
    for key in ("macro_ba", "gain"):
        values = sorted(row[key] for row in boot["draws"])
        for quantile, reported in zip((.025, .975), boot["intervals"][key]):
            index = (len(values) - 1) * quantile
            low = int(index)
            high = min(low + 1, len(values) - 1)
            close(values[low] + (index-low) * (values[high]-values[low]), reported)
    # Compute the decision independently from the stored scalar metrics.
    s, p = summary["scores"]["selected"], summary["scores"]["family_prior"]
    practical = (s["macro"]["balanced_accuracy"] >= .85 and
                 s["macro"]["balanced_accuracy"] - p["macro"]["balanced_accuracy"] >= .10 and
                 all(s[a]["balanced_accuracy"] >= .75 and s[a]["failure_recall"] >= .75 for a in ("pick", "insert", "remove")) and
                 s["macro"]["brier"] <= p["macro"]["brier"] + .02)
    expected = "SIMPLE_RULE_SUFFICIENT" if practical else (
        "RESIDUAL_REQUIRES_PROBE" if boot["valid"] >= 1000 and boot["intervals"]["gain"][0] > 0 else "UNCERTAIN_RESIDUAL")
    assert expected == summary["decision"]
    result = {"status": "PASS", "population_rows": 413, "predictions": len(predictions),
              "selected_errors": len(errors), "decision": expected,
              "checks": ["frozen sources", "train before test seal", "fixed denominator", "split disjointness",
                         "prediction replay", "independent metrics", "error rows", "decision arithmetic"]}
    with (out / "verification.json").open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    hashes = {str(p): digest(p) for root in (raw, out) for p in sorted(root.iterdir()) if p.is_file() and p.name != "checksums.json"}
    with (out / "checksums.json").open("x") as stream:
        json.dump(hashes, stream, indent=2)
        stream.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
