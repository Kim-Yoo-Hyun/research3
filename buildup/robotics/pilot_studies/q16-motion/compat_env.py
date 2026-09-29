"""CPU collision-only PushT adapter for the demonstration's exact ManiSkill revision."""
import gymnasium as gym
import numpy as np
import sapien
import torch
from mani_skill.envs.tasks.tabletop.push_t import PushTEnv, WhiteTableSceneBuilder
from mani_skill.envs.tasks.tabletop.roll_ball import RollBallEnv
from mani_skill.envs.scene import ManiSkillScene
from mani_skill.utils.registration import register_env
from mani_skill.utils.scene_builder.table import TableSceneBuilder


def arr(value):
    return value.detach().cpu().numpy().copy()


class CPUWhiteTable(WhiteTableSceneBuilder):
    def build(self):
        # Match the source table/ground collision geometry without visual assets.
        builder = self.scene.create_actor_builder()
        builder.add_box_collision(
            pose=sapien.Pose(p=[0, 0, 0.9196429 / 2]),
            half_size=(2.418 / 2, 1.209 / 2, 0.9196429 / 2),
        )
        builder.initial_pose = sapien.Pose(
            p=[-0.12, 0, -0.9196429], q=[0.7071068, 0, 0, 0.7071068],
        )
        self.table = builder.build_kinematic(name='table-workspace')
        self.table_height = 0.9196429
        ground = self.scene.create_actor_builder()
        ground.add_plane_collision(sapien.Pose(
            p=[0, 0, -self.table_height], q=[0.7071068, 0, -0.7071068, 0]))
        ground.initial_pose = sapien.Pose()
        self.ground = ground.build_static(name='ground')
        self.scene_objects = [self.table, self.ground]


@register_env('Q16AuditPushT-v1', max_episode_steps=100)
class CPUPushT(PushTEnv):
    def _setup_scene(self):
        # Source revision always creates a Vulkan RenderSystem, even in state mode.
        # Keep its CPU PhysX system and scene wrapper, omitting only rendering.
        self._set_scene_config()
        system = sapien.physx.PhysxCpuSystem()
        self.scene = ManiSkillScene([sapien.Scene([system])],
                                    sim_config=self.sim_config, device=self.device,
                                    parallel_in_single_scene=self._parallel_in_single_scene)
        self.scene.px.timestep = 1.0 / self._sim_freq

    def _setup_sensors(self, options):
        self._sensors = {}
        self._human_render_cameras = {}
        self.scene.sensors = self._sensors
        self.scene.human_render_cameras = self._human_render_cameras

    def _load_lighting(self, options):
        pass

    def _load_scene(self, options):
        self.ee_starting_pos2D = self.ee_starting_pos2D.to(self.device)
        self.ee_starting_pos3D = self.ee_starting_pos3D.to(self.device)
        self.table_scene = CPUWhiteTable(self, robot_init_qpos_noise=self.robot_init_qpos_noise)
        self.table_scene.build()

        # Exact native two-box collision geometry and material; no visual actors.
        builder = self.scene.create_actor_builder()
        builder._mass = self.T_mass
        material = sapien.physx.PhysxMaterial(self.T_dynamic_friction, self.T_static_friction, 0.0)
        builder.add_box_collision(pose=sapien.Pose([0, -0.0375, 0]),
                                  half_size=[0.1, 0.025, 0.02], material=material)
        builder.add_box_collision(pose=sapien.Pose([0, 0.1 - 0.0375, 0]),
                                  half_size=[0.025, 0.075, 0.02], material=material)
        builder.initial_pose = sapien.Pose(p=[0, 0, 0.1])
        self.tee = builder.build(name='Tee')
        goal = self.scene.create_actor_builder()
        goal.initial_pose = sapien.Pose(p=[0, 0, 0.1])
        self.goal_tee = goal.build_kinematic(name='goal_Tee')
        ee_goal = self.scene.create_actor_builder()
        ee_goal.initial_pose = sapien.Pose(p=[0, 0, 0.1])
        self.ee_goal_pos = ee_goal.build_kinematic(name='goal_ee')

        # Copy pinned task's torch-only pseudo-render grid and goal transform.
        res, half_width = 64, 0.15
        self.res, self.uv_half_width = res, half_width
        line = torch.arange(res, dtype=torch.float32).view(1, res).repeat(res, 1) - res / 2
        self.uv_grid = ((torch.cat([line.unsqueeze(0), (-line.T).unsqueeze(0)], 0) + 0.5)
                        / ((res / 2) / half_width)).to(self.device)
        self.homo_uv = torch.cat([self.uv_grid, torch.ones_like(self.uv_grid[0])[None]], 0)
        self.center_of_mass = (0, 0.0375)
        box1 = torch.tensor([[-0.1, 0.025], [0.1, 0.025], [-0.1, -0.025], [0.1, -0.025]])
        box2 = torch.tensor([[-0.025, 0.175], [0.025, 0.175], [-0.025, 0.025], [0.025, 0.025]])
        for box in (box1, box2):
            box[:, 1] -= self.center_of_mass[1]
            box *= (res / 2) / half_width
            box += res / 2
        box1, box2 = box1.long(), box2.long()
        self.tee_render = torch.zeros(res, res)
        self.tee_render.T[box1[0, 0]:box1[1, 0], box1[2, 1]:box1[0, 1]] = 1
        self.tee_render.T[box2[0, 0]:box2[1, 0], box2[2, 1]:box2[0, 1]] = 1
        self.tee_render = self.tee_render.flip(0).to(self.device)
        q_goal = torch.tensor([[np.cos(self.goal_z_rot / 2), 0, 0,
                                np.sin(self.goal_z_rot / 2)]], dtype=torch.float32)
        zrot = self.quat_to_zrot(q_goal)[0]
        goal_trans = torch.eye(3)
        goal_trans[:2, :2] = zrot[:2, :2]
        goal_trans[:2, 2] = self.goal_offset
        self.world_to_goal_trans = torch.linalg.inv(goal_trans).to(self.device)


@register_env('Q16AuditPushTGpu-v1', max_episode_steps=100)
class GPUPushT(CPUPushT):
    def _setup_scene(self):
        # The demonstration uses PhysX CUDA. Only visualization is omitted.
        self._set_scene_config()
        system = sapien.physx.PhysxGpuSystem(device=self._sim_device)
        self.scene = ManiSkillScene([sapien.Scene([system])],
                                    sim_config=self.sim_config, device=self.device,
                                    parallel_in_single_scene=self._parallel_in_single_scene)
        self.scene.px.timestep = 1.0 / self._sim_freq


@register_env('Q16AuditRollBall-v1', max_episode_steps=80)
class CPURollBall(RollBallEnv):
    def _load_scene(self, options):
        self.table_scene = TableSceneBuilder(self, robot_init_qpos_noise=0)
        self.table_scene.build()
        builder = self.scene.create_actor_builder()
        builder.add_sphere_collision(radius=self.ball_radius)
        builder.initial_pose = sapien.Pose(p=[0, 0, 0.1])
        self.ball = builder.build(name='ball')
        goal = self.scene.create_actor_builder()
        goal.initial_pose = sapien.Pose(p=[0, 0, 0.1])
        self.goal_region = goal.build_kinematic(name='goal_region')
        self.reached_status = torch.zeros(self.num_envs, dtype=torch.float32)


def make_env(task, device='cpu', obs_mode='none', native=False):
    if native:
        assert task == 'push_t' and device == 'gpu'
        return gym.make('PushT-v1', num_envs=1, obs_mode=obs_mode,
                        reward_mode='none', control_mode='pd_ee_delta_pos',
                        sim_backend='physx_cuda', render_backend='sapien_cuda')
    uid = {'push_t': 'Q16AuditPushTGpu-v1' if device == 'gpu' else 'Q16AuditPushT-v1',
           'roll_ball': 'Q16AuditRollBall-v1'}[task]
    return gym.make(uid, num_envs=1, obs_mode=obs_mode, reward_mode='none',
                    control_mode='pd_ee_delta_pos',
                    sim_backend='physx_cuda' if device == 'gpu' else 'physx_cpu',
                    render_backend='sapien_cuda' if device == 'gpu' else 'sapien_cpu',
                    sim_config=dict(sim_freq=100, control_freq=20))


def observe(env, task):
    e = env.unwrapped
    actor = e.tee if task == 'push_t' else e.ball
    target = e.goal_tee if task == 'push_t' else e.goal_region
    return dict(object=arr(actor.pose.raw_pose)[0], goal=arr(target.pose.raw_pose)[0],
                velocity=arr(actor.linear_velocity)[0], tcp=arr(e.agent.tcp.pose.raw_pose)[0],
                qpos=arr(e.agent.robot.qpos)[0])


def native_metric(env, task):
    e = env.unwrapped
    if task == 'push_t':
        value = float(e.pseudo_render_intersection().item())
        return value, bool(e.evaluate()['success'].item())
    ball, target = e.ball.pose.p[0, :2], e.goal_region.pose.p[0, :2]
    value = float(torch.linalg.norm(ball - target).item())
    return value, bool(e.evaluate()['success'].item())
