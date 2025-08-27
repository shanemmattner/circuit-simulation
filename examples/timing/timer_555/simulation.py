"""Simulation functions for 555 timer circuits."""

import numpy as np
from typing import Dict, Any, Optional
from .circuit import Timer555Circuit


def simulate_555_timer(
    circuit: Timer555Circuit,
    duration: float = 10e-3,
    timestep: Optional[float] = None,
    trigger_time: Optional[float] = None
) -> Dict[str, Any]:
    """Simulate 555 timer circuit.
    
    Args:
        circuit: 555 timer circuit
        duration: Simulation duration
        timestep: Time step
        trigger_time: Trigger time for monostable
        
    Returns:
        Simulation results
    """
    if timestep is None:
        if circuit.frequency:
            timestep = 1 / (circuit.frequency * 100)  # 100 points per cycle
        else:
            timestep = duration / 1000
    
    time = np.arange(0, duration + timestep, timestep)
    
    if circuit.mode == "astable":
        results = _simulate_astable(circuit, time)
    elif circuit.mode == "monostable":
        results = _simulate_monostable(circuit, time, trigger_time)
    elif circuit.mode == "bistable":
        results = _simulate_bistable(circuit, time)
    else:  # PWM
        results = _simulate_pwm(circuit, time)
    
    results["time"] = time.tolist()
    results["duration"] = duration
    
    return results


def _simulate_astable(circuit: Timer555Circuit, time: np.ndarray) -> Dict[str, Any]:
    """Simulate astable oscillator.
    
    Args:
        circuit: 555 timer circuit
        time: Time array
        
    Returns:
        Simulation results
    """
    output = np.zeros_like(time)
    capacitor_voltage = np.zeros_like(time)
    
    # Get thresholds
    thresholds = circuit.get_threshold_voltages()
    v_upper = thresholds["upper_threshold"]
    v_lower = thresholds["lower_threshold"]
    
    # Initial conditions
    charging = True
    v_cap = 0
    
    dt = time[1] - time[0] if len(time) > 1 else 1e-6
    
    for i in range(len(time)):
        if charging:
            # Charging through R1 + R2
            tau = (circuit.r1 + circuit.r2) * circuit.c
            v_cap += (circuit.vcc - v_cap) * (1 - np.exp(-dt/tau))
            
            if v_cap >= v_upper:
                charging = False
                output[i] = 0
            else:
                output[i] = circuit.vcc
        else:
            # Discharging through R2
            tau = circuit.r2 * circuit.c
            v_cap *= np.exp(-dt/tau)
            
            if v_cap <= v_lower:
                charging = True
                output[i] = circuit.vcc
            else:
                output[i] = 0
        
        capacitor_voltage[i] = v_cap
    
    # Calculate measured frequency
    transitions = np.where(np.abs(np.diff(output)) > circuit.vcc/2)[0]
    if len(transitions) > 2:
        periods = np.diff(transitions[::2]) * dt
        measured_frequency = 1 / np.mean(periods) if len(periods) > 0 else 0
    else:
        measured_frequency = 0
    
    return {
        "output": output.tolist(),
        "capacitor_voltage": capacitor_voltage.tolist(),
        "measured_frequency": measured_frequency
    }


def _simulate_monostable(
    circuit: Timer555Circuit,
    time: np.ndarray,
    trigger_time: Optional[float]
) -> Dict[str, Any]:
    """Simulate monostable one-shot.
    
    Args:
        circuit: 555 timer circuit
        time: Time array
        trigger_time: When to trigger
        
    Returns:
        Simulation results
    """
    output = np.zeros_like(time)
    trigger = np.zeros_like(time)
    capacitor_voltage = np.zeros_like(time)
    
    if trigger_time is None:
        trigger_time = time[len(time)//10]  # Trigger at 10% of duration
    
    # Create trigger pulse
    trigger_index = np.argmin(np.abs(time - trigger_time))
    trigger[trigger_index] = 1
    
    # Get threshold
    thresholds = circuit.get_threshold_voltages()
    v_threshold = thresholds["upper_threshold"]
    
    # Simulate
    triggered = False
    pulse_start = 0
    dt = time[1] - time[0] if len(time) > 1 else 1e-6
    
    for i in range(len(time)):
        if trigger[i] > 0 and not triggered:
            triggered = True
            pulse_start = i
        
        if triggered:
            # Calculate time since trigger
            t_elapsed = (i - pulse_start) * dt
            
            if t_elapsed < circuit.pulse_width:
                output[i] = circuit.vcc
                # Capacitor charges
                tau = circuit.r1 * circuit.c
                capacitor_voltage[i] = circuit.vcc * (1 - np.exp(-t_elapsed/tau))
            else:
                output[i] = 0
                capacitor_voltage[i] = 0
                triggered = False
    
    return {
        "output": output.tolist(),
        "trigger": trigger.tolist(),
        "capacitor_voltage": capacitor_voltage.tolist()
    }


def _simulate_bistable(circuit: Timer555Circuit, time: np.ndarray) -> Dict[str, Any]:
    """Simulate bistable flip-flop.
    
    Args:
        circuit: 555 timer circuit
        time: Time array
        
    Returns:
        Simulation results
    """
    output = np.zeros_like(time)
    
    # Toggle at fixed intervals for demo
    toggle_period = len(time) // 4
    state = False
    
    for i in range(len(time)):
        if i % toggle_period == 0:
            state = not state
        output[i] = circuit.vcc if state else 0
    
    return {
        "output": output.tolist(),
        "capacitor_voltage": [0] * len(time)
    }


def _simulate_pwm(circuit: Timer555Circuit, time: np.ndarray) -> Dict[str, Any]:
    """Simulate PWM mode.
    
    Args:
        circuit: 555 timer circuit
        time: Time array
        
    Returns:
        Simulation results
    """
    # Similar to astable but with variable duty cycle
    output = np.zeros_like(time)
    
    period = 1 / circuit.frequency if circuit.frequency else 1e-3
    
    for i, t in enumerate(time):
        phase = (t % period) / period
        output[i] = circuit.vcc if phase < circuit.duty_cycle else 0
    
    return {
        "output": output.tolist(),
        "capacitor_voltage": [0] * len(time)
    }


def calculate_timing_parameters(circuit: Timer555Circuit) -> Dict[str, Any]:
    """Calculate comprehensive timing parameters.
    
    Args:
        circuit: 555 timer circuit
        
    Returns:
        Timing parameters
    """
    params = {}
    
    if circuit.mode == "astable":
        params["frequency"] = circuit.frequency
        params["period"] = 1 / circuit.frequency if circuit.frequency else None
        params["duty_cycle"] = circuit.duty_cycle
        
        if circuit.r1 and circuit.r2 and circuit.c:
            params["high_time"] = 0.693 * (circuit.r1 + circuit.r2) * circuit.c
            params["low_time"] = 0.693 * circuit.r2 * circuit.c
            
            # Rise and fall times
            params["rise_time"] = 2.2 * circuit.r2 * circuit.c
            params["fall_time"] = 2.2 * circuit.r2 * circuit.c
    
    elif circuit.mode == "monostable":
        params["pulse_width"] = circuit.pulse_width
        if circuit.pulse_width:
            params["recovery_time"] = circuit.pulse_width * 0.1  # ~10% recovery
            params["max_trigger_rate"] = 1 / (circuit.pulse_width * 1.1)
    
    # Power consumption estimate
    if circuit.r1 and circuit.r2:
        # Average current through timing resistors
        r_total = circuit.r1 + circuit.r2
        params["average_current"] = circuit.vcc / r_total / 2  # Rough average
        params["power_dissipation"] = params["average_current"] * circuit.vcc
    
    return params