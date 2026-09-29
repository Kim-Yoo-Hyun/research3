"""Sequence-conditioned object and TCP trajectory prediction from real action windows."""
from pathlib import Path
import numpy as np
import torch
from diffusion import STEPS


class WorldNet(torch.nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.net = torch.nn.Sequential(torch.nn.Linear(input_dim, 256), torch.nn.SiLU(),
                                       torch.nn.Linear(256, 256), torch.nn.SiLU(),
                                       torch.nn.Linear(256, STEPS * 6))

    def forward(self, x):
        return self.net(x).reshape(-1, STEPS, 6)


def windows(episodes):
    inputs, targets = [], []
    for episode in episodes:
        states, actions = episode['state'], episode['action']
        for t in range(len(actions) - STEPS + 1):
            previous = states[max(0, t - 1)]
            current = states[t]
            prior_action = actions[max(0, t - 1)]
            sequence = actions[t:t + STEPS]
            future = states[t + 1:t + STEPS + 1]
            positions = np.concatenate([future[:, :3] - current[:3],
                                        future[:, 13:16] - current[13:16]], 1)
            inputs.append(np.concatenate([previous, current, prior_action, sequence.reshape(-1)]))
            targets.append(positions)
    return np.asarray(inputs, np.float32), np.asarray(targets, np.float32)


def fit(train, val, output):
    torch.manual_seed(160232)
    x, y = windows(train)
    vx, vy = windows(val)
    mean = x.mean(0)
    std = np.maximum(x.std(0), 0.01)
    yscale = np.maximum(y.std((0, 1)), 0.01)
    tx = torch.from_numpy(np.clip((x - mean) / std, -8, 8))
    ty = torch.from_numpy(y / yscale)
    tvx = torch.from_numpy(np.clip((vx - mean) / std, -8, 8))
    tvy = torch.from_numpy(vy / yscale)
    net = WorldNet(tx.shape[1])
    optimizer = torch.optim.AdamW(net.parameters(), lr=5e-4, weight_decay=1e-5)
    best = float('inf')
    best_epoch = 0
    best_weights = None
    curve = []
    for epoch in range(60):
        net.train()
        for batch in torch.randperm(len(tx)).split(256):
            loss = ((net(tx[batch]) - ty[batch]) ** 2).mean()
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        net.eval()
        with torch.no_grad():
            total = 0.0
            for batch in torch.arange(len(tvx)).split(512):
                total += float(((net(tvx[batch]) - tvy[batch]) ** 2).mean()) * len(batch)
            value = total / len(tvx)
        curve.append(value)
        if value < best:
            best = value
            best_epoch = epoch + 1
            best_weights = {k: v.detach().clone() for k, v in net.state_dict().items()}
        if (epoch + 1) % 10 == 0:
            print('dynamics epoch', epoch + 1, 'val_mse', value, flush=True)
    torch.save(dict(weights=best_weights, mean=mean, std=std, yscale=yscale,
                    best_epoch=best_epoch, fit_seed=160232), Path(output) / 'world.pt')
    model = World(Path(output) / 'world.pt')
    prediction = model.predict(vx)
    object_rmse = float(np.sqrt(np.mean(np.sum((prediction[:, :, :3] - vy[:, :, :3]) ** 2, 2))))
    tcp_rmse = float(np.sqrt(np.mean(np.sum((prediction[:, :, 3:] - vy[:, :, 3:]) ** 2, 2))))
    return dict(train_windows=len(tx), val_windows=len(tvx), parameters=sum(p.numel() for p in net.parameters()),
                best_epoch=best_epoch, val_mse=best, val_object_rmse_m=object_rmse,
                val_tcp_rmse_m=tcp_rmse, curve=curve)


class World:
    def __init__(self, path):
        checkpoint = torch.load(path, map_location='cpu', weights_only=False)
        self.mean = checkpoint['mean']
        self.std = checkpoint['std']
        self.yscale = checkpoint['yscale']
        self.net = WorldNet(len(self.mean))
        self.net.load_state_dict(checkpoint['weights'])
        self.net.eval()

    def predict(self, x):
        with torch.no_grad():
            normalized = torch.from_numpy(np.clip((x - self.mean) / self.std, -8, 8)).float()
            return self.net(normalized).numpy() * self.yscale

    def forecast(self, previous, current, prior_action, candidate_chunks):
        n = len(candidate_chunks)
        base = np.tile(np.concatenate([previous, current, prior_action]), (n, 1))
        x = np.concatenate([base, candidate_chunks.reshape(n, -1)], 1).astype(np.float32)
        relative = self.predict(x)
        return relative + np.concatenate([current[:3], current[13:16]])[None, None, :]
