import unittest
import numpy as np
import sys
import os

# Adjust sys.path to find the src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rgs_core import adaptability_2d, rgm_distance_2d, coupling_function_2d
from src.rgs_pathfinding import rgm_a_star_2d, manhattan_distance

class TestAdaptability2D(unittest.TestCase):
    def test_adaptability_2d_bounds(self):
        pos_values = [(0.0, 0.0), (0.5, 0.5), (0.2, 0.8)]
        d_res_values = [1.0, 10.0]
        N_ord_sets = [[1,2,3], [1,3,5,7]]
        x0_vec_values = [(0.0,0.0), (0.1, 0.2)]

        for pos in pos_values:
            for d_res in d_res_values:
                for N_ord in N_ord_sets:
                    for x0_vec in x0_vec_values:
                        result = adaptability_2d(pos, d_res, N_ord, x0_vec)
                        self.assertTrue(0 <= result <= 1, f"Adaptability out of bounds: {result} for {pos}, {d_res}, {N_ord}, {x0_vec}")

    def test_adaptability_2d_symmetry_components(self):
        pos = (0.2, 0.7)
        d_res = 5.0
        N_ord = [1,2,3]
        
        a1 = adaptability_2d(pos, d_res, N_ord, x0_vec=(0.0, 0.1))
        a2 = adaptability_2d((pos[1], pos[0]), d_res, N_ord, x0_vec=(0.1, 0.0))
        
        self.assertAlmostEqual(a1, a2, msg="Adaptability component symmetry failed.")

class TestRGM2DProperties(unittest.TestCase):
    def test_rgm_2d_non_negativity(self):
        pos_values = [(0.0, 0.0), (0.5, 0.5), (0.2, 0.8), (0.1, 0.9)]
        d_res_values = [1.0, 10.0]
        N_ord_sets = [[1,2,3], [1,3,5,7]]
        x0_vec_values = [(0.0,0.0), (0.1, 0.2)]
        
        for i in range(len(pos_values) -1):
            p1 = pos_values[i]
            p2 = pos_values[i+1]
            for d_res in d_res_values:
                for N_ord in N_ord_sets:
                    for x0_vec in x0_vec_values:
                        d_base = np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
                        result = rgm_distance_2d(p1, p2, d_res, N_ord, d_base, x0_vec=x0_vec)
                        self.assertTrue(result >= 0, f"RGM distance non-negative failed: {result} for {p1}, {p2}, {d_res}, {N_ord}, {x0_vec}")

    def test_rgm_2d_identity(self):
        pos_values = [(0.0, 0.0), (0.5, 0.5), (0.2, 0.8)]
        d_res_values = [1.0, 10.0]
        N_ord_sets = [[1,2,3], [1,3,5,7]]
        x0_vec_values = [(0.0,0.0), (0.1, 0.2)]

        for pos in pos_values:
            for d_res in d_res_values:
                for N_ord in N_ord_sets:
                    for x0_vec in x0_vec_values:
                        result = rgm_distance_2d(pos, pos, d_res, N_ord, 0.0, x0_vec=x0_vec)
                        self.assertAlmostEqual(result, 0.0, msg=f"RGM distance identity failed: {result} for {pos}, {d_res}, {N_ord}, {x0_vec}")

    def test_rgm_2d_symmetry(self):
        p1 = (0.1, 0.2)
        p2 = (0.8, 0.5)
        d_res_values = [1.0, 10.0]
        N_ord_sets = [[1,2,3], [1,3,5,7]]
        x0_vec_values = [(0.0,0.0), (0.1, 0.2)]
        
        d_base = np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

        for d_res in d_res_values:
            for N_ord in N_ord_sets:
                for x0_vec in x0_vec_values:
                    d12 = rgm_distance_2d(p1, p2, d_res, N_ord, d_base, x0_vec=x0_vec)
                    d21 = rgm_distance_2d(p2, p1, d_res, N_ord, d_base, x0_vec=x0_vec)
                    self.assertAlmostEqual(d12, d21, msg=f"RGM distance symmetry failed: {d12} vs {d21} for {d_res}, {N_ord}, {x0_vec}")

class TestRGMPathfinding2D(unittest.TestCase):
    def test_rgm_a_star_2d_runs(self):
        grid_size = (5, 5)
        start = (0,0)
        goal = (4,4)
        grid_to_xy_map = lambda r, c: (float(r)/grid_size[0], float(c)/grid_size[1])
        d_res = 5.0
        N_ord = [1,2,3]
        x0_vec = (0.0, 0.0)

        path = rgm_a_star_2d(grid_size, start, goal, grid_to_xy_map, d_res, N_ord, x0_vec=x0_vec)
        
        self.assertIsNotNone(path, "Path should not be None")
        self.assertTrue(len(path) > 0, "Path should not be empty")
        self.assertEqual(path[0], start, "Path should start at the start node")
        self.assertEqual(path[-1], goal, "Path should end at the goal node")

if __name__ == "__main__":
    unittest.main()
