#!/usr/bin/env python3
"""
Debug PySpice AC Source Configuration

This script tests AC voltage source configuration directly in PySpice to understand
why we're getting zero values.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_pyspice_ac_directly():
    """Test PySpice AC analysis directly to isolate the issue"""
    print("🔍 Testing PySpice AC Source Configuration")
    print("=" * 50)
    
    try:
        from PySpice.Spice.Netlist import Circuit
        from PySpice.Unit import u_V, u_Ohm, u_F
        
        print("✅ PySpice imported successfully")
        
        # Create a simple RC low-pass filter directly in PySpice
        circuit = Circuit("RC_Filter_Test")
        
        # Add components with proper AC source
        voltage_source = circuit.V(1, "input", circuit.gnd, 1@u_V)
        
        # Try different ways to set AC magnitude
        print(f"🔍 Testing AC source configuration...")
        
        # Method 1: Set ac property
        voltage_source.ac = 1.0
        print(f"   Method 1: voltage_source.ac = 1.0")
        
        # Add R and C
        circuit.R(1, "input", "output", 1000@u_Ohm)
        circuit.C(1, "output", circuit.gnd, 1e-6@u_F)
        
        print(f"✅ Circuit built with R=1kΩ, C=1μF")
        
        # Create simulator
        simulator = circuit.simulator(temperature=25, nominal_temperature=25)
        print(f"✅ Simulator created")
        
        # Run AC analysis
        print(f"🌊 Running AC analysis...")
        analysis = simulator.ac(start_frequency=1, stop_frequency=10000, number_of_points=20, variation='dec')
        
        print(f"✅ AC analysis completed")
        print(f"   Nodes available: {list(analysis.nodes.keys())}")
        print(f"   Frequencies: {len(analysis.frequency)} points")
        print(f"   Frequency range: {float(analysis.frequency[0]):.1f} to {float(analysis.frequency[-1]):.1f} Hz")
        
        # Check voltage results
        for node_name, voltage_data in analysis.nodes.items():
            print(f"\n   🔌 {node_name}:")
            
            voltage_array = list(voltage_data)[:5]  # First 5 points
            print(f"      First 5 values: {voltage_array}")
            
            # Calculate magnitude and phase
            import numpy as np
            voltage_np = np.array(voltage_data)
            magnitude = np.abs(voltage_np)
            phase = np.angle(voltage_np, deg=True)
            
            print(f"      Magnitude range: {magnitude.min():.6f} to {magnitude.max():.6f}")
            print(f"      Phase range: {phase.min():.1f}° to {phase.max():.1f}°")
            
            # Check specific frequencies
            cutoff_freq = 159.2  # Expected cutoff for 1kΩ, 1μF
            freq_array = np.array([float(f) for f in analysis.frequency])
            
            # Find closest frequency to cutoff
            cutoff_idx = np.argmin(np.abs(freq_array - cutoff_freq))
            print(f"      At ~{freq_array[cutoff_idx]:.1f} Hz: |V| = {magnitude[cutoff_idx]:.3f}, ∠ = {phase[cutoff_idx]:.1f}°")
    
    except ImportError as e:
        print(f"❌ PySpice import failed: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


def test_alternative_ac_configuration():
    """Test alternative AC configuration methods"""
    print("\n🧪 Testing Alternative AC Source Configuration")
    print("=" * 50)
    
    try:
        from PySpice.Spice.Netlist import Circuit
        from PySpice.Unit import u_V, u_Ohm, u_F
        
        # Method 2: Create voltage source with explicit AC parameters
        circuit = Circuit("RC_Filter_Test_v2")
        
        # Try adding voltage source with explicit AC declaration
        circuit.V('input', 'input', circuit.gnd, 'DC 0 AC 1')  # SPICE syntax
        circuit.R(1, "input", "output", 1000@u_Ohm)
        circuit.C(1, "output", circuit.gnd, 1e-6@u_F)
        
        print("✅ Circuit with explicit DC 0 AC 1 syntax")
        
        simulator = circuit.simulator(temperature=25, nominal_temperature=25)
        analysis = simulator.ac(start_frequency=1, stop_frequency=10000, number_of_points=20, variation='dec')
        
        print(f"✅ AC analysis completed")
        
        # Check results
        for node_name, voltage_data in analysis.nodes.items():
            voltage_array = list(voltage_data)[:3]
            print(f"   {node_name}: {voltage_array}")
            
            import numpy as np
            magnitude = np.abs(np.array(voltage_data))
            if magnitude.max() > 0:
                print(f"   ✅ Non-zero values found! Max magnitude: {magnitude.max():.3f}")
            else:
                print(f"   ❌ Still getting zeros")
                
    except Exception as e:
        print(f"❌ Alternative test failed: {e}")


if __name__ == "__main__":
    test_pyspice_ac_directly()
    test_alternative_ac_configuration()