"""Simulation functions for transistor amplifiers."""

import numpy as np
from typing import Dict, Any, Optional
from .circuit import TransistorAmplifierCircuit


def simulate_transistor_amp(
    circuit: TransistorAmplifierCircuit,
    analysis_type: str = "ac",
    **kwargs
) -> Dict[str, Any]:
    """Simulate transistor amplifier.
    
    Args:
        circuit: Transistor amplifier circuit
        analysis_type: Type of analysis
        **kwargs: Analysis parameters
        
    Returns:
        Simulation results
    """
    if analysis_type == "ac":
        return _simulate_ac(circuit, **kwargs)
    elif analysis_type == "transient":
        return _simulate_transient(circuit, **kwargs)
    else:
        return {}


def _simulate_ac(
    circuit: TransistorAmplifierCircuit,
    start_freq: float = 10,
    stop_freq: float = 1e6,
    points: int = 100
) -> Dict[str, Any]:
    """AC frequency response simulation.
    
    Args:
        circuit: Transistor amplifier
        start_freq: Start frequency
        stop_freq: Stop frequency
        points: Number of points
        
    Returns:
        AC analysis results
    """
    frequencies = np.logspace(np.log10(start_freq), np.log10(stop_freq), points)
    
    # Get midband gain
    av = circuit.calculate_voltage_gain()
    
    # Simple single-pole model
    # Assume 3dB frequency based on bypass capacitor
    if circuit.bypass_capacitor and circuit.re:
        f_low = 1 / (2 * np.pi * circuit.re * circuit.bypass_capacitor)
    else:
        f_low = 10  # Default 10Hz
    
    f_high = 1e6  # Assume 1MHz upper limit
    
    gains = []
    phases = []
    
    for f in frequencies:
        # High-pass and low-pass response
        h_low = 1j * f / f_low / (1 + 1j * f / f_low)
        h_high = 1 / (1 + 1j * f / f_high)
        h_total = av * h_low * h_high
        
        gains.append(abs(h_total))
        phases.append(np.degrees(np.angle(h_total)))
    
    return {
        "frequency": frequencies.tolist(),
        "gain": gains,
        "phase": phases,
        "midband_gain": av
    }


def _simulate_transient(
    circuit: TransistorAmplifierCircuit,
    duration: float = 10e-3,
    timestep: Optional[float] = None,
    input_amplitude: float = 0.1,
    frequency: float = 1000
) -> Dict[str, Any]:
    """Transient response simulation.
    
    Args:
        circuit: Transistor amplifier
        duration: Simulation duration
        timestep: Time step
        input_amplitude: Input signal amplitude
        frequency: Input frequency
        
    Returns:
        Transient results
    """
    if timestep is None:
        timestep = duration / 1000
    
    time = np.arange(0, duration + timestep, timestep)
    
    # Input signal
    v_in = input_amplitude * np.sin(2 * np.pi * frequency * time)
    
    # Get gain
    av = circuit.calculate_voltage_gain()
    
    # Simple amplification (ignoring nonlinearities)
    bias = calculate_bias_point(circuit)
    v_out = bias["vc"] + av * v_in
    
    # Clip at rails
    v_out = np.clip(v_out, 0.1, circuit.vcc - 0.1)
    
    return {
        "time": time.tolist(),
        "v_in": v_in.tolist(),
        "v_out": v_out.tolist(),
        "dc_bias": bias["vc"]
    }


def calculate_bias_point(circuit: TransistorAmplifierCircuit) -> Dict[str, float]:
    """Calculate DC bias point.
    
    Args:
        circuit: Transistor amplifier
        
    Returns:
        Bias voltages and currents
    """
    # Voltage divider bias
    if circuit.r1 and circuit.r2:
        vb = circuit.vcc * circuit.r2 / (circuit.r1 + circuit.r2)
    else:
        vb = circuit.vcc / 2
    
    # Emitter voltage
    ve = vb - circuit.vbe if circuit.re else 0
    
    # Emitter current
    ie = ve / circuit.re if circuit.re else 1e-3
    
    # Collector current (approximately equal to emitter current)
    ic = ie * circuit.beta / (circuit.beta + 1)
    
    # Base current
    ib = ic / circuit.beta
    
    # Collector voltage (ensure it's positive)
    if circuit.rc:
        vc = circuit.vcc - ic * circuit.rc
        vc = max(vc, 0.1)  # Ensure not negative
    else:
        vc = circuit.vcc / 2
    
    return {
        "vb": vb,
        "ve": ve,
        "vc": vc,
        "ib": ib,
        "ic": ic,
        "ie": ie
    }