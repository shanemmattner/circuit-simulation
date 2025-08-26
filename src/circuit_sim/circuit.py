"""
Circuit definition module.

This module provides the main Circuit class for defining electronic circuits.
"""

from typing import Any, Dict, List, Union


class Circuit:
    """
    Represents an electronic circuit.

    A circuit consists of components (resistors, capacitors, etc.) connected
    at nodes. Node 0 is always ground.

    Example:
        >>> circuit = Circuit("RC Filter")
        >>> circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        >>> circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        >>> circuit.add_capacitor("C1", node1=2, node2=0, capacitance="1u")
        >>> results = circuit.simulate(analysis="transient", stop_time="10ms")
    """

    def __init__(self, name: str) -> None:
        """
        Initialize a new circuit.

        Args:
            name: Descriptive name for the circuit
        """
        self.name = name
        self.components: List[Dict[str, Any]] = []
        self.nodes: set = {0}  # Always include ground
        self._simulation_results = None

    def add_voltage_source(
        self, name: str, positive: Union[int, str], negative: Union[int, str], dc_value: str
    ) -> "Circuit":
        """
        Add a DC voltage source to the circuit.

        Args:
            name: Component identifier (e.g., "V1")
            positive: Positive terminal node
            negative: Negative terminal node (often 0 or "gnd")
            dc_value: DC voltage value (e.g., "5V", "3.3V")

        Returns:
            self for method chaining
        """
        # Convert "gnd" to 0
        if positive == "gnd":
            positive = 0
        if negative == "gnd":
            negative = 0

        self.nodes.add(positive)
        self.nodes.add(negative)

        self.components.append(
            {
                "type": "voltage_source",
                "name": name,
                "positive": positive,
                "negative": negative,
                "dc_value": dc_value,
            }
        )

        return self

    def add_resistor(
        self, name: str, node1: Union[int, str], node2: Union[int, str], resistance: str
    ) -> "Circuit":
        """
        Add a resistor to the circuit.

        Args:
            name: Component identifier (e.g., "R1")
            node1: First connection node
            node2: Second connection node
            resistance: Resistance value (e.g., "1k", "10M")

        Returns:
            self for method chaining
        """
        # Convert "gnd" to 0
        if node1 == "gnd":
            node1 = 0
        if node2 == "gnd":
            node2 = 0

        self.nodes.add(node1)
        self.nodes.add(node2)

        self.components.append(
            {
                "type": "resistor",
                "name": name,
                "node1": node1,
                "node2": node2,
                "resistance": resistance,
            }
        )

        return self

    def add_capacitor(
        self, name: str, node1: Union[int, str], node2: Union[int, str], capacitance: str
    ) -> "Circuit":
        """
        Add a capacitor to the circuit.

        Args:
            name: Component identifier (e.g., "C1")
            node1: First connection node
            node2: Second connection node
            capacitance: Capacitance value (e.g., "1u", "100n")

        Returns:
            self for method chaining
        """
        # Convert "gnd" to 0
        if node1 == "gnd":
            node1 = 0
        if node2 == "gnd":
            node2 = 0

        self.nodes.add(node1)
        self.nodes.add(node2)

        self.components.append(
            {
                "type": "capacitor",
                "name": name,
                "node1": node1,
                "node2": node2,
                "capacitance": capacitance,
            }
        )

        return self

    def add_inductor(
        self, name: str, node1: Union[int, str], node2: Union[int, str], inductance: str
    ) -> "Circuit":
        """
        Add an inductor to the circuit.

        Args:
            name: Component identifier (e.g., "L1")
            node1: First connection node
            node2: Second connection node
            inductance: Inductance value (e.g., "1m", "100u")

        Returns:
            self for method chaining
        """
        # Convert "gnd" to 0
        if node1 == "gnd":
            node1 = 0
        if node2 == "gnd":
            node2 = 0

        self.nodes.add(node1)
        self.nodes.add(node2)

        self.components.append(
            {
                "type": "inductor",
                "name": name,
                "node1": node1,
                "node2": node2,
                "inductance": inductance,
            }
        )

        return self

    def add_current_source(
        self, name: str, positive: Union[int, str], negative: Union[int, str], dc_value: str
    ) -> "Circuit":
        """
        Add a DC current source to the circuit.

        Args:
            name: Component identifier (e.g., "I1")
            positive: Positive terminal node (current flows out)
            negative: Negative terminal node (current flows in)
            dc_value: DC current value (e.g., "10mA", "1A")

        Returns:
            self for method chaining
        """
        # Convert "gnd" to 0
        if positive == "gnd":
            positive = 0
        if negative == "gnd":
            negative = 0

        self.nodes.add(positive)
        self.nodes.add(negative)

        self.components.append(
            {
                "type": "current_source",
                "name": name,
                "positive": positive,
                "negative": negative,
                "dc_value": dc_value,
            }
        )

        return self

    def simulate(self, analysis: str = "dc", **kwargs) -> "SimulationResults":
        """
        Run circuit simulation.

        Args:
            analysis: Type of analysis ("dc", "transient", "ac")
            **kwargs: Analysis-specific parameters
                - For transient: stop_time, step_time
                - For ac: start_freq, stop_freq, points

        Returns:
            SimulationResults object containing simulation data

        Raises:
            NotImplementedError: Simulation not yet implemented
        """
        # This will be implemented when we integrate PySpice
        raise NotImplementedError("Simulation will be implemented with PySpice integration")

    def __repr__(self) -> str:
        """String representation of the circuit."""
        return f"Circuit('{self.name}', {len(self.components)} components, {len(self.nodes)} nodes)"


# Placeholder for SimulationResults class
class SimulationResults:
    """Placeholder for simulation results - will be implemented later."""

    pass
