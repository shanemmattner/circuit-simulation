#!/usr/bin/env python3
"""
Debug Pi Filter Node Analysis

Check which nodes in the Pi filter should show the frequency response.
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine


def debug_pi_filter_nodes():
    """Debug which nodes in Pi filter show frequency response"""
    print("🔍 Debugging Pi Filter Node Response")
    print("=" * 50)
    
    # Create Pi filter - let's trace the nodes carefully
    circuit = Circuit("Pi Low-Pass Filter")
    
    print("🏗️  Building Pi filter circuit:")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="5V")
    print("   V1: Node 1 (+) to GND (-)")
    
    circuit.add_capacitor("C1", node1=1, node2="gnd", capacitance="10uF")
    print("   C1: Node 1 to GND (input capacitor)")
    
    circuit.add_inductor("L1", node1=1, node2=2, inductance="1mH")
    print("   L1: Node 1 to Node 2 (series inductor)")
    
    circuit.add_capacitor("C2", node1=2, node2="gnd", capacitance="10uF") 
    print("   C2: Node 2 to GND (output capacitor)")
    
    circuit.add_resistor("R_load", node1=2, node2="gnd", resistance="50")
    print("   R_load: Node 2 to GND (load resistor)")
    
    print(f"\n📊 Circuit topology:")
    print(f"   Node 1: Input (voltage source + input cap)")
    print(f"   Node 2: Output (through inductor, with output cap + load)")
    print(f"   Expected: Node 2 should show low-pass response")
    
    # Run AC analysis
    engine = SimulationEngine()
    
    try:
        print(f"\n🌊 Running AC analysis...")
        ac_results = engine.simulate_ac(
            circuit, 
            start_frequency=1, 
            stop_frequency=100000, 
            points_per_decade=30
        )
        
        print(f"✅ AC simulation successful: {len(ac_results.frequency)} points")
        print(f"   Available nodes: {ac_results.nodes}")
        
        # Analyze each node's response
        frequencies = np.array(ac_results.frequency)
        
        for node in ac_results.nodes:
            if node == 0:
                continue
                
            voltage = ac_results.voltage(node)
            if voltage is not None:
                magnitude = np.abs(voltage)
                phase = np.angle(voltage, deg=True)
                
                print(f"\n📈 Node {node} Analysis:")
                print(f"   Magnitude range: {magnitude.min():.6f} to {magnitude.max():.6f}")
                
                # Check if it's a flat response (input) or has rolloff (output)
                mag_variation = magnitude.max() - magnitude.min()
                print(f"   Magnitude variation: {mag_variation:.6f}")
                
                if mag_variation > 0.1:
                    print(f"   🎯 This node shows frequency response! (good for Bode plot)")
                else:
                    print(f"   📏 This node is flat (input/supply node)")
                
                # Sample key frequencies
                low_freq_idx = 0
                high_freq_idx = -1
                mid_freq_idx = len(frequencies) // 2
                
                print(f"   At {frequencies[low_freq_idx]:.1f} Hz: {magnitude[low_freq_idx]:.6f}")
                print(f"   At {frequencies[mid_freq_idx]:.1f} Hz: {magnitude[mid_freq_idx]:.6f}")
                print(f"   At {frequencies[high_freq_idx]:.1f} Hz: {magnitude[high_freq_idx]:.6f}")
        
        print(f"\n🎯 Recommendation:")
        print(f"   For Pi filter, focus Bode plot on Node 2 (output)")
        print(f"   Node 1 will be flat (it's the input)")
        
    except Exception as e:
        print(f"❌ AC analysis failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_pi_filter_nodes()