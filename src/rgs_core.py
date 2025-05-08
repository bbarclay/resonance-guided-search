"""
Resonance-Guided Search (RGS) - Core Implementation

This module implements the core functionality for the Resonance-Guided Search framework
as described in the paper "Resonance-Guided Search: A Novel Heuristic Framework Based on 
Adaptability in Conserved Systems."

It provides functions to compute:
- Adaptability metric A(x, d_res)
- Coherence metric C(x, d_res)
- Resonance-Guided Metric (RGM)
"""

import numpy as np
from typing import List, Tuple, Callable, Union, Optional


def theta(x: float, x0: float = 0.0) -> float:
    """
    Compute the primary angle.
    
    Args:
        x: Configuration parameter
        x0: Reference point
        
    Returns:
        Primary angle θ(x)
    """
    return 2 * np.pi * (x - x0)


def phi(x: float, d_res: float, x0: float = 0.0) -> float:
    """
    Compute the secondary angle.
    
    Args:
        x: Configuration parameter
        d_res: Depth parameter
        x0: Reference point
        
    Returns:
        Secondary angle φ(x, d_res)
    """
    return d_res * np.pi * (x - x0)


def coupling_function(x: float, d_res: float, n: int, x0: float = 0.0) -> float:
    """
    Compute the coupling function h_n(x, d_res) for a specific orbital order n.
    
    Args:
        x: Configuration parameter
        d_res: Depth parameter
        n: Orbital order
        x0: Reference point
        
    Returns:
        Coupling function value h_n(x, d_res)
    """
    t = theta(x, x0)
    p = phi(x, d_res, x0)
    
    # Using np.abs() is more efficient than taking the absolute value with |...|
    sin_term = np.abs(np.sin(n * t)) ** (d_res / n)
    cos_term = np.abs(np.cos(n * p)) ** (1 / n)
    
    return sin_term * cos_term


def adaptability(x: float, d_res: float, N_ord: List[int], x0: float = 0.0) -> float:
    """
    Compute the Adaptability metric A(x, d_res).
    
    Args:
        x: Configuration parameter
        d_res: Depth parameter
        N_ord: Set of orbital orders
        x0: Reference point
        
    Returns:
        Adaptability A(x, d_res)
    """
    if not N_ord:
        raise ValueError("N_ord cannot be empty")
    
    h_sum = sum(coupling_function(x, d_res, n, x0) for n in N_ord)
    return h_sum / len(N_ord)


def coherence(x: float, d_res: float, N_ord: List[int], x0: float = 0.0) -> float:
    """
    Compute the Coherence metric C(x, d_res).
    
    Args:
        x: Configuration parameter
        d_res: Depth parameter
        N_ord: Set of orbital orders
        x0: Reference point
        
    Returns:
        Coherence C(x, d_res)
    """
    return 1.0 - adaptability(x, d_res, N_ord, x0)


def modulating_function(A1: float, A2: float, w: float = 2.0, epsilon: float = 1e-9) -> float:
    """
    Compute the modulating function f_mod for the RGM.
    
    Args:
        A1: Adaptability at point 1
        A2: Adaptability at point 2
        w: Weight parameter
        epsilon: Small constant to prevent division by zero
        
    Returns:
        Modulating function value
    """
    avg_adaptability = (A1 + A2) / 2.0
    return 1.0 / (1.0 + w * avg_adaptability + epsilon)


def rgm_distance(x1: float, x2: float, d_res: float, N_ord: List[int], 
                 d_base: float, w: float = 2.0, x0: float = 0.0, 
                 epsilon: float = 1e-9) -> float:
    """
    Compute the Resonance-Guided Metric (RGM) distance between two points.
    
    Args:
        x1: Configuration parameter for point 1
        x2: Configuration parameter for point 2
        d_res: Depth parameter
        N_ord: Set of orbital orders
        d_base: Base distance between x1 and x2
        w: Weight parameter for the modulating function
        x0: Reference point for adaptability calculation
        epsilon: Small constant to prevent division by zero
        
    Returns:
        RGM distance between x1 and x2
    """
    A1 = adaptability(x1, d_res, N_ord, x0)
    A2 = adaptability(x2, d_res, N_ord, x0)
    
    return d_base * modulating_function(A1, A2, w, epsilon)


# Vectorized versions for efficient computation over arrays

def adaptability_array(x_array: np.ndarray, d_res: float, N_ord: List[int], 
                       x0: float = 0.0) -> np.ndarray:
    """
    Compute the Adaptability metric A(x, d_res) over an array of x values.
    
    Args:
        x_array: Array of configuration parameters
        d_res: Depth parameter
        N_ord: Set of orbital orders
        x0: Reference point
        
    Returns:
        Array of Adaptability values
    """
    if not N_ord:
        raise ValueError("N_ord cannot be empty")
    
    adaptability_values = np.zeros_like(x_array, dtype=float)
    for n in N_ord:
        t = 2 * np.pi * (x_array - x0)
        p = d_res * np.pi * (x_array - x0)
        
        sin_term = np.abs(np.sin(n * t)) ** (d_res / n)
        cos_term = np.abs(np.cos(n * p)) ** (1 / n)
        
        adaptability_values += sin_term * cos_term
    
    return adaptability_values / len(N_ord)