"""Tests for RLC resonance circuit example."""

import pytest
import numpy as np
from pathlib import Path

from examples.intermediate.rlc_resonance import (
    RLCResonanceCircuit,
    simulate_rlc_circuit,
    calculate_impedance_spectrum,
    analyze_resonance,
    generate_resonance_plots
)


class TestRLCResonanceCircuit:
    """Test RLC resonance circuit implementation."""
    
    def test_series_rlc_creation(self):
        """Test creating a series RLC circuit."""
        circuit = RLCResonanceCircuit(
            r=10,        # 10Ω
            l=1e-3,      # 1mH
            c=1e-6,      # 1µF
            topology="series",
            vin=1.0
        )
        
        assert circuit.r == 10
        assert circuit.l == 1e-3
        assert circuit.c == 1e-6
        assert circuit.topology == "series"
        
        # Check resonant frequency calculation
        # f0 = 1 / (2π√(LC))
        expected_f0 = 1 / (2 * np.pi * np.sqrt(1e-3 * 1e-6))
        assert abs(circuit.resonant_frequency - expected_f0) < 0.1
    
    def test_parallel_rlc_creation(self):
        """Test creating a parallel RLC circuit."""
        circuit = RLCResonanceCircuit(
            r=1000,      # 1kΩ
            l=10e-3,     # 10mH
            c=100e-9,    # 100nF
            topology="parallel"
        )
        
        assert circuit.topology == "parallel"
        
        # Resonant frequency same for series and parallel
        expected_f0 = 1 / (2 * np.pi * np.sqrt(10e-3 * 100e-9))
        assert abs(circuit.resonant_frequency - expected_f0) < 0.1
    
    def test_quality_factor_calculation(self):
        """Test Q factor calculation."""
        # High Q circuit
        circuit_high_q = RLCResonanceCircuit(
            r=1,         # Low resistance
            l=1e-3,
            c=1e-6,
            topology="series"
        )
        
        # Low Q circuit
        circuit_low_q = RLCResonanceCircuit(
            r=100,       # High resistance
            l=1e-3,
            c=1e-6,
            topology="series"
        )
        
        # Q factor for series: Q = (1/R) * sqrt(L/C)
        assert circuit_high_q.q_factor > circuit_low_q.q_factor
        assert circuit_high_q.q_factor > 10  # High Q
        assert circuit_low_q.q_factor < 5    # Low Q
    
    def test_bandwidth_calculation(self):
        """Test bandwidth calculation."""
        circuit = RLCResonanceCircuit(
            r=10,
            l=1e-3,
            c=1e-6,
            topology="series"
        )
        
        # Bandwidth = f0 / Q
        expected_bw = circuit.resonant_frequency / circuit.q_factor
        assert abs(circuit.bandwidth - expected_bw) < 1.0
    
    def test_impedance_at_resonance(self):
        """Test impedance calculation at resonance."""
        circuit = RLCResonanceCircuit(
            r=10,
            l=1e-3,
            c=1e-6,
            topology="series"
        )
        
        # At resonance, series RLC impedance = R
        z_resonance = circuit.calculate_impedance(circuit.resonant_frequency)
        assert abs(abs(z_resonance) - circuit.r) < 0.1
        
        # Phase should be near zero at resonance
        phase = np.angle(z_resonance, deg=True)
        assert abs(phase) < 1.0
    
    def test_damping_types(self):
        """Test different damping conditions."""
        # Underdamped (oscillatory)
        underdamped = RLCResonanceCircuit(r=10, l=1e-3, c=1e-6)
        assert underdamped.damping_type == "underdamped"
        assert underdamped.damping_ratio < 1.0
        
        # Critically damped
        # For critical damping: R = 2*sqrt(L/C)
        r_critical = 2 * np.sqrt(1e-3 / 1e-6)
        critical = RLCResonanceCircuit(r=r_critical, l=1e-3, c=1e-6)
        assert abs(critical.damping_ratio - 1.0) < 0.01
        assert critical.damping_type == "critically_damped"
        
        # Overdamped (no oscillation)
        overdamped = RLCResonanceCircuit(r=200, l=1e-3, c=1e-6)
        assert overdamped.damping_ratio > 1.0
        assert overdamped.damping_type == "overdamped"


class TestRLCSimulation:
    """Test RLC circuit simulation."""
    
    def test_frequency_response(self):
        """Test frequency response simulation."""
        circuit = RLCResonanceCircuit(r=10, l=1e-3, c=1e-6)
        
        results = simulate_rlc_circuit(
            circuit,
            analysis_type="ac",
            start_freq=100,
            stop_freq=100000,
            points_per_decade=20
        )
        
        assert "frequency" in results
        assert "magnitude" in results
        assert "phase" in results
        assert "impedance" in results
        
        # Find peak response near resonance
        f0_index = np.argmin(np.abs(np.array(results["frequency"]) - circuit.resonant_frequency))
        
        # For series RLC, current is maximum at resonance
        # For parallel RLC, voltage is maximum at resonance
        if circuit.topology == "series":
            # Minimum impedance at resonance
            impedances = np.array(results["impedance"])
            assert f0_index == np.argmin(np.abs(impedances))
    
    def test_transient_response(self):
        """Test transient step response."""
        circuit = RLCResonanceCircuit(r=10, l=1e-3, c=1e-6)
        
        results = simulate_rlc_circuit(
            circuit,
            analysis_type="transient",
            duration=1e-3,
            timestep=1e-6
        )
        
        assert "time" in results
        assert "voltage" in results
        assert "current" in results
        
        # Check for oscillatory behavior in underdamped circuit
        voltage = np.array(results["voltage"])
        
        # Find peaks (oscillations)
        peaks = []
        for i in range(1, len(voltage) - 1):
            if voltage[i] > voltage[i-1] and voltage[i] > voltage[i+1]:
                peaks.append(i)
        
        # Underdamped should oscillate
        if circuit.damping_type == "underdamped":
            assert len(peaks) > 2
    
    def test_impedance_spectrum(self):
        """Test impedance spectrum calculation."""
        circuit = RLCResonanceCircuit(r=10, l=1e-3, c=1e-6)
        
        frequencies = np.logspace(2, 5, 100)
        spectrum = calculate_impedance_spectrum(circuit, frequencies)
        
        assert "frequency" in spectrum
        assert "impedance_mag" in spectrum
        assert "impedance_phase" in spectrum
        assert "real_part" in spectrum
        assert "imaginary_part" in spectrum
        
        # Verify minimum impedance at resonance for series
        if circuit.topology == "series":
            z_mags = spectrum["impedance_mag"]
            min_index = np.argmin(z_mags)
            f_at_min = frequencies[min_index]
            assert abs(f_at_min - circuit.resonant_frequency) < circuit.bandwidth


class TestResonanceAnalysis:
    """Test resonance analysis functions."""
    
    def test_analyze_resonance(self):
        """Test comprehensive resonance analysis."""
        circuit = RLCResonanceCircuit(r=10, l=1e-3, c=1e-6)
        
        analysis = analyze_resonance(circuit)
        
        assert "resonant_frequency" in analysis
        assert "q_factor" in analysis
        assert "bandwidth" in analysis
        assert "damping_ratio" in analysis
        assert "damping_type" in analysis
        assert "half_power_frequencies" in analysis
        assert "phase_at_resonance" in analysis
        
        # Check half-power frequencies
        f_lower = analysis["half_power_frequencies"]["lower"]
        f_upper = analysis["half_power_frequencies"]["upper"]
        
        assert f_lower < circuit.resonant_frequency < f_upper
        assert abs((f_upper - f_lower) - circuit.bandwidth) < 1.0
    
    def test_selectivity(self):
        """Test selectivity calculation."""
        # High Q circuit (selective)
        selective = RLCResonanceCircuit(r=1, l=1e-3, c=1e-6)
        
        # Low Q circuit (less selective)
        broad = RLCResonanceCircuit(r=100, l=1e-3, c=1e-6)
        
        analysis_selective = analyze_resonance(selective)
        analysis_broad = analyze_resonance(broad)
        
        # Selectivity = Q factor
        assert analysis_selective["selectivity"] > analysis_broad["selectivity"]
    
    def test_energy_storage(self):
        """Test energy storage calculations."""
        circuit = RLCResonanceCircuit(r=10, l=1e-3, c=1e-6, vin=1.0)
        
        analysis = analyze_resonance(circuit)
        
        assert "energy_stored" in analysis
        assert "max_inductor_energy" in analysis["energy_stored"]
        assert "max_capacitor_energy" in analysis["energy_stored"]
        
        # At resonance, energy oscillates between L and C
        # For ideal LC, max energies would be equal
        # With resistance, there's some difference
        e_l = analysis["energy_stored"]["max_inductor_energy"]
        e_c = analysis["energy_stored"]["max_capacitor_energy"]
        # Just verify both are calculated and positive
        assert e_l > 0
        assert e_c > 0


class TestResonancePlots:
    """Test resonance visualization."""
    
    def test_resonance_plot_generation(self):
        """Test generating resonance plots."""
        circuit = RLCResonanceCircuit(r=10, l=1e-3, c=1e-6)
        
        frequencies = np.logspace(2, 5, 100)
        spectrum = calculate_impedance_spectrum(circuit, frequencies)
        
        fig = generate_resonance_plots(circuit, spectrum)
        
        assert fig is not None
        assert len(fig.data) >= 2  # Magnitude and phase
        assert "Resonance" in fig.layout.title.text
    
    def test_nyquist_plot(self):
        """Test Nyquist plot generation."""
        circuit = RLCResonanceCircuit(r=10, l=1e-3, c=1e-6)
        
        frequencies = np.logspace(2, 5, 100)
        spectrum = calculate_impedance_spectrum(circuit, frequencies)
        
        fig = generate_resonance_plots(
            circuit, 
            spectrum,
            plot_type="nyquist"
        )
        
        # Nyquist plot shows real vs imaginary impedance
        assert any("Real" in str(fig.layout.xaxis.title) for fig in [fig])
        assert any("Imaginary" in str(fig.layout.yaxis.title) for fig in [fig])
    
    def test_3d_resonance_surface(self):
        """Test 3D resonance surface plot."""
        circuit = RLCResonanceCircuit(r=10, l=1e-3, c=1e-6)
        
        # Vary both frequency and a parameter (e.g., resistance)
        fig = generate_resonance_plots(
            circuit,
            None,
            plot_type="3d_surface",
            vary_param="r",
            param_range=(1, 100, 10)
        )
        
        assert fig is not None
        # 3D plot should have surface trace
        assert any(hasattr(trace, 'z') for trace in fig.data)


class TestRLCApplications:
    """Test specific RLC circuit applications."""
    
    def test_bandpass_filter(self):
        """Test RLC as bandpass filter."""
        # Design bandpass for 1kHz center, 100Hz bandwidth
        f0 = 1000  # Hz
        bw = 100   # Hz
        q = f0 / bw  # Q = 10
        
        # Calculate components for series RLC
        # Choosing L = 1mH
        l = 1e-3
        c = 1 / ((2 * np.pi * f0) ** 2 * l)
        r = 2 * np.pi * f0 * l / q
        
        circuit = RLCResonanceCircuit(r=r, l=l, c=c, topology="series")
        
        assert abs(circuit.resonant_frequency - f0) < 10
        assert abs(circuit.bandwidth - bw) < 10
        assert abs(circuit.q_factor - q) < 1
    
    def test_notch_filter(self):
        """Test RLC as notch (band-stop) filter."""
        # Parallel RLC acts as notch filter in series with signal path
        circuit = RLCResonanceCircuit(
            r=1000,
            l=10e-3,
            c=100e-9,
            topology="parallel"
        )
        
        # At resonance, parallel RLC has maximum impedance
        z_at_f0 = circuit.calculate_impedance(circuit.resonant_frequency)
        z_at_low = circuit.calculate_impedance(10)
        z_at_high = circuit.calculate_impedance(100000)
        
        # Impedance should be maximum at resonance for parallel
        assert abs(z_at_f0) > abs(z_at_low)
        assert abs(z_at_f0) > abs(z_at_high)
    
    def test_tank_circuit(self):
        """Test parallel LC tank circuit (high Q oscillator)."""
        # Tank circuit with very HIGH parallel resistance for high Q
        # In parallel topology, high R means high Q
        tank = RLCResonanceCircuit(
            r=100000,  # Very high parallel resistance
            l=100e-6,
            c=1e-9,
            topology="parallel"
        )
        
        # Very high Q for oscillation
        assert tank.q_factor > 100
        
        # Very narrow bandwidth
        assert tank.bandwidth < tank.resonant_frequency / 100