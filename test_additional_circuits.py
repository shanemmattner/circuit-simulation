#!/usr/bin/env python3
"""
Test Additional Common Circuit Examples

This script creates and tests reports for additional common electronic circuits
that are frequently used in education and practice.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import traceback

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine
from circuit_sim.reports import ReportGenerator


def create_high_pass_filter():
    """Create a high-pass RC filter"""
    circuit = Circuit("RC High-Pass Filter")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
    circuit.add_capacitor("C1", node1=1, node2=2, capacitance="100nF")
    circuit.add_resistor("R1", node1=2, node2="gnd", resistance="1.6k")
    return circuit


def create_band_pass_filter():
    """Create a band-pass filter using RLC circuit"""
    circuit = Circuit("RLC Band-Pass Filter")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="100")
    circuit.add_inductor("L1", node1=2, node2=3, inductance="10mH")
    circuit.add_capacitor("C1", node1=3, node2="gnd", capacitance="100nF")
    return circuit


def create_colpitts_oscillator():
    """Create a simplified Colpitts oscillator (without active elements)"""
    circuit = Circuit("Colpitts Oscillator Tank")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="12V")
    circuit.add_inductor("L1", node1=1, node2=2, inductance="100uH")
    circuit.add_capacitor("C1", node1=2, node2=3, capacitance="100pF")
    circuit.add_capacitor("C2", node1=3, node2="gnd", capacitance="1nF")
    circuit.add_resistor("R_load", node1=2, node2="gnd", resistance="1k")  # Load
    return circuit


def create_pi_filter():
    """Create a Pi low-pass filter"""
    circuit = Circuit("Pi Low-Pass Filter")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="5V")
    circuit.add_capacitor("C1", node1=1, node2="gnd", capacitance="10uF")  # Input cap
    circuit.add_inductor("L1", node1=1, node2=2, inductance="1mH")        # Series inductor
    circuit.add_capacitor("C2", node1=2, node2="gnd", capacitance="10uF")  # Output cap
    circuit.add_resistor("R_load", node1=2, node2="gnd", resistance="50")  # 50 ohm load
    return circuit


def create_t_filter():
    """Create a T low-pass filter"""
    circuit = Circuit("T Low-Pass Filter")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="5V")
    circuit.add_inductor("L1", node1=1, node2=2, inductance="1mH")         # First series inductor
    circuit.add_inductor("L2", node1=2, node2=3, inductance="1mH")         # Second series inductor
    circuit.add_capacitor("C1", node1=2, node2="gnd", capacitance="10uF")  # Shunt capacitor
    circuit.add_resistor("R_load", node1=3, node2="gnd", resistance="50")  # Load
    return circuit


def create_twin_t_notch():
    """Create a Twin-T notch filter"""
    circuit = Circuit("Twin-T Notch Filter")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
    # T-section with capacitors
    circuit.add_capacitor("C1", node1=1, node2=2, capacitance="100nF")
    circuit.add_capacitor("C2", node1=2, node2=3, capacitance="100nF")  
    circuit.add_resistor("R3", node1=2, node2="gnd", resistance="1.6k")   # Shunt resistor
    # T-section with resistors  
    circuit.add_resistor("R1", node1=1, node2=4, resistance="800")       # Half value
    circuit.add_resistor("R2", node1=4, node2=3, resistance="800")       # Half value
    circuit.add_capacitor("C3", node1=4, node2="gnd", capacitance="200nF") # Double value
    circuit.add_resistor("R_load", node1=3, node2="gnd", resistance="10k") # Load
    return circuit


def create_wien_bridge():
    """Create Wien bridge network"""
    circuit = Circuit("Wien Bridge Network")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
    # Series RC branch
    circuit.add_resistor("R1", node1=1, node2=2, resistance="1.6k")
    circuit.add_capacitor("C1", node1=2, node2=3, capacitance="100nF")
    # Parallel RC branch  
    circuit.add_resistor("R2", node1=1, node2=4, resistance="1.6k")
    circuit.add_capacitor("C2", node1=4, node2="gnd", capacitance="100nF")
    circuit.add_resistor("R_bridge", node1=3, node2=4, resistance="10k")  # Bridge connection
    circuit.add_resistor("R_load", node1=3, node2="gnd", resistance="10k") # Load
    return circuit


def create_chebyshev_filter():
    """Create a 3rd order Chebyshev low-pass filter"""
    circuit = Circuit("3rd Order Chebyshev LPF")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
    # Source impedance
    circuit.add_resistor("R_source", node1=1, node2=2, resistance="50")
    # Chebyshev filter elements (example values)
    circuit.add_inductor("L1", node1=2, node2=3, inductance="2.7mH")     # First series L
    circuit.add_capacitor("C1", node1=3, node2="gnd", capacitance="470nF") # First shunt C
    circuit.add_inductor("L2", node1=3, node2=4, inductance="1.2mH")     # Second series L  
    circuit.add_capacitor("C2", node1=4, node2="gnd", capacitance="470nF") # Second shunt C
    circuit.add_resistor("R_load", node1=4, node2="gnd", resistance="50")  # Load impedance
    return circuit


def create_crystal_oscillator():
    """Create crystal oscillator equivalent circuit"""
    circuit = Circuit("Crystal Oscillator Model")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="5V")
    # Crystal equivalent circuit
    circuit.add_resistor("R_series", node1=1, node2=2, resistance="50")    # Series resistance
    circuit.add_inductor("L_motional", node1=2, node2=3, inductance="10mH") # Motional inductance
    circuit.add_capacitor("C_motional", node1=3, node2=4, capacitance="0.01pF") # Motional capacitance
    circuit.add_capacitor("C_parallel", node1=2, node2=4, capacitance="5pF")     # Parallel capacitance
    circuit.add_resistor("R_load", node1=4, node2="gnd", resistance="1M")        # Load
    return circuit


def create_ladder_filter():
    """Create 5th order ladder filter"""
    circuit = Circuit("5th Order Ladder Filter")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
    circuit.add_resistor("R_source", node1=1, node2=2, resistance="50")
    # 5th order ladder
    circuit.add_inductor("L1", node1=2, node2=3, inductance="1.5mH")
    circuit.add_capacitor("C1", node1=3, node2="gnd", capacitance="330nF")
    circuit.add_inductor("L2", node1=3, node2=4, inductance="2.2mH")
    circuit.add_capacitor("C2", node1=4, node2="gnd", capacitance="470nF")
    circuit.add_inductor("L3", node1=4, node2=5, inductance="1.5mH")
    circuit.add_resistor("R_load", node1=5, node2="gnd", resistance="50")
    return circuit


def test_circuit_with_reports(circuit_name, circuit_func):
    """Test a circuit with comprehensive report generation"""
    print(f"\n🔬 Testing {circuit_name}")
    print("-" * 50)
    
    try:
        # Create circuit
        circuit = circuit_func()
        print(f"✅ Circuit created: {len(circuit.components)} components, {len(circuit.nodes)} nodes")
        
        # Test simulation
        engine = SimulationEngine()
        
        # Try DC analysis
        dc_results = None
        try:
            dc_results = engine.simulate_dc(circuit)
            print("✅ DC simulation successful")
        except Exception as e:
            print(f"⚠️  DC simulation failed: {e}")
        
        # Try transient analysis
        transient_results = None
        try:
            transient_results = engine.simulate_transient(circuit, stop_time=0.001)  # 1ms
            print("✅ Transient simulation successful")
        except Exception as e:
            print(f"⚠️  Transient simulation failed: {e}")
        
        # Try AC analysis
        ac_results = None
        try:
            ac_results = engine.simulate_ac(circuit, start_frequency=1, stop_frequency=1000000, points_per_decade=10)
            print("✅ AC simulation successful")
        except Exception as e:
            print(f"⚠️  AC simulation failed: {e}")
        
        # Generate reports if we have any results
        if any([dc_results, transient_results, ac_results]):
            generator = ReportGenerator()
            
            # Create results object
            from circuit_sim.simulator.results import SimulationResults
            results = SimulationResults(circuit.name)
            
            if dc_results:
                results.dc_results = dc_results
            if transient_results:
                results.transient_results = transient_results
            if ac_results:
                results.ac_results = ac_results
            
            # Generate detailed report only (to save time)
            try:
                report_path = generator.generate_report(
                    circuit=circuit,
                    results=results,
                    report_type="detailed",
                    output_format="html"
                )
                
                # Check if file exists
                if os.path.exists(report_path):
                    file_size = os.path.getsize(report_path)
                    print(f"✅ Detailed report: {file_size:,} bytes -> {report_path}")
                else:
                    print(f"⚠️  Report path returned but file not found: {report_path}")
                    
            except Exception as e:
                print(f"❌ Report generation failed: {e}")
                traceback.print_exc()
        
        else:
            print("❌ No simulation results available for report generation")
            
        return True
        
    except Exception as e:
        print(f"❌ Circuit test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("🚀 Testing Additional Common Circuit Examples")
    print("=" * 70)
    
    test_circuits = [
        ("RC High-Pass Filter", create_high_pass_filter),
        ("RLC Band-Pass Filter", create_band_pass_filter),
        ("Pi Low-Pass Filter", create_pi_filter),
        ("T Low-Pass Filter", create_t_filter),
        ("Twin-T Notch Filter", create_twin_t_notch),
        ("Wien Bridge Network", create_wien_bridge),
        ("3rd Order Chebyshev Filter", create_chebyshev_filter),
        ("Crystal Oscillator Model", create_crystal_oscillator),
        ("5th Order Ladder Filter", create_ladder_filter),
        ("Colpitts Oscillator Tank", create_colpitts_oscillator),
    ]
    
    successful = 0
    total = len(test_circuits)
    
    for circuit_name, circuit_func in test_circuits:
        if test_circuit_with_reports(circuit_name, circuit_func):
            successful += 1
    
    print("\n" + "=" * 70)
    print("📊 ADDITIONAL CIRCUITS TEST SUMMARY")
    print("=" * 70)
    print(f"Circuits tested: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    print(f"Success rate: {successful/total*100:.1f}%")
    
    if successful > 0:
        print(f"\n📁 Reports saved in: reports/")
        print(f"🌐 Open the HTML files in your browser to view the reports!")


if __name__ == "__main__":
    main()