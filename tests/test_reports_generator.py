"""
Test cases for the main ReportGenerator class.

Tests the complete report generation pipeline integration.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import tempfile

import numpy as np
import pytest

from circuit_sim.circuit import Circuit
from circuit_sim.reports.generator import ReportGenerator
from circuit_sim.simulator.results import SimulationResults


class TestReportGenerator:
    """Test the ReportGenerator class."""

    def setup_method(self):
        """Setup test fixtures."""
        self.generator = ReportGenerator()

        # Create test circuit
        self.circuit = Circuit("Test Circuit")
        self.circuit.add_voltage_source("V1", 1, 0, "5V")
        self.circuit.add_resistor("R1", 1, 2, "1k")
        self.circuit.add_resistor("R2", 2, 0, "2k")

        # Create test DC results
        self.dc_results = SimulationResults("dc")
        self.dc_results.add_voltage(1, 5.0)
        self.dc_results.add_voltage(2, 3.33)
        self.dc_results.add_current("V1", 0.00167)
        self.dc_results.add_current("R1", 0.00167)
        self.dc_results.add_current("R2", 0.00167)

    def test_generator_initialization(self):
        """Test generator initializes with correct components."""
        assert self.generator is not None
        assert hasattr(self.generator, "chart_generator")
        assert hasattr(self.generator, "metrics_calculator")
        assert hasattr(self.generator, "env")

    def test_generate_html_report_detailed(self):
        """Test generating detailed HTML report."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_report.html")

            result_path = self.generator.generate_report(
                circuit=self.circuit,
                results=self.dc_results,
                report_type="detailed",
                output_format="html",
                output_path=output_path,
            )

            assert result_path == output_path
            assert os.path.exists(output_path)

            # Read and verify content
            with open(output_path, "r") as f:
                content = f.read()

            assert "Test Circuit" in content
            assert "DC Operating Points" in content
            assert "5.0" in content  # Voltage value
            assert "3.33" in content  # Second voltage value

    def test_generate_html_report_quick(self):
        """Test generating quick HTML report."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "quick_report.html")

            result_path = self.generator.generate_report(
                circuit=self.circuit,
                results=self.dc_results,
                report_type="quick",
                output_format="html",
                output_path=output_path,
            )

            assert os.path.exists(result_path)

            with open(result_path, "r") as f:
                content = f.read()

            assert "Quick Analysis Summary" in content
            assert "Test Circuit" in content

    def test_generate_html_report_executive(self):
        """Test generating executive HTML report."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "exec_report.html")

            result_path = self.generator.generate_report(
                circuit=self.circuit,
                results=self.dc_results,
                report_type="executive",
                output_format="html",
                output_path=output_path,
            )

            assert os.path.exists(result_path)

            with open(result_path, "r") as f:
                content = f.read()

            assert "Executive Dashboard" in content
            assert "Business Impact" in content

    def test_generate_report_with_transient_data(self):
        """Test report generation with transient analysis data."""
        # Create transient results
        time = np.linspace(0, 0.01, 100)
        voltage = 5 * (1 - np.exp(-time / 0.001))

        transient_results = SimulationResults("transient")
        transient_results.set_time_vector(time)
        transient_results.add_voltage(1, voltage)
        transient_results.add_current("R1", voltage / 1000)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "transient_report.html")

            result_path = self.generator.generate_report(
                circuit=self.circuit,
                results=transient_results,
                report_type="detailed",
                output_format="html",
                output_path=output_path,
            )

            assert os.path.exists(result_path)

            with open(result_path, "r") as f:
                content = f.read()

            assert "Transient Analysis" in content
            assert (
                "Rise Time" in content or "Settling Time" in content
            )  # Should have metrics

    def test_generate_report_with_custom_description(self):
        """Test report generation with custom description."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "custom_report.html")

            result_path = self.generator.generate_report(
                circuit=self.circuit,
                results=self.dc_results,
                report_type="detailed",
                output_format="html",
                output_path=output_path,
                description="Custom circuit analysis for testing",
            )

            with open(result_path, "r") as f:
                content = f.read()

            assert "Custom circuit analysis for testing" in content

    def test_generate_report_auto_path(self):
        """Test report generation with automatic path generation."""
        result_path = self.generator.generate_report(
            circuit=self.circuit,
            results=self.dc_results,
            report_type="quick",
            output_format="html",
        )

        try:
            assert os.path.exists(result_path)
            assert result_path.endswith(".html")
            assert "Test_Circuit" in result_path or "Test-Circuit" in result_path

            with open(result_path, "r") as f:
                content = f.read()

            assert "Test Circuit" in content

        finally:
            if os.path.exists(result_path):
                os.unlink(result_path)

    def test_invalid_report_type(self):
        """Test error handling for invalid report type."""
        with pytest.raises(ValueError, match="report_type must be one of"):
            self.generator.generate_report(
                circuit=self.circuit,
                results=self.dc_results,
                report_type="invalid_type",
            )

    def test_invalid_output_format(self):
        """Test error handling for invalid output format."""
        with pytest.raises(ValueError, match="output_format must be one of"):
            self.generator.generate_report(
                circuit=self.circuit,
                results=self.dc_results,
                output_format="invalid_format",
            )

    def test_prepare_report_data(self):
        """Test the internal _prepare_report_data method."""
        report_data = self.generator._prepare_report_data(
            self.circuit, self.dc_results, "detailed"
        )

        # Check all expected keys are present
        expected_keys = [
            "metadata",
            "circuit",
            "results",
            "charts",
            "metrics",
            "summary",
            "raw_circuit",
            "raw_results",
        ]

        for key in expected_keys:
            assert key in report_data

        # Check metadata content
        metadata = report_data["metadata"]
        assert metadata["circuit_name"] == "Test Circuit"
        assert metadata["component_count"] == 3
        assert metadata["analysis_type"] == "dc"

        # Check circuit analysis
        circuit_data = report_data["circuit"]
        assert circuit_data["total_components"] == 3
        assert len(circuit_data["components"]) == 3

        # Check that charts were generated
        assert "charts" in report_data
        assert isinstance(report_data["charts"], dict)

    def test_circuit_analysis(self):
        """Test the _analyze_circuit method."""
        circuit_analysis = self.generator._analyze_circuit(self.circuit)

        assert "components" in circuit_analysis
        assert "component_types" in circuit_analysis
        assert "total_components" in circuit_analysis
        assert "total_nodes" in circuit_analysis

        # Should have 3 components
        assert len(circuit_analysis["components"]) == 3
        assert circuit_analysis["total_components"] == 3

        # Check component types breakdown
        component_types = circuit_analysis["component_types"]
        assert "voltage_source" in component_types
        assert "resistor" in component_types
        assert component_types["resistor"] == 2

    def test_get_component_value(self):
        """Test component value extraction."""
        resistor = {"type": "resistor", "resistance": "1k"}
        voltage_source = {"type": "voltage_source", "dc_value": "5V"}
        capacitor = {"type": "capacitor", "capacitance": "1u"}

        assert self.generator._get_component_value(resistor) == "1k"
        assert self.generator._get_component_value(voltage_source) == "5V"
        assert self.generator._get_component_value(capacitor) == "1u"

    def test_get_component_nodes(self):
        """Test component node extraction."""
        resistor = {"node1": 1, "node2": 2}
        voltage_source = {"positive": 1, "negative": 0}

        assert self.generator._get_component_nodes(resistor) == "1 - 2"
        assert self.generator._get_component_nodes(voltage_source) == "1 - 0"

    def test_process_results_dc(self):
        """Test DC results processing."""
        processed = self.generator._process_results(self.dc_results)

        assert processed["analysis_type"] == "dc"
        assert "dc_operating_points" in processed

        dc_points = processed["dc_operating_points"]
        assert len(dc_points) >= 2  # Should have at least 2 nodes

        # Check node 1 data
        node1_data = next(p for p in dc_points if "Node 1" in p["node"])
        assert node1_data["voltage"] == 5.0

    def test_generate_summary(self):
        """Test summary generation."""
        # Mock metrics for testing
        mock_metrics = {"power_dissipation": 0.025, "efficiency": 0.85}

        summary = self.generator._generate_summary(
            self.dc_results, mock_metrics, self.circuit
        )

        assert "text" in summary
        assert "key_findings" in summary
        assert "recommendations" in summary

        # Should mention DC analysis
        assert "DC" in summary["text"]

        # Should have findings about power and efficiency
        findings = summary["key_findings"]
        assert any("power" in finding.lower() for finding in findings)

    def test_extract_key_findings(self):
        """Test key findings extraction."""
        mock_metrics = {"power_dissipation": 0.1, "efficiency": 0.9, "rise_time": 0.001}

        findings = self.generator._extract_key_findings(self.dc_results, mock_metrics)

        assert len(findings) > 0
        # Should mention power dissipation for DC analysis
        assert any("100.000 mW" in finding for finding in findings)

    def test_generate_recommendations(self):
        """Test recommendations generation."""
        recommendations = self.generator._generate_recommendations(
            self.dc_results, {}, self.circuit
        )

        assert len(recommendations) > 0
        assert isinstance(recommendations[0], str)

    def test_generate_output_path(self):
        """Test automatic output path generation."""
        path = self.generator._generate_output_path(
            "My Test Circuit", "detailed", "html"
        )

        assert path.endswith(".html")
        assert "My_Test_Circuit" in path or "My-Test-Circuit" in path
        assert "detailed" in path
        assert "reports" in path

    def test_memory_efficiency_large_circuit(self):
        """Test memory efficiency with large circuit."""
        # Create larger circuit
        large_circuit = Circuit("Large Test Circuit")
        for i in range(50):
            large_circuit.add_resistor(f"R{i}", i, i + 1, f"{i+1}k")

        # Create results with many nodes
        large_results = SimulationResults("dc")
        for i in range(50):
            large_results.add_voltage(i, float(i) * 0.1)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "large_report.html")

            result_path = self.generator.generate_report(
                circuit=large_circuit,
                results=large_results,
                report_type="quick",  # Use quick to reduce processing
                output_format="html",
                output_path=output_path,
            )

            assert os.path.exists(result_path)

            # File should be reasonable size (not excessive)
            file_size = os.path.getsize(result_path)
            assert file_size < 5 * 1024 * 1024  # Less than 5MB
