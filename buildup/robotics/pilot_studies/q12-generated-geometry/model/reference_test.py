"""Docker-only synthetic operator and full-architecture readiness checks."""
import json
import time
from pathlib import Path
import numpy as np
import torch
from reference import fps, gather, KNN, construct


def scalar_fps(points, count):
    # Independent scalar traversal of the audited CUDA algorithm, including ties.
    size = len(points)
    threads = min(512, 2 ** (size.bit_length() - 1))
    nearest = np.full(size, np.float32(1e10))
    out = [0]
    for _ in range(1, count):
        winners = []
        for tid in range(threads):
            best, idx = -1., 0
            for i in range(tid, size, threads):
                x, y, z = points[i]
                if x*x + y*y + z*z <= np.float32(1e-3):
                    continue
                dx, dy, dz = points[i] - points[out[-1]]
                nearest[i] = min(nearest[i], dx*dx + dy*dy + dz*dz)
                if nearest[i] > best:
                    best, idx = nearest[i], i
            winners.append((best, idx))
        while len(winners) > 1:
            half = len(winners) // 2
            winners = [winners[i+half] if winners[i+half][0] > winners[i][0] else winners[i] for i in range(half)]
        out.append(winners[0][1])
    return np.array(out)


def main():
    torch.set_num_threads(4)
    torch.manual_seed(12020)
    torch.use_deterministic_algorithms(True)
    cases = [np.zeros((8, 3), dtype=np.float32),
             np.array([[0,0,0],[1,0,0],[0,1,0],[-1,0,0],[0,0,0.01],[0,-1,0],[1,0,0]], dtype=np.float32),
             np.random.RandomState(12020).normal(size=(521,3)).astype(np.float32)]
    for points in cases:
        count = min(18, len(points))
        actual = fps(torch.from_numpy(points)[None], count).numpy()[0]
        assert np.array_equal(actual, scalar_fps(points, count))
    points = torch.tensor([[[1., -1., 1., 0.], [0., 0., 0., 2.], [0., 0., 0., 0.]]])
    query = torch.zeros((1,3,1))
    distance, indices = KNN(4)(points, query)
    assert indices.flatten().tolist() == [0,1,2,3]
    assert distance.flatten().tolist() == [1.,1.,1.,2.]
    assert torch.equal(gather(points, torch.tensor([[2,0]], dtype=torch.int32)), points[:,:, [2,0]])
    # Full learned architecture, synthetic weights/input only; no checkpoint or XYZ mount.
    config = json.loads((Path(__file__).parent/'schema_protocol.json').read_text())['model_config']
    start = time.monotonic()
    model, _ = construct(config)
    xyz = torch.randn(1,2048,3)
    xyz = (xyz - xyz.mean(1, keepdim=True)) / 5
    with torch.inference_mode():
        sparse, dense = model(xyz)
        second = model(xyz)
    assert sparse.shape == (1,192,3) and dense.shape == (1,8192,3)
    assert torch.isfinite(sparse).all() and torch.isfinite(dense).all()
    assert torch.equal(dense[:,6144:], xyz)
    assert torch.equal(sparse[:,96:], gather(xyz.transpose(1,2), fps(xyz,96)).transpose(1,2))
    assert all(torch.equal(a,b) for a,b in zip((sparse,dense),second))
    receipt = dict(status='PASS_SYNTHETIC_REFERENCE_PREFLIGHT', fps_cases=3,
                   knn_tie_and_gather_checks=True, full_architecture_forwards=2,
                   checkpoint_mounted=False, real_xyz_mounted=False,
                   copied_suffix_exact=True, same_process_repeat_exact=True,
                   native_cuda_parity=False, elapsed_seconds=round(time.monotonic()-start,3))
    print(json.dumps(receipt))
    output = Path('/output')
    if output.is_dir():
        (output/'preflight.json').write_text(json.dumps(receipt,indent=2)+'\n')


if __name__ == '__main__':
    main()
