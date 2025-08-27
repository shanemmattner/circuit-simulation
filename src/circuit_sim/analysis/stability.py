"""
Stability analysis tools for transfer functions.
"""

from typing import Dict, Tuple, Optional
import numpy as np
from dataclasses import dataclass


@dataclass
class StabilityMetrics:
    """Container for stability analysis metrics."""

    phase_margin: float  # Degrees
    gain_margin: float  # dB
    phase_crossover_freq: float  # rad/s
    gain_crossover_freq: float  # rad/s
    is_stable: bool

    def __str__(self) -> str:
        """String representation of stability metrics."""
        return (
            f"Stability Analysis:\n"
            f"  Phase Margin: {self.phase_margin:.1f}°\n"
            f"  Gain Margin: {self.gain_margin:.1f} dB\n"
            f"  Phase Crossover: {self.phase_crossover_freq:.2f} rad/s\n"
            f"  Gain Crossover: {self.gain_crossover_freq:.2f} rad/s\n"
            f"  System is {'STABLE' if self.is_stable else 'UNSTABLE'}"
        )


def calculate_stability_margins(
    transfer_function, frequency_range: Optional[Tuple[float, float]] = None
) -> StabilityMetrics:
    """
    Calculate stability margins for a transfer function.

    Args:
        transfer_function: TransferFunction object to analyze
        frequency_range: Optional (min, max) frequency range in rad/s

    Returns:
        StabilityMetrics with phase/gain margins
    """
    # Default frequency range
    if frequency_range is None:
        frequency_range = (0.001, 10000)

    # Generate frequency vector
    frequencies = np.logspace(np.log10(frequency_range[0]), np.log10(frequency_range[1]), 1000)

    # Calculate frequency response
    response = transfer_function.frequency_response(frequencies)
    magnitude_db = 20 * np.log10(np.abs(response))
    phase_deg = np.angle(response, deg=True)

    # Unwrap phase for continuity
    phase_deg = np.unwrap(phase_deg * np.pi / 180) * 180 / np.pi

    # Find gain crossover (where |H| = 1 or 0 dB)
    gc_idx = np.where(np.diff(np.sign(magnitude_db)))[0]
    if len(gc_idx) > 0:
        gc_idx = gc_idx[0]
        gain_crossover_freq = frequencies[gc_idx]
        # Phase margin is 180° + phase at gain crossover
        phase_margin = 180 + phase_deg[gc_idx]
    else:
        gain_crossover_freq = 0
        phase_margin = np.inf

    # Find phase crossover (where phase = -180°)
    target_phase = -180
    pc_idx = np.where(np.diff(np.sign(phase_deg - target_phase)))[0]
    if len(pc_idx) > 0:
        pc_idx = pc_idx[0]
        phase_crossover_freq = frequencies[pc_idx]
        # Gain margin is -magnitude at phase crossover
        gain_margin = -magnitude_db[pc_idx]
    else:
        phase_crossover_freq = 0
        gain_margin = np.inf

    # Check stability
    is_stable = transfer_function.is_stable

    # Additional check: positive margins indicate stability
    if phase_margin > 0 and gain_margin > 0:
        is_stable = is_stable and True
    else:
        is_stable = False

    return StabilityMetrics(
        phase_margin=phase_margin,
        gain_margin=gain_margin,
        phase_crossover_freq=phase_crossover_freq,
        gain_crossover_freq=gain_crossover_freq,
        is_stable=is_stable,
    )
