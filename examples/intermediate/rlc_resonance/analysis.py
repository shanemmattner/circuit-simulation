"""Analysis functions for RLC resonance circuit."""

from typing import Any, Dict

import numpy as np

from .circuit import RLCResonanceCircuit


def analyze_resonance(circuit: RLCResonanceCircuit) -> Dict[str, Any]:
    """Perform comprehensive resonance analysis.

    Args:
        circuit: RLC resonance circuit

    Returns:
        Dictionary with resonance analysis results
    """
    # Get half-power frequencies
    f_lower, f_upper = circuit.calculate_half_power_frequencies()

    # Calculate phase at resonance
    z_at_resonance = circuit.calculate_impedance(circuit.resonant_frequency)
    phase_at_resonance = np.degrees(np.angle(z_at_resonance))

    # Calculate maximum energy storage (at peak voltage/current)
    # For series RLC with step input, max current = V/R
    max_current = circuit.vin / circuit.r
    max_voltage_c = circuit.vin  # Maximum voltage across capacitor

    max_inductor_energy = 0.5 * circuit.l * max_current**2
    max_capacitor_energy = 0.5 * circuit.c * max_voltage_c**2

    # Calculate selectivity (same as Q for single resonance)
    selectivity = circuit.q_factor

    # Power factor at resonance (should be 1 for series, varies for parallel)
    if circuit.topology == "series":
        power_factor = 1.0  # Pure resistive at resonance
    else:
        # For parallel, depends on component values
        power_factor = circuit.r / abs(z_at_resonance)

    return {
        "resonant_frequency": circuit.resonant_frequency,
        "resonant_frequency_hz": f"{circuit.resonant_frequency:.2f} Hz",
        "angular_frequency": circuit.angular_frequency,
        "q_factor": circuit.q_factor,
        "bandwidth": circuit.bandwidth,
        "bandwidth_hz": f"{circuit.bandwidth:.2f} Hz",
        "damping_ratio": circuit.damping_ratio,
        "damping_type": circuit.damping_type,
        "characteristic_impedance": circuit.characteristic_impedance,
        "half_power_frequencies": {
            "lower": f_lower,
            "upper": f_upper,
            "lower_hz": f"{f_lower:.2f} Hz",
            "upper_hz": f"{f_upper:.2f} Hz",
        },
        "phase_at_resonance": phase_at_resonance,
        "impedance_at_resonance": abs(z_at_resonance),
        "selectivity": selectivity,
        "power_factor_at_resonance": power_factor,
        "energy_stored": {
            "max_inductor_energy": max_inductor_energy,
            "max_capacitor_energy": max_capacitor_energy,
            "total_max_energy": max_inductor_energy + max_capacitor_energy,
        },
        "rise_time": (
            1 / (circuit.damping_ratio * circuit.angular_frequency)
            if circuit.damping_ratio > 0
            else float("inf")
        ),
        "settling_time": (
            4 / (circuit.damping_ratio * circuit.angular_frequency)
            if circuit.damping_ratio > 0
            else float("inf")
        ),
    }


def design_bandpass_filter(
    center_frequency: float,
    bandwidth: float,
    impedance: float = 50,
    topology: str = "series",
) -> RLCResonanceCircuit:
    """Design an RLC bandpass filter.

    Args:
        center_frequency: Center frequency in Hz
        bandwidth: 3dB bandwidth in Hz
        impedance: Characteristic impedance in ohms
        topology: "series" or "parallel"

    Returns:
        RLCResonanceCircuit configured as bandpass filter
    """
    # Calculate Q factor
    q_factor = center_frequency / bandwidth

    # Calculate L and C for given center frequency and impedance
    # Z0 = sqrt(L/C), f0 = 1/(2π√(LC))

    # Choose L based on impedance and frequency
    l = impedance / (2 * np.pi * center_frequency)

    # Calculate C from resonance condition
    c = 1 / ((2 * np.pi * center_frequency) ** 2 * l)

    # Calculate R from Q factor
    if topology == "series":
        # For series: Q = (1/R) * sqrt(L/C)
        r = np.sqrt(l / c) / q_factor
    else:
        # For parallel: Q = R / sqrt(L/C)
        r = q_factor * np.sqrt(l / c)

    # Create circuit
    circuit = RLCResonanceCircuit(r=r, l=l, c=c, topology=topology)

    # Verify design
    actual_f0 = circuit.resonant_frequency
    actual_bw = circuit.bandwidth
    actual_q = circuit.q_factor

    print("Designed Bandpass Filter:")
    print(
        f"  Target: f0={center_frequency:.1f}Hz, BW={bandwidth:.1f}Hz, Q={q_factor:.2f}"
    )
    print(f"  Actual: f0={actual_f0:.1f}Hz, BW={actual_bw:.1f}Hz, Q={actual_q:.2f}")
    print(f"  Components: R={r:.2f}Ω, L={l*1e3:.3f}mH, C={c*1e9:.3f}nF")

    return circuit


def design_notch_filter(
    notch_frequency: float, q_factor: float = 10, impedance: float = 50
) -> RLCResonanceCircuit:
    """Design an RLC notch (band-reject) filter.

    For a notch filter, use parallel RLC in series with signal path.
    At resonance, parallel RLC has maximum impedance, blocking the signal.

    Args:
        notch_frequency: Frequency to reject in Hz
        q_factor: Quality factor (higher = narrower notch)
        impedance: Characteristic impedance in ohms

    Returns:
        RLCResonanceCircuit configured as notch filter
    """
    # Calculate L and C for given notch frequency
    l = impedance / (2 * np.pi * notch_frequency)
    c = 1 / ((2 * np.pi * notch_frequency) ** 2 * l)

    # For parallel RLC notch: Q = R / sqrt(L/C)
    r = q_factor * np.sqrt(l / c)

    # Create parallel circuit (acts as notch in series path)
    circuit = RLCResonanceCircuit(r=r, l=l, c=c, topology="parallel")

    # Calculate notch depth (impedance ratio)
    z_at_notch = abs(circuit.calculate_impedance(notch_frequency))
    z_at_low = abs(circuit.calculate_impedance(10))
    notch_depth_db = 20 * np.log10(z_at_notch / z_at_low)

    print("Designed Notch Filter:")
    print(f"  Notch frequency: {notch_frequency:.1f}Hz")
    print(f"  Q factor: {circuit.q_factor:.2f}")
    print(f"  Notch depth: {notch_depth_db:.1f}dB")
    print(f"  Components: R={r:.2f}Ω, L={l*1e3:.3f}mH, C={c*1e9:.3f}nF")

    return circuit


def analyze_stability(circuit: RLCResonanceCircuit) -> Dict[str, Any]:
    """Analyze circuit stability.

    Args:
        circuit: RLC circuit

    Returns:
        Stability analysis results
    """
    # For RLC circuits, stability is determined by damping
    is_stable = circuit.damping_ratio > 0

    # Calculate poles of the system
    omega_n = circuit.angular_frequency
    zeta = circuit.damping_ratio

    if circuit.damping_type == "underdamped":
        # Complex conjugate poles
        real_part = -zeta * omega_n
        imag_part = omega_n * np.sqrt(1 - zeta**2)
        poles = [complex(real_part, imag_part), complex(real_part, -imag_part)]
    elif circuit.damping_type == "critically_damped":
        # Repeated real poles
        poles = [complex(-omega_n, 0), complex(-omega_n, 0)]
    else:  # overdamped
        # Two distinct real poles
        alpha = zeta * omega_n
        beta = omega_n * np.sqrt(zeta**2 - 1)
        poles = [complex(-(alpha - beta), 0), complex(-(alpha + beta), 0)]

    # Phase margin (for feedback systems)
    # At gain crossover frequency (|H| = 1)
    gain_crossover_freq = circuit.resonant_frequency
    h_at_gc = circuit.transfer_function(gain_crossover_freq)
    phase_at_gc = np.degrees(np.angle(h_at_gc))
    phase_margin = 180 + phase_at_gc

    # Gain margin (at phase crossover, phase = -180°)
    # For second-order system, this occurs at infinity
    gain_margin_db = float("inf") if is_stable else 0

    return {
        "is_stable": is_stable,
        "poles": poles,
        "damping_ratio": circuit.damping_ratio,
        "damping_type": circuit.damping_type,
        "natural_frequency": omega_n,
        "phase_margin_degrees": phase_margin,
        "gain_margin_db": gain_margin_db,
        "time_to_half_amplitude": (
            np.log(2) / (zeta * omega_n) if zeta > 0 else float("inf")
        ),
        "oscillation_frequency": (
            circuit.damped_frequency if circuit.damping_type == "underdamped" else 0
        ),
    }


def calculate_sensitivity(
    circuit: RLCResonanceCircuit, parameter: str, variation: float = 0.01
) -> Dict[str, float]:
    """Calculate sensitivity to parameter variations.

    Args:
        circuit: RLC circuit
        parameter: Parameter to vary ("r", "l", or "c")
        variation: Fractional variation (e.g., 0.01 for 1%)

    Returns:
        Sensitivity analysis results
    """
    # Store original values
    original_f0 = circuit.resonant_frequency
    original_q = circuit.q_factor
    original_bw = circuit.bandwidth

    # Get original parameter value
    original_value = getattr(circuit, parameter)

    # Apply variation
    new_value = original_value * (1 + variation)
    setattr(circuit, parameter, new_value)

    # Recalculate parameters
    circuit._calculate_parameters()

    # Get new values
    new_f0 = circuit.resonant_frequency
    new_q = circuit.q_factor
    new_bw = circuit.bandwidth

    # Calculate sensitivities (fractional change per fractional parameter change)
    s_f0 = ((new_f0 - original_f0) / original_f0) / variation
    s_q = ((new_q - original_q) / original_q) / variation if original_q > 0 else 0
    s_bw = ((new_bw - original_bw) / original_bw) / variation if original_bw > 0 else 0

    # Restore original value
    setattr(circuit, parameter, original_value)
    circuit._calculate_parameters()

    return {
        f"sensitivity_f0_to_{parameter}": s_f0,
        f"sensitivity_q_to_{parameter}": s_q,
        f"sensitivity_bw_to_{parameter}": s_bw,
        "parameter_varied": parameter,
        "variation_applied": variation,
    }
