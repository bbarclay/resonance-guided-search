"""
Resonance-Guided Search (RGS) - Pathfinding Implementation

This module implements an A* search algorithm with Resonance-Guided Metric (RGM)
as described in the paper.
"""

import numpy as np
import heapq
from typing import List, Tuple, Dict, Set, Callable, Optional
import sys
import os

# Import from within the package
from src.rgs_core import adaptability, rgm_distance, adaptability_2d, rgm_distance_2d


class Node:
    """A node in the search graph for A* algorithm."""
    
    def __init__(self, position: Tuple[int, int], parent=None):
        self.position = position
        self.parent = parent
        self.g = 0  # Cost from start node to current node
        self.h = 0  # Heuristic (estimated cost from current node to goal)
        self.f = 0  # Total cost (g + h)
    
    def __eq__(self, other):
        return self.position == other.position
    
    def __lt__(self, other):
        return self.f < other.f
    
    def __hash__(self):
        return hash(self.position)


def manhattan_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    """
    Calculate the Manhattan distance between two positions.
    
    Args:
        pos1: First position (row, col)
        pos2: Second position (row, col)
        
    Returns:
        Manhattan distance
    """
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def rgm_grid_distance(
    pos1: Tuple[int, int], 
    pos2: Tuple[int, int], 
    grid_to_x_map: Callable[[int, int], float], 
    d_res: float, 
    N_ord: List[int], 
    w: float = 2.0, 
    x0: float = 0.0
) -> float:
    """
    Calculate the RGM distance between two adjacent grid positions.
    
    Args:
        pos1: First position (row, col)
        pos2: Second position (row, col)
        grid_to_x_map: Function to map grid position to x value
        d_res: Depth parameter
        N_ord: Set of orbital orders
        w: Weight parameter
        x0: Reference point
        
    Returns:
        RGM distance
    """
    # Get x values corresponding to grid positions
    x1 = grid_to_x_map(pos1[0], pos1[1])
    x2 = grid_to_x_map(pos2[0], pos2[1])
    
    # Base distance (Manhattan distance = 1 for adjacent cells)
    d_base = 1.0
    
    # Calculate RGM distance
    return rgm_distance(x1, x2, d_res, N_ord, d_base, w, x0)


def rgm_grid_distance_2d(
    pos1: Tuple[int, int],
    pos2: Tuple[int, int],
    grid_to_xy_map: Callable[[int, int], Tuple[float, float]],
    d_res: float,
    N_ord: List[int],
    w: float = 2.0,
    x0_vec: Tuple[float, float] = (0.0, 0.0)
) -> float:
    """
    Calculate the RGM distance between two adjacent grid positions using 2D adaptability.

    Args:
        pos1: First position (row, col)
        pos2: Second position (row, col)
        grid_to_xy_map: Function to map grid position (row, col) to (x_val, y_val)
        d_res: Depth parameter
        N_ord: Set of orbital orders
        w: Weight parameter
        x0_vec: Reference point vector (x0_x, x0_y)

    Returns:
        RGM distance
    """
    xy1 = grid_to_xy_map(pos1[0], pos1[1])
    xy2 = grid_to_xy_map(pos2[0], pos2[1])

    # Base distance (Manhattan distance = 1 for adjacent cells)
    d_base = 1.0

    # Calculate RGM distance using the 2D version
    return rgm_distance_2d(xy1, xy2, d_res, N_ord, d_base, w, x0_vec)


def a_star_search(
    grid_size: Tuple[int, int],
    start: Tuple[int, int],
    goal: Tuple[int, int],
    distance_func: Callable[[Tuple[int, int], Tuple[int, int]], float],
    heuristic_func: Callable[[Tuple[int, int], Tuple[int, int]], float]
) -> List[Tuple[int, int]]:
    """
    Perform A* search on a grid.
    
    Args:
        grid_size: Tuple (rows, cols) specifying the grid dimensions
        start: Start position (row, col)
        goal: Goal position (row, col)
        distance_func: Function to calculate distance between adjacent positions
        heuristic_func: Function to estimate distance to goal
        
    Returns:
        List of positions (row, col) representing the path from start to goal
    """
    rows, cols = grid_size
    
    # Create start and goal nodes
    start_node = Node(start)
    goal_node = Node(goal)
    
    # Initialize open and closed lists
    open_list = []
    closed_set = set()
    
    # Add the start node to the open list
    heapq.heappush(open_list, (start_node.f, id(start_node), start_node))
    
    # Loop until the open list is empty
    while open_list:
        # Get the node with the lowest f score
        _, _, current_node = heapq.heappop(open_list)
        
        # Add the current node to the closed list
        closed_set.add(current_node.position)
        
        # Check if we reached the goal
        if current_node.position == goal_node.position:
            # Reconstruct the path
            path = []
            while current_node is not None:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]  # Return path from start to goal
        
        # Generate neighboring positions
        neighbors = []
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Right, Down, Left, Up
            new_position = (current_node.position[0] + dr, current_node.position[1] + dc)
            
            # Check if the position is valid
            if (new_position[0] < 0 or new_position[0] >= rows or
                new_position[1] < 0 or new_position[1] >= cols):
                continue
            
            # Create a new node
            neighbor = Node(new_position, current_node)
            
            # Skip if the neighbor is in the closed list
            if neighbor.position in closed_set:
                continue
            
            # Calculate g, h, and f values
            neighbor.g = current_node.g + distance_func(current_node.position, neighbor.position)
            neighbor.h = heuristic_func(neighbor.position, goal_node.position)
            neighbor.f = neighbor.g + neighbor.h
            
            # Check if the neighbor is already in the open list with a better score
            skip = False
            for _, _, open_node in open_list:
                if neighbor == open_node and neighbor.g >= open_node.g:
                    skip = True
                    break
            if skip:
                continue
            
            # Add the neighbor to the open list
            heapq.heappush(open_list, (neighbor.f, id(neighbor), neighbor))
    
    # No path found
    return []


def standard_a_star(
    grid_size: Tuple[int, int],
    start: Tuple[int, int],
    goal: Tuple[int, int]
) -> List[Tuple[int, int]]:
    """
    Perform standard A* search on a grid using Manhattan distance.
    
    Args:
        grid_size: Tuple (rows, cols) specifying the grid dimensions
        start: Start position (row, col)
        goal: Goal position (row, col)
        
    Returns:
        List of positions (row, col) representing the path from start to goal
    """
    # Use Manhattan distance for both the distance and heuristic functions
    return a_star_search(
        grid_size=grid_size,
        start=start,
        goal=goal,
        distance_func=lambda pos1, pos2: 1.0,  # All adjacent cells have a cost of 1
        heuristic_func=manhattan_distance
    )


def rgm_a_star(
    grid_size: Tuple[int, int],
    start: Tuple[int, int],
    goal: Tuple[int, int],
    grid_to_x_map: Callable[[int, int], float],
    d_res: float,
    N_ord: List[int],
    w: float = 2.0,
    x0: float = 0.0
) -> List[Tuple[int, int]]:
    """
    Perform RGM-guided A* search on a grid.
    
    Args:
        grid_size: Tuple (rows, cols) specifying the grid dimensions
        start: Start position (row, col)
        goal: Goal position (row, col)
        grid_to_x_map: Function to map grid position to x value
        d_res: Depth parameter
        N_ord: Set of orbital orders
        w: Weight parameter
        x0: Reference point
        
    Returns:
        List of positions (row, col) representing the path from start to goal
    """
    # Define the RGM distance function for adjacent grid positions
    def distance_func(pos1, pos2):
        return rgm_grid_distance(pos1, pos2, grid_to_x_map, d_res, N_ord, w, x0)
    
    # Use Manhattan distance as a heuristic
    # Note: This might not be admissible for A* if RGM distances can be less than Manhattan,
    # but it works for demonstration purposes
    return a_star_search(
        grid_size=grid_size,
        start=start,
        goal=goal,
        distance_func=distance_func,
        heuristic_func=manhattan_distance
    )


def adaptive_rgm_a_star(
    grid_size: Tuple[int, int],
    start: Tuple[int, int],
    goal: Tuple[int, int],
    grid_to_x_map: Callable[[int, int], float],
    N_ord: List[int],
    d_res_far: float,
    d_res_near: float,
    w: float = 2.0,
    x0: float = 0.0,
    heuristic_func: Callable[[Tuple[int, int], Tuple[int, int]], float] = manhattan_distance
) -> List[Tuple[int, int]]:
    """
    Perform RGM-guided A* search with d_res adapting based on heuristic distance to goal.

    This strategy dynamically adjusts the d_res parameter used in RGM calculations.
    When the current position is far from the goal (as per the heuristic), d_res_far
    is predominantly used. As the position gets closer to the goal, d_res transitions
    towards d_res_near. This allows for potentially different search behaviors
    (e.g., more explorative far away, more exploitative nearby).

    Args:
        grid_size: Tuple (rows, cols) specifying the grid dimensions.
        start: Start position (row, col).
        goal: Goal position (row, col).
        grid_to_x_map: Function to map grid position (row, col) to a scalar x value.
        N_ord: Set of orbital orders for RGM.
        d_res_far: Depth parameter value when far from the goal.
        d_res_near: Depth parameter value when near the goal.
        w: Weight parameter for RGM.
        x0: Reference point for RGM.
        heuristic_func: Function to estimate distance to goal. Defaults to manhattan_distance.

    Returns:
        List of positions (row, col) representing the path from start to goal.
        The A* search might not be strictly admissible due to dynamic edge costs.
    """
    h_start = heuristic_func(start, goal)

    def adaptive_distance_func(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        h_current = heuristic_func(pos1, goal)

        if h_start == 0:  # Handles case where start is the goal or h_start is zero
            h_ratio = 0.0
        else:
            h_ratio = min(1.0, h_current / h_start)  # Clamped ratio

        # Linearly interpolate d_res based on the heuristic ratio
        current_d_res = d_res_far * h_ratio + d_res_near * (1.0 - h_ratio)

        x1 = grid_to_x_map(pos1[0], pos1[1])
        x2 = grid_to_x_map(pos2[0], pos2[1])
        
        d_base = 1.0  # Base distance for adjacent grid cells

        return rgm_distance(x1, x2, current_d_res, N_ord, d_base, w, x0)

    return a_star_search(
        grid_size=grid_size,
        start=start,
        goal=goal,
        distance_func=adaptive_distance_func,
        heuristic_func=heuristic_func  # Use the provided heuristic
    )


def rgm_a_star_2d(
    grid_size: Tuple[int, int],
    start: Tuple[int, int],
    goal: Tuple[int, int],
    grid_to_xy_map: Callable[[int, int], Tuple[float, float]],
    d_res: float,
    N_ord: List[int],
    w: float = 2.0,
    x0_vec: Tuple[float, float] = (0.0, 0.0)
) -> List[Tuple[int, int]]:
    """
    Perform RGM-guided A* search on a grid using 2D adaptability.

    Args:
        grid_size: Tuple (rows, cols) specifying the grid dimensions
        start: Start position (row, col)
        goal: Goal position (row, col)
        grid_to_xy_map: Function to map grid position (row, col) to (x_val, y_val)
        d_res: Depth parameter
        N_ord: Set of orbital orders
        w: Weight parameter
        x0_vec: Reference point vector (x0_x, x0_y)

    Returns:
        List of positions (row, col) representing the path from start to goal
    """
    # Define the RGM distance function for adjacent grid positions using 2D adaptability
    def distance_func(pos1, pos2):
        return rgm_grid_distance_2d(pos1, pos2, grid_to_xy_map, d_res, N_ord, w, x0_vec)

    # Use Manhattan distance as a heuristic
    # Note: This might not be admissible for A* if RGM distances can be less than Manhattan,
    # but it works for demonstration purposes
    return a_star_search(
        grid_size=grid_size,
        start=start,
        goal=goal,
        distance_func=distance_func,
        heuristic_func=manhattan_distance
    )