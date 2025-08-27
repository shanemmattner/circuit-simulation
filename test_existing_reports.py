#!/usr/bin/env python3
"""
Test Report Generation on Existing Working Examples

This script tests report generation on known-working circuit examples that use circuit_sim.Circuit.
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


def create_rlc_resonant():
    """Create an RLC resonant circuit"""
    circuit = Circuit("RLC Resonant Circuit")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="5V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="10")
    circuit.add_inductor("L1", node1=2, node2=3, inductance="1mH")
    circuit.add_capacitor("C1", node1=3, node2="gnd", capacitance="10nF")
    return circuit


def create_bridge_rectifier():
    """Create a simple bridge rectifier circuit"""
    circuit = Circuit("Bridge Rectifier")
    circuit.add_voltage_source("V1", positive=1, negative=2, dc_value="12V")
    circuit.add_resistor("R1", node1=3, node2="gnd", resistance="1k")
    # Note: Simplified without diodes for basic testing
    circuit.add_resistor("R_bridge", node1=1, node2=3, resistance="1")
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
            
            # Create output directory
            output_dir = Path("test_reports")
            output_dir.mkdir(exist_ok=True)
            
            # Generate different report types
            for report_type in ["detailed", "quick", "executive"]:
                try:
                    report_html = generator.generate_report(
                        circuit=circuit,
                        results=results,
                        report_type=report_type,
                        output_format="html"
                    )
                    
                    # Save report
                    report_path = output_dir / f"{circuit_name.replace(' ', '_')}_{report_type}_report.html"
                    with open(report_path, 'w') as f:
                        f.write(report_html)
                    
                    file_size = len(report_html)
                    print(f"✅ {report_type.title()} report: {file_size:,} bytes -> {report_path}")
                    
                except Exception as e:
                    print(f"❌ {report_type.title()} report failed: {e}")
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
    print("🚀 Testing Report Generation on Working Circuit Examples")
    print("=" * 70)
    
    test_circuits = [
        ("Voltage Divider", create_voltage_divider),
        ("RC Filter", create_rc_filter),
        ("RL Circuit", create_rl_circuit),
        ("RLC Resonant", create_rlc_resonant),
        ("Bridge Rectifier", create_bridge_rectifier),
    ]
    
    successful = 0
    total = len(test_circuits)
    
    for circuit_name, circuit_func in test_circuits:
        if test_circuit_with_reports(circuit_name, circuit_func):
            successful += 1
    
    print("\n" + "=" * 70)
    print("📊 REPORT GENERATION TEST SUMMARY")
    print("=" * 70)
    print(f"Circuits tested: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    print(f"Success rate: {successful/total*100:.1f}%")
    
    if successful > 0:
        print(f"\n📁 Reports saved in: test_reports/")
        print(f"🌐 Open the HTML files in your browser to view the reports!")


if __name__ == "__main__":
    main()