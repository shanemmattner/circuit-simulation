#!/usr/bin/env python3
"""
Transfer Function Analysis Demo

Demonstrates extracting and analyzing transfer functions from circuits.
"""

import numpy as np
from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine
from circuit_sim.analysis import TransferFunction


def example_rc_filter():
    """Analyze a simple RC low-pass filter."""
    print("\n" + "="*60)
    print("RC LOW-PASS FILTER ANALYSIS")
    print("="*60)
    
    # Create RC filter: Vin -> R -> Vout -> C -> GND
    circuit = Circuit("RC Low-Pass Filter")
    circuit.add_resistor("R1", "in", "out", "1k")  # 1kΩ
    circuit.add_capacitor("C1", "out", "0", "1u")  # 1μF
    circuit.add_voltage_source("V1", "in", "0", "1V")
    
    # Run AC analysis from 1Hz to 100kHz
    engine = SimulationEngine()
    results = engine.simulate_ac(circuit, 1, 100e3, points_per_decade=20)
    
    # Extract transfer function
    tf = results.to_transfer_function("in", "out")
    
    print(f"\nTransfer Function Properties:")
    print(f"  Order: {tf.order}")
    print(f"  DC Gain: {tf.dc_gain:.3f} ({20*np.log10(tf.dc_gain):.1f} dB)")
    print(f"  Bandwidth: {tf.bandwidth/(2*np.pi):.1f} Hz")
    print(f"  Poles: {tf.poles}")
    print(f"  Is Stable: {tf.is_stable}")
    
    # Calculate theoretical values for comparison
    R = 1000  # ohms
    C = 1e-6  # farads
    fc_theoretical = 1 / (2 * np.pi * R * C)
    print(f"\nTheoretical cutoff frequency: {fc_theoretical:.1f} Hz")
    
    # Analyze stability
    margins = tf.stability_margins()
    print(f"\n{margins}")
    
    return tf


def example_second_order_filter():
    """Analyze a second-order active filter."""
    print("\n" + "="*60)
    print("SECOND-ORDER ACTIVE FILTER ANALYSIS")
    print("="*60)
    
    # Create a Sallen-Key low-pass filter
    circuit = Circuit("Sallen-Key Filter")
    
    # Input stage
    circuit.add_voltage_source("V1", "in", "0", "1V")
    circuit.add_resistor("R1", "in", "n1", "10k")  # 10kΩ
    circuit.add_resistor("R2", "n1", "n2", "10k")  # 10kΩ
    circuit.add_capacitor("C1", "n2", "out", "10n")  # 10nF
    circuit.add_capacitor("C2", "n1", "0", "10n")  # 10nF
    
    # Unity-gain buffer (ideal op-amp)
    circuit.add_vcvs("E1", "out", "0", "n2", "0", 1)  # Voltage follower
    
    # Run AC analysis
    engine = SimulationEngine()
    results = engine.simulate_ac(circuit, 10, 100e3, points_per_decade=30)
    
    # Extract transfer function
    tf = results.to_transfer_function("in", "out")
    
    print(f"\nTransfer Function Properties:")
    print(f"  Order: {tf.order}")
    print(f"  DC Gain: {tf.dc_gain:.3f} ({20*np.log10(tf.dc_gain):.1f} dB)")
    print(f"  Bandwidth: {tf.bandwidth/(2*np.pi):.1f} Hz")
    print(f"  Number of poles: {len(tf.poles)}")
    print(f"  Is Stable: {tf.is_stable}")
    
    # Time domain analysis
    print(f"\nStep Response Characteristics:")
    print(f"  Rise Time: {tf.rise_time()*1000:.2f} ms")
    print(f"  Settling Time (2%): {tf.settling_time()*1000:.2f} ms")
    print(f"  Overshoot: {tf.overshoot():.1f}%")
    
    return tf


def example_feedback_system():
    """Analyze a feedback amplifier for stability."""
    print("\n" + "="*60)
    print("FEEDBACK AMPLIFIER STABILITY ANALYSIS")
    print("="*60)
    
    # Create feedback amplifier with compensation
    circuit = Circuit("Feedback Amplifier")
    
    # Input and feedback network
    circuit.add_voltage_source("V1", "in", "0", "1V")
    circuit.add_resistor("R1", "in", "n1", "10k")  # Input resistor
    circuit.add_resistor("R2", "n1", "out", "90k")  # Feedback resistor
    
    # Amplifier with frequency-dependent gain (simulated with RC)
    circuit.add_vcvs("E1", "n2", "0", "n1", "0", 100)  # High gain
    circuit.add_resistor("R3", "n2", "out", "100")  # Output resistance
    circuit.add_capacitor("C1", "out", "0", "100p")  # Parasitic capacitance
    
    # Compensation capacitor
    circuit.add_capacitor("Cc", "n1", "out", "10p")  # Miller compensation
    
    # Run AC analysis
    engine = SimulationEngine()
    results = engine.simulate_ac(circuit, 1, 10e6, points_per_decade=20)
    
    # Extract closed-loop transfer function
    tf = results.to_transfer_function("in", "out")
    
    print(f"\nClosed-Loop Transfer Function:")
    print(f"  DC Gain: {tf.dc_gain:.1f} ({20*np.log10(tf.dc_gain):.1f} dB)")
    print(f"  Bandwidth: {tf.bandwidth/(2*np.pi)/1000:.1f} kHz")
    print(f"  Is Stable: {tf.is_stable}")
    
    # Stability analysis
    margins = tf.stability_margins()
    print(f"\n{margins}")
    
    if margins.phase_margin < 45:
        print("\n⚠️  Warning: Phase margin is low. Consider increasing compensation.")
    else:
        print("\n✓ System has adequate phase margin for stability.")
    
    return tf


def example_from_poles_zeros():
    """Create transfer function directly from poles and zeros."""
    print("\n" + "="*60)
    print("TRANSFER FUNCTION FROM POLES AND ZEROS")
    print("="*60)
    
    # Design a lead compensator
    zeros = [-1000]  # Zero at 1000 rad/s
    poles = [-10000]  # Pole at 10000 rad/s
    gain = 10
    
    tf = TransferFunction.from_poles_zeros(poles, zeros, gain)
    
    print(f"\nLead Compensator Design:")
    print(f"  Zeros: {zeros}")
    print(f"  Poles: {poles}")
    print(f"  DC Gain: {tf.dc_gain:.1f}")
    print(f"  Peak frequency: {np.sqrt(1000*10000)/(2*np.pi):.1f} Hz")
    
    # Analyze frequency response
    frequencies = np.logspace(1, 5, 100)  # 10 Hz to 100 kHz
    response = tf.frequency_response(frequencies)
    
    max_gain_idx = np.argmax(np.abs(response))
    max_gain_freq = frequencies[max_gain_idx] / (2*np.pi)
    max_gain_db = 20*np.log10(np.abs(response[max_gain_idx]))
    
    print(f"  Maximum gain: {max_gain_db:.1f} dB at {max_gain_freq:.1f} Hz")
    
    # Phase contribution
    phase_at_peak = np.angle(response[max_gain_idx], deg=True)
    print(f"  Phase at peak: {phase_at_peak:.1f}°")
    
    return tf


def main():
    """Run all transfer function analysis examples."""
    print("\n" + "#"*60)
    print("# TRANSFER FUNCTION ANALYSIS DEMONSTRATION")
    print("#"*60)
    
    # Run examples
    tf_rc = example_rc_filter()
    tf_active = example_second_order_filter()
    tf_feedback = example_feedback_system()
    tf_lead = example_from_poles_zeros()
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print("\nTransfer function analysis provides crucial insights for:")
    print("  • Filter design and characterization")
    print("  • Control system stability analysis")
    print("  • Frequency response optimization")
    print("  • Time-domain performance prediction")


if __name__ == "__main__":
    main()