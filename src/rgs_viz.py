"""
Resonance-Guided Search (RGS) - Visualization Module

This module provides functions for visualizing adaptability landscapes and
pathfinding results from the Resonance-Guided Search framework.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from typing import List, Tuple, Optional, Union, Dict
import os
import sys

# Import from within the package
from src.rgs_core import adaptability, adaptability_array, adaptability_2d, adaptability_2d_array
from typing import List, Tuple, Optional, Union, Dict, Callable


def plot_adaptability_landscape(
    x_range: Tuple[float, float], 
    d_res_range: Tuple[float, float], 
    N_ord: List[int],
    num_x_points: int = 500,
    num_d_res_points: int = 20,
    x0: float = 0.0,
    log_scale_d_res: bool = True,
    log_scale_color: bool = True,
    cmap: str = 'viridis',
    title: Optional[str] = None,
    save_path: Optional[str] = None,
    fig_size: Tuple[float, float] = (10, 8)
) -> Tuple[Figure, Axes]:
    """
    Plot the adaptability landscape A(x, d_res) as a heatmap.
    
    Args:
        x_range: Tuple (min_x, max_x) specifying the range of x values
        d_res_range: Tuple (min_d_res, max_d_res) specifying the range of d_res values
        N_ord: Set of orbital orders
        num_x_points: Number of points to sample along the x axis
        num_d_res_points: Number of points to sample along the d_res axis
        x0: Reference point for adaptability calculation
        log_scale_d_res: Whether to use log scale for d_res axis
        log_scale_color: Whether to use log scale for color mapping
        cmap: Colormap to use
        title: Plot title (if None, a default title is generated)
        save_path: Path to save the figure (if None, the figure is not saved)
        fig_size: Figure size in inches
        
    Returns:
        Tuple (fig, ax) containing the figure and axes
    """
    # Generate x and d_res values
    x_values = np.linspace(x_range[0], x_range[1], num_x_points)
    
    if log_scale_d_res:
        d_res_values = np.logspace(np.log10(d_res_range[0]), np.log10(d_res_range[1]), num_d_res_points)
    else:
        d_res_values = np.linspace(d_res_range[0], d_res_range[1], num_d_res_points)
    
    # Create a meshgrid for vectorized computation
    X, D_RES = np.meshgrid(x_values, d_res_values)
    
    # Initialize the adaptability matrix
    A_matrix = np.zeros_like(X)
    
    # Compute adaptability for each d_res value
    for i, d_res in enumerate(d_res_values):
        A_matrix[i, :] = adaptability_array(x_values, d_res, N_ord, x0)
    
    # Create the figure and axes
    fig, ax = plt.subplots(figsize=fig_size)
    
    # Create the heatmap
    if log_scale_color:
        norm = colors.LogNorm(vmin=max(1e-5, A_matrix.min()), vmax=A_matrix.max())
    else:
        norm = colors.Normalize(vmin=A_matrix.min(), vmax=A_matrix.max())
    
    im = ax.pcolormesh(X, D_RES, A_matrix, cmap=cmap, norm=norm, shading='auto')
    
    # Add a colorbar
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label('Adaptability $A(x, d_{res})$')
    
    # Set axis labels
    ax.set_xlabel('Configuration $x$')
    ax.set_ylabel('Depth $d_{res}$')
    
    # Set y-axis to log scale if specified
    if log_scale_d_res:
        ax.set_yscale('log')
    
    # Set the title
    if title is None:
        title = f'Adaptability Landscape $A(x, d_{{res}})$ for $N_{{ord}}=\\{{{N_ord[0]},...,{N_ord[-1]}\\}}$'
    ax.set_title(title)
    
    # Add grid lines
    ax.grid(True, alpha=0.3)
    
    # Save the figure if a path is provided
    if save_path is not None:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig, ax


def plot_grid_pathfinding(
    grid_size: Tuple[int, int],
    start: Tuple[int, int],
    goal: Tuple[int, int],
    paths: Dict[str, List[Tuple[int, int]]],
    grid_to_x_map: Callable[[int, int], float],  # Maps grid (r,c) to a single float x
    d_res: float,
    N_ord: List[int],
    x0: float = 0.0,  # For 1D adaptability
    title: Optional[str] = None,
    save_path: Optional[str] = None,
    fig_size: Tuple[float, float] = (10, 8)
) -> Tuple[Figure, Axes]:
    """
    Plot paths on a grid with 1D adaptability values (mapped from grid) as the background.

    Args:
        grid_size: Tuple (rows, cols) specifying the grid dimensions.
        start: Tuple (row, col) of the start position.
        goal: Tuple (row, col) of the goal position.
        paths: Dictionary mapping path names to lists of (row, col) coordinates.
        grid_to_x_map: Function mapping (row, col) grid coordinates to a scalar x value.
        d_res: Depth parameter for adaptability calculation.
        N_ord: Set of orbital orders.
        x0: Reference point for 1D adaptability calculation.
        title: Plot title. If None, a default is generated.
        save_path: Path to save the figure. If None, not saved.
        fig_size: Figure size.

    Returns:
        Tuple (fig, ax) containing the figure and axes.
    """
    rows, cols = grid_size
    fig, ax = plt.subplots(figsize=fig_size)

    # Compute 1D adaptability values for each grid cell using grid_to_x_map
    A_grid = np.zeros((rows, cols))
    for r in range(rows):
        for c in range(cols):
            x_val = grid_to_x_map(r, c)
            A_grid[r, c] = adaptability(x_val, d_res, N_ord, x0) # Using 1D adaptability

    im = ax.imshow(A_grid, cmap='viridis', origin='upper', interpolation='none')
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label('Adaptability $A(x, d_{res})$') # Label for 1D adaptability

    # Plot paths (this part is identical to plot_grid_pathfinding_2d_background)
    path_colors = ['white', 'red', 'green', 'magenta', 'cyan', 'yellow']
    line_styles = ['-', '--', '-.', ':', '-', '--']
    for i, (path_name, path) in enumerate(paths.items()):
        if not path: # Handle empty paths
            continue
        path_array = np.array(path)
        ax.plot(path_array[:, 1], path_array[:, 0],
                color=path_colors[i % len(path_colors)],
                linestyle=line_styles[i % len(line_styles)],
                linewidth=2.5,
                label=path_name)

    ax.plot(start[1], start[0], 'bo', markersize=10, label='Start')
    ax.plot(goal[1], goal[0], 'rx', markersize=10, label='Goal')

    ax.set_xlabel('Column')
    ax.set_ylabel('Row')

    if title is None:
        title = (f'Pathfinding Comparison ({rows}x{cols} Grid, 1D Adaptability Background)\n'
                   f'$d_{{res}}={d_res:.2f}, N_{{ord}}=\\{{{N_ord[0]},...,{N_ord[-1]}\\}}, x0={x0:.2f}$')
    ax.set_title(title)

    ax.grid(True, alpha=0.3)
    ax.legend(loc='best')

    ax.set_xticks(np.arange(-0.5, cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, rows, 1), minor=True)
    ax.grid(which='minor', color='black', linestyle='-', linewidth=0.5, alpha=0.2)

    ax.set_xlim(-0.5, cols - 0.5)
    ax.set_ylim(rows - 0.5, -0.5) # Origin 'upper' means (0,0) is top-left

    if save_path is not None:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig, ax


def plot_adaptability_landscape_2d(
    x_coords_range: Tuple[float, float],
    y_coords_range: Tuple[float, float],
    d_res: float,
    N_ord: List[int],
    num_points: int = 100,
    x0_vec: Tuple[float, float] = (0.0, 0.0),
    cmap: str = 'viridis',
    title: Optional[str] = None,
    save_path: Optional[str] = None,
    fig_size: Tuple[float, float] = (10, 8)
) -> Tuple[Figure, Axes]:
    """
    Plot the 2D adaptability landscape A((x,y), d_res) as a heatmap.

    Args:
        x_coords_range: Tuple (min_x, max_x) for x-coordinates.
        y_coords_range: Tuple (min_y, max_y) for y-coordinates.
        d_res: Fixed depth parameter.
        N_ord: Set of orbital orders.
        num_points: Number of points for both x and y axes.
        x0_vec: Reference point vector (x0_x, x0_y).
        cmap: Colormap to use.
        title: Plot title. If None, a default is generated.
        save_path: Path to save the figure. If None, not saved.
        fig_size: Figure size.

    Returns:
        Tuple (fig, ax) containing the figure and axes.
    """
    x_values = np.linspace(x_coords_range[0], x_coords_range[1], num_points)
    y_values = np.linspace(y_coords_range[0], y_coords_range[1], num_points)

    A_matrix = adaptability_2d_array(x_values, y_values, d_res, N_ord, x0_vec)

    fig, ax = plt.subplots(figsize=fig_size)

    # pcolormesh expects X, Y, C where C is (len(y_values), len(x_values))
    # adaptability_2d_array returns A_matrix with shape (len(y_coords), len(x_coords))
    # which matches the requirement.
    im = ax.pcolormesh(x_values, y_values, A_matrix, cmap=cmap, shading='auto')

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label(f'Adaptability $A((x,y), d_{{res}}={d_res:.2f})$')

    ax.set_xlabel('X coordinate')
    ax.set_ylabel('Y coordinate')

    if title is None:
        title = (f'2D Adaptability Landscape $A((x,y), d_{{res}}={d_res:.2f})$\n'
                   f'$N_{{ord}}=\\{{{N_ord[0]},...,{N_ord[-1]}\\}}, x0={x0_vec}$')
    ax.set_title(title)
    ax.set_aspect('equal', 'box') # Ensure square pixels

    ax.grid(True, alpha=0.3)

    if save_path is not None:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig, ax


def plot_adaptability_profile(
    x_range: Tuple[float, float], 
    d_res_values: List[float], 
    N_ord: List[int],
    num_x_points: int = 500,
    x0: float = 0.0,
    colors: Optional[List[str]] = None,
    title: Optional[str] = None,
    save_path: Optional[str] = None,
    fig_size: Tuple[float, float] = (10, 6)
) -> Tuple[Figure, Axes]:
    """
    Plot adaptability profiles A(x) for different d_res values.
    
    Args:
        x_range: Tuple (min_x, max_x) specifying the range of x values
        d_res_values: List of d_res values to plot
        N_ord: Set of orbital orders
        num_x_points: Number of points to sample along the x axis
        x0: Reference point for adaptability calculation
        colors: List of colors for each d_res value (if None, default colors are used)
        title: Plot title (if None, a default title is generated)
        save_path: Path to save the figure (if None, the figure is not saved)
        fig_size: Figure size in inches
        
    Returns:
        Tuple (fig, ax) containing the figure and axes
    """
    # Generate x values
    x_values = np.linspace(x_range[0], x_range[1], num_x_points)
    
    # Create the figure and axes
    fig, ax = plt.subplots(figsize=fig_size)
    
    # Use default colors if none provided
    if colors is None:
        colors = plt.cm.viridis(np.linspace(0, 1, len(d_res_values)))
    
    # Plot adaptability profile for each d_res value
    for i, d_res in enumerate(d_res_values):
        a_values = adaptability_array(x_values, d_res, N_ord, x0)
        ax.plot(x_values, a_values, label=f'$d_{{res}}={d_res}$', color=colors[i])
    
    # Set axis labels
    ax.set_xlabel('Configuration $x$')
    ax.set_ylabel('Adaptability $A(x, d_{res})$')
    
    # Set the title
    if title is None:
        title = f'Adaptability Profiles for Different $d_{{res}}$ values\n$N_{{ord}}=\\{{{N_ord[0]},...,{N_ord[-1]}\\}}$'
    ax.set_title(title)
    
    # Add grid lines and legend
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Save the figure if a path is provided
    if save_path is not None:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig, ax


def plot_grid_pathfinding_2d_background(
    grid_size: Tuple[int, int],
    start: Tuple[int, int],
    goal: Tuple[int, int],
    paths: Dict[str, List[Tuple[int, int]]],
    grid_to_xy_map: Callable[[int, int], Tuple[float, float]],
    d_res: float,
    N_ord: List[int],
    x0_vec: Tuple[float, float] = (0.0, 0.0),
    title: Optional[str] = None,
    save_path: Optional[str] = None,
    fig_size: Tuple[float, float] = (10, 8)
) -> Tuple[Figure, Axes]:
    """
    Plot paths on a grid with 2D adaptability values as the background.

    Args:
        grid_size: Tuple (rows, cols) specifying the grid dimensions.
        start: Tuple (row, col) of the start position.
        goal: Tuple (row, col) of the goal position.
        paths: Dictionary mapping path names to lists of (row, col) coordinates.
        grid_to_xy_map: Function mapping (row, col) to (x_val, y_val) for adaptability.
        d_res: Depth parameter for adaptability calculation.
        N_ord: Set of orbital orders.
        x0_vec: Reference point vector (x0_x, x0_y).
        title: Plot title. If None, a default is generated.
        save_path: Path to save the figure. If None, not saved.
        fig_size: Figure size.

    Returns:
        Tuple (fig, ax) containing the figure and axes.
    """
    rows, cols = grid_size
    fig, ax = plt.subplots(figsize=fig_size)

    A_grid = np.zeros((rows, cols))
    for r in range(rows):
        for c in range(cols):
            xy_val = grid_to_xy_map(r, c)
            A_grid[r, c] = adaptability_2d(xy_val, d_res, N_ord, x0_vec)

    im = ax.imshow(A_grid, cmap='viridis', origin='upper', interpolation='none')
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label('Adaptability $A((x,y), d_{res})$')

    path_colors = ['white', 'red', 'green', 'magenta', 'cyan', 'yellow']
    line_styles = ['-', '--', '-.', ':', '-', '--']
    for i, (path_name, path) in enumerate(paths.items()):
        path_array = np.array(path)
        ax.plot(path_array[:, 1], path_array[:, 0],
                color=path_colors[i % len(path_colors)],
                linestyle=line_styles[i % len(line_styles)],
                linewidth=2.5,
                label=path_name)

    ax.plot(start[1], start[0], 'bo', markersize=10, label='Start')
    ax.plot(goal[1], goal[0], 'rx', markersize=10, label='Goal')

    ax.set_xlabel('Column')
    ax.set_ylabel('Row')

    if title is None:
        title = (f'Pathfinding Comparison ({rows}x{cols} Grid, 2D Adaptability Background)\n'
                   f'$d_{{res}}={d_res:.2f}, N_{{ord}}=\\{{{N_ord[0]},...,{N_ord[-1]}\\}}, x0={x0_vec}$')
    ax.set_title(title)

    ax.grid(True, alpha=0.3)
    ax.legend(loc='best')

    ax.set_xticks(np.arange(-0.5, cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, rows, 1), minor=True)
    ax.grid(which='minor', color='black', linestyle='-', linewidth=0.5, alpha=0.2)

    ax.set_xlim(-0.5, cols - 0.5)
    ax.set_ylim(rows - 0.5, -0.5)

    if save_path is not None:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig, ax