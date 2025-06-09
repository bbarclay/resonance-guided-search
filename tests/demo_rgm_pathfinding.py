#!/usr/bin/env python
"""
Demo script for pathfinding comparison between standard A* and RGM-guided A* search
as described in the paper "Resonance-Guided Search: A Novel Heuristic Framework Based on
Adaptability in Conserved Systems"
"""

import os
import sys
import matplotlib.pyplot as plt

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import directly from the modules
from src.rgs_pathfinding import standard_a_star, rgm_a_star
from src.rgs_viz import plot_grid_pathfinding

# Create figures directory if it doesn't exist
FIGURES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures"
)
os.makedirs(FIGURES_DIR, exist_ok=True)


def main():
    # Define grid parameters
    grid_size = (20, 30)  # (rows, cols)
    start = (2, 2)
    goal = (17, 27)

    # Define X_max for the grid-to-x mapping
    X_max = 2.0

    # Define the function to map grid positions to x values
    def grid_to_x_map(row, col):
        # Map grid positions to x values in [0, X_max)
        # Using a simple formula that creates interesting patterns
        return ((row * 0.1 + col * 0.05) * X_max) % X_max

    # Define orbital orders and other parameters
    N_ord = list(range(1, 13))  # {1, 2, ..., 12}

    # Various depth parameters to explore
    d_res_values = [5.0, 20.0, 80.0]

    # Run standard A* search
    print("Running standard A* search...")
    standard_path = standard_a_star(grid_size, start, goal)
    print(f"  Standard A* path length: {len(standard_path)}")

    # Run RGM-guided A* searches with different d_res values
    rgm_paths = {}
    for d_res in d_res_values:
        print(f"Running RGM-guided A* search with d_res={d_res}...")
        path = rgm_a_star(
            grid_size=grid_size,
            start=start,
            goal=goal,
            grid_to_x_map=grid_to_x_map,
            d_res=d_res,
            N_ord=N_ord,
            w=2.0,
        )
        rgm_paths[f"RGM d_res={d_res}"] = path
        print(f"  RGM-guided A* path length (d_res={d_res}): {len(path)}")

    # Collect all paths for visualization
    all_paths = {"Standard A*": standard_path}
    all_paths.update(rgm_paths)

    # Plot comparison for a specific d_res value (for background)
    d_res_for_bg = 20.0
    print(
        f"Creating pathfinding comparison visualization (background: d_res={d_res_for_bg})..."
    )

    fig, ax = plot_grid_pathfinding(
        grid_size=grid_size,
        start=start,
        goal=goal,
        paths=all_paths,
        grid_to_x_map=grid_to_x_map,
        d_res=d_res_for_bg,
        N_ord=N_ord,
        title=f"Pathfinding Comparison on a {grid_size[0]}×{grid_size[1]} Grid\nBackground: $A(x, d_{{res}}={d_res_for_bg})$",
    )

    # Save the figure
    fig_path = os.path.join(FIGURES_DIR, "pathfinding_comparison.png")
    plt.savefig(fig_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved to {fig_path}")

    print("\nPathfinding comparison complete.")


if __name__ == "__main__":
    main()
