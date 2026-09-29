"""Independent native-pixel score reconstruction using Pillow histograms, no NumPy."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops


def checksum(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(args):
    output = Path(args.output)
    assert not output.exists()
    prep, scored = Path(args.prepared), Path(args.scored)
    cases = {c["id"]: c for c in json.loads((prep / "cases.json").read_text())}
    results = [json.loads(line) for line in (scored / "scores.jsonl").read_text().splitlines()]
    summary = json.loads((scored / "summary.json").read_text())
    assert len(results) == len(cases) * 3 == 45
    keys = {(r["case"], r["view_index"]) for r in results}
    assert len(keys) == len(results) and keys == {(c, v) for c in cases for v in range(3)}
    max_error = 0.0
    for r in results:
        c, v = cases[r["case"]], r["view_index"]
        pa, pb = (prep / "originals" / c[k][v] for k in ("start", "end"))
        with Image.open(pa) as ia, Image.open(pb) as ib:
            a, b = ia.convert("RGB"), ib.convert("RGB")
        assert a.size == b.size
        hist = ImageChops.difference(a, b).histogram()
        n = a.width * a.height * 3
        total = sum((i % 256) * count for i, count in enumerate(hist))
        assert sum(hist) == n
        expected = total / (255 * n)
        error = abs(expected - r["mean_absolute_change"])
        max_error = max(max_error, error)
        assert error < 1e-14 and total == r["absolute_difference_sum"] and n == r["rgb_element_count"]
        assert (total == 0) == r["rgb_equal"]
        assert (checksum(pa) == checksum(pb)) == r["byte_equal"]
        assert r["source_row_1based"] == c["source_row_1based"] and r["source_label"] == c["source_label"]
        if c["role"] == "constructed":
            assert total == 0
    for cmp in summary["comparison"]:
        rows = {r["role"]: r for r in results if r["group"] == cmp["group"] and r["view_index"] == cmp["view_index"]}
        assert cmp["failure_change"] == rows["source_failure"]["mean_absolute_change"]
        assert cmp["success_change"] == rows["source_success"]["mean_absolute_change"]
    result = {"status": "PASS", "independently_reconstructed_rows": len(results),
              "max_absolute_mean_error": max_error, "cases": len(cases),
              "method": "Pillow ImageChops unsigned difference histogram, integer weighted sum; no NumPy import",
              "scores_sha256": checksum(scored / "scores.jsonl"), "verify_source_sha256": checksum(__file__),
              "limitations": "Same image decoder; verifies numeric arithmetic and row mapping, not source labels or failure provenance."}
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--prepared", required=True)
    p.add_argument("--scored", required=True)
    p.add_argument("--output", required=True)
    main(p.parse_args())
