"""Analysis functions for op-amp circuits."""

import numpy as np
from typing import Dict, Any, List, Optional
from .circuit import OpAmpCircuit


def analyze_amplifier(
    circuit: OpAmpCircuit,
    include_noise: bool = False,
    include_stability: bool = False
) -> Dict[str, Any]:
    """Perform comprehensive amplifier analysis.
    
    Args:
        circuit: Op-amp circuit
        include_noise: Include noise analysis
        include_stability: Include stability analysis
        
    Returns:
        Analysis results
    """
    analysis = {}
    
    # Basic parameters
    analysis["configuration"] = circuit.config
    analysis["ideal_gain"] = circuit.calculate_ideal_gain()
    analysis["input_impedance"] = circuit.calculate_input_impedance()
    analysis["output_impedance"] = circuit.calculate_output_impedance()
    
    # Bandwidth and frequency response
    bandwidth = circuit.calculate_bandwidth()
    if bandwidth:
        analysis["bandwidth"] = bandwidth
        analysis["gain_bandwidth_product"] = circuit.gbw if circuit.gbw else None
    
    # Slew rate
    if circuit.slew_rate:
        analysis["slew_rate"] = circuit.slew_rate
        analysis["slew_rate_v_us"] = circuit.slew_rate / 1e6
        
        # Full power bandwidth (limited by slew rate)
        # FPBW = SR / (2π * Vpeak)
        vpeak = min(abs(circuit.vcc), abs(circuit.vee)) - 2
        analysis["full_power_bandwidth"] = circuit.slew_rate / (2 * np.pi * vpeak)
    
    # Power consumption
    analysis["supply_current"] = _estimate_supply_current(circuit)
    analysis["power_dissipation"] = analysis["supply_current"] * (circuit.vcc - circuit.vee)
    
    # Noise analysis
    if include_noise:
        noise = _analyze_noise(circuit)
        analysis.update(noise)
    
    # Stability analysis
    if include_stability:
        stability = _analyze_stability(circuit)
        analysis.update(stability)
    
    return analysis


def calculate_gain_bandwidth(circuit: OpAmpCircuit) -> Dict[str, Any]:
    """Calculate gain-bandwidth product and related parameters.
    
    Args:
        circuit: Op-amp circuit
        
    Returns:
        Gain-bandwidth analysis
    """
    ideal_gain = circuit.calculate_ideal_gain() or 1
    dc_gain = abs(ideal_gain)
    
    # Get or estimate GBW
    if circuit.gbw:
        gbw = circuit.gbw
    else:
        # Estimate from model
        if "LM358" in circuit.model.upper():
            gbw = 1e6
        elif "TL072" in circuit.model.upper():
            gbw = 3e6
        elif "LF351" in circuit.model.upper():
            gbw = 4e6
        else:
            gbw = 1e6  # Default 1MHz
    
    # Calculate bandwidth
    bandwidth = gbw / dc_gain
    
    # Unity gain frequency
    unity_gain_freq = gbw
    
    # Phase margin estimate (simplified)
    # For single-pole compensation: PM ≈ 90° - arctan(fc/f_unity)
    phase_margin = 90 - np.degrees(np.arctan(bandwidth / unity_gain_freq))
    
    return {
        "dc_gain": dc_gain,
        "dc_gain_db": 20 * np.log10(dc_gain),
        "bandwidth": bandwidth,
        "gain_bandwidth_product": gbw,
        "unity_gain_frequency": unity_gain_freq,
        "phase_margin_estimate": phase_margin
    }


def _estimate_supply_current(circuit: OpAmpCircuit) -> float:
    """Estimate supply current.
    
    Args:
        circuit: Op-amp circuit
        
    Returns:
        Estimated supply current in amperes
    """
    # Typical quiescent currents
    if "LM358" in circuit.model.upper():
        return 0.5e-3  # 0.5mA
    elif "TL072" in circuit.model.upper():
        return 1.4e-3  # 1.4mA per amp
    elif "LF351" in circuit.model.upper():
        return 1.8e-3  # 1.8mA
    else:
        return 1e-3  # Default 1mA


def _analyze_noise(circuit: OpAmpCircuit) -> Dict[str, Any]:
    """Analyze noise performance.
    
    Args:
        circuit: Op-amp circuit
        
    Returns:
        Noise analysis results
    """
    # Typical noise specs (simplified)
    if "LF351" in circuit.model.upper():
        # Low noise JFET input
        v_noise = 18e-9  # 18nV/√Hz
        i_noise = 0.01e-12  # 0.01pA/√Hz
    elif "TL072" in circuit.model.upper():
        # JFET input
        v_noise = 18e-9
        i_noise = 0.01e-12
    else:
        # Bipolar input (LM358, etc.)
        v_noise = 40e-9  # 40nV/√Hz
        i_noise = 0.5e-12  # 0.5pA/√Hz
    
    # Calculate total input-referred noise
    # Resistor thermal noise
    r_source = circuit.r_in if circuit.config == "inverting" else 0
    k_b = 1.38e-23  # Boltzmann constant
    temp = 300  # Room temperature
    r_noise = np.sqrt(4 * k_b * temp * r_source) if r_source > 0 else 0
    
    # Total input noise
    total_input_noise = np.sqrt(v_noise**2 + (i_noise * r_source)**2 + r_noise**2)
    
    # Output noise
    gain = abs(circuit.calculate_ideal_gain() or 1)
    total_output_noise = total_input_noise * gain
    
    # Noise bandwidth (simplified)
    noise_bandwidth = (circuit.calculate_bandwidth() or 1e6) * np.pi / 2
    
    return {
        "input_noise_voltage": v_noise,
        "input_noise_voltage_nv_sqrt_hz": v_noise * 1e9,
        "input_noise_current": i_noise,
        "input_noise_current_pa_sqrt_hz": i_noise * 1e12,
        "resistor_noise": r_noise,
        "total_input_noise": total_input_noise,
        "total_output_noise": total_output_noise,
        "noise_bandwidth": noise_bandwidth
    }


def _analyze_stability(circuit: OpAmpCircuit) -> Dict[str, Any]:
    """Analyze circuit stability.
    
    Args:
        circuit: Op-amp circuit
        
    Returns:
        Stability analysis results
    """
    # Simplified stability analysis
    ideal_gain = abs(circuit.calculate_ideal_gain() or 1)
    
    # Estimate loop gain
    if circuit.gbw:
        open_loop_gain = circuit.gbw * 10  # Estimate DC open-loop gain
        loop_gain = open_loop_gain / (1 + open_loop_gain / ideal_gain)
    else:
        loop_gain = 1e5 / (1 + 1e5 / ideal_gain)
    
    # Phase margin estimation
    # For compensated op-amp with single dominant pole
    bandwidth = circuit.calculate_bandwidth() or 1e6
    unity_gain_freq = circuit.gbw or 1e6
    
    # Phase shift at unity gain crossover
    if bandwidth < unity_gain_freq / 10:
        # Dominant pole well below unity gain
        phase_margin = 90 - np.degrees(np.arctan(bandwidth / unity_gain_freq))
    else:
        # Multiple poles affecting phase
        phase_margin = 45  # Conservative estimate
    
    # Add compensation effect
    if circuit.c_compensation:
        # Miller compensation improves phase margin
        phase_margin += 20
    
    # Gain margin (simplified)
    gain_margin = 20 * np.log10(loop_gain) if loop_gain > 1 else float('inf')
    
    # Stability determination
    is_stable = phase_margin > 45 and gain_margin > 6
    
    return {
        "loop_gain": loop_gain,
        "loop_gain_db": 20 * np.log10(loop_gain) if loop_gain > 0 else -100,
        "phase_margin": phase_margin,
        "gain_margin": gain_margin,
        "is_stable": is_stable,
        "stability_criteria": "Phase margin > 45° and Gain margin > 6dB"
    }


def compare_amplifiers(circuits: List[OpAmpCircuit]) -> Dict[str, Any]:
    """Compare multiple amplifier configurations.
    
    Args:
        circuits: List of op-amp circuits
        
    Returns:
        Comparison results
    """
    comparison = {
        "gain_comparison": [],
        "bandwidth_comparison": [],
        "input_impedance_comparison": [],
        "configurations": []
    }
    
    for circuit in circuits:
        gain = circuit.calculate_ideal_gain()
        bandwidth = circuit.calculate_bandwidth()
        z_in = circuit.calculate_input_impedance()
        
        comparison["gain_comparison"].append(gain if gain is not None else 0)
        comparison["bandwidth_comparison"].append(bandwidth if bandwidth else 0)
        comparison["input_impedance_comparison"].append(z_in)
        comparison["configurations"].append(circuit.config)
    
    # Find best/worst
    gains = [g for g in comparison["gain_comparison"] if g is not None]
    if gains:
        comparison["highest_gain"] = max(abs(g) for g in gains)
        comparison["lowest_gain"] = min(abs(g) for g in gains)
    
    bws = [b for b in comparison["bandwidth_comparison"] if b > 0]
    if bws:
        comparison["highest_bandwidth"] = max(bws)
        comparison["lowest_bandwidth"] = min(bws)
    
    return comparison