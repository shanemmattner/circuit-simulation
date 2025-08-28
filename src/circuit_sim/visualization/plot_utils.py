"""Utility functions for plotting."""

import numpy as np
from typing import List, Dict, Any


def create_grid_lines(
    start: float, stop: float, scale: str = "linear", num_lines: int = 10
) -> np.ndarray:
    """Create grid line positions.

    Args:
        start: Start value
        stop: Stop value
        scale: "linear" or "log"
        num_lines: Number of grid lines

    Returns:
        Array of grid line positions
    """
    if scale == "log":
        # For log scale, create lines at powers of 10
        start_exp = np.log10(max(start, 1e-10))
        stop_exp = np.log10(max(stop, 1e-10))
        exponents = np.linspace(start_exp, stop_exp, num_lines)
        return 10**exponents
    else:
        return np.linspace(start, stop, num_lines)


def calculate_stability_margin(
    magnitude: np.ndarray, phase: np.ndarray, frequencies: np.ndarray
) -> Dict[str, Any]:
    """Calculate stability margins from frequency response.

    Args:
        magnitude: Magnitude response (linear)
        phase: Phase response (radians)
        frequencies: Frequency array

    Returns:
        Dictionary with stability margin information
    """
    # Convert to dB and degrees
    magnitude_db = 20 * np.log10(np.maximum(magnitude, 1e-10))
    phase_deg = np.degrees(phase)

    # Find gain crossover frequency (where magnitude = 0 dB)
    gain_crossover_idx = np.where(np.diff(np.sign(magnitude_db)))[0]
    if len(gain_crossover_idx) > 0:
        gain_crossover_freq = frequencies[gain_crossover_idx[0]]
        phase_margin_deg = 180 + phase_deg[gain_crossover_idx[0]]
    else:
        gain_crossover_freq = None
        phase_margin_deg = None

    # Find phase crossover frequency (where phase = -180°)
    phase_crossover_idx = np.where(np.diff(np.sign(phase_deg + 180)))[0]
    if len(phase_crossover_idx) > 0:
        phase_crossover_freq = frequencies[phase_crossover_idx[0]]
        gain_margin_db = -magnitude_db[phase_crossover_idx[0]]
    else:
        phase_crossover_freq = None
        gain_margin_db = None

    # Determine stability
    is_stable = True
    if gain_margin_db is not None and gain_margin_db < 0:
        is_stable = False
    if phase_margin_deg is not None and phase_margin_deg < 0:
        is_stable = False

    return {
        "gain_margin_db": gain_margin_db,
        "phase_margin_deg": phase_margin_deg,
        "gain_crossover_freq": gain_crossover_freq,
        "phase_crossover_freq": phase_crossover_freq,
        "is_stable": is_stable,
    }


def get_color_palette(palette_name: str, num_colors: int) -> List[str]:
    """Get color palette for plotting.

    Args:
        palette_name: Name of palette (default, professional, colorblind)
        num_colors: Number of colors needed

    Returns:
        List of color hex codes
    """
    palettes = {
        "default": [
            "#1f77b4",
            "#ff7f0e",
            "#2ca02c",
            "#d62728",
            "#9467bd",
            "#8c564b",
            "#e377c2",
            "#7f7f7f",
        ],
        "professional": [
            "#000000",
            "#555555",
            "#888888",
            "#bbbbbb",
            "#1f4788",
            "#2e7d32",
            "#c62828",
            "#f57c00",
        ],
        "colorblind": [
            "#0173B2",
            "#DE8F05",
            "#029E73",
            "#CC78BC",
            "#ECE133",
            "#56B4E9",
            "#F0E442",
            "#D55E00",
        ],
    }

    palette = palettes.get(palette_name, palettes["default"])

    # Repeat colors if needed
    while len(palette) < num_colors:
        palette = palette + palette

    return palette[:num_colors]


def count_encirclements(
    real: np.ndarray, imag: np.ndarray, point_real: float, point_imag: float
) -> int:
    """Count encirclements of a point in the complex plane.

    Uses the winding number algorithm.

    Args:
        real: Real part of trajectory
        imag: Imaginary part of trajectory
        point_real: Real part of point to check
        point_imag: Imaginary part of point to check

    Returns:
        Number of counter-clockwise encirclements
    """
    # Shift trajectory relative to the point
    shifted_real = real - point_real
    shifted_imag = imag - point_imag

    # Calculate angles
    angles = np.arctan2(shifted_imag, shifted_real)

    # Unwrap angles to avoid discontinuities
    angles = np.unwrap(angles)

    # Total angle change divided by 2π gives number of encirclements
    total_angle_change = angles[-1] - angles[0]
    encirclements = int(np.round(total_angle_change / (2 * np.pi)))

    return encirclements
