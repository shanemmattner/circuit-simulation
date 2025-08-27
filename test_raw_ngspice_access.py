#!/usr/bin/env python3
"""
Test Raw NgSpice Access

Try to access ngspice data before PySpice converts it to UnitValue objects.
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path for imports  
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_raw_ngspice_data():
    """Test accessing raw ngspice data directly"""
    print("🔍 Testing Raw NgSpice Data Access")
    print("=" * 40)
    
    try:
        from PySpice.Spice.Netlist import Circuit as PySpiceCircuit
        from PySpice.Unit import u_Ohm, u_F
        
        # Create simple RC circuit
        circuit = PySpiceCircuit("Raw_NgSpice_Test")
        circuit.V(1, "input", circuit.gnd, "DC 0 AC 1")
        circuit.R(1, "input", "output", 1000@u_Ohm)
        circuit.C(1, "output", circuit.gnd, 100e-9@u_F)
        
        simulator = circuit.simulator(temperature=25, nominal_temperature=25)
        print("✅ Circuit ready")
        
        # Before running analysis, check if we can access raw ngspice
        if hasattr(simulator, '_ngspice_shared'):
            ngspice = simulator._ngspice_shared
            print(f"✅ NgSpice shared instance: {type(ngspice)}")
            
            # Try to run analysis and capture raw data
            print(f"\n🌊 Running AC analysis with raw data capture...")
            
            # Run the analysis
            analysis = simulator.ac(start_frequency=10, stop_frequency=1000, number_of_points=10, variation='dec')
            
            # Check if the analysis object has raw data access
            print(f"📊 Analysis type: {type(analysis)}")
            
            # Try different approaches to get raw complex data
            approaches = [
                ("analysis._data", lambda: getattr(analysis, '_data', None)),
                ("analysis.data", lambda: getattr(analysis, 'data', None)), 
                ("ngspice.vector_data", lambda: getattr(ngspice, 'vector_data', None)),
                ("simulator._data", lambda: getattr(simulator, '_data', None)),
            ]
            
            for approach_name, approach_func in approaches:
                try:
                    raw_data = approach_func()
                    if raw_data is not None:
                        print(f"   ✅ {approach_name}: {type(raw_data)}")
                        
                        # If it's a dict or has keys, explore
                        if hasattr(raw_data, 'keys'):
                            print(f"      Keys: {list(raw_data.keys())[:5]}")
                        elif hasattr(raw_data, '__len__'):
                            print(f"      Length: {len(raw_data)}")
                            
                    else:
                        print(f"   ❌ {approach_name}: None")
                        
                except Exception as e:
                    print(f"   ❌ {approach_name}: {e}")
            
            # Check the analysis result structure more deeply
            print(f"\n🔬 Deep Analysis Structure:")
            for attr in ['nodes', 'branches', 'frequency']:
                if hasattr(analysis, attr):
                    obj = getattr(analysis, attr)
                    print(f"   {attr}: {type(obj)}")
                    
                    if attr == 'nodes' and hasattr(obj, 'keys'):
                        for node_name in list(obj.keys())[:2]:
                            node_data = obj[node_name]
                            print(f"      {node_name}: {type(node_data)}")
                            
                            # Check if node data has attributes we haven't explored
                            node_attrs = [a for a in dir(node_data) if not a.startswith('_')]
                            print(f"         Attributes: {node_attrs[:5]}")
                            
        else:
            print("❌ No ngspice shared instance accessible")
            
    except Exception as e:
        print(f"❌ Raw ngspice test failed: {e}")
        import traceback
        traceback.print_exc()


def research_pyspice_ac_limitations():
    """Research PySpice AC analysis limitations"""
    print(f"\n📚 PySpice AC Analysis Research")
    print("=" * 35)
    
    print("🔍 Known PySpice AC Issues:")
    print("   1. UnitValue class converts complex → real (Unit.py:892)")
    print("   2. AC analysis designed for magnitude-only in many PySpice examples")
    print("   3. Complex number support may be incomplete")
    
    print(f"\n🎯 Potential Solutions:")
    print("   1. Override result extraction to preserve complex data")
    print("   2. Patch PySpice UnitValue to handle complex numbers")
    print("   3. Use raw ngspice interface directly") 
    print("   4. Switch to different Python SPICE library")
    
    print(f"\n💡 Immediate Next Steps:")
    print("   1. Check if PySpice has AC complex result examples")
    print("   2. Look for PySpice configuration options for complex preservation")
    print("   3. Consider creating custom result extraction method")


if __name__ == "__main__":
    test_raw_ngspice_data()
    research_pyspice_ac_limitations()