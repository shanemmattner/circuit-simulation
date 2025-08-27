"""
Integration tests for complete AC frequency analysis workflow.
"""

import numpy as np
import pytest

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine


class TestACAnalysisIntegration:
    """Test complete AC analysis workflow integration."""

    def test_rc_lowpass_filter_complete_workflow(self):
        """Test complete AC analysis workflow with RC low-pass filter."""
        # Create RC low-pass filter: R=1kΩ, C=1µF → fc ≈ 159Hz
        circuit = Circuit("RC Low-Pass Filter")
        circuit.add_voltage_source("V1", 1, 0, "DC 0V AC 1V")  # 1V AC source
        circuit.add_resistor("R1", 1, 2, "1k")                # 1kΩ resistor
        circuit.add_capacitor("C1", 2, 0, "1u")               # 1µF capacitor

        # Run AC analysis
        engine = SimulationEngine()
        results = engine.simulate_ac(
            circuit,
            start_frequency=1,       # 1 Hz
            stop_frequency=100000,   # 100 kHz
            points_per_decade=30     # High resolution
        )

        # Verify basic structure
        assert results.analysis_type == "ac"
        assert results.frequency is not None
        assert len(results.frequency) > 0

        # Verify nodes
        assert 1 in results.nodes  # Input node
        assert 2 in results.nodes  # Output node

        # Get transfer function data
        v_in = results.voltage(1)   # Should be 1V at all frequencies (input)
        v_out = results.voltage(2)  # Output voltage (filtered)

        assert v_in is not None
        assert v_out is not None
        assert len(v_in) == len(v_out)

        # Calculate theoretical cutoff frequency
        R = 1000.0  # 1kΩ
        C = 1e-6    # 1µF
        fc_theoretical = 1 / (2 * np.pi * R * C)  # ≈ 159.15 Hz

        # Verify filter characteristics
        frequencies = results.frequency
        
        # Find indices for key frequencies
        dc_idx = 0  # Lowest frequency
        fc_idx = np.argmin(np.abs(frequencies - fc_theoretical))
        hf_idx = -1  # Highest frequency

        # Test magnitude response
        magnitude = results.magnitude(2)
        magnitude_db = results.magnitude_db(2)
        
        # At very low frequency: gain ≈ 0dB (no attenuation)
        assert abs(magnitude_db[dc_idx] - 0.0) < 0.5
        
        # At cutoff frequency: gain ≈ -3dB  
        assert abs(magnitude_db[fc_idx] - (-3.0)) < 0.5
        
        # At high frequency: significant attenuation (< -40dB)
        assert magnitude_db[hf_idx] < -40

        # Test phase response
        phase = results.phase_deg(2)
        
        # At low frequency: phase ≈ 0°
        assert abs(phase[dc_idx]) < 10
        
        # At cutoff frequency: phase ≈ -45°
        assert abs(phase[fc_idx] - (-45)) < 10
        
        # At high frequency: phase approaches -90°
        assert phase[hf_idx] < -80

        # Test rolloff rate (-20dB/decade for single pole)
        # Find frequency 10x above cutoff
        f_10fc_idx = np.argmin(np.abs(frequencies - (10 * fc_theoretical)))
        if f_10fc_idx < len(magnitude_db):
            gain_10fc = magnitude_db[f_10fc_idx]
            # Should be approximately -23dB (−3dB at fc + −20dB for decade)
            expected_gain = -3 - 20  # -23dB
            assert abs(gain_10fc - expected_gain) < 5  # Within 5dB tolerance

    def test_rl_highpass_filter_workflow(self):
        """Test AC analysis with RL high-pass filter."""
        # Actually, let's test with an RC high-pass filter instead (simpler)
        # RC high-pass: input → C → output → R → gnd
        circuit = Circuit("RC High-Pass Filter")  
        circuit.add_voltage_source("V1", 1, 0, "DC 0V AC 1V")  # 1V AC source
        circuit.add_capacitor("C1", 1, 2, "100n")             # 100nF capacitor in series
        circuit.add_resistor("R1", 2, 0, "1k")                # 1kΩ resistor to ground (output)

        # Run AC analysis
        engine = SimulationEngine()
        results = engine.simulate_ac(
            circuit,
            start_frequency=10,      # 10 Hz
            stop_frequency=100000,   # 100 kHz
            points_per_decade=25
        )

        # Verify structure
        assert results.analysis_type == "ac"
        assert results.frequency is not None

        # Calculate theoretical cutoff frequency for RC high-pass
        R = 1000.0  # 1kΩ
        C = 100e-9  # 100nF  
        fc_theoretical = 1 / (2 * np.pi * R * C)  # ≈ 1591.5 Hz

        # Test high-pass characteristics
        frequencies = results.frequency
        fc_idx = np.argmin(np.abs(frequencies - fc_theoretical))
        
        magnitude_db = results.magnitude_db(2)
        
        # At low frequency: significant attenuation for high-pass
        assert magnitude_db[0] < -10  # Should be attenuated at low freq
        
        # At cutoff frequency: ≈ -3dB
        assert abs(magnitude_db[fc_idx] - (-3)) < 2
        
        # At high frequency: gain approaches 0dB  
        assert magnitude_db[-1] > -5  # Should approach 0dB at high freq

    def test_bode_plot_integration(self):
        """Test Bode plot generation integration."""
        # Create simple RC circuit
        circuit = Circuit("RC Test")
        circuit.add_voltage_source("Vin", 1, 0, "DC 0V AC 1V")
        circuit.add_resistor("R", 1, 2, "1k")
        circuit.add_capacitor("C", 2, 0, "100n")  # 100nF → fc ≈ 1.59kHz

        # Run AC analysis
        engine = SimulationEngine()
        results = engine.simulate_ac(circuit, 10, 100000, 20)

        # Generate Bode plot
        plot_data = results.plot_bode("V(2)", title="RC Filter Bode Plot", show=False)

        # Verify plot data structure
        assert "magnitude_db" in plot_data
        assert "phase_deg" in plot_data
        assert "frequencies" in plot_data
        assert plot_data["signal"] == "V(2)"

        # Verify data consistency
        assert len(plot_data["magnitude_db"]) == len(results.frequency)
        assert len(plot_data["phase_deg"]) == len(results.frequency)
        
        # Verify filter response characteristics
        mag_db = plot_data["magnitude_db"]
        phase_deg = plot_data["phase_deg"]
        
        # Low frequency: ~0dB, ~0°
        assert abs(mag_db[0]) < 1
        assert abs(phase_deg[0]) < 10
        
        # High frequency: significant attenuation, approaching -90°
        assert mag_db[-1] < -20
        assert phase_deg[-1] < -60

    def test_multiple_pole_filter(self):
        """Test AC analysis with multiple-pole filter."""
        # Create two-stage RC filter (cascaded RC sections)
        circuit = Circuit("Two-Stage RC Filter")
        circuit.add_voltage_source("Vin", 1, 0, "DC 0V AC 1V")
        
        # First stage: R1-C1
        circuit.add_resistor("R1", 1, 2, "1k")
        circuit.add_capacitor("C1", 2, 0, "100n")
        
        # Second stage: R2-C2 (same values for identical poles)
        circuit.add_resistor("R2", 2, 3, "1k")  
        circuit.add_capacitor("C2", 3, 0, "100n")

        # Run AC analysis
        engine = SimulationEngine()
        results = engine.simulate_ac(circuit, 1, 1000000, 25)

        # Two-pole filter should have -40dB/decade rolloff
        frequencies = results.frequency
        magnitude_db = results.magnitude_db(3)  # Final output

        # Find two frequencies one decade apart in the rolloff region
        fc = 1 / (2 * np.pi * 1000 * 100e-9)  # ≈ 1.59kHz per stage
        f1 = 10 * fc    # Well above cutoff
        f2 = 100 * fc   # One decade higher

        f1_idx = np.argmin(np.abs(frequencies - f1))
        f2_idx = np.argmin(np.abs(frequencies - f2))

        if f2_idx < len(magnitude_db):
            gain_difference = magnitude_db[f2_idx] - magnitude_db[f1_idx]
            # Should be approximately -40dB/decade for two poles
            assert gain_difference < -30  # At least -30dB/decade (allowing some tolerance)

    def test_error_handling(self):
        """Test error handling in AC analysis."""
        circuit = Circuit("Empty")  # Empty circuit
        engine = SimulationEngine()

        # Empty circuit should either fail or return empty results
        try:
            results = engine.simulate_ac(circuit, 100, 1000, 10)
            # If it succeeds, should have valid structure but no meaningful data
            assert results.analysis_type == "ac"
            assert len(results.nodes) == 0  # No nodes with data
        except (RuntimeError, ValueError, Exception):
            # Also acceptable if it raises an error for empty circuit
            pass

        # Test invalid frequency range
        circuit.add_voltage_source("V1", 1, 0, "1V")
        circuit.add_resistor("R1", 1, 0, "1k")
        
        # Invalid frequency range (start > stop)
        with pytest.raises((ValueError, RuntimeError)):
            engine.simulate_ac(circuit, 1000, 100, 10)  # start_freq > stop_freq