"""Small state-conditioned denoising diffusion policy for eight real robot actions."""
from pathlib import Path
import math
import numpy as np
import torch

STEPS = 8
ACTION_DIM = 4
TRAIN_TIMESTEPS = 16
ACTION_SCALE = np.array([0.25, 0.25, 0.25, 1.0], np.float32)


class Denoiser(torch.nn.Module):
    def __init__(self, observation_dim):
        super().__init__()
        dim = observation_dim + STEPS * ACTION_DIM + 16
        self.net = torch.nn.Sequential(torch.nn.Linear(dim, 256), torch.nn.SiLU(),
                                       torch.nn.Linear(256, 256), torch.nn.SiLU(),
                                       torch.nn.Linear(256, STEPS * ACTION_DIM))
        self.anchor_net = torch.nn.Sequential(torch.nn.Linear(observation_dim, 256), torch.nn.SiLU(),
                                              torch.nn.Linear(256, 256), torch.nn.SiLU(),
                                              torch.nn.Linear(256, STEPS * ACTION_DIM))

    def forward(self, noisy, observation, t):
        half = torch.arange(8, device=t.device, dtype=torch.float32)
        frequencies = torch.exp(-math.log(10000) * half / 7)
        angles = t.float()[:, None] * frequencies[None, :]
        time_embedding = torch.cat([angles.sin(), angles.cos()], 1)
        x = torch.cat([noisy.flatten(1), observation, time_embedding], 1)
        return self.net(x).reshape(-1, STEPS, ACTION_DIM)

    def anchor(self, observation):
        return self.anchor_net(observation).reshape(-1, STEPS, ACTION_DIM)


def schedule():
    # End near Gaussian noise so sampling from N(0, I) matches the training process.
    beta = torch.linspace(0.002, 0.30, TRAIN_TIMESTEPS)
    alpha = 1.0 - beta
    return alpha, torch.cumprod(alpha, 0)


def windows(episodes):
    observations, chunks = [], []
    for episode in episodes:
        states = episode['state']
        actions = episode['action']
        for t in range(len(actions) - STEPS + 1):
            observations.append(np.concatenate([states[max(t - 1, 0)], states[t]]))
            chunks.append(actions[t:t + STEPS])
    return np.asarray(observations, np.float32), np.asarray(chunks, np.float32)


def fit(episodes_train, episodes_val, output):
    torch.manual_seed(160231)
    observations, actions = windows(episodes_train)
    validation, val_actions = windows(episodes_val)
    mean = observations.mean(0)
    std = np.maximum(observations.std(0), 0.01)
    train_x = torch.from_numpy(np.clip((observations - mean) / std, -8, 8))
    val_x = torch.from_numpy(np.clip((validation - mean) / std, -8, 8))
    train_y = torch.from_numpy(np.clip(actions / ACTION_SCALE, -1, 1))
    val_y = torch.from_numpy(np.clip(val_actions / ACTION_SCALE, -1, 1))
    net = Denoiser(train_x.shape[1])
    optimizer = torch.optim.AdamW(net.parameters(), lr=3e-4, weight_decay=1e-5)
    _, abar = schedule()
    best = float('inf')
    best_epoch = 0
    best_weights = None
    curve = []
    for epoch in range(60):
        net.train()
        order = torch.randperm(len(train_x))
        for batch in order.split(256):
            t = torch.randint(0, TRAIN_TIMESTEPS, (len(batch),))
            noise = torch.randn_like(train_y[batch])
            noisy = abar[t, None, None].sqrt() * train_y[batch] + (1 - abar[t, None, None]).sqrt() * noise
            noise_loss = ((net(noisy, train_x[batch], t) - noise) ** 2).mean()
            behavior = net.anchor(train_x[batch])
            behavior_loss = ((behavior[:, :, :3] - train_y[batch, :, :3]) ** 2).mean() \
                + 2 * ((behavior[:, :, 3] - train_y[batch, :, 3]) ** 2).mean()
            loss = noise_loss + 2 * behavior_loss
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        net.eval()
        with torch.no_grad():
            generator = torch.Generator().manual_seed(9000)
            total = 0.0
            anchor_total = 0.0
            for batch in torch.arange(len(val_x)).split(512):
                t = torch.randint(0, TRAIN_TIMESTEPS, (len(batch),), generator=generator)
                noise = torch.randn(val_y[batch].shape, generator=generator)
                noisy = abar[t, None, None].sqrt() * val_y[batch] + (1 - abar[t, None, None]).sqrt() * noise
                total += float(((net(noisy, val_x[batch], t) - noise) ** 2).mean()) * len(batch)
                anchor = net.anchor(val_x[batch])
                anchor_total += float(((anchor[:, :, :3] - val_y[batch, :, :3]) ** 2).mean()
                                      + 2 * ((anchor[:, :, 3] - val_y[batch, :, 3]) ** 2).mean()) * len(batch)
            value = total / len(val_x)
            anchor_value = anchor_total / len(val_x)
        score = value + anchor_value
        curve.append(dict(noise=value, behavior=anchor_value))
        if score < best:
            best = score
            best_epoch = epoch + 1
            best_weights = {k: v.detach().clone() for k, v in net.state_dict().items()}
        if (epoch + 1) % 10 == 0:
            print('policy epoch', epoch + 1, 'val_noise_mse', value,
                  'val_behavior_mse', anchor_value, flush=True)
    checkpoint = dict(weights=best_weights, mean=mean, std=std, steps=STEPS,
                      action_scale=ACTION_SCALE, train_timesteps=TRAIN_TIMESTEPS,
                      fit_seed=160231, best_epoch=best_epoch, val_combined_loss=best)
    torch.save(checkpoint, Path(output) / 'policy.pt')
    return dict(train_windows=len(train_x), val_windows=len(val_x), parameters=sum(p.numel() for p in net.parameters()),
                best_epoch=best_epoch, val_combined_loss=best,
                val_noise_mse=curve[best_epoch - 1]['noise'],
                val_behavior_mse=curve[best_epoch - 1]['behavior'], curve=curve)


class Policy:
    def __init__(self, path):
        checkpoint = torch.load(path, map_location='cpu', weights_only=False)
        self.mean = checkpoint['mean']
        self.std = checkpoint['std']
        self.net = Denoiser(len(self.mean))
        self.net.load_state_dict(checkpoint['weights'])
        self.net.eval()
        self.alpha, self.abar = schedule()

    def sample(self, previous, current, seed, anchor_only=False):
        observation = np.concatenate([previous, current])
        x = torch.from_numpy(np.clip((observation - self.mean) / self.std, -8, 8)[None, :])
        generator = torch.Generator().manual_seed(int(seed))
        noisy = torch.randn((1, STEPS, ACTION_DIM), generator=generator)
        with torch.no_grad():
            anchor = self.net.anchor(x).clamp(-1, 1)
            if anchor_only:
                action = anchor
            else:
                for i in reversed(range(TRAIN_TIMESTEPS)):
                    t = torch.tensor([i], dtype=torch.long)
                    epsilon = self.net(noisy, x, t)
                    estimate = (noisy - (1 - self.abar[i]).sqrt() * epsilon) / self.abar[i].sqrt()
                    estimate = estimate.clamp(-1, 1)
                    if i:
                        # Deterministic DDIM reverse step, with identical initial noise across routes.
                        noisy = self.abar[i - 1].sqrt() * estimate + (1 - self.abar[i - 1]).sqrt() * epsilon
                    else:
                        noisy = estimate
                action = 0.75 * anchor + 0.25 * noisy
            action[:, :, 3] = torch.where(anchor[:, :, 3] >= 0, 1., -1.)
        return np.clip(action[0].numpy() * ACTION_SCALE, -ACTION_SCALE, ACTION_SCALE).astype(np.float32)
