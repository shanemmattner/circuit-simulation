"""Simulation functions for bridge rectifier."""

import numpy as np
from typing import Dict, Any, Optional
from .circuit import BridgeRectifierCircuit


def simulate_rectifier(
    circuit: BridgeRectifierCircuit, duration: float = 100e-3, timestep: Optional[float] = None
) -> Dict[str, Any]:
    """Simulate bridge rectifier circuit.

    Args:
        circuit: Bridge rectifier circuit
        duration: Simulation duration
        timestep: Time step

    Returns:
        Simulation results
    """
    if timestep is None:
        timestep = 1 / (circuit.frequency * 1000)  # 1000 points per cycle

    time = np.arange(0, duration + timestep, timestep)

    # Input AC voltage
    v_in = circuit.v_ac_peak * np.sin(2 * np.pi * circuit.frequency * time)

    # Rectified output
    v_rectified = np.abs(v_in) - 2 * circuit.diode_drop
    v_rectified[v_rectified < 0] = 0  # No conduction below diode drops

    if circuit.filter_capacitor:
        # With filter capacitor
        v_out = _simulate_with_filter(v_rectified, time, circuit)
    else:
        v_out = v_rectified

    # Load current
    i_load = v_out / circuit.load_resistance

    # Calculate output frequency (ripple frequency)
    # For full-wave, it's 2x input frequency
    output_frequency = 2 * circuit.frequency

    return {
        "time": time.tolist(),
        "v_in": v_in.tolist(),
        "v_out": v_out.tolist(),
        "i_load": i_load.tolist(),
        "output_frequency": output_frequency,
    }


def _simulate_with_filter(
    v_rectified: np.ndarray, time: np.ndarray, circuit: BridgeRectifierCircuit
) -> np.ndarray:
    """Simulate with filter capacitor.

    Args:
        v_rectified: Rectified voltage
        time: Time array
        circuit: Bridge rectifier circuit

    Returns:
        Filtered output voltage
    """
    v_out = np.zeros_like(v_rectified)
    v_cap = 0  # Initial capacitor voltage

    dt = time[1] - time[0] if len(time) > 1 else 1e-6
    rc = circuit.load_resistance * circuit.filter_capacitor

    for i in range(len(time)):
        if v_rectified[i] > v_cap:
            # Diode conducts, capacitor charges
            v_cap = v_rectified[i]
        else:
            # Diode off, capacitor discharges
            v_cap = v_cap * np.exp(-dt / rc)

        v_out[i] = v_cap

    return v_out


def calculate_ripple(circuit: BridgeRectifierCircuit) -> Dict[str, Any]:
    """Calculate ripple characteristics.

    Args:
        circuit: Bridge rectifier circuit

    Returns:
        Ripple analysis
    """
    ripple_voltage = circuit.calculate_ripple_voltage()
    dc_output = circuit.calculate_output_voltage()

    return {
        "ripple_voltage": ripple_voltage,
        "ripple_percent": (ripple_voltage / dc_output) * 100 if dc_output > 0 else 100,
        "ripple_frequency": 2 * circuit.frequency,  # Full-wave
        "dc_output": dc_output,
        "rms_ripple": ripple_voltage / (2 * np.sqrt(3)),  # Triangular wave
    }
