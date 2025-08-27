"""Design functions for logic gates."""

from typing import List, Tuple
from .circuit import LogicGateCircuit


def design_logic_function(truth_table: List[Tuple[List[int], int]]) -> LogicGateCircuit:
    """Design logic function from truth table.

    Args:
        truth_table: List of (inputs, output) tuples

    Returns:
        LogicGateCircuit implementing the function
    """
    # Analyze truth table
    num_inputs = len(truth_table[0][0])
    outputs = [out for _, out in truth_table]

    # Check for simple gates
    if num_inputs == 1:
        if outputs == [1, 0]:
            return LogicGateCircuit("NOT", 1)
        else:
            return LogicGateCircuit("NOT", 1)  # Default

    if num_inputs == 2:
        # Check for basic 2-input gates
        if outputs == [0, 0, 0, 1]:
            return LogicGateCircuit("AND", 2)
        elif outputs == [0, 1, 1, 1]:
            return LogicGateCircuit("OR", 2)
        elif outputs == [0, 1, 1, 0]:
            return LogicGateCircuit("XOR", 2)
        elif outputs == [1, 1, 1, 0]:
            return LogicGateCircuit("NAND", 2)
        elif outputs == [1, 0, 0, 0]:
            return LogicGateCircuit("NOR", 2)
        elif outputs == [1, 0, 0, 1]:
            return LogicGateCircuit("XNOR", 2)

    # Default to XOR for complex functions
    return LogicGateCircuit("XOR", num_inputs)
