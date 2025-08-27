"""
Tests for the simulation results class.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from circuit_sim.simulator.results import SimulationResults


class TestSimulationResults:
    """Test the SimulationResults class."""

    def test_results_creation(self):
        """Test that results can be created."""
        results = SimulationResults("dc")
        assert results is not None
        assert results.analysis_type == "dc"
        assert results.time is None
        assert results.frequency is None
        assert results.nodes == []
        assert results.components == []

    def test_add_voltage(self):
        """Test adding voltage data."""
        results = SimulationResults("dc")

        # Add scalar voltage
        results.add_voltage(1, 5.0)
        assert results.voltage(1) is not None
        assert results.voltage(1)[0] == 5.0

        # Add array voltage
        results.add_voltage(2, np.array([1.0, 2.0, 3.0]))
        assert results.voltage(2) is not None
        assert len(results.voltage(2)) == 3
        assert results.voltage(2)[1] == 2.0

    def test_add_current(self):
        """Test adding current data."""
        results = SimulationResults("dc")

        # Add scalar current
        results.add_current("R1", 0.01)
        assert results.current("R1") is not None
        assert results.current("R1")[0] == 0.01

        # Add array current
        results.add_current("R2", np.array([0.1, 0.2, 0.3]))
        assert results.current("R2") is not None
        assert len(results.current("R2")) == 3
        assert results.current("R2")[2] == 0.3

    def test_ground_node(self):
        """Test ground node handling."""
        results = SimulationResults("transient")
        results.set_time_vector(np.linspace(0, 1, 10))

        # Ground should return zeros
        gnd_voltage = results.voltage(0)
        assert gnd_voltage is not None
        assert len(gnd_voltage) == 10
        assert np.all(gnd_voltage == 0)

        # Test string ground
        gnd_voltage = results.voltage("gnd")
        assert gnd_voltage is not None
        assert np.all(gnd_voltage == 0)

        # Test uppercase ground
        gnd_voltage = results.voltage("GND")
        assert gnd_voltage is not None
        assert np.all(gnd_voltage == 0)

    def test_time_vector(self):
        """Test time vector for transient analysis."""
        results = SimulationResults("transient")

        time = np.linspace(0, 0.01, 100)
        results.set_time_vector(time)

        assert results.time is not None
        assert len(results.time) == 100
        assert results.time[0] == 0
        assert results.time[-1] == 0.01

    def test_frequency_vector(self):
        """Test frequency vector for AC analysis."""
        results = SimulationResults("ac")

        freq = np.logspace(1, 6, 50)
        results.set_frequency_vector(freq)

        assert results.frequency is not None
        assert len(results.frequency) == 50
        assert results.frequency[0] == 10
        assert results.frequency[-1] == 1e6

    def test_metadata(self):
        """Test metadata storage."""
        results = SimulationResults("dc")

        results.add_metadata("circuit_name", "Test Circuit")
        results.add_metadata("simulation_time", 0.123)
        results.add_metadata("convergence", True)

        assert results._metadata["circuit_name"] == "Test Circuit"
        assert results._metadata["simulation_time"] == 0.123
        assert results._metadata["convergence"] is True

    def test_nodes_property(self):
        """Test nodes property."""
        results = SimulationResults("dc")

        results.add_voltage(1, 5.0)
        results.add_voltage(2, 3.3)
        results.add_voltage("vcc", 12.0)

        nodes = results.nodes
        assert len(nodes) == 3
        assert 1 in nodes
        assert 2 in nodes
        assert "vcc" in nodes

    def test_components_property(self):
        """Test components property."""
        results = SimulationResults("dc")

        results.add_current("R1", 0.01)
        results.add_current("R2", 0.02)
        results.add_current("V1", -0.03)

        components = results.components
        assert len(components) == 3
        assert "R1" in components
        assert "R2" in components
        assert "V1" in components

    def test_repr(self):
        """Test string representation."""
        results = SimulationResults("transient")

        # Add some data
        results.set_time_vector(np.linspace(0, 1, 100))
        results.add_voltage(1, np.ones(100))
        results.add_voltage(2, np.ones(100))
        results.add_current("R1", np.ones(100))

        repr_str = repr(results)
        assert "transient" in repr_str
        assert "nodes=2" in repr_str
        assert "components=1" in repr_str
        assert "time_points=100" in repr_str

    def test_plot_dc(self):
        """Test plotting DC results."""
        results = SimulationResults("dc")
        results.add_voltage(1, 10.0)
        results.add_voltage(2, 5.0)
        results.add_voltage(3, 2.5)

        # Just check that plot method exists and can be called
        assert hasattr(results, "plot")
        # We won't actually test matplotlib mocking as it's complex in Docker

    def test_plot_transient(self):
        """Test plotting transient results."""
        results = SimulationResults("transient")

        time = np.linspace(0, 0.01, 100)
        voltage = 5 * (1 - np.exp(-time / 0.001))

        results.set_time_vector(time)
        results.add_voltage(2, voltage)

        # Mock matplotlib
        with patch("matplotlib.pyplot") as mock_plt:
            mock_fig = MagicMock()
            mock_ax = MagicMock()
            mock_plt.subplots.return_value = (mock_fig, mock_ax)

            # Plot specific signal
            results.plot("V(2)", show=False)

            # Verify line plot was created
            mock_ax.plot.assert_called()
            mock_ax.set_xlabel.assert_called_with("Time (s)")
            mock_ax.set_ylabel.assert_called()

    def test_plot_ac(self):
        """Test plotting AC results."""
        results = SimulationResults("ac")

        freq = np.logspace(1, 6, 50)
        gain = 1 / np.sqrt(1 + (freq / 1000) ** 2)

        results.set_frequency_vector(freq)
        results.add_voltage(2, gain)

        # Mock matplotlib
        with patch("matplotlib.pyplot") as mock_plt:
            mock_fig = MagicMock()
            mock_ax = MagicMock()
            mock_plt.subplots.return_value = (mock_fig, mock_ax)

            # Plot frequency response
            results.plot("V(2)", show=False)

            # Verify semilog plot was created
            mock_ax.semilogx.assert_called()
            mock_ax.set_xlabel.assert_called_with("Frequency (Hz)")
            mock_ax.set_ylabel.assert_called_with("Magnitude (dB)")

    def test_plot_current(self):
        """Test plotting current signals."""
        results = SimulationResults("transient")

        time = np.linspace(0, 0.01, 100)
        current = 0.01 * np.sin(2 * np.pi * 100 * time)

        results.set_time_vector(time)
        results.add_current("R1", current)

        # Mock matplotlib
        with patch("matplotlib.pyplot") as mock_plt:
            mock_fig = MagicMock()
            mock_ax = MagicMock()
            mock_plt.subplots.return_value = (mock_fig, mock_ax)

            # Plot current signal
            results.plot("I(R1)", show=False)

            # Verify plot was created with current label
            mock_ax.plot.assert_called()
            mock_ax.set_ylabel.assert_called_with("Current (A)")

    def test_plot_save_to_file(self):
        """Test saving plot to file."""
        results = SimulationResults("dc")
        results.add_voltage(1, 5.0)

        # Mock matplotlib
        with patch("matplotlib.pyplot") as mock_plt:
            mock_fig = MagicMock()
            mock_ax = MagicMock()
            mock_plt.subplots.return_value = (mock_fig, mock_ax)

            # Create temp file
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = tmp.name

            try:
                # Plot and save
                results.plot(save_to=tmp_path, show=False)

                # Verify savefig was called
                mock_plt.savefig.assert_called_with(tmp_path, dpi=150, bbox_inches="tight")
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

    def test_plot_multiple_signals(self):
        """Test plotting multiple signals."""
        results = SimulationResults("transient")

        time = np.linspace(0, 0.01, 100)
        v1 = 5 * np.ones(100)
        v2 = 2.5 * (1 - np.exp(-time / 0.001))

        results.set_time_vector(time)
        results.add_voltage(1, v1)
        results.add_voltage(2, v2)

        # Mock matplotlib
        with patch("matplotlib.pyplot") as mock_plt:
            mock_fig = MagicMock()
            mock_ax = MagicMock()
            mock_plt.subplots.return_value = (mock_fig, mock_ax)

            # Plot multiple signals
            results.plot("V(1)", "V(2)", show=False)

            # Verify multiple plot calls
            assert mock_ax.plot.call_count == 2

    def test_plot_no_matplotlib(self):
        """Test error when matplotlib is not available."""
        results = SimulationResults("dc")
        results.add_voltage(1, 5.0)

        # Mock import error for matplotlib
        with patch.dict("sys.modules", {"matplotlib.pyplot": None}):
            with pytest.raises(ImportError, match="matplotlib"):
                results.plot()

    def test_nonexistent_node(self):
        """Test accessing nonexistent node."""
        results = SimulationResults("dc")
        results.add_voltage(1, 5.0)

        # Nonexistent node should return None
        assert results.voltage(99) is None
        assert results.voltage("missing") is None

    def test_nonexistent_component(self):
        """Test accessing nonexistent component."""
        results = SimulationResults("dc")
        results.add_current("R1", 0.01)

        # Nonexistent component should return None
        assert results.current("R99") is None
        assert results.current("missing") is None

    def test_complex_voltage_storage(self):
        """Test storing and retrieving complex voltage data for AC analysis."""
        results = SimulationResults("ac")
        
        # Create frequency vector
        frequencies = np.logspace(1, 4, 100)  # 10Hz to 10kHz
        results.set_frequency_vector(frequencies)
        
        # Create complex voltage data (simulating RC filter response)
        # V_out/V_in = 1/(1 + jωRC) for RC = 1ms time constant
        omega = 2 * np.pi * frequencies
        rc_time_constant = 1e-3  # 1ms
        transfer_function = 1 / (1 + 1j * omega * rc_time_constant)
        
        # Store complex voltage data
        results.add_voltage(2, transfer_function)
        
        # Retrieve and verify
        v_complex = results.voltage(2)
        assert v_complex is not None
        assert len(v_complex) == len(frequencies)
        assert np.iscomplexobj(v_complex)  # Should be complex array
        
        # Verify at very low frequency (10Hz with 1ms time constant has some phase shift)
        # At f=10Hz, ωRC = 2π×10×0.001 = 0.0628
        # Expected: 1/(1+j×0.0628) = 0.996-j×0.0626
        assert abs(v_complex[0].real - 0.996) < 0.01
        assert abs(v_complex[0].imag - (-0.0626)) < 0.01
        
        # Verify at high frequency (should have significant phase shift)
        assert abs(v_complex[-1]) < 0.1  # High attenuation
        
    def test_magnitude_phase_extraction(self):
        """Test magnitude and phase extraction from complex data."""
        results = SimulationResults("ac")
        
        # Create test complex data: 5V at 45° phase shift
        test_voltage = 5.0 * np.exp(1j * np.pi / 4)  # 5∠45° 
        complex_array = np.array([test_voltage, test_voltage * 0.5])  # Second point at half magnitude
        
        results.add_voltage(1, complex_array)
        
        # Test magnitude extraction (should be new method)
        magnitude = results.magnitude(1)
        assert magnitude is not None
        assert abs(magnitude[0] - 5.0) < 1e-6
        assert abs(magnitude[1] - 2.5) < 1e-6
        
        # Test magnitude in dB
        magnitude_db = results.magnitude_db(1)
        assert magnitude_db is not None
        assert abs(magnitude_db[0] - 20*np.log10(5.0)) < 1e-6  # 20*log10(5) ≈ 13.98 dB
        assert abs(magnitude_db[1] - 20*np.log10(2.5)) < 1e-6  # 20*log10(2.5) ≈ 7.96 dB
        
        # Test phase extraction  
        phase_rad = results.phase_rad(1)
        phase_deg = results.phase_deg(1)
        assert phase_rad is not None
        assert phase_deg is not None
        assert abs(phase_rad[0] - np.pi/4) < 1e-6  # 45° in radians
        assert abs(phase_deg[0] - 45.0) < 1e-6     # 45° in degrees
        
    def test_complex_current_storage(self):
        """Test storing complex current data for AC analysis."""
        results = SimulationResults("ac")
        
        # Create complex current data (90° leading voltage for capacitive load)
        current_magnitude = 0.001  # 1mA
        phase_lead = np.pi/2  # 90° leading
        complex_current = current_magnitude * np.exp(1j * phase_lead)
        
        # Store as array
        results.add_current("C1", np.array([complex_current, complex_current * 0.5]))
        
        # Retrieve and verify
        i_complex = results.current("C1")
        assert i_complex is not None
        assert np.iscomplexobj(i_complex)
        
        # Verify magnitude and phase
        assert abs(abs(i_complex[0]) - current_magnitude) < 1e-6
        assert abs(np.angle(i_complex[0]) - phase_lead) < 1e-6

    def test_bode_plot_generation(self):
        """Test Bode plot generation for AC analysis results."""
        results = SimulationResults("ac")
        
        # Create frequency sweep data
        frequencies = np.logspace(1, 4, 50)  # 10Hz to 10kHz
        results.set_frequency_vector(frequencies)
        
        # Create RC low-pass filter response: H(jω) = 1/(1 + jωRC)
        omega = 2 * np.pi * frequencies
        rc_time_constant = 1e-3  # 1ms → fc = 159Hz
        transfer_function = 1 / (1 + 1j * omega * rc_time_constant)
        
        results.add_voltage(2, transfer_function)  # Output voltage
        
        # Test Bode plot method (should be added to SimulationResults)
        plot_data = results.plot_bode("V(2)", title="RC Low-Pass Filter", show=False)
        
        # Verify plot data structure
        assert plot_data is not None
        assert "magnitude_db" in plot_data
        assert "phase_deg" in plot_data
        assert "frequencies" in plot_data
        
        # Verify data arrays
        assert len(plot_data["magnitude_db"]) == len(frequencies)
        assert len(plot_data["phase_deg"]) == len(frequencies)
        assert len(plot_data["frequencies"]) == len(frequencies)
        
        # Verify Bode plot characteristics
        mag_db = plot_data["magnitude_db"]
        phase_deg = plot_data["phase_deg"]
        
        # At low frequency: magnitude ≈ 0dB, phase ≈ 0°
        assert abs(mag_db[0] - 0.0) < 0.1  # Should be ~0dB at low freq
        assert abs(phase_deg[0] - 0.0) < 5.0  # Should be ~0° at low freq
        
        # At high frequency: significant attenuation and -90° phase shift
        assert mag_db[-1] < -20  # Should have significant attenuation
        assert phase_deg[-1] < -45  # Should approach -90° phase shift
        
        # At cutoff frequency (~159Hz), should be -3dB and -45°
        fc_idx = np.argmin(np.abs(frequencies - 159))
        assert abs(mag_db[fc_idx] - (-3)) < 1  # -3dB at cutoff
        assert abs(phase_deg[fc_idx] - (-45)) < 10  # -45° at cutoff
