#!/usr/bin/env python
"""
Smoke tests for visualization demo scripts.
These tests run the scripts and check if they produce the expected output files.
"""

import os
import sys
import unittest
import subprocess

# Add the parent directory to the path to allow imports from src
# This is relevant if the scripts themselves import from src, which they do.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FIGURES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures"
)

# Expected output files
PATHFINDING_FIG = os.path.join(FIGURES_DIR, "pathfinding_comparison.png")
LANDSCAPE_NAMES = ["Baseline", "Sparse", "Low_Orders", "High_Orders"]
LANDSCAPE_FIGS = [
    os.path.join(FIGURES_DIR, f"A_landscape_{name}.png") for name in LANDSCAPE_NAMES
]
PROFILE_FIGS = [
    os.path.join(FIGURES_DIR, f"A_profiles_{name}.png") for name in LANDSCAPE_NAMES
]

ALL_EXPECTED_FIGS = [PATHFINDING_FIG] + LANDSCAPE_FIGS + PROFILE_FIGS


class TestVisualizationScripts(unittest.TestCase):
    """Tests that visualization scripts run and produce output."""

    def setUp(self):
        """Ensure the figures directory exists and remove any pre-existing figures."""
        os.makedirs(FIGURES_DIR, exist_ok=True)
        # Clean up any figures that might exist from previous runs before each test
        for fig_path in ALL_EXPECTED_FIGS:
            try:
                os.remove(fig_path)
            except FileNotFoundError:
                pass # File doesn't exist, which is fine

    def tearDown(self):
        """Clean up generated figures after tests."""
        for fig_path in ALL_EXPECTED_FIGS:
            try:
                os.remove(fig_path)
            except FileNotFoundError:
                pass

    def test_demo_rgm_pathfinding_runs(self):
        """Test that demo_rgm_pathfinding.py runs and creates its output file."""
        # Ensure the specific file for this test is gone if setUp didn't catch it
        # or if it was created by another process mid-test (unlikely here).
        if os.path.exists(PATHFINDING_FIG):
            os.remove(PATHFINDING_FIG)

        script_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "demo_rgm_pathfinding.py"
        )
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=False, # Check manually to provide better error messages
        )

        self.assertEqual(result.returncode, 0, f"Script {script_path} failed with error:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
        self.assertTrue(
            os.path.exists(PATHFINDING_FIG),
            f"Script {script_path} did not create expected file {PATHFINDING_FIG}",
        )

    def test_adaptability_landscape_script_runs(self):
        """Test that test_adaptability_landscape.py runs and creates its output files."""
        # Ensure specific files for this test are gone
        for fig_path in LANDSCAPE_FIGS + PROFILE_FIGS:
            if os.path.exists(fig_path):
                os.remove(fig_path)

        script_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "test_adaptability_landscape.py"
        )
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=False, # Check manually
        )

        self.assertEqual(result.returncode, 0, f"Script {script_path} failed with error:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")

        for fig_path in LANDSCAPE_FIGS:
            self.assertTrue(
                os.path.exists(fig_path),
                f"Script {script_path} did not create expected landscape file {fig_path}",
            )
        for fig_path in PROFILE_FIGS:
            self.assertTrue(
                os.path.exists(fig_path),
                f"Script {script_path} did not create expected profile file {fig_path}",
            )


if __name__ == "__main__":
    unittest.main()
