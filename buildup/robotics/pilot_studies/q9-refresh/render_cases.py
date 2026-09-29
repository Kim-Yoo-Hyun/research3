"""Render selected diagnostic RGB frames after inspecting the point trace."""
import io
import json
import sys
from pathlib import Path
import numpy as np
from inspect_input import CpuUnpickler
from observe import write_png

data = CpuUnpickler(io.BytesIO(Path('/input/env.pkl').read_bytes())).load()
rows = [json.loads(line) for line in Path('/results/trace.jsonl').read_text().splitlines()]
output = Path(sys.argv[1])
output.mkdir(parents=True, exist_ok=False)
for name, indices in [('metal bowl', [0, 17, 22]), ('orange', [2, 19])]:
    panels = []
    for idx in indices:
        rgb = data['rgb'][idx].cpu().numpy().copy()
        if np.nanmax(rgb) <= 1:
            rgb *= 255
        row = next(r for r in rows if r['query'] == name and r['array_index'] == idx)
        u, v = [int(round(x)) for x in row['uv']]
        # Outline keeps the inspected pixel visible.
        rgb[v-6:v+7, u-6] = [255, 0, 255]
        rgb[v-6:v+7, u+6] = [255, 0, 255]
        rgb[v-6, u-6:u+7] = [255, 0, 255]
        rgb[v+6, u-6:u+7] = [255, 0, 255]
        panels.append(rgb)
    write_png(output / (name.replace(' ', '_') + '.png'), np.concatenate(panels, axis=1))
print('Rendered metal bowl indices 0/17/22 and orange 2/19; post-observation diagnostics only.')
