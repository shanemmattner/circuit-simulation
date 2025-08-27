"""Tests for RC filter example circuit."""

import numpy as np

from examples.basic.rc_filter import (
    RCFilterCircuit,
    calculate_frequency_response,
    generate_bode_plot,
    simulate_rc_filter,
)


class TestRCFilterCircuit:
    """Test RC filter circuit implementation."""

    def test_lowpass_filter_creation(self):
        """Test creating a low-pass RC filter."""
        circuit = RCFilterCircuit(r=1000, c=1e-6, filter_type="lowpass", vin=1.0)  # 1kΩ  # 1µF

        assert circuit.r == 1000
        assert circuit.c == 1e-6
        assert circuit.filter_type == "lowpass"
        assert circuit.vin == 1.0

        # Check cutoff frequency calculation
        expected_fc = 1 / (2 * np.pi * 1000 * 1e-6)  # ~159.15 Hz
        assert abs(circuit.cutoff_frequency - expected_fc) < 0.01

    def test_highpass_filter_creation(self):
        """Test creating a high-pass RC filter."""
        circuit = RCFilterCircuit(r=10000, c=100e-9, filter_type="highpass")  # 10kΩ  # 100nF

        assert circuit.filter_type == "highpass"

        # Check cutoff frequency
        expected_fc = 1 / (2 * np.pi * 10000 * 100e-9)  # ~159.15 Hz
        assert abs(circuit.cutoff_frequency - expected_fc) < 0.01

    def test_time_constant(self):
        """Test time constant calculation."""
        circuit = RCFilterCircuit(r=1000, c=1e-6)

        expected_tau = 1000 * 1e-6  # 1ms
        assert circuit.time_constant == expected_tau

    def test_netlist_generation_lowpass(self):
        """Test SPICE netlist generation for lowpass filter."""
        circuit = RCFilterCircuit(r=1000, c=1e-6, filter_type="lowpass")
        netlist = circuit.generate_netlist()

        assert "RC Low-Pass Filter" in netlist
        assert "R1" in netlist
        assert "C1" in netlist
        assert ".ac" in netlist.lower()  # AC analysis

    def test_netlist_generation_highpass(self):
        """Test SPICE netlist generation for highpass filter."""
        circuit = RCFilterCircuit(r=1000, c=1e-6, filter_type="highpass")
        netlist = circuit.generate_netlist()

        assert "RC High-Pass Filter" in netlist
        # Component order is different for highpass
        assert "C1" in netlist
        assert "R1" in netlist


class TestRCFilterSimulation:
    """Test RC filter simulation functionality."""

    def test_step_response(self):
        """Test transient step response simulation."""
        circuit = RCFilterCircuit(r=1000, c=1e-6, filter_type="lowpass")

        results = simulate_rc_filter(
            circuit, analysis_type="transient", duration=5e-3, timestep=1e-5  # 5 time constants
        )

        assert "time" in results
        assert "output" in results
        assert "input" in results

        # At t = tau, output should be ~63.2% of input for lowpass
        tau_index = int(circuit.time_constant / 1e-5)
        expected_voltage = circuit.vin * 0.632
        assert abs(results["output"][tau_index] - expected_voltage) < 0.1

    def test_frequency_response(self):
        """Test AC frequency response simulation."""
        circuit = RCFilterCircuit(r=1000, c=1e-6, filter_type="lowpass")

        results = simulate_rc_filter(
            circuit, analysis_type="ac", start_freq=1, stop_freq=100000, points_per_decade=20
        )

        assert "frequency" in results
        assert "magnitude_db" in results
        assert "phase_deg" in results

        # At cutoff frequency, magnitude should be -3dB
        fc = circuit.cutoff_frequency
        fc_index = np.argmin(np.abs(np.array(results["frequency"]) - fc))
        assert abs(results["magnitude_db"][fc_index] - (-3.0)) < 0.5

    def test_calculate_frequency_response(self):
        """Test analytical frequency response calculation."""
        circuit = RCFilterCircuit(r=1000, c=1e-6, filter_type="lowpass")

        frequencies = np.logspace(0, 5, 100)  # 1Hz to 100kHz
        response = calculate_frequency_response(circuit, frequencies)

        assert "frequency" in response
        assert "magnitude" in response
        assert "phase" in response
        assert "magnitude_db" in response

        # Verify DC response (lowpass should pass DC)
        assert abs(response["magnitude"][0] - 1.0) < 0.01

        # Verify high frequency attenuation
        assert response["magnitude"][-1] < 0.01

    def test_highpass_frequency_response(self):
        """Test highpass filter frequency response."""
        circuit = RCFilterCircuit(r=1000, c=1e-6, filter_type="highpass")

        frequencies = np.logspace(0, 5, 100)
        response = calculate_frequency_response(circuit, frequencies)

        # Highpass blocks DC
        assert response["magnitude"][0] < 0.01

        # Highpass passes high frequencies
        assert abs(response["magnitude"][-1] - 1.0) < 0.01

    def test_phase_response(self):
        """Test phase response calculation."""
        circuit = RCFilterCircuit(r=1000, c=1e-6, filter_type="lowpass")

        # At cutoff frequency, phase should be -45 degrees for lowpass
        fc = circuit.cutoff_frequency
        response = calculate_frequency_response(circuit, [fc])

        assert abs(response["phase"][0] - (-45)) < 1.0


class TestRCFilterAnalysis:
    """Test RC filter analysis functions."""

    def test_filter_characterization(self):
        """Test filter characterization metrics."""
        circuit = RCFilterCircuit(r=1000, c=1e-6)

        char = circuit.characterize_filter()

        assert "cutoff_frequency" in char
        assert "time_constant" in char
        assert "attenuation_per_decade" in char
        assert "attenuation_per_octave" in char

        # First-order filter has -20dB/decade rolloff
        assert char["attenuation_per_decade"] == -20
        assert char["attenuation_per_octave"] == -6

    def test_group_delay(self):
        """Test group delay calculation."""
        circuit = RCFilterCircuit(r=1000, c=1e-6)

        frequencies = [100, 1000, 10000]
        delays = circuit.calculate_group_delay(frequencies)

        assert len(delays) == len(frequencies)
        # Group delay should be maximum at low frequencies for lowpass
        assert delays[0] > delays[-1]


class TestBodePlot:
    """Test Bode plot generation."""

    def test_bode_plot_generation(self):
        """Test generating Bode plot."""
        circuit = RCFilterCircuit(r=1000, c=1e-6)

        frequencies = np.logspace(0, 5, 100)
        response = calculate_frequency_response(circuit, frequencies)

        fig = generate_bode_plot(circuit, response)

        assert fig is not None
        assert len(fig.data) >= 2  # Magnitude and phase traces
        assert "Bode Plot" in fig.layout.title.text

    def test_bode_plot_with_markers(self):
        """Test Bode plot with cutoff frequency marker."""
        circuit = RCFilterCircuit(r=1000, c=1e-6)

        frequencies = np.logspace(0, 5, 100)
        response = calculate_frequency_response(circuit, frequencies)

        fig = generate_bode_plot(circuit, response, show_cutoff=True, show_phase=True)

        # Check for cutoff frequency annotation
        assert any("cutoff" in str(annotation).lower() for annotation in fig.layout.annotations)


class TestRCFilterComparison:
    """Test comparing different RC filter configurations."""

    def test_filter_comparison(self):
        """Test comparing multiple filter configurations."""
        filters = [
            RCFilterCircuit(r=1000, c=1e-6, filter_type="lowpass"),
            RCFilterCircuit(r=10000, c=100e-9, filter_type="lowpass"),
            RCFilterCircuit(r=1000, c=1e-6, filter_type="highpass"),
        ]

        # All should have valid cutoff frequencies
        for f in filters:
            assert f.cutoff_frequency > 0

        # Different R and C with same product should have same fc
        assert abs(filters[0].cutoff_frequency - filters[1].cutoff_frequency) < 1.0

    def test_cascade_filters(self):
        """Test cascading multiple RC stages."""
        circuit = RCFilterCircuit(r=1000, c=1e-6)

        # Cascading n identical stages
        n_stages = 2
        cascade_response = circuit.calculate_cascade_response(n_stages, 1000)

        # Magnitude should be (single_stage)^n
        single_response = calculate_frequency_response(circuit, [1000])
        expected_mag = single_response["magnitude"][0] ** n_stages

        assert abs(cascade_response["magnitude"] - expected_mag) < 0.01
