"""Small episode-disjoint state BC and paired evaluation on public CPU PushT; Docker only."""
import hashlib
import json
from pathlib import Path
import sys

import gymnasium as gym
import gym_pusht  # noqa: F401
import numpy as np
import zarr

ROOT = Path('/output')
ZIP = ROOT / 'demos/pusht.zip'
FIT = ROOT / 'bc_fit1'
EVAL = ROOT / 'bc_eval1'
SEEDS = tuple(range(48000, 48016))


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def data_arrays():
    store = zarr.ZipStore(str(ZIP), mode='r')
    try:
        group = zarr.open_group(store=store, path='pusht/pusht_cchi_v7_replay.zarr', mode='r')
        states = np.asarray(group['data/state'][:], np.float64)
        actions = np.asarray(group['data/action'][:], np.float64)
        ends = np.asarray(group['meta/episode_ends'][:], np.int64)
    finally:
        store.close()
    assert states.shape == (25650, 5) and actions.shape == (25650, 2)
    assert ends.shape == (206,) and ends[-1] == len(states)
    assert np.all(np.diff(ends) > 0) and np.isfinite(states).all() and np.isfinite(actions).all()
    assert np.all((actions >= 0) & (actions <= 512))
    return states, actions, ends


def transform(state):
    state = np.asarray(state, np.float64)
    return np.concatenate((state[..., :4], np.sin(state[..., 4:5]),
                           np.cos(state[..., 4:5])), axis=-1)


def features(state, mean, std):
    z = (transform(state) - mean) / std
    z = z.reshape(-1, 6)
    quadratic = [z[:, i:i+1] * z[:, j:j+1] for i in range(6) for j in range(i, 6)]
    return np.concatenate((np.ones((len(z), 1)), z, *quadratic), axis=-1)


def fit():
    FIT.mkdir(exist_ok=False)
    states, actions, ends = data_arrays()
    train_stop, valid_stop = int(ends[159]), int(ends[179])
    train = states[:train_stop]
    valid = states[train_stop:valid_stop]
    mean = transform(train).mean(0)
    std = transform(train).std(0).clip(1e-3)
    train_x = features(train, mean, std)
    valid_x = features(valid, mean, std)
    train_y = actions[:train_stop] / 512.0
    valid_y = actions[train_stop:valid_stop] / 512.0
    choices = []
    best = None
    for alpha in (1.0, 100.0, 1000.0):
        penalty = np.eye(train_x.shape[1]) * alpha
        penalty[0, 0] = 0.0
        coef = np.linalg.solve(train_x.T @ train_x + penalty, train_x.T @ train_y)
        val_mse_px = float(np.mean((valid_x @ coef * 512.0 - actions[train_stop:valid_stop]) ** 2))
        choices.append(dict(alpha=alpha, validation_action_mse_px2=val_mse_px))
        if best is None or val_mse_px < best[0]:
            best = (val_mse_px, alpha, coef)
    checkpoint = FIT / 'ridge.npz'
    np.savez_compressed(checkpoint, mean=mean, std=std, coef=best[2], alpha=best[1])
    write(FIT / 'fit.json', dict(status='completed', source_zip_sha256=digest(ZIP),
                                 source_rows=len(states), source_episodes=len(ends),
                                 state_dim=5, action_dim=2, train_episode_ids=list(range(160)),
                                 validation_episode_ids=list(range(160, 180)),
                                 unused_episode_ids=list(range(180, 206)),
                                 train_rows=train_stop, validation_rows=valid_stop-train_stop,
                                 train_last_row=train_stop-1, validation_last_row=valid_stop-1,
                                 observation='agent XY, T XY, T angle; sin/cos angle features',
                                 action='absolute target XY, clipped to [0,512] at inference',
                                 policy='normalized degree-2 ridge behavioral cloning',
                                 choices=choices, selected_alpha=best[1],
                                 selected_validation_action_mse_px2=best[0],
                                 checkpoint=checkpoint.name, checkpoint_sha256=digest(checkpoint)))
    print(json.dumps(dict(train_rows=train_stop, valid_rows=valid_stop-train_stop,
                          selected_alpha=best[1], valid_mse_px2=best[0])), flush=True)


def action_from_model(state, mean, std, coef):
    value = (features(state, mean, std) @ coef * 512.0).reshape(2)
    return np.clip(value, 0, 512).astype(np.float32)


def full_state(env):
    e = env.unwrapped
    return np.asarray([*e.agent.position, *e.agent.velocity, *e.block.position,
                       *e.block.velocity, e.block.angle, e.block.angular_velocity], np.float64)


def rollout(seed, route, mean, std, coef):
    env = gym.make('gym_pusht/PushT-v0', obs_type='state', render_mode=None,
                   disable_env_checker=True)
    try:
        obs, _ = env.reset(seed=seed)
        obs = np.asarray(obs, np.float64)
        initial = full_state(env)
        initial_object = initial[4:6].copy()
        hold = obs[:2].copy().astype(np.float32)
        observations, full, coverage, contact, actions = [obs], [initial], [float(env.unwrapped._get_coverage())], [], []
        ever_success = False
        for _ in range(300):
            action = hold if route == 'hold' else action_from_model(obs, mean, std, coef)
            obs, _, terminated, truncated, info = env.step(action)
            obs = np.asarray(obs, np.float64)
            observations.append(obs)
            full.append(full_state(env))
            coverage.append(float(info['coverage']))
            contact.append(int(info['n_contacts']))
            actions.append(action)
            ever_success |= bool(info['is_success'])
            if terminated or truncated:
                break
        return dict(observation=np.asarray(observations), full=np.asarray(full),
                    coverage=np.asarray(coverage), contact=np.asarray(contact),
                    action=np.asarray(actions)), dict(seed=seed, route=route,
                    steps=len(actions), any_success=ever_success,
                    final_success=bool(coverage[-1] > .95),
                    final_coverage=float(coverage[-1]), max_coverage=float(max(coverage)),
                    any_contact=bool(any(contact)), contact_steps=int(np.sum(np.asarray(contact) > 0)),
                    object_motion=float(np.linalg.norm(np.asarray(full)[-1, 4:6]-initial_object)))
    finally:
        env.close()


def evaluate():
    EVAL.mkdir(exist_ok=False)
    fit_meta = json.loads((FIT / 'fit.json').read_text())
    assert digest(ZIP) == fit_meta['source_zip_sha256']
    assert digest(FIT / 'ridge.npz') == fit_meta['checkpoint_sha256']
    with np.load(FIT / 'ridge.npz') as model:
        mean, std, coef = (model[key].copy() for key in ('mean', 'std', 'coef'))
    rows = []
    for seed in SEEDS:
        initials = []
        for route in ('hold', 'ridge_bc'):
            trace, row = rollout(seed, route, mean, std, coef)
            path = EVAL / f'{route}_{seed}.npz'
            np.savez_compressed(path, **trace)
            row.update(trace=path.name, sha256=digest(path))
            initials.append(trace['full'][0])
            rows.append(row)
            print(json.dumps({key: row[key] for key in ('seed', 'route', 'final_success',
                                                         'max_coverage', 'any_contact')}), flush=True)
        assert np.allclose(initials[0], initials[1], atol=1e-8)
    write(EVAL / 'evaluation.json', dict(status='completed', environment='gym_pusht/PushT-v0',
                                        source_zip_sha256=fit_meta['source_zip_sha256'],
                                        policy_checkpoint_sha256=fit_meta['checkpoint_sha256'],
                                        seeds=list(SEEDS), horizon=300, native_success='coverage > 0.95',
                                        rows=rows))


if __name__ == '__main__':
    if sys.argv[1] == 'fit':
        fit()
    elif sys.argv[1] == 'evaluate':
        evaluate()
    else:
        raise ValueError(sys.argv[1])
