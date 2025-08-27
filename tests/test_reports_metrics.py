"""
Test cases for the report metrics calculator.

Tests metric calculations for DC, transient, and AC analysis results.
"""

import numpy as np
import pytest
from unittest.mock import Mock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from circuit_sim.reports.utils.metrics import MetricsCalculator
from circuit_sim.simulator.results import SimulationResults
from circuit_sim.circuit import Circuit


class TestMetricsCalculator:
    """Test the MetricsCalculator class."""

    def setup_method(self):
        """Setup test fixtures."""
        self.calculator = MetricsCalculator()

    def test_calculate_dc_power_dissipation(self):
        """Test DC power dissipation calculation."""
        # Create mock results
        results = SimulationResults("dc")
        results.add_voltage(1, 5.0)  # 5V at node 1
        results.add_voltage(2, 3.0)  # 3V at node 2
        results.add_current("R1", 0.005)  # 5mA through R1
        
        # Create mock circuit
        circuit = Circuit("Test")
        circuit.add_resistor("R1", 1, 2, "1k")
        
        metrics = self.calculator.calculate_metrics(results, circuit)
        
        assert "power_dissipation" in metrics
        assert isinstance(metrics["power_dissipation"], float)
        assert metrics["power_dissipation"] > 0

    def test_calculate_dc_efficiency(self):
        """Test DC efficiency calculation."""
        results = SimulationResults("dc")
        results.add_voltage(1, 5.0)
        results.add_current("V1", 0.01)  # Source current
        results.add_current("R1", 0.005)  # Load current
        
        circuit = Circuit("Test")
        circuit.add_voltage_source("V1", 1, 0, "5V")
        circuit.add_resistor("R1", 1, 0, "1k")
        
        metrics = self.calculator.calculate_metrics(results, circuit)
        
        assert "efficiency" in metrics
        assert 0 <= metrics["efficiency"] <= 1

    def test_calculate_transient_rise_time(self):
        """Test transient rise time calculation."""
        # Create step response data
        time = np.linspace(0, 0.01, 1000)
        voltage = 5 * (1 - np.exp(-time / 0.001))  # RC charging curve
        
        results = SimulationResults("transient")
        results.set_time_vector(time)
        results.add_voltage(1, voltage)
        
        circuit = Circuit("Test RC")
        circuit.add_resistor("R1", 1, 2, "1k")
        circuit.add_capacitor("C1", 2, 0, "1u")
        
        metrics = self.calculator.calculate_metrics(results, circuit)
        
        assert "rise_time" in metrics
        assert metrics["rise_time"] > 0
        assert metrics["rise_time"] < 0.01  # Should be less than total time

    def test_calculate_transient_settling_time(self):
        """Test transient settling time calculation."""
        time = np.linspace(0, 0.01, 1000)
        # Underdamped response with settling
        voltage = 5 * (1 - 1.1 * np.exp(-time / 0.002) * np.cos(2 * np.pi * 100 * time))
        
        results = SimulationResults("transient")
        results.set_time_vector(time)
        results.add_voltage(1, voltage)
        
        circuit = Circuit("Test RLC")
        
        metrics = self.calculator.calculate_metrics(results, circuit)
        
        assert "settling_time" in metrics
        assert metrics["settling_time"] > 0

    def test_calculate_transient_overshoot(self):
        """Test transient overshoot calculation."""
        time = np.linspace(0, 0.01, 1000)
        # Response with overshoot
        voltage = 5 * (1 - 1.2 * np.exp(-time / 0.001) * np.cos(2 * np.pi * 500 * time))
        
        results = SimulationResults("transient")
        results.set_time_vector(time)
        results.add_voltage(1, voltage)
        
        circuit = Circuit("Test")
        
        metrics = self.calculator.calculate_metrics(results, circuit)
        
        assert "overshoot" in metrics
        assert metrics["overshoot"] >= 0
        assert metrics["overshoot"] <= 100  # Percentage

    def test_calculate_ac_bandwidth(self):
        """Test AC bandwidth calculation."""
        frequency = np.logspace(1, 6, 1000)  # 10 Hz to 1 MHz
        # Low-pass filter response
        magnitude = 1 / np.sqrt(1 + (frequency / 1000) ** 2)
        complex_response = magnitude * np.exp(1j * np.angle(-1j * frequency / 1000))
        
        results = SimulationResults("ac")
        results.set_frequency_vector(frequency)
        results.add_voltage(1, complex_response)
        
        circuit = Circuit("Low-pass filter")
        
        metrics = self.calculator.calculate_metrics(results, circuit)
        
        assert "bandwidth" in metrics
        assert metrics["bandwidth"] > 0
        assert metrics["bandwidth"] < frequency[-1]

    def test_calculate_ac_gain(self):
        """Test AC gain calculation."""
        frequency = np.logspace(1, 6, 100)
        magnitude = np.ones_like(frequency) * 2.0  # 6dB gain
        complex_response = magnitude * np.exp(1j * np.zeros_like(frequency))
        
        results = SimulationResults("ac")
        results.set_frequency_vector(frequency)
        results.add_voltage(1, complex_response)
        
        circuit = Circuit("Amplifier")
        
        metrics = self.calculator.calculate_metrics(results, circuit)
        
        assert "gain" in metrics
        assert abs(metrics["gain"] - 6.0) < 0.1  # Should be ~6dB

    def test_calculate_ac_phase_margin(self):
        """Test AC phase margin calculation."""
        frequency = np.logspace(1, 6, 1000)
        # Create frequency response with phase margin
        magnitude = 1 / (1 + (frequency / 1000) ** 2)
        phase = -2 * np.arctan(frequency / 1000)
        complex_response = magnitude * np.exp(1j * phase)
        
        results = SimulationResults("ac")
        results.set_frequency_vector(frequency)
        results.add_voltage(1, complex_response)
        
        circuit = Circuit("Feedback system")
        
        metrics = self.calculator.calculate_metrics(results, circuit)
        
        assert "phase_margin" in metrics
        assert -180 <= metrics["phase_margin"] <= 180

    def test_no_data_returns_empty_metrics(self):
        """Test that empty results return empty metrics."""
        results = SimulationResults("dc")
        circuit = Circuit("Empty")
        
        metrics = self.calculator.calculate_metrics(results, circuit)
        
        assert isinstance(metrics, dict)
        # Should have at least basic metrics or be empty

    def test_invalid_analysis_type_handled_gracefully(self):
        """Test that invalid analysis types are handled gracefully."""
        results = SimulationResults("invalid_type")
        circuit = Circuit("Test")
        
        metrics = self.calculator.calculate_metrics(results, circuit)
        
        assert isinstance(metrics, dict)

    def test_power_calculation_with_zero_current(self):
        """Test power calculation handles zero current gracefully."""
        results = SimulationResults("dc")
        results.add_voltage(1, 5.0)
        results.add_current("R1", 0.0)  # Zero current
        
        circuit = Circuit("Test")
        circuit.add_resistor("R1", 1, 0, "inf")  # Infinite resistance
        
        metrics = self.calculator.calculate_metrics(results, circuit)
        
        assert "power_dissipation" in metrics
        assert metrics["power_dissipation"] == 0.0