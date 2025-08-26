"""
PySpice circuit builder.

Converts our simplified Circuit representation to PySpice format.
"""

from typing import Any, Dict

from ..circuit import Circuit
from ..parser import parse_value


class PySpiceBuilder:
    """Builds PySpice circuits from our Circuit representation."""

    def __init__(self):
        """Initialize the builder."""
        self._pyspice_available = self._check_pyspice()

    def _check_pyspice(self) -> bool:
        """Check if PySpice is available."""
        try:
            import importlib.util

            # Check if PySpice can be imported
            spec = importlib.util.find_spec("PySpice")
            return spec is not None
        except (ImportError, ValueError):
            return False

    def build_circuit(self, circuit: Circuit) -> Any:
        """
        Convert our Circuit to a PySpice Circuit.

        Args:
            circuit: Our Circuit representation

        Returns:
            PySpice Circuit object

        Raises:
            ImportError: If PySpice is not installed
            ValueError: If circuit has invalid components
        """
        if not self._pyspice_available:
            raise ImportError("PySpice is not installed. Install it with: pip install PySpice")

        from PySpice.Spice.Netlist import Circuit as PySpiceCircuit

        # Create PySpice circuit
        pyspice_circuit = PySpiceCircuit(circuit.name)

        # Track component counts for unique naming
        component_counts: Dict[str, int] = {}

        # Process each component
        for comp in circuit.components:
            comp_type = comp["type"]

            if comp_type == "voltage_source":
                self._add_voltage_source(pyspice_circuit, comp, component_counts)
            elif comp_type == "current_source":
                self._add_current_source(pyspice_circuit, comp, component_counts)
            elif comp_type == "resistor":
                self._add_resistor(pyspice_circuit, comp, component_counts)
            elif comp_type == "capacitor":
                self._add_capacitor(pyspice_circuit, comp, component_counts)
            elif comp_type == "inductor":
                self._add_inductor(pyspice_circuit, comp, component_counts)
            else:
                raise ValueError(f"Unknown component type: {comp_type}")

        return pyspice_circuit

    def _get_component_id(self, comp: Dict, counts: Dict[str, int]) -> str:
        """Get unique component identifier."""
        # Use provided name if it doesn't start with the type prefix
        name = comp.get("name", "")
        comp_type = comp["type"]

        # Map component types to SPICE prefixes
        type_prefixes = {
            "voltage_source": "V",
            "current_source": "I",
            "resistor": "R",
            "capacitor": "C",
            "inductor": "L",
        }

        prefix = type_prefixes.get(comp_type, "X")

        # If name starts with correct prefix, use it as-is
        if name.upper().startswith(prefix):
            return name

        # Otherwise, generate a unique name
        if comp_type not in counts:
            counts[comp_type] = 0
        counts[comp_type] += 1

        # If user provided a name, append it
        if name:
            return f"{prefix}{counts[comp_type]}_{name}"
        else:
            return f"{prefix}{counts[comp_type]}"

    def _node_to_pyspice(self, node: Any, pyspice_circuit: Any) -> Any:
        """Convert node identifier to PySpice format."""
        # Node 0 is ground in PySpice
        if node == 0 or node == "0" or str(node).lower() == "gnd":
            return pyspice_circuit.gnd
        return node

    def _add_voltage_source(self, pyspice_circuit: Any, comp: Dict, counts: Dict[str, int]):
        """Add voltage source to PySpice circuit."""
        from PySpice.Unit import u_V

        name = self._get_component_id(comp, counts)
        node1 = self._node_to_pyspice(comp["positive"], pyspice_circuit)
        node2 = self._node_to_pyspice(comp["negative"], pyspice_circuit)

        # Parse voltage value
        voltage = parse_value(comp["dc_value"])

        # Add to circuit (remove the prefix from name since PySpice adds it)
        if name.upper().startswith("V"):
            name = name[1:]  # Remove V prefix

        # Use PySpice units correctly (using @ operator with unit objects)
        pyspice_circuit.V(name, node1, node2, voltage @ u_V)

    def _add_current_source(self, pyspice_circuit: Any, comp: Dict, counts: Dict[str, int]):
        """Add current source to PySpice circuit."""
        from PySpice.Unit import u_A

        name = self._get_component_id(comp, counts)
        node1 = self._node_to_pyspice(comp["positive"], pyspice_circuit)
        node2 = self._node_to_pyspice(comp["negative"], pyspice_circuit)

        # Parse current value
        current = parse_value(comp["dc_value"])

        # Add to circuit
        if name.upper().startswith("I"):
            name = name[1:]  # Remove I prefix

        # Use PySpice units correctly
        pyspice_circuit.I(name, node1, node2, current @ u_A)

    def _add_resistor(self, pyspice_circuit: Any, comp: Dict, counts: Dict[str, int]):
        """Add resistor to PySpice circuit."""
        from PySpice.Unit import u_Ohm

        name = self._get_component_id(comp, counts)
        node1 = self._node_to_pyspice(comp["node1"], pyspice_circuit)
        node2 = self._node_to_pyspice(comp["node2"], pyspice_circuit)

        # Parse resistance value
        resistance = parse_value(comp["resistance"])

        # Add to circuit
        if name.upper().startswith("R"):
            name = name[1:]  # Remove R prefix

        # Use PySpice units correctly
        pyspice_circuit.R(name, node1, node2, resistance @ u_Ohm)

    def _add_capacitor(self, pyspice_circuit: Any, comp: Dict, counts: Dict[str, int]):
        """Add capacitor to PySpice circuit."""
        from PySpice.Unit import u_F

        name = self._get_component_id(comp, counts)
        node1 = self._node_to_pyspice(comp["node1"], pyspice_circuit)
        node2 = self._node_to_pyspice(comp["node2"], pyspice_circuit)

        # Parse capacitance value
        capacitance = parse_value(comp["capacitance"])

        # Add to circuit
        if name.upper().startswith("C"):
            name = name[1:]  # Remove C prefix

        # Use PySpice units correctly
        pyspice_circuit.C(name, node1, node2, capacitance @ u_F)

    def _add_inductor(self, pyspice_circuit: Any, comp: Dict, counts: Dict[str, int]):
        """Add inductor to PySpice circuit."""
        from PySpice.Unit import u_H

        name = self._get_component_id(comp, counts)
        node1 = self._node_to_pyspice(comp["node1"], pyspice_circuit)
        node2 = self._node_to_pyspice(comp["node2"], pyspice_circuit)

        # Parse inductance value
        inductance = parse_value(comp["inductance"])

        # Add to circuit
        if name.upper().startswith("L"):
            name = name[1:]  # Remove L prefix

        # Use PySpice units correctly
        pyspice_circuit.L(name, node1, node2, inductance @ u_H)
