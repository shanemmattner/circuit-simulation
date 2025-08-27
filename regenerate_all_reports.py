#!/usr/bin/env python3
"""
Complete Report Regeneration Script

This script completely clears all reports and regenerates everything with the latest fixes.
Use this for testing after making changes to chart generation or report logic.
"""

import sys
import os
import shutil
from pathlib import Path
import traceback

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine
from circuit_sim.reports import ReportGenerator


def clear_all_reports():
    """Clear all existing report directories"""
    print("🗑️  Clearing All Existing Reports")
    print("=" * 40)
    
    dirs_to_clear = ["reports", "test_reports", "fixed_reports", "reports_test_output"]
    
    for dir_name in dirs_to_clear:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"   ✅ Cleared: {dir_name}/")
        else:
            print(f"   📁 Not found: {dir_name}/")
    
    # Create fresh reports directory
    Path("reports").mkdir(exist_ok=True)
    print(f"   ✅ Created: reports/")


# Circuit Definitions
CIRCUITS = {
    "Basic Voltage Divider": lambda: Circuit("Voltage Divider")
        .add_voltage_source("V1", positive=1, negative="gnd", dc_value="10V")
        .add_resistor("R1", node1=1, node2=2, resistance="1k")
        .add_resistor("R2", node1=2, node2="gnd", resistance="1k"),
    
    "RC Low-Pass Filter": lambda: Circuit("RC Low-Pass Filter")
        .add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
        .add_resistor("R1", node1=1, node2=2, resistance="1k")
        .add_capacitor("C1", node1=2, node2="gnd", capacitance="1uF"),
    
    "RC High-Pass Filter": lambda: Circuit("RC High-Pass Filter")
        .add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
        .add_capacitor("C1", node1=1, node2=2, capacitance="100nF")
        .add_resistor("R1", node1=2, node2="gnd", resistance="1.6k"),
    
    "RL Circuit": lambda: Circuit("RL Circuit")
        .add_voltage_source("V1", positive=1, negative="gnd", dc_value="12V")
        .add_resistor("R1", node1=1, node2=2, resistance="100")
        .add_inductor("L1", node1=2, node2="gnd", inductance="10mH"),
    
    "RLC Resonant": lambda: Circuit("RLC Resonant Circuit")
        .add_voltage_source("V1", positive=1, negative="gnd", dc_value="5V")
        .add_resistor("R1", node1=1, node2=2, resistance="10")
        .add_inductor("L1", node1=2, node2=3, inductance="1mH")
        .add_capacitor("C1", node1=3, node2="gnd", capacitance="10nF"),
    
    "Pi Low-Pass Filter": lambda: Circuit("Pi Low-Pass Filter")
        .add_voltage_source("V1", positive=1, negative="gnd", dc_value="5V")
        .add_capacitor("C1", node1=1, node2="gnd", capacitance="10uF")
        .add_inductor("L1", node1=1, node2=2, inductance="1mH")
        .add_capacitor("C2", node1=2, node2="gnd", capacitance="10uF")
        .add_resistor("R_load", node1=2, node2="gnd", resistance="50"),
    
    "Wien Bridge": lambda: Circuit("Wien Bridge Network")
        .add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
        .add_resistor("R1", node1=1, node2=2, resistance="1.6k")
        .add_capacitor("C1", node1=2, node2=3, capacitance="100nF")
        .add_resistor("R2", node1=1, node2=4, resistance="1.6k")
        .add_capacitor("C2", node1=4, node2="gnd", capacitance="100nF")
        .add_resistor("R_bridge", node1=3, node2=4, resistance="10k")
        .add_resistor("R_load", node1=3, node2="gnd", resistance="10k"),
}


def generate_all_analysis_reports(circuit_name, circuit_func):
    """Generate DC, Transient, and AC reports for a single circuit"""
    print(f"\n🔬 Generating All Reports: {circuit_name}")
    print("-" * 50)
    
    try:
        circuit = circuit_func()
        print(f"✅ Circuit: {len(circuit.components)} components, {len(circuit.nodes)} nodes")
        
        engine = SimulationEngine()
        generator = ReportGenerator()
        
        reports_generated = []
        
        # Generate for each analysis type
        analyses = [
            ("DC", lambda: engine.simulate_dc(circuit)),
            ("Transient", lambda: engine.simulate_transient(circuit, stop_time=0.001)),
            ("AC", lambda: engine.simulate_ac(circuit, start_frequency=1, stop_frequency=100000, points_per_decade=20))
        ]
        
        for analysis_name, simulate_func in analyses:
            try:
                print(f"   🔄 {analysis_name} analysis...")
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
                    
                    # Check chart content
                    with open(report_path, 'r') as f:
                        content = f.read()
                    
                    chart_count = content.count('Plotly.newPlot')
                    has_real_data = 'y":[' in content and not ('y":[0,0,0' in content and chart_count == 1)
                    
                    status = "✅" if has_real_data else "⚠️"
                    print(f"   {status} {analysis_name}: {file_size//1024:,}KB, {chart_count} charts, real_data={has_real_data}")
                    
                    reports_generated.append({
                        "type": analysis_name,
                        "size_kb": file_size//1024,
                        "charts": chart_count,
                        "has_data": has_real_data
                    })
                else:
                    print(f"   ❌ {analysis_name}: Report file not found")
                    
            except Exception as e:
                print(f"   ❌ {analysis_name}: {e}")
        
        return reports_generated
        
    except Exception as e:
        print(f"❌ Circuit generation failed: {e}")
        return []


def main():
    """Main regeneration function"""
    print("🚀 COMPLETE REPORT REGENERATION")
    print("=" * 50)
    print("This script will:")
    print("1. Clear ALL existing reports")
    print("2. Regenerate reports with latest fixes")
    print("3. Test each circuit type thoroughly")
    print("4. Create summary index page")
    print()
    
    # Step 1: Clear everything
    clear_all_reports()
    
    # Step 2: Generate reports for all circuits
    print(f"\n📊 Generating Reports for {len(CIRCUITS)} Circuit Types")
    print("=" * 60)
    
    all_results = []
    successful_circuits = 0
    
    for circuit_name, circuit_func in CIRCUITS.items():
        reports = generate_all_analysis_reports(circuit_name, circuit_func)
        if reports:
            all_results.extend(reports)
            successful_circuits += 1
    
    # Step 3: Generate summary
    print(f"\n" + "=" * 60)
    print("📊 REGENERATION COMPLETE")
    print("=" * 60)
    
    total_reports = len(all_results)
    total_charts = sum(r["charts"] for r in all_results)
    avg_size = sum(r["size_kb"] for r in all_results) / max(1, total_reports)
    reports_with_data = len([r for r in all_results if r["has_data"]])
    
    print(f"Circuits processed: {successful_circuits}/{len(CIRCUITS)}")
    print(f"Total reports: {total_reports}")
    print(f"Reports with real data: {reports_with_data}/{total_reports}")
    print(f"Total Plotly charts: {total_charts}")
    print(f"Average report size: {avg_size:.1f} KB")
    
    # Success rate analysis
    success_rate = (reports_with_data / total_reports * 100) if total_reports > 0 else 0
    print(f"Data quality success rate: {success_rate:.1f}%")
    
    if success_rate < 90:
        print(f"⚠️  Warning: {100-success_rate:.1f}% of reports may have chart issues")
    else:
        print(f"✅ Excellent: {success_rate:.1f}% of reports have working charts!")
    
    # Step 4: Create index
    print(f"\n🌐 Creating Report Index...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, "open_all_reports.py"], 
                              capture_output=True, text=True, cwd=".")
        if result.returncode == 0:
            print("✅ Index page created successfully")
        else:
            print(f"⚠️  Index creation issue: {result.stderr}")
    except Exception as e:
        print(f"⚠️  Could not auto-create index: {e}")
    
    print(f"\n🎯 Final Status:")
    print(f"📁 Reports directory: reports/")
    print(f"🌐 Index page: reports/index.html")
    print(f"✨ Ready for review!")


if __name__ == "__main__":
    main()