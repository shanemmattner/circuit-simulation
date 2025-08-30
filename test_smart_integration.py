#!/usr/bin/env python3
"""
Test the smart KiCad-Spice integration with various component types.
"""

import json
import sys
from pathlib import Path

# Add circuit-simulation to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from circuit_sim.circuit_synth_integration import simulate_from_circuit_synth, CircuitSynthError

def create_test_circuit_with_transistor():
    """Create a test circuit with BJT transistor amplifier."""
    return {
        "name": "BJT_Amplifier",
        "description": "Simple BJT amplifier circuit",
        "components": {
            "Q1": {
                "symbol": "Device:Q_NPN_CBE",
                "ref": "Q1",
                "value": "2N3904",  # Should be found in KiCad-Spice-Library
                "footprint": "Package_TO_SOT_THT:TO-92_Inline"
            },
            "R1": {
                "symbol": "Device:R",
                "ref": "R1", 
                "value": "10k",
                "footprint": "Resistor_SMD:R_0603_1608Metric"
            },
            "R2": {
                "symbol": "Device:R",
                "ref": "R2",
                "value": "1k", 
                "footprint": "Resistor_SMD:R_0603_1608Metric"
            },
            "C1": {
                "symbol": "Device:C",
                "ref": "C1",
                "value": "100nF",
                "footprint": "Capacitor_SMD:C_0603_1608Metric"
            },
            "V1": {
                "symbol": "Device:V",
                "ref": "V1",
                "value": "12V",
                "footprint": ""
            }
        },
        "nets": {
            "VCC": [
                {"component": "V1", "pin": {"number": "1", "name": "+", "type": "power"}},
                {"component": "R1", "pin": {"number": "1", "name": "~", "type": "passive"}}
            ],
            "BASE": [
                {"component": "R1", "pin": {"number": "2", "name": "~", "type": "passive"}},
                {"component": "Q1", "pin": {"number": "2", "name": "B", "type": "input"}}
            ],
            "COLLECTOR": [
                {"component": "Q1", "pin": {"number": "1", "name": "C", "type": "passive"}},
                {"component": "R2", "pin": {"number": "1", "name": "~", "type": "passive"}}
            ],
            "OUTPUT": [
                {"component": "R2", "pin": {"number": "2", "name": "~", "type": "passive"}},
                {"component": "C1", "pin": {"number": "1", "name": "~", "type": "passive"}}
            ],
            "GND": [
                {"component": "V1", "pin": {"number": "2", "name": "-", "type": "power"}},
                {"component": "Q1", "pin": {"number": "3", "name": "E", "type": "passive"}},
                {"component": "C1", "pin": {"number": "2", "name": "~", "type": "passive"}}
            ]
        }
    }

def create_test_circuit_with_diode():
    """Create a test circuit with diode rectifier."""
    return {
        "name": "Diode_Rectifier", 
        "description": "Simple diode rectifier",
        "components": {
            "D1": {
                "symbol": "Device:D",
                "ref": "D1",
                "value": "1N4148",  # Should be found in library
                "footprint": "Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal"
            },
            "R1": {
                "symbol": "Device:R",
                "ref": "R1",
                "value": "1k",
                "footprint": "Resistor_SMD:R_0603_1608Metric"
            },
            "C1": {
                "symbol": "Device:C", 
                "ref": "C1",
                "value": "47uF",
                "footprint": "Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm"
            },
            "V1": {
                "symbol": "Device:V",
                "ref": "V1", 
                "value": "5V",
                "footprint": ""
            }
        },
        "nets": {
            "INPUT": [
                {"component": "V1", "pin": {"number": "1", "name": "+", "type": "power"}},
                {"component": "D1", "pin": {"number": "1", "name": "K", "type": "passive"}}
            ],
            "OUTPUT": [
                {"component": "D1", "pin": {"number": "2", "name": "A", "type": "passive"}}, 
                {"component": "R1", "pin": {"number": "1", "name": "~", "type": "passive"}},
                {"component": "C1", "pin": {"number": "1", "name": "~", "type": "passive"}}
            ],
            "GND": [
                {"component": "V1", "pin": {"number": "2", "name": "-", "type": "power"}},
                {"component": "R1", "pin": {"number": "2", "name": "~", "type": "passive"}},
                {"component": "C1", "pin": {"number": "2", "name": "~", "type": "passive"}}
            ]
        }
    }

def create_test_circuit_unknown_component():
    """Create a test circuit with unknown component to test fallbacks."""
    return {
        "name": "Unknown_Component_Test",
        "description": "Test circuit with unknown component",
        "components": {
            "Q1": {
                "symbol": "Device:Q_NPN_CBE",
                "ref": "Q1",
                "value": "UNKNOWN_TRANSISTOR_XYZ123",  # Should fallback to default
                "footprint": "Package_TO_SOT_THT:TO-92_Inline"
            },
            "R1": {
                "symbol": "Device:R",
                "ref": "R1",
                "value": "1k",
                "footprint": "Resistor_SMD:R_0603_1608Metric" 
            },
            "V1": {
                "symbol": "Device:V",
                "ref": "V1",
                "value": "5V",
                "footprint": ""
            }
        },
        "nets": {
            "VCC": [
                {"component": "V1", "pin": {"number": "1", "name": "+", "type": "power"}},
                {"component": "R1", "pin": {"number": "1", "name": "~", "type": "passive"}}
            ],
            "BASE": [
                {"component": "R1", "pin": {"number": "2", "name": "~", "type": "passive"}},
                {"component": "Q1", "pin": {"number": "2", "name": "B", "type": "input"}}
            ],
            "COLLECTOR": [
                {"component": "Q1", "pin": {"number": "1", "name": "C", "type": "passive"}}
            ],
            "GND": [
                {"component": "V1", "pin": {"number": "2", "name": "-", "type": "power"}},
                {"component": "Q1", "pin": {"number": "3", "name": "E", "type": "passive"}}
            ]
        }
    }

def test_smart_integration():
    """Test smart KiCad-Spice integration with various circuits."""
    print("🧪 Testing Smart KiCad-Spice Integration")
    print("=" * 60)
    
    test_circuits = [
        ("BJT Amplifier (Known Component)", create_test_circuit_with_transistor()),
        ("Diode Rectifier (Known Component)", create_test_circuit_with_diode()),
        ("Unknown Component Fallback", create_test_circuit_unknown_component()),
    ]
    
    results = []
    
    for test_name, circuit_data in test_circuits:
        print(f"\n📋 Testing: {test_name}")
        print("-" * 40)
        
        try:
            # Test the integration
            results_obj = simulate_from_circuit_synth(circuit_data)
            
            print("✅ Integration successful!")
            print("📊 Results:")
            if hasattr(results_obj, 'voltages') and results_obj.voltages:
                for node, voltage_array in results_obj.voltages.items():
                    voltage = voltage_array[0] if len(voltage_array) > 0 else 0.0
                    print(f"   {node}: {voltage:.3f} V")
            
            results.append((test_name, True, None))
            
        except CircuitSynthError as e:
            print(f"❌ Circuit-synth integration error: {e.message}")
            if e.details:
                print("🔍 Error details:")
                for key, value in e.details.items():
                    if key != 'json_data':  # Skip large JSON dump
                        print(f"   {key}: {value}")
            results.append((test_name, False, str(e)))
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            results.append((test_name, False, str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 SMART INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for test_name, success, error in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if error and not success:
            print(f"      Error: {error}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🚀 Smart KiCad-Spice Integration is working!")
        print("   • Component mapping: Intelligent model resolution")
        print("   • Fallback handling: Graceful degradation") 
        print("   • SPICE simulation: End-to-end functionality")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed - needs investigation")
        return False

if __name__ == "__main__":
    import logging
    
    # Enable logging to see mapping details
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    
    success = test_smart_integration()
    sys.exit(0 if success else 1)