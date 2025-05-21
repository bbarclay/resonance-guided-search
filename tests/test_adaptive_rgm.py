import unittest
import numpy as np
import sys
import os
from typing import Callable, Tuple, List

# Adjust sys.path to find the src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rgs_pathfinding import adaptive_rgm_a_star, manhattan_distance
from src.rgs_core import rgm_distance # For potential direct testing if needed, though not used in final version

class TestAdaptiveDResLogic(unittest.TestCase):
    """
    Tests the d_res interpolation logic within the adaptive_rgm_a_star function.
    Since the actual distance function is nested, we replicate the d_res calculation
    logic here for direct testing.
    """
    def test_d_res_interpolation(self):
        d_res_far = 5.0
        d_res_near = 80.0

        # Case 1: h_ratio = 0.0 (at goal)
        h_ratio_goal = 0.0
        calc_d_res_goal = d_res_far * h_ratio_goal + d_res_near * (1.0 - h_ratio_goal)
        self.assertAlmostEqual(calc_d_res_goal, d_res_near, 
                               msg="d_res should be d_res_near when h_ratio is 0.0")

        # Case 2: h_ratio = 1.0 (at start or furthest point)
        h_ratio_start = 1.0
        calc_d_res_start = d_res_far * h_ratio_start + d_res_near * (1.0 - h_ratio_start)
        self.assertAlmostEqual(calc_d_res_start, d_res_far,
                               msg="d_res should be d_res_far when h_ratio is 1.0")

        # Case 3: h_ratio = 0.5 (mid-way)
        h_ratio_mid = 0.5
        calc_d_res_mid = d_res_far * h_ratio_mid + d_res_near * (1.0 - h_ratio_mid)
        expected_d_res_mid = (d_res_far + d_res_near) / 2.0
        self.assertAlmostEqual(calc_d_res_mid, expected_d_res_mid,
                               msg="d_res should be the average when h_ratio is 0.5")
        
        # Case 4: h_ratio clamped (e.g., > 1.0, should be treated as 1.0 for d_res calc if not clamped prior)
        # The adaptive_rgm_a_star clamps h_ratio to min(1.0, h_current / h_start)
        # So we test with h_ratio = 1.0 as the effective maximum for this calculation part.
        # If h_current > h_start, h_ratio becomes 1.0 due to clamping in adaptive_rgm_a_star
        h_ratio_clamped_high = 1.0 # Simulating clamped ratio
        calc_d_res_clamped_high = d_res_far * h_ratio_clamped_high + d_res_near * (1.0 - h_ratio_clamped_high)
        self.assertAlmostEqual(calc_d_res_clamped_high, d_res_far,
                               msg="d_res should be d_res_far when h_ratio is effectively 1.0 (clamped)")

        # Case 5: h_ratio between 0 and 0.5
        h_ratio_low_mid = 0.25
        calc_d_res_low_mid = d_res_far * h_ratio_low_mid + d_res_near * (1.0 - h_ratio_low_mid)
        expected_d_res_low_mid = d_res_far * 0.25 + d_res_near * 0.75
        self.assertAlmostEqual(calc_d_res_low_mid, expected_d_res_low_mid,
                               msg="d_res interpolation failed for h_ratio = 0.25")

        # Case 6: h_ratio between 0.5 and 1.0
        h_ratio_high_mid = 0.75
        calc_d_res_high_mid = d_res_far * h_ratio_high_mid + d_res_near * (1.0 - h_ratio_high_mid)
        expected_d_res_high_mid = d_res_far * 0.75 + d_res_near * 0.25
        self.assertAlmostEqual(calc_d_res_high_mid, expected_d_res_high_mid,
                               msg="d_res interpolation failed for h_ratio = 0.75")


class TestAdaptiveRGMPathfinding(unittest.TestCase):
    def setUp(self):
        self.grid_size = (5, 5)
        self.N_ord = [1, 2, 3]
        self.d_res_far = 5.0
        self.d_res_near = 20.0
        self.w = 2.0
        self.x0 = 0.0
        # A simple grid_to_x_map for testing purposes
        self.grid_to_x_map = lambda r, c: (float(r) / self.grid_size[0] + float(c) / self.grid_size[1]) / 2.0

    def test_adaptive_rgm_a_star_runs(self):
        start = (0, 0)
        goal = (4, 4)
        
        path = adaptive_rgm_a_star(
            grid_size=self.grid_size,
            start=start,
            goal=goal,
            grid_to_x_map=self.grid_to_x_map,
            N_ord=self.N_ord,
            d_res_far=self.d_res_far,
            d_res_near=self.d_res_near,
            w=self.w,
            x0=self.x0
            # Using default manhattan_distance heuristic
        )
        
        self.assertIsNotNone(path, "Path should not be None")
        self.assertTrue(len(path) > 0, "Path should not be empty")
        self.assertEqual(path[0], start, "Path should start at the start node")
        self.assertEqual(path[-1], goal, "Path should end at the goal node")

    def test_adaptive_rgm_a_star_start_is_goal(self):
        start = (2, 2)
        goal = (2, 2) # Start is the same as goal
        
        path = adaptive_rgm_a_star(
            grid_size=self.grid_size,
            start=start,
            goal=goal,
            grid_to_x_map=self.grid_to_x_map,
            N_ord=self.N_ord,
            d_res_far=self.d_res_far,
            d_res_near=self.d_res_near,
            w=self.w,
            x0=self.x0
        )
        
        self.assertIsNotNone(path, "Path should not be None when start is goal")
        self.assertEqual(len(path), 1, "Path length should be 1 when start is goal")
        self.assertEqual(path[0], start, "Path should consist of only the start/goal node")

    def test_adaptive_rgm_a_star_no_path(self):
        # Create a scenario where no path is possible by making part of the grid unreachable
        # This is harder to guarantee with RGM as costs are complex.
        # A simpler check is a very large grid where goal is far.
        # For this unit test, we'll assume basic A* behavior: if goal is outside, it might return empty.
        # However, a_star_search as implemented will try until open_list is empty.
        # A true "no path" might involve obstacles, which are not part of this A* version.
        # This test is more of a sanity check that it terminates.
        grid_size_large = (2,2)
        start_large = (0,0)
        goal_large = (5,5) # Goal outside the small grid_size_large

        path = adaptive_rgm_a_star(
            grid_size=grid_size_large, # Small grid
            start=start_large,
            goal=goal_large,      # Goal outside grid
            grid_to_x_map=lambda r,c: (float(r)/2 + float(c)/2)/2.0,
            N_ord=self.N_ord,
            d_res_far=self.d_res_far,
            d_res_near=self.d_res_near
        )
        # The current a_star_search explores valid neighbors. If goal is outside, it won't be found.
        self.assertEqual(path, [], "Path should be empty if goal is unreachable/outside grid")

if __name__ == "__main__":
    unittest.main()
