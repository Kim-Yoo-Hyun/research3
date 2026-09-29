"""Q16 delayed-object PushCube comparison; simulator/ML execution only in Docker."""
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
from delay_dynamics import World, fit as fit_world
from delay_task import Sensor, FeedbackWithDelay, vector, LAG_STEPS, LAG_SECONDS
from push_task import make_env, observe, native_success, set_friction, EPISODE_STEPS, DT

torch.set_num_threads(1)
ROOT = Path('/output')
NOMINAL_TRAIN = range(40000, 40096)
NOMINAL_VAL = range(40096, 40120)
EXTRA_TRAIN = range(41000, 41032)
EXTRA_VAL = range(41032, 41040)
CONDITIONS = (('nominal', 0.4), ('low_friction', 0.05))
ROUTES = ('delayed_feedback', 'velocity_feedback', 'frozen', 'updated', 'model_guided', 'clean_feedback')


def serial(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(type(value).__name__)


def write(path, value):
    path.write_text(json.dumps(value, indent=2, default=serial, allow_nan=False) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reset(env, seed, friction):
    env.reset(seed=seed)
    set_friction(env, friction)
    o = observe(env.unwrapped)
    return dict(seed=seed, friction=friction, lag_steps=LAG_STEPS, lag_seconds=LAG_SECONDS,
                initial_cube=o['cube'][:3], initial_tcp=o['tcp'][:3], native_goal=o['goal'],
                goal_radius=env.unwrapped.goal_radius)


def save_episode(out, key, states, truth, actions, labels, decisions, meta):
    array = {k: np.stack([s[k] for s in states]) for k in states[0]}
    array.update(state=np.stack([vector(s) for s in states]),
                 truth_state=np.stack([vector(s) for s in truth]),
                 true_cube=np.stack([s['cube'] for s in truth]),
                 action=np.stack(actions), native_success=np.asarray(labels, np.bool_))
    path = out / f'{key}.npz'
    if path.exists():
        raise FileExistsError(path)
    np.savez_compressed(path, **array)
    distance = np.linalg.norm(array['true_cube'][:, :2] - array['goal'][:, :2], axis=1)
    first = np.flatnonzero(array['native_success'])
    meta.update(key=key, trace_sha256=sha(path), native_success=bool(labels[-1]),
                success_any=bool(first.size), first_success_s=float(first[0] * DT) if first.size else None,
                final_xy_error_m=float(distance[-1]), initial_xy_error_m=float(distance[0]),
                min_xy_error_m=float(distance.min()), cube_x_progress_m=float(array['true_cube'][-1, 0] - array['true_cube'][0, 0]),
                decisions=len(decisions), mean_latency_ms=float(np.mean([d['latency_ms'] for d in decisions])),
                mean_correction_norm=float(np.mean([d.get('correction_norm', 0.) for d in decisions])))
    errors = [d['prediction_error_m'] for d in decisions if d.get('prediction_error_m') is not None]
    meta['mean_prediction_error_m'] = float(np.mean(errors)) if errors else None
    write(path.with_suffix('.json'), dict(meta=meta, decisions=decisions))
    return meta


def collect(out):
    env = make_env()
    records = []
    for split, seeds, friction in (('nominal_train', NOMINAL_TRAIN, 0.4),
                                   ('nominal_val', NOMINAL_VAL, 0.4),
                                   ('extra_train', EXTRA_TRAIN, 0.05),
                                   ('extra_val', EXTRA_VAL, 0.05)):
        for seed in seeds:
            meta = reset(env, seed, friction)
            meta.update(split=split, source='delayed-velocity feedback teacher, real executed actions')
            teacher = FeedbackWithDelay(compensate=True)
            rng = np.random.default_rng(seed + 190000)
            sensor = Sensor(env)
            first_observation, first_truth = sensor.read()
            states, truth = [first_observation], [first_truth]
            labels = [native_success(env.unwrapped)]
            actions = []
            decisions = []
            for t in range(EPISODE_STEPS):
                start = time.perf_counter()
                action, phase = teacher.action(states[-1])
                action[:3] = np.clip(action[:3] + rng.uniform(-0.02, 0.02, 3), -0.25, 0.25)
                latency = 1000 * (time.perf_counter() - start)
                env.step(action)
                measured, actual = sensor.read()
                states.append(measured)
                truth.append(actual)
                labels.append(native_success(env.unwrapped))
                actions.append(action)
                decisions.append(dict(t=t, phase=phase, latency_ms=latency))
            records.append(save_episode(out, f'{seed}_teacher', states, truth, actions, labels, decisions, meta))
            if len(records) % 20 == 0:
                print('collected', len(records), flush=True)
    env.close()
    write(out / 'collection.json', dict(records=records, train_nominal=len(NOMINAL_TRAIN),
                                        val_nominal=len(NOMINAL_VAL), train_extra=len(EXTRA_TRAIN),
                                        val_extra=len(EXTRA_VAL), evaluation_seed_start=44000,
                                        lag_steps=LAG_STEPS, lag_seconds=LAG_SECONDS))


def load(data, seeds):
    return [dict(np.load(data / f'{seed}_teacher.npz')) for seed in seeds]


def fit(data, out):
    nominal_train, nominal_val = load(data, NOMINAL_TRAIN), load(data, NOMINAL_VAL)
    extra_train, extra_val = load(data, EXTRA_TRAIN), load(data, EXTRA_VAL)
    frozen_dir, updated_dir = out / 'frozen', out / 'updated'
    frozen_dir.mkdir()
    updated_dir.mkdir()
    results = dict(frozen_policy=fit_policy(nominal_train, nominal_val, frozen_dir),
                   updated_policy=fit_policy(nominal_train + extra_train, nominal_val + extra_val, updated_dir),
                   dynamics=fit_world(nominal_train + extra_train, nominal_val + extra_val, out),
                   split=dict(nominal_train=len(nominal_train), nominal_val=len(nominal_val),
                              extra_train=len(extra_train), extra_val=len(extra_val)))
    write(out / 'fit.json', results)
    for name in ('installed.lock', 'os-packages.lock'):
        shutil.copy2(Path('/recipe') / name, out / name)


def candidates(base, offset=0.08):
    chunks = [base.copy()]
    for axis in (0, 1, 2):
        for delta in (-offset, offset):
            trial = base.copy()
            trial[:, axis] = np.clip(trial[:, axis] + delta, -0.25, 0.25)
            chunks.append(trial)
    return np.stack(chunks)


def correct(base, world, previous, current, prior, offset=0.04):
    chunks = candidates(base, offset)
    forecast = world.forecast(previous, current, prior, chunks)
    goal = current[-3:]
    object_xy = forecast[:, -1, :2]
    tcp_xy = forecast[:, -1, 3:5]
    goal_error = np.linalg.norm(object_xy - goal[None, :2], axis=1)
    # Discourage candidates that move the TCP away from the object during contact.
    contact = np.linalg.norm(tcp_xy - object_xy - np.array([-0.04, 0], np.float32), axis=1)
    change = ((chunks - base[None]) ** 2).mean((1, 2))
    score = goal_error + 0.2 * contact + 0.1 * change
    index = int(np.argmin(score))
    return chunks[index], forecast[index], dict(selected=index, correction_norm=float(np.linalg.norm(chunks[index] - base)),
                                                  score=float(score[index]))


def contact_gate(o):
    cube = o['cube'][:3].copy()
    cube[:2] += o['velocity'][:2] * LAG_SECONDS
    tcp = o['tcp'][:3]
    return bool(tcp[0] <= cube[0] - 0.02 and abs(tcp[1] - cube[1]) < 0.04
                and tcp[2] <= cube[2] + 0.065)


def evaluate_one(env, seed, condition, friction, route, frozen, updated, world, out, checkpoint_hash):
    meta = reset(env, seed, friction)
    meta.update(condition=condition, route=route, checkpoint_sha256=checkpoint_hash)
    sensor = Sensor(env)
    first_observation, first_truth = sensor.read()
    states, truth = [first_observation], [first_truth]
    labels = [native_success(env.unwrapped)]
    actions, decisions = [], []
    previous = states[0]
    prior_action = np.zeros(4, np.float32)
    feedback = FeedbackWithDelay(compensate=(route == 'velocity_feedback'))
    for t in range(0, EPISODE_STEPS, 2):
        current = states[-1]
        start = time.perf_counter()
        if route in ('delayed_feedback', 'velocity_feedback', 'clean_feedback'):
            action, phase = feedback.action(truth[-1] if route == 'clean_feedback' else current)
            chunk = np.tile(action, (CHUNK, 1))
            prediction = None
            extra = dict(phase=phase)
        else:
            policy = updated if route == 'updated' else frozen
            chunk = policy.sample(vector(previous), vector(current), seed * 100000 + t)
            prediction = None
            extra = {}
            if route == 'model_guided':
                allowed = contact_gate(current)
                extra = dict(contact_gate_open=allowed)
                if allowed:
                    chunk, prediction, correction = correct(chunk, world, vector(previous), vector(current), prior_action)
                    extra.update(correction)
        latency = 1000 * (time.perf_counter() - start)
        prefix = 2
        for i in range(prefix):
            action = chunk[i].copy()
            env.step(action)
            measured, actual = sensor.read()
            states.append(measured)
            truth.append(actual)
            labels.append(native_success(env.unwrapped))
            actions.append(action)
        error = None
        if prediction is not None:
            # Offline diagnosis only; this true-state residual never affects action selection.
            residual = truth[-1]['cube'][:3] - prediction[prefix - 1, :3]
            error = float(np.linalg.norm(residual))
        decisions.append(dict(t=t, latency_ms=latency, prediction_error_m=error, **extra))
        previous = current
        prior_action = actions[-1]
    return save_episode(out, f'{seed}_{condition}_{route}', states, truth, actions, labels, decisions, meta)


def evaluate(models, out, seed_start, seed_count):
    frozen = Policy(models / 'frozen/policy.pt')
    updated = Policy(models / 'updated/policy.pt')
    world = World(models / 'world.pt')
    hashes = {name: sha(models / name) for name in ('frozen/policy.pt', 'updated/policy.pt', 'world.pt')}
    env = make_env()
    records = []
    for seed in range(seed_start, seed_start + seed_count):
        for condition, friction in CONDITIONS:
            for route in ROUTES:
                records.append(evaluate_one(env, seed, condition, friction, route, frozen, updated, world, out, hashes))
        print('evaluated seed', seed, len(records), flush=True)
    env.close()
    write(out / 'episodes.json', dict(records=records, seed_start=seed_start, seed_count=seed_count,
                                      conditions=CONDITIONS, routes=ROUTES, checkpoints=hashes))


def verify(data, models, evaluation, out):
    payload = json.loads((evaluation / 'episodes.json').read_text())
    records = payload['records']
    checks = []
    for rec in records:
        path = evaluation / f"{rec['key']}.npz"
        if sha(path) != rec['trace_sha256']:
            raise ValueError(f'checksum {path}')
        with np.load(path) as episode:
            if (episode['state'].shape != (EPISODE_STEPS + 1, 41)
                    or episode['truth_state'].shape != (EPISODE_STEPS + 1, 41)
                    or episode['action'].shape != (EPISODE_STEPS, 4)):
                raise ValueError(f'shape {path}')
            true_state = episode['truth_state']
            observed = episode['state']
            expected = true_state[np.maximum(np.arange(len(true_state)) - LAG_STEPS, 0)]
            if not np.array_equal(observed[:, :13], expected[:, :13]):
                raise ValueError(f'object delay {path}')
            if not np.array_equal(observed[:, 13:], true_state[:, 13:]):
                raise ValueError(f'current robot/goal {path}')
            distance = np.linalg.norm(episode['true_cube'][:, :2] - episode['goal'][:, :2], axis=1)
            native = (distance < 0.1) & (episode['true_cube'][:, 2] < 0.025)
            if not np.array_equal(native, episode['native_success']):
                raise ValueError(f'native label {path}')
            if abs(float(distance[-1]) - rec['final_xy_error_m']) > 1e-7:
                raise ValueError(f'distance {path}')
        checks.append(rec)
    if len(checks) != payload['seed_count'] * len(CONDITIONS) * len(ROUTES):
        raise ValueError('evaluation count')
    collection = json.loads((data / 'collection.json').read_text())
    if len(collection['records']) != 160:
        raise ValueError('collection count')
    for rec in collection['records']:
        path = data / f"{rec['key']}.npz"
        if sha(path) != rec['trace_sha256']:
            raise ValueError(f'teacher checksum {path}')
        with np.load(path) as episode:
            expected = episode['truth_state'][np.maximum(np.arange(EPISODE_STEPS + 1) - LAG_STEPS, 0)]
            if not np.array_equal(episode['state'][:, :13], expected[:, :13]):
                raise ValueError(f'teacher delay {path}')
    grouping = {}
    for condition, _ in CONDITIONS:
        for route in ROUTES:
            rows = [r for r in records if r['condition'] == condition and r['route'] == route]
            grouping[f'{condition}/{route}'] = dict(n=len(rows), successes=sum(r['native_success'] for r in rows),
                                                    mean_final_xy_error_m=float(np.mean([r['final_xy_error_m'] for r in rows])),
                                                    median_final_xy_error_m=float(np.median([r['final_xy_error_m'] for r in rows])),
                                                    mean_latency_ms=float(np.mean([r['mean_latency_ms'] for r in rows])))
    paired = {}
    for condition, _ in CONDITIONS:
        keys = {r['seed'] for r in records if r['condition'] == condition}
        if len(keys) != payload['seed_count']:
            raise ValueError('seed pairing')
        for seed in keys:
            rows = [r for r in records if r['condition'] == condition and r['seed'] == seed]
            if len(rows) != len(ROUTES):
                raise ValueError('route pairing')
            for key in ('initial_cube', 'initial_tcp', 'native_goal', 'friction', 'lag_steps'):
                if any(row[key] != rows[0][key] for row in rows[1:]):
                    raise ValueError(f'initial-state mismatch {seed}/{condition}/{key}')
        paired[condition] = sorted(keys)
    result = dict(evaluation_episodes=len(records), states=len(records) * (EPISODE_STEPS + 1),
                  teacher_episodes=len(collection['records']), checked_checksum_count=len(records) + len(collection['records']),
                  lag_steps=LAG_STEPS, lag_seconds=LAG_SECONDS,
                  groups=grouping, paired_seeds=paired, models_sha256=payload['checkpoints'])
    write(out / 'verification.json', result)
    with (out / 'episodes.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['seed', 'condition', 'route', 'native_success',
                                                     'final_xy_error_m', 'cube_x_progress_m', 'first_success_s',
                                                     'mean_latency_ms', 'mean_prediction_error_m'])
        writer.writeheader()
        writer.writerows({k: r[k] for k in writer.fieldnames} for r in records)
    print(json.dumps(result, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['smoke', 'collect', 'fit', 'evaluate', 'verify'])
    parser.add_argument('--attempt', required=True)
    parser.add_argument('--data', default='collect1')
    parser.add_argument('--models', default='fit1')
    parser.add_argument('--evaluation', default='eval1')
    parser.add_argument('--seed-start', type=int, default=44000)
    parser.add_argument('--seed-count', type=int, default=16)
    args = parser.parse_args()
    out = ROOT / args.attempt
    out.mkdir(parents=True, exist_ok=True)
    if args.stage == 'smoke':
        env = make_env()
        results = []
        for seed in range(45000, 45008):
            for route in ('delayed_feedback', 'velocity_feedback', 'clean_feedback'):
                meta = reset(env, seed, 0.4)
                meta.update(route=route)
                sensor = Sensor(env)
                measured, actual = sensor.read()
                states, truth = [measured], [actual]
                labels = [native_success(env.unwrapped)]
                actions, decisions = [], []
                feedback = FeedbackWithDelay(compensate=(route == 'velocity_feedback'))
                for t in range(EPISODE_STEPS):
                    action, phase = feedback.action(truth[-1] if route == 'clean_feedback' else states[-1])
                    env.step(action)
                    measured, actual = sensor.read()
                    states.append(measured)
                    truth.append(actual)
                    labels.append(native_success(env.unwrapped))
                    actions.append(action)
                    decisions.append(dict(t=t, phase=phase, latency_ms=0.))
                results.append(save_episode(out, f'{seed}_{route}_smoke', states, truth,
                                            actions, labels, decisions, meta))
        env.close()
        write(out / 'smoke.json', dict(records=results))
        for route in ('delayed_feedback', 'velocity_feedback', 'clean_feedback'):
            rows = [r for r in results if r['route'] == route]
            print('smoke_success', route, sum(r['native_success'] for r in rows), len(rows), flush=True)
    elif args.stage == 'collect':
        collect(out)
    elif args.stage == 'fit':
        fit(ROOT / args.data, out)
    elif args.stage == 'evaluate':
        evaluate(ROOT / args.models, out, args.seed_start, args.seed_count)
    else:
        verify(ROOT / args.data, ROOT / args.models, ROOT / args.evaluation, out)


if __name__ == '__main__':
    main()
