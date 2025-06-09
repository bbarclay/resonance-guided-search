#!/usr/bin/env python
"""
Demo script for visualizing adaptability landscapes as described in the paper
"Resonance-Guided Search: A Novel Heuristic Framework Based on Adaptability in Conserved Systems"
"""

import os
import sys
import matplotlib.pyplot as plt

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import directly from the modules
from src.rgs_viz import plot_adaptability_landscape, plot_adaptability_profile

# Create figures directory if it doesn't exist
FIGURES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures"
)
os.makedirs(FIGURES_DIR, exist_ok=True)


def main():
    # Define parameters
    x_range = (0.01, 1.0)  # Range of x values to explore
    d_res_range = (2.0, 256.0)  # Range of d_res values to explore

    # Define different sets of orbital orders to experiment with
    N_ord_sets = {
        "Baseline": list(range(1, 13)),  # {1, 2, ..., 12}
        "Sparse": [1, 5, 10],
        "Low_Orders": [1, 2, 3],
        "High_Orders": [10, 11, 12],
    }

    # Plot adaptability landscapes for each set of orbital orders
    for name, N_ord in N_ord_sets.items():
        print(f"Plotting adaptability landscape for {name} (N_ord = {N_ord})...")

        # Plot adaptability landscape (heatmap)
        fig, ax = plot_adaptability_landscape(
            x_range=x_range,
            d_res_range=d_res_range,
            N_ord=N_ord,
            num_x_points=500,
            num_d_res_points=30,
            log_scale_d_res=True,
            log_scale_color=True,
            title=f"Adaptability Landscape $A(x, d_{{res}})$ for $N_{{ord}}$ ({name})",
        )

        # Save the figure
        fig_path = os.path.join(FIGURES_DIR, f"A_landscape_{name}.png")
        plt.savefig(fig_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"  Saved to {fig_path}")

    # Plot adaptability profiles for selected d_res values
    d_res_values = [2.0, 5.0, 10.0, 20.0, 50.0, 100.0]
    for name, N_ord in N_ord_sets.items():
        print(f"Plotting adaptability profiles for {name} (N_ord = {N_ord})...")

        # Plot adaptability profiles
        fig, ax = plot_adaptability_profile(
            x_range=x_range,
            d_res_values=d_res_values,
            N_ord=N_ord,
            num_x_points=500,
            title=f"Adaptability Profiles for Different $d_{{res}}$ values\n$N_{{ord}}$ ({name})",
        )

        # Save the figure
        fig_path = os.path.join(FIGURES_DIR, f"A_profiles_{name}.png")
        plt.savefig(fig_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"  Saved to {fig_path}")

    print("\nAll adaptability landscapes and profiles have been generated.")


if __name__ == "__main__":
    main()
