"""Container-only, no retraining: 18 fresh-process conditions, 576 episodes."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

OUT = Path('/output')
INPUT = Path('/input')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def evaluate(variant, seed, route):
    import random
    from types import SimpleNamespace
    import gymnasium as gym
    import numpy as np
    import torch
    import task
    from common import array, configuration, official_ppo, snapshot, write_json

    started = time.monotonic()
    random.seed(2026091901); np.random.seed(2026091901); torch.manual_seed(2026091901)
    env = gym.make('Q15PickCube-v1', num_envs=32, obs_mode='state', control_mode='pd_joint_delta_pos',
                   sim_backend='physx_cuda', reward_mode='normalized_dense', render_mode=None,
                   reward_variant=variant, density_multiplier=1., friction_multiplier=1.)
    e = env.unwrapped
    obs, _ = env.reset(seed=2026091901)
    config = configuration(e)
    assert e.sim_freq == 100 and e.control_freq == 20 and e._sim_steps_per_control == 5
    controllers = e.agent.controller.controllers
    arm, gripper = controllers['arm'], controllers['gripper']
    assert arm.config.use_delta and not arm.config.use_target and arm.config.normalize_action
    assert arm.config.lower == -0.1 and arm.config.upper == 0.1
    assert not arm.config.interpolate and not gripper.config.interpolate and not gripper.config.use_delta
    assert array(arm.active_joint_indices).tolist() == list(range(7))
    assert array(gripper.active_joint_indices).tolist() == [7, 8]
    checkpoint = INPUT / 'fits' / f'{variant}_{seed}' / 'checkpoint_195.pt'
    meta = json.loads(checkpoint.with_suffix('.json').read_text())
    assert sha(checkpoint) == meta['sha256'] and meta['seed'] == seed and meta['reward_variant'] == variant
    policy = official_ppo().Agent(SimpleNamespace(single_observation_space=e.single_observation_space,
                                                 single_action_space=e.single_action_space)).to(e.device)
    policy.load_state_dict(torch.load(checkpoint, map_location=e.device, weights_only=True))
    policy.eval()
    records = {k: [v] for k, v in snapshot(e, obs).items()}

    def put(key, value):
        records.setdefault(key, []).append(array(value))

    latched = torch.zeros(32, dtype=torch.bool, device=e.device)
    q_hold = torch.zeros((32, 7), device=e.device)
    gripper_hold = torch.zeros(32, device=e.device)
    physical_steps = 0
    native_after = e._after_simulation_step

    def after():
        nonlocal physical_steps
        physical_steps += 1
        native_after()

    e._after_simulation_step = after
    native_set = e.agent.set_action

    def record_targets(action):
        native_set(action)
        buffer = e.agent.robot.get_drive_targets()
        for key, controller in controllers.items():
            assert torch.equal(buffer[:, controller.active_joint_indices], controller._target_qpos)
            put('target_' + key, controller._target_qpos)
        put('target_buffer', buffer)

    e.agent.set_action = record_targets
    with torch.inference_mode():
        for step in range(50):
            policy_action = policy.get_action(obs, deterministic=True)
            policy_action = torch.clamp(policy_action, torch.as_tensor(e.single_action_space.low, device=e.device),
                                        torch.as_tensor(e.single_action_space.high, device=e.device))
            action = policy_action.clone()
            active = latched.clone() if route == 'hold' else torch.zeros_like(latched)
            if active.any():
                action[active, :7] = torch.clamp((q_hold[active] - e.agent.robot.qpos[active, :7]) / 0.1, -1, 1)
                action[active, 7] = gripper_hold[active]
            for key, value in dict(policy_action=policy_action, action=action, active=active,
                                   q_hold=q_hold, gripper_hold=gripper_hold).items():
                put(key, value)
            obs, reward, terminated, truncated, info = env.step(action)
            for key, value in snapshot(e, obs).items():
                records[key].append(value)
            for key in ['success', 'is_obj_placed', 'is_robot_static', 'is_grasped']:
                put(key, info[key])
            for key, value in dict(reward=reward, terminated=terminated, truncated=truncated,
                                   elapsed_steps=e.elapsed_steps).items():
                put(key, value)
            newly = info['success'] & ~latched
            q_hold[newly] = e.agent.robot.qpos[newly, :7]
            gripper_hold[newly] = action[newly, 7]
            latched |= newly
            assert physical_steps == (step + 1) * 5
    name = f'{variant}_{seed}_{route}'
    path = OUT / 'evaluation' / name
    assert not path.with_suffix('.npz').exists()
    np.savez_compressed(path.with_suffix('.npz'), **{k: np.stack(v) for k, v in records.items()})
    write_json(path.with_suffix('.json'), dict(variant=variant, training_seed=seed, route=route,
               seed=2026091901, num_envs=32, steps=50, physical_steps=physical_steps, config=config,
               checkpoint=str(checkpoint), checkpoint_sha256=sha(checkpoint),
               trace_sha256=sha(path.with_suffix('.npz')), seconds=time.monotonic() - started,
               cuda_peak_bytes=torch.cuda.max_memory_allocated()))
    print(name, 'end', int(array(info['success']).sum()), flush=True)
    env.close()


def run():
    assert not (OUT / 'run_status.json').exists(), 'Fresh output required'
    for folder in ['source', 'evaluation']:
        (OUT / folder).mkdir()
    for name in ['hold.py', 'hold_job.py', 'common.py', 'task.py', 'Dockerfile', 'requirements.lock']:
        shutil.copyfile(Path('/study') / name, OUT / 'source' / name)
    for name in ['installed.lock', 'os-packages.lock']:
        shutil.copyfile(Path('/recipe') / name, OUT / name)
    inputs = []
    for variant, seed in itertools.product(['native', 'no_grasp', 'half'], [101, 202, 303]):
        fit = INPUT / 'fits' / f'{variant}_{seed}'
        meta = json.loads((fit / 'checkpoint_195.json').read_text())
        assert meta['sha256'] == sha(fit / 'checkpoint_195.pt') and meta['update'] == 195
        for path in [fit / 'checkpoint_195.pt', fit / 'checkpoint_195.json', fit / 'config.json',
                     INPUT / 'evaluation' / f'{variant}_{seed}_u195_d1_f1.npz',
                     INPUT / 'evaluation' / f'{variant}_{seed}_u195_d1_f1.json']:
            inputs.append(dict(path=str(path.relative_to(INPUT)), sha256=sha(path), bytes=path.stat().st_size))
    save(OUT / 'inputs.json', inputs)
    status = dict(status='running', exploratory=True, training=False, evaluation=[], reset_seed=2026091901)
    save(OUT / 'run_status.json', status)
    start = time.monotonic()
    try:
        for variant, seed, route in itertools.product(['native', 'no_grasp', 'half'], [101, 202, 303], ['continued', 'hold']):
            name = f'{variant}_{seed}_{route}'
            command = [sys.executable, '-B', '-u', str(OUT / 'source/hold.py'),
                       '--variant', variant, '--seed', str(seed), '--route', route]
            # Execute archived helpers so the trace has immutable implementation provenance.
            with (OUT / 'evaluation' / f'{name}.log').open('x') as stream:
                result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT,
                                        timeout=min(180, 900 - (time.monotonic() - start)))
            status['evaluation'].append(dict(name=name, command=command, exit=result.returncode))
            save(OUT / 'run_status.json', status)
            assert result.returncode == 0, name
            print('EVALUATED', name, flush=True)
        status['status'] = 'completed'
    except BaseException as error:
        status.update(status='failed', error=repr(error))
        raise
    finally:
        status['seconds'] = time.monotonic() - start
        save(OUT / 'run_status.json', status)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--variant', choices=['native', 'no_grasp', 'half'])
    parser.add_argument('--seed', type=int)
    parser.add_argument('--route', choices=['continued', 'hold'])
    args = parser.parse_args()
    if args.route:
        evaluate(args.variant, args.seed, args.route)
    else:
        run()
