"""Simulation functions for voltage divider circuit."""

from typing import Any, Dict, Tuple

import numpy as np

from .circuit import VoltageDividerCircuit


def simulate_voltage_divider(
    circuit: VoltageDividerCircuit, analysis_type: str = "dc", **kwargs
) -> Dict[str, Any]:
    """Simulate voltage divider circuit.

    Args:
        circuit: Voltage divider circuit instance
        analysis_type: Type of analysis ("dc", "sweep", "transient")
        **kwargs: Additional parameters for specific analysis types

    Returns:
        Dictionary containing simulation results
    """
    if analysis_type == "dc":
        return _simulate_dc(circuit)
    elif analysis_type == "sweep":
        return _simulate_sweep(circuit, **kwargs)
    elif analysis_type == "transient":
        return _simulate_transient(circuit, **kwargs)
    else:
        raise ValueError(f"Unknown analysis type: {analysis_type}")


def _simulate_dc(circuit: VoltageDividerCircuit) -> Dict[str, Any]:
    """Run DC operating point analysis.

    Args:
        circuit: Voltage divider circuit

    Returns:
        DC analysis results
    """
    # Calculate theoretical values (in real implementation, would use SPICE)
    vout = circuit.calculate_theoretical_output()

    # Calculate currents
    v_r1 = circuit.vin - vout
    i_r1 = v_r1 / circuit.r1
    i_r2 = vout / circuit.r2

    results = {
        "output_voltage": vout,
        "input_current": i_r1,
        "r1_current": i_r1,
        "r2_current": i_r2,
        "r1_voltage": v_r1,
        "r2_voltage": vout,
        "power_dissipation": circuit.calculate_power_dissipation(),
    }

    if circuit.r_load:
        results["load_current"] = vout / circuit.r_load

    return results


def _simulate_sweep(
    circuit: VoltageDividerCircuit,
    sweep_param: str = "vin",
    sweep_range: Tuple[float, float, float] = (0, 10, 0.5),
    **kwargs,
) -> Dict[str, Any]:
    """Run parameter sweep simulation.

    Args:
        circuit: Voltage divider circuit
        sweep_param: Parameter to sweep ("vin", "r1", "r2")
        sweep_range: (start, stop, step) for sweep

    Returns:
        Sweep simulation results
    """
    start, stop, step = sweep_range
    sweep_values = np.arange(start, stop + step, step)
    output_voltages = []

    # Store original value
    original_value = getattr(circuit, sweep_param)

    for value in sweep_values:
        # Update parameter
        setattr(circuit, sweep_param, value)

        # Calculate output
        if value > 0:  # Avoid division by zero
            vout = circuit.calculate_theoretical_output()
        else:
            vout = 0.0

        output_voltages.append(vout)

    # Restore original value
    setattr(circuit, sweep_param, original_value)

    return {
        "sweep_param": sweep_param,
        "sweep_values": sweep_values.tolist(),
        "output_voltages": output_voltages,
        "sweep_range": sweep_range,
    }


def _simulate_transient(
    circuit: VoltageDividerCircuit, duration: float = 1e-3, timestep: float = 1e-6, **kwargs
) -> Dict[str, Any]:
    """Run transient analysis (step response).

    Args:
        circuit: Voltage divider circuit
        duration: Simulation duration in seconds
        timestep: Time step in seconds

    Returns:
        Transient analysis results
    """
    time = np.arange(0, duration + timestep, timestep)

    # For ideal resistors, output reaches steady state immediately
    vout_steady = circuit.calculate_theoretical_output()

    # Add some RC time constant if capacitance is specified
    tau = kwargs.get("tau", 0)  # Time constant

    if tau > 0:
        # Exponential step response
        vout = vout_steady * (1 - np.exp(-time / tau))
    else:
        # Ideal response (instantaneous)
        vout = np.full_like(time, vout_steady)

    return {
        "time": time.tolist(),
        "output_voltage": vout.tolist(),
        "steady_state": vout_steady,
        "duration": duration,
        "timestep": timestep,
    }


def analyze_divider_ratio(
    circuit: VoltageDividerCircuit, tolerance: float = 0.05
) -> Dict[str, Any]:
    """Analyze voltage divider ratio with component tolerances.

    Args:
        circuit: Voltage divider circuit
        tolerance: Component tolerance (e.g., 0.05 for 5%)

    Returns:
        Analysis results including sensitivity
    """
    # Nominal values
    nominal_ratio = circuit.r2 / (circuit.r1 + circuit.r2)
    nominal_vout = circuit.calculate_theoretical_output()

    # Worst-case analysis
    r1_min = circuit.r1 * (1 - tolerance)
    r1_max = circuit.r1 * (1 + tolerance)
    r2_min = circuit.r2 * (1 - tolerance)
    r2_max = circuit.r2 * (1 + tolerance)

    # Best case for ratio (max R2, min R1)
    max_ratio = r2_max / (r1_min + r2_max)
    max_vout = circuit.vin * max_ratio

    # Worst case for ratio (min R2, max R1)
    min_ratio = r2_min / (r1_max + r2_min)
    min_vout = circuit.vin * min_ratio

    # Sensitivity analysis
    dr1_ratio = -circuit.r2 / ((circuit.r1 + circuit.r2) ** 2)
    dr2_ratio = circuit.r1 / ((circuit.r1 + circuit.r2) ** 2)

    return {
        "nominal_ratio": nominal_ratio,
        "nominal_output": nominal_vout,
        "min_ratio": min_ratio,
        "max_ratio": max_ratio,
        "min_output": min_vout,
        "max_output": max_vout,
        "tolerance": tolerance,
        "sensitivity": {
            "r1": dr1_ratio,  # d(ratio)/d(R1)
            "r2": dr2_ratio,  # d(ratio)/d(R2)
        },
        "variation_percent": ((max_vout - min_vout) / nominal_vout) * 100,
    }


def calculate_thevenin_equivalent(circuit: VoltageDividerCircuit) -> Dict[str, float]:
    """Calculate Thevenin equivalent circuit.

    Args:
        circuit: Voltage divider circuit

    Returns:
        Thevenin voltage and resistance
    """
    # Thevenin voltage (open circuit voltage)
    v_th = circuit.calculate_theoretical_output()

    # Thevenin resistance (looking back from output)
    r_th = (circuit.r1 * circuit.r2) / (circuit.r1 + circuit.r2)

    return {"v_thevenin": v_th, "r_thevenin": r_th}
