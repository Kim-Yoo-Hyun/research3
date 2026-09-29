"""Constructed state-based dynamic grasp task. Container-only execution."""
import numpy as np
import sapien
import torch
import gymnasium as gym
from mani_skill.envs.tasks.tabletop.pick_cube import PickCubeEnv
from mani_skill.utils.registration import register_env
from mani_skill.utils.scene_builder.table import TableSceneBuilder

DT = 0.05
HORIZON = 2
STEPS = 80
GOAL = np.array([0.08, -0.08, 0.16], np.float32)


def arr(x):
    return x.detach().cpu().numpy().copy()


@register_env('Q16DynamicCube-v1', max_episode_steps=200)
class DynamicCube(PickCubeEnv):
    def _load_scene(self, options):
        # Native build_cube constructs a RenderMaterial even with render_backend='none'.
        # Collision-only construction keeps this CPU study independent of a render device.
        self.table_scene = TableSceneBuilder(self, robot_init_qpos_noise=0)
        self.table_scene.build()
        builder = self.scene.create_actor_builder()
        builder.add_box_collision(half_size=[self.cube_half_size]*3)
        builder.initial_pose = sapien.Pose(p=[0,0,self.cube_half_size])
        self.cube = builder.build(name='cube')
        goal = self.scene.create_actor_builder()
        goal.initial_pose = sapien.Pose(p=GOAL)
        self.goal_site = goal.build_kinematic(name='goal_site')
        self._hidden_objects.append(self.goal_site)
        # Low table/cube friction preserves the initial slide long enough to intercept.
        # Finger material is unchanged (Panda native high friction); never overwrite pose in rollout.
        for actor in (self.cube, self.table_scene.table):
            for body in actor._bodies:
                for shape in body.collision_shapes:
                    shape.physical_material = sapien.physx.PhysxMaterial(0.01, 0.01, 0.0)


def make_env():
    return gym.make('Q16DynamicCube-v1', num_envs=1, obs_mode='none', reward_mode='none',
                    control_mode='pd_ee_delta_pos', robot_init_qpos_noise=0,
                    sim_backend='physx_cpu', render_backend='none',
                    sim_config=dict(sim_freq=200, control_freq=20))


def observe(e):
    # No evaluate() output, contact sensor or native is_grasped observation enters this record.
    return dict(cube=arr(e.cube.pose.raw_pose)[0], velocity=arr(e.cube.linear_velocity)[0],
                omega=arr(e.cube.angular_velocity)[0], tcp=arr(e.agent.tcp.pose.raw_pose)[0],
                qpos=arr(e.agent.robot.qpos)[0], qvel=arr(e.agent.robot.qvel)[0])


def features(o, prev):
    return np.concatenate([o['cube'], o['velocity'], o['omega'], o['tcp']-o['cube'],
                           o['qpos'], o['qvel'], (o['cube'][:3]-prev['cube'][:3])/(DT*HORIZON)]).astype(np.float32)


def labels(e):
    p = arr(e.cube.pose.p)[0]
    grasp = bool(e.agent.is_grasping(e.cube).item())
    links = [e.agent.finger1_link, e.agent.finger2_link]
    forces = np.stack([arr(e.scene.get_pairwise_contact_forces(link,e.cube))[0] for link in links])
    directions = np.stack([arr(link.pose.to_transformation_matrix())[0,:3,1]*sign for link,sign in zip(links,[1,-1])])
    return dict(grasp=grasp, success=bool(grasp and np.linalg.norm(p-GOAL) <= 0.025),
                goal_distance=float(np.linalg.norm(p-GOAL)),forces=forces,directions=directions)


def initialize(env, seed, moving):
    env.reset(seed=seed)
    e = env.unwrapped
    # Reproducible fresh preparation, then a single initial-state assignment before t=0.
    start = np.array([-0.025, 0., 0.115])
    for _ in range(24):
        tcp = arr(e.agent.tcp.pose.p)[0]
        a = np.r_[np.clip((start-tcp)/0.1, -0.25, 0.25), 1.].astype(np.float32)
        env.step(a)
    rng = np.random.default_rng(seed)
    pos = np.r_[rng.uniform(-0.035, 0.035, 2), 0.021]
    speed = rng.uniform(0.10, 0.18)
    angle = rng.uniform(-np.pi, np.pi)
    vel = np.array([np.cos(angle)*speed, np.sin(angle)*speed, 0.]) if moving else np.zeros(3)
    e.cube.set_pose(sapien.Pose(p=pos))
    e.cube.set_linear_velocity(vel.astype(np.float32))
    e.cube.set_angular_velocity(np.zeros(3, np.float32))
    e.goal_site.set_pose(sapien.Pose(p=GOAL))
    return dict(seed=seed, moving=bool(moving), initial_position=pos.tolist(), initial_velocity=vel.tolist(),
                start_tcp=arr(e.agent.tcp.pose.p)[0].tolist())


class Controller:
    def __init__(self, mode='servo', predictor=None):
        self.mode = mode
        self.predictor = predictor
        self.phase = 0  # above, descend, close, transport
        self.closed_steps = 0

    def action(self, o, prev, hold=HORIZON):
        obj, tcp = o['cube'][:3], o['tcp'][:3]
        xy = np.linalg.norm(tcp[:2]-obj[:2])
        if self.phase == 0 and xy < 0.016 and tcp[2] < 0.086:
            self.phase = 1
        if self.phase == 1 and xy < 0.023 and tcp[2] < 0.033:
            self.phase = 2
        if self.phase == 2:
            # Six completed control steps of closing, independent of decision cadence.
            # This preserves the original hold=2 trajectory and matches fast hold=1.
            if self.closed_steps >= 6:
                self.phase = 3
            else:
                self.closed_steps += hold
        if self.phase == 3:
            # Keep the object-to-TCP offset, but do not use the grasp oracle.
            target = GOAL + (tcp-obj) if obj[2] > 0.055 else np.r_[tcp[:2], 0.17]
            if obj[2] > 0.055:
                target = np.clip(target, [-0.3,-0.3,0.06], [0.3,0.3,0.3])
        else:
            target = obj.copy()
            if self.mode != 'servo':
                target[:2] += o['velocity'][:2] * (DT*HORIZON)
            target[2] = 0.075 if self.phase == 0 else 0.024
        grip = -1. if self.phase >= 2 else 1.
        base = np.r_[np.clip((target-tcp)/0.1, -0.25, 0.25), grip].astype(np.float32)
        candidates = np.tile(base, (9,1))
        offsets = np.array([(x,y) for x in [-0.06,0,0.06] for y in [-0.06,0,0.06]])
        candidates[:,:2] = np.clip(candidates[:,:2]+offsets, -0.25, 0.25)
        if self.predictor is None or self.phase == 3:
            return base, dict(phase=self.phase, selected=4)
        f = features(o,prev)
        delta = self.predictor.predict(f, candidates)
        predicted = obj[None,:] + delta
        # Shared short-horizon position cost. Actual low-level control integrates repeated deltas.
        future_tcp = tcp[None,:] + candidates[:,:3] * (0.1*HORIZON)
        costs = ((future_tcp[:,:2]-predicted[:,:2])**2).sum(1) + 0.02*((candidates-base)**2).sum(1)
        i = int(np.argmin(costs))
        return candidates[i], dict(phase=self.phase, selected=i, predictions=delta.tolist(), costs=costs.tolist())
