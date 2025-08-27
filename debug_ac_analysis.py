#!/usr/bin/env python3
"""
Debug AC Analysis Zero Values

This script debugs why AC analysis is showing 0 magnitude and phase in Bode plots.
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine


def debug_ac_analysis():
    """Debug AC analysis data to find why values are zero"""
    print("🔍 Debugging AC Analysis Zero Values")
    print("=" * 50)
    
    # Create RC low-pass filter (should have clear frequency response)
    circuit = Circuit("RC Low-Pass Filter")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="1k") 
    circuit.add_capacitor("C1", node1=2, node2="gnd", capacitance="1uF")
    
    print(f"✅ Created RC filter: R=1kΩ, C=1μF")
    print(f"   Expected cutoff frequency: {1/(2*np.pi*1000*1e-6):.1f} Hz")
    
    engine = SimulationEngine()
    
    # Test AC analysis with detailed debugging
    try:
        print("\n🌊 Running AC analysis...")
        ac_results = engine.simulate_ac(
            circuit, 
            start_frequency=1, 
            stop_frequency=10000,  # 10kHz 
            points_per_decade=20
        )
        
        print(f"✅ AC simulation successful")
        print(f"   Analysis type: {ac_results.analysis_type}")
        print(f"   Nodes available: {ac_results.nodes}")
        
        # Check frequency data
        if hasattr(ac_results, 'frequency') and ac_results.frequency is not None:
            freq = ac_results.frequency
            print(f"   📶 Frequency points: {len(freq)}")
            print(f"   📶 Frequency range: {freq[0]:.1f} Hz to {freq[-1]:.1f} Hz")
            print(f"   📶 Sample frequencies: {freq[:5]}")
        else:
            print("   ❌ No frequency data available")
            
        # Check voltage data for each node
        for node in ac_results.nodes:
            voltage = ac_results.voltage(node)
            print(f"\n   🔌 Node {node}:")
            
            if voltage is not None:
                print(f"      Data type: {type(voltage)}")
                print(f"      Data shape: {np.array(voltage).shape}")
                
                # Check if complex (AC analysis should be complex)
                voltage_array = np.array(voltage)
                if np.iscomplexobj(voltage_array):
                    print(f"      Complex data: ✅")
                    magnitude = np.abs(voltage_array)
                    phase = np.angle(voltage_array, deg=True)
                    
                    print(f"      Magnitude range: {magnitude.min():.6f} to {magnitude.max():.6f}")
                    print(f"      Phase range: {phase.min():.1f}° to {phase.max():.1f}°")
                    
                    # Check for zeros
                    zero_count = np.sum(magnitude == 0)
                    if zero_count > 0:
                        print(f"      ⚠️  Zero magnitude values: {zero_count}/{len(magnitude)}")
                    
                    # Sample values
                    print(f"      First 3 values: {voltage_array[:3]}")
                    print(f"      Magnitudes: {magnitude[:3]}")
                    print(f"      Phases: {phase[:3]}")
                    
                else:
                    print(f"      ❌ Not complex data: {voltage_array[:5]}")
                    
            else:
                print(f"      ❌ No voltage data")
    
    except Exception as e:
        print(f"❌ AC simulation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test with different circuit for comparison
    print("\n" + "=" * 50)
    print("🔬 Testing Simple Resistor Divider for AC")
    print("=" * 50)
    
    simple_circuit = Circuit("Simple Divider")
    simple_circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
    simple_circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
    simple_circuit.add_resistor("R2", node1=2, node2="gnd", resistance="1k")
    
    try:
        print("🌊 Running AC analysis on resistor divider...")
        ac_simple = engine.simulate_ac(simple_circuit, start_frequency=1, stop_frequency=1000, points_per_decade=10)
        
        print(f"✅ Simple circuit AC successful")
        
        for node in ac_simple.nodes:
            if node != 0:  # Skip ground
                voltage = ac_simple.voltage(node)
                if voltage is not None:
                    voltage_array = np.array(voltage)
                    if np.iscomplexobj(voltage_array):
                        magnitude = np.abs(voltage_array)
                        phase = np.angle(voltage_array, deg=True)
                        print(f"   Node {node}: |V| = {magnitude[0]:.3f}, ∠ = {phase[0]:.1f}°")
                        
                        # For resistor divider, we expect magnitude ≈ 0.5 (half voltage)
                        if magnitude[0] > 0.4 and magnitude[0] < 0.6:
                            print(f"      ✅ Expected magnitude for voltage divider")
                        else:
                            print(f"      ⚠️  Unexpected magnitude")
        
    except Exception as e:
        print(f"❌ Simple AC simulation failed: {e}")


if __name__ == "__main__":
    debug_ac_analysis()