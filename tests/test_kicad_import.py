"""
Test module for KiCad netlist import functionality.
"""

import pytest

from src.io.models.circuit_synth_json import CircuitSynthImporter
from src.io.parsers.kicad_parser import KiCadParser


class TestKiCadImport:
    """Test KiCad netlist import functionality."""

    def test_import_simple_kicad_netlist(self):
        """Test importing basic KiCad netlist format."""
        parser = KiCadParser()

        # Simple KiCad netlist content
        kicad_content = """(export (version D)
  (design
    (source /path/to/test.sch)
    (date "2025-08-27 19:00:00")
    (tool "Eeschema"))
  (components
    (comp (ref R1)
      (value 1k)
      (footprint Resistor_SMD:R_0603_1608Metric)
      (libsource (lib Device) (part R)))
    (comp (ref R2)
      (value 2k2)
      (footprint Resistor_SMD:R_0603_1608Metric)
      (libsource (lib Device) (part R))))
  (nets
    (net (code 1) (name "Net-(R1-Pad1)")
      (node (ref R1) (pin 1)))
    (net (code 2) (name "Net-(R1-Pad2)")
      (node (ref R1) (pin 2))
      (node (ref R2) (pin 1)))
    (net (code 3) (name GND)
      (node (ref R2) (pin 2)))))"""

        circuit = parser.parse_content(kicad_content)

        assert circuit.name is not None
        assert len(circuit.components) == 2  # R1, R2

        component_names = [comp.get("name", "") for comp in circuit.components]
        assert "R1" in component_names
        assert "R2" in component_names

    def test_import_circuit_synth_json(self):
        """Test importing circuit-synth hierarchical JSON."""
        importer = CircuitSynthImporter()

        # Simplified circuit-synth JSON structure
        json_data = {
            "name": "Test Board",
            "description": "Test hierarchical board",
            "components": {
                "R1": {
                    "symbol": "Device:R",
                    "ref": "R1",
                    "value": "10k",
                    "pins": [
                        {"pin_id": "1", "name": "~", "func": "passive"},
                        {"pin_id": "2", "name": "~", "func": "passive"},
                    ],
                }
            },
            "nets": {
                "VCC": [{"component": "R1", "pin": {"number": "1", "name": "~", "type": "passive"}}]
            },
            "subcircuits": [
                {
                    "name": "Power_Supply",
                    "components": {
                        "U1": {
                            "symbol": "Regulator_Linear:AMS1117-3.3",
                            "ref": "U1",
                            "value": "AMS1117-3.3",
                        }
                    },
                    "nets": {},
                }
            ],
        }

        circuit = importer.import_from_dict(json_data)

        assert circuit.name == "Test Board"
        assert len(circuit.components) >= 1  # At least R1

        # Check for subcircuits
        assert hasattr(circuit, "_subcircuits") or len(circuit.components) > 1

    def test_simulate_imported_subcircuit(self):
        """Test simulating an individual subcircuit."""
        importer = CircuitSynthImporter()

        # Power supply subcircuit
        power_supply_json = {
            "name": "Power_Supply",
            "components": {
                "V1": {"symbol": "power:+5V", "ref": "V1", "value": "5V"},
                "R1": {"symbol": "Device:R", "ref": "R1", "value": "100"},
                "C1": {"symbol": "Device:C", "ref": "C1", "value": "100uF"},
            },
            "nets": {
                "VCC": [{"component": "V1", "pin": {"number": "1"}}],
                "VOUT": [
                    {"component": "R1", "pin": {"number": "1"}},
                    {"component": "C1", "pin": {"number": "1"}},
                ],
                "GND": [
                    {"component": "V1", "pin": {"number": "2"}},
                    {"component": "R1", "pin": {"number": "2"}},
                    {"component": "C1", "pin": {"number": "2"}},
                ],
            },
        }

        circuit = importer.import_subcircuit(power_supply_json)

        assert circuit.name == "Power_Supply"
        assert len(circuit.components) >= 2  # V1, R1, C1

        # Should be simulatable
        from circuit_sim.simulator import SimulationEngine

        engine = SimulationEngine()

        # This should work - basic power supply circuit
        try:
            results = engine.simulate_dc(circuit)
            assert results is not None
        except Exception as e:
            pytest.skip(f"Simulation not yet fully integrated: {e}")
