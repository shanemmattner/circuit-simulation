"""Simulation functions for op-amp circuits."""

from typing import Any, Dict

import numpy as np

from .circuit import OpAmpCircuit


def simulate_opamp(
    circuit: OpAmpCircuit, analysis_type: str = "dc", **kwargs
) -> Dict[str, Any]:
    """Simulate op-amp circuit.

    Args:
        circuit: Op-amp circuit instance
        analysis_type: Type of analysis ("dc", "ac", "transient")
        **kwargs: Additional parameters

    Returns:
        Simulation results
    """
    if analysis_type == "dc":
        return _simulate_dc(circuit, **kwargs)
    elif analysis_type == "ac":
        return _simulate_ac(circuit, **kwargs)
    elif analysis_type == "transient":
        return _simulate_transient(circuit, **kwargs)
    else:
        raise ValueError(f"Unknown analysis type: {analysis_type}")


def _simulate_dc(
    circuit: OpAmpCircuit, vin_range: tuple = (-1, 1, 0.01)
) -> Dict[str, Any]:
    """Run DC sweep simulation.

    Args:
        circuit: Op-amp circuit
        vin_range: (start, stop, step) for input voltage

    Returns:
        DC analysis results
    """
    start, stop, step = vin_range
    vin_values = np.arange(start, stop + step, step)
    vout_values = []

    ideal_gain = circuit.calculate_ideal_gain()

    for vin in vin_values:
        if circuit.model == "ideal" and ideal_gain is not None:
            # Ideal op-amp calculation
            vout = ideal_gain * vin

            # Apply supply rail limiting
            vout = np.clip(vout, circuit.vee + 1, circuit.vcc - 1)
        else:
            # More realistic with saturation
            if ideal_gain is not None:
                vout = ideal_gain * vin

                # Saturation effects
                if abs(vout) > abs(circuit.vcc) - 2:
                    vout = np.sign(vout) * (abs(circuit.vcc) - 2)
            else:
                vout = 0

        vout_values.append(vout)

    # Calculate for single operating point
    if circuit.vin is not None:
        if ideal_gain is not None:
            output_voltage = ideal_gain * circuit.vin
            output_voltage = np.clip(output_voltage, circuit.vee + 1, circuit.vcc - 1)
            input_current = circuit.vin / circuit.calculate_input_impedance()
        else:
            output_voltage = 0
            input_current = 0
    else:
        output_voltage = vout_values[len(vout_values) // 2]
        input_current = 0

    return {
        "input_voltage": vin_values.tolist(),
        "output_voltage": output_voltage,  # Single point
        "output_voltages": vout_values,  # Sweep
        "input_current": input_current,
        "gain": ideal_gain,
        "analysis_type": "dc",
    }


def _simulate_ac(
    circuit: OpAmpCircuit,
    start_freq: float = 1,
    stop_freq: float = 1e6,
    points_per_decade: int = 20,
) -> Dict[str, Any]:
    """Run AC frequency response analysis.

    Args:
        circuit: Op-amp circuit
        start_freq: Starting frequency in Hz
        stop_freq: Stopping frequency in Hz
        points_per_decade: Number of points per decade

    Returns:
        AC analysis results
    """
    # Generate frequency points
    decades = np.log10(stop_freq / start_freq)
    num_points = int(decades * points_per_decade)
    frequencies = np.logspace(np.log10(start_freq), np.log10(stop_freq), num_points)

    ideal_gain = circuit.calculate_ideal_gain() or 1
    bandwidth = circuit.calculate_bandwidth() or 1e6

    gains = []
    phases = []

    for freq in frequencies:
        if circuit.config == "integrator":
            # Integrator: Gain = -1/(jωRC)
            omega = 2 * np.pi * freq
            h = -1 / (1j * omega * circuit.r_in * circuit.c_feedback)
            gain = abs(h)
            phase = np.degrees(np.angle(h))
        else:
            # Single-pole rolloff model
            h = ideal_gain / (1 + 1j * freq / bandwidth)
            gain = abs(h)
            phase = np.degrees(np.angle(h))

        gains.append(gain)
        phases.append(phase)

    # Convert to dB
    gains_db = [20 * np.log10(g) if g > 0 else -100 for g in gains]

    return {
        "frequency": frequencies.tolist(),
        "gain": gains,
        "gain_db": gains_db,
        "phase": phases,
        "bandwidth": bandwidth,
        "dc_gain": ideal_gain,
        "analysis_type": "ac",
    }


def _simulate_transient(
    circuit: OpAmpCircuit,
    duration: float = 1e-3,
    timestep: float = None,
    input_type: str = "step",
    step_amplitude: float = None,
    frequency: float = 1000,
) -> Dict[str, Any]:
    """Run transient analysis.

    Args:
        circuit: Op-amp circuit
        duration: Simulation duration in seconds
        timestep: Time step (default: duration/1000)
        input_type: "step", "sine", "square", "triangle"
        step_amplitude: Amplitude for step input
        frequency: Frequency for periodic inputs

    Returns:
        Transient analysis results
    """
    if timestep is None:
        timestep = duration / 1000

    time = np.arange(0, duration + timestep, timestep)

    # Generate input signal
    if step_amplitude is None:
        step_amplitude = circuit.vin

    if input_type == "step":
        input_signal = np.ones_like(time) * step_amplitude
        input_signal[0] = 0
    elif input_type == "sine":
        input_signal = step_amplitude * np.sin(2 * np.pi * frequency * time)
    elif input_type == "square":
        input_signal = step_amplitude * np.sign(np.sin(2 * np.pi * frequency * time))
    elif input_type == "triangle":
        period = 1 / frequency
        input_signal = step_amplitude * (
            2 * np.abs(2 * (time / period - np.floor(time / period + 0.5))) - 1
        )
    else:
        input_signal = np.zeros_like(time)

    # Calculate output response
    output = calculate_transient_response(circuit, time, input_signal)

    return {
        "time": time.tolist(),
        "input": input_signal.tolist(),
        "output": output.tolist(),
        "duration": duration,
        "timestep": timestep,
        "input_type": input_type,
        "analysis_type": "transient",
    }


def calculate_transient_response(
    circuit: OpAmpCircuit, time: np.ndarray, input_signal: np.ndarray
) -> np.ndarray:
    """Calculate transient response.

    Args:
        circuit: Op-amp circuit
        time: Time array
        input_signal: Input signal array

    Returns:
        Output signal array
    """
    output = np.zeros_like(input_signal)
    ideal_gain = circuit.calculate_ideal_gain() or 1

    if circuit.config == "integrator":
        # Integrator response
        dt = time[1] - time[0] if len(time) > 1 else 1e-6
        for i in range(1, len(time)):
            # Integration: Vout = -(1/RC) * integral(Vin dt)
            output[i] = output[i - 1] - (input_signal[i] * dt) / (
                circuit.r_in * circuit.c_feedback
            )

            # Apply saturation
            output[i] = np.clip(output[i], circuit.vee + 1, circuit.vcc - 1)

    elif circuit.slew_rate:
        # Apply slew rate limiting
        dt = time[1] - time[0] if len(time) > 1 else 1e-6

        for i in range(len(time)):
            target = ideal_gain * input_signal[i]

            if i == 0:
                output[i] = 0
            else:
                # Maximum change limited by slew rate
                max_change = circuit.slew_rate * dt
                actual_change = target - output[i - 1]

                if abs(actual_change) > max_change:
                    actual_change = np.sign(actual_change) * max_change

                output[i] = output[i - 1] + actual_change

            # Apply saturation
            output[i] = np.clip(output[i], circuit.vee + 1, circuit.vcc - 1)

    else:
        # Ideal response with bandwidth limiting
        bandwidth = circuit.calculate_bandwidth() or 1e6
        tau = 1 / (2 * np.pi * bandwidth)
        dt = time[1] - time[0] if len(time) > 1 else 1e-6

        for i in range(len(time)):
            target = ideal_gain * input_signal[i]

            if i == 0:
                output[i] = 0
            else:
                # First-order response
                output[i] = output[i - 1] + (target - output[i - 1]) * (
                    1 - np.exp(-dt / tau)
                )

            # Apply saturation
            output[i] = np.clip(output[i], circuit.vee + 1, circuit.vcc - 1)

    return output


def calculate_frequency_response(
    circuit: OpAmpCircuit, frequencies: np.ndarray
) -> Dict[str, Any]:
    """Calculate frequency response at specific frequencies.

    Args:
        circuit: Op-amp circuit
        frequencies: Array of frequencies in Hz

    Returns:
        Frequency response data
    """
    ideal_gain = circuit.calculate_ideal_gain() or 1
    bandwidth = circuit.calculate_bandwidth() or 1e6

    gains = []
    phases = []

    for freq in frequencies:
        if circuit.config == "integrator":
            omega = 2 * np.pi * freq
            h = -1 / (1j * omega * circuit.r_in * circuit.c_feedback)
        else:
            # Single-pole model
            h = ideal_gain / (1 + 1j * freq / bandwidth)

        gains.append(abs(h))
        phases.append(np.degrees(np.angle(h)))

    return {
        "frequency": frequencies.tolist(),
        "gain": gains,
        "gain_db": [20 * np.log10(g) if g > 0 else -100 for g in gains],
        "phase": phases,
    }
