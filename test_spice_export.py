#!/usr/bin/env python3
"""
Test SPICE Export Functionality

This script tests the new to_spice() method we just added to circuit-synth.
"""

import sys
import os
sys.path.insert(0, 'submodules/circuit-synth/src')

try:
    from circuit_synth import circuit, Component, Net
    
    print("✅ Successfully imported circuit-synth")
    
    @circuit(name="test_voltage_divider")
    def voltage_divider():
        """Simple voltage divider for testing SPICE export"""
        # Create components
        r1 = Component(symbol="Device:R", ref="R", value="10k")
        r2 = Component(symbol="Device:R", ref="R", value="10k")
        
        # Create nets
        vin = Net('VIN')
        vout = Net('VOUT') 
        gnd = Net('GND')
        
        # Make connections
        r1[1] += vin
        r1[2] += vout
        r2[1] += vout
        r2[2] += gnd
        
        print("✅ Circuit definition successful")
        return circuit
    
    # Create the circuit
    print("🔧 Creating voltage divider circuit...")
    circuit_obj = voltage_divider()
    
    print(f"Circuit name: {circuit_obj.name}")
    print(f"Number of components: {len(circuit_obj.get_components())}")
    print(f"Number of nets: {len(circuit_obj.get_nets())}")
    
    # Test SPICE export
    print("\n📤 Testing SPICE export...")
    try:
        spice_netlist = circuit_obj.to_spice()
        print("✅ SPICE export successful!")
        
        print("\n📄 Generated SPICE Netlist:")
        print("=" * 50)
        print(spice_netlist)
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ SPICE export failed: {e}")
        import traceback
        traceback.print_exc()

except ImportError as e:
    print(f"❌ Failed to import circuit-synth: {e}")
    print("Make sure you're in the correct directory and circuit-synth is installed")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()