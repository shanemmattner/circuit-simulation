#!/usr/bin/env python3
"""
Create a simple demo circuit for circuit-synth → circuit-simulation integration.
This bypasses the need for circuit-synth dependencies.
"""

import json
from pathlib import Path


def create_voltage_divider_circuit():
    """Create a simple voltage divider circuit."""
    return {
        "name": "Voltage_Divider_Demo",
        "description": "Simple voltage divider circuit for circuit-synth integration demo",
        "components": {
            "V1": {
                "symbol": "Device:V",
                "ref": "V1",
                "value": "12V",
                "footprint": "TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm",
                "description": "12V DC power supply"
            },
            "R1": {
                "symbol": "Device:R", 
                "ref": "R1",
                "value": "1k",
                "footprint": "Resistor_SMD:R_0603_1608Metric",
                "description": "1kΩ resistor"
            },
            "R2": {
                "symbol": "Device:R",
                "ref": "R2", 
                "value": "2k",
                "footprint": "Resistor_SMD:R_0603_1608Metric",
                "description": "2kΩ resistor"
            }
        },
        "nets": {
            "VIN": [
                {
                    "component": "V1",
                    "pin": {
                        "number": "1",
                        "name": "+",
                        "type": "passive"
                    }
                },
                {
                    "component": "R1", 
                    "pin": {
                        "number": "1",
                        "name": "~",
                        "type": "passive"
                    }
                }
            ],
            "VOUT": [
                {
                    "component": "R1",
                    "pin": {
                        "number": "2", 
                        "name": "~",
                        "type": "passive"
                    }
                },
                {
                    "component": "R2",
                    "pin": {
                        "number": "1",
                        "name": "~", 
                        "type": "passive"
                    }
                }
            ],
            "GND": [
                {
                    "component": "V1",
                    "pin": {
                        "number": "2",
                        "name": "-",
                        "type": "passive" 
                    }
                },
                {
                    "component": "R2",
                    "pin": {
                        "number": "2",
                        "name": "~",
                        "type": "passive"
                    }
                }
            ]
        }
    }


def create_rc_filter_circuit():
    """Create an RC low-pass filter circuit."""
    return {
        "name": "RC_Filter_Demo",
        "description": "RC low-pass filter circuit for frequency analysis",
        "components": {
            "V1": {
                "symbol": "Device:V",
                "ref": "V1",
                "value": "5V",
                "footprint": "TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm",
                "description": "5V AC signal source"
            },
            "R1": {
                "symbol": "Device:R", 
                "ref": "R1",
                "value": "1k",
                "footprint": "Resistor_SMD:R_0603_1608Metric",
                "description": "1kΩ series resistor"
            },
            "C1": {
                "symbol": "Device:C",
                "ref": "C1", 
                "value": "100nF",
                "footprint": "Capacitor_SMD:C_0603_1608Metric",
                "description": "100nF filter capacitor"
            }
        },
        "nets": {
            "INPUT": [
                {
                    "component": "V1",
                    "pin": {
                        "number": "1",
                        "name": "+",
                        "type": "passive"
                    }
                },
                {
                    "component": "R1", 
                    "pin": {
                        "number": "1",
                        "name": "~",
                        "type": "passive"
                    }
                }
            ],
            "OUTPUT": [
                {
                    "component": "R1",
                    "pin": {
                        "number": "2", 
                        "name": "~",
                        "type": "passive"
                    }
                },
                {
                    "component": "C1",
                    "pin": {
                        "number": "1",
                        "name": "~", 
                        "type": "passive"
                    }
                }
            ],
            "GND": [
                {
                    "component": "V1",
                    "pin": {
                        "number": "2",
                        "name": "-",
                        "type": "passive" 
                    }
                },
                {
                    "component": "C1",
                    "pin": {
                        "number": "2",
                        "name": "~",
                        "type": "passive"
                    }
                }
            ]
        }
    }


def main():
    """Create demo circuits for testing."""
    print("🔧 Creating demo circuits for circuit-synth integration...")
    print()
    
    # Create voltage divider
    voltage_divider = create_voltage_divider_circuit()
    with open("Voltage_Divider_Demo.json", "w") as f:
        json.dump(voltage_divider, f, indent=2)
    print("✅ Created: Voltage_Divider_Demo.json")
    print("   • 12V input, 1kΩ + 2kΩ voltage divider")
    print("   • Expected VOUT: 8V (12V × 2kΩ/(1kΩ+2kΩ))")
    print()
    
    # Create RC filter
    rc_filter = create_rc_filter_circuit()
    with open("RC_Filter_Demo.json", "w") as f:
        json.dump(rc_filter, f, indent=2)
    print("✅ Created: RC_Filter_Demo.json") 
    print("   • 5V input, 1kΩ resistor, 100nF capacitor")
    print("   • Low-pass filter, cutoff ≈ 1.6kHz")
    print()
    
    print("🚀 Ready to test! Run:")
    print("   uv run python demo_circuit_synth_with_plots.py Voltage_Divider_Demo.json")
    print("   or")
    print("   uv run python demo_circuit_synth_with_plots.py RC_Filter_Demo.json")


if __name__ == "__main__":
    main()