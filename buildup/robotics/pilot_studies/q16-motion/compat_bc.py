"""Small same-observation imitation route for source-matched PushT, Docker only."""
import argparse
import hashlib
import json
from pathlib import Path
import time

import h5py
import numpy as np
import torch
from torch import nn

from compat_env import make_env, native_metric, observe

ROOT = Path('/output')
H5 = Path('/demos/trajectory.none.pd_ee_delta_pos.physx_cuda.h5')
META = H5.with_suffix('.json')
PPO = Path('/demos/ppo_pd_ee_delta_pos_ckpt.pt')
SOURCE = 'baab60ede2e89167c1b7aaed41a9aa8e690a9d1e'
DEV = 8
TRAIN = 64
VALID = 8
SEEDS = tuple(range(47000, 47008))


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def restore(env, group, frame):
    states = group['env_states']
    payload = {
        category: {name: torch.as_tensor(states[category][name][frame],
                                         dtype=torch.float32, device=env.unwrapped.device).unsqueeze(0)
                   for name in states[category]}
        for category in ('actors', 'articulations')
    }
    env.unwrapped.set_state_dict(payload)


def extract(attempt, train_count, valid_count):
    out = ROOT / attempt
    out.mkdir(exist_ok=True)
    meta = json.loads(META.read_text())
    assert meta['commit_info']['commit_id'] == SOURCE
    assert meta['env_info']['env_kwargs']['obs_mode'] == 'state'
    assert meta['env_info']['env_kwargs']['control_mode'] == 'pd_ee_delta_pos'
    episodes = meta['episodes'][DEV:DEV+train_count+valid_count]
    assert len(episodes) == train_count+valid_count
    assert len(set(x['episode_seed'] for x in episodes)) == len(episodes)
    env = make_env('push_t', device='gpu', obs_mode='state', native=True)
    split = {'train': [], 'valid': []}
    payload = {}
    started = time.perf_counter()
    try:
        with h5py.File(H5, 'r') as h5:
            for index, item in enumerate(episodes):
                group = h5[f"traj_{item['episode_id']}"]
                actions = np.asarray(group['actions'], np.float32)
                env.reset(seed=item['episode_seed'])
                observations = []
                for frame in range(len(actions)):
                    restore(env, group, frame)
                    observations.append(env.unwrapped.get_obs().detach().cpu().numpy().reshape(-1))
                observations = np.asarray(observations, np.float32)
                assert observations.shape == (len(actions), 31) and actions.shape[1] == 3
                assert np.isfinite(observations).all() and np.isfinite(actions).all()
                states = group['env_states']
                articulation = np.asarray(states['articulations']['panda_stick'][:len(actions)], np.float32)
                tee = np.asarray(states['actors']['Tee'][:len(actions), :7], np.float32)
                goal = np.asarray(states['actors']['goal_Tee'][:len(actions), :3], np.float32)
                assert np.allclose(observations[:, :7], articulation[:, 13:20], atol=1e-4)
                assert np.allclose(observations[:, 7:14], articulation[:, 20:27], atol=1e-4)
                assert np.allclose(observations[:, -10:-7], goal, atol=1e-4)
                assert np.allclose(observations[:, -7:], tee, atol=1e-4)
                partition = 'train' if index < train_count else 'valid'
                split[partition].append(dict(episode_id=item['episode_id'], seed=item['episode_seed'],
                                             rows=len(actions)))
                payload.setdefault(partition + '_obs', []).append(observations)
                payload.setdefault(partition + '_act', []).append(actions)
                if (index + 1) % 8 == 0:
                    print(json.dumps(dict(processed=index+1, elapsed_s=round(time.perf_counter()-started, 1))), flush=True)
    finally:
        env.close()
    arrays = {key: np.concatenate(values, axis=0) for key, values in payload.items()}
    file = out / 'dataset.npz'
    np.savez_compressed(file, **arrays)
    save_json(out / 'extraction.json', dict(status='completed', source_commit=SOURCE,
                                            source_h5_sha256=digest(H5),
                                            checkpoint_sha256=digest(PPO),
                                            observation_dim=31, action_dim=3,
                                            train_episodes=train_count, valid_episodes=valid_count,
                                            dev_episodes=[x['episode_id'] for x in meta['episodes'][:DEV]],
                                            split=split,
                                            rows={key: len(arrays[key + '_obs']) for key in split},
                                            dataset='dataset.npz', dataset_sha256=digest(file),
                                            elapsed_s=time.perf_counter()-started))


class BC(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(31, 128), nn.Tanh(),
                                 nn.Linear(128, 128), nn.Tanh(),
                                 nn.Linear(128, 3), nn.Tanh())

    def forward(self, x):
        return self.net(x)


def fit(attempt, data_attempt):
    out = ROOT / attempt
    out.mkdir(exist_ok=True)
    source = ROOT / data_attempt
    manifest = json.loads((source / 'extraction.json').read_text())
    assert manifest['status'] == 'completed'
    assert len(manifest['split']['train']) == manifest['train_episodes']
    assert len(manifest['split']['valid']) == manifest['valid_episodes']
    assert digest(source / manifest['dataset']) == manifest['dataset_sha256']
    with np.load(source / manifest['dataset'], allow_pickle=False) as data:
        train_x = torch.as_tensor(data['train_obs'], device='cuda')
        train_y = torch.as_tensor(data['train_act'], device='cuda')
        valid_x = torch.as_tensor(data['valid_obs'], device='cuda')
        valid_y = torch.as_tensor(data['valid_act'], device='cuda')
    torch.manual_seed(16025)
    torch.cuda.manual_seed_all(16025)
    mean = train_x.mean(0)
    scale = train_x.std(0).clamp_min(1e-3)
    train_x = (train_x - mean) / scale
    valid_x = (valid_x - mean) / scale
    model = BC().cuda()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    generator = torch.Generator(device='cuda').manual_seed(16025)
    best = float('inf')
    history = []
    started = time.perf_counter()
    for epoch in range(1, 61):
        model.train()
        order = torch.randperm(len(train_x), generator=generator, device='cuda')
        for batch in order.split(256):
            loss = ((model(train_x[batch]) - train_y[batch]) ** 2).mean()
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
        model.eval()
        with torch.no_grad():
            train_loss = float(((model(train_x) - train_y) ** 2).mean().item())
            valid_loss = float(((model(valid_x) - valid_y) ** 2).mean().item())
        history.append(dict(epoch=epoch, train_mse=train_loss, valid_mse=valid_loss))
        if valid_loss < best:
            best = valid_loss
            best_epoch = epoch
            torch.save(dict(model=model.state_dict(), mean=mean.cpu(), scale=scale.cpu(),
                            source_data_sha256=manifest['dataset_sha256'], epoch=epoch), out / 'bc.pt')
        if epoch % 10 == 0:
            print(json.dumps(history[-1]), flush=True)
    save_json(out / 'fit.json', dict(status='completed', source_data=data_attempt,
                                     data_sha256=manifest['dataset_sha256'],
                                     train_episodes=manifest['train_episodes'],
                                     valid_episodes=manifest['valid_episodes'],
                                     train_rows=len(train_x), valid_rows=len(valid_x),
                                     policy='31-128-128-3 tanh MLP, normalized state, MSE',
                                     seed=16025, epochs=60, batch_size=256,
                                     best_epoch=best_epoch, best_valid_mse=best,
                                     checkpoint='bc.pt', checkpoint_sha256=digest(out / 'bc.pt'),
                                     history=history, elapsed_s=time.perf_counter()-started))


def load_ppo():
    weights = torch.load(PPO, map_location='cpu', weights_only=True)
    actor = nn.Sequential(nn.Linear(31, 256), nn.Tanh(),
                          nn.Linear(256, 256), nn.Tanh(),
                          nn.Linear(256, 256), nn.Tanh(),
                          nn.Linear(256, 3)).cuda()
    actor.load_state_dict({key.removeprefix('actor_mean.'): value
                           for key, value in weights.items() if key.startswith('actor_mean.')})
    actor.eval()
    return actor


def evaluate(attempt, fit_attempt, seeds):
    out = ROOT / attempt
    out.mkdir(exist_ok=True)
    fit_dir = ROOT / fit_attempt
    fit_meta = json.loads((fit_dir / 'fit.json').read_text())
    assert digest(fit_dir / 'bc.pt') == fit_meta['checkpoint_sha256']
    checkpoint = torch.load(fit_dir / 'bc.pt', map_location='cpu', weights_only=True)
    bc = BC().cuda()
    bc.load_state_dict(checkpoint['model'])
    bc.eval()
    mean = checkpoint['mean'].cuda()
    scale = checkpoint['scale'].cuda()
    ppo = load_ppo()
    demo_seeds = {item['episode_seed'] for item in json.loads(META.read_text())['episodes']}
    assert not demo_seeds.intersection(seeds)
    rows = []
    started = time.perf_counter()
    env = make_env('push_t', device='gpu', obs_mode='state', native=True)
    try:
        for seed in seeds:
            initials = []
            for route in ('zero', 'ppo_mean', 'bc'):
                obs, _ = env.reset(seed=seed)
                initial = observe(env, 'push_t')
                initials.append(np.concatenate((initial['object'], initial['goal'], initial['qpos'])))
                trajectory = [initial['object']]
                metrics = [native_metric(env, 'push_t')[0]]
                successes = []
                actions = []
                with torch.no_grad():
                    for step in range(100):
                        if route == 'zero':
                            action = np.zeros(3, np.float32)
                        elif route == 'ppo_mean':
                            action = ppo(obs).detach().cpu().numpy().reshape(-1)
                        else:
                            action = bc((obs - mean) / scale).detach().cpu().numpy().reshape(-1)
                        obs, _, terminated, truncated, _ = env.step(action)
                        metric, success = native_metric(env, 'push_t')
                        trajectory.append(observe(env, 'push_t')['object'])
                        metrics.append(metric)
                        successes.append(success)
                        actions.append(action)
                        if bool(torch.as_tensor(terminated).any()) or bool(torch.as_tensor(truncated).any()):
                            break
                trace = out / f'{route}_{seed}.npz'
                np.savez_compressed(trace, object=np.asarray(trajectory),
                                    metric=np.asarray(metrics, np.float32),
                                    success=np.asarray(successes, bool),
                                    action=np.asarray(actions, np.float32), initial=initials[-1])
                row = dict(seed=seed, route=route, steps=len(actions),
                           final_success=bool(successes[-1]), any_success=bool(any(successes)),
                           final_metric=float(metrics[-1]), max_metric=float(max(metrics)),
                           trace=trace.name, sha256=digest(trace))
                rows.append(row)
                print(json.dumps(row), flush=True)
            assert all(np.allclose(initials[0], value, atol=1e-5) for value in initials[1:])
    finally:
        env.close()
    save_json(out / 'evaluation.json', dict(status='completed', native_task='PushT-v1',
                                            source_commit=SOURCE, backend='physx_cuda',
                                            observation_mode='state', control_mode='pd_ee_delta_pos',
                                            seeds=seeds, fit=fit_attempt,
                                            bc_checkpoint_sha256=fit_meta['checkpoint_sha256'],
                                            ppo_checkpoint_sha256=digest(PPO),
                                            rows=rows, elapsed_s=time.perf_counter()-started))


def verify(attempt, evaluation_attempt):
    out = ROOT / attempt
    out.mkdir(exist_ok=True)
    source = ROOT / evaluation_attempt
    manifest = json.loads((source / 'evaluation.json').read_text())
    assert manifest['status'] == 'completed' and len(manifest['rows']) == 3*len(manifest['seeds'])
    counts = {}
    for row in manifest['rows']:
        path = source / row['trace']
        assert digest(path) == row['sha256']
        with np.load(path, allow_pickle=False) as data:
            n = row['steps']
            assert data['object'].shape == (n+1, 7)
            assert data['metric'].shape == (n+1,)
            assert data['action'].shape == (n, 3)
            assert data['success'].shape == (n,)
            assert np.isfinite(data['object']).all() and np.isfinite(data['metric']).all()
            assert np.isfinite(data['action']).all()
            assert np.array_equal(data['success'], data['metric'][1:] >= .90)
            assert bool(data['success'][-1]) == row['final_success']
            assert abs(float(data['metric'][-1]) - row['final_metric']) < 1e-5
            counts.setdefault(row['route'], []).append(row['final_success'])
    for seed in manifest['seeds']:
        group = [r for r in manifest['rows'] if r['seed'] == seed]
        assert {r['route'] for r in group} == {'zero', 'ppo_mean', 'bc'}
        with np.load(source / group[0]['trace']) as ref:
            initial = ref['initial'].copy()
        for row in group[1:]:
            with np.load(source / row['trace']) as data:
                assert np.allclose(initial, data['initial'], atol=1e-5)
    summary = dict(status='passed', episodes=len(manifest['rows']), traces=len(manifest['rows']),
                   final_success={key: sum(values) for key, values in counts.items()},
                   mean_final_metric={key: float(np.mean([r['final_metric'] for r in manifest['rows']
                                                           if r['route'] == key])) for key in counts},
                   evaluation=evaluation_attempt)
    save_json(out / 'verification.json', summary)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=('extract', 'fit', 'evaluate', 'validate'))
    parser.add_argument('--attempt', required=True)
    parser.add_argument('--data', default='data1')
    parser.add_argument('--fit', default='fit1')
    parser.add_argument('--evaluation', default='eval1')
    parser.add_argument('--train-episodes', type=int, default=TRAIN)
    parser.add_argument('--valid-episodes', type=int, default=VALID)
    parser.add_argument('--seed-start', type=int, default=SEEDS[0])
    parser.add_argument('--seed-count', type=int, default=len(SEEDS))
    args = parser.parse_args()
    {'extract': lambda: extract(args.attempt, args.train_episodes, args.valid_episodes),
     'fit': lambda: fit(args.attempt, args.data),
     'evaluate': lambda: evaluate(args.attempt, args.fit,
                                  tuple(range(args.seed_start, args.seed_start+args.seed_count))),
     'validate': lambda: verify(args.attempt, args.evaluation)}[args.stage]()
