#!/usr/bin/env python3
"""
Test script to verify circuit type detection is working correctly
"""

from professional_circuit_analysis import ProfessionalAnalyzer

def test_circuit_type_detection():
    analyzer = ProfessionalAnalyzer()

    # Test ESP32 circuit detection
    esp32_circuit = {
        'components': {
            'U1': 'AMS1117-3.3',
            'U2': 'ESP32-C6-MINI-1',
            'C1': '10uF',
            'C2': '22uF',
            'R1': '1k',
            'J1': 'USB_C_Receptacle',
            'D1': 'LED'
        }
    }

    # Test simple RC filter
    rc_filter = {
        'components': {
            'R1': '1k',
            'C1': '100n'
        }
    }

    # Test amplifier circuit
    amplifier = {
        'components': {
            'U1': 'LM358',
            'R1': '10k',
            'R2': '100k',
            'C1': '10n'
        }
    }

    # Test power supply only
    power_supply = {
        'components': {
            'U1': 'AMS1117-3.3',
            'C1': '10uF',
            'C2': '22uF'
        }
    }

    print("🧪 Testing Circuit Type Detection")
    print("=" * 50)

    esp32_type = analyzer._detect_circuit_type(esp32_circuit)
    print(f"ESP32 Board → {esp32_type}")

    rc_type = analyzer._detect_circuit_type(rc_filter)
    print(f"RC Filter → {rc_type}")

    amp_type = analyzer._detect_circuit_type(amplifier)
    print(f"Amplifier → {amp_type}")

    ps_type = analyzer._detect_circuit_type(power_supply)
    print(f"Power Supply → {ps_type}")

    # Test expected results
    assert esp32_type == 'digital_mcu', f"Expected 'digital_mcu', got '{esp32_type}'"
    assert rc_type == 'filter_circuit', f"Expected 'filter_circuit', got '{rc_type}'"
    assert amp_type == 'analog_amplifier', f"Expected 'analog_amplifier', got '{amp_type}'"
    assert ps_type == 'power_supply', f"Expected 'power_supply', got '{ps_type}'"

    print("\n✅ All circuit type detection tests passed!")

if __name__ == "__main__":
    test_circuit_type_detection()