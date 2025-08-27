"""Simulation functions for RLC resonance circuit."""

import numpy as np
from typing import Dict, Any, Optional, List
from .circuit import RLCResonanceCircuit


def simulate_rlc_circuit(
    circuit: RLCResonanceCircuit, analysis_type: str = "ac", **kwargs
) -> Dict[str, Any]:
    """Simulate RLC resonance circuit.

    Args:
        circuit: RLC resonance circuit instance
        analysis_type: Type of analysis ("ac", "transient", "impedance")
        **kwargs: Additional parameters for specific analysis types

    Returns:
        Dictionary containing simulation results
    """
    if analysis_type == "ac":
        return _simulate_ac(circuit, **kwargs)
    elif analysis_type == "transient":
        return _simulate_transient(circuit, **kwargs)
    elif analysis_type == "impedance":
        return _simulate_impedance(circuit, **kwargs)
    else:
        raise ValueError(f"Unknown analysis type: {analysis_type}")


def _simulate_ac(
    circuit: RLCResonanceCircuit,
    start_freq: float = None,
    stop_freq: float = None,
    points_per_decade: int = 30,
) -> Dict[str, Any]:
    """Run AC frequency response analysis.

    Args:
        circuit: RLC circuit
        start_freq: Starting frequency (default: f0/100)
        stop_freq: Stopping frequency (default: f0*100)
        points_per_decade: Number of points per decade

    Returns:
        AC analysis results
    """
    if start_freq is None:
        start_freq = circuit.resonant_frequency / 100
    if stop_freq is None:
        stop_freq = circuit.resonant_frequency * 100

    # Generate frequency points
    decades = np.log10(stop_freq / start_freq)
    num_points = int(decades * points_per_decade)
    frequencies = np.logspace(np.log10(start_freq), np.log10(stop_freq), num_points)

    # Calculate response
    magnitudes = []
    phases = []
    impedances = []
    impedance_mags = []
    impedance_phases = []

    for freq in frequencies:
        # Transfer function
        h = circuit.transfer_function(freq)
        magnitudes.append(abs(h))
        phases.append(np.degrees(np.angle(h)))

        # Impedance
        z = circuit.calculate_impedance(freq)
        impedances.append(abs(z))
        impedance_mags.append(abs(z))
        impedance_phases.append(np.degrees(np.angle(z)))

    return {
        "frequency": frequencies.tolist(),
        "magnitude": magnitudes,
        "phase": phases,
        "magnitude_db": [20 * np.log10(m) if m > 0 else -100 for m in magnitudes],
        "impedance": impedance_mags,
        "impedance_phase": impedance_phases,
        "resonant_frequency": circuit.resonant_frequency,
        "q_factor": circuit.q_factor,
        "bandwidth": circuit.bandwidth,
        "analysis_type": "ac",
    }


def _simulate_transient(
    circuit: RLCResonanceCircuit,
    duration: float = None,
    timestep: float = None,
    input_type: str = "step",
) -> Dict[str, Any]:
    """Run transient analysis.

    Args:
        circuit: RLC circuit
        duration: Simulation duration (default: 20 periods)
        timestep: Time step (default: period/100)
        input_type: Type of input ("step", "impulse", "sine")

    Returns:
        Transient analysis results
    """
    period = 1 / circuit.resonant_frequency

    if duration is None:
        duration = 20 * period
    if timestep is None:
        timestep = period / 100

    time = np.arange(0, duration + timestep, timestep)

    # Generate input signal
    if input_type == "step":
        input_signal = np.ones_like(time) * circuit.vin
        input_signal[0] = 0
    elif input_type == "impulse":
        input_signal = np.zeros_like(time)
        input_signal[0] = circuit.vin / timestep  # Unit impulse
    elif input_type == "sine":
        # Sine at resonant frequency
        input_signal = circuit.vin * np.sin(2 * np.pi * circuit.resonant_frequency * time)
    else:
        raise ValueError(f"Unknown input type: {input_type}")

    # Calculate response using state-space or analytical solution
    voltage, current = calculate_step_response(circuit, time, input_signal)

    return {
        "time": time.tolist(),
        "input": input_signal.tolist(),
        "voltage": voltage.tolist(),
        "current": current.tolist(),
        "period": period,
        "damping_type": circuit.damping_type,
        "analysis_type": "transient",
    }


def _simulate_impedance(
    circuit: RLCResonanceCircuit,
    start_freq: float = None,
    stop_freq: float = None,
    num_points: int = 200,
) -> Dict[str, Any]:
    """Run impedance analysis.

    Args:
        circuit: RLC circuit
        start_freq: Starting frequency
        stop_freq: Stopping frequency
        num_points: Number of frequency points

    Returns:
        Impedance analysis results
    """
    if start_freq is None:
        start_freq = circuit.resonant_frequency / 100
    if stop_freq is None:
        stop_freq = circuit.resonant_frequency * 100

    frequencies = np.logspace(np.log10(start_freq), np.log10(stop_freq), num_points)

    spectrum = calculate_impedance_spectrum(circuit, frequencies)

    return spectrum


def calculate_impedance_spectrum(
    circuit: RLCResonanceCircuit, frequencies: np.ndarray
) -> Dict[str, Any]:
    """Calculate impedance spectrum.

    Args:
        circuit: RLC circuit
        frequencies: Array of frequencies in Hz

    Returns:
        Impedance spectrum data
    """
    impedance_mag = []
    impedance_phase = []
    real_part = []
    imaginary_part = []

    for freq in frequencies:
        z = circuit.calculate_impedance(freq)
        impedance_mag.append(abs(z))
        impedance_phase.append(np.degrees(np.angle(z)))
        real_part.append(z.real)
        imaginary_part.append(z.imag)

    return {
        "frequency": frequencies.tolist(),
        "impedance_mag": impedance_mag,
        "impedance_phase": impedance_phase,
        "real_part": real_part,
        "imaginary_part": imaginary_part,
        "resonant_frequency": circuit.resonant_frequency,
    }


def calculate_step_response(
    circuit: RLCResonanceCircuit, time: np.ndarray, input_signal: np.ndarray = None
) -> tuple:
    """Calculate step response using analytical solution.

    Args:
        circuit: RLC circuit
        time: Time array
        input_signal: Input signal (default: unit step)

    Returns:
        Tuple of (voltage, current) arrays
    """
    if input_signal is None:
        input_signal = np.ones_like(time)

    voltage = np.zeros_like(time)
    current = np.zeros_like(time)

    # Natural frequency and damping
    omega_n = circuit.angular_frequency
    zeta = circuit.damping_ratio

    if circuit.damping_type == "underdamped":
        # Underdamped response
        omega_d = circuit.damped_frequency * 2 * np.pi

        for i in range(1, len(time)):
            t = time[i]
            # Step response for underdamped system
            if circuit.topology == "series":
                # Voltage across capacitor
                voltage[i] = input_signal[i] * (
                    1
                    - np.exp(-zeta * omega_n * t)
                    * (np.cos(omega_d * t) + (zeta * omega_n / omega_d) * np.sin(omega_d * t))
                )
                # Current through circuit
                current[i] = (
                    (input_signal[i] / circuit.r)
                    * np.exp(-zeta * omega_n * t)
                    * np.sin(omega_d * t)
                )
            else:  # parallel
                # Different response for parallel
                voltage[i] = input_signal[i] * np.exp(-zeta * omega_n * t) * np.cos(omega_d * t)
                current[i] = (input_signal[i] / circuit.r) * (
                    1 - np.exp(-zeta * omega_n * t) * np.cos(omega_d * t)
                )

    elif circuit.damping_type == "critically_damped":
        # Critically damped response
        for i in range(1, len(time)):
            t = time[i]
            if circuit.topology == "series":
                voltage[i] = input_signal[i] * (1 - np.exp(-omega_n * t) * (1 + omega_n * t))
                current[i] = (input_signal[i] / circuit.r) * omega_n * t * np.exp(-omega_n * t)
            else:
                voltage[i] = input_signal[i] * np.exp(-omega_n * t) * (1 + omega_n * t)
                current[i] = (input_signal[i] / circuit.r) * (
                    1 - np.exp(-omega_n * t) * (1 + omega_n * t)
                )

    else:  # overdamped
        # Overdamped response
        alpha = zeta * omega_n
        beta = omega_n * np.sqrt(zeta**2 - 1)

        for i in range(1, len(time)):
            t = time[i]
            if circuit.topology == "series":
                voltage[i] = input_signal[i] * (
                    1
                    - ((alpha + beta) / (2 * beta)) * np.exp(-(alpha - beta) * t)
                    + ((alpha - beta) / (2 * beta)) * np.exp(-(alpha + beta) * t)
                )
                current[i] = (input_signal[i] / (circuit.r * 2 * beta)) * (
                    np.exp(-(alpha - beta) * t) - np.exp(-(alpha + beta) * t)
                )
            else:
                voltage[i] = input_signal[i] * (
                    ((alpha + beta) / (2 * beta)) * np.exp(-(alpha - beta) * t)
                    - ((alpha - beta) / (2 * beta)) * np.exp(-(alpha + beta) * t)
                )
                current[i] = (input_signal[i] / circuit.r) * (1 - voltage[i] / input_signal[i])

    return voltage, current


def calculate_frequency_response(
    circuit: RLCResonanceCircuit, frequencies: np.ndarray
) -> Dict[str, Any]:
    """Calculate frequency response.

    Args:
        circuit: RLC circuit
        frequencies: Array of frequencies in Hz

    Returns:
        Frequency response data
    """
    magnitudes = []
    phases = []
    real_parts = []
    imag_parts = []

    for freq in frequencies:
        h = circuit.transfer_function(freq)
        magnitudes.append(abs(h))
        phases.append(np.degrees(np.angle(h)))
        real_parts.append(h.real)
        imag_parts.append(h.imag)

    return {
        "frequency": frequencies.tolist(),
        "magnitude": magnitudes,
        "phase": phases,
        "magnitude_db": [20 * np.log10(m) if m > 0 else -100 for m in magnitudes],
        "real": real_parts,
        "imaginary": imag_parts,
    }
