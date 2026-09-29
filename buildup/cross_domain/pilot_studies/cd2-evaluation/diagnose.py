"""Post-hoc explanation of verified outputs; does not change selection or metrics."""
import argparse
import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads((args.output / "protocol.json").read_text())
    refs = {}
    matrices = {}
    for model in config["models"]:
        doc = json.loads((args.input / "source/data/results" / (model + ".json")).read_text(), parse_float=F)
        table = {(t["category"], t["name"], level): F(v) for t in doc["tasks"]
                 for level, v in enumerate(t["data"]["sr"])}
        matrices[model] = [table[key] for key in sorted(table)]
        refs[model] = sum(table.values()) / len(table)
        cells = sorted(table)
    groups = defaultdict(list)
    for i, (category, _, level) in enumerate(cells):
        groups[(category, level)].append(i)
    pair_groups = defaultdict(list)
    for line in (args.output / "pairs.jsonl").read_text().splitlines():
        r = json.loads(line)
        key = (r["split"], r["budget"], r["method"], r["left"], r["right"])
        pair_groups[key].append(r)
    pair_table = []
    for (split, budget, method, left, right), rows in sorted(pair_groups.items()):
        counts = Counter(r["status"] for r in rows)
        pair_table.append({"split": split, "budget": budget, "method": method, "left": left, "right": right,
                           "reference_gap_pp": float(100 * (refs[left] - refs[right])),
                           "draws": len(rows), "reversed": counts["reversed"], "predicted_tie": counts["predicted_tie"]})
    subsets = [json.loads(line) for line in (args.output / "subsets.jsonl").read_text().splitlines()]
    cases = []
    for subset in subsets:
        if subset["method"] != "greedy":
            continue
        ids = subset["indices"]
        for model in config["splits"][subset["split"]]["target"]:
            values = matrices[model]
            terms = []
            for (category, level), indices in sorted(groups.items()):
                obs = [i for i in indices if i in ids]
                truth = sum(values[i] for i in indices) / len(indices)
                sampled = sum(values[i] for i in obs) / len(obs) if obs else None
                p, q = F(len(indices), 33), F(len(obs), len(ids))
                within = q * (sampled - truth) if obs else F(0)
                allocation = (q - p) * truth
                terms.append({"category": category, "level": level, "n_observed": len(obs),
                              "reference": float(truth), "estimate": float(sampled) if obs else None,
                              "within_contribution_pp": float(100 * within),
                              "allocation_contribution_pp": float(100 * allocation),
                              "total_contribution_exact": str(within + allocation)})
            estimate = sum(values[i] for i in ids) / len(ids)
            assert sum(F(t["total_contribution_exact"]) for t in terms) == estimate - refs[model]
            cases.append({"subset_id": subset["subset_id"], "model": model,
                          "reference_pp": float(100 * refs[model]), "estimate_pp": float(100 * estimate),
                          "signed_error_pp": float(100 * (estimate - refs[model])),
                          "missing_strata": [f"{t['category']}/L{t['level']}" for t in terms if t["n_observed"] == 0],
                          "stratum_error_decomposition": terms})
    report = {"purpose": "post-hoc explanation of close reference gaps and aggregate error cancellation; no new selection",
              "reference_means_pp": {m: float(100 * v) for m, v in refs.items()},
              "pair_breakdown": pair_table, "greedy_cases": cases,
              "verified_exact_decompositions": len(cases),
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    args.destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    for row in pair_table:
        if row["budget"] == 18:
            print(json.dumps(row))
    print(json.dumps({"greedy_cases": len(cases), "exact_decompositions_passed": len(cases)}))


if __name__ == "__main__":
    main()
