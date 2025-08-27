#!/usr/bin/env python3
"""
Test Improved Node Labels

Generate a single report to test the improved node labeling system.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine
from circuit_sim.reports import ReportGenerator


def test_improved_labeling():
    """Test the improved node labeling in a report"""
    print("🏷️  Testing Improved Node Labeling")
    print("=" * 40)
    
    # Create RC filter
    circuit = Circuit("RC Low-Pass Filter")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="1k") 
    circuit.add_capacitor("C1", node1=2, node2="gnd", capacitance="1uF")
    
    print("📊 Circuit: RC Low-Pass Filter")
    print("   Expected labels:")
    print("   Node 1: Circuit Input [V1+]")
    print("   Node 2: Filter Output [Before C1]")
    
    engine = SimulationEngine()
    
    # Generate AC report with improved labels
    try:
        ac_results = engine.simulate_ac(circuit, start_frequency=1, stop_frequency=10000, points_per_decade=20)
        print(f"✅ AC simulation successful")
        
        generator = ReportGenerator()
        report_path = generator.generate_report(
            circuit=circuit,
            results=ac_results,
            report_type="detailed",
            output_format="html"
        )
        
        if os.path.exists(report_path):
            file_size = os.path.getsize(report_path)
            
            # Check for improved labels in the HTML
            with open(report_path, 'r') as f:
                content = f.read()
            
            # Look for our improved labeling
            has_circuit_input = "Circuit Input" in content
            has_filter_output = "Filter Output" in content or "Before C" in content
            has_old_labels = "V(Node 2)" in content and "Bode Plot - V(Node" in content
            
            print(f"✅ Report generated: {file_size:,} bytes")
            print(f"📊 Chart improvements:")
            print(f"   Circuit Input labels: {'✅' if has_circuit_input else '❌'}")
            print(f"   Filter Output labels: {'✅' if has_filter_output else '❌'}")
            print(f"   Old generic labels: {'⚠️' if has_old_labels else '✅ Removed'}")
            
            print(f"\n🔗 Report with improved labels: {report_path}")
            
            return True
        else:
            print(f"❌ Report not found: {report_path}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    test_improved_labeling()