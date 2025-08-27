#!/usr/bin/env python3
"""
Generate All Circuit Reports with Working Charts

This script generates comprehensive reports for all circuit examples with working Plotly charts.
"""

import os
import sys
from pathlib import Path
import traceback

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine
from circuit_sim.reports import ReportGenerator


# Basic Circuits
def create_voltage_divider():
    circuit = Circuit("Voltage Divider")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="10V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
    circuit.add_resistor("R2", node1=2, node2="gnd", resistance="1k")
    return circuit

def create_rc_lowpass():
    circuit = Circuit("RC Low-Pass Filter")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
    circuit.add_capacitor("C1", node1=2, node2="gnd", capacitance="1uF")
    return circuit

def create_rc_highpass():
    circuit = Circuit("RC High-Pass Filter")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
    circuit.add_capacitor("C1", node1=1, node2=2, capacitance="100nF")
    circuit.add_resistor("R1", node1=2, node2="gnd", resistance="1.6k")
    return circuit

def create_rl_circuit():
    circuit = Circuit("RL Circuit")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="12V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="100")
    circuit.add_inductor("L1", node1=2, node2="gnd", inductance="10mH")
    return circuit

# Advanced Filters
def create_rlc_resonant():
    circuit = Circuit("RLC Resonant Circuit")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="5V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="10")
    circuit.add_inductor("L1", node1=2, node2=3, inductance="1mH")
    circuit.add_capacitor("C1", node1=3, node2="gnd", capacitance="10nF")
    return circuit

def create_pi_filter():
    circuit = Circuit("Pi Low-Pass Filter")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="5V")
    circuit.add_capacitor("C1", node1=1, node2="gnd", capacitance="10uF")
    circuit.add_inductor("L1", node1=1, node2=2, inductance="1mH")
    circuit.add_capacitor("C2", node1=2, node2="gnd", capacitance="10uF")
    circuit.add_resistor("R_load", node1=2, node2="gnd", resistance="50")
    return circuit

def create_wien_bridge():
    circuit = Circuit("Wien Bridge Network")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="1.6k")
    circuit.add_capacitor("C1", node1=2, node2=3, capacitance="100nF")
    circuit.add_resistor("R2", node1=1, node2=4, resistance="1.6k")
    circuit.add_capacitor("C2", node1=4, node2="gnd", capacitance="100nF")
    circuit.add_resistor("R_bridge", node1=3, node2=4, resistance="10k")
    circuit.add_resistor("R_load", node1=3, node2="gnd", resistance="10k")
    return circuit


def generate_comprehensive_reports(circuit_name, circuit_func):
    """Generate comprehensive reports for a circuit across all analysis types"""
    print(f"\n🔬 Generating Reports for {circuit_name}")
    print("-" * 50)
    
    try:
        circuit = circuit_func()
        print(f"✅ Circuit: {len(circuit.components)} components, {len(circuit.nodes)} nodes")
        
        engine = SimulationEngine()
        generator = ReportGenerator()
        
        report_summary = {"circuit": circuit_name, "reports": []}
        
        # Generate reports for each analysis type
        analysis_types = [
            ("DC", lambda: engine.simulate_dc(circuit)),
            ("Transient", lambda: engine.simulate_transient(circuit, stop_time=0.001)),  
            ("AC", lambda: engine.simulate_ac(circuit, start_frequency=1, stop_frequency=100000, points_per_decade=20))
        ]
        
        for analysis_name, simulate_func in analysis_types:
            try:
                print(f"   🔄 Running {analysis_name} simulation...")
                results = simulate_func()
                
                # Generate detailed report
                report_path = generator.generate_report(
                    circuit=circuit,
                    results=results,
                    report_type="detailed",
                    output_format="html"
                )
                
                if os.path.exists(report_path):
                    file_size = os.path.getsize(report_path)
                    
                    # Check for charts
                    with open(report_path, 'r') as f:
                        content = f.read()
                        chart_count = content.count('Plotly.newPlot')
                        interactive_divs = content.count('<div id="')
                    
                    print(f"   ✅ {analysis_name} Report: {file_size:,} bytes, {chart_count} charts, {interactive_divs} divs")
                    
                    report_summary["reports"].append({
                        "type": analysis_name,
                        "path": report_path,
                        "size_kb": round(file_size/1024, 1),
                        "charts": chart_count,
                        "interactive_elements": interactive_divs
                    })
                
            except Exception as e:
                print(f"   ❌ {analysis_name} failed: {e}")
        
        return report_summary
        
    except Exception as e:
        print(f"❌ Circuit failed: {e}")
        return None


def main():
    """Generate comprehensive reports for all circuits"""
    print("🚀 Generating All Circuit Reports with Working Charts")
    print("=" * 70)
    
    # Clear existing reports
    import shutil
    reports_dir = Path("reports")
    if reports_dir.exists():
        shutil.rmtree(reports_dir)
    reports_dir.mkdir()
    
    print("🗑️  Cleared existing reports")
    
    test_circuits = [
        ("Voltage Divider", create_voltage_divider),
        ("RC Low-Pass Filter", create_rc_lowpass),
        ("RC High-Pass Filter", create_rc_highpass),
        ("RL Circuit", create_rl_circuit),
        ("RLC Resonant Circuit", create_rlc_resonant),
        ("Pi Low-Pass Filter", create_pi_filter),
        ("Wien Bridge Network", create_wien_bridge),
    ]
    
    all_reports = []
    successful = 0
    total = len(test_circuits)
    
    for circuit_name, circuit_func in test_circuits:
        report_summary = generate_comprehensive_reports(circuit_name, circuit_func)
        if report_summary:
            all_reports.append(report_summary)
            successful += 1
    
    # Generate summary
    print("\n" + "=" * 70)
    print("📊 COMPREHENSIVE REPORT GENERATION SUMMARY")
    print("=" * 70)
    
    total_reports = sum(len(r["reports"]) for r in all_reports)
    total_charts = sum(sum(report["charts"] for report in r["reports"]) for r in all_reports)
    avg_size = sum(sum(report["size_kb"] for report in r["reports"]) for r in all_reports) / max(1, total_reports)
    
    print(f"Circuit types: {successful}/{total}")
    print(f"Total reports: {total_reports}")
    print(f"Total Plotly charts: {total_charts}")
    print(f"Average report size: {avg_size:.1f} KB")
    
    # Detailed breakdown
    print(f"\n📋 Report Breakdown:")
    for report_summary in all_reports:
        print(f"\n🔸 {report_summary['circuit']}:")
        for report in report_summary["reports"]:
            print(f"   {report['type']:>12}: {report['size_kb']:>6} KB, {report['charts']} charts")
    
    print(f"\n✨ All reports with working charts saved in: {reports_dir}/")


if __name__ == "__main__":
    main()