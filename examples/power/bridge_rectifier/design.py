"""Design functions for bridge rectifier power supplies."""

from typing import Optional

import numpy as np

from .circuit import BridgeRectifierCircuit


def design_power_supply(
    v_out: float,
    i_out: float,
    ripple_max: float = 1.0,
    v_ac_rms: Optional[float] = None,
    frequency: float = 60,
) -> BridgeRectifierCircuit:
    """Design a bridge rectifier power supply.

    Args:
        v_out: Desired DC output voltage
        i_out: Output current in amperes
        ripple_max: Maximum ripple voltage
        v_ac_rms: AC input voltage (RMS)
        frequency: AC frequency

    Returns:
        Configured BridgeRectifierCircuit
    """
    # Calculate load resistance
    r_load = v_out / i_out if i_out > 0 else 1000

    # If AC voltage not specified, choose based on output
    if v_ac_rms is None:
        # Need higher AC for headroom (diode drops + ripple)
        v_ac_rms = (v_out + 2 * 0.7 + ripple_max) / np.sqrt(2) * 1.2

    # Calculate required capacitor for ripple spec
    # Vripple = I/(2*f*C) => C = I/(2*f*Vripple)
    c_filter = i_out / (2 * frequency * ripple_max)

    # Round up to standard value
    c_filter = _round_to_standard_capacitor(c_filter * 2)  # Extra margin for ripple

    return BridgeRectifierCircuit(
        v_ac_rms=v_ac_rms,
        frequency=frequency,
        load_resistance=r_load,
        filter_capacitor=c_filter,
    )


def _round_to_standard_capacitor(value: float) -> float:
    """Round to standard capacitor value.

    Args:
        value: Capacitance in farads

    Returns:
        Standard capacitor value
    """
    # Common electrolytic values in µF
    standard_uf = [10, 22, 33, 47, 100, 220, 330, 470, 1000, 2200, 3300, 4700, 10000]

    value_uf = value * 1e6

    # Find closest standard value
    closest = min(standard_uf, key=lambda x: abs(x - value_uf))

    return closest * 1e-6
