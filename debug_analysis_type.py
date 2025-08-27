#!/usr/bin/env python3
"""
Debug Analysis Type Issue

Check what analysis_type the SimulationResults should have and fix the chart generation.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine


def debug_analysis_type():
    """Debug what analysis_type the real SimulationResults objects have"""
    print("🔍 Debugging Analysis Type Issue")
    print("=" * 50)
    
    # Create a simple circuit
    circuit = Circuit("Debug Circuit")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="5V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
    circuit.add_resistor("R2", node1=2, node2="gnd", resistance="1k")
    
    engine = SimulationEngine()
    
    # Test DC simulation
    print("\n📊 DC Analysis:")
    try:
        dc_results = engine.simulate_dc(circuit)
        print(f"   ✅ Success: {type(dc_results)}")
        print(f"   📋 Attributes: {[attr for attr in dir(dc_results) if not attr.startswith('_')]}")
        print(f"   📊 Analysis type: {getattr(dc_results, 'analysis_type', 'NOT SET')}")
        print(f"   📈 Nodes: {getattr(dc_results, 'nodes', 'NOT SET')}")
        
        # Check methods
        if hasattr(dc_results, 'voltage'):
            print(f"   🔌 Has voltage() method: True")
            for node in dc_results.nodes:
                voltage = dc_results.voltage(node)
                print(f"      Node {node}: {voltage}")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test Transient simulation
    print("\n⏱️  Transient Analysis:")
    try:
        transient_results = engine.simulate_transient(circuit, stop_time=0.001)
        print(f"   ✅ Success: {type(transient_results)}")
        print(f"   📊 Analysis type: {getattr(transient_results, 'analysis_type', 'NOT SET')}")
        print(f"   📈 Nodes: {getattr(transient_results, 'nodes', 'NOT SET')}")
        print(f"   ⏰ Has time data: {hasattr(transient_results, 'time')}")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test AC simulation  
    print("\n🌊 AC Analysis:")
    try:
        ac_results = engine.simulate_ac(circuit, start_frequency=1, stop_frequency=1000000, points_per_decade=10)
        print(f"   ✅ Success: {type(ac_results)}")
        print(f"   📊 Analysis type: {getattr(ac_results, 'analysis_type', 'NOT SET')}")
        print(f"   📈 Nodes: {getattr(ac_results, 'nodes', 'NOT SET')}")
        print(f"   📶 Has frequency data: {hasattr(ac_results, 'frequency')}")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")


if __name__ == "__main__":
    debug_analysis_type()