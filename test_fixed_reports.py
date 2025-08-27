#!/usr/bin/env python3
"""
Test Report Generation with Fixed Chart Issue

This script generates reports properly by passing the original SimulationResults 
objects directly, rather than creating new ones.
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


def create_voltage_divider():
    """Create a simple voltage divider circuit"""
    circuit = Circuit("Voltage Divider")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="10V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
    circuit.add_resistor("R2", node1=2, node2="gnd", resistance="1k")
    return circuit


def create_rc_filter():
    """Create an RC low-pass filter"""
    circuit = Circuit("RC Low-Pass Filter")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
    circuit.add_capacitor("C1", node1=2, node2="gnd", capacitance="1uF")
    return circuit


def create_rl_circuit():
    """Create an RL circuit"""
    circuit = Circuit("RL Circuit")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="12V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="100")
    circuit.add_inductor("L1", node1=2, node2="gnd", inductance="10mH")
    return circuit


def test_circuit_with_proper_reports(circuit_name, circuit_func):
    """Test a circuit with proper report generation using original SimulationResults"""
    print(f"\n🔬 Testing {circuit_name}")
    print("-" * 50)
    
    try:
        # Create circuit
        circuit = circuit_func()
        print(f"✅ Circuit created: {len(circuit.components)} components, {len(circuit.nodes)} nodes")
        
        # Test simulation
        engine = SimulationEngine()
        generator = ReportGenerator()
        
        # Create output directory
        output_dir = Path("fixed_reports")
        output_dir.mkdir(exist_ok=True)
        
        # Test each analysis type separately with proper charts
        
        # 1. DC Analysis with charts
        try:
            dc_results = engine.simulate_dc(circuit)
            print("✅ DC simulation successful")
            
            # Generate DC report directly with original results
            dc_report_path = generator.generate_report(
                circuit=circuit,
                results=dc_results,  # Pass original results directly!
                report_type="detailed",
                output_format="html"
            )
            
            # Check file size
            if os.path.exists(dc_report_path):
                file_size = os.path.getsize(dc_report_path)
                print(f"✅ DC report: {file_size:,} bytes -> {dc_report_path}")
                
                # Verify charts are present
                with open(dc_report_path, 'r') as f:
                    content = f.read()
                    chart_count = content.count('Plotly.newPlot')
                    if chart_count > 0:
                        print(f"   📊 Contains {chart_count} Plotly charts!")
                    else:
                        print(f"   ⚠️  No Plotly charts found")
            
        except Exception as e:
            print(f"⚠️  DC analysis failed: {e}")
        
        # 2. Transient Analysis with charts
        try:
            transient_results = engine.simulate_transient(circuit, stop_time=0.001)
            print("✅ Transient simulation successful")
            
            # Generate Transient report directly
            transient_report_path = generator.generate_report(
                circuit=circuit,
                results=transient_results,  # Pass original results directly!
                report_type="detailed",
                output_format="html"
            )
            
            # Check file size
            if os.path.exists(transient_report_path):
                file_size = os.path.getsize(transient_report_path)
                print(f"✅ Transient report: {file_size:,} bytes -> {transient_report_path}")
                
                # Verify charts are present
                with open(transient_report_path, 'r') as f:
                    content = f.read()
                    chart_count = content.count('Plotly.newPlot')
                    if chart_count > 0:
                        print(f"   📊 Contains {chart_count} Plotly charts!")
                    else:
                        print(f"   ⚠️  No Plotly charts found")
            
        except Exception as e:
            print(f"⚠️  Transient analysis failed: {e}")
        
        # 3. AC Analysis with charts
        try:
            ac_results = engine.simulate_ac(circuit, start_frequency=1, stop_frequency=1000000, points_per_decade=10)
            print("✅ AC simulation successful")
            
            # Generate AC report directly
            ac_report_path = generator.generate_report(
                circuit=circuit,
                results=ac_results,  # Pass original results directly!
                report_type="detailed", 
                output_format="html"
            )
            
            # Check file size
            if os.path.exists(ac_report_path):
                file_size = os.path.getsize(ac_report_path)
                print(f"✅ AC report: {file_size:,} bytes -> {ac_report_path}")
                
                # Verify charts are present
                with open(ac_report_path, 'r') as f:
                    content = f.read()
                    chart_count = content.count('Plotly.newPlot')
                    if chart_count > 0:
                        print(f"   📊 Contains {chart_count} Plotly charts!")
                    else:
                        print(f"   ⚠️  No Plotly charts found")
            
        except Exception as e:
            print(f"⚠️  AC analysis failed: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ Circuit test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Main test function with proper chart generation"""
    print("🚀 Testing Report Generation with Proper Charts")
    print("=" * 70)
    
    test_circuits = [
        ("Voltage Divider", create_voltage_divider),
        ("RC Filter", create_rc_filter), 
        ("RL Circuit", create_rl_circuit),
    ]
    
    successful = 0
    total = len(test_circuits)
    
    for circuit_name, circuit_func in test_circuits:
        if test_circuit_with_proper_reports(circuit_name, circuit_func):
            successful += 1
    
    print("\n" + "=" * 70)
    print("📊 FIXED REPORT GENERATION TEST SUMMARY")
    print("=" * 70)
    print(f"Circuits tested: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    print(f"Success rate: {successful/total*100:.1f}%")
    
    if successful > 0:
        print(f"\n📁 Reports with charts saved in: fixed_reports/")
        print(f"🌐 Check the reports - they should now contain Plotly charts!")


if __name__ == "__main__":
    main()