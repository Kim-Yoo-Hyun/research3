"""Independent NumPy output audit; no torch, checkpoint, or learned model imports."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', type=Path, default=Path(__file__).parent)
    parser.add_argument('--inputs', type=Path, default=Path('/inputs'))
    parser.add_argument('--predictions', type=Path, default=Path('/predictions'))
    parser.add_argument('--gt', type=Path, default=Path('/gt'))
    parser.add_argument('--output', type=Path, default=Path('/verification/verification.json'))
    args = parser.parse_args()
    base = args.base
    frozen = json.loads((base/'completion_freeze.json').read_text())
    for name, digest in frozen['files'].items():
        assert sha(base/name) == digest, name
    protocol = json.loads((base/'completion_protocol.json').read_text())
    manifest = json.loads((base/'completion_inputs.json').read_text())
    receipts = [json.loads((args.predictions/str(i)/'result.json').read_text()) for i in range(2)]
    for i,r in enumerate(receipts):
        assert r['repeat'] == i and r['device'] == 'cpu' and r['strict_load']
        assert r['protocol_sha256'] == sha(base/'completion_protocol.json')
        assert r['freeze_sha256'] == sha(base/'completion_freeze.json')
        assert r['checkpoint_sha256'] == protocol['checkpoint_sha256']
        assert [p['index'] for p in r['pairs']] == [0,1,2,3]
    rows = []
    for item in manifest['pairs']:
        idx = item['index']
        row = dict(index=idx)
        try:
            if any(r['pairs'][idx]['status'] != 'pass' for r in receipts):
                raise ValueError('A recorded inference failed; retain this case in denominator')
            path = args.inputs/item['sampled_file']
            assert sha(path) == item['sampled_sha256']
            sampled = np.loadtxt(path, dtype=np.float64)
            center = sampled.mean(0)
            radius = np.sqrt(np.sum((sampled-center)**2, axis=1)).max()
            expected = ((sampled-center)/radius).astype(np.float32)
            arrays = []
            for repeat in range(2):
                file = args.predictions/str(repeat)/f'{idx}.npz'
                assert sha(file) == receipts[repeat]['pairs'][idx]['sha256']
                with np.load(file, allow_pickle=False) as z:
                    arrays.append({k:z[k] for k in z.files})
            first, second = arrays
            assert set(first) == set(second) == {'sparse','dense','input','centroid','radius','sparse_input_indices'}
            assert all(np.array_equal(first[k],second[k]) for k in first)
            assert np.array_equal(first['input'], expected)
            assert np.array_equal(first['centroid'], center) and first['radius'] == radius
            assert first['sparse'].shape == (192,3) and first['dense'].shape == (8192,3)
            assert first['sparse'].dtype == first['dense'].dtype == np.float32
            assert all(np.isfinite(v).all() for v in first.values())
            assert np.array_equal(first['dense'][6144:],expected)
            inverse_error = float(np.abs(first['dense'][6144:].astype(np.float64)*radius+center-sampled).max()
                                  / max(float(radius), float(np.abs(sampled).max()), 1.))
            assert inverse_error <= protocol['inverse_tolerance']
            indices = first['sparse_input_indices']
            assert indices.shape == (96,) and indices.dtype == np.int32
            assert ((indices>=0)&(indices<2048)).all() and indices[0] == 0
            assert np.array_equal(first['sparse'][96:], expected[indices])
            gt_path = args.gt/item['gt_file']
            assert sha(gt_path) == item['gt_sha256']
            gt = np.loadtxt(gt_path, dtype=np.float64)
            assert gt.shape == (8192,3) and np.isfinite(gt).all()
            generated = first['dense'][:6144]
            source_set = set(map(tuple,expected))
            # These are descriptive provenance counts, without quality thresholds.
            row.update(status='pass', repeat_array_exact=True, copied_suffix_exact=True,
                       copied_inverse_scaled_max_error=inverse_error,
                       generated_points=6144, generated_unique_points=len(np.unique(generated,axis=0)),
                       generated_exact_input_coincidences=sum(tuple(p) in source_set for p in generated),
                       gt_rows=8192, gt_unique_points=len(np.unique(gt,axis=0)),
                       gt_sampling='all supplied rows retained; no FPS/dedup replacement',
                       metric_frame='partial-derived normalized; physical units/camera unverified')
        except Exception as error:
            row.update(status='fail', error=str(error))
        rows.append(row)
    result = dict(protocol_sha256=sha(base/'completion_protocol.json'), pairs=rows,
                  independent_model_forward_verification=False,
                  native_cuda_parity=False, physical_frame_verified=False,
                  decision=('REFERENCE_OUTPUT_VERIFIED_NATIVE_AND_PHYSICAL_UNRESOLVED'
                            if all(r['status']=='pass' for r in rows) else 'REFINE_REFERENCE_OUTPUT'))
    out = args.output
    assert not out.exists()
    out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
