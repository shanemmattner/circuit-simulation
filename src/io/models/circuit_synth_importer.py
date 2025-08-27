"""
Circuit-synth JSON importer.

Simplified version of circuit-synth's json_loader for basic import functionality.
"""

from typing import Any, Dict

from circuit_sim import Circuit


class CircuitSynthImporter:
    """Import circuit-synth JSON format to Circuit objects."""

    def import_from_dict(self, data: Dict[str, Any]) -> Circuit:
        """Import circuit from circuit-synth JSON dictionary."""
        circuit_name = data.get("name", "Imported Circuit")
        circuit = Circuit(circuit_name)

        # Parse components
        components_data = data.get("components", {})
        for ref, comp_data in components_data.items():
            symbol = comp_data.get("symbol", "")
            value = comp_data.get("value", "")

            # Map common symbols to circuit components
            if "Device:R" in symbol or ref.startswith("R"):
                circuit.add_resistor(ref, "1", "0", value or "1k")
            elif "Device:C" in symbol or ref.startswith("C"):
                circuit.add_capacitor(ref, "1", "0", value or "1uF")
            elif "Device:L" in symbol or ref.startswith("L"):
                circuit.add_inductor(ref, "1", "0", value or "1mH")
            elif "power:" in symbol or ref.startswith("V"):
                # Power supply symbols
                circuit.add_voltage_source(ref, "1", "0", value or "5V")

        # Store subcircuits for later processing
        subcircuits = data.get("subcircuits", [])
        if subcircuits:
            circuit._subcircuits = subcircuits

        return circuit

    def import_subcircuit(self, subcircuit_data: Dict[str, Any]) -> Circuit:
        """Import individual subcircuit for simulation."""
        return self.import_from_dict(subcircuit_data)
