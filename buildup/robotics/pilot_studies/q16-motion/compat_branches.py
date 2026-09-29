"""Exploratory paired PushT action branches; run only in the Q16 CUDA container."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import torch
from torch import nn

from compat_bc import BC, load_ppo
from compat_env import make_env, native_metric, observe

ROOT = Path('/output')
PREVIOUS = Path('/previous')
SEEDS = (47010, 47011, 47012, 47014)
GOAL_YAW = 5 * math.pi / 3
NAMES = ('bc', 'feedback', 'bc_plus_x', 'bc_minus_x', 'bc_plus_y', 'bc_minus_y', 'ppo_mean')


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def write(path, payload):
    path.write_text(json.dumps(payload, indent=2, allow_nan=False) + '\n')


def yaw(q):
    q = np.asarray(q)
    return np.arctan2(2 * (q[..., 0] * q[..., 3] + q[..., 1] * q[..., 2]),
                     1 - 2 * (q[..., 2] ** 2 + q[..., 3] ** 2))


def xy_yaw(x):
    return np.stack((x[..., 24], x[..., 25], yaw(x[..., 27:31])), axis=-1)


def transitions(data, split, counts):
    x, a = data[f'{split}_obs'], data[f'{split}_act']
    pairs = []
    cursor = 0
    for item in counts:
        length = item['rows']
        pairs.append((np.arange(cursor, cursor + length - 1),
                      np.arange(cursor + 1, cursor + length)))
        cursor += length
    assert cursor == len(x) == len(a)
    first, next_ = (np.concatenate([p[i] for p in pairs]) for i in (0, 1))
    target = xy_yaw(x[next_]) - xy_yaw(x[first])
    target[:, 2] = np.arctan2(np.sin(target[:, 2]), np.cos(target[:, 2]))
    features = np.concatenate((x[first], a[first]), axis=-1)
    return features.astype(np.float32), target.astype(np.float32)


class Dynamics(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(34, 128), nn.Tanh(), nn.Linear(128, 128),
                                 nn.Tanh(), nn.Linear(128, 3))

    def forward(self, x):
        return self.net(x)


def fit():
    out = ROOT / 'fit1'
    out.mkdir()
    meta = json.loads((PREVIOUS / 'data_full1/extraction.json').read_text())
    assert sha(PREVIOUS / 'data_full1/dataset.npz') == meta['dataset_sha256']
    with np.load(PREVIOUS / 'data_full1/dataset.npz') as data:
        train_x, train_y = transitions(data, 'train', meta['split']['train'])
        valid_x, valid_y = transitions(data, 'valid', meta['split']['valid'])
    assert len(train_x) == meta['rows']['train'] - 792
    assert len(valid_x) == meta['rows']['valid'] - 88
    torch.manual_seed(16026)
    torch.cuda.manual_seed_all(16026)
    xmean = torch.from_numpy(train_x.mean(0)).cuda()
    xstd = torch.from_numpy(train_x.std(0).clip(1e-3)).cuda()
    ymean = torch.from_numpy(train_y.mean(0)).cuda()
    ystd = torch.from_numpy(train_y.std(0).clip(1e-4)).cuda()
    tx = (torch.from_numpy(train_x).cuda() - xmean) / xstd
    ty = (torch.from_numpy(train_y).cuda() - ymean) / ystd
    vx = (torch.from_numpy(valid_x).cuda() - xmean) / xstd
    vy = torch.from_numpy(valid_y).cuda()
    model = Dynamics().cuda()
    optim = torch.optim.Adam(model.parameters(), lr=1e-3)
    generator = torch.Generator(device='cuda').manual_seed(16026)
    history = []
    best = math.inf
    for epoch in range(1, 31):
        model.train()
        for batch in torch.randperm(len(tx), generator=generator, device='cuda').split(512):
            error = ((model(tx[batch]) - ty[batch]) ** 2).mean()
            optim.zero_grad(set_to_none=True)
            error.backward()
            optim.step()
        model.eval()
        with torch.no_grad():
            pred = model(vx) * ystd + ymean
            rmse = torch.sqrt(((pred - vy) ** 2).mean(0)).cpu().numpy().tolist()
            score = float(np.mean(rmse))
        history.append(dict(epoch=epoch, valid_rmse_xy_yaw=rmse))
        if score < best:
            best = score
            best_epoch = epoch
            torch.save(dict(model=model.state_dict(), xmean=xmean.cpu(), xstd=xstd.cpu(),
                            ymean=ymean.cpu(), ystd=ystd.cpu(), epoch=epoch,
                            data_sha256=meta['dataset_sha256']), out / 'dynamics.pt')
        if epoch % 5 == 0:
            print(json.dumps(history[-1]), flush=True)
    write(out / 'fit.json', dict(status='completed', source_data_sha256=meta['dataset_sha256'],
                                 train_transitions=len(train_x), valid_transitions=len(valid_x),
                                 seed=16026, epochs=30, batch_size=512, architecture='34-128-128-3 tanh',
                                 target='next object delta XY/yaw', best_epoch=best_epoch,
                                 best_valid_rmse_xy_yaw=history[best_epoch-1]['valid_rmse_xy_yaw'],
                                 checkpoint_sha256=sha(out / 'dynamics.pt'), history=history))


def load_models():
    bc_meta = json.loads((PREVIOUS / 'fit_full1/fit.json').read_text())
    assert sha(PREVIOUS / 'fit_full1/bc.pt') == bc_meta['checkpoint_sha256']
    saved_bc = torch.load(PREVIOUS / 'fit_full1/bc.pt', map_location='cpu', weights_only=True)
    bc = BC().cuda().eval()
    bc.load_state_dict(saved_bc['model'])
    fit_meta = json.loads((ROOT / 'fit1/fit.json').read_text())
    assert sha(ROOT / 'fit1/dynamics.pt') == fit_meta['checkpoint_sha256']
    saved_dynamics = torch.load(ROOT / 'fit1/dynamics.pt', map_location='cpu', weights_only=True)
    dynamics = Dynamics().cuda().eval()
    dynamics.load_state_dict(saved_dynamics['model'])
    return bc, saved_bc['mean'].cuda(), saved_bc['scale'].cuda(), dynamics, saved_dynamics


def bc_action(bc, mean, scale, obs):
    with torch.no_grad():
        return bc((obs - mean) / scale).detach().cpu().numpy().reshape(3).astype(np.float32)


def feedback_action(obs):
    x = obs.detach().cpu().numpy().reshape(-1)
    tcp, goal, obj = x[14:17], x[21:24], x[24:27]
    direction = goal[:2] - obj[:2]
    direction /= max(float(np.linalg.norm(direction)), 1e-6)
    target = np.r_[goal[:2] - 0.035 * direction, 0.03]
    return np.clip((target - tcp) / 0.1, -0.25, 0.25).astype(np.float32)


def prediction(model, saved, obs, actions):
    x = obs.detach().cpu().numpy().reshape(31)
    features = np.concatenate((np.repeat(x[None], len(actions), axis=0),
                               np.asarray(actions, np.float32)), axis=1)
    with torch.no_grad():
        raw = torch.from_numpy(features).cuda()
        mean = saved['xmean'].cuda()
        std = saved['xstd'].cuda()
        delta = (model((raw - mean) / std) * saved['ystd'].cuda() +
                 saved['ymean'].cuda()).cpu().numpy()
    current = xy_yaw(x)
    predicted = current[None] + delta
    score = -np.linalg.norm(predicted[:, :2] - x[21:23], axis=1) / 0.1
    score += 0.2 * np.cos(predicted[:, 2] - GOAL_YAW)
    return delta, score


def select_steps(trace):
    obj, metric = trace['object'], trace['metric']
    displacement = np.linalg.norm(obj[:, :2] - obj[0, :2], axis=1)
    candidates = np.flatnonzero(displacement[:90] >= 0.02)
    if not len(candidates):
        return [], 'no 2 cm translation before final 10 steps'
    first = int(candidates[0])
    peak = int(candidates[np.argmax(metric[candidates])])
    return sorted(set((first, peak))), None


def fresh_bc(env, seed, bc, mean, scale):
    obs, _ = env.reset(seed=seed)
    objects = [observe(env, 'push_t')['object']]
    metrics = [native_metric(env, 'push_t')[0]]
    actions = []
    snapshots = [snapshot(env, obs)]
    for _ in range(100):
        action = bc_action(bc, mean, scale, obs)
        obs, _, _, _, _ = env.step(action)
        actions.append(action)
        objects.append(observe(env, 'push_t')['object'])
        metrics.append(native_metric(env, 'push_t')[0])
        snapshots.append(snapshot(env, obs))
    return (dict(object=np.asarray(objects), metric=np.asarray(metrics, np.float32),
                 action=np.asarray(actions, np.float32)), snapshots)


def snapshot(env, obs):
    e = env.unwrapped
    return dict(physics=copy.deepcopy(e.get_state_dict()),
                controller=copy.deepcopy(e.agent.controller.get_state()),
                elapsed=copy.deepcopy(e._elapsed_steps),
                observation=obs.detach().clone())


def restore_snapshot(env, snap):
    e = env.unwrapped
    e.set_state_dict(copy.deepcopy(snap['physics']))
    e.agent.controller.set_state(copy.deepcopy(snap['controller']))
    e._elapsed_steps[:] = snap['elapsed']
    obs = e.get_obs()
    if not np.allclose(obs.detach().cpu().numpy(), snap['observation'].detach().cpu().numpy(), atol=5e-5):
        raise ValueError('Snapshot observation differs after restore')
    return obs


def replay_prefix(env, seed, step, bc, mean, scale, reference):
    obs, _ = env.reset(seed=seed)
    first = observe(env, 'push_t')
    current_metric, _ = native_metric(env, 'push_t')
    assert np.allclose(first['object'], reference['object'][0], atol=5e-5)
    assert abs(current_metric - float(reference['metric'][0])) < 1e-3
    for i in range(step):
        action = bc_action(bc, mean, scale, obs)
        if not np.allclose(action, reference['action'][i], atol=1e-4):
            raise ValueError(f'BC action prefix differs: seed={seed}, step={i}')
        obs, _, _, _, _ = env.step(action)
        current = observe(env, 'push_t')
        current_metric, _ = native_metric(env, 'push_t')
        if not np.allclose(current['object'], reference['object'][i+1], atol=5e-4):
            raise ValueError(f'Object prefix differs: seed={seed}, step={i+1}')
        if abs(current_metric - float(reference['metric'][i+1])) >= 0.005:
            raise ValueError(f'Overlap prefix differs: seed={seed}, step={i+1}')
    return obs


def diagnose(attempt):
    out = ROOT / attempt
    out.mkdir()
    bc, mean, scale, model, saved = load_models()
    ppo = load_ppo()
    env = make_env('push_t', device='gpu', obs_mode='state', native=True)
    rows = []
    skipped = []
    replay_comparisons = []
    try:
        for seed in SEEDS:
            with np.load(PREVIOUS / f'eval_full1/bc_{seed}.npz') as old_file:
                old = {key: old_file[key] for key in old_file.files}
            fresh, snapshots = fresh_bc(env, seed, bc, mean, scale)
            trace_file = out / f'bc_replay_{seed}.npz'
            np.savez_compressed(trace_file, **fresh)
            same_length = len(old['action']) == len(fresh['action'])
            comparison = dict(seed=seed, original_final_metric=float(old['metric'][-1]),
                              replay_final_metric=float(fresh['metric'][-1]),
                              replay_final_success=bool(fresh['metric'][-1] >= .90),
                              same_length=same_length, trace=trace_file.name, sha256=sha(trace_file))
            if same_length:
                comparison.update(max_action_difference=float(np.max(np.abs(old['action']-fresh['action']))),
                                  max_object_position_difference=float(np.max(np.abs(old['object'][:, :3]-fresh['object'][:, :3]))),
                                  max_metric_difference=float(np.max(np.abs(old['metric']-fresh['metric']))))
            replay_comparisons.append(comparison)
            print(json.dumps(comparison), flush=True)
            if comparison['replay_final_success']:
                skipped.append(dict(seed=seed, reason='prior BC failure did not reproduce in fresh full trajectory'))
                continue
            steps, reason = select_steps(fresh)
            if reason:
                skipped.append(dict(seed=seed, reason=reason))
                continue
            for step in steps:
                snap = snapshots[step]
                state_file = out / f'state_{seed}_{step}.pt'
                torch.save(snap, state_file)
                obs = restore_snapshot(env, snap)
                before = observe(env, 'push_t')
                initial_metric, _ = native_metric(env, 'push_t')
                if not np.allclose(before['object'], fresh['object'][step], atol=5e-4):
                    raise ValueError(f'Snapshot object differs from source BC: {seed} {step}')
                base = bc_action(bc, mean, scale, obs)
                simple = feedback_action(obs)
                with torch.no_grad():
                    reference = ppo(obs).detach().cpu().numpy().reshape(3).astype(np.float32)
                offset = np.array([[.2, 0, 0], [-.2, 0, 0], [0, .2, 0], [0, -.2, 0]], np.float32)
                names = NAMES
                actions = [base, simple] + [np.clip(base + shift, -1, 1) for shift in offset] + [reference]
                predicted, score = prediction(model, saved, obs, actions)
                selected = int(np.argmax(score[:6]))
                branch_rows = []
                for name, action, delta, value in zip(names + ('bc_repeat',), actions + [base],
                                                      np.concatenate((predicted, predicted[:1])),
                                                      np.concatenate((score, score[:1]))):
                    branch_obs = restore_snapshot(env, snap)
                    check = observe(env, 'push_t')
                    if not all(np.allclose(before[key], check[key], atol=5e-5)
                               for key in ('object', 'goal', 'tcp', 'qpos')):
                        raise ValueError(f'Paired prefix state differs: {seed} {step} {name}')
                    if not np.allclose(obs.detach().cpu().numpy(), branch_obs.detach().cpu().numpy(), atol=5e-5):
                        raise ValueError(f'Paired observation differs: {seed} {step} {name}')
                    branch_obs, _, _, _, _ = env.step(action)
                    after_one = observe(env, 'push_t')
                    metric_one, _ = native_metric(env, 'push_t')
                    actual = xy_yaw(branch_obs.detach().cpu().numpy().reshape(-1)) - xy_yaw(obs.detach().cpu().numpy().reshape(-1))
                    actual[2] = math.atan2(math.sin(actual[2]), math.cos(actual[2]))
                    for _ in range(10):
                        branch_obs, _, _, _, _ = env.step(bc_action(bc, mean, scale, branch_obs))
                    metric_final, success = native_metric(env, 'push_t')
                    branch_rows.append(dict(route=name, action=action.tolist(), predicted_delta=delta.tolist(),
                                            actual_delta=actual.tolist(), predicted_score=float(value),
                                            metric_after_one=metric_one, metric_after_ten=metric_final,
                                            success_after_ten=success,
                                            prediction_error_xy=float(np.linalg.norm(delta[:2]-actual[:2]))))
                baseline_repeat = branch_rows.pop()
                if abs(baseline_repeat['metric_after_one'] - branch_rows[0]['metric_after_one']) > 0.005 or \
                   abs(baseline_repeat['metric_after_ten'] - branch_rows[0]['metric_after_ten']) > 0.005:
                    raise ValueError(f'BC repeat branch changed after state restores: {seed} {step}')
                row = dict(seed=seed, step=step, initial_metric=initial_metric,
                           snapshot=state_file.name, snapshot_sha256=sha(state_file),
                           initial_object=before['object'].tolist(), initial_goal=before['goal'].tolist(),
                           bc_repeat_metric_after_one=baseline_repeat['metric_after_one'],
                           bc_repeat_metric_after_ten=baseline_repeat['metric_after_ten'],
                           selected_by_model=names[selected], branches=branch_rows)
                rows.append(row)
                print(json.dumps(dict(seed=seed, step=step, selected=names[selected],
                                      after_ten={r['route']: round(r['metric_after_ten'], 3) for r in branch_rows})), flush=True)
    finally:
        env.close()
    write(out / 'branches.json', dict(status='completed', purpose='exploratory development',
                                      source_eval_sha256=sha(PREVIOUS / 'eval_full1/evaluation.json'),
                                      bc_sha256=sha(PREVIOUS / 'fit_full1/bc.pt'),
                                      dynamics_sha256=sha(ROOT / 'fit1/dynamics.pt'),
                                      seeds=list(SEEDS), selected_state_count=len(rows), skipped=skipped,
                                      replay_comparisons=replay_comparisons,
                                      candidates=NAMES, score='-XY distance / 0.1 + 0.2*cos(yaw - 5pi/3)',
                                      rows=rows))


def validate(attempt):
    source = ROOT / attempt / 'branches.json'
    data = json.loads(source.read_text())
    assert data['status'] == 'completed' and data['seeds'] == list(SEEDS)
    assert len(data['rows']) + len(data['skipped']) >= len(SEEDS)
    seen = set()
    tally = dict(model_over_bc=0, model_over_feedback=0, model_different_bc=0,
                 feedback_over_bc=0, valid_states=0)
    for row in data['rows']:
        key = (row['seed'], row['step'])
        assert key not in seen
        seen.add(key)
        assert sha(ROOT / attempt / row['snapshot']) == row['snapshot_sha256']
        branch = {b['route']: b for b in row['branches']}
        assert set(branch) == set(data['candidates'])
        assert row['selected_by_model'] == max(row['branches'][:6], key=lambda b: b['predicted_score'])['route']
        for b in row['branches']:
            assert np.isfinite(b['action']).all() and np.isfinite(b['actual_delta']).all()
            assert np.isfinite(b['predicted_delta']).all()
            assert b['success_after_ten'] == (b['metric_after_ten'] >= .90)
            assert abs(b['prediction_error_xy'] - np.linalg.norm(np.asarray(b['predicted_delta'][:2]) -
                                                                np.asarray(b['actual_delta'][:2]))) < 1e-6
        assert abs(row['bc_repeat_metric_after_one'] - branch['bc']['metric_after_one']) <= .005
        assert abs(row['bc_repeat_metric_after_ten'] - branch['bc']['metric_after_ten']) <= .005
        chosen = branch[row['selected_by_model']]
        tally['valid_states'] += 1
        tally['model_different_bc'] += chosen['route'] != 'bc'
        tally['model_over_bc'] += chosen['metric_after_ten'] > branch['bc']['metric_after_ten'] + 1e-4
        tally['model_over_feedback'] += chosen['metric_after_ten'] > branch['feedback']['metric_after_ten'] + 1e-4
        tally['feedback_over_bc'] += branch['feedback']['metric_after_ten'] > branch['bc']['metric_after_ten'] + 1e-4
    for replay in data['replay_comparisons']:
        assert sha(ROOT / attempt / replay['trace']) == replay['sha256']
    write(ROOT / attempt / 'verification.json', dict(status='passed', branch_sha256=sha(source),
                                                  seeds=list(SEEDS), state_pairs=sorted([list(x) for x in seen]),
                                                  summary=tally, skipped=data['skipped']))
    print(json.dumps(tally), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=('fit', 'diagnose', 'validate'))
    parser.add_argument('--attempt', default='branch2')
    args = parser.parse_args()
    {'fit': fit, 'diagnose': lambda: diagnose(args.attempt),
     'validate': lambda: validate(args.attempt)}[args.stage]()
