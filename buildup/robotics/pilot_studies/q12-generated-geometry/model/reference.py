"""CPU reference operators for a bounded diagnostic; CUDA parity is unverified."""
import ast
from pathlib import Path
from types import SimpleNamespace
import torch
from torch import nn
from construction import SourceTransform, UnavailableOperator


def fps(points, count):
    assert points.device.type == 'cpu' and points.dtype == torch.float32
    batch, size, dims = points.shape
    assert dims == 3 and 0 < count <= size
    threads = min(512, 2 ** (size.bit_length() - 1))
    padded = ((size + threads - 1) // threads) * threads
    result = torch.zeros((batch, count), dtype=torch.int32)
    # Follow audited Pointnet2 start=0, mag>1e-3, temp=1e10 and
    # per-thread strict comparison / halving reduction tie precedence.
    for b in range(batch):
        xyz = points[b]
        eligible = (xyz[:, 0]**2 + xyz[:, 1]**2 + xyz[:, 2]**2) > 1e-3
        nearest = torch.full((size,), 1e10)
        old = 0
        for step in range(1, count):
            delta = xyz - xyz[old]
            distance = delta[:, 0]**2 + delta[:, 1]**2 + delta[:, 2]**2
            nearest = torch.where(eligible, torch.minimum(nearest, distance), nearest)
            candidates = torch.full((padded,), -1.)
            candidates[:size] = torch.where(eligible, nearest, -1.)
            values, blocks = candidates.reshape(-1, threads).max(dim=0)
            indices = blocks * threads + torch.arange(threads)
            indices = torch.where(values < 0, 0, indices)
            width = threads // 2
            while width:
                right = values[width:2*width] > values[:width]
                indices = torch.where(right, indices[width:2*width], indices[:width])
                values = torch.maximum(values[:width], values[width:2*width])
                width //= 2
            old = int(indices[0])
            result[b, step] = old
    return result


def gather(features, indices):
    return features.gather(2, indices.long().unsqueeze(1).expand(-1, features.shape[1], -1))


class KNN(nn.Module):
    def __init__(self, k, transpose_mode=False):
        super().__init__()
        assert not transpose_mode
        self.k = k

    def forward(self, reference, query):
        assert reference.device.type == query.device.type == 'cpu'
        assert reference.dtype == query.dtype == torch.float32
        assert reference.shape[1] == query.shape[1] == 3
        # Direct squared Euclidean distance; fixed dimension order and stable
        # lower-reference-index ties. Do not claim this reproduces CUDA rounding.
        distance = None
        for dim in range(3):
            term = (query[:, dim, :, None] - reference[:, dim, None, :])**2
            distance = term if distance is None else distance + term
        indices = torch.argsort(distance, dim=-1, stable=True)[..., :self.k]
        values = distance.gather(-1, indices).sqrt()
        return values.transpose(1, 2).contiguous(), indices.transpose(1, 2).contiguous()


def construct(config):
    base = Path(__file__).parent / 'upstream'
    common = dict(torch=torch, nn=nn, KNN=KNN,
                  pointnet2_utils=SimpleNamespace(furthest_point_sample=fps, gather_operation=gather),
                  ChamferDistanceL1=UnavailableOperator, ChamferDistanceL2=UnavailableOperator,
                  DropPath=UnavailableOperator, trunc_normal_=nn.init.trunc_normal_)
    scopes, receipts = {}, []
    for name, allocations, decorators in [('dgcnn_group.py', 0, 0), ('SGrasp.py', 1, 1)]:
        path = base / name
        transform = SourceTransform()
        tree = transform.visit(ast.parse(path.read_text()))
        ast.fix_missing_locations(tree)
        assert (transform.cpu_allocations, transform.decorators) == (allocations, decorators)
        scope = dict(common)
        if name == 'SGrasp.py':
            scope['DGCNN_Grouper'] = scopes['dgcnn_group.py']['DGCNN_Grouper']
        exec(compile(tree, str(path), 'exec'), scope)
        scopes[name] = scope
        receipts.append(dict(file=name, removed_imports=transform.imports,
                             cpu_allocations=allocations, registry_decorators=decorators))
    return scopes['SGrasp.py']['SGrasp'](SimpleNamespace(**config)).cpu().eval(), receipts
