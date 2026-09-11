"""Scientific invariants for threshold fitting and temporal extraction; Docker only."""
import tempfile
import unittest
from pathlib import Path

import h5py
import numpy as np

from baselines import features_for_segment, fit_tree, metrics, predict, decision_for


class BaselineTests(unittest.TestCase):
    def test_balanced_tree_detects_minority_and_probability_is_separate(self):
        x = np.array([[0.]] * 90 + [[1.]] * 10)
        y = np.array([True] * 90 + [False] * 10)
        tree = fit_tree(x, y, ["f"], 2)
        model = {"tree": tree}
        self.assertEqual(predict(model, {"features": {"f": 0}})[0], True)
        self.assertEqual(predict(model, {"features": {"f": 1}})[0], False)
        self.assertAlmostEqual(tree["threshold"], .5)
        self.assertEqual(tree["right"]["n"], 10)

    def test_min_leaf_blocks_isolation_of_rare_row(self):
        x = np.array([[0.]] * 9 + [[1.]])
        tree = fit_tree(x, np.array([True] * 9 + [False]), ["f"], 2)
        self.assertNotIn("feature", tree)

    def test_metric_imbalance_and_calibration(self):
        result = metrics([True] * 9 + [False], [True] * 10, [.9] * 10)
        self.assertEqual(result["balanced_accuracy"], .5)
        self.assertEqual(result["failure_recall"], 0)
        self.assertAlmostEqual(result["brier"], .09)
        self.assertAlmostEqual(result["ece_5"], 0)

    def test_segment_endpoint_future_exclusion_and_quaternion_sign(self):
        with tempfile.TemporaryDirectory() as directory:
            with h5py.File(Path(directory) / "fixture.h5", "w") as handle:
                data = {
                    "pose": [[0, 0, 0, 1, 0, 0, 0], [1, 0, 0, -1, 0, 0, 0], [999, 0, 0, 1, 0, 0, 0]],
                    "gripper_positions": [[0, 0], [1, 2], [999, 999]],
                    "measured_force": [[0, 0, 0], [3, 4, 0], [999, 999, 999]],
                    "compensated_base_force": [[0, 0, 0], [3, 4, 0], [999, 999, 999]],
                }
                for name, values in data.items():
                    handle[f"robot_state/{name}"] = np.array(values, float)
                    handle[f"timestamps/{name}"] = [0., 1., 2.]
                f = features_for_segment(handle, 0, 1)
                self.assertEqual(len(f), 33)
                self.assertEqual(f["pose_displacement"], 1)
                self.assertEqual(f["pose_rotation"], 0)
                self.assertEqual(f["measured_peak"], 5)
                self.assertEqual(f["measured_impulse"], 2.5)
                self.assertEqual(f["measured_duration_5"], 0)
                self.assertEqual(f["gripper_change_sum"], 3)
                with self.assertRaises(ValueError):
                    features_for_segment(handle, 3, 4)

    def test_practical_criterion_requires_each_action_failure_recall(self):
        selected = {"macro": {"balanced_accuracy": .9, "brier": .1}}
        for action in ("pick", "insert", "remove"):
            selected[action] = {"balanced_accuracy": .9, "failure_recall": .8}
        scores = {"selected": selected, "family_prior": {"macro": {"balanced_accuracy": .5, "brier": .1}}}
        uncertainty = {"valid": 1500, "intervals": {"gain": [.2, .5]}}
        self.assertEqual(decision_for(scores, uncertainty)[0], "SIMPLE_RULE_SUFFICIENT")
        selected["remove"]["failure_recall"] = .5
        self.assertEqual(decision_for(scores, uncertainty)[0], "RESIDUAL_REQUIRES_PROBE")


if __name__ == "__main__":
    unittest.main()
