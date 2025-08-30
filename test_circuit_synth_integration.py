#!/usr/bin/env python3
"""
Test circuit-synth integration with actual circuit-synth JSON.
"""

import json
import sys
from pathlib import Path

# Add circuit-simulation to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from circuit_sim.circuit_synth_integration import simulate_from_circuit_synth, CircuitSynthError

def test_rc_filter_integration():
    """Test RC filter integration with real circuit-synth JSON."""
    print("🧪 Testing circuit-synth integration")
    print("=" * 50)
    
    # Load the actual circuit-synth JSON
    json_path = "submodules/circuit-synth/example_project/circuit-synth/Simple_RC_Filter.json"
    with open(json_path, 'r') as f:
        circuit_data = json.load(f)
    
    print(f"📋 Loaded circuit: {circuit_data['name']}")
    print(f"🧩 Components: {list(circuit_data['components'].keys())}")
    print(f"🌐 Nets: {list(circuit_data['nets'].keys())}")
    
    # Add voltage source for simulation
    circuit_data["components"]["V1"] = {
        "symbol": "Device:V",
        "ref": "V1", 
        "value": "5V",
        "footprint": ""
    }
    
    # Connect voltage source
    circuit_data["nets"]["INPUT"].append({
        "component": "V1", 
        "pin": {"number": "1", "name": "+", "type": "power"}
    })
    circuit_data["nets"]["GND"].append({
        "component": "V1",
        "pin": {"number": "2", "name": "-", "type": "power"}
    })
    
    print("⚡ Added 5V voltage source for simulation")
    
    try:
        print("🔄 Running circuit-synth integration...")
        results = simulate_from_circuit_synth(circuit_data)
        
        print("✅ Integration successful!")
        print("📊 Results:")
        if hasattr(results, 'voltages') and results.voltages:
            for node, voltage_array in results.voltages.items():
                voltage = voltage_array[0] if len(voltage_array) > 0 else 0.0
                print(f"   {node}: {voltage:.3f} V")
        
        return True
        
    except CircuitSynthError as e:
        print(f"❌ Circuit-synth integration error: {e.message}")
        if e.details:
            print("🔍 Error details:")
            for key, value in e.details.items():
                if key != 'json_data':  # Skip large JSON dump
                    print(f"   {key}: {value}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_rc_filter_integration()
    if success:
        print("\n🎯 Integration test PASSED")
        print("✅ Circuit-synth → Circuit-simulation workflow is working!")
    else:
        print("\n❌ Integration test FAILED")
        sys.exit(1)