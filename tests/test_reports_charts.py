"""
Test cases for Plotly chart generation.

Tests interactive chart generation for DC, transient, and AC analysis.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


import numpy as np
import pytest

from circuit_sim.circuit import Circuit
from circuit_sim.reports.charts.plotly_charts import PlotlyChartGenerator
from circuit_sim.simulator.results import SimulationResults


class TestPlotlyChartGenerator:
    """Test the PlotlyChartGenerator class."""

    def setup_method(self):
        """Setup test fixtures."""
        self.chart_generator = PlotlyChartGenerator()

    def test_chart_generator_initialization(self):
        """Test chart generator initializes correctly."""
        assert self.chart_generator is not None
        assert hasattr(self.chart_generator, "color_palette")
        assert len(self.chart_generator.color_palette) > 0

    def test_create_charts_dc_analysis(self):
        """Test DC analysis chart creation."""
        # Create DC simulation results
        results = SimulationResults("dc")
        results.add_voltage(1, 5.0)
        results.add_voltage(2, 3.0)
        results.add_current("R1", 0.002)

        circuit = Circuit("DC Test")
        circuit.add_resistor("R1", 1, 2, "1k")

        charts = self.chart_generator.create_charts(results, circuit)

        assert isinstance(charts, dict)
        assert "dc_voltages" in charts

        # Check chart properties
        dc_chart = charts["dc_voltages"]
        assert dc_chart.layout.title.text == "DC Operating Points"
        assert len(dc_chart.data) > 0

    def test_create_charts_transient_analysis(self):
        """Test transient analysis chart creation."""
        # Create transient simulation results
        time = np.linspace(0, 0.01, 100)
        voltage = 5 * (1 - np.exp(-time / 0.001))

        results = SimulationResults("transient")
        results.set_time_vector(time)
        results.add_voltage(1, voltage)
        results.add_current("R1", voltage / 1000)  # Ohm's law

        circuit = Circuit("Transient Test")
        circuit.add_resistor("R1", 1, 0, "1k")

        charts = self.chart_generator.create_charts(results, circuit)

        assert isinstance(charts, dict)
        assert "transient_voltages" in charts

        # Check chart properties
        transient_chart = charts["transient_voltages"]
        assert "Node Voltages vs Time" in transient_chart.layout.title.text
        assert len(transient_chart.data) > 0

    def test_create_charts_ac_analysis(self):
        """Test AC analysis chart creation."""
        # Create AC simulation results
        frequency = np.logspace(1, 5, 100)
        magnitude = 1 / np.sqrt(1 + (frequency / 1000) ** 2)
        phase = -np.arctan(frequency / 1000)
        complex_voltage = magnitude * np.exp(1j * phase)

        results = SimulationResults("ac")
        results.set_frequency_vector(frequency)
        results.add_voltage(1, complex_voltage)

        circuit = Circuit("AC Test")
        circuit.add_resistor("R1", 1, 0, "1k")
        circuit.add_capacitor("C1", 1, 0, "1u")

        charts = self.chart_generator.create_charts(results, circuit)

        assert isinstance(charts, dict)
        # Should have bode plot for node 1
        assert "bode_node_1" in charts

        # Check Bode plot properties
        bode_chart = charts["bode_node_1"]
        assert "Bode Plot" in bode_chart.layout.title.text
        assert len(bode_chart.data) == 2  # Magnitude and phase traces

    def test_create_charts_empty_results(self):
        """Test chart creation with empty results."""
        results = SimulationResults("dc")
        circuit = Circuit("Empty")

        charts = self.chart_generator.create_charts(results, circuit)

        assert isinstance(charts, dict)
        # Should return empty dictionary or handle gracefully

    def test_create_comparison_chart_transient(self):
        """Test comparison chart creation for transient results."""
        # Create two different transient results
        time = np.linspace(0, 0.01, 100)
        voltage1 = 5 * (1 - np.exp(-time / 0.001))
        voltage2 = 5 * (1 - np.exp(-time / 0.002))

        results1 = SimulationResults("transient")
        results1.set_time_vector(time)
        results1.add_voltage(1, voltage1)

        results2 = SimulationResults("transient")
        results2.set_time_vector(time)
        results2.add_voltage(1, voltage2)

        comparison_chart = self.chart_generator.create_comparison_chart(
            [results1, results2], ["Fast RC", "Slow RC"]
        )

        assert comparison_chart is not None
        assert "Comparison" in comparison_chart.layout.title
        assert len(comparison_chart.data) == 2  # Two traces

    def test_create_comparison_chart_ac(self):
        """Test comparison chart creation for AC results."""
        frequency = np.logspace(1, 5, 100)

        # Two different filter responses
        magnitude1 = 1 / np.sqrt(1 + (frequency / 1000) ** 2)
        magnitude2 = 1 / np.sqrt(1 + (frequency / 10000) ** 2)

        complex1 = magnitude1 * np.exp(1j * -np.arctan(frequency / 1000))
        complex2 = magnitude2 * np.exp(1j * -np.arctan(frequency / 10000))

        results1 = SimulationResults("ac")
        results1.set_frequency_vector(frequency)
        results1.add_voltage(1, complex1)

        results2 = SimulationResults("ac")
        results2.set_frequency_vector(frequency)
        results2.add_voltage(1, complex2)

        comparison_chart = self.chart_generator.create_comparison_chart(
            [results1, results2], ["1kHz Filter", "10kHz Filter"]
        )

        assert comparison_chart is not None
        assert comparison_chart.layout.xaxis.type == "log"
        assert len(comparison_chart.data) == 2

    def test_comparison_chart_validation(self):
        """Test comparison chart input validation."""
        with pytest.raises(ValueError):
            # Mismatched lengths
            self.chart_generator.create_comparison_chart(
                [SimulationResults("dc")], ["label1", "label2"]
            )

    def test_dc_chart_with_currents(self):
        """Test DC chart generation includes current data when available."""
        results = SimulationResults("dc")
        results.add_voltage(1, 5.0)
        results.add_current("R1", 0.005)
        results.add_current("R2", 0.003)

        circuit = Circuit("DC with currents")
        circuit.add_resistor("R1", 1, 0, "1k")
        circuit.add_resistor("R2", 1, 0, "1.5k")

        charts = self.chart_generator.create_charts(results, circuit)

        assert "dc_voltages" in charts
        assert "dc_currents" in charts

        current_chart = charts["dc_currents"]
        assert "Component Currents" in current_chart.layout.title.text

    def test_transient_combined_chart(self):
        """Test combined voltage and current chart for transient analysis."""
        time = np.linspace(0, 0.01, 100)
        voltage = 5 * (1 - np.exp(-time / 0.001))
        current = voltage / 1000  # Simple I = V/R

        results = SimulationResults("transient")
        results.set_time_vector(time)
        results.add_voltage(1, voltage)
        results.add_current("R1", current)

        circuit = Circuit("Combined test")

        charts = self.chart_generator.create_charts(results, circuit)

        assert "transient_combined" in charts
        combined_chart = charts["transient_combined"]
        assert combined_chart.layout.height == 800  # Taller for subplot

    def test_ac_frequency_response_overview(self):
        """Test AC frequency response overview with multiple nodes."""
        frequency = np.logspace(1, 5, 100)

        # Multiple node responses
        voltage1 = (
            1
            / np.sqrt(1 + (frequency / 1000) ** 2)
            * np.exp(1j * -np.arctan(frequency / 1000))
        )
        voltage2 = (
            0.5
            / np.sqrt(1 + (frequency / 2000) ** 2)
            * np.exp(1j * -np.arctan(frequency / 2000))
        )

        results = SimulationResults("ac")
        results.set_frequency_vector(frequency)
        results.add_voltage(1, voltage1)
        results.add_voltage(2, voltage2)

        circuit = Circuit("Multi-node AC")

        charts = self.chart_generator.create_charts(results, circuit)

        assert "frequency_response" in charts
        overview_chart = charts["frequency_response"]
        assert len(overview_chart.data) == 2  # Two nodes

    def test_chart_styling_consistency(self):
        """Test that charts use consistent styling."""
        results = SimulationResults("dc")
        results.add_voltage(1, 5.0)

        circuit = Circuit("Style test")

        charts = self.chart_generator.create_charts(results, circuit)

        for chart_name, chart in charts.items():
            # Check template is set
            assert chart.layout.template == "plotly_white"

            # Check title is centered
            if hasattr(chart.layout.title, "x"):
                assert chart.layout.title.x == 0.5

    def test_color_palette_usage(self):
        """Test that color palette is used correctly."""
        time = np.linspace(0, 0.01, 100)

        results = SimulationResults("transient")
        results.set_time_vector(time)

        # Add multiple voltage traces
        for i in range(5):
            voltage = (i + 1) * (1 - np.exp(-time / 0.001))
            results.add_voltage(i + 1, voltage)

        circuit = Circuit("Color test")

        charts = self.chart_generator.create_charts(results, circuit)

        if "transient_voltages" in charts:
            chart = charts["transient_voltages"]
            # Should have 5 traces with different colors
            assert len(chart.data) == 5

            colors_used = [trace.line.color for trace in chart.data]
            # Should use color palette colors
            for color in colors_used:
                assert color in self.chart_generator.color_palette

    def test_hover_template_formatting(self):
        """Test that hover templates are properly formatted."""
        time = np.linspace(0, 0.01, 10)  # Small dataset for testing
        voltage = 5 * np.ones_like(time)

        results = SimulationResults("transient")
        results.set_time_vector(time)
        results.add_voltage(1, voltage)

        circuit = Circuit("Hover test")

        charts = self.chart_generator.create_charts(results, circuit)

        if "transient_voltages" in charts:
            chart = charts["transient_voltages"]
            for trace in chart.data:
                assert hasattr(trace, "hovertemplate")
                assert "Time:" in trace.hovertemplate
                assert "Voltage:" in trace.hovertemplate
