#!/usr/bin/env python3
"""
Fix PySpice AC Configuration

The current fix isn't working - we're still getting real-only values.
Let me try different PySpice AC configuration approaches.
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_different_pyspice_ac_configs():
    """Test different PySpice AC configuration methods"""
    print("🔧 Testing Different PySpice AC Configurations")
    print("=" * 55)
    
    try:
        from PySpice.Spice.Netlist import Circuit as PySpiceCircuit
        from PySpice.Unit import u_V, u_Ohm, u_F
        
        configs_to_test = [
            {
                "name": "Current Method (String)",
                "config": lambda circuit: circuit.V(1, "input", circuit.gnd, "DC 0 AC 1")
            },
            {
                "name": "PySpice AC Method",  
                "config": lambda circuit: circuit.V(1, "input", circuit.gnd, 1@u_V, ac=1@u_V)
            },
            {
                "name": "Explicit AC Syntax",
                "config": lambda circuit: circuit.V(1, "input", circuit.gnd, "ac 1 0")  # AC magnitude 1V, phase 0°
            },
            {
                "name": "DC + AC Separate",
                "config": lambda circuit: circuit.V(1, "input", circuit.gnd, dc_value=0@u_V, ac_value=1@u_V)
            }
        ]
        
        for config_test in configs_to_test:
            print(f"\n🧪 Testing: {config_test['name']}")
            print("-" * 30)
            
            try:
                # Create RC high-pass filter (should show clear phase shift)
                circuit = PySpiceCircuit("RC_HPF_Test")
                
                # Add voltage source with current config method
                config_test["config"](circuit)
                
                # Add RC high-pass components
                circuit.C(1, "input", "output", 100e-9@u_F)  # 100nF
                circuit.R(1, "output", circuit.gnd, 1600@u_Ohm)  # 1.6k
                
                print("   ✅ Circuit built")
                
                # Run AC analysis
                simulator = circuit.simulator(temperature=25, nominal_temperature=25)
                analysis = simulator.ac(start_frequency=10, stop_frequency=100000, number_of_points=30, variation='dec')
                
                print("   ✅ AC analysis completed")
                
                # Check for complex values
                output_voltage = analysis.nodes['output']
                voltage_array = np.array([complex(v) for v in output_voltage])
                
                # Analyze results
                has_imag = np.any(voltage_array.imag != 0)
                max_imag = np.abs(voltage_array.imag).max()
                phase_range = np.angle(voltage_array, deg=True).max() - np.angle(voltage_array, deg=True).min()
                
                print(f"   📊 Results:")
                print(f"      Has imaginary: {'✅' if has_imag else '❌'}")
                print(f"      Max |imag|: {max_imag:.10f}")
                print(f"      Phase range: {phase_range:.2f}°")
                
                if has_imag and phase_range > 10:
                    print(f"   🎯 SUCCESS! This config gives complex values with phase shift")
                    
                    # Test expected high-pass behavior
                    frequencies = np.array([float(f) for f in analysis.frequency])
                    magnitude = np.abs(voltage_array)
                    phase = np.angle(voltage_array, deg=True)
                    
                    # High-pass should show low frequency attenuation
                    low_freq_mag = magnitude[0]
                    high_freq_mag = magnitude[-1]
                    
                    print(f"      Low freq (10 Hz): {low_freq_mag:.6f}V, {phase[0]:.1f}°")
                    print(f"      High freq (100kHz): {high_freq_mag:.6f}V, {phase[-1]:.1f}°")
                    
                    if high_freq_mag > low_freq_mag * 2:
                        print(f"   ✅ Shows high-pass behavior!")
                    else:
                        print(f"   ⚠️  Magnitude behavior unclear")
                        
                else:
                    print(f"   ❌ Still getting real-only or flat response")
                
            except Exception as e:
                print(f"   ❌ Config failed: {e}")
    
    except ImportError:
        print("❌ PySpice not available")


def test_voltage_source_ac_property():
    """Test setting AC property differently"""
    print(f"\n🔋 Testing Voltage Source AC Property Configuration")
    print("=" * 55)
    
    try:
        from PySpice.Spice.Netlist import Circuit as PySpiceCircuit
        from PySpice.Unit import u_V, u_Ohm, u_F
        
        circuit = PySpiceCircuit("AC_Property_Test")
        
        # Create voltage source
        v_source = circuit.V(1, "input", circuit.gnd, 0@u_V)  # DC = 0V
        
        # Try different ways to set AC property
        methods = [
            ("v_source.ac = 1", lambda: setattr(v_source, 'ac', 1)),
            ("v_source.ac = 1@u_V", lambda: setattr(v_source, 'ac', 1@u_V)),
            ("v_source.parameters['ac'] = 1", lambda: v_source.parameters.update({'ac': 1})),
        ]
        
        for method_name, method_func in methods:
            try:
                print(f"\n🧪 Method: {method_name}")
                
                # Reset and configure
                method_func()
                
                # Add RC components
                circuit.R(1, "input", "output", 1000@u_Ohm)
                circuit.C(1, "output", circuit.gnd, 1e-6@u_F)
                
                print("   ✅ AC property set, circuit complete")
                
            except Exception as e:
                print(f"   ❌ Method failed: {e}")
        
    except Exception as e:
        print(f"❌ Voltage source property test failed: {e}")


if __name__ == "__main__":
    test_different_pyspice_ac_configs()
    test_voltage_source_ac_property()