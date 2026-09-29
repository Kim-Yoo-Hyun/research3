"""Reward intervention and actor-local physical changes; original evaluator/observations."""
import numpy as np
import sapien
import torch
from mani_skill.envs.tasks.tabletop.pick_cube import PickCubeEnv
from mani_skill.utils.registration import register_env
from common import array

@register_env('Q15PickCube-v1', max_episode_steps=50)
class RewardPickCube(PickCubeEnv):
    def __init__(self,*args,reward_variant='native',density_multiplier=1.0,friction_multiplier=1.0,**kwargs):
        assert reward_variant in ('native','no_grasp','half')
        self.reward_variant=reward_variant
        self.density_multiplier=float(density_multiplier)
        self.friction_multiplier=float(friction_multiplier)
        self.reward_calls=0
        self.audit_samples=[]
        super().__init__(*args,**kwargs)

    def _load_scene(self,options):
        super()._load_scene(options)
        # Native builder finishes before GPU initialization. Uniform density scales both inertia and mass.
        for body in self.cube._bodies:
            if self.density_multiplier != 1:
                inertia=np.asarray(body.inertia).copy()
                body.mass=float(body.mass)*self.density_multiplier
                body.inertia=inertia*self.density_multiplier
            if self.friction_multiplier != 1:
                for shape in body.collision_shapes:
                    m=shape.physical_material
                    # A fresh material avoids mutating shared table/robot materials.
                    replacement=sapien.physx.PhysxMaterial(
                        float(m.static_friction)*self.friction_multiplier,
                        float(m.dynamic_friction)*self.friction_multiplier,float(m.restitution))
                    shape.physical_material=replacement

    def compute_normalized_dense_reward(self,obs,action,info):
        native=super().compute_normalized_dense_reward(obs,action,info)
        if self.reward_variant=='no_grasp':
            reward=native - 0.2*info['is_grasped'].float()*(~info['success']).float()
        elif self.reward_variant=='half':
            reward=0.5*native
        else:
            reward=native
        self.reward_calls+=1
        if self.reward_calls in (1,2500,4850,9750):
            self.audit_samples.append(dict(call=self.reward_calls,
                cube=array(self.cube.pose.p[:16]),tcp=array(self.agent.tcp.pose.p[:16]),
                goal=array(self.goal_site.pose.p[:16]),qvel=array(self.agent.robot.qvel[:16]),
                native=array(native[:16]),reward=array(reward[:16]),
                **{k:array(info[k][:16]) for k in ['is_grasped','is_obj_placed','is_robot_static','success']}))
        return reward
