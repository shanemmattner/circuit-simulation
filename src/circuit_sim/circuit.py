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
        self,
        name: str,
        positive: Union[int, str],
        negative: Union[int, str],
        dc_value: str,
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
        self,
        name: str,
        node1: Union[int, str],
        node2: Union[int, str],
        capacitance: str,
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
        self,
        name: str,
        positive: Union[int, str],
        negative: Union[int, str],
        dc_value: str,
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

    def add_bjt_transistor(
        self,
        name: str,
        collector: Union[int, str],
        base: Union[int, str],
        emitter: Union[int, str],
        model: str = "2N3904",
    ) -> "Circuit":
        """
        Add a BJT transistor to the circuit.

        Args:
            name: Component identifier (e.g., "Q1")
            collector: Collector terminal node
            base: Base terminal node
            emitter: Emitter terminal node
            model: SPICE model name (e.g., "2N3904")

        Returns:
            self for method chaining
        """
        # Convert "gnd" to 0
        for node in [collector, base, emitter]:
            if node == "gnd":
                node = 0
            self.nodes.add(node)

        self.components.append(
            {
                "type": "bjt_transistor",
                "name": name,
                "collector": collector,
                "base": base,
                "emitter": emitter,
                "model": model,
            }
        )

        return self

    def add_diode(
        self,
        name: str,
        anode: Union[int, str],
        cathode: Union[int, str],
        model: str = "1N4148",
    ) -> "Circuit":
        """
        Add a diode to the circuit.

        Args:
            name: Component identifier (e.g., "D1")
            anode: Anode terminal node
            cathode: Cathode terminal node
            model: SPICE model name (e.g., "1N4148")

        Returns:
            self for method chaining
        """
        # Convert "gnd" to 0
        if anode == "gnd":
            anode = 0
        if cathode == "gnd":
            cathode = 0

        self.nodes.add(anode)
        self.nodes.add(cathode)

        self.components.append(
            {
                "type": "diode",
                "name": name,
                "anode": anode,
                "cathode": cathode,
                "model": model,
            }
        )

        return self

    def add_opamp(
        self,
        name: str,
        vplus: Union[int, str],
        vminus: Union[int, str],
        vout: Union[int, str],
        vcc: Union[int, str],
        vee: Union[int, str],
        model: str = "LM358",
    ) -> "Circuit":
        """
        Add an operational amplifier to the circuit.

        Args:
            name: Component identifier (e.g., "U1")
            vplus: Non-inverting input node
            vminus: Inverting input node
            vout: Output node
            vcc: Positive supply node
            vee: Negative supply node (often ground)
            model: SPICE model name (e.g., "LM358")

        Returns:
            self for method chaining
        """
        # Convert "gnd" to 0 and add all nodes
        for node in [vplus, vminus, vout, vcc, vee]:
            if node == "gnd":
                node = 0
            self.nodes.add(node)

        self.components.append(
            {
                "type": "opamp",
                "name": name,
                "vplus": vplus,
                "vminus": vminus,
                "vout": vout,
                "vcc": vcc,
                "vee": vee,
                "model": model,
            }
        )

        return self

    def add_mosfet(
        self,
        name: str,
        drain: Union[int, str],
        gate: Union[int, str],
        source: Union[int, str],
        bulk: Union[int, str],
        model: str = "IRF540",
    ) -> "Circuit":
        """
        Add a MOSFET transistor to the circuit.

        Args:
            name: Component identifier (e.g., "Q1")
            drain: Drain terminal node
            gate: Gate terminal node
            source: Source terminal node
            bulk: Bulk/substrate terminal node
            model: SPICE model name (e.g., "IRF540")

        Returns:
            self for method chaining
        """
        # Convert "gnd" to 0 and add all nodes
        for node in [drain, gate, source, bulk]:
            if node == "gnd":
                node = 0
            self.nodes.add(node)

        self.components.append(
            {
                "type": "mosfet",
                "name": name,
                "drain": drain,
                "gate": gate,
                "source": source,
                "bulk": bulk,
                "model": model,
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
            ImportError: If PySpice/ngspice not available
            RuntimeError: If simulation fails
        """
        from .simulator import SimulationEngine

        engine = SimulationEngine()

        if analysis == "dc":
            return engine.simulate_dc(self)
        elif analysis == "transient":
            stop_time = kwargs.get("stop_time")
            if stop_time is None:
                raise ValueError("transient analysis requires stop_time parameter")

            step_time = kwargs.get("step_time")
            start_time = kwargs.get("start_time", 0)
            max_time_step = kwargs.get("max_time_step")

            return engine.simulate_transient(
                self, stop_time, step_time, start_time, max_time_step
            )
        elif analysis == "ac":
            start_freq = kwargs.get("start_freq") or kwargs.get("start_frequency")
            stop_freq = kwargs.get("stop_freq") or kwargs.get("stop_frequency")

            if start_freq is None or stop_freq is None:
                raise ValueError(
                    "AC analysis requires start_freq and stop_freq parameters"
                )

            points_per_decade = kwargs.get("points_per_decade", 10)
            variation = kwargs.get("variation", "dec")

            return engine.simulate_ac(
                self, start_freq, stop_freq, points_per_decade, variation
            )
        else:
            raise ValueError(
                f"Unknown analysis type: {analysis}. Use 'dc', 'transient', or 'ac'"
            )

    def __repr__(self) -> str:
        """String representation of the circuit."""
        return f"Circuit('{self.name}', {len(self.components)} components, {len(self.nodes)} nodes)"


# Placeholder for SimulationResults class
class SimulationResults:
    """Placeholder for simulation results - will be implemented later."""

    pass
