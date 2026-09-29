"""Create a visual review index for saved policy-request RGB frames, in Docker."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    case_dirs = sorted(args.cases.glob("seed_*"))
    if (args.cases / "requests.jsonl").exists():
        case_dirs.insert(0, args.cases)
    for seed_dir in case_dirs:
        requests = seed_dir / "requests.jsonl"
        if not requests.exists():
            continue
        frames = []
        for line in requests.read_text().splitlines():
            item = json.loads(line)
            image_record = item["request"]["image_history"][-1]
            saved = Path(image_record["path"]).name
            path = seed_dir / "request_images" / saved
            if path.exists():
                frames.append((item["env_step"], path))
        if not frames:
            continue
        tile_w, tile_h, cols = 224, 250, 5
        rows = (len(frames) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * tile_w, rows * tile_h), "white")
        draw = ImageDraw.Draw(sheet)
        for index, (step, path) in enumerate(frames):
            x = (index % cols) * tile_w
            y = (index // cols) * tile_h
            with Image.open(path) as image:
                sheet.paste(image.convert("RGB"), (x, y + 20))
            draw.text((x + 4, y + 3), f"step {step}", fill="black")
        sheet.save(args.output / f"{seed_dir.name}_requests.png")
        print(json.dumps({"seed": seed_dir.name, "frames": len(frames)}), flush=True)


if __name__ == "__main__":
    main()
