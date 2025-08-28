"""
Specialized AC Analysis Behavior Tests

These tests specifically target the AC analysis issues discovered:
1. PySpice returning real-only values instead of complex
2. Missing phase information in frequency response
3. Chart generation issues with AC data

This module works with the visual testing framework to provide
comprehensive validation of AC analysis functionality.
"""

import pytest
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine
from visual_testing_framework import (
    VisualTestFramework,
    CircuitBehaviorValidator,
)


class TestACAnalysisBehavior:
    """Test suite specifically for AC analysis behavior validation."""

    @pytest.fixture
    def engine(self):
        """Simulation engine fixture."""
        return SimulationEngine()

    @pytest.fixture
    def visual_framework(self):
        """Visual testing framework fixture."""
        return VisualTestFramework("tests/test_output/ac_behavior")

    @pytest.fixture
    def behavior_validator(self):
        """Behavior validator fixture."""
        return CircuitBehaviorValidator()

    @pytest.fixture
    def rc_lowpass_circuit(self):
        """RC low-pass filter circuit fixture."""
        circuit = Circuit("RC Low-pass Test")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="1V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1000")  # 1kΩ
        circuit.add_capacitor("C1", node1=2, node2=0, capacitance="1e-6")  # 1μF
        return circuit

    @pytest.fixture
    def rc_highpass_circuit(self):
        """RC high-pass filter circuit fixture."""
        circuit = Circuit("RC High-pass Test")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="1V")
        circuit.add_capacitor("C1", node1=1, node2=2, capacitance="1e-6")  # 1μF
        circuit.add_resistor("R1", node1=2, node2=0, resistance="1000")  # 1kΩ
        return circuit

    @pytest.fixture
    def rlc_bandpass_circuit(self):
        """RLC band-pass filter circuit fixture."""
        circuit = Circuit("RLC Band-pass Test")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="1V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="100")  # 100Ω
        circuit.add_inductor("L1", node1=2, node2=3, inductance="1e-3")  # 1mH
        circuit.add_capacitor("C1", node1=3, node2=0, capacitance="1e-6")  # 1μF
        return circuit

    def test_ac_analysis_returns_complex_values(
        self, engine, rc_lowpass_circuit, behavior_validator
    ):
        """Test that AC analysis returns proper complex values with phase information."""

        # Run AC analysis
        ac_results = engine.simulate_ac(
            rc_lowpass_circuit,
            start_frequency=1,
            stop_frequency=100000,
            points_per_decade=10,
        )

        # Validate complex values
        result = behavior_validator.validate_ac_complex_values(ac_results, node_id=2)

        # Test should pass - we should have complex values
        assert (
            result.passed
        ), f"AC analysis complex value validation failed: {result.issues}"
        assert (
            result.score >= 0.8
        ), f"AC analysis complex value score too low: {result.score}"

        # Verify we have actual complex data
        voltage_data = ac_results.get_voltage(2)
        assert voltage_data is not None, "No voltage data for output node"
        assert np.iscomplexobj(
            voltage_data
        ), "Voltage data should be complex numpy array"

        # Check that we have meaningful phase information
        phase_values = np.angle(voltage_data, deg=True)
        phase_range = phase_values.max() - phase_values.min()
        assert (
            phase_range > 30
        ), f"Phase range too small ({phase_range:.1f}°) - should show significant phase shift"

        # For RC low-pass, phase should be between 0° and -90°
        assert np.all(
            phase_values <= 5
        ), f"Some phase values too positive: max={phase_values.max():.1f}°"
        assert np.all(
            phase_values >= -95
        ), f"Some phase values too negative: min={phase_values.min():.1f}°"

    def test_rc_lowpass_behavior_validation(
        self, engine, rc_lowpass_circuit, behavior_validator
    ):
        """Test RC low-pass filter behavior against theoretical expectations."""

        # Circuit parameters
        R_ohms = 1000
        C_farads = 1e-6

        # Run AC analysis
        ac_results = engine.simulate_ac(
            rc_lowpass_circuit,
            start_frequency=0.1,
            stop_frequency=100000,
            points_per_decade=20,
        )

        # Validate behavior
        result = behavior_validator.validate_rc_lowpass_behavior(
            rc_lowpass_circuit, ac_results, R_ohms, C_farads
        )

        # Assertions for test framework
        assert result.passed, f"RC low-pass behavior validation failed: {result.issues}"
        assert (
            result.score >= 0.7
        ), f"RC low-pass behavior score too low: {result.score}"

        # Check specific physics expectations
        metadata = result.metadata.get("physics_analysis", {})

        # Cutoff frequency should be approximately 159 Hz for 1kΩ, 1μF
        expected_cutoff = 1 / (2 * np.pi * R_ohms * C_farads)  # ~159.15 Hz
        actual_cutoff = metadata.get("cutoff_frequency_hz", 0)
        assert (
            abs(actual_cutoff - expected_cutoff) / expected_cutoff < 0.1
        ), f"Cutoff frequency error too large: {actual_cutoff:.1f} Hz (expected {expected_cutoff:.1f} Hz)"

        # DC gain should be near 0 dB
        dc_gain = metadata.get("dc_gain_db", -999)
        assert abs(dc_gain) < 1.0, f"DC gain should be ~0 dB, got {dc_gain:.2f} dB"

        # Cutoff gain should be near -3 dB
        cutoff_gain = metadata.get("cutoff_gain_db", -999)
        assert (
            abs(cutoff_gain - (-3.0)) < 1.0
        ), f"Cutoff gain should be ~-3 dB, got {cutoff_gain:.2f} dB"

    def test_rc_highpass_phase_response(
        self, engine, rc_highpass_circuit, behavior_validator
    ):
        """Test RC high-pass filter has correct phase response (0° to +90°)."""

        # Run AC analysis
        ac_results = engine.simulate_ac(
            rc_highpass_circuit,
            start_frequency=1,
            stop_frequency=100000,
            points_per_decade=15,
        )

        # Verify complex values first
        complex_result = behavior_validator.validate_ac_complex_values(
            ac_results, node_id=2
        )
        assert complex_result.passed, "High-pass filter should return complex AC values"

        # Get voltage data and check phase characteristics
        voltage_data = ac_results.get_voltage(2)
        phase_values = np.angle(voltage_data, deg=True)

        # High-pass filter phase should go from +90° to 0°
        # At low frequencies: approaching +90°
        # At high frequencies: approaching 0°
        frequencies = ac_results.get_frequency_vector()

        low_freq_indices = frequencies < 100  # Low frequency range
        high_freq_indices = frequencies > 10000  # High frequency range

        if np.any(low_freq_indices):
            low_freq_phase = np.mean(phase_values[low_freq_indices])
            assert (
                low_freq_phase > 45
            ), f"Low frequency phase should be >45°, got {low_freq_phase:.1f}°"

        if np.any(high_freq_indices):
            high_freq_phase = np.mean(phase_values[high_freq_indices])
            assert (
                abs(high_freq_phase) < 15
            ), f"High frequency phase should be ~0°, got {high_freq_phase:.1f}°"

    def test_rlc_bandpass_resonance_behavior(
        self, engine, rlc_bandpass_circuit, behavior_validator
    ):
        """Test RLC band-pass filter shows proper resonance characteristics."""

        # Circuit parameters
        L_henrys = 1e-3  # 1mH
        C_farads = 1e-6  # 1μF

        # Calculate expected resonance frequency
        f_resonance = 1 / (2 * np.pi * np.sqrt(L_henrys * C_farads))  # ~5033 Hz

        # Run AC analysis centered around resonance
        ac_results = engine.simulate_ac(
            rlc_bandpass_circuit,
            start_frequency=100,
            stop_frequency=50000,
            points_per_decade=25,
        )

        # Verify complex values
        complex_result = behavior_validator.validate_ac_complex_values(
            ac_results, node_id=3
        )
        assert complex_result.passed, "RLC band-pass should return complex AC values"

        # Analyze resonance characteristics
        frequencies = ac_results.get_frequency_vector()
        voltage_data = ac_results.get_voltage(3)
        magnitude_db = 20 * np.log10(np.abs(voltage_data))

        # Find peak magnitude (should be at resonance)
        peak_idx = np.argmax(magnitude_db)
        peak_frequency = frequencies[peak_idx]
        peak_magnitude = magnitude_db[peak_idx]

        # Verify resonance frequency is close to theoretical
        freq_error = abs(peak_frequency - f_resonance) / f_resonance
        assert (
            freq_error < 0.1
        ), f"Resonance frequency error: {peak_frequency:.1f} Hz (expected {f_resonance:.1f} Hz)"

        # At resonance, phase should be approximately 0°
        phase_at_resonance = np.angle(voltage_data[peak_idx], deg=True)
        assert (
            abs(phase_at_resonance) < 10
        ), f"Phase at resonance should be ~0°, got {phase_at_resonance:.1f}°"

        # Check that magnitude actually peaks (band-pass behavior)
        # Compare peak to frequencies decade below and above
        lower_decade_idx = np.argmin(np.abs(frequencies - (f_resonance / 10)))
        upper_decade_idx = np.argmin(np.abs(frequencies - (f_resonance * 10)))

        peak_vs_lower = peak_magnitude - magnitude_db[lower_decade_idx]
        peak_vs_upper = peak_magnitude - magnitude_db[upper_decade_idx]

        assert (
            peak_vs_lower > 10
        ), f"Insufficient low-frequency attenuation: {peak_vs_lower:.1f} dB"
        assert (
            peak_vs_upper > 10
        ), f"Insufficient high-frequency attenuation: {peak_vs_upper:.1f} dB"

    def test_frequency_vector_generation(self, engine, rc_lowpass_circuit):
        """Test that frequency vectors are generated correctly for AC analysis."""

        # Test logarithmic (decade) variation
        ac_results_log = engine.simulate_ac(
            rc_lowpass_circuit,
            start_frequency=10,
            stop_frequency=10000,
            points_per_decade=10,
            variation="dec",
        )

        frequencies_log = ac_results_log.get_frequency_vector()
        assert (
            frequencies_log is not None
        ), "Should have frequency vector for decade variation"

        # Check that frequencies are logarithmically spaced
        log_freqs = np.log10(frequencies_log)
        log_diffs = np.diff(log_freqs)

        # Differences should be approximately constant for logarithmic spacing
        log_diff_std = np.std(log_diffs)
        log_diff_mean = np.mean(log_diffs)

        assert (
            log_diff_std / log_diff_mean < 0.1
        ), "Frequencies not properly logarithmically spaced"

        # Check frequency range
        assert (
            frequencies_log[0] >= 9 and frequencies_log[0] <= 11
        ), f"Start frequency incorrect: {frequencies_log[0]}"
        assert (
            frequencies_log[-1] >= 9000 and frequencies_log[-1] <= 11000
        ), f"Stop frequency incorrect: {frequencies_log[-1]}"

        # Test linear variation
        ac_results_lin = engine.simulate_ac(
            rc_lowpass_circuit,
            start_frequency=100,
            stop_frequency=1000,
            variation="lin",
        )

        frequencies_lin = ac_results_lin.get_frequency_vector()
        assert (
            frequencies_lin is not None
        ), "Should have frequency vector for linear variation"

        # Check that frequencies are linearly spaced
        lin_diffs = np.diff(frequencies_lin)
        lin_diff_std = np.std(lin_diffs)
        lin_diff_mean = np.mean(lin_diffs)

        assert (
            lin_diff_std / lin_diff_mean < 0.1
        ), "Frequencies not properly linearly spaced"

    @pytest.mark.parametrize(
        "R_ohms,C_farads,expected_cutoff",
        [
            (1000, 1e-6, 159.15),  # Standard RC
            (2200, 470e-9, 153.9),  # Common values
            (10000, 100e-9, 159.15),  # High R, low C
        ],
    )
    def test_rc_filter_parameter_sweep(
        self, engine, behavior_validator, R_ohms, C_farads, expected_cutoff
    ):
        """Test RC filters with different component values."""

        # Create circuit with specific values
        circuit = Circuit(f"RC Filter R={R_ohms}Ω C={C_farads*1e6:.0f}μF")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="1V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance=str(R_ohms))
        circuit.add_capacitor("C1", node1=2, node2=0, capacitance=str(C_farads))

        # Run analysis
        ac_results = engine.simulate_ac(
            circuit, start_frequency=1, stop_frequency=100000, points_per_decade=20
        )

        # Validate behavior
        result = behavior_validator.validate_rc_lowpass_behavior(
            circuit, ac_results, R_ohms, C_farads
        )

        assert (
            result.passed
        ), f"Parameter sweep failed for R={R_ohms}Ω, C={C_farads*1e6:.0f}μF: {result.issues}"

        # Check cutoff frequency accuracy
        actual_cutoff = result.metadata["physics_analysis"]["cutoff_frequency_hz"]
        cutoff_error = abs(actual_cutoff - expected_cutoff) / expected_cutoff
        assert (
            cutoff_error < 0.05
        ), f"Cutoff frequency error: {actual_cutoff:.1f} Hz (expected {expected_cutoff:.1f} Hz)"

    def test_ac_analysis_edge_cases(self, engine, rc_lowpass_circuit):
        """Test AC analysis edge cases and error conditions."""

        # Test very low frequency start
        try:
            ac_results = engine.simulate_ac(
                rc_lowpass_circuit,
                start_frequency=0.001,  # 1 mHz
                stop_frequency=1000,
                points_per_decade=5,
            )

            frequencies = ac_results.get_frequency_vector()
            assert frequencies[0] >= 0.0009, "Very low start frequency should work"

        except Exception as e:
            pytest.fail(f"Very low start frequency should not fail: {e}")

        # Test very high frequency end
        try:
            ac_results = engine.simulate_ac(
                rc_lowpass_circuit,
                start_frequency=1000,
                stop_frequency=1e9,  # 1 GHz
                points_per_decade=5,
            )

            frequencies = ac_results.get_frequency_vector()
            assert frequencies[-1] >= 9e8, "Very high stop frequency should work"

        except Exception as e:
            pytest.fail(f"Very high stop frequency should not fail: {e}")

        # Test single point analysis
        ac_results = engine.simulate_ac(
            rc_lowpass_circuit,
            start_frequency=1000,
            stop_frequency=1000,
            points_per_decade=1,
        )

        frequencies = ac_results.get_frequency_vector()
        assert len(frequencies) >= 1, "Single point analysis should work"

        voltage_data = ac_results.get_voltage(2)
        assert voltage_data is not None, "Single point should return voltage data"
        assert np.iscomplexobj(voltage_data), "Single point should return complex data"


class TestACAnalysisRegression:
    """Regression tests for previously found AC analysis bugs."""

    def test_pyspice_ac_source_configuration_bug(self):
        """Test that PySpice AC sources are configured correctly to return complex values."""

        try:
            from PySpice.Spice.Netlist import Circuit as PySpiceCircuit
            from PySpice.Unit import u_V, u_Ohm, u_F

            # Create circuit directly with PySpice to test configuration
            circuit = PySpiceCircuit("AC Source Test")

            # Test the specific configuration we use in our builder
            circuit.V("input", "input", circuit.gnd, "DC 0 AC 1")
            circuit.R(1, "input", "output", 1000 @ u_Ohm)
            circuit.C(1, "output", circuit.gnd, 1e-6 @ u_F)

            # Create simulator and run AC analysis
            simulator = circuit.simulator(temperature=25, nominal_temperature=25)
            analysis = simulator.ac(
                start_frequency=100,
                stop_frequency=10000,
                number_of_points=20,
                variation="dec",
            )

            # Verify we get complex values
            for node_name, voltage_data in analysis.nodes.items():
                if "output" in node_name:
                    voltage_array = np.array(list(voltage_data))

                    # This should be complex
                    assert np.iscomplexobj(
                        voltage_array
                    ), f"Node {node_name} should return complex values"

                    # Should have meaningful phase information
                    phase_values = np.angle(voltage_array, deg=True)
                    phase_range = phase_values.max() - phase_values.min()
                    assert (
                        phase_range > 30
                    ), f"Node {node_name} phase range too small: {phase_range:.1f}°"

                    # Magnitude should be reasonable
                    magnitude = np.abs(voltage_array)
                    assert np.all(
                        magnitude > 0
                    ), f"Node {node_name} should have non-zero magnitude"
                    assert np.all(
                        magnitude <= 1.1
                    ), f"Node {node_name} magnitude seems too high (input is 1V)"

                    break
            else:
                pytest.fail("No 'output' node found in analysis results")

        except ImportError:
            pytest.skip("PySpice not available for direct testing")

    def test_chart_generation_with_complex_data(self, rc_lowpass_circuit):
        """Test that chart generation works properly with complex AC data."""

        engine = SimulationEngine()

        # Get AC results
        ac_results = engine.simulate_ac(
            rc_lowpass_circuit,
            start_frequency=10,
            stop_frequency=10000,
            points_per_decade=10,
        )

        # Test data extraction for charting
        frequencies = ac_results.get_frequency_vector()
        voltage_data = ac_results.get_voltage(2)

        assert frequencies is not None, "Should have frequency vector for charting"
        assert voltage_data is not None, "Should have voltage data for charting"
        assert np.iscomplexobj(
            voltage_data
        ), "Voltage data should be complex for proper Bode plots"

        # Test magnitude and phase extraction (what charts need)
        magnitude_db = 20 * np.log10(np.abs(voltage_data))
        phase_deg = np.angle(voltage_data, deg=True)

        assert np.all(
            np.isfinite(magnitude_db)
        ), "Magnitude should be finite for charting"
        assert np.all(np.isfinite(phase_deg)), "Phase should be finite for charting"

        # Phase should show meaningful variation for RC filter
        phase_range = phase_deg.max() - phase_deg.min()
        assert (
            phase_range > 30
        ), f"Phase range too small for meaningful Bode plot: {phase_range:.1f}°"

        # Magnitude should decrease with frequency (low-pass behavior)
        # Check that high frequency magnitude is less than low frequency
        low_freq_mag = magnitude_db[0]
        high_freq_mag = magnitude_db[-1]
        assert (
            high_freq_mag < low_freq_mag
        ), "Low-pass filter should attenuate high frequencies"
