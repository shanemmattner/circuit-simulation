"""Simulation functions for power supply."""

import numpy as np
from typing import Dict, Any, Optional
from .circuit import PowerSupplyCircuit


def simulate_power_supply(
    circuit: PowerSupplyCircuit,
    load_profile: str = "constant",
    duration: float = 100e-3,
    timestep: Optional[float] = None,
) -> Dict[str, Any]:
    """Simulate power supply.

    Args:
        circuit: Power supply circuit
        load_profile: Load type ("constant", "step", "pulse")
        duration: Simulation duration
        timestep: Time step

    Returns:
        Simulation results
    """
    if timestep is None:
        timestep = duration / 1000

    time = np.arange(0, duration + timestep, timestep)

    # Generate load current profile
    if load_profile == "constant":
        i_load = np.ones_like(time) * circuit.i_max * 0.5
    elif load_profile == "step":
        i_load = np.ones_like(time) * circuit.i_max * 0.2
        i_load[len(i_load) // 2 :] = circuit.i_max * 0.8
    elif load_profile == "pulse":
        period = duration / 5
        i_load = circuit.i_max * 0.5 * (np.sin(2 * np.pi * time / period) > 0)
    else:
        i_load = np.zeros_like(time)

    # Simulate output voltage response
    v_out = np.ones_like(time) * circuit.v_dc_output

    # Add load regulation effects
    regulation = circuit.calculate_load_regulation() / 100
    v_out = v_out * (1 - regulation * i_load / circuit.i_max)

    # Add output ripple
    ripple = circuit.calculate_output_ripple()
    v_out += ripple * np.sin(2 * np.pi * 120 * time)  # 120Hz ripple

    return {
        "time": time.tolist(),
        "v_out": v_out.tolist(),
        "i_load": i_load.tolist(),
        "regulation": regulation,
    }


def calculate_efficiency(circuit: PowerSupplyCircuit, load_current: float) -> Dict[str, float]:
    """Calculate efficiency at given load.

    Args:
        circuit: Power supply circuit
        load_current: Load current

    Returns:
        Efficiency data
    """
    power_out = circuit.v_dc_output * load_current

    if circuit.regulator_type == "linear":
        # Linear regulator losses
        power_in = circuit.v_filtered * load_current
    else:
        # Switching regulator (account for efficiency)
        efficiency = 0.85
        power_in = power_out / efficiency

    power_loss = power_in - power_out
    efficiency = (power_out / power_in) * 100 if power_in > 0 else 0

    return {
        "efficiency": efficiency,
        "power_in": power_in,
        "power_out": power_out,
        "power_loss": power_loss,
    }
