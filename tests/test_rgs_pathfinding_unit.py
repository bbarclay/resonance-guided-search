#!/usr/bin/env python
"""
Unit tests for rgs_pathfinding.py
"""

import os
import sys
import unittest
import numpy as np

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rgs_pathfinding import (
    Node,
    a_star_search,
    standard_a_star,
    rgm_a_star,
    manhattan_distance,
    rgm_grid_distance,
)
from src.rgs_core import adaptability  # Required for rgm_grid_distance via rgm_a_star


class TestNode(unittest.TestCase):
    """Tests for the Node class."""

    def test_node_creation(self):
        node = Node((0, 0))
        self.assertEqual(node.position, (0, 0))
        self.assertIsNone(node.parent)
        self.assertEqual(node.g, 0)
        self.assertEqual(node.h, 0)
        self.assertEqual(node.f, 0)

    def test_node_equality(self):
        node1 = Node((0, 0))
        node2 = Node((0, 0))
        node3 = Node((1, 0))
        self.assertEqual(node1, node2)
        self.assertNotEqual(node1, node3)

    def test_node_less_than(self):
        node1 = Node((0, 0))
        node1.f = 1
        node2 = Node((1, 0))
        node2.f = 2
        self.assertLess(node1, node2)

    def test_node_hash(self):
        node1 = Node((0, 0))
        node2 = Node((0, 0))
        s = {node1}
        self.assertIn(node2, s)


class TestManhattanDistance(unittest.TestCase):
    """Tests for the manhattan_distance function."""

    def test_manhattan_distance_calculation(self):
        self.assertEqual(manhattan_distance((0, 0), (2, 2)), 4)
        self.assertEqual(manhattan_distance((0, 0), (0, 0)), 0)
        self.assertEqual(manhattan_distance((1, 1), (4, 5)), 7)


class TestStandardAStar(unittest.TestCase):
    """Tests for the standard_a_star function."""

    def test_simple_path_found(self):
        grid_size = (3, 3)
        start = (0, 0)
        goal = (2, 2)
        path = standard_a_star(grid_size, start, goal)
        self.assertTrue(path, "Path should not be empty")
        # Expected path length can vary, but for 3x3 from (0,0) to (2,2) it's 5
        # e.g., (0,0)->(1,0)->(2,0)->(2,1)->(2,2) or (0,0)->(0,1)->(0,2)->(1,2)->(2,2) etc.
        self.assertEqual(len(path), 5, f"Path length was {len(path)}, expected 5. Path: {path}")
        self.assertEqual(path[0], start, "Path should start at the start node")
        self.assertEqual(path[-1], goal, "Path should end at the goal node")

    def test_start_equals_goal(self):
        grid_size = (3, 3)
        start = (1, 1)
        goal = (1, 1)
        path = standard_a_star(grid_size, start, goal)
        self.assertEqual(path, [(1, 1)], f"Path was {path}, expected [(1,1)]")

    def test_no_path_outside_grid(self):
        # Goal is outside the grid, a_star_search should return empty list
        grid_size = (3, 3)
        start = (0, 0)
        goal = (3, 3) # Outside 3x3 grid (max index is 2)
        path = standard_a_star(grid_size, start, goal)
        self.assertEqual(path, [], f"Path was {path}, expected []")

    def test_path_around_obstacle_implicit(self):
        # This test relies on the fact that a_star_search explores neighbors.
        # If we make a very narrow grid, it should still find the path.
        grid_size = (5, 1) # A tall, narrow grid
        start = (0, 0)
        goal = (4, 0)
        path = standard_a_star(grid_size, start, goal)
        self.assertEqual(len(path), 5) # (0,0)->(1,0)->(2,0)->(3,0)->(4,0)
        self.assertEqual(path, [(0,0), (1,0), (2,0), (3,0), (4,0)])


class TestRgmAStar(unittest.TestCase):
    """Tests for the rgm_a_star function."""

    def test_rgm_path_found_basic(self):
        grid_size = (3, 3)
        start = (0, 0)
        goal = (2, 2)
        grid_to_x_map = lambda r, c: (r + c) * 0.1  # Simple map
        d_res = 5.0
        N_ord = [1, 2, 3]

        path = rgm_a_star(
            grid_size=grid_size,
            start=start,
            goal=goal,
            grid_to_x_map=grid_to_x_map,
            d_res=d_res,
            N_ord=N_ord,
        )
        self.assertTrue(path, "RGM A* path should not be empty")
        self.assertEqual(path[0], start, "Path should start at the start node")
        self.assertEqual(path[-1], goal, "Path should end at the goal node")

        for i in range(len(path)):
            r, c = path[i]
            self.assertTrue(0 <= r < grid_size[0], f"Row {r} out of bounds for path element {path[i]}")
            self.assertTrue(0 <= c < grid_size[1], f"Col {c} out of bounds for path element {path[i]}")
            if i > 0:
                prev_r, prev_c = path[i-1]
                # Ensure steps are adjacent
                self.assertEqual(manhattan_distance((r,c), (prev_r, prev_c)), 1, f"Path elements {path[i-1]} and {path[i]} are not adjacent.")

    def test_rgm_start_equals_goal(self):
        grid_size = (3, 3)
        start = (1, 1)
        goal = (1, 1)
        grid_to_x_map = lambda r, c: (r + c) * 0.1
        d_res = 5.0
        N_ord = [1, 2, 3]
        path = rgm_a_star(grid_size, start, goal, grid_to_x_map, d_res, N_ord)
        self.assertEqual(path, [(1,1)])

    def test_rgm_grid_distance_calculation(self):
        # Test rgm_grid_distance directly
        pos1 = (0,0)
        pos2 = (0,1)
        grid_to_x_map = lambda r,c: (r*0.1 + c*0.2)
        d_res = 10.0
        N_ord = [1,2,3]

        # x1 = 0, x2 = 0.2
        # A1 = adaptability(0, 10.0, [1,2,3])
        # A2 = adaptability(0.2, 10.0, [1,2,3])
        # d_base = 1.0

        dist = rgm_grid_distance(pos1, pos2, grid_to_x_map, d_res, N_ord)
        self.assertGreater(dist, 0, "RGM grid distance should be positive")
        # Actual value depends on adaptability, which is complex.
        # Just verify it runs and returns a plausible value.

if __name__ == "__main__":
    unittest.main()
