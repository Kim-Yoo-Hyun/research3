"""Q16 exploratory policy adaptation. Run only inside its Docker image."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import time

import numpy as np
import torch
from diffusion import Policy, fit as fit_policy, STEPS as CHUNK
from dynamics import World, fit as fit_world
from task import make_env, initialize, observe, labels, Controller, GOAL, DT

torch.set_num_threads(1)
ROOT = Path('/output')
EPISODE_STEPS = 80
CONDITIONS = (('static', False, 0.01), ('moving', True, 0.01), ('friction', True, 0.05))
ROUTES = ('cv', 'anchor', 'policy2', 'policy1', 'fixed', 'feedback')


def serial(x):
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, np.generic):
        return x.item()
    raise TypeError(type(x).__name__)


def write(path, data):
    path.write_text(json.dumps(data, indent=2, default=serial, allow_nan=False) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vector(observation):
    # Only current/past observations. No contact, phase, goal-success or future state.
    return np.concatenate([observation[k] for k in ('cube', 'velocity', 'omega', 'tcp', 'qpos', 'qvel')]).astype(np.float32)


def set_friction(env, value):
    e = env.unwrapped
    for actor in (e.cube, e.table_scene.table):
        for body in actor._bodies:
            for shape in body.collision_shapes:
                shape.physical_material = __import__('sapien').physx.PhysxMaterial(value, value, 0.0)


def prepare(env, seed, moving, friction):
    meta = initialize(env, seed, moving)
    set_friction(env, friction)
    meta['friction'] = friction
    return meta


def raw_episode(states, truth, actions, decisions, meta, out):
    arrays = {key: np.stack([state[key] for state in states]) for key in states[0]}
    arrays.update(state=np.stack([vector(state) for state in states]),
                  action=np.stack(actions),
                  force=np.stack([value['forces'] for value in truth]),
                  direction=np.stack([value['directions'] for value in truth]),
                  grasp=np.array([value['grasp'] for value in truth]),
                  success=np.array([value['success'] for value in truth]))
    path = out / (meta['key'] + '.npz')
    if path.exists():
        raise FileExistsError(path)
    np.savez_compressed(path, **arrays)
    meta['trace_sha256'] = sha(path)
    meta['success_final5'] = bool(arrays['success'][-5:].all())
    meta['grasp_once'] = bool(arrays['grasp'].any())
    meta['releases'] = int(np.sum(arrays['grasp'][:-1] & ~arrays['grasp'][1:]))
    meta['final_goal_distance_m'] = float(np.linalg.norm(arrays['cube'][-1, :3] - GOAL))
    first = np.flatnonzero(arrays['success'])
    meta['first_success_s'] = float(first[0] * DT) if len(first) else None
    meta['decisions'] = len(decisions)
    meta['mean_decision_latency_ms'] = float(np.mean([d['latency_ms'] for d in decisions]))
    meta['mean_correction_norm'] = float(np.mean([d.get('correction_norm', 0.) for d in decisions]))
    errors = [d['prefix_error_m'] for d in decisions if d.get('prefix_error_m') is not None]
    meta['mean_prefix_prediction_error_m'] = float(np.mean(errors)) if errors else None
    write(path.with_suffix('.json'), dict(meta=meta, decisions=decisions))
    return meta


def collect(out):
    env = make_env()
    records = []
    for moving, seeds, split in ((False, range(30000, 30160), 'policy'),
                                 (True, range(31000, 31064), 'world')):
        for seed in seeds:
            meta = prepare(env, seed, moving, 0.01)
            meta.update(key=f'{seed}_{int(moving)}_teacher', split=split,
                        study='teacher demonstrations; 20 Hz; actual action sequence')
            teacher = Controller('cv')
            rng = np.random.default_rng(seed + 720000)
            states = [observe(env.unwrapped)]
            truth = [labels(env.unwrapped)]
            actions = []
            decisions = []
            previous = states[0]
            for t in range(EPISODE_STEPS):
                current = states[-1]
                start = time.perf_counter()
                action, debug = teacher.action(current, previous, hold=1)
                # Small action variation for world-model identification. No future or label input.
                action[:3] = np.clip(action[:3] + rng.uniform(-0.035, 0.035, 3), -0.25, 0.25)
                latency = 1000 * (time.perf_counter() - start)
                env.step(action)
                states.append(observe(env.unwrapped))
                truth.append(labels(env.unwrapped))
                actions.append(action.copy())
                decisions.append(dict(t=t, latency_ms=latency, teacher_phase=debug['phase']))
                previous = current
            records.append(raw_episode(states, truth, actions, decisions, meta, out))
            if len(records) % 16 == 0:
                print('collected', len(records), flush=True)
    env.close()
    write(out / 'collection.json', dict(episodes=len(records), records=records,
                                        policy_train_seeds=[30000, 30128], policy_val_seeds=[30128, 30160],
                                        world_extra_train=[31000, 31048], world_extra_val=[31048, 31064],
                                        evaluation_seeds=[32000, 32008]))


def load_episode(path):
    return dict(np.load(path))


def fit(data, out):
    static_train = [load_episode(data / f'{seed}_0_teacher.npz') for seed in range(30000, 30128)]
    static_val = [load_episode(data / f'{seed}_0_teacher.npz') for seed in range(30128, 30160)]
    moving_train = [load_episode(data / f'{seed}_1_teacher.npz') for seed in range(31000, 31048)]
    moving_val = [load_episode(data / f'{seed}_1_teacher.npz') for seed in range(31048, 31064)]
    summary = dict(policy=fit_policy(static_train, static_val, out),
                   dynamics=fit_world(static_train + moving_train, static_val + moving_val, out))
    summary['training_episodes'] = dict(policy=128, policy_validation=32, dynamics_extra=48,
                                        dynamics_extra_validation=16)
    write(out / 'fit.json', summary)
    for name in ('installed.lock', 'os-packages.lock'):
        shutil.copy2(Path('/recipe') / name, out / name)


def candidate_chunks(base):
    candidates = [base.copy()]
    for axis in range(3):
        for offset in (-0.08, 0.08):
            trial = base.copy()
            trial[:, axis] = np.clip(trial[:, axis] + offset, -0.25, 0.25)
            candidates.append(trial)
    for until in (2, 4):
        trial = base.copy()
        trial[until:, 3] = -1.
        candidates.append(trial)
    return np.stack(candidates)


def choose(chunk, world, previous, current, prior_action, bias):
    candidates = candidate_chunks(chunk)
    prediction = world.forecast(previous, current, prior_action, candidates)
    if bias is not None:
        # Last executed prefix's observed minus predicted object displacement.
        # Adjust future object positions without an online weight update.
        scale = (np.arange(CHUNK, dtype=np.float32) + 1) / 2
        prediction[:, :, :3] += bias[None, None, :] * scale[None, :, None]
    object_pos = prediction[:, :, :3]
    tcp_pos = prediction[:, :, 3:]
    if current[2] < 0.055:
        distance = np.linalg.norm(tcp_pos - object_pos, axis=2)
        objective = distance[:, -1] + 0.3 * distance.min(1) - 0.4 * np.maximum(object_pos[:, -1, 2] - 0.021, 0)
    else:
        objective = np.linalg.norm(object_pos[:, -1] - GOAL, axis=1)
    change = ((candidates - chunk[None]) ** 2).mean((1, 2))
    cost = objective + 0.10 * change
    index = int(np.argmin(cost))
    return candidates[index], prediction[index], dict(selected=index, cost=float(cost[index]),
                                                       correction_norm=float(np.linalg.norm(candidates[index] - chunk)))


def evaluate_episode(env, seed, condition, moving, friction, route, policy, world, out, model_sha):
    meta = prepare(env, seed, moving, friction)
    meta.update(key=f'{seed}_{condition}_{route}', condition=condition, route=route, model_sha256=model_sha)
    states = [observe(env.unwrapped)]
    truth = [labels(env.unwrapped)]
    actions = []
    decisions = []
    previous = states[0]
    prior_action = np.zeros(4, np.float32)
    teacher = Controller('cv') if route == 'cv' else None
    bias = np.zeros(3, np.float32)
    for t in range(0, EPISODE_STEPS, 1 if route == 'policy1' else 2):
        current = states[-1]
        previous_vec = vector(previous)
        current_vec = vector(current)
        start = time.perf_counter()
        if teacher is not None:
            single, extra = teacher.action(current, previous, hold=2)
            chunk = np.tile(single, (CHUNK, 1))
            forecast = None
        else:
            chunk = policy.sample(previous_vec, current_vec, seed * 100000 + t,
                                  anchor_only=(route == 'anchor'))
            extra = {}
            if route in ('fixed', 'feedback'):
                chunk, forecast, extra = choose(chunk, world, previous_vec, current_vec,
                                                prior_action, bias if route == 'feedback' else None)
            else:
                forecast = None
        latency = 1000 * (time.perf_counter() - start)
        prefix = 1 if route == 'policy1' else 2
        for i in range(prefix):
            action = chunk[i].copy()
            env.step(action)
            states.append(observe(env.unwrapped))
            truth.append(labels(env.unwrapped))
            actions.append(action)
        error = None
        if forecast is not None:
            error_vec = states[-1]['cube'][:3] - forecast[prefix - 1, :3]
            error = float(np.linalg.norm(error_vec))
            if route == 'feedback':
                bias = np.clip(error_vec, -0.03, 0.03)
        decisions.append(dict(t=t, latency_ms=latency, prefix_error_m=error, **extra))
        previous = current
        prior_action = actions[-1]
    return raw_episode(states, truth, actions, decisions, meta, out)


def evaluate(models, out, seed_start, seed_count):
    policy = Policy(models / 'policy.pt')
    world = World(models / 'world.pt')
    model_sha = {name: sha(models / name) for name in ('policy.pt', 'world.pt')}
    env = make_env()
    records = []
    for seed in range(seed_start, seed_start + seed_count):
        for condition, moving, friction in CONDITIONS:
            for route in ROUTES:
                records.append(evaluate_episode(env, seed, condition, moving, friction,
                                                route, policy, world, out, model_sha))
        print('evaluated initial seed', seed, len(records), flush=True)
    env.close()
    write(out / 'episodes.json', dict(records=records, conditions=CONDITIONS, routes=ROUTES,
                                      seed_start=seed_start, seed_count=seed_count,
                                      model_sha256=model_sha, device='cpu',
                                      source_commit='a4a4f9272ad64b1564035874b605ceb687b63ed8'))
    for name in ('installed.lock', 'os-packages.lock'):
        shutil.copy2(Path('/recipe') / name, out / name)


def verify(data, models, evaluation, out):
    evaluation_record = json.loads((evaluation / 'episodes.json').read_text())
    records = evaluation_record['records']
    seeds = range(evaluation_record['seed_start'],
                  evaluation_record['seed_start'] + evaluation_record['seed_count'])
    assert min(seeds) >= 32000
    assert len(records) == len(seeds) * len(CONDITIONS) * len(ROUTES)
    assert set(row['seed'] for row in records) == set(seeds)
    assert len(list(data.glob('*.npz'))) == 224
    for name in ('policy.pt', 'world.pt'):
        expected = sha(models / name)
        assert all(row['model_sha256'][name] == expected for row in records)
    raw_states = 0
    initial = {}
    verified = []
    for row in records:
        path = evaluation / (row['key'] + '.npz')
        assert sha(path) == row['trace_sha256']
        episode = dict(np.load(path))
        assert episode['action'].shape == (EPISODE_STEPS, 4)
        assert episode['state'].shape == (EPISODE_STEPS + 1, 38)
        assert np.isfinite(np.concatenate([value.ravel() for value in episode.values()])).all()
        force = episode['force']
        direction = episode['direction']
        magnitude = np.linalg.norm(force, axis=2)
        cosine = np.sum(force * direction, axis=2) / np.maximum(magnitude * np.linalg.norm(direction, axis=2), 1e-20)
        grasp = np.all((magnitude >= 0.5) & (cosine >= np.cos(np.deg2rad(85))), axis=1)
        success = grasp & (np.linalg.norm(episode['cube'][:, :3] - GOAL, axis=1) <= 0.025)
        assert np.array_equal(grasp, episode['grasp'])
        assert np.array_equal(success, episode['success'])
        assert bool(success[-5:].all()) == row['success_final5']
        assert int(np.sum(grasp[:-1] & ~grasp[1:])) == row['releases']
        assert np.allclose(episode['state'][:, :7], episode['cube'])
        assert np.allclose(episode['state'][:, 13:20], episode['tcp'])
        assert np.max(np.abs(episode['action'][:, :3])) <= 0.250001
        assert np.max(np.abs(episode['action'][:, 3])) <= 1.000001
        key = (row['seed'], row['condition'])
        now = episode['state'][0]
        if key in initial:
            assert np.allclose(now, initial[key], rtol=0, atol=1e-7), key
        else:
            initial[key] = now
        raw_states += len(episode['state'])
        verified.append(row)
    assert len(initial) == len(seeds) * len(CONDITIONS)
    groups = []
    for condition, _, _ in CONDITIONS:
        for route in ROUTES:
            group = [row for row in verified if row['condition'] == condition and row['route'] == route]
            groups.append(dict(condition=condition, route=route, episodes=len(group),
                               success=sum(row['success_final5'] for row in group),
                               grasp_once=sum(row['grasp_once'] for row in group),
                               releases=sum(row['releases'] for row in group),
                               mean_final_distance_m=float(np.mean([row['final_goal_distance_m'] for row in group])),
                               mean_latency_ms=float(np.mean([row['mean_decision_latency_ms'] for row in group])),
                               mean_correction_norm=float(np.mean([row['mean_correction_norm'] for row in group])),
                               mean_prefix_prediction_error_m=float(np.mean([
                                   row['mean_prefix_prediction_error_m'] for row in group
                                   if row['mean_prefix_prediction_error_m'] is not None]))
                               if route in ('fixed', 'feedback') else None))
    lookup = {(row['seed'], row['condition'], row['route']): row for row in records}
    paired = []
    for condition, _, _ in CONDITIONS:
        for baseline in ('cv', 'anchor', 'policy2', 'policy1', 'fixed'):
            pairs = [(lookup[(seed, condition, baseline)], lookup[(seed, condition, 'feedback')])
                     for seed in seeds]
            paired.append(dict(condition=condition, baseline=baseline,
                               feedback_improved=sum((not a['success_final5']) and b['success_final5'] for a, b in pairs),
                               feedback_harmed=sum(a['success_final5'] and (not b['success_final5']) for a, b in pairs)))
    summary = dict(scope='exploratory first policy-adaptation prototype; one trained policy and world model; no paper claim',
                   verification=dict(status='passed', evaluation_episodes=len(records), raw_states=raw_states,
                                     paired_initial_conditions=len(initial), collection_episodes=224,
                                     checks=['source trace sha256', 'force/direction grasp', 'goal and sustained success',
                                             'paired initial state', 'episode separation', 'finite values',
                                             'policy and world checkpoint identity']),
                   fit=json.loads((models / 'fit.json').read_text()), results=groups, paired_feedback=paired)
    summary['fit']['policy'].pop('curve')
    summary['fit']['dynamics'].pop('curve')
    write(out / 'summary.json', summary)
    with (out / 'episodes.csv').open('w') as stream:
        keys = ('seed', 'condition', 'route', 'success_final5', 'grasp_once', 'releases',
                'first_success_s', 'final_goal_distance_m', 'mean_decision_latency_ms',
                'mean_correction_norm', 'mean_prefix_prediction_error_m')
        writer = csv.DictWriter(stream, fieldnames=keys)
        writer.writeheader()
        writer.writerows({key: row[key] for key in keys} for row in records)
    print(json.dumps(dict(verification=summary['verification'], results=groups), indent=2), flush=True)


def diagnose(data, evaluation, out):
    first_seed = min(row['seed'] for row in json.loads((evaluation / 'episodes.json').read_text())['records'])
    records = []
    for seed, condition, route in ((30000, 'teacher', 'teacher'),
                                   (first_seed, 'static', 'cv'), (first_seed, 'static', 'anchor'),
                                   (first_seed, 'static', 'policy2'),
                                   (first_seed, 'static', 'fixed'), (first_seed, 'static', 'feedback'),
                                   (first_seed, 'moving', 'policy2')):
        key = f'{seed}_0_teacher' if route == 'teacher' else f'{seed}_{condition}_{route}'
        path = (data if route == 'teacher' else evaluation) / (key + '.npz')
        d = dict(np.load(path))
        actions = d['action']
        object_pos = d['cube'][:, :3]
        tcp_pos = d['tcp'][:, :3]
        records.append(dict(key=key,
                            first_12_actions=actions[:12].round(4).tolist(),
                            first_12_mean_action=actions[:12].mean(0).tolist(),
                            whole_episode_action_std=actions.std(0).tolist(),
                            first_12_gripper_close_fraction=float(np.mean(actions[:12, 3] < 0)),
                            first_40_min_tcp_object_distance_m=float(np.linalg.norm(tcp_pos[:41] - object_pos[:41], axis=1).min()),
                            min_tcp_object_distance_m=float(np.linalg.norm(tcp_pos - object_pos, axis=1).min()),
                            max_object_height_m=float(object_pos[:, 2].max()),
                            grasp_once=bool(d['grasp'].any()),
                            final_goal_distance_m=float(np.linalg.norm(object_pos[-1] - GOAL))))
    write(out / 'diagnosis.json', records)
    print(json.dumps(records, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=('collect', 'fit', 'evaluate', 'verify', 'diagnose'))
    parser.add_argument('--attempt', required=True)
    parser.add_argument('--data', default='collect1')
    parser.add_argument('--models', default='fit1')
    parser.add_argument('--evaluation', default='eval1')
    parser.add_argument('--seed-start', type=int, default=32008)
    parser.add_argument('--seed-count', type=int, default=8)
    args = parser.parse_args()
    out = ROOT / args.attempt
    out.mkdir(exist_ok=True)
    if args.stage == 'collect':
        collect(out)
    elif args.stage == 'fit':
        fit(ROOT / args.data, out)
    elif args.stage == 'evaluate':
        evaluate(ROOT / args.models, out, args.seed_start, args.seed_count)
    elif args.stage == 'verify':
        verify(ROOT / args.data, ROOT / args.models, ROOT / args.evaluation, out)
    else:
        diagnose(ROOT / args.data, ROOT / args.evaluation, out)


if __name__ == '__main__':
    main()
