"""Collision-only rendering variant of pinned native PushCube-v1. Container-only."""
import gymnasium as gym
import numpy as np
import sapien
from mani_skill.envs.tasks.tabletop.push_cube import PushCubeEnv
from mani_skill.utils.registration import register_env
from mani_skill.utils.scene_builder.table import TableSceneBuilder

DT = 0.05
EPISODE_STEPS = 50


def arr(x):
    return x.detach().cpu().numpy().copy()


@register_env('Q16PushCube-v1', max_episode_steps=50)
class PushCubeNoRender(PushCubeEnv):
    def _load_scene(self, options):
        # Keep native reset/evaluate/control. Omit visual meshes/materials for CPU PhysX.
        self.table_scene = TableSceneBuilder(self, robot_init_qpos_noise=0)
        self.table_scene.build()
        builder = self.scene.create_actor_builder()
        builder.add_box_collision(half_size=[self.cube_half_size] * 3)
        builder.initial_pose = sapien.Pose(p=[0, 0, self.cube_half_size])
        self.obj = builder.build(name='cube')
        goal = self.scene.create_actor_builder()
        goal.initial_pose = sapien.Pose(p=[0, 0, 1e-3])
        self.goal_region = goal.build_kinematic(name='goal_region')
        self._hidden_objects.append(self.goal_region)


def make_env():
    return gym.make('Q16PushCube-v1', num_envs=1, obs_mode='none', reward_mode='none',
                    control_mode='pd_ee_delta_pos', robot_init_qpos_noise=0,
                    sim_backend='physx_cpu', render_backend='none',
                    sim_config=dict(sim_freq=200, control_freq=20))


def observe(e):
    return dict(cube=arr(e.obj.pose.raw_pose)[0], velocity=arr(e.obj.linear_velocity)[0],
                omega=arr(e.obj.angular_velocity)[0], tcp=arr(e.agent.tcp.pose.raw_pose)[0],
                qpos=arr(e.agent.robot.qpos)[0], qvel=arr(e.agent.robot.qvel)[0],
                goal=arr(e.goal_region.pose.p)[0])


def native_success(e):
    return bool(e.evaluate()['success'].item())


def set_friction(env, value):
    e = env.unwrapped
    for actor in (e.obj, e.table_scene.table):
        for body in actor._bodies:
            for shape in body.collision_shapes:
                shape.physical_material = sapien.physx.PhysxMaterial(value, value, 0.0)


class Feedback:
    def __init__(self):
        self.phase = 'approach'

    def action(self, o):
        cube, tcp, goal = o['cube'][:3], o['tcp'][:3], o['goal']
        behind = cube + np.array([-0.06, 0., 0.035], np.float32)
        if (self.phase == 'approach' and tcp[0] <= cube[0] - 0.045
                and abs(tcp[1] - cube[1]) <= 0.018 and tcp[2] <= cube[2] + 0.05):
            self.phase = 'push'
        if self.phase == 'approach':
            target = behind
        else:
            target = np.array([goal[0] - 0.07, goal[1], cube[2] + 0.006], np.float32)
        action = np.r_[np.clip((target - tcp) / 0.1, -0.25, 0.25), -1.].astype(np.float32)
        return action, self.phase
