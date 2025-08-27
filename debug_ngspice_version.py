#!/usr/bin/env python3
"""
Debug NgSpice Version and Complex Number Extraction

The warning "Casting complex values to real discards the imaginary part" suggests
PySpice is converting complex values to real. Let's investigate this.
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))


def check_ngspice_version():
    """Check ngspice version and configuration"""
    print("🔍 NgSpice Version and Configuration Check")
    print("=" * 50)
    
    try:
        from PySpice.Spice.NgSpice.Shared import NgSpiceShared
        
        # Get ngspice instance
        ngspice = NgSpiceShared.new_instance()
        
        print("✅ NgSpice instance created")
        
        # Check version
        try:
            # Try to get version info
            print("📋 NgSpice Information:")
            print(f"   NgSpice available: {NgSpiceShared.ngspice_id()}")
            
        except Exception as e:
            print(f"   ⚠️  Version check failed: {e}")
            
        # Check if ngspice supports complex numbers properly
        print(f"\n🧪 Testing NgSpice Complex Number Support")
        
        # Create simple AC circuit directly with ngspice
        test_netlist = [
            "AC Test Circuit",
            "V1 input 0 DC 0 AC 1",  # 1V AC source
            "R1 input output 1000",
            "C1 output 0 100n",
            ".ac dec 10 1 1000",
            ".print ac v(output)",
            ".end"
        ]
        
        # Try running this netlist directly
        for line in test_netlist:
            print(f"   {line}")
            
    except ImportError as e:
        print(f"❌ NgSpice import failed: {e}")
    except Exception as e:
        print(f"❌ NgSpice test failed: {e}")


def test_pyspice_extraction_issue():
    """Test if the issue is in PySpice result extraction"""
    print(f"\n🔍 Testing PySpice Result Extraction")
    print("=" * 45)
    
    try:
        from PySpice.Spice.Netlist import Circuit as PySpiceCircuit
        from PySpice.Unit import u_V, u_Ohm, u_F
        
        # Create circuit with explicit complex test
        circuit = PySpiceCircuit("Complex_Extraction_Test")
        
        # Use raw SPICE syntax that definitely works
        circuit.raw_spice = """
V1 input 0 DC 0 AC 1
R1 input output 1000
C1 output 0 100n
.ac dec 20 1 10000
"""
        
        print("✅ Circuit with raw SPICE syntax")
        print("   Using explicit ngspice syntax that should work")
        
        simulator = circuit.simulator(temperature=25, nominal_temperature=25)
        
        try:
            analysis = simulator.ac(start_frequency=1, stop_frequency=10000, number_of_points=20, variation='dec')
            print("✅ AC analysis completed")
            
            # Check raw analysis object
            print(f"📊 Analysis object type: {type(analysis)}")
            print(f"   Nodes available: {list(analysis.nodes.keys())}")
            
            if 'output' in analysis.nodes:
                output = analysis.nodes['output']
                print(f"   Output type: {type(output)}")
                print(f"   Output length: {len(output)}")
                
                # Check the actual raw data before any conversion
                raw_first_value = output[0]
                print(f"   First raw value: {raw_first_value} (type: {type(raw_first_value)})")
                
                # Check if the raw value is complex
                if hasattr(raw_first_value, 'real') and hasattr(raw_first_value, 'imag'):
                    print(f"   Raw value real part: {raw_first_value.real}")
                    print(f"   Raw value imag part: {raw_first_value.imag}")
                    
                    if raw_first_value.imag != 0:
                        print("   ✅ Raw ngspice data IS complex!")
                    else:
                        print("   ❌ Raw ngspice data is real-only")
                else:
                    print("   ❌ Raw value doesn't have real/imag attributes")
                
                # Test manual conversion
                print(f"\n🔄 Testing manual complex conversion:")
                try:
                    manual_complex = [complex(v) for v in output[:3]]
                    print(f"   Manual conversion: {manual_complex}")
                    
                    phases = [np.angle(v, deg=True) for v in manual_complex]
                    print(f"   Manual phases: {phases}")
                    
                except Exception as e:
                    print(f"   ❌ Manual conversion failed: {e}")
                
        except Exception as e:
            print(f"❌ AC analysis failed: {e}")
            
    except Exception as e:
        print(f"❌ PySpice test failed: {e}")
        import traceback
        traceback.print_exc()


def check_pyspice_unit_conversion():
    """Check if PySpice unit conversion is causing the issue"""
    print(f"\n🔍 Checking PySpice Unit Conversion")
    print("=" * 40)
    
    try:
        from PySpice.Unit import u_V
        
        # The warning message suggests unit conversion issue
        print("⚠️  Warning seen: 'Casting complex values to real discards the imaginary part'")
        print("   This happens in PySpice unit handling")
        
        # Check if this is related to the @ operator usage
        test_value = 1.5 + 0.5j  # Complex number
        
        print(f"Original complex: {test_value}")
        
        try:
            unit_value = test_value @ u_V
            print(f"After @ u_V: {unit_value} (type: {type(unit_value)})")
            
            # Check if conversion preserves complex nature
            if hasattr(unit_value, 'value'):
                print(f"Unit value: {unit_value.value} (type: {type(unit_value.value)})")
        except Exception as e:
            print(f"Unit conversion test failed: {e}")
    
    except Exception as e:
        print(f"❌ Unit test failed: {e}")


if __name__ == "__main__":
    check_ngspice_version()
    test_pyspice_extraction_issue()
    check_pyspice_unit_conversion()