"""
Test real KiCad netlist import with actual files from circuit-synth.
"""

from pathlib import Path

from circuit_sim.simulator import SimulationEngine
from src.io.parsers.kicad_parser import KiCadParser


class TestRealKiCadImport:
    """Test with real KiCad netlist files."""

    def test_import_real_resistor_divider(self):
        """Test importing actual resistor divider .net file from circuit-synth."""
        parser = KiCadParser()

        # Load the real netlist file
        netlist_path = Path("tests/fixtures/netlist_io/kicad/resistor_divider.net")

        with open(netlist_path, "r") as f:
            content = f.read()

        circuit = parser.parse_content(content)

        # Should have 2 resistors
        assert len(circuit.components) == 2
        component_names = [comp.get("name", "") for comp in circuit.components]
        assert "R1" in component_names
        assert "R2" in component_names

        # Check resistor values
        r1 = next(comp for comp in circuit.components if comp.get("name") == "R1")
        r2 = next(comp for comp in circuit.components if comp.get("name") == "R2")
        assert r1.get("resistance") == "10k"
        assert r2.get("resistance") == "10k"

    def test_simulate_imported_resistor_divider(self):
        """Test simulating the imported resistor divider."""
        parser = KiCadParser()

        # Import the circuit
        netlist_path = Path("tests/fixtures/netlist_io/kicad/resistor_divider.net")
        with open(netlist_path, "r") as f:
            content = f.read()

        circuit = parser.parse_content(content)

        # Add a voltage source for simulation (KiCad netlists don't include sources)
        # Based on the netlist: +3V3 net exists, so add 3.3V source
        circuit.add_voltage_source("V_SUPPLY", "+3V3", "GND", "3.3V")

        # Run DC simulation
        engine = SimulationEngine()
        results = engine.simulate_dc(circuit)

        # Voltage divider should give 1.65V at middle node
        # (3.3V * 10k/(10k+10k) = 1.65V)
        middle_voltage = results.voltage("DIVIDER_OUTPUT")[0] if hasattr(results, "voltage") else 0

        # Allow 10% tolerance
        expected = 1.65
        tolerance = 0.165
        assert (
            abs(middle_voltage - expected) < tolerance
        ), f"Expected ~{expected}V, got {middle_voltage}V"

    def test_extract_net_connectivity(self):
        """Test that we correctly extract node connectivity from KiCad nets."""
        parser = KiCadParser()

        # Test with simple content
        kicad_content = """
(nets
  (net (code "1") (name "+3V3")
    (node (ref "R1") (pin "1") (pintype "passive")))
  (net (code "2") (name "/DIVIDER_OUTPUT") 
    (node (ref "R1") (pin "2") (pintype "passive"))
    (node (ref "R2") (pin "1") (pintype "passive")))
  (net (code "3") (name "GND")
    (node (ref "R2") (pin "2") (pintype "passive"))))
        """

        # Should extract connectivity properly
        nets = parser._extract_nets_section(kicad_content)

        assert "+3V3" in nets
        assert "/DIVIDER_OUTPUT" in nets
        assert "GND" in nets

        # Check connections
        assert len(nets["/DIVIDER_OUTPUT"]) == 2  # Connected to R1 pin 2 AND R2 pin 1
