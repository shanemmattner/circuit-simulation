#!/usr/bin/env python3
"""
Debug Bode Plot Calculations

Investigate why Bode plots are still showing incorrect values despite fixes.
Test each circuit type and examine the actual data being plotted.
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine


def debug_voltage_divider_ac():
    """Debug voltage divider AC analysis - should be flat at -6dB"""
    print("🔍 Debugging Voltage Divider AC Analysis")
    print("=" * 50)
    
    # Voltage divider: should be 0.5V output (= -6.02dB) at all frequencies
    circuit = Circuit("Voltage Divider")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="10V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
    circuit.add_resistor("R2", node1=2, node2="gnd", resistance="1k")
    
    print("   Topology: V1(10V) → R1(1k) → Node2 → R2(1k) → GND")
    print("   Expected: Node 2 should be 5V DC, 0.5V AC (= -6.02dB)")
    
    engine = SimulationEngine()
    
    # Test DC first
    dc_results = engine.simulate_dc(circuit)
    print(f"\n📊 DC Results:")
    for node in dc_results.nodes:
        if node != 0:
            voltage = dc_results.voltage(node)
            print(f"   Node {node}: {voltage[0]:.3f}V")
    
    # Test AC
    ac_results = engine.simulate_ac(circuit, start_frequency=1, stop_frequency=1000, points_per_decade=10)
    print(f"\n🌊 AC Results:")
    print(f"   Nodes: {ac_results.nodes}")
    
    for node in ac_results.nodes:
        if node != 0:
            voltage = ac_results.voltage(node) 
            if voltage is not None:
                magnitude = np.abs(voltage)
                magnitude_db = 20 * np.log10(np.maximum(magnitude, 1e-12))
                phase = np.angle(voltage, deg=True)
                
                print(f"\n   Node {node}:")
                print(f"   Raw magnitude: {magnitude[0]:.6f} to {magnitude[-1]:.6f}")
                print(f"   Magnitude dB: {magnitude_db[0]:.2f} to {magnitude_db[-1]:.2f}")
                print(f"   Phase: {phase[0]:.1f}° to {phase[-1]:.1f}°")
                
                # Expected for voltage divider
                if node == 2:
                    expected_mag = 0.5  # Half of 1V AC input
                    expected_db = 20 * np.log10(expected_mag)  # Should be -6.02dB
                    print(f"   Expected: {expected_mag:.3f}V = {expected_db:.2f}dB")
                    
                    if abs(magnitude[0] - expected_mag) < 0.01:
                        print(f"   ✅ Correct magnitude")
                    else:
                        print(f"   ❌ Incorrect magnitude")


def debug_rc_filter_ac():
    """Debug RC filter - should show proper rolloff"""
    print("\n🔍 Debugging RC Low-Pass Filter")
    print("=" * 50)
    
    circuit = Circuit("RC Low-Pass Filter")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
    circuit.add_capacitor("C1", node1=2, node2="gnd", capacitance="1uF")
    
    # Calculate expected cutoff frequency
    R = 1000  # 1k ohm
    C = 1e-6  # 1uF
    fc = 1 / (2 * np.pi * R * C)
    print(f"   Expected cutoff frequency: {fc:.1f} Hz")
    print(f"   At fc: magnitude should be -3dB (0.707V)")
    
    engine = SimulationEngine()
    ac_results = engine.simulate_ac(circuit, start_frequency=1, stop_frequency=100000, points_per_decade=30)
    
    frequencies = np.array(ac_results.frequency)
    print(f"\n🌊 AC Analysis: {len(frequencies)} points from {frequencies[0]:.1f} to {frequencies[-1]:.1f} Hz")
    
    for node in ac_results.nodes:
        if node != 0:
            voltage = ac_results.voltage(node)
            if voltage is not None:
                magnitude = np.abs(voltage)
                magnitude_db = 20 * np.log10(np.maximum(magnitude, 1e-12))
                
                print(f"\n   Node {node}:")
                
                # Find specific frequency points
                low_idx = 0  # 1 Hz
                cutoff_idx = np.argmin(np.abs(frequencies - fc))  # Near cutoff
                high_idx = np.argmin(np.abs(frequencies - 10000))  # 10kHz
                
                print(f"   At {frequencies[low_idx]:.1f} Hz: {magnitude[low_idx]:.6f}V = {magnitude_db[low_idx]:.2f}dB")
                print(f"   At {frequencies[cutoff_idx]:.1f} Hz: {magnitude[cutoff_idx]:.6f}V = {magnitude_db[cutoff_idx]:.2f}dB")
                print(f"   At {frequencies[high_idx]:.1f} Hz: {magnitude[high_idx]:.6f}V = {magnitude_db[high_idx]:.2f}dB")
                
                if node == 2:  # Output node
                    # Check if we see proper rolloff
                    rolloff = magnitude_db[low_idx] - magnitude_db[high_idx]
                    print(f"   Total rolloff: {rolloff:.1f}dB")
                    
                    if rolloff > 20:  # Should see significant attenuation
                        print(f"   ✅ Good rolloff behavior")
                    else:
                        print(f"   ❌ Insufficient rolloff")


def debug_what_pyspice_returns():
    """Debug what PySpice actually returns for AC analysis"""
    print("\n🔍 Debugging Raw PySpice AC Data")
    print("=" * 50)
    
    # Test PySpice directly
    try:
        from PySpice.Spice.Netlist import Circuit as PySpiceCircuit
        from PySpice.Unit import u_V, u_Ohm, u_F
        
        # Simple RC filter
        circuit = PySpiceCircuit("RC_Direct_Test")
        circuit.V(1, "input", circuit.gnd, "DC 0 AC 1")  # 1V AC source
        circuit.R(1, "input", "output", 1000@u_Ohm)
        circuit.C(1, "output", circuit.gnd, 1e-6@u_F)
        
        simulator = circuit.simulator(temperature=25, nominal_temperature=25)
        analysis = simulator.ac(start_frequency=1, stop_frequency=1000, number_of_points=10, variation='dec')
        
        print("✅ Direct PySpice AC analysis")
        print(f"   Available nodes: {list(analysis.nodes.keys())}")
        print(f"   Frequency points: {len(analysis.frequency)}")
        
        # Check actual PySpice data format
        for node_name in analysis.nodes.keys():
            if 'output' in node_name.lower():
                voltage_data = analysis.nodes[node_name]
                print(f"\n   Raw PySpice data for {node_name}:")
                print(f"   Type: {type(voltage_data)}")
                
                # Convert to numpy array and check
                voltage_array = np.array([complex(v) for v in voltage_data])
                magnitude = np.abs(voltage_array)
                phase = np.angle(voltage_array, deg=True)
                
                print(f"   First 3 complex values: {voltage_array[:3]}")
                print(f"   Magnitudes: {magnitude[:3]}")
                print(f"   Phases: {phase[:3]}")
                
                # Check if we see rolloff
                rolloff_db = 20 * np.log10(magnitude[0]) - 20 * np.log10(magnitude[-1])
                print(f"   Rolloff: {rolloff_db:.1f}dB from 1Hz to 1kHz")
                
    except Exception as e:
        print(f"❌ Direct PySpice test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_voltage_divider_ac()
    debug_rc_filter_ac() 
    debug_what_pyspice_returns()