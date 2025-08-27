"""Simulation functions for RC filter circuit."""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from .circuit import RCFilterCircuit


def simulate_rc_filter(
    circuit: RCFilterCircuit, analysis_type: str = "ac", **kwargs
) -> Dict[str, Any]:
    """Simulate RC filter circuit.

    Args:
        circuit: RC filter circuit instance
        analysis_type: Type of analysis ("ac", "transient", "dc")
        **kwargs: Additional parameters for specific analysis types

    Returns:
        Dictionary containing simulation results
    """
    if analysis_type == "ac":
        return _simulate_ac(circuit, **kwargs)
    elif analysis_type == "transient":
        return _simulate_transient(circuit, **kwargs)
    elif analysis_type == "dc":
        return _simulate_dc(circuit)
    else:
        raise ValueError(f"Unknown analysis type: {analysis_type}")


def _simulate_ac(
    circuit: RCFilterCircuit,
    start_freq: float = 1,
    stop_freq: float = 100000,
    points_per_decade: int = 20,
) -> Dict[str, Any]:
    """Run AC frequency response analysis.

    Args:
        circuit: RC filter circuit
        start_freq: Starting frequency in Hz
        stop_freq: Stopping frequency in Hz
        points_per_decade: Number of points per decade

    Returns:
        AC analysis results
    """
    # Generate logarithmic frequency points
    decades = np.log10(stop_freq / start_freq)
    num_points = int(decades * points_per_decade)
    frequencies = np.logspace(np.log10(start_freq), np.log10(stop_freq), num_points)

    # Calculate response at each frequency
    magnitudes = []
    phases = []
    magnitudes_db = []

    for freq in frequencies:
        mag = circuit.magnitude_response(freq)
        phase = circuit.phase_response(freq)
        mag_db = circuit.magnitude_db(freq)

        magnitudes.append(mag)
        phases.append(phase)
        magnitudes_db.append(mag_db)

    return {
        "frequency": frequencies.tolist(),
        "magnitude": magnitudes,
        "phase_deg": phases,
        "magnitude_db": magnitudes_db,
        "cutoff_frequency": circuit.cutoff_frequency,
        "analysis_type": "ac",
    }


def _simulate_transient(
    circuit: RCFilterCircuit,
    duration: float = None,
    timestep: float = None,
    input_type: str = "step",
) -> Dict[str, Any]:
    """Run transient analysis.

    Args:
        circuit: RC filter circuit
        duration: Simulation duration in seconds (default: 10 time constants)
        timestep: Time step in seconds (default: duration/1000)
        input_type: Type of input signal ("step", "pulse", "sine")

    Returns:
        Transient analysis results
    """
    if duration is None:
        duration = 10 * circuit.time_constant

    if timestep is None:
        timestep = duration / 1000

    time = np.arange(0, duration + timestep, timestep)

    # Generate input signal
    if input_type == "step":
        input_signal = np.ones_like(time) * circuit.vin
        input_signal[0] = 0  # Start from 0
    elif input_type == "pulse":
        # Square wave with period = 4 * tau
        period = 4 * circuit.time_constant
        input_signal = circuit.vin * (np.floor(2 * time / period) % 2)
    elif input_type == "sine":
        # Sine wave at cutoff frequency
        input_signal = circuit.vin * np.sin(2 * np.pi * circuit.cutoff_frequency * time)
    else:
        raise ValueError(f"Unknown input type: {input_type}")

    # Calculate output using differential equation solution
    output = calculate_step_response(circuit, time, input_signal)

    return {
        "time": time.tolist(),
        "input": input_signal.tolist(),
        "output": output.tolist(),
        "time_constant": circuit.time_constant,
        "duration": duration,
        "timestep": timestep,
        "input_type": input_type,
        "analysis_type": "transient",
    }


def _simulate_dc(circuit: RCFilterCircuit) -> Dict[str, Any]:
    """Run DC analysis (steady-state).

    Args:
        circuit: RC filter circuit

    Returns:
        DC analysis results
    """
    # At DC (f=0), capacitor is open circuit
    if circuit.filter_type == "lowpass":
        # Lowpass passes DC
        dc_gain = 1.0
        output_voltage = circuit.vin
    else:  # highpass
        # Highpass blocks DC
        dc_gain = 0.0
        output_voltage = 0.0

    return {
        "input_voltage": circuit.vin,
        "output_voltage": output_voltage,
        "dc_gain": dc_gain,
        "analysis_type": "dc",
    }


def calculate_frequency_response(circuit: RCFilterCircuit, frequencies) -> Dict[str, Any]:
    """Calculate analytical frequency response.

    Args:
        circuit: RC filter circuit
        frequencies: Array or list of frequencies in Hz

    Returns:
        Frequency response data
    """
    # Convert to numpy array if needed
    if not isinstance(frequencies, np.ndarray):
        frequencies = np.array(frequencies)

    magnitudes = []
    phases = []
    magnitudes_db = []

    for freq in frequencies:
        h = circuit.transfer_function(freq)
        mag = abs(h)
        phase = np.degrees(np.angle(h))
        mag_db = 20 * np.log10(mag) if mag > 0 else -100

        magnitudes.append(mag)
        phases.append(phase)
        magnitudes_db.append(mag_db)

    return {
        "frequency": frequencies.tolist(),
        "magnitude": magnitudes,
        "phase": phases,
        "magnitude_db": magnitudes_db,
    }


def calculate_step_response(
    circuit: RCFilterCircuit, time: np.ndarray, input_signal: np.ndarray = None
) -> np.ndarray:
    """Calculate step response using analytical solution.

    Args:
        circuit: RC filter circuit
        time: Time array
        input_signal: Input signal array (default: unit step)

    Returns:
        Output signal array
    """
    if input_signal is None:
        input_signal = np.ones_like(time)

    output = np.zeros_like(time)
    tau = circuit.time_constant

    if circuit.filter_type == "lowpass":
        # Lowpass step response: Vout = Vin * (1 - exp(-t/tau))
        for i in range(1, len(time)):
            dt = time[i] - time[i - 1]
            # Exponential charging/discharging
            output[i] = output[i - 1] + (input_signal[i] - output[i - 1]) * (1 - np.exp(-dt / tau))

    else:  # highpass
        # Highpass step response: Vout = Vin * exp(-t/tau)
        for i in range(1, len(time)):
            dt = time[i] - time[i - 1]
            # Derivative of input plus exponential decay
            input_derivative = (input_signal[i] - input_signal[i - 1]) / dt if dt > 0 else 0
            output[i] = output[i - 1] * np.exp(-dt / tau) + input_derivative * tau

    return output


def analyze_filter_performance(
    circuit: RCFilterCircuit, test_frequency: float = None
) -> Dict[str, Any]:
    """Analyze filter performance metrics.

    Args:
        circuit: RC filter circuit
        test_frequency: Frequency to test (default: cutoff frequency)

    Returns:
        Performance metrics
    """
    if test_frequency is None:
        test_frequency = circuit.cutoff_frequency

    # Calculate response at test frequency
    h = circuit.transfer_function(test_frequency)
    mag = abs(h)
    phase = np.degrees(np.angle(h))

    # Calculate bandwidth (for first-order filter, BW = fc)
    bandwidth = circuit.cutoff_frequency

    # Calculate rise time (10% to 90%)
    rise_time = 2.2 * circuit.time_constant

    # Calculate settling time (to within 2%)
    settling_time = 4 * circuit.time_constant

    return {
        "test_frequency": test_frequency,
        "magnitude": mag,
        "magnitude_db": 20 * np.log10(mag) if mag > 0 else -100,
        "phase_deg": phase,
        "bandwidth_hz": bandwidth,
        "rise_time_s": rise_time,
        "settling_time_s": settling_time,
        "time_constant_s": circuit.time_constant,
        "cutoff_frequency_hz": circuit.cutoff_frequency,
        "quality_factor": 0.707,  # Q factor for first-order RC filter
        "rolloff_rate_db_per_decade": -20,
        "rolloff_rate_db_per_octave": -6,
    }


def calculate_noise_performance(
    circuit: RCFilterCircuit, temperature: float = 300, bandwidth: float = None
) -> Dict[str, float]:
    """Calculate noise performance of RC filter.

    Args:
        circuit: RC filter circuit
        temperature: Temperature in Kelvin (default: 300K)
        bandwidth: Noise bandwidth in Hz (default: filter bandwidth)

    Returns:
        Noise performance metrics
    """
    if bandwidth is None:
        # For first-order RC filter, noise bandwidth = π/2 * f_3dB
        bandwidth = np.pi / 2 * circuit.cutoff_frequency

    # Boltzmann constant
    k = 1.38e-23  # J/K

    # Johnson-Nyquist noise from resistor
    # v_n = sqrt(4 * k * T * R * BW)
    resistor_noise = np.sqrt(4 * k * temperature * circuit.r * bandwidth)

    # Noise figure (for passive filter, NF = 1 or 0 dB)
    noise_figure_db = 0.0

    return {
        "resistor_noise_vrms": resistor_noise,
        "resistor_noise_nv_per_sqrt_hz": np.sqrt(4 * k * temperature * circuit.r) * 1e9,
        "noise_bandwidth_hz": bandwidth,
        "noise_figure_db": noise_figure_db,
        "temperature_k": temperature,
    }
