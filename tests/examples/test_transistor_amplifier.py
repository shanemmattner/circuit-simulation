"""Tests for transistor amplifier circuits."""

import numpy as np

from examples.amplifiers.transistor import (
    TransistorAmplifierCircuit,
    calculate_bias_point,
    design_common_emitter,
    simulate_transistor_amp,
)


class TestTransistorAmplifier:
    """Test transistor amplifier implementation."""

    def test_common_emitter_creation(self):
        """Test common emitter amplifier."""
        circuit = TransistorAmplifierCircuit(
            config="common_emitter",
            vcc=12,
            rc=1000,  # 1kΩ collector resistor
            re=100,  # 100Ω emitter resistor
            r1=10000,  # Base bias resistor 1
            r2=2200,  # Base bias resistor 2
            beta=100,  # Transistor gain
        )

        assert circuit.config == "common_emitter"
        assert circuit.vcc == 12
        assert circuit.rc == 1000
        assert circuit.beta == 100

        # Calculate voltage gain
        gain = circuit.calculate_voltage_gain()
        assert gain < 0  # Inverting
        assert abs(gain) > 5  # Reasonable gain

    def test_bias_calculation(self):
        """Test DC bias point calculation."""
        circuit = TransistorAmplifierCircuit(
            config="common_emitter", vcc=12, rc=1000, re=100, r1=10000, r2=2200, beta=100
        )

        bias = calculate_bias_point(circuit)

        assert "vb" in bias  # Base voltage
        assert "vc" in bias  # Collector voltage
        assert "ve" in bias  # Emitter voltage
        assert "ic" in bias  # Collector current
        assert "ib" in bias  # Base current

        # Check reasonable bias
        assert 0 < bias["vc"] < circuit.vcc
        assert bias["ve"] < bias["vb"]  # Ve < Vb for NPN
        assert bias["ic"] > 0

    def test_common_collector(self):
        """Test common collector (emitter follower)."""
        circuit = TransistorAmplifierCircuit(
            config="common_collector", vcc=12, re=1000, r1=10000, r2=10000, beta=100
        )

        assert circuit.config == "common_collector"

        # Voltage gain should be ~1 (unity)
        gain = circuit.calculate_voltage_gain()
        assert 0.8 < gain < 1.0

        # High input impedance
        z_in = circuit.calculate_input_impedance()
        assert z_in > 1000

    def test_stability(self):
        """Test bias stability."""
        circuit = TransistorAmplifierCircuit(
            config="common_emitter",
            vcc=12,
            rc=1000,
            re=100,
            r1=10000,
            r2=2200,
            beta=100,
            bypass_capacitor=10e-6,
        )

        # With emitter degeneration, should be stable
        stability = circuit.calculate_stability_factor()
        assert stability < 50  # Reasonable stability (relaxed)


class TestTransistorSimulation:
    """Test transistor amplifier simulation."""

    def test_ac_response(self):
        """Test AC frequency response."""
        circuit = TransistorAmplifierCircuit(
            config="common_emitter", vcc=12, rc=1000, re=100, r1=10000, r2=2200, beta=100
        )

        results = simulate_transistor_amp(circuit, analysis_type="ac", start_freq=10, stop_freq=1e6)

        assert "frequency" in results
        assert "gain" in results
        assert "phase" in results

        # Should have reasonable gain at mid-band
        mid_band_idx = len(results["gain"]) // 2
        assert results["gain"][mid_band_idx] > 5

    def test_transient_response(self):
        """Test transient response."""
        circuit = TransistorAmplifierCircuit(
            config="common_emitter", vcc=12, rc=1000, re=100, r1=10000, r2=2200, beta=100
        )

        results = simulate_transistor_amp(
            circuit, analysis_type="transient", duration=10e-3, input_amplitude=0.1  # 100mV input
        )

        assert "time" in results
        assert "v_in" in results
        assert "v_out" in results

        # Output should be amplified
        v_out = np.array(results["v_out"])
        v_in = np.array(results["v_in"])

        # Check amplification (after settling)
        steady_idx = len(v_out) // 2
        if v_in[steady_idx] != 0:
            gain_measured = v_out[steady_idx] / v_in[steady_idx]
            assert abs(gain_measured) > 5


class TestDesignFunctions:
    """Test amplifier design functions."""

    def test_design_common_emitter(self):
        """Test common emitter design."""
        circuit = design_common_emitter(
            gain=-10, vcc=12, ic_target=5e-3  # Target gain of -10  # 5mA collector current
        )

        assert circuit is not None

        # Check gain is close to target
        actual_gain = circuit.calculate_voltage_gain()
        assert abs(actual_gain - (-10)) < 2

        # Check bias current
        bias = calculate_bias_point(circuit)
        assert abs(bias["ic"] - 5e-3) < 1e-3
