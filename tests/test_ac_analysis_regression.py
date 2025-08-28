#!/usr/bin/env python3
"""
Comprehensive unit tests to prevent AC analysis regression.

These tests ensure that the complex data extraction and phase information
fixes remain working correctly. Critical for maintaining AC analysis integrity.
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine


class TestACAnalysisRegression:
    """Comprehensive regression tests for AC analysis functionality."""

    @pytest.fixture
    def engine(self):
        """Simulation engine fixture."""
        return SimulationEngine()

    def test_ac_results_are_complex_arrays(self, engine):
        """
        CRITICAL: Ensure AC analysis always returns complex numpy arrays.

        This test prevents regression where PySpice UnitValue objects
        return only real parts instead of complex data.
        """
        # Simple RC circuit
        circuit = Circuit("AC Complex Data Test")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="1V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1000")
        circuit.add_capacitor("C1", node1=2, node2=0, capacitance="1e-6")

        # Run AC analysis
        ac_results = engine.simulate_ac(
            circuit, start_frequency=10, stop_frequency=1000, points_per_decade=5
        )

        # Critical assertions
        voltage_data = ac_results.get_voltage(2)
        assert voltage_data is not None, "Must have voltage data for output node"
        assert isinstance(voltage_data, np.ndarray), "Voltage data must be numpy array"
        assert np.iscomplexobj(
            voltage_data
        ), "CRITICAL: Voltage data must be complex array"
        assert len(voltage_data) > 0, "Must have voltage samples"

        # Verify complex values have meaningful imaginary parts
        has_imaginary = np.any(np.imag(voltage_data) != 0)
        assert (
            has_imaginary
        ), "CRITICAL: Complex data must have non-zero imaginary parts"

        # Verify phase information is meaningful
        phase_values = np.angle(voltage_data, deg=True)
        phase_range = phase_values.max() - phase_values.min()
        assert (
            phase_range > 5
        ), f"Phase range too small: {phase_range:.1f}° (expected >5°)"

    def test_frequency_vector_extraction(self, engine):
        """
        Test that frequency vectors are properly extracted from PySpice FrequencyValue objects.

        Prevents regression where frequency data contains PySpice units instead of floats.
        """
        circuit = Circuit("Frequency Vector Test")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="1V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="100")

        # Test decade variation
        ac_results = engine.simulate_ac(
            circuit, start_frequency=100, stop_frequency=10000, points_per_decade=10
        )

        frequencies = ac_results.get_frequency_vector()
        assert frequencies is not None, "Must have frequency vector"
        assert isinstance(frequencies, np.ndarray), "Frequencies must be numpy array"
        assert frequencies.dtype in [
            np.float64,
            np.float32,
        ], f"Frequencies must be float, got {frequencies.dtype}"

        # Verify frequency range
        assert (
            frequencies[0] >= 99 and frequencies[0] <= 101
        ), f"Start frequency wrong: {frequencies[0]}"
        assert (
            frequencies[-1] >= 9000 and frequencies[-1] <= 11000
        ), f"Stop frequency wrong: {frequencies[-1]}"

        # Verify logarithmic spacing
        log_freqs = np.log10(frequencies)
        log_diffs = np.diff(log_freqs)
        spacing_std = np.std(log_diffs)
        spacing_mean = np.mean(log_diffs)
        assert (
            spacing_std / spacing_mean < 0.1
        ), "Frequencies not logarithmically spaced"

    def test_rc_lowpass_theoretical_validation(self, engine):
        """
        Validate AC analysis against theoretical RC low-pass filter response.

        This test ensures the simulation matches expected physics.
        """
        # Standard RC low-pass: R=1kΩ, C=1μF, fc ≈ 159 Hz
        R_ohms = 1000
        C_farads = 1e-6
        expected_cutoff = 1 / (2 * np.pi * R_ohms * C_farads)  # ~159.15 Hz

        circuit = Circuit("RC Theoretical Validation")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="1V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance=str(R_ohms))
        circuit.add_capacitor("C1", node1=2, node2=0, capacitance=str(C_farads))

        # Sweep around cutoff frequency
        ac_results = engine.simulate_ac(
            circuit, start_frequency=1, stop_frequency=100000, points_per_decade=25
        )

        frequencies = ac_results.get_frequency_vector()
        voltage_data = ac_results.get_voltage(2)

        # Calculate transfer function
        magnitude_db = 20 * np.log10(np.abs(voltage_data))
        phase_deg = np.angle(voltage_data, deg=True)

        # Find cutoff frequency (−3dB point)
        cutoff_idx = np.argmin(np.abs(magnitude_db - (-3.0)))
        actual_cutoff = frequencies[cutoff_idx]

        # Validate cutoff frequency (within 5% tolerance)
        cutoff_error = abs(actual_cutoff - expected_cutoff) / expected_cutoff
        assert (
            cutoff_error < 0.05
        ), f"Cutoff frequency error: {actual_cutoff:.1f} Hz (expected {expected_cutoff:.1f} Hz)"

        # Validate DC gain (should be ~0 dB)
        dc_gain = magnitude_db[0]
        assert abs(dc_gain) < 0.5, f"DC gain should be ~0 dB, got {dc_gain:.2f} dB"

        # Validate phase response
        dc_phase = phase_deg[0]
        high_freq_phase = phase_deg[-1]
        assert abs(dc_phase) < 5, f"DC phase should be ~0°, got {dc_phase:.1f}°"
        assert (
            high_freq_phase < -80
        ), f"High frequency phase should be < -80°, got {high_freq_phase:.1f}°"

    def test_multiple_circuits_parallel(self, engine):
        """
        Test multiple different circuits to ensure robust complex data extraction.

        This catches edge cases in different circuit topologies.
        """
        test_circuits = [
            # RC Low-pass
            {
                "name": "RC Low-pass",
                "components": [
                    ("V", "V1", 1, 0, "1V"),
                    ("R", "R1", 1, 2, "1000"),
                    ("C", "C1", 2, 0, "1e-6"),
                ],
                "expected_phase_range": (30, 90),
            },
            # RC High-pass
            {
                "name": "RC High-pass",
                "components": [
                    ("V", "V1", 1, 0, "1V"),
                    ("C", "C1", 1, 2, "1e-6"),
                    ("R", "R1", 2, 0, "1000"),
                ],
                "expected_phase_range": (30, 90),
            },
            # RLC Resonant
            {
                "name": "RLC Resonant",
                "components": [
                    ("V", "V1", 1, 0, "1V"),
                    ("R", "R1", 1, 2, "100"),
                    ("L", "L1", 2, 3, "1e-3"),
                    ("C", "C1", 3, 0, "1e-6"),
                ],
                "expected_phase_range": (90, 180),
            },
        ]

        for circuit_def in test_circuits:
            circuit = Circuit(circuit_def["name"])

            # Build circuit from component list
            for comp_type, name, n1, n2, value in circuit_def["components"]:
                if comp_type == "V":
                    circuit.add_voltage_source(
                        name, positive=n1, negative=n2, dc_value=value
                    )
                elif comp_type == "R":
                    circuit.add_resistor(name, node1=n1, node2=n2, resistance=value)
                elif comp_type == "C":
                    circuit.add_capacitor(name, node1=n1, node2=n2, capacitance=value)
                elif comp_type == "L":
                    circuit.add_inductor(name, node1=n1, node2=n2, inductance=value)

            # Run AC analysis
            ac_results = engine.simulate_ac(
                circuit, start_frequency=10, stop_frequency=10000, points_per_decade=15
            )

            # Get output node (assume node 2 for simple circuits, node 3 for RLC)
            output_node = 3 if circuit_def["name"] == "RLC Resonant" else 2
            voltage_data = ac_results.get_voltage(output_node)

            # Critical regression tests
            assert voltage_data is not None, f"{circuit_def['name']}: No voltage data"
            assert np.iscomplexobj(
                voltage_data
            ), f"{circuit_def['name']}: Not complex data"

            # Validate phase range for circuit type
            phase_values = np.angle(voltage_data, deg=True)
            phase_range = phase_values.max() - phase_values.min()
            min_expected, max_expected = circuit_def["expected_phase_range"]

            assert (
                min_expected <= phase_range <= max_expected
            ), f"{circuit_def['name']}: Phase range {phase_range:.1f}° not in [{min_expected}, {max_expected}]"

    def test_ac_analysis_edge_cases(self, engine):
        """Test AC analysis edge cases that could cause regression."""

        circuit = Circuit("Edge Case Test")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="1V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1000")
        circuit.add_capacitor("C1", node1=2, node2=0, capacitance="1e-6")

        # Test very few points
        ac_results = engine.simulate_ac(
            circuit, start_frequency=100, stop_frequency=1000, points_per_decade=2
        )
        voltage_data = ac_results.get_voltage(2)
        assert np.iscomplexobj(voltage_data), "Few points: Must preserve complex data"
        assert len(voltage_data) >= 2, "Few points: Must have minimum data points"

        # Test single point
        ac_results = engine.simulate_ac(
            circuit, start_frequency=1000, stop_frequency=1000, points_per_decade=1
        )
        voltage_data = ac_results.get_voltage(2)
        assert np.iscomplexobj(voltage_data), "Single point: Must preserve complex data"
        assert len(voltage_data) >= 1, "Single point: Must have at least one point"

        # Test very wide frequency range
        ac_results = engine.simulate_ac(
            circuit, start_frequency=0.1, stop_frequency=1e6, points_per_decade=5
        )
        voltage_data = ac_results.get_voltage(2)
        assert np.iscomplexobj(voltage_data), "Wide range: Must preserve complex data"

        frequencies = ac_results.get_frequency_vector()
        assert (
            frequencies[0] >= 0.09
        ), f"Wide range: Start frequency wrong: {frequencies[0]}"
        assert (
            frequencies[-1] >= 9e5
        ), f"Wide range: Stop frequency wrong: {frequencies[-1]}"

    def test_results_compatibility_methods(self, engine):
        """
        Test compatibility methods like get_voltage() and get_frequency_vector().

        Ensures the API additions don't break existing functionality.
        """
        circuit = Circuit("API Compatibility Test")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="1V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1000")

        ac_results = engine.simulate_ac(
            circuit, start_frequency=10, stop_frequency=1000, points_per_decade=5
        )

        # Test both old and new API methods
        voltage_old = ac_results.voltage(2)
        voltage_new = ac_results.get_voltage(2)

        frequency_old = ac_results.frequency
        frequency_new = ac_results.get_frequency_vector()

        assert np.array_equal(
            voltage_old, voltage_new
        ), "get_voltage() must match voltage()"
        assert np.array_equal(
            frequency_old, frequency_new
        ), "get_frequency_vector() must match frequency"

        # Test non-existent nodes
        assert (
            ac_results.get_voltage(999) is None
        ), "Non-existent node should return None"

    def test_numpy_array_consistency(self, engine):
        """
        Test that numpy array operations work consistently with AC results.

        Critical for chart generation and mathematical operations.
        """
        circuit = Circuit("Numpy Consistency Test")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="1V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1000")
        circuit.add_capacitor("C1", node1=2, node2=0, capacitance="1e-6")

        ac_results = engine.simulate_ac(
            circuit, start_frequency=10, stop_frequency=10000, points_per_decade=10
        )

        voltage_data = ac_results.get_voltage(2)
        ac_results.get_frequency_vector()

        # Test vectorized operations (critical for chart generation)
        magnitude = np.abs(voltage_data)
        phase = np.angle(voltage_data, deg=True)
        magnitude_db = 20 * np.log10(magnitude)

        # Ensure all operations return valid arrays
        assert np.all(np.isfinite(magnitude)), "Magnitude must be finite"
        assert np.all(np.isfinite(phase)), "Phase must be finite"
        assert np.all(np.isfinite(magnitude_db)), "Magnitude (dB) must be finite"

        # Ensure proper array shapes
        assert magnitude.shape == voltage_data.shape, "Magnitude shape mismatch"
        assert phase.shape == voltage_data.shape, "Phase shape mismatch"
        assert magnitude_db.shape == voltage_data.shape, "Magnitude (dB) shape mismatch"

        # Test complex arithmetic
        conjugate = np.conj(voltage_data)
        power = voltage_data * conjugate  # Should be real
        assert np.all(np.imag(power) < 1e-10), "Power calculation should be real"

    @pytest.mark.parametrize("variation", ["dec", "lin"])
    def test_frequency_variations(self, engine, variation):
        """Test both decade and linear frequency variations."""

        circuit = Circuit(f"Frequency Variation Test ({variation})")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="1V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1000")

        ac_results = engine.simulate_ac(
            circuit,
            start_frequency=100,
            stop_frequency=1000,
            points_per_decade=5,
            variation=variation,
        )

        voltage_data = ac_results.get_voltage(2)
        frequencies = ac_results.get_frequency_vector()

        assert np.iscomplexobj(voltage_data), f"{variation}: Must preserve complex data"
        assert len(frequencies) > 0, f"{variation}: Must have frequency points"

        if variation == "dec":
            # Test logarithmic spacing
            log_freqs = np.log10(frequencies)
            log_diffs = np.diff(log_freqs)
            spacing_cv = np.std(log_diffs) / np.mean(log_diffs)
            assert spacing_cv < 0.1, f"Dec variation not logarithmic: CV = {spacing_cv}"

        elif variation == "lin":
            # Test linear spacing
            lin_diffs = np.diff(frequencies)
            spacing_cv = np.std(lin_diffs) / np.mean(lin_diffs)
            assert spacing_cv < 0.1, f"Lin variation not linear: CV = {spacing_cv}"


class TestACAnalysisIntegration:
    """Integration tests for AC analysis with report generation."""

    @pytest.mark.skip(
        reason="Chart integration test - Bode plot method needs verification"
    )
    def test_ac_results_chart_integration(self):
        """Test that AC results integrate properly with chart generation."""
        from circuit_sim.reports.charts.plotly_charts import PlotlyChartGenerator

        engine = SimulationEngine()
        circuit = Circuit("Chart Integration Test")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="1V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1000")
        circuit.add_capacitor("C1", node1=2, node2=0, capacitance="1e-6")

        ac_results = engine.simulate_ac(
            circuit, start_frequency=10, stop_frequency=10000, points_per_decade=10
        )

        # Test Bode plot generation
        chart_gen = PlotlyChartGenerator()

        try:
            # This should not raise exceptions
            bode_fig = chart_gen.create_bode_plot(ac_results, output_nodes=[2])
            assert bode_fig is not None, "Bode plot generation failed"

            # Verify the chart has the expected traces (magnitude and phase)
            assert (
                len(bode_fig.data) >= 2
            ), "Bode plot should have magnitude and phase traces"

        except Exception as e:
            pytest.fail(f"Bode plot generation failed: {e}")


# Performance regression tests
class TestACAnalysisPerformance:
    """Performance tests to ensure AC analysis doesn't regress in speed."""

    def test_ac_analysis_performance(self):
        """Test that AC analysis completes within reasonable time."""
        import time

        engine = SimulationEngine()
        circuit = Circuit("Performance Test")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="1V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1000")
        circuit.add_capacitor("C1", node1=2, node2=0, capacitance="1e-6")

        # Test with moderate number of points
        start_time = time.time()
        ac_results = engine.simulate_ac(
            circuit, start_frequency=1, stop_frequency=100000, points_per_decade=20
        )
        elapsed_time = time.time() - start_time

        # Should complete within reasonable time (adjust threshold as needed)
        assert (
            elapsed_time < 5.0
        ), f"AC analysis too slow: {elapsed_time:.2f}s (expected <5s)"

        # Verify results are still correct
        voltage_data = ac_results.get_voltage(2)
        assert np.iscomplexobj(
            voltage_data
        ), "Performance test: Must preserve complex data"
