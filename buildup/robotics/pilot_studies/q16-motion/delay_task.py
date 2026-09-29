"""Deterministic delayed object measurements for Q16; run only in Docker."""
import numpy as np
from push_task import observe, Feedback, DT

LAG_STEPS = 4
LAG_SECONDS = DT * LAG_STEPS


class Sensor:
    def __init__(self, env):
        self.env = env
        self.history = []

    def read(self):
        truth = observe(self.env.unwrapped)
        self.history.append(truth)
        late = self.history[max(0, len(self.history) - LAG_STEPS - 1)]
        measured = dict(truth)
        for key in ('cube', 'velocity', 'omega'):
            measured[key] = late[key].copy()
        return measured, truth


class FeedbackWithDelay:
    def __init__(self, compensate=False):
        self.controller = Feedback()
        self.compensate = compensate

    def action(self, measured):
        if self.compensate:
            estimate = dict(measured)
            pose = measured['cube'].copy()
            pose[:2] += measured['velocity'][:2] * LAG_SECONDS
            estimate['cube'] = pose
            return self.controller.action(estimate)
        return self.controller.action(measured)


def vector(o):
    return np.concatenate([o[k] for k in ('cube', 'velocity', 'omega', 'tcp', 'qpos', 'qvel', 'goal')]).astype(np.float32)
