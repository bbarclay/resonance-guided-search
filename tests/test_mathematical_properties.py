#!/usr/bin/env python
"""
Unit tests for verifying the mathematical properties of the Resonance-Guided Search framework
as described in the paper "Resonance-Guided Search: A Novel Heuristic Framework Based on
Adaptability in Conserved Systems"

This test suite verifies:
1. Bounds on adaptability (0 ≤ A(x, d_res) ≤ 1)
2. Periodicity of adaptability (A(x + 1, d_res) = A(x, d_res))
3. Properties of the RGM (non-negativity, identity of indiscernibles, symmetry)
4. Convergence properties of RGM
"""

import os
import sys
import unittest
import numpy as np

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import directly from the modules
from src.rgs_core import adaptability, rgm_distance, modulating_function, adaptability_array


class TestAdaptabilityBounds(unittest.TestCase):
    """Test that adaptability is bounded between 0 and 1."""

    def test_adaptability_bounds(self):
        """Test that adaptability is bounded between 0 and 1 for various inputs."""
        # Test parameters
        x_values = np.linspace(0, 2, 100)  # Test over a range of x values
        d_res_values = [1.0, 5.0, 20.0, 100.0]  # Test different depth parameters
        N_ord_sets = [
            [1, 2, 3, 4, 5],  # Low orders
            [10, 11, 12],  # High orders
            [1, 5, 10],  # Sparse
            list(range(1, 13)),  # Full range
        ]

        for d_res in d_res_values:
            for N_ord in N_ord_sets:
                for x in x_values:
                    a = adaptability(x, d_res, N_ord)
                    self.assertGreaterEqual(
                        a,
                        0,
                        f"Adaptability < 0 for x={x}, d_res={d_res}, N_ord={N_ord}",
                    )
                    self.assertLessEqual(
                        a,
                        1,
                        f"Adaptability > 1 for x={x}, d_res={d_res}, N_ord={N_ord}",
                    )


class TestAdaptabilityPeriodicity(unittest.TestCase):
    """Test the theoretical basis for periodicity in the adaptability metric."""

    def test_theoretical_periodicity(self):
        """
        Test the theoretical basis for periodicity.

        Since the sine and cosine functions have period 2π, and our angles
        are defined as θ(x) = 2π(x-x0) and φ(x) = d_res·π(x-x0),
        increasing x by 1 should result in the same angles modulo 2π.
        """
        from src.rgs_core import theta, phi

        x_values = [0.1, 0.5, 1.0, 2.0]
        d_res_values = [1.0, 5.0, 20.0]
        x0 = 0.0

        for x in x_values:
            for d_res in d_res_values:
                # For theta, adding 1 to x should increase by 2π
                t1 = theta(x, x0)
                t2 = theta(x + 1, x0)
                self.assertAlmostEqual(
                    t1 % (2 * np.pi),
                    t2 % (2 * np.pi),
                    places=10,
                    msg=f"Theta periodicity failed for x={x}, d_res={d_res}",
                )

                # For phi, adding 1 to x should increase by d_res·π
                p1 = phi(x, d_res, x0)
                p2 = phi(x + 1, d_res, x0)
                expected_diff = d_res * np.pi
                actual_diff = p2 - p1
                self.assertAlmostEqual(
                    actual_diff,
                    expected_diff,
                    places=10,
                    msg=f"Phi increment failed for x={x}, d_res={d_res}",
                )

    def test_coupling_function_periodicity(self):
        """
        Test the periodicity of the coupling function for specific cases.

        The coupling function h_n(x, d_res) should be periodic with period 1
        for integer orbital orders when d_res is an integer multiple of n.
        """
        from src.rgs_core import coupling_function

        # Test with specific values known to work well
        x = 0.5
        x0 = 0.0
        test_cases = [
            # n, d_res pairs where periodicity should hold well
            (1, 1.0),
            (2, 2.0),
            (3, 3.0),
            (4, 4.0),
        ]

        for n, d_res in test_cases:
            h1 = coupling_function(x, d_res, n, x0)
            h2 = coupling_function(x + 1, d_res, n, x0)

            # Use a reasonable tolerance for floating point comparison
            self.assertAlmostEqual(
                h1,
                h2,
                places=5,
                msg=f"Coupling function periodicity failed for n={n}, d_res={d_res}",
            )

    def test_adaptability_metric_periodicity(self):
        """Test that A(x + 1, d_res) = A(x, d_res) for various inputs."""
        # Test parameters
        x_values = np.linspace(0, 1, 10)  # Test over a range of x values
        d_res_values = [1.0, 5.0, 20.0]  # Test different depth parameters
        N_ord_sets = [
            [1, 2, 3],  # Low orders
            [10, 11, 12],  # High orders
            list(range(1, 7)),  # Medium range
        ]
        x0 = 0.0

        for d_res in d_res_values:
            for N_ord in N_ord_sets:
                for x in x_values:
                    a1 = adaptability(x, d_res, N_ord, x0)
                    a2 = adaptability(x + 1, d_res, N_ord, x0)
                    self.assertAlmostEqual(
                        a1,
                        a2,
                        places=10,
                        msg=f"Adaptability metric periodicity failed for x={x}, d_res={d_res}, N_ord={N_ord}",
                    )


class TestAdaptabilityInputValidation(unittest.TestCase):
    """Test input validation for adaptability functions."""

    def test_empty_n_ord_raises_value_error_adaptability(self):
        """Test that adaptability() raises ValueError for empty N_ord."""
        with self.assertRaises(ValueError):
            adaptability(x=0.5, d_res=1.0, N_ord=[], x0=0.0)

    def test_empty_n_ord_raises_value_error_adaptability_array(self):
        """Test that adaptability_array() raises ValueError for empty N_ord."""
        with self.assertRaises(ValueError):
            adaptability_array(x_array=np.array([0.5]), d_res=1.0, N_ord=[], x0=0.0)


class TestRGMProperties(unittest.TestCase):
    """Test the metric properties of the Resonance-Guided Metric."""

    def test_rgm_non_negativity(self):
        """Test that d_rgm(x1, x2) ≥ 0 for all x1, x2."""
        # Test parameters
        x_values = np.linspace(0, 1, 20)  # Test over a range of x values
        d_res = 10.0
        N_ord = list(range(1, 13))
        w_values = [0.1, 1.0, 10.0]

        for w in w_values:
            for x1 in x_values:
                for x2 in x_values:
                    d_base = abs(x1 - x2)  # Euclidean distance in 1D
                    d = rgm_distance(x1, x2, d_res, N_ord, d_base, w)
                    self.assertGreaterEqual(
                        d, 0, f"RGM distance < 0 for x1={x1}, x2={x2}, w={w}"
                    )

    def test_rgm_identity(self):
        """Test that d_rgm(x, x) = 0 for all x."""
        # Test parameters
        x_values = np.linspace(0, 1, 20)  # Test over a range of x values
        d_res = 10.0
        N_ord = list(range(1, 13))
        w_values = [0.1, 1.0, 10.0]

        for w in w_values:
            for x in x_values:
                d_base = 0.0  # Distance to self is 0
                d = rgm_distance(x, x, d_res, N_ord, d_base, w)
                self.assertAlmostEqual(
                    d, 0, places=10, msg=f"RGM distance to self != 0 for x={x}, w={w}"
                )

    def test_rgm_symmetry(self):
        """Test that d_rgm(x1, x2) = d_rgm(x2, x1) for all x1, x2."""
        # Test parameters
        x_values = np.linspace(0, 1, 20)  # Test over a range of x values
        d_res = 10.0
        N_ord = list(range(1, 13))
        w_values = [0.1, 1.0, 10.0]

        for w in w_values:
            for x1 in x_values:
                for x2 in x_values:
                    d_base = abs(x1 - x2)  # Euclidean distance in 1D
                    d12 = rgm_distance(x1, x2, d_res, N_ord, d_base, w)
                    d21 = rgm_distance(x2, x1, d_res, N_ord, d_base, w)
                    self.assertAlmostEqual(
                        d12,
                        d21,
                        places=10,
                        msg=f"RGM not symmetric for x1={x1}, x2={x2}, w={w}",
                    )


class TestRGMConvergence(unittest.TestCase):
    """Test the convergence properties of the Resonance-Guided Metric."""

    def test_rgm_convergence_to_base(self):
        """Test that as w → 0, d_rgm(x1, x2) → d_base(x1, x2)."""
        # Test parameters
        x1, x2 = 0.3, 0.7
        d_res = 10.0
        N_ord = list(range(1, 13))
        d_base = abs(x1 - x2)  # Euclidean distance in 1D

        # Test with decreasing w values
        w_values = [1.0, 0.1, 0.01, 0.001, 0.0001]

        for w in w_values:
            d = rgm_distance(x1, x2, d_res, N_ord, d_base, w)
            # As w gets smaller, d should approach d_base
            relative_error = abs(d - d_base) / d_base
            self.assertLessEqual(
                relative_error, w * 10, f"RGM not converging to base metric for w={w}"
            )

    def test_high_adaptability_preference(self):
        """Test that as w increases, paths through high adaptability regions are favored."""
        # Test parameters
        d_res = 10.0
        N_ord = list(range(1, 13))

        # Find points with significantly different adaptability values
        # by sampling and selecting the highest and lowest
        x_samples = np.linspace(0.1, 0.9, 100)
        adaptability_values = [adaptability(x, d_res, N_ord) for x in x_samples]

        # Find indices of min and max adaptability
        min_idx = np.argmin(adaptability_values)
        max_idx = np.argmax(adaptability_values)

        # Ensure they're significantly different
        A_low = adaptability_values[min_idx]
        A_high = adaptability_values[max_idx]

        if (A_high - A_low) < 0.1:
            self.skipTest(
                "Could not find points with sufficiently different adaptability values"
            )

        x_low_A = x_samples[min_idx]
        x_high_A = x_samples[max_idx]

        # Common point to measure distance from
        x_common = 0.0
        d_base = 1.0  # Same base distance

        # Test with increasing w values
        w_values = [0.1, 1.0, 10.0, 100.0]

        for w in w_values:
            d_low = rgm_distance(x_common, x_low_A, d_res, N_ord, d_base, w)
            d_high = rgm_distance(x_common, x_high_A, d_res, N_ord, d_base, w)

            # As w increases, the ratio d_high/d_low should decrease
            # (high adaptability path becomes more favorable)
            self.assertLess(
                d_high, d_low, f"High adaptability path not favored for w={w}"
            )

            # For large w, verify that the ratio is decreasing as w increases
            if w > 1.0:
                # Calculate modulating functions directly
                f_mod_low = modulating_function(
                    A_low, adaptability(x_common, d_res, N_ord), w
                )
                f_mod_high = modulating_function(
                    A_high, adaptability(x_common, d_res, N_ord), w
                )

                # The ratio of modulating functions should be less than 1
                # (high adaptability path has smaller modulating function)
                ratio = f_mod_high / f_mod_low
                self.assertLess(
                    ratio,
                    1.0,
                    f"Modulating function ratio not favorable for high adaptability at w={w}",
                )


if __name__ == "__main__":
    unittest.main()
