"""Prepare a diagnostic image figure, then separately score after visual notes exist."""
import argparse
import hashlib
import io
import json
import platform
import tarfile
from pathlib import Path

import numpy as np
import PIL
from PIL import Image, ImageDraw


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def rgb(path):
    with Image.open(path) as image:
        return image.convert("RGB")


def render_panel(rows, dest):
    # Diagnostic figure only: native pixels remain available separately and are used for scores.
    cell_w, cell_h, header = 640, 430, 46
    canvas = Image.new("RGB", (3 * cell_w, len(rows) * (cell_h + header)), "white")
    draw = ImageDraw.Draw(canvas)
    for row_id, (caption, paths) in enumerate(rows):
        top = row_id * (cell_h + header)
        for view, path in enumerate(paths):
            image = rgb(path)
            image.thumbnail((cell_w, cell_h), Image.Resampling.LANCZOS)
            draw.text((view * cell_w + 8, top + 8), caption + f" | view {view}", fill="black")
            canvas.paste(image, (view * cell_w, top + header))
    canvas.save(dest)


def prepare(args):
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=False)
    spec = json.loads(Path(args.selection).read_text())
    assert Path(args.archive).stat().st_size == spec["archive_bytes"]
    assert digest(args.archive) == spec["archive_sha256"]
    assert digest(args.metadata) == spec["metadata_sha256"]
    records = [json.loads(line) for line in Path(args.metadata).read_text().splitlines()]
    row_ids = sorted(set(spec["controls"] + [p[k] for p in spec["pairs"] for k in ("failure", "success")]))
    selected = {row_id: records[row_id - 1] for row_id in row_ids}
    for rec in selected.values():
        assert len(rec["images"]) == 6
    wanted = {path for rec in selected.values() for path in rec["images"]}
    seen = set()
    identities = []
    # Extract exactly the selected regular files; no archive paths are executed or followed.
    with tarfile.open(args.archive, "r:gz") as archive:
        for member in archive:
            name = member.name.removeprefix("./")
            if name not in wanted:
                continue
            assert member.isfile() and name not in seen
            relative = Path(name)
            assert not relative.is_absolute() and ".." not in relative.parts
            data = archive.extractfile(member).read()
            dest = out / "originals" / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            with Image.open(io.BytesIO(data)) as image:
                image.load()
                size, mode = image.size, image.mode
            identities.append({"path": name, "sha256": hashlib.sha256(data).hexdigest(),
                               "bytes": len(data), "size": size, "mode": mode})
            seen.add(name)
    assert seen == wanted, sorted(wanted - seen)
    cases = []
    for pair in spec["pairs"]:
        failure, success = selected[pair["failure"]], selected[pair["success"]]
        assert failure["execution_reward"] == 0 and success["execution_reward"] == 1
        for key in ("task_instruction", "detailed_subtask_name"):
            assert failure[key] == success[key]
        assert failure["images"][:3] == success["images"][:3]
        rows = []
        for role, rec, row_id in (("source_failure", failure, pair["failure"]),
                                  ("source_success", success, pair["success"]),
                                  ("constructed", success, None)):
            start = rec["images"][:3]
            end = start if role == "constructed" else rec["images"][3:]
            case_id = pair["id"] + "_" + role
            cases.append({"id": case_id, "group": pair["id"], "role": role,
                          "source_row_1based": row_id,
                          "source_label": None if row_id is None else rec["execution_reward"],
                          "task": rec["task_instruction"], "subtask": rec["detailed_subtask_name"],
                          "start": start, "end": end})
        start_paths = [out / "originals" / p for p in failure["images"][:3]]
        rows.append((pair["id"] + " START", start_paths))
        rows.append((f"END A row {pair['failure']}", [out / "originals" / p for p in failure["images"][3:]]))
        rows.append((f"END B row {pair['success']}", [out / "originals" / p for p in success["images"][3:]]))
        render_panel(rows, out / f"{pair['id']}.png")
    controls = []
    for row_id in spec["controls"]:
        rec = selected[row_id]
        assert rec["images"][:3] == rec["images"][3:]
        cases.append({"id": f"control_{row_id}", "group": "controls", "role": "control",
                      "source_row_1based": row_id, "source_label": rec["execution_reward"],
                      "task": rec["task_instruction"], "subtask": rec["detailed_subtask_name"],
                      "start": rec["images"][:3], "end": rec["images"][3:]})
        controls.append((f"row {row_id}: {rec['detailed_subtask_name']}",
                         [out / "originals" / p for p in rec["images"][:3]]))
    render_panel(controls, out / "controls.png")
    dump(out / "cases.json", cases)
    dump(out / "input.json", {"spec": spec, "files": identities, "selected_source_rows": len(selected),
                              "images": len(identities), "cases": len(cases),
                              "python": platform.python_version(), "numpy": np.__version__,
                              "pillow": PIL.__version__, "device": "cpu", "seed": None,
                              "observe_source_sha256": digest(__file__),
                              "numeric_scores_computed": False})
    print(json.dumps({"prepared_cases": len(cases), "images": len(identities), "numeric_scores_computed": False}))


def score(args):
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=False)
    inp = Path(args.prepared)
    annotation = json.loads(Path(args.annotations).read_text())
    assert annotation["phase"] == "before_numeric_scores"
    cases = json.loads((inp / "cases.json").read_text())
    interpretations = {r["group"]: r for r in annotation["groups"]}
    results = []
    for case in cases:
        for view, (start, end) in enumerate(zip(case["start"], case["end"], strict=True)):
            a = np.asarray(rgb(inp / "originals" / start), dtype=np.int16)
            b = np.asarray(rgb(inp / "originals" / end), dtype=np.int16)
            assert a.shape == b.shape and a.ndim == 3 and a.shape[2] == 3
            absolute = np.abs(a - b)
            label = case["source_label"]
            if case["role"] == "constructed":
                state = interpretations[case["group"]]["initial_goal_state"]
                label = 0 if state == "visibly_unmet" else None
            results.append({"case": case["id"], "group": case["group"], "role": case["role"],
                            "source_row_1based": case["source_row_1based"], "source_label": case["source_label"],
                            "interpreted_label": label, "view_index": view, "shape": list(a.shape),
                            "rgb_equal": bool(np.array_equal(a, b)),
                            "byte_equal": digest(inp / "originals" / start) == digest(inp / "originals" / end),
                            "absolute_difference_sum": int(absolute.sum(dtype=np.int64)),
                            "rgb_element_count": int(a.size),
                            "mean_absolute_change": float(absolute.mean(dtype=np.float64) / 255)})
    with (out / "scores.jsonl").open("w") as stream:
        for result in results:
            stream.write(json.dumps(result, allow_nan=False) + "\n")
    comparison = []
    for group in interpretations:
        rows = [r for r in results if r["group"] == group]
        for view in range(3):
            mapped = {r["role"]: r for r in rows if r["view_index"] == view}
            if not mapped:
                continue
            f, s = mapped["source_failure"]["mean_absolute_change"], mapped["source_success"]["mean_absolute_change"]
            comparison.append({"group": group, "view_index": view, "failure_change": f,
                               "success_change": s, "failure_minus_success": f - s})
    dump(out / "summary.json", {"cases": len(cases), "rows": len(results), "comparison": comparison,
                                 "annotations_sha256": digest(args.annotations),
                                 "cases_sha256": digest(inp / "cases.json"),
                                 "observe_source_sha256": digest(__file__), "device": "cpu",
                                 "seed": None, "performance_claim": None})
    print(json.dumps({"cases": len(cases), "score_rows": len(results), "comparison": comparison}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare", "score"])
    parser.add_argument("--selection", default="/study/selection.json")
    parser.add_argument("--metadata", default="/metadata/ur5_metadata.jsonl")
    parser.add_argument("--archive", default="/input/records.tar.gz")
    parser.add_argument("--prepared", default="/prepared")
    parser.add_argument("--annotations", default="/study/annotations.json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    {"prepare": prepare, "score": score}[args.mode](args)
