"""
Time domain response calculations for transfer functions.
"""

from typing import Tuple, Optional
import numpy as np
from scipy import signal


def step_response(
    transfer_function, time: Optional[np.ndarray] = None, settle_time: Optional[float] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate unit step response of transfer function.

    Args:
        transfer_function: TransferFunction object
        time: Time vector, auto-generated if None
        settle_time: Time to simulate, auto-estimated if None

    Returns:
        Tuple of (time, response) arrays
    """
    # Convert to scipy LTI system
    num = transfer_function.numerator_coeffs
    den = transfer_function.denominator_coeffs
    sys = signal.TransferFunction(num, den)

    # Auto-generate time vector if not provided
    if time is None:
        if settle_time is None:
            # Estimate settling time from dominant pole
            poles = transfer_function.poles
            if len(poles) > 0:
                # Find slowest pole (closest to imaginary axis)
                real_parts = np.real(poles)
                real_parts = real_parts[real_parts < 0]  # Only stable poles
                if len(real_parts) > 0:
                    slowest_pole = np.max(real_parts)
                    settle_time = -4 / slowest_pole  # 4 time constants
                else:
                    settle_time = 10  # Default
            else:
                settle_time = 10

        time = np.linspace(0, settle_time, 1000)

    # Calculate step response
    t, y = signal.step(sys, T=time)
    return t, y


def impulse_response(
    transfer_function, time: Optional[np.ndarray] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate impulse response of transfer function.

    Args:
        transfer_function: TransferFunction object
        time: Time vector, auto-generated if None

    Returns:
        Tuple of (time, response) arrays
    """
    # Convert to scipy LTI system
    num = transfer_function.numerator_coeffs
    den = transfer_function.denominator_coeffs
    sys = signal.TransferFunction(num, den)

    # Auto-generate time vector if not provided
    if time is None:
        # Use same logic as step response
        time, _ = step_response(transfer_function)

    # Calculate impulse response
    t, y = signal.impulse(sys, T=time)
    return t, y


def calculate_rise_time(
    time: np.ndarray, response: np.ndarray, lower: float = 0.1, upper: float = 0.9
) -> float:
    """
    Calculate rise time (time from lower% to upper% of final value).

    Args:
        time: Time vector
        response: Step response values
        lower: Lower percentage (default 10%)
        upper: Upper percentage (default 90%)

    Returns:
        Rise time in same units as time vector
    """
    final_value = response[-1]
    lower_val = lower * final_value
    upper_val = upper * final_value

    # Find crossing times
    lower_idx = np.where(response >= lower_val)[0]
    upper_idx = np.where(response >= upper_val)[0]

    if len(lower_idx) > 0 and len(upper_idx) > 0:
        t_lower = time[lower_idx[0]]
        t_upper = time[upper_idx[0]]
        return float(t_upper - t_lower)
    return float(np.nan)


def calculate_settling_time(
    time: np.ndarray, response: np.ndarray, tolerance: float = 0.02
) -> float:
    """
    Calculate settling time (time to stay within tolerance of final value).

    Args:
        time: Time vector
        response: Step response values
        tolerance: Tolerance band (default 2%)

    Returns:
        Settling time in same units as time vector
    """
    final_value = response[-1]
    upper_bound = final_value * (1 + tolerance)
    lower_bound = final_value * (1 - tolerance)

    # Find where response enters and stays within bounds
    within_bounds = (response >= lower_bound) & (response <= upper_bound)

    # Find last time it exits the bounds
    exits_bounds = np.where(~within_bounds)[0]
    if len(exits_bounds) > 0:
        last_exit_idx = exits_bounds[-1]
        if last_exit_idx < len(time) - 1:
            return float(time[last_exit_idx + 1])

    # If always within bounds or never settles
    if within_bounds[0]:
        return float(time[0])
    return float(np.nan)


def calculate_overshoot(response: np.ndarray) -> float:
    """
    Calculate percent overshoot of step response.

    Args:
        response: Step response values

    Returns:
        Percent overshoot (0-100)
    """
    final_value = response[-1]
    if final_value == 0:
        return 0

    peak_value = np.max(response)
    overshoot = (peak_value - final_value) / final_value * 100
    return float(max(0, overshoot))
