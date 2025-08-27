"""
Simplified tests for the simulation engine.
Focus on basic functionality without complex mocking.
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine, SimulationResults


class TestSimulationEngineBasics:
    """Test basic simulation engine functionality."""

    def test_engine_creation(self):
        """Test that engine can be created."""
        engine = SimulationEngine()
        assert engine is not None

    def test_simulate_dc_basic(self):
        """Test basic DC simulation."""
        # Create simple voltage divider
        circuit = Circuit("Test")
        circuit.add_voltage_source("V1", 1, 0, "10V")
        circuit.add_resistor("R1", 1, 2, "1k")
        circuit.add_resistor("R2", 2, 0, "1k")

        engine = SimulationEngine()

        # Mock PySpice
        mock_builder = MagicMock()
        mock_pyspice_circuit = MagicMock()
        mock_builder.build_circuit.return_value = mock_pyspice_circuit

        # Mock simulator
        mock_simulator = MagicMock()
        mock_op = MagicMock()
        mock_op.__getitem__ = lambda self, key: {
            1: 10.0,
            2: 5.0,
        }.get(key, 0.0)
        mock_simulator.operating_point.return_value = mock_op
        mock_pyspice_circuit.simulator.return_value = mock_simulator

        with patch("circuit_sim.simulator.engine.PySpiceBuilder", return_value=mock_builder):
            results = engine.simulate_dc(circuit)

        assert isinstance(results, SimulationResults)
        assert results.analysis_type == "dc"

    def test_simulate_transient_basic(self):
        """Test basic transient simulation."""
        # Create RC circuit
        circuit = Circuit("RC")
        circuit.add_voltage_source("V1", 1, 0, "5V")
        circuit.add_resistor("R1", 1, 2, "10k")
        circuit.add_capacitor("C1", 2, 0, "1u")

        engine = SimulationEngine()

        # Mock PySpice
        mock_builder = MagicMock()
        mock_pyspice_circuit = MagicMock()
        mock_builder.build_circuit.return_value = mock_pyspice_circuit

        # Mock simulator
        mock_simulator = MagicMock()
        mock_analysis = MagicMock()

        # Create mock time and voltage data
        time = np.linspace(0, 0.001, 100)
        voltage = 5 * (1 - np.exp(-time / (10e3 * 1e-6)))

        mock_analysis.time = time
        mock_analysis.nodes = {1: 10.0 * np.ones(100), 2: voltage}
        mock_analysis.__getitem__ = lambda self, key: self.nodes.get(key)

        mock_simulator.transient.return_value = mock_analysis
        mock_pyspice_circuit.simulator.return_value = mock_simulator

        with patch("circuit_sim.simulator.engine.PySpiceBuilder", return_value=mock_builder):
            results = engine.simulate_transient(circuit, stop_time=0.001, step_time=0.00001)

        assert isinstance(results, SimulationResults)
        assert results.analysis_type == "transient"

    def test_simulate_ac_implemented(self):
        """Test that AC simulation is now implemented."""
        # Create RC filter
        circuit = Circuit("Filter")
        circuit.add_voltage_source("V1", 1, 0, "1V")
        circuit.add_resistor("R1", 1, 2, "1k")
        circuit.add_capacitor("C1", 2, 0, "100n")

        engine = SimulationEngine()

        # AC analysis is now implemented
        results = engine.simulate_ac(
            circuit, start_frequency=10, stop_frequency=1e6, points_per_decade=20
        )
        
        # Verify basic AC results
        assert results.analysis_type == "ac"
        assert results.frequency is not None
        assert len(results.frequency) > 0

    def test_transient_default_parameters(self):
        """Test transient simulation with default parameters."""
        circuit = Circuit("Test")
        circuit.add_voltage_source("V1", 1, 0, "5V")
        circuit.add_resistor("R1", 1, 0, "1k")

        engine = SimulationEngine()

        # Mock PySpice
        mock_builder = MagicMock()
        mock_pyspice_circuit = MagicMock()
        mock_builder.build_circuit.return_value = mock_pyspice_circuit

        mock_simulator = MagicMock()
        mock_analysis = MagicMock()
        mock_analysis.time = np.array([0, 0.001])
        mock_analysis.nodes = {}
        mock_analysis.__getitem__ = lambda self, key: np.array([0, 0])
        mock_simulator.transient.return_value = mock_analysis
        mock_pyspice_circuit.simulator.return_value = mock_simulator

        with patch("circuit_sim.simulator.engine.PySpiceBuilder", return_value=mock_builder):
            # Test with minimal parameters (stop_time is required)
            results = engine.simulate_transient(circuit, stop_time=0.01)
            assert results is not None
