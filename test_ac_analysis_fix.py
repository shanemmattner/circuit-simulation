#!/usr/bin/env python3
"""
Test AC analysis with proper error handling and node naming
"""

import numpy as np
from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine
from circuit_sim.analysis import TransferFunction

def test_ac_analysis_with_proper_nodes():
    """Test AC analysis avoiding Python keyword node names."""
    print("🔧 TESTING AC ANALYSIS WITH PROPER NODE NAMES")
    print("=" * 55)
    
    try:
        # Create RC filter with numeric node names (avoiding Python keywords)
        circuit = Circuit("RC Filter")
        # For AC analysis, we need to add AC source information
        # Note: The current API may not support AC sources directly
        # Let's try a different approach
        circuit.add_voltage_source("V1", "1", "0", "1V")  # DC source
        circuit.add_resistor("R1", "1", "2", "1k")        # 1kΩ from node 1 to 2
        circuit.add_capacitor("C1", "2", "0", "1u")       # 1μF from node 2 to ground
        
        print("Circuit created:")
        print("  V1: 1V source from node 1 to ground")
        print("  R1: 1kΩ from node 1 to node 2") 
        print("  C1: 1μF from node 2 to ground")
        print("  Expected: RC low-pass filter, fc = 159.2 Hz")
        
        # Run AC analysis
        engine = SimulationEngine()
        print("\nRunning AC analysis from 10Hz to 1kHz...")
        results = engine.simulate_ac(circuit, 10, 1000, points_per_decade=10)
        
        print("✅ AC analysis completed successfully!")
        
        # Check what we got
        print(f"Nodes found: {results.nodes}")
        print(f"Frequency points: {len(results.frequency) if results.frequency is not None else 'None'}")
        
        if results.frequency is not None:
            print(f"Frequency range: {results.frequency[0]:.1f} to {results.frequency[-1]:.1f} Hz")
        
        # Debug: Check all available voltages
        print("\nAll available voltages:")
        for node in results.nodes:
            voltage = results.voltage(node)
            print(f"  Node {node}: {voltage[0] if voltage is not None and len(voltage) > 0 else 'None'}")
        
        # Try transfer function extraction with available nodes
        available_nodes = results.nodes
        if len(available_nodes) >= 2:
            node1, node2 = available_nodes[:2]
            print(f"\nAttempting transfer function extraction from node {node1} to node {node2}...")
            try:
                tf = results.to_transfer_function(node1, node2)
                
                print("🎉 Transfer function extracted successfully!")
                print(f"DC Gain: {tf.dc_gain:.3f}")
                print(f"Bandwidth: {tf.bandwidth/(2*np.pi):.1f} Hz")
            except Exception as e:
                print(f"❌ Transfer function extraction failed: {e}")
            
        else:
            print("❌ Not enough nodes available for transfer function extraction")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_simple_voltage_divider():
    """Test with an even simpler circuit - voltage divider."""
    print("\n" + "🔧 TESTING SIMPLE VOLTAGE DIVIDER")
    print("=" * 55)
    
    try:
        # Simple resistive voltage divider
        circuit = Circuit("Voltage Divider")
        circuit.add_voltage_source("V1", "1", "0", "1V")
        circuit.add_resistor("R1", "1", "2", "1k")  # 1kΩ
        circuit.add_resistor("R2", "2", "0", "1k")  # 1kΩ
        
        print("Circuit: Voltage divider with two 1kΩ resistors")
        print("Expected: V2 = 0.5 * V1 (flat frequency response)")
        
        # Run AC analysis
        engine = SimulationEngine()
        results = engine.simulate_ac(circuit, 1, 1000, points_per_decade=5)
        
        print("✅ AC analysis completed!")
        
        # Check transfer function
        tf = results.to_transfer_function("1", "2")
        print(f"Transfer function DC gain: {tf.dc_gain:.3f}")
        print(f"Expected: 0.5")
        print(f"Error: {abs(tf.dc_gain - 0.5)/0.5*100:.1f}%")
        
        if abs(tf.dc_gain - 0.5) < 0.01:
            print("✅ Voltage divider working correctly!")
        else:
            print("⚠️ Voltage divider result unexpected")
            
    except Exception as e:
        print(f"❌ Error in voltage divider test: {e}")

def test_manual_transfer_function():
    """Test creating transfer function manually to verify our fixes."""
    print("\n" + "🔧 TESTING MANUAL TRANSFER FUNCTION CREATION")
    print("=" * 55)
    
    try:
        # Create transfer function with known good data
        frequencies = np.logspace(0, 3, 50)  # 1 to 1000 rad/s
        
        # Generate ideal RC response: H(jω) = 1/(1 + jωRC)
        R = 1000  # 1kΩ
        C = 1e-6  # 1μF
        s = 1j * frequencies
        h_ideal = 1 / (1 + s * R * C)
        
        print(f"Creating transfer function from ideal RC response")
        print(f"R = {R}Ω, C = {C*1e6}μF")
        print(f"Expected cutoff: {1/(2*np.pi*R*C):.1f} Hz")
        
        tf = TransferFunction.from_frequency_response(frequencies, h_ideal)
        
        print("✅ Transfer function created from frequency response!")
        print(f"Extracted DC gain: {tf.dc_gain:.3f}")
        print(f"Extracted bandwidth: {tf.bandwidth/(2*np.pi):.1f} Hz")
        print(f"Expected bandwidth: {1/(2*np.pi*R*C):.1f} Hz")
        
        error = abs(tf.bandwidth/(2*np.pi) - 1/(2*np.pi*R*C)) / (1/(2*np.pi*R*C)) * 100
        print(f"Bandwidth error: {error:.2f}%")
        
        if error < 5:
            print("✅ Manual transfer function extraction working perfectly!")
        else:
            print("⚠️ Manual transfer function has some error")
            
    except Exception as e:
        print(f"❌ Error in manual transfer function test: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all AC analysis tests."""
    print("🎯 AC ANALYSIS AND TRANSFER FUNCTION TESTING")
    print("=" * 55)
    print("Testing AC analysis engine fixes and transfer function integration")
    
    test_ac_analysis_with_proper_nodes()
    test_simple_voltage_divider()
    test_manual_transfer_function()
    
    print("\n" + "=" * 55)
    print("🎯 AC ANALYSIS TESTING COMPLETE")

if __name__ == "__main__":
    main()