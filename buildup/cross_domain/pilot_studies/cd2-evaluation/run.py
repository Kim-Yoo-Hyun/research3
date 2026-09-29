"""Exploratory compression of a fixed published aggregate table; CPU Docker only."""
import argparse
import csv
import hashlib
import itertools
import json
import math
import platform
import random
import sys
import time
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def mean(xs):
    return math.fsum(xs) / len(xs)


def sign(x, tol):
    return 0 if abs(x) <= tol else (1 if x > 0 else -1)


def load_data(input_dir, config):
    manifest = json.loads((input_dir / "source_manifest.json").read_text())
    assert manifest["commit"] == config["source_commit"]
    assert set(manifest["selected_model_ids"]) == set(config["models"])
    for record in manifest["files"]:
        payload = (input_dir / "source" / record["source_path"]).read_bytes()
        assert len(payload) == record["bytes"]
        assert hashlib.sha256(payload).hexdigest() == record["sha256"]
    cells = None
    matrix = {}
    for model in config["models"]:
        path = input_dir / "source/data/results" / (model + ".json")
        data = json.loads(path.read_text(), parse_float=Fraction, parse_int=Fraction)
        values = {}
        for task in data["tasks"]:
            assert len(task["data"]["sr"]) == 3
            for level, sr in enumerate(task["data"]["sr"]):
                key = (task["category"], task["name"], level)
                assert key not in values and 0 <= sr <= 1
                values[key] = sr
        if cells is None:
            cells = sorted(values)
        assert sorted(values) == cells and len(cells) == 33
        matrix[model] = [values[cell] for cell in cells]
    strata = defaultdict(list)
    for index, (category, _, level) in enumerate(cells):
        strata[(category, level)].append(index)
    assert len(strata) == 12
    return manifest, cells, dict(sorted(strata.items())), matrix


def greedy(development, budget):
    """Only development data can enter selection; exact rational tie breaking."""
    n = len(next(iter(development.values())))
    reference = {m: sum(xs) / n for m, xs in development.items()}
    sums = {m: Fraction(0) for m in development}
    selected = []
    trace = []
    for step in range(1, budget + 1):
        candidates = []
        for i in range(n):
            if i in selected:
                continue
            objective = sum(((sums[m] + xs[i]) / step - reference[m]) ** 2
                            for m, xs in development.items()) / len(development)
            candidates.append((objective, i))
        objective, chosen = min(candidates)
        selected.append(chosen)
        trace.append({"cell_index": chosen, "objective_exact": str(objective)})
        for m, xs in development.items():
            sums[m] += xs[chosen]
    return selected, trace


def sample(method, budget, seed, strata, config):
    rng = random.Random(seed)
    if method == "uniform":
        return rng.sample(range(33), budget)
    selected = []
    for (category, _), indices in strata.items():
        count = config["stratified_allocation"][str(budget)][category]
        selected.extend(rng.sample(indices, count))
    return selected


def evaluate(values, selected, weights, strata):
    score = math.fsum(float(values[i]) * w for i, w in zip(selected, weights))
    profiles = []
    for (category, level), indices in strata.items():
        observed = [i for i in indices if i in selected]
        ref = mean([float(values[i]) for i in indices])
        estimate = mean([float(values[i]) for i in observed]) if observed else None
        profiles.append({"category": category, "level": level, "n_total": len(indices),
                         "n_observed": len(observed), "reference": ref, "estimate": estimate,
                         "absolute_error": abs(estimate - ref) if observed else None})
    errors = [p["absolute_error"] for p in profiles if p["estimate"] is not None]
    reference = mean([float(v) for v in values])
    return {"reference": reference, "estimate": score, "absolute_error": abs(score - reference),
            "profile": profiles, "observed_strata": len(errors),
            "partial_profile_mae": mean(errors), "observed_profile_max_error": max(errors),
            "full_profile_mae": mean(errors) if len(errors) == len(strata) else None}


def aggregate(subsets, scores, pairs):
    table = []
    keys = sorted({(r["split"], r["budget"], r["method"]) for r in subsets})
    for split, budget, method in keys:
        def belongs(row):
            return (row["split"], row["budget"], row["method"]) == (split, budget, method)
        subs = [r for r in subsets if belongs(r)]
        rows = [r for r in scores if belongs(r)]
        ps = [r for r in pairs if belongs(r)]
        complete = [r for r in rows if r["full_profile_mae"] is not None]
        counts = Counter(r["status"] for r in ps)
        decisive = len(ps) - counts["reference_tie"]
        table.append({"split": split, "budget": budget, "method": method, "draws": len(subs),
                      "target_score_rows": len(rows), "score_mae_pp": 100 * mean([r["absolute_error"] for r in rows]),
                      "pair_count": len(ps), "reference_distinct_pairs": decisive,
                      "correct_pairs": counts["correct"], "reversed_pairs": counts["reversed"],
                      "predicted_ties": counts["predicted_tie"], "reference_ties": counts["reference_tie"],
                      "reversal_percent": 100 * counts["reversed"] / decisive if decisive else None,
                      "predicted_tie_percent": 100 * counts["predicted_tie"] / decisive if decisive else None,
                      "mean_observed_strata": mean([r["observed_strata"] for r in rows]),
                      "complete_draws": sum(r["observed_strata"] == 12 for r in subs),
                      "complete_profile_score_rows": len(complete),
                      "full_profile_mae_pp_conditional": 100 * mean([r["full_profile_mae"] for r in complete]) if complete else None,
                      "partial_profile_mae_pp": 100 * mean([r["partial_profile_mae"] for r in rows]),
                      "observed_profile_max_error_pp_mean": 100 * mean([r["observed_profile_max_error"] for r in rows])})
    return table


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=Path("/study/protocol.json"))
    args = parser.parse_args()
    start = time.monotonic()
    args.output.mkdir(parents=True, exist_ok=True)
    assert not (args.output / "reference.json").exists(), "Do not overwrite a completed/partial observation"
    config = json.loads(args.config.read_text())
    manifest, cells, strata, matrix = load_data(args.input, config)
    dump(args.output / "protocol.json", config)
    dump(args.output / "input_manifest.json", manifest)
    reference = {"cells": [{"index": i, "category": c, "suite": s, "level": l} for i, (c, s, l) in enumerate(cells)],
                 "models": {m: {"values": [float(v) for v in xs],
                                **evaluate(xs, list(range(33)), [1 / 33] * 33, strata)} for m, xs in matrix.items()}}
    dump(args.output / "reference.json", reference)
    subsets, scores, pairs = [], [], []
    for split, groups in config["splits"].items():
        assert set(groups["target"]).isdisjoint(groups["development"])
        assert set(groups["target"] + groups["development"]) == set(matrix)
        for budget in config["budgets"]:
            for method in config["methods"]:
                seeds = [None] if method == "greedy" else range(config["seed_start"], config["seed_stop"])
                for seed in seeds:
                    trace = []
                    if method == "greedy":
                        selected, trace = greedy({m: matrix[m] for m in groups["development"]}, budget)
                    else:
                        selected = sample(method, budget, seed, strata, config)
                    assert len(selected) == len(set(selected)) == budget
                    counts = Counter((cells[i][0], cells[i][2]) for i in selected)
                    weights = [len(strata[(cells[i][0], cells[i][2])]) / (33 * counts[(cells[i][0], cells[i][2])])
                               if method == "stratified" else 1 / budget for i in selected]
                    assert abs(math.fsum(weights) - 1) < 1e-12
                    sid = f"{split}-{budget}-{method}-{seed if seed is not None else 'deterministic'}"
                    base = {"subset_id": sid, "split": split, "budget": budget, "method": method, "seed": seed}
                    subsets.append({**base, "indices": selected, "weights": weights, "observed_strata": len(counts),
                                    "selection_source_models": groups["development"] if method == "greedy" else [],
                                    "greedy_trace": trace})
                    target = {}
                    for model in groups["target"]:
                        row = {**base, "model": model, **evaluate(matrix[model], selected, weights, strata)}
                        scores.append(row)
                        target[model] = row
                    for left, right in itertools.combinations(groups["target"], 2):
                        ref_sign = sign(target[left]["reference"] - target[right]["reference"], config["tie_tolerance"])
                        pred_sign = sign(target[left]["estimate"] - target[right]["estimate"], config["tie_tolerance"])
                        status = ("reference_tie" if ref_sign == 0 else "predicted_tie" if pred_sign == 0
                                  else "correct" if ref_sign == pred_sign else "reversed")
                        pairs.append({**base, "left": left, "right": right, "reference_sign": ref_sign,
                                      "predicted_sign": pred_sign, "status": status})
    for name, records in (("subsets", subsets), ("scores", scores), ("pairs", pairs)):
        with (args.output / (name + ".jsonl")).open("w") as stream:
            for record in records:
                stream.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
    summary = aggregate(subsets, scores, pairs)
    dump(args.output / "summary.json", summary)
    with (args.output / "summary.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    dump(args.output / "execution.json", {"python": sys.version, "platform": platform.platform(), "device": "cpu",
         "duration_seconds": time.monotonic() - start, "argv": sys.argv,
         "counts": {"subsets": len(subsets), "scores": len(scores), "pairs": len(pairs)},
         "code_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in Path("/study").iterdir() if p.is_file()}})
    payload_names = ("protocol.json", "input_manifest.json", "reference.json", "subsets.jsonl",
                     "scores.jsonl", "pairs.jsonl", "summary.json", "summary.csv", "execution.json")
    dump(args.output / "artifacts.json", [{"path": name, "bytes": (args.output / name).stat().st_size,
         "sha256": hashlib.sha256((args.output / name).read_bytes()).hexdigest()} for name in payload_names])
    print(json.dumps({"completed": True, "subsets": len(subsets), "scores": len(scores), "pairs": len(pairs),
                      "seconds": time.monotonic() - start}))


if __name__ == "__main__":
    main()
