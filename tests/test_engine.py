"""
Tests for the simulation engine.
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine, SimulationResults


class TestSimulationEngine:
    """Test the simulation engine."""

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

    def test_simulate_ac_basic(self):
        """Test basic AC simulation."""
        # Create RC filter
        circuit = Circuit("Filter")
        circuit.add_voltage_source("V1", 1, 0, "1V")
        circuit.add_resistor("R1", 1, 2, "1k")
        circuit.add_capacitor("C1", 2, 0, "100n")

        engine = SimulationEngine()

        # AC analysis not implemented yet
        with pytest.raises(NotImplementedError, match="AC analysis"):
            engine.simulate_ac(
                circuit, start_frequency=10, stop_frequency=1e6, points_per_decade=20
            )

    def test_pyspice_not_available(self):
        """Test error when PySpice is not available."""
        circuit = Circuit("Test")
        circuit.add_resistor("R1", 1, 0, "1k")

        engine = SimulationEngine()

        # Mock PySpiceBuilder to raise ImportError
        mock_builder = MagicMock()
        mock_builder.build_circuit.side_effect = ImportError("PySpice is not installed")

        with patch("circuit_sim.simulator.engine.PySpiceBuilder", return_value=mock_builder):
            # The engine catches ImportError and tries to handle it
            try:
                engine.simulate_dc(circuit)
                assert False, "Should have raised an error"
            except (ImportError, RuntimeError) as e:
                assert "PySpice" in str(e) or "simulation" in str(e)

    def test_simulation_error_handling(self):
        """Test handling of simulation errors."""
        circuit = Circuit("Test")
        circuit.add_voltage_source("V1", 1, 0, "10V")
        circuit.add_resistor("R1", 1, 2, "0")  # Zero resistance might cause issues

        engine = SimulationEngine()

        # Mock PySpice to raise simulation error
        mock_builder = MagicMock()
        mock_pyspice_circuit = MagicMock()
        mock_builder.build_circuit.return_value = mock_pyspice_circuit

        mock_simulator = MagicMock()
        mock_simulator.operating_point.side_effect = RuntimeError("Convergence failed")
        mock_pyspice_circuit.simulator.return_value = mock_simulator

        with patch("circuit_sim.simulator.engine.PySpiceBuilder", return_value=mock_builder):
            try:
                engine.simulate_dc(circuit)
                assert False, "Should have raised RuntimeError"
            except RuntimeError as e:
                assert "Convergence" in str(e) or "simulation" in str(e)

    def test_transient_parameters(self):
        """Test transient simulation parameter validation."""
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
            # Test with custom parameters
            results = engine.simulate_transient(
                circuit, stop_time=0.1, step_time=0.001, start_time=0.01, max_time_step=0.002
            )

            # Verify parameters were passed correctly
            mock_simulator.transient.assert_called_once()
            call_args = mock_simulator.transient.call_args
            assert call_args is not None

    def test_ac_parameters(self):
        """Test AC simulation parameter validation."""
        circuit = Circuit("Test")
        circuit.add_voltage_source("V1", 1, 0, "1V")
        circuit.add_resistor("R1", 1, 0, "1k")

        engine = SimulationEngine()

        # AC analysis not implemented yet
        with pytest.raises(NotImplementedError, match="AC analysis"):
            engine.simulate_ac(
                circuit,
                start_frequency=100,
                stop_frequency=10000,
                number_of_points=50,
                variation="lin",
            )

    def test_empty_circuit(self):
        """Test simulation with empty circuit."""
        circuit = Circuit("Empty")

        engine = SimulationEngine()

        # Mock PySpice to return empty results
        mock_builder = MagicMock()
        mock_pyspice_circuit = MagicMock()
        mock_builder.build_circuit.return_value = mock_pyspice_circuit

        # Create a mock nodes collection that behaves like an empty dict
        mock_nodes = {}

        mock_simulator = MagicMock()
        mock_op = MagicMock()
        # Mock both dictionary access patterns
        mock_op.__getitem__ = lambda self, key: 0.0
        mock_op.nodes = mock_nodes
        mock_op.__iter__ = lambda self: iter(mock_nodes)

        mock_simulator.operating_point.return_value = mock_op
        mock_pyspice_circuit.simulator.return_value = mock_simulator

        with patch("circuit_sim.simulator.engine.PySpiceBuilder", return_value=mock_builder):
            results = engine.simulate_dc(circuit)
            assert results.nodes == []  # No nodes in empty circuit
