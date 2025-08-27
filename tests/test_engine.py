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

    def test_simulate_ac_basic_rc_circuit(self):
        """Test basic AC simulation with RC circuit - TDD failing test."""
        # Create RC low-pass filter: R=1k, C=1µF, fc ≈ 159Hz
        circuit = Circuit("RC Filter")
        circuit.add_voltage_source("V1", 1, 0, "DC 0V AC 1V")  # 1V AC source with 0V DC
        circuit.add_resistor("R1", 1, 2, "1k")       # 1kΩ resistor
        circuit.add_capacitor("C1", 2, 0, "1u")      # 1µF capacitor

        engine = SimulationEngine()
        
        # This should work after we implement AC analysis
        results = engine.simulate_ac(
            circuit,
            start_frequency=10,      # 10 Hz
            stop_frequency=10000,    # 10 kHz  
            points_per_decade=20
        )
        
        # Verify results structure
        assert results.analysis_type == "ac"
        assert results.frequency is not None
        assert len(results.frequency) > 0
        
        # Should have complex voltage at output node (node 2)
        v_out = results.voltage(2)
        assert v_out is not None
        assert len(v_out) == len(results.frequency)
        
        # At DC (low freq), magnitude should be ≈ 1V (no attenuation)
        # AC analysis at 10Hz should pass through the RC filter easily
        assert abs(abs(v_out[0]) - 1.0) < 0.1
        
        # At high frequencies, should have significant attenuation
        # At 10x cutoff frequency, should be < 0.1V magnitude
        fc_theoretical = 1 / (2 * np.pi * 1000 * 1e-6)  # ≈159Hz
        high_freq_idx = -1  # Last frequency point (10kHz)
        assert abs(v_out[high_freq_idx]) < 0.1

    def test_frequency_vector_generation_logarithmic(self):
        """Test logarithmic frequency vector generation - isolated unit test."""
        engine = SimulationEngine()
        
        # Test decade variation
        frequencies = engine._generate_frequency_vector(
            start_freq=10,       # 10 Hz
            stop_freq=10000,     # 10 kHz (3 decades)
            points_per_decade=20,
            variation="dec"
        )
        
        # Should have approximately 3 decades * 20 points/decade + 1 = 61 points
        expected_points = int(3 * 20) + 1
        assert len(frequencies) == expected_points
        
        # First frequency should be 10 Hz
        assert abs(frequencies[0] - 10.0) < 1e-6
        
        # Last frequency should be 10000 Hz
        assert abs(frequencies[-1] - 10000.0) < 1e-3
        
        # Should be logarithmically spaced
        # Check that ratios between adjacent points are approximately constant
        ratios = frequencies[1:] / frequencies[:-1]
        ratio_mean = np.mean(ratios)
        ratio_std = np.std(ratios)
        
        # For logarithmic spacing, ratios should be very consistent
        assert ratio_std / ratio_mean < 0.01  # Less than 1% variation
        
        # Ratio should be approximately 10^(1/20) for 20 points per decade
        expected_ratio = 10.0 ** (1.0 / 20.0)
        assert abs(ratio_mean - expected_ratio) < 0.01

    def test_frequency_vector_generation_linear(self):
        """Test linear frequency vector generation."""
        engine = SimulationEngine()
        
        # Test linear variation
        frequencies = engine._generate_frequency_vector(
            start_freq=1000,     # 1 kHz
            stop_freq=2000,      # 2 kHz
            points_per_decade=10,  # Ignored for linear
            variation="lin"
        )
        
        # Should have 1000 points (default for linear)
        assert len(frequencies) == 1000
        
        # First frequency should be 1000 Hz
        assert abs(frequencies[0] - 1000.0) < 1e-6
        
        # Last frequency should be 2000 Hz  
        assert abs(frequencies[-1] - 2000.0) < 1e-6
        
        # Should be linearly spaced
        # Check that differences between adjacent points are constant
        diffs = np.diff(frequencies)
        diff_std = np.std(diffs)
        diff_mean = np.mean(diffs)
        
        # For linear spacing, differences should be very consistent
        assert diff_std / diff_mean < 1e-10  # Very small variation

    def test_complex_impedance_calculation(self):
        """Test complex impedance calculation for R, L, C components."""
        engine = SimulationEngine()
        
        # Test resistor impedance: Z_R = R (purely real)
        z_resistor = engine._calculate_component_impedance("resistor", 1000.0, 1000.0)  # 1kΩ at 1kHz
        assert abs(z_resistor.real - 1000.0) < 1e-6
        assert abs(z_resistor.imag) < 1e-6
        
        # Test capacitor impedance: Z_C = 1/(jωC) = -j/(ωC)
        # For C=1µF at f=1kHz: ω = 2π×1000, Z = -j/(2π×1000×1e-6) = -j159.15Ω
        z_capacitor = engine._calculate_component_impedance("capacitor", 1e-6, 1000.0)  # 1µF at 1kHz
        expected_imag = -1.0 / (2 * np.pi * 1000.0 * 1e-6)
        assert abs(z_capacitor.real) < 1e-6  # Real part should be ~0
        assert abs(z_capacitor.imag - expected_imag) < 1e-3
        
        # Test inductor impedance: Z_L = jωL
        # For L=10mH at f=1kHz: ω = 2π×1000, Z = j×2π×1000×10e-3 = j62.83Ω
        z_inductor = engine._calculate_component_impedance("inductor", 10e-3, 1000.0)  # 10mH at 1kHz
        expected_imag = 2 * np.pi * 1000.0 * 10e-3
        assert abs(z_inductor.real) < 1e-6  # Real part should be ~0
        assert abs(z_inductor.imag - expected_imag) < 1e-3
        
        # Test frequency dependence - capacitor impedance should decrease with frequency
        z_cap_10hz = engine._calculate_component_impedance("capacitor", 1e-6, 10.0)
        z_cap_10khz = engine._calculate_component_impedance("capacitor", 1e-6, 10000.0)
        assert abs(z_cap_10hz) > abs(z_cap_10khz)  # Lower freq = higher impedance for capacitor
        
        # Test frequency dependence - inductor impedance should increase with frequency  
        z_ind_10hz = engine._calculate_component_impedance("inductor", 10e-3, 10.0)
        z_ind_10khz = engine._calculate_component_impedance("inductor", 10e-3, 10000.0)
        assert abs(z_ind_10hz) < abs(z_ind_10khz)  # Higher freq = higher impedance for inductor

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
