#!/usr/bin/env python3
"""
AC frequency analysis demonstration.

Shows how to use the newly implemented AC analysis capabilities.
"""

import numpy as np
from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine


def demo_rc_filter_analysis():
    """Demonstrate AC analysis with RC low-pass filter."""
    print("=== RC Low-Pass Filter AC Analysis ===")
    
    # Create RC filter: R=1kΩ, C=1µF → fc ≈ 159Hz
    circuit = Circuit("RC Low-Pass Filter")
    circuit.add_voltage_source("Vin", 1, 0, "DC 0V AC 1V")  # 1V AC source
    circuit.add_resistor("R1", 1, 2, "1k")                  # 1kΩ
    circuit.add_capacitor("C1", 2, 0, "1u")                 # 1µF
    
    # Run AC analysis from 1Hz to 100kHz
    engine = SimulationEngine()
    results = engine.simulate_ac(
        circuit,
        start_frequency=1,
        stop_frequency=100000,
        points_per_decade=30
    )
    
    print(f"Frequency sweep: {results.frequency[0]:.1f}Hz to {results.frequency[-1]:.1f}Hz")
    print(f"Number of points: {len(results.frequency)}")
    
    # Calculate theoretical cutoff frequency
    fc_theoretical = 1 / (2 * np.pi * 1000 * 1e-6)
    print(f"Theoretical cutoff frequency: {fc_theoretical:.1f}Hz")
    
    # Find actual -3dB frequency
    magnitude_db = results.magnitude_db(2)
    fc_idx = np.argmin(np.abs(magnitude_db - (-3)))
    fc_measured = results.frequency[fc_idx]
    print(f"Measured -3dB frequency: {fc_measured:.1f}Hz")
    print(f"Error: {abs(fc_theoretical - fc_measured):.1f}Hz ({abs(fc_theoretical - fc_measured)/fc_theoretical*100:.1f}%)")
    
    # Show key response points
    print("\nFrequency Response Summary:")
    print(f"  At 10Hz:    {magnitude_db[np.argmin(np.abs(results.frequency - 10))]:.1f}dB")
    print(f"  At 159Hz:   {magnitude_db[np.argmin(np.abs(results.frequency - fc_theoretical))]:.1f}dB")
    print(f"  At 1kHz:    {magnitude_db[np.argmin(np.abs(results.frequency - 1000))]:.1f}dB")
    print(f"  At 10kHz:   {magnitude_db[np.argmin(np.abs(results.frequency - 10000))]:.1f}dB")
    
    # Generate Bode plot
    plot_data = results.plot_bode("V(2)", title="RC Low-Pass Filter", show=False)
    print(f"Bode plot generated with {len(plot_data['frequencies'])} points")
    
    return results


def demo_frequency_comparison():
    """Compare different frequency sweep types."""
    print("\n=== Frequency Sweep Comparison ===")
    
    # Simple circuit for testing
    circuit = Circuit("Test Circuit")
    circuit.add_voltage_source("V1", 1, 0, "DC 0V AC 1V")
    circuit.add_resistor("R1", 1, 0, "1k")  # Simple resistor
    
    engine = SimulationEngine()
    
    # Logarithmic sweep
    results_log = engine.simulate_ac(circuit, 10, 10000, 10, "dec")
    print(f"Logarithmic sweep: {len(results_log.frequency)} points")
    
    # Linear sweep  
    results_lin = engine.simulate_ac(circuit, 10, 10000, 10, "lin")
    print(f"Linear sweep: {len(results_lin.frequency)} points")
    
    # Show frequency distribution
    print("Logarithmic frequencies (first 10):", results_log.frequency[:10])
    print("Linear frequencies (first 10):", results_lin.frequency[:10])


def demo_complex_impedance():
    """Demonstrate complex impedance calculations.""" 
    print("\n=== Complex Impedance Analysis ===")
    
    engine = SimulationEngine()
    
    # Test different components at 1kHz
    freq = 1000.0
    print(f"Impedance calculations at {freq}Hz:")
    
    # Resistor: Z = R
    z_r = engine._calculate_component_impedance("resistor", 1000, freq)
    print(f"  1kΩ Resistor: {z_r:.3f} = {abs(z_r):.1f}Ω ∠{np.angle(z_r, deg=True):.1f}°")
    
    # Capacitor: Z = -j/(ωC)
    z_c = engine._calculate_component_impedance("capacitor", 1e-6, freq)  # 1µF
    print(f"  1µF Capacitor: {z_c:.3f} = {abs(z_c):.1f}Ω ∠{np.angle(z_c, deg=True):.1f}°")
    
    # Inductor: Z = jωL  
    z_l = engine._calculate_component_impedance("inductor", 10e-3, freq)  # 10mH
    print(f"  10mH Inductor: {z_l:.3f} = {abs(z_l):.1f}Ω ∠{np.angle(z_l, deg=True):.1f}°")


def demo_magnitude_phase_extraction():
    """Demonstrate magnitude and phase extraction."""
    print("\n=== Magnitude and Phase Extraction ===")
    
    # Create circuit with known response
    circuit = Circuit("Phase Shift Demo")
    circuit.add_voltage_source("V1", 1, 0, "DC 0V AC 1V")
    circuit.add_resistor("R1", 1, 2, "1k")
    circuit.add_capacitor("C1", 2, 0, "1u")
    
    engine = SimulationEngine()
    results = engine.simulate_ac(circuit, 100, 1000, 20)
    
    # Show magnitude and phase data
    node = 2
    magnitude = results.magnitude(node)
    magnitude_db = results.magnitude_db(node) 
    phase_rad = results.phase_rad(node)
    phase_deg = results.phase_deg(node)
    
    print(f"Node {node} analysis:")
    print(f"  Magnitude range: {np.min(magnitude):.4f}V to {np.max(magnitude):.4f}V")
    print(f"  Magnitude dB range: {np.min(magnitude_db):.1f}dB to {np.max(magnitude_db):.1f}dB") 
    print(f"  Phase range: {np.min(phase_deg):.1f}° to {np.max(phase_deg):.1f}°")


def main():
    """Run all AC analysis demonstrations."""
    print("🔬 Circuit Simulation - AC Frequency Analysis Demo")
    print("=" * 60)
    
    try:
        demo_rc_filter_analysis()
        demo_frequency_comparison()
        demo_complex_impedance() 
        demo_magnitude_phase_extraction()
        
        print("\n" + "=" * 60)
        print("✅ All AC analysis demonstrations completed successfully!")
        print("🎯 Key capabilities demonstrated:")
        print("   • Frequency domain simulation (AC analysis)")
        print("   • Complex voltage/current calculations") 
        print("   • Magnitude and phase extraction")
        print("   • Bode plot generation")
        print("   • Filter response validation")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()