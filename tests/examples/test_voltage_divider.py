"""Tests for voltage divider example circuit."""

from pathlib import Path

import numpy as np

from examples.basic.voltage_divider import (
    VoltageDividerCircuit,
    analyze_divider_ratio,
    generate_report,
    simulate_voltage_divider,
)


class TestVoltageDividerCircuit:
    """Test voltage divider circuit implementation."""

    def test_circuit_creation(self):
        """Test creating a voltage divider circuit."""
        circuit = VoltageDividerCircuit(r1=1000, r2=2000, vin=5.0)

        assert circuit.r1 == 1000
        assert circuit.r2 == 2000
        assert circuit.vin == 5.0
        assert circuit.circuit is not None

    def test_theoretical_output(self):
        """Test theoretical voltage calculation."""
        circuit = VoltageDividerCircuit(r1=1000, r2=1000, vin=10.0)

        # For equal resistors, output should be Vin/2
        expected = 5.0
        actual = circuit.calculate_theoretical_output()
        assert abs(actual - expected) < 0.01

        # For R2 = 2*R1, output should be 2/3 * Vin
        circuit2 = VoltageDividerCircuit(r1=1000, r2=2000, vin=9.0)
        expected2 = 6.0  # 2/3 * 9
        actual2 = circuit2.calculate_theoretical_output()
        assert abs(actual2 - expected2) < 0.01

    def test_netlist_generation(self):
        """Test SPICE netlist generation."""
        circuit = VoltageDividerCircuit(r1=1000, r2=2000, vin=5.0)
        netlist = circuit.generate_netlist()

        assert "Voltage Divider Circuit" in netlist
        assert "V1" in netlist  # Voltage source
        assert "R1" in netlist  # First resistor
        assert "R2" in netlist  # Second resistor
        assert "1k" in netlist or "1000" in netlist
        assert "2k" in netlist or "2000" in netlist
        assert ".dc" in netlist.lower()  # DC analysis

    def test_with_load_resistor(self):
        """Test voltage divider with load resistor."""
        circuit = VoltageDividerCircuit(r1=1000, r2=1000, vin=10.0, r_load=1000)

        # With load, the effective R2 becomes R2 || R_load = 500
        # Output = Vin * (R2||R_load) / (R1 + R2||R_load) = 10 * 500/1500 = 3.33V
        expected = 3.333
        actual = circuit.calculate_theoretical_output()
        assert abs(actual - expected) < 0.01


class TestVoltageDividerSimulation:
    """Test voltage divider simulation."""

    def test_dc_simulation(self):
        """Test DC operating point simulation."""
        circuit = VoltageDividerCircuit(r1=1000, r2=1000, vin=5.0)
        results = simulate_voltage_divider(circuit, analysis_type="dc")

        assert results is not None
        assert "output_voltage" in results
        assert "input_current" in results

        # Check output voltage is approximately Vin/2
        assert abs(results["output_voltage"] - 2.5) < 0.1

    def test_sweep_simulation(self):
        """Test parameter sweep simulation."""
        circuit = VoltageDividerCircuit(r1=1000, r2=1000, vin=5.0)
        results = simulate_voltage_divider(
            circuit, analysis_type="sweep", sweep_param="vin", sweep_range=(0, 10, 0.5)
        )

        assert results is not None
        assert "sweep_values" in results
        assert "output_voltages" in results
        assert len(results["sweep_values"]) == len(results["output_voltages"])

        # Output should be proportional to input
        ratios = np.array(results["output_voltages"]) / np.array(
            results["sweep_values"]
        )
        expected_ratio = 0.5  # For equal resistors
        assert all(abs(r - expected_ratio) < 0.01 for r in ratios[1:])  # Skip 0V

    def test_tolerance_analysis(self):
        """Test resistor tolerance analysis."""
        circuit = VoltageDividerCircuit(r1=1000, r2=1000, vin=5.0)
        results = analyze_divider_ratio(circuit, tolerance=0.05)  # 5% tolerance

        assert "nominal_ratio" in results
        assert "min_ratio" in results
        assert "max_ratio" in results
        assert "sensitivity" in results

        # Nominal ratio should be 0.5 for equal resistors
        assert abs(results["nominal_ratio"] - 0.5) < 0.01

        # Min/max should reflect tolerance
        assert results["min_ratio"] < results["nominal_ratio"]
        assert results["max_ratio"] > results["nominal_ratio"]


class TestVoltageDividerReport:
    """Test report generation for voltage divider."""

    def test_report_generation(self):
        """Test generating interactive report."""
        circuit = VoltageDividerCircuit(r1=1000, r2=2000, vin=5.0)
        results = simulate_voltage_divider(circuit, analysis_type="dc")

        report = generate_report(circuit, results)

        assert report is not None
        assert report.title == "Voltage Divider Analysis"
        assert len(report.figures) > 0

        # Check that report can be saved
        output_path = Path("test_output.html")
        report.save(output_path)
        assert output_path.exists()
        output_path.unlink()  # Clean up

    def test_report_with_sweep(self):
        """Test report with parameter sweep."""
        circuit = VoltageDividerCircuit(r1=1000, r2=1000, vin=5.0)
        results = simulate_voltage_divider(
            circuit,
            analysis_type="sweep",
            sweep_param="r2",
            sweep_range=(100, 10000, 100),
        )

        report = generate_report(circuit, results, include_sweep=True)

        assert len(report.figures) >= 2  # Should have multiple plots
        assert "Parameter Sweep" in str(report.figures)
