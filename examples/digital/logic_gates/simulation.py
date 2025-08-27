"""Simulation functions for logic gates."""

import numpy as np
from typing import List, Dict, Any, Optional
from .circuit import LogicGateCircuit


def simulate_logic_gate(
    circuit: LogicGateCircuit,
    input_signals: List[List[int]],
    duration: float = 1e-3,
    timestep: Optional[float] = None
) -> Dict[str, Any]:
    """Simulate logic gate circuit.
    
    Args:
        circuit: Logic gate circuit
        input_signals: List of input signal sequences
        duration: Simulation duration
        timestep: Time step
        
    Returns:
        Simulation results
    """
    if timestep is None:
        timestep = circuit.propagation_delay / 10 if circuit.propagation_delay > 0 else 1e-9
    
    # Create time array
    num_samples = max(len(sig) for sig in input_signals)
    time_per_sample = duration / num_samples
    time = np.arange(0, duration, timestep)
    
    # Expand input signals to match time array
    expanded_inputs = []
    for signal in input_signals:
        expanded = []
        for i, t in enumerate(time):
            sample_idx = int(t / time_per_sample)
            if sample_idx < len(signal):
                expanded.append(signal[sample_idx])
            else:
                expanded.append(signal[-1])
        expanded_inputs.append(expanded)
    
    # Simulate gate output with propagation delay
    output = []
    delay_samples = int(circuit.propagation_delay / timestep)
    
    for i in range(len(time)):
        # Get inputs at current time
        current_inputs = [inp[i] for inp in expanded_inputs]
        
        # Evaluate gate
        gate_output = circuit.evaluate(current_inputs)
        
        # Apply propagation delay
        if i < delay_samples:
            output.append(0)
        else:
            output.append(gate_output)
    
    return {
        "time": time.tolist(),
        "inputs": expanded_inputs,
        "output": output,
        "propagation_delay": circuit.propagation_delay
    }


def create_truth_table(circuit: LogicGateCircuit) -> Dict[str, List]:
    """Generate truth table for logic gate.
    
    Args:
        circuit: Logic gate circuit
        
    Returns:
        Truth table dictionary
    """
    num_combinations = 2 ** circuit.num_inputs
    inputs = []
    outputs = []
    
    for i in range(num_combinations):
        # Generate binary input combination
        input_combo = []
        for j in range(circuit.num_inputs):
            bit = (i >> (circuit.num_inputs - 1 - j)) & 1
            input_combo.append(bit)
        
        inputs.append(input_combo)
        outputs.append(circuit.evaluate(input_combo))
    
    return {
        "inputs": inputs,
        "outputs": outputs,
        "gate_type": circuit.gate_type
    }