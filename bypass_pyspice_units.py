#!/usr/bin/env python3
"""
Bypass PySpice Unit System for AC Analysis

Try to extract complex AC data directly from ngspice before PySpice 
converts it to real-only UnitValue objects.
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_raw_ngspice_extraction():
    """Test if we can get raw complex data from ngspice"""
    print("🔍 Testing Raw NgSpice Complex Data Extraction")
    print("=" * 55)
    
    try:
        from PySpice.Spice.Netlist import Circuit as PySpiceCircuit
        from PySpice.Unit import u_Ohm, u_F
        
        # Create simple RC filter
        circuit = PySpiceCircuit("Raw_Complex_Test")
        circuit.V(1, "input", circuit.gnd, "DC 0 AC 1")
        circuit.R(1, "input", "output", 1000@u_Ohm) 
        circuit.C(1, "output", circuit.gnd, 100e-9@u_F)  # 100nF for clear phase shift
        
        simulator = circuit.simulator(temperature=25, nominal_temperature=25)
        
        print("✅ Circuit and simulator created")
        
        # Access the low-level ngspice interface
        try:
            # Get the NgSpice shared instance 
            ngspice_shared = simulator._ngspice_shared
            print(f"✅ Got NgSpice shared instance: {type(ngspice_shared)}")
            
            # Try to access the raw simulation data before PySpice processes it
            analysis = simulator.ac(start_frequency=10, stop_frequency=1000, number_of_points=10, variation='dec')
            
            print(f"✅ AC analysis completed")
            
            # Check if we can access raw data
            print(f"📊 Analysis attributes: {[attr for attr in dir(analysis) if not attr.startswith('_')]}")
            
            # Check if there's a way to get raw complex data
            if hasattr(analysis, 'nodes'):
                output_waveform = analysis.nodes['output']
                print(f"🌊 Waveform type: {type(output_waveform)}")
                print(f"   Waveform attributes: {[attr for attr in dir(output_waveform) if not attr.startswith('_')]}")
                
                # Check if waveform has raw data access
                if hasattr(output_waveform, 'data'):
                    raw_data = output_waveform.data
                    print(f"   Raw data type: {type(raw_data)}")
                    if hasattr(raw_data, 'dtype'):
                        print(f"   Raw data dtype: {raw_data.dtype}")
                        
                elif hasattr(output_waveform, 'values'):
                    print(f"   Has values attribute")
                    
                # Check the abscissa (should be frequency) 
                if hasattr(output_waveform, 'abscissa'):
                    freq_data = output_waveform.abscissa
                    print(f"   Frequency data type: {type(freq_data)}")
                    
        except Exception as e:
            print(f"❌ Raw data access failed: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ NgSpice raw test failed: {e}")


def test_alternative_ac_extraction():
    """Test alternative methods to extract complex AC data"""
    print(f"\n🧪 Testing Alternative AC Data Extraction")
    print("=" * 50)
    
    try:
        # Maybe we need to configure PySpice differently for complex analysis
        from PySpice.Spice.Netlist import Circuit as PySpiceCircuit
        from PySpice.Unit import u_Ohm, u_F
        
        circuit = PySpiceCircuit("Alternative_AC_Test")
        
        # Try different voltage source configurations
        print("🔧 Testing various AC source configurations:")
        
        configs = [
            ("Standard SPICE", "V1 input 0 ac 1"),
            ("With DC component", "V1 input 0 dc 0 ac 1 0"),  # DC=0, AC=1V, phase=0°
            ("Phase specified", "V1 input 0 ac 1 90"),  # 1V at 90° phase
        ]
        
        for config_name, spice_line in configs:
            print(f"\n   🧪 {config_name}: {spice_line}")
            
            try:
                # Create fresh circuit for each test
                test_circuit = PySpiceCircuit("Test_" + config_name.replace(" ", "_"))
                
                # Add components using raw SPICE
                test_circuit.raw_spice = f"""
{spice_line}
R1 input output 1000
C1 output 0 100n
.ac dec 10 10 1000
"""
                
                simulator = test_circuit.simulator()
                analysis = simulator.ac(start_frequency=10, stop_frequency=1000, number_of_points=10, variation='dec')
                
                # Check if this config gives better results
                output = analysis.nodes['output']
                first_val = output[0]
                
                print(f"      Result: {first_val} (type: {type(first_val)})")
                
                # Check if we can extract complex from the raw SPICE result differently
                if hasattr(first_val, '__complex__'):
                    complex_val = complex(first_val)
                    print(f"      Complex conversion: {complex_val}")
                    if complex_val.imag != 0:
                        print(f"      ✅ SUCCESS! Got non-zero imaginary: {complex_val.imag}")
                        
            except Exception as e:
                print(f"      ❌ Config failed: {e}")
    
    except Exception as e:
        print(f"❌ Alternative extraction test failed: {e}")


if __name__ == "__main__":
    check_ngspice_version()
    test_alternative_ac_extraction()