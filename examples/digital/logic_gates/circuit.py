"""Logic gate circuit implementation."""

from typing import List


class LogicGateCircuit:
    """Digital logic gate circuit."""

    def __init__(
        self,
        gate_type: str,
        num_inputs: int = 2,
        vcc: float = 5.0,
        propagation_delay: float = 1e-9,
    ):
        """Initialize logic gate.

        Args:
            gate_type: Type of gate (AND, OR, NOT, XOR, NAND, NOR, XNOR)
            num_inputs: Number of inputs
            vcc: Supply voltage
            propagation_delay: Gate delay in seconds
        """
        self.gate_type = gate_type.upper()
        self.num_inputs = num_inputs
        self.vcc = vcc
        self.propagation_delay = propagation_delay

        # Threshold for logic levels
        self.v_threshold = vcc / 2
        self.v_high = vcc * 0.7
        self.v_low = vcc * 0.3

    def evaluate(self, inputs: List[int]) -> int:
        """Evaluate logic gate output.

        Args:
            inputs: List of binary inputs

        Returns:
            Binary output
        """
        if self.gate_type == "AND":
            return int(all(inputs))

        elif self.gate_type == "OR":
            return int(any(inputs))

        elif self.gate_type == "NOT":
            return int(not inputs[0])

        elif self.gate_type == "NAND":
            return int(not all(inputs))

        elif self.gate_type == "NOR":
            return int(not any(inputs))

        elif self.gate_type == "XOR":
            return int(sum(inputs) % 2)

        elif self.gate_type == "XNOR":
            return int(not (sum(inputs) % 2))

        else:
            return 0

    def voltage_to_logic(self, voltage: float) -> int:
        """Convert voltage to logic level.

        Args:
            voltage: Input voltage

        Returns:
            Logic level (0 or 1)
        """
        return int(voltage > self.v_threshold)

    def logic_to_voltage(self, logic: int) -> float:
        """Convert logic level to voltage.

        Args:
            logic: Logic level

        Returns:
            Output voltage
        """
        return self.vcc if logic else 0.0
