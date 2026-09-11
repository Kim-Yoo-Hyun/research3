"""Frozen four-input CPU reference diagnostic; never mounts or reads GT."""
import argparse
import json
import time
from pathlib import Path
import numpy as np
import torch
from reference import construct, fps
from schema import sha, choose, schema


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repeat', type=int, choices=[0,1], required=True)
    parser.add_argument('--base', type=Path, default=Path(__file__).parent)
    parser.add_argument('--checkpoint', type=Path, default=Path('/checkpoint/model.pth'))
    parser.add_argument('--inputs', type=Path, default=Path('/inputs'))
    parser.add_argument('--output', type=Path, default=Path('/output'))
    args = parser.parse_args()
    base = args.base
    frozen = json.loads((base/'completion_freeze.json').read_text())
    for name, digest in frozen['files'].items():
        assert sha(base/name) == digest, name
    protocol = json.loads((base/'completion_protocol.json').read_text())
    manifest = json.loads((base/'completion_inputs.json').read_text())
    checkpoint = args.checkpoint
    assert sha(checkpoint) == protocol['checkpoint_sha256']
    torch.set_num_threads(protocol['cpus'])
    torch.manual_seed(protocol['seed'])
    torch.use_deterministic_algorithms(True)
    model, adapters = construct(protocol['model_config'])
    root, state, prefix = choose(torch.load(checkpoint, map_location='cpu', weights_only=True), ['base_model'])
    assert schema(state) == schema(model.state_dict())
    model.load_state_dict(state, strict=True)
    assert all(torch.equal(v, state[k]) for k,v in model.state_dict().items())
    out = args.output / str(args.repeat)
    out.mkdir(exist_ok=False)
    result = dict(repeat=args.repeat, device='cpu', torch=torch.__version__,
                  checkpoint_sha256=sha(checkpoint), protocol_sha256=sha(base/'completion_protocol.json'),
                  freeze_sha256=sha(base/'completion_freeze.json'), root=root, prefix_removed=prefix,
                  strict_load=True, gt_mounted=False, native_parity=False, adapters=adapters, pairs=[])
    with torch.inference_mode():
        for item in manifest['pairs']:
            row = dict(index=item['index'])
            start = time.monotonic()
            try:
                path = args.inputs / item['sampled_file']
                assert sha(path) == item['sampled_sha256']
                sampled = np.loadtxt(path, dtype=np.float64)
                assert sampled.shape == (2048,3) and np.isfinite(sampled).all()
                center = sampled.mean(0)
                radius = np.linalg.norm(sampled-center, axis=1).max()
                assert np.isfinite(radius) and radius > 0
                xyz = torch.from_numpy(((sampled-center)/radius).astype(np.float32))[None]
                sparse, dense = model(xyz)
                source_indices = fps(xyz, 96).numpy()[0]
                assert sparse.shape == (1,192,3) and dense.shape == (1,8192,3)
                assert torch.isfinite(sparse).all() and torch.isfinite(dense).all()
                assert torch.equal(dense[:,6144:], xyz)
                assert torch.equal(sparse[:,96:], xyz[:,source_indices.astype(np.int64)])
                filename = f"{item['index']}.npz"
                np.savez(out/filename, sparse=sparse.numpy()[0], dense=dense.numpy()[0],
                         input=xyz.numpy()[0], centroid=center, radius=radius,
                         sparse_input_indices=source_indices)
                row.update(status='pass', file=filename, sha256=sha(out/filename))
            except Exception as error:
                row.update(status='fail', error=str(error))
            row['elapsed_seconds'] = round(time.monotonic()-start,3)
            result['pairs'].append(row)
    result['decision'] = ('REFERENCE_OUTPUT_CONTROLS_PASS' if all(x['status']=='pass' for x in result['pairs'])
                          else 'REFINE_REFERENCE_OUTPUT')
    (out/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    assert sum(p.stat().st_size for p in args.output.rglob('*') if p.is_file()) <= protocol['output_cap_mib']*1024**2
    print(json.dumps(dict(repeat=args.repeat, decision=result['decision'], pairs=result['pairs'])))


if __name__ == '__main__':
    main()
