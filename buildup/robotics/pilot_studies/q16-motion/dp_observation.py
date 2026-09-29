"""Fixed Push-T geometry reconstructed only from visible policy keypoints."""
import numpy as np

from diffusion_policy.env.pusht.pusht_env import pymunk_to_shapely
from diffusion_policy.env.pusht.pusht_keypoints_env import PushTKeypointsEnv


def wrap(angle):
    return float(np.arctan2(np.sin(angle), np.cos(angle)))


class ObservationGeometry:
    def __init__(self):
        template = PushTKeypointsEnv(legacy=True, keypoint_visible_rate=1.0,
                                    agent_keypoints=False, render_action=False)
        try:
            template.seed(0)
            template.reset()
            self.local = np.asarray(template.kp_manager.local_keypoint_map['block'],
                                    np.float64).copy()
            self.shapes = tuple(template.block.shapes)
            self.goal = np.asarray(template.goal_pose,np.float64).copy()
            self.goal_geom = pymunk_to_shapely(
                template._get_goal_pose_body(self.goal),self.shapes)
            self.body_from_pose = template._get_goal_pose_body
            assert self.local.shape == (9,2)
        finally:
            template.close()

    def from_state(self, state):
        state=np.asarray(state,np.float64)
        angle=state[4]
        rot=np.asarray([[np.cos(angle),np.sin(angle)],
                        [-np.sin(angle),np.cos(angle)]])
        points=self.local@rot+state[2:4]
        return np.r_[points.flatten(),state[:2]]

    def decode(self, observation):
        observation=np.asarray(observation,np.float64)
        assert observation.shape in ((20,),(40,))
        if observation.shape==(40,):
            assert np.all(observation[20:]==1)
        points=observation[:18].reshape(9,2)
        local=self.local
        a=local-local.mean(0)
        b=points-points.mean(0)
        u,_,vt=np.linalg.svd(a.T@b)
        adjust=np.diag([1.,np.linalg.det(u@vt)])
        rot=u@adjust@vt
        center=points.mean(0)-local.mean(0)@rot
        angle=np.arctan2(rot[0,1],rot[0,0])%(2*np.pi)
        return np.r_[observation[18:20],center,angle]

    def overlap(self, state):
        state=np.asarray(state,np.float64)
        body=self.body_from_pose(state[2:5])
        geom=pymunk_to_shapely(body,self.shapes)
        return float(self.goal_geom.intersection(geom).area/self.goal_geom.area)


def feedback_target(state, limit=60.):
    state=np.asarray(state,np.float64)
    direction=np.asarray([256.,256.])-state[2:4]
    direction*=min(1.,limit/max(np.linalg.norm(direction),1e-12))
    return np.clip(state[:2]+direction,0.,512.)
