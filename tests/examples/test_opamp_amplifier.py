"""Tests for op-amp amplifier example circuits."""

import numpy as np

from examples.amplifiers.opamp import (
    OpAmpCircuit,
    analyze_amplifier,
    calculate_gain_bandwidth,
    generate_amplifier_report,
    simulate_opamp,
)


class TestOpAmpCircuit:
    """Test op-amp circuit implementation."""

    def test_inverting_amplifier_creation(self):
        """Test creating an inverting amplifier."""
        circuit = OpAmpCircuit(
            config="inverting",
            r_in=10000,  # 10kΩ input
            r_feedback=100000,  # 100kΩ feedback
            model="LM358",
        )

        assert circuit.config == "inverting"
        assert circuit.r_in == 10000
        assert circuit.r_feedback == 100000
        assert circuit.model == "LM358"

        # Check gain calculation
        expected_gain = -100000 / 10000  # -10
        assert abs(circuit.calculate_ideal_gain() - expected_gain) < 0.01

    def test_non_inverting_amplifier_creation(self):
        """Test creating a non-inverting amplifier."""
        circuit = OpAmpCircuit(config="non_inverting", r_in=10000, r_feedback=90000, model="TL072")

        assert circuit.config == "non_inverting"

        # Non-inverting gain = 1 + Rf/Rin
        expected_gain = 1 + 90000 / 10000  # 10
        assert abs(circuit.calculate_ideal_gain() - expected_gain) < 0.01

    def test_differential_amplifier(self):
        """Test differential amplifier configuration."""
        circuit = OpAmpCircuit(
            config="differential",
            r_in=10000,
            r_feedback=10000,
            r_in2=10000,
            r_ground=10000,
            model="LF351",
        )

        assert circuit.config == "differential"

        # For equal resistors, differential gain = 1
        expected_gain = 1.0
        assert abs(circuit.calculate_ideal_gain() - expected_gain) < 0.01

    def test_buffer_configuration(self):
        """Test unity gain buffer (voltage follower)."""
        circuit = OpAmpCircuit(config="buffer", model="LM358")

        assert circuit.config == "buffer"
        assert circuit.calculate_ideal_gain() == 1.0

    def test_integrator_configuration(self):
        """Test integrator circuit."""
        circuit = OpAmpCircuit(
            config="integrator", r_in=10000, c_feedback=1e-6, model="TL072"  # 1µF
        )

        assert circuit.config == "integrator"
        assert circuit.c_feedback == 1e-6

        # Integrator time constant
        assert circuit.time_constant == 10000 * 1e-6  # 10ms

    def test_model_loading(self):
        """Test loading real op-amp SPICE models."""
        circuit = OpAmpCircuit(
            config="inverting",
            r_in=1000,
            r_feedback=10000,
            model="LM358",  # Should load from KiCad library
        )

        # Verify model is loaded
        assert circuit.spice_model is not None
        assert "LM358" in circuit.spice_model.upper() or ".subckt" in circuit.spice_model.lower()


class TestOpAmpSimulation:
    """Test op-amp circuit simulation."""

    def test_dc_simulation(self):
        """Test DC operating point simulation."""
        circuit = OpAmpCircuit(
            config="inverting",
            r_in=1000,
            r_feedback=10000,
            vin=0.5,
            model="ideal",  # Use ideal model for predictable testing
        )

        results = simulate_opamp(circuit, analysis_type="dc")

        assert "output_voltage" in results
        assert "input_current" in results

        # Output should be -10 * 0.5 = -5V
        expected_output = -5.0
        assert abs(results["output_voltage"] - expected_output) < 0.1

    def test_ac_frequency_response(self):
        """Test AC frequency response."""
        circuit = OpAmpCircuit(config="non_inverting", r_in=10000, r_feedback=90000, model="ideal")

        results = simulate_opamp(circuit, analysis_type="ac", start_freq=1, stop_freq=1e6)

        assert "frequency" in results
        assert "gain_db" in results
        assert "phase" in results

        # Low frequency gain should be 20*log10(10) = 20dB
        low_freq_gain = results["gain_db"][0]
        assert abs(low_freq_gain - 20) < 1

    def test_transient_response(self):
        """Test transient step response."""
        circuit = OpAmpCircuit(config="buffer", model="ideal")

        results = simulate_opamp(
            circuit, analysis_type="transient", duration=1e-3, input_type="step"
        )

        assert "time" in results
        assert "output" in results
        assert "input" in results

        # Buffer output should follow input
        output = np.array(results["output"])
        input_signal = np.array(results["input"])

        # After settling, output should equal input
        assert abs(output[-1] - input_signal[-1]) < 0.01

    def test_slew_rate_limitation(self):
        """Test slew rate limiting in transient response."""
        circuit = OpAmpCircuit(config="buffer", model="LM358", slew_rate=0.5e6)  # 0.5V/µs

        results = simulate_opamp(
            circuit,
            analysis_type="transient",
            duration=100e-6,
            input_type="step",
            step_amplitude=10,
        )

        # Calculate actual slew rate from results
        output = np.array(results["output"])
        time = np.array(results["time"])

        # Find maximum rate of change
        dt = time[1] - time[0]
        dv_dt = np.diff(output) / dt
        max_slew = np.max(np.abs(dv_dt))

        # Should be limited by slew rate
        assert max_slew <= circuit.slew_rate * 1.1  # 10% tolerance


class TestAmplifierAnalysis:
    """Test amplifier analysis functions."""

    def test_gain_bandwidth_product(self):
        """Test gain-bandwidth product calculation."""
        circuit = OpAmpCircuit(
            config="inverting", r_in=1000, r_feedback=10000, model="TL072", gbw=3e6  # 3MHz GBW
        )

        analysis = calculate_gain_bandwidth(circuit)

        assert "dc_gain" in analysis
        assert "bandwidth" in analysis
        assert "gain_bandwidth_product" in analysis

        # Bandwidth = GBW / |Gain|
        expected_bw = 3e6 / 10  # Gain magnitude is 10 for inverting with -10 gain
        assert abs(analysis["bandwidth"] - expected_bw) < expected_bw * 0.2  # Allow 20% tolerance

    def test_input_output_impedance(self):
        """Test input/output impedance calculation."""
        circuit = OpAmpCircuit(config="non_inverting", r_in=10000, r_feedback=90000)

        analysis = analyze_amplifier(circuit)

        assert "input_impedance" in analysis
        assert "output_impedance" in analysis

        # Non-inverting has very high input impedance
        assert analysis["input_impedance"] > 1e6

        # Output impedance should be very low
        assert analysis["output_impedance"] < 100

    def test_noise_analysis(self):
        """Test noise performance analysis."""
        circuit = OpAmpCircuit(
            config="inverting", r_in=1000, r_feedback=10000, model="LF351"  # Low noise op-amp
        )

        analysis = analyze_amplifier(circuit, include_noise=True)

        assert "input_noise_voltage" in analysis
        assert "input_noise_current" in analysis
        assert "total_output_noise" in analysis

        # Verify noise is calculated
        assert analysis["input_noise_voltage"] > 0
        assert analysis["total_output_noise"] > 0

    def test_stability_analysis(self):
        """Test stability and phase margin."""
        circuit = OpAmpCircuit(
            config="inverting",
            r_in=1000,
            r_feedback=100000,  # High gain
            c_compensation=10e-12,  # Compensation capacitor
        )

        analysis = analyze_amplifier(circuit, include_stability=True)

        assert "phase_margin" in analysis
        assert "gain_margin" in analysis
        assert "is_stable" in analysis

        # Should be stable with compensation
        assert analysis["is_stable"] == True
        assert analysis["phase_margin"] > 45  # Degrees


class TestAmplifierReport:
    """Test amplifier report generation."""

    def test_report_generation(self):
        """Test generating amplifier analysis report."""
        circuit = OpAmpCircuit(config="non_inverting", r_in=10000, r_feedback=90000, model="TL072")

        results = simulate_opamp(circuit, analysis_type="ac")
        analysis = analyze_amplifier(circuit)

        report = generate_amplifier_report(circuit, results, analysis)

        assert report is not None
        assert len(report.figures) > 0
        assert "Amplifier" in report.title

    def test_comparison_plot(self):
        """Test comparing multiple op-amp configurations."""
        circuits = [
            OpAmpCircuit(config="inverting", r_in=1000, r_feedback=10000),
            OpAmpCircuit(config="non_inverting", r_in=1000, r_feedback=9000),
            OpAmpCircuit(config="buffer"),
        ]

        # Generate comparison report
        from examples.amplifiers.opamp import compare_amplifiers

        comparison = compare_amplifiers(circuits)

        assert "gain_comparison" in comparison
        assert "bandwidth_comparison" in comparison
        assert len(comparison["gain_comparison"]) == 3


class TestPracticalCircuits:
    """Test practical op-amp applications."""

    def test_instrumentation_amplifier(self):
        """Test three op-amp instrumentation amplifier."""
        from examples.amplifiers.opamp import InstrumentationAmplifier

        inst_amp = InstrumentationAmplifier(
            gain=100, r_gain=1000, model="LM358"  # Gain setting resistor
        )

        assert inst_amp.differential_gain == 100
        assert inst_amp.common_mode_gain < 0.01  # High CMRR

    def test_active_filter(self):
        """Test active low-pass filter."""
        from examples.amplifiers.opamp import ActiveFilter

        filter_circuit = ActiveFilter(
            filter_type="lowpass",
            cutoff_freq=1000,
            gain=10,
            order=2,  # Second-order Butterworth
            model="TL072",
        )

        assert filter_circuit.cutoff_frequency == 1000
        assert filter_circuit.passband_gain == 10

        # Test frequency response at cutoff
        response = filter_circuit.frequency_response(1000)
        assert abs(response) < 10 / np.sqrt(2) * 1.1  # -3dB point

    def test_comparator(self):
        """Test op-amp as comparator."""
        from examples.amplifiers.opamp import Comparator

        comp = Comparator(threshold=2.5, hysteresis=0.1, model="LM358")

        # Test switching thresholds
        assert abs(comp.upper_threshold - 2.55) < 0.01
        assert abs(comp.lower_threshold - 2.45) < 0.01

        # Test output states
        assert comp.compare(3.0) == comp.vcc  # High
        assert comp.compare(2.0) == 0  # Low
