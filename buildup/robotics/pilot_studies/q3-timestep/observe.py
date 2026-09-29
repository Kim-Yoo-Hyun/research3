"""One fresh-process GPU condition; preserve the native step and GPU target apply path."""
import argparse
import dataclasses
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import sys
import time
from types import SimpleNamespace

import gymnasium as gym
import numpy as np
import torch
import mani_skill.envs


def array(x):
    return x.detach().cpu().numpy().copy()


def json_value(x):
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, np.generic):
        return x.item()
    if isinstance(x, torch.Tensor):
        return array(x).tolist()
    raise TypeError(type(x).__name__)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--frequency', type=int, choices=[100, 200, 400], required=True)
    parser.add_argument('--mode', choices=['closed', 'replay'], required=True)
    parser.add_argument('--repeat', type=int, choices=[0, 1], required=True)
    parser.add_argument('--attempt', required=True)
    args = parser.parse_args()
    out = Path('/output') / args.attempt
    name = f'{args.mode}_{args.frequency}_{args.repeat}'
    assert not (out / f'{name}.npz').exists(), 'Do not overwrite an earlier condition'
    torch.set_num_threads(1)
    random.seed(20260918)
    np.random.seed(20260918)
    torch.manual_seed(20260918)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    assert torch.cuda.is_available()
    checkpoint = Path('/inputs/ppo_pd_joint_delta_pos_ckpt.pt')
    expected = '78959417279892d73e4ed5930a6d8de8626a24eee0ec553dfc6af61391b0b356'
    assert sha(checkpoint) == expected
    source = Path('/opt/ManiSkill/examples/baselines/ppo/ppo.py')
    assert sha(source) == '3fa4818861d428480244aae889bc679b2c8e89b59d6289014003c266a84dbab0'
    spec = importlib.util.spec_from_file_location('official_ppo', source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    started = time.monotonic()
    env = gym.make('PickCube-v1', num_envs=8, robot_uids='panda', obs_mode='state',
                   control_mode='pd_joint_delta_pos', sim_backend='physx_cuda',
                   render_mode=None, sim_config={'sim_freq': args.frequency, 'control_freq': 20})
    e = env.unwrapped
    assert e.gpu_sim_enabled and e.control_freq == 20 and e.sim_freq == args.frequency
    assert e._sim_steps_per_control == args.frequency // 20
    policy = module.Agent(SimpleNamespace(single_observation_space=e.single_observation_space,
                                          single_action_space=e.single_action_space)).to(e.device)
    policy.load_state_dict(torch.load(checkpoint, map_location=e.device, weights_only=True))
    policy.eval()
    obs, _ = env.reset(seed=20260918)
    controllers = e.agent.controller.controllers
    assert set(controllers) == {'arm', 'gripper'}
    for c in controllers.values():
        assert not c.config.interpolate
    assert controllers['arm'].config.use_delta and not controllers['arm'].config.use_target
    assert not controllers['gripper'].config.use_delta
    reference_path = out / 'closed_100_0.npz'
    reference = np.load(reference_path) if name != 'closed_100_0' else None
    records = {}

    def put(key, value):
        records.setdefault(key, []).append(array(value))

    def snapshot(observation):
        for key, value in {'obs': observation, 'qpos': e.agent.robot.qpos,
                           'qvel': e.agent.robot.qvel, 'cube_pose': e.cube.pose.raw_pose,
                           'cube_velocity': e.cube.linear_velocity,
                           'cube_angular_velocity': e.cube.angular_velocity,
                           'goal': e.goal_site.pose.p}.items():
            put(key, value)
        for group, values in e.get_state_dict().items():
            for key, value in values.items():
                put(f'state/{group}/{key}', value)

    snapshot(obs)
    if reference is not None:
        for key, rows in records.items():
            assert np.array_equal(rows[0], reference[key][0]), f'Unmatched initial {key}'
    step = 0
    native_set = e.agent.set_action
    target_indices = {key: array(c.active_joint_indices).astype(int) for key, c in controllers.items()}

    def controlled_set(action):
        if args.mode == 'closed':
            native_set(action)
        else:
            # Keep native _step_action so gpu_apply_articulation_target_position is still called.
            for key, c in controllers.items():
                target = torch.as_tensor(reference[f'target/{key}'][step], device=e.device)
                c._step = 0
                c._start_qpos = c.qpos.clone()
                c._target_qpos = target.clone()
                c.set_drive_targets(c._target_qpos)
        buffer = e.agent.robot.get_drive_targets()
        for key, c in controllers.items():
            assert torch.equal(buffer[:, c.active_joint_indices], c._target_qpos)
            put(f'target/{key}', c._target_qpos)
        put('target/buffer', buffer)

    e.agent.set_action = controlled_set
    native_after = e._after_simulation_step
    physics_steps = 0

    def after_simulation():
        nonlocal physics_steps
        physics_steps += 1
        native_after()

    e._after_simulation_step = after_simulation
    with torch.inference_mode():
        for step in range(50):
            if args.mode == 'closed':
                action = policy.get_action(obs, deterministic=True)
            else:
                # Placeholder is intercepted above; it never sets native relative targets.
                action = torch.zeros((8, *e.single_action_space.shape), device=e.device)
            put('action', action)
            obs, reward, terminated, truncated, info = env.step(action)
            snapshot(obs)
            for key in ['success', 'is_obj_placed', 'is_robot_static', 'is_grasped']:
                put(f'official/{key}', info[key])
            put('terminated', terminated)
            put('truncated', truncated)
            put('elapsed_steps', e.elapsed_steps)
            for key, c in controllers.items():
                assert torch.equal(e.agent.robot.get_drive_targets()[:, c.active_joint_indices], c._target_qpos)
            assert physics_steps == (step + 1) * (args.frequency // 20)
    data = {key: np.stack(rows) for key, rows in records.items()}
    data['control_time'] = np.arange(51, dtype=np.float64) / 20
    data['physics_steps'] = np.arange(51, dtype=np.int64) * (args.frequency // 20)
    assert bool(data['truncated'][-1].all()) and not bool(data['truncated'][:-1].any())
    np.savez_compressed(out / f'{name}.npz', **data)
    metadata = dict(condition=name, mode=args.mode, frequency=args.frequency, repeat=args.repeat,
                    seed=20260918, environments=8, control_steps=50, control_frequency=20,
                    actual_physics_steps=physics_steps, actual_physics_timestep=float(e.scene.px.timestep),
                    sim_config=dataclasses.asdict(e.sim_config),
                    controller_configs={k: dataclasses.asdict(c.config) for k, c in controllers.items()},
                    target_indices=target_indices, cube_mass=[float(b.mass) for b in e.cube._bodies],
                    cube_half_size=float(e.cube_half_size), goal_threshold=float(e.goal_thresh),
                    robot_materials=e.agent.urdf_config, device=str(e.device), gpu=torch.cuda.get_device_name(),
                    torch_version=torch.__version__, source_commit='a4a4f9272ad64b1564035874b605ceb687b63ed8',
                    checkpoint_sha256=expected, official_ppo_sha256=sha(source),
                    trace_sha256=sha(out / f'{name}.npz'), seconds=time.monotonic() - started,
                    replay_reference='closed_100_0' if args.mode == 'replay' else None,
                    replay_action_field='intercepted zero placeholder' if args.mode == 'replay' else 'PPO mean')
    (out / f'{name}.json').write_text(json.dumps(metadata, indent=2, default=json_value) + '\n')
    print(json.dumps({'condition': name, 'success_at_end': data['official/success'][-1].tolist(),
                      'success_once': data['official/success'].any(axis=0).tolist(),
                      'seconds': metadata['seconds']}), flush=True)
    env.close()


if __name__ == '__main__':
    main()
