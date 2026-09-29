"""Reconstruct saved scores from original decimals without importing analysis code."""
import argparse
import hashlib
import itertools
import json
import math
import random
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path


CHECKS = 0


def check(condition, context):
    global CHECKS
    CHECKS += 1
    if not condition:
        raise AssertionError(context)


def close(actual, expected, context):
    check(actual is not None and math.isfinite(actual) and abs(actual - float(expected)) < 1e-10, context)


def avg(values):
    return sum(values) / len(values)


def records(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads((args.output / "protocol.json").read_text())
    check(config == json.loads(Path("/study/protocol.json").read_text()), "image/output config")
    manifest = json.loads((args.input / "source_manifest.json").read_text())
    check(manifest == json.loads((args.output / "input_manifest.json").read_text()), "source manifest")
    for entry in manifest["files"]:
        payload = (args.input / "source" / entry["source_path"]).read_bytes()
        check(len(payload) == entry["bytes"] and hashlib.sha256(payload).hexdigest() == entry["sha256"], "input hash")
    for entry in json.loads((args.output / "artifacts.json").read_text()):
        payload = (args.output / entry["path"]).read_bytes()
        check(len(payload) == entry["bytes"] and hashlib.sha256(payload).hexdigest() == entry["sha256"], "output hash")
    matrix = {}
    for model in config["models"]:
        data = json.loads((args.input / "source/data/results" / (model + ".json")).read_text(), parse_float=F)
        values = {(t["category"], t["name"], level): F(value)
                  for t in data["tasks"] for level, value in enumerate(t["data"]["sr"])}
        matrix[model] = [values[key] for key in sorted(values)]
        keys = sorted(values)
    expected_cells = [{"index": i, "category": c, "suite": s, "level": l} for i, (c, s, l) in enumerate(keys)]
    reference = json.loads((args.output / "reference.json").read_text())
    check(reference["cells"] == expected_cells, "cell ordering")
    groups = defaultdict(list)
    for i, (category, _, level) in enumerate(keys):
        groups[(category, level)].append(i)
    groups = dict(sorted(groups.items()))
    refs = {m: avg(values) for m, values in matrix.items()}
    for model, values in matrix.items():
        for actual, expected in zip(reference["models"][model]["values"], values):
            close(actual, expected, "reference values")
        close(reference["models"][model]["estimate"], refs[model], "full-budget reconstruction")
        close(reference["models"][model]["reference"], refs[model], "reference mean")
        close(reference["models"][model]["full_profile_mae"], 0, "full-budget profile")
    subsets = records(args.output / "subsets.jsonl")
    scores = records(args.output / "scores.jsonl")
    pairs = records(args.output / "pairs.jsonl")
    by_id = {row["subset_id"]: row for row in subsets}
    check(len(by_id) == len(subsets) == 1604, "unique subset count")
    score_map = {(r["subset_id"], r["model"]): r for r in scores}
    pair_map = {(r["subset_id"], r["left"], r["right"]): r for r in pairs}
    check(len(score_map) == len(scores) == 4812, "unique target score count")
    check(len(pair_map) == len(pairs) == 5614, "unique pair count")
    for subset in subsets:
        sid, selected = subset["subset_id"], subset["indices"]
        split, method, budget = subset["split"], subset["method"], subset["budget"]
        target = config["splits"][split]["target"]
        dev = config["splits"][split]["development"]
        check(set(target).isdisjoint(dev), "selection leakage")
        check(len(selected) == len(set(selected)) == budget and all(0 <= i < 33 for i in selected), "subset validity")
        observed = {g: [i for i in indices if i in selected] for g, indices in groups.items()}
        check(subset["observed_strata"] == sum(bool(v) for v in observed.values()), "coverage")
        if method == "greedy":
            check(subset["seed"] is None and subset["selection_source_models"] == dev, "development-only greedy")
            chosen = []
            for step, saved in enumerate(subset["greedy_trace"], 1):
                costs = {i: avg([(avg([matrix[m][j] for j in chosen + [i]]) - refs[m]) ** 2 for m in dev])
                         for i in range(33) if i not in chosen}
                winner = min(costs, key=lambda i: (costs[i], i))
                check(winner == saved["cell_index"] == selected[step - 1], "greedy minimizer")
                check(F(saved["objective_exact"]) == costs[winner], "greedy exact objective")
                chosen.append(winner)
            check(len(chosen) == budget, "greedy trace length")
        else:
            check(subset["selection_source_models"] == [], "random selection cannot use outcomes")
            rng = random.Random(subset["seed"])
            if method == "uniform":
                expected = rng.sample(range(33), budget)
            else:
                expected = []
                for (category, level), indices in groups.items():
                    allocation = config["stratified_allocation"][str(budget)][category]
                    check(len(observed[(category, level)]) == allocation, "stratified allocation")
                    expected.extend(rng.sample(indices, allocation))
            check(selected == expected, "seed reconstruction")
            other = "B" if split == "A" else "A"
            check(selected == by_id[f"{other}-{budget}-{method}-{subset['seed']}"]["indices"], "shared random subset")
        weights = [F(len(groups[(keys[i][0], keys[i][2])]), 33 * len(observed[(keys[i][0], keys[i][2])]))
                   if method == "stratified" else F(1, budget) for i in selected]
        check(sum(weights) == 1, "weight normalization")
        for actual, expected in zip(subset["weights"], weights):
            close(actual, expected, "cell weight")
        estimated = {}
        for model in target:
            row = score_map[(sid, model)]
            estimate = sum(matrix[model][i] * w for i, w in zip(selected, weights))
            estimated[model] = estimate
            close(row["estimate"], estimate, "independent weighted score")
            close(row["reference"], refs[model], "model reference")
            close(row["absolute_error"], abs(estimate - refs[model]), "score error")
            profile = {(p["category"], p["level"]): p for p in row["profile"]}
            check(len(profile) == len(row["profile"]) == 12, "profile schema")
            errors = []
            for group, indices in groups.items():
                p = profile[group]
                truth = avg([matrix[model][i] for i in indices])
                check(p["n_total"] == len(indices) and p["n_observed"] == len(observed[group]), "stratum denominator")
                close(p["reference"], truth, "profile reference")
                if not observed[group]:
                    check(p["estimate"] is None and p["absolute_error"] is None, "missing is not zero")
                else:
                    prediction = avg([matrix[model][i] for i in observed[group]])
                    error = abs(prediction - truth)
                    close(p["estimate"], prediction, "stratum estimate")
                    close(p["absolute_error"], error, "stratum error")
                    errors.append(error)
            check(row["observed_strata"] == len(errors), "model coverage")
            close(row["partial_profile_mae"], avg(errors), "partial MAE")
            close(row["observed_profile_max_error"], max(errors), "maximum observed error")
            if len(errors) == 12:
                close(row["full_profile_mae"], avg(errors), "complete profile MAE")
            else:
                check(row["full_profile_mae"] is None, "incomplete profile has no full MAE")
        def signed(value):
            return 0 if abs(value) <= F(str(config["tie_tolerance"])) else (1 if value > 0 else -1)
        for a, b in itertools.combinations(target, 2):
            row = pair_map[(sid, a, b)]
            rs, ps = signed(refs[a] - refs[b]), signed(estimated[a] - estimated[b])
            status = "reference_tie" if rs == 0 else "predicted_tie" if ps == 0 else "correct" if rs == ps else "reversed"
            check((row["reference_sign"], row["predicted_sign"], row["status"]) == (rs, ps, status), "independent pair ordering")
    summary = json.loads((args.output / "summary.json").read_text())
    check(len(summary) == 12, "summary row count")
    for row in summary:
        def matching(r):
            return all(r[k] == row[k] for k in ("split", "budget", "method"))
        ss, sr, pr = ([r for r in collection if matching(r)] for collection in (subsets, scores, pairs))
        counts = Counter(r["status"] for r in pr)
        complete = [r for r in sr if r["full_profile_mae"] is not None]
        integers = {"draws": len(ss), "target_score_rows": len(sr), "pair_count": len(pr),
                    "reference_distinct_pairs": len(pr) - counts["reference_tie"], "correct_pairs": counts["correct"],
                    "reversed_pairs": counts["reversed"], "predicted_ties": counts["predicted_tie"],
                    "reference_ties": counts["reference_tie"], "complete_draws": sum(r["observed_strata"] == 12 for r in ss),
                    "complete_profile_score_rows": len(complete)}
        for key, expected in integers.items():
            check(row[key] == expected, "summary count " + key)
        floats = {"score_mae_pp": 100 * avg([r["absolute_error"] for r in sr]),
                  "mean_observed_strata": avg([r["observed_strata"] for r in sr]),
                  "partial_profile_mae_pp": 100 * avg([r["partial_profile_mae"] for r in sr]),
                  "observed_profile_max_error_pp_mean": 100 * avg([r["observed_profile_max_error"] for r in sr])}
        for key, expected in floats.items():
            close(row[key], expected, "summary value " + key)
        for key, numerator in (("reversal_percent", counts["reversed"]), ("predicted_tie_percent", counts["predicted_tie"])):
            denominator = integers["reference_distinct_pairs"]
            if denominator:
                close(row[key], 100 * numerator / denominator, "ordering rate")
            else:
                check(row[key] is None, "undefined ordering rate")
        if complete:
            close(row["full_profile_mae_pp_conditional"], 100 * avg([r["full_profile_mae"] for r in complete]), "conditional profile summary")
        else:
            check(row["full_profile_mae_pp_conditional"] is None, "undefined complete profile summary")

    # Only these small behavioral checks import the producer. All saved-output checks above are independent.
    from run import evaluate, greedy, sign
    toy = [F(0), F(1), F(1), F(0)]
    strata = {("A", 0): [0, 1], ("B", 0): [2], ("C", 0): [3]}
    unequal = evaluate(toy, [0, 2, 3], [.5, .25, .25], strata)
    close(unequal["estimate"], F(1, 4), "unequal strata cannot use unweighted mean")
    missing = evaluate(toy, [0], [1.0], strata)
    check(missing["full_profile_mae"] is None and missing["profile"][1]["estimate"] is None, "missing control")
    all_cells = evaluate(toy, list(range(4)), [.25] * 4, strata)
    close(all_cells["estimate"], F(1, 2), "toy full budget")
    close(all_cells["full_profile_mae"], 0, "toy full profile")
    check([sign(x, 1e-12) for x in (0, 1e-13, -1e-13, .1, -.1)] == [0, 0, 0, 1, -1], "tie control")
    check(greedy({"development": [F(1, 2)] * 3}, 2)[0] == [0, 1], "lexical exact tie")
    receipt = {"status": "passed", "checks": CHECKS, "source_files": len(manifest["files"]),
               "verified_subsets": len(subsets), "verified_model_scores": len(scores), "verified_pairs": len(pairs),
               "verified_summaries": len(summary), "arithmetic": "original decimal values as exact Fractions; float output tolerance 1e-10",
               "claim_boundary": "finite aggregate table; no episode-level inference"}
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
