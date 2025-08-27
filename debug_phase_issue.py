#!/usr/bin/env python3
"""
Debug Phase Issue

RC filters should show phase shift (0° to -90°), but we're getting all zeros.
Let's investigate the complex number extraction and phase calculation.
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine


def debug_complex_data_extraction():
    """Debug if we're getting proper complex numbers from PySpice"""
    print("🔍 Debugging Complex Number Extraction")
    print("=" * 50)
    
    # RC filter should show clear phase shift
    circuit = Circuit("RC Filter Phase Test")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
    circuit.add_capacitor("C1", node1=2, node2="gnd", capacitance="1uF")
    
    engine = SimulationEngine()
    
    # Test AC with specific frequency points where we should see phase shift
    ac_results = engine.simulate_ac(circuit, start_frequency=1, stop_frequency=10000, points_per_decade=20)
    
    print(f"✅ AC simulation complete")
    
    # Check Node 2 (output) complex data in detail
    node2_voltage = ac_results.voltage(2)
    print(f"\n📊 Node 2 Complex Data Analysis:")
    print(f"   Data type: {type(node2_voltage)}")
    print(f"   Array type: {type(np.array(node2_voltage))}")
    print(f"   Is complex: {np.iscomplexobj(node2_voltage)}")
    
    # Convert to numpy array
    voltage_array = np.array(node2_voltage)
    print(f"   Array dtype: {voltage_array.dtype}")
    print(f"   Shape: {voltage_array.shape}")
    
    # Check first few values
    print(f"\n🔬 First 10 Complex Values:")
    for i in range(min(10, len(voltage_array))):
        v = voltage_array[i]
        freq = ac_results.frequency[i]
        mag = abs(v)
        phase = np.angle(v, deg=True)
        print(f"   {freq:6.1f} Hz: {v:12} → |V|={mag:.6f}, ∠={phase:6.2f}°")
    
    # Check if any values have non-zero imaginary parts
    imaginary_parts = voltage_array.imag
    print(f"\n📐 Imaginary Part Analysis:")
    print(f"   Imaginary range: {imaginary_parts.min():.10f} to {imaginary_parts.max():.10f}")
    print(f"   Non-zero imaginary count: {np.count_nonzero(imaginary_parts)}/{len(imaginary_parts)}")
    
    if np.all(imaginary_parts == 0):
        print(f"   ❌ ALL VALUES ARE REAL! This explains zero phase.")
        print(f"   🧪 RC filter should have complex values with phase shift")
    else:
        print(f"   ✅ Some complex values found")
    
    # Expected phase for RC low-pass filter
    R = 1000
    C = 1e-6
    frequencies = np.array(ac_results.frequency)
    
    print(f"\n🎯 Expected Phase for RC Filter:")
    for freq in [1, 10, 100, 1000, 10000]:
        if freq <= frequencies.max():
            omega = 2 * np.pi * freq
            expected_phase = -np.degrees(np.arctan(omega * R * C))
            print(f"   {freq:5} Hz: Expected phase = {expected_phase:6.1f}°")


def test_pyspice_complex_directly():
    """Test if PySpice is returning complex numbers correctly"""
    print(f"\n🧪 Testing PySpice Complex Numbers Directly")
    print("=" * 50)
    
    try:
        from PySpice.Spice.Netlist import Circuit as PySpiceCircuit
        from PySpice.Unit import u_V, u_Ohm, u_F
        
        # Create RC filter directly in PySpice
        circuit = PySpiceCircuit("RC_Complex_Test")
        circuit.V(1, "input", circuit.gnd, "DC 0 AC 1")
        circuit.R(1, "input", "output", 1000@u_Ohm)
        circuit.C(1, "output", circuit.gnd, 1e-6@u_F)
        
        simulator = circuit.simulator(temperature=25, nominal_temperature=25)
        analysis = simulator.ac(start_frequency=1, stop_frequency=10000, number_of_points=20, variation='dec')
        
        print(f"✅ Direct PySpice AC analysis")
        
        # Check the raw PySpice complex data
        output_voltage = analysis.nodes['output']
        input_voltage = analysis.nodes['input']
        
        print(f"\n📊 PySpice Raw Data:")
        print(f"   Output type: {type(output_voltage)}")
        print(f"   Input type: {type(input_voltage)}")
        
        # Convert to complex arrays
        output_array = np.array([complex(v) for v in output_voltage])
        input_array = np.array([complex(v) for v in input_voltage])
        
        print(f"\n🔬 Output Node Analysis:")
        print(f"   First 5 values: {output_array[:5]}")
        print(f"   Real parts: {output_array.real[:5]}")
        print(f"   Imag parts: {output_array.imag[:5]}")
        
        # Calculate phase manually
        phase_manual = np.angle(output_array, deg=True)
        print(f"   Manual phase calc: {phase_manual[:5]}")
        
        print(f"\n🔬 Input Node Analysis:")
        print(f"   First 5 values: {input_array[:5]}")
        print(f"   Real parts: {input_array.real[:5]}")
        print(f"   Imag parts: {input_array.imag[:5]}")
        
        # Check if inputs are all real (they should be for a voltage source)
        if np.all(input_array.imag == 0):
            print(f"   ✅ Input is all real (expected for AC source)")
        
        # Check if output has complex values
        if np.any(output_array.imag != 0):
            print(f"   ✅ Output has complex values (expected for RC filter)")
            print(f"   📐 Phase range: {phase_manual.min():.2f}° to {phase_manual.max():.2f}°")
        else:
            print(f"   ❌ Output is all real (problem!)")
            
    except Exception as e:
        print(f"❌ Direct PySpice test failed: {e}")


if __name__ == "__main__":
    debug_complex_data_extraction()
    test_pyspice_complex_directly()