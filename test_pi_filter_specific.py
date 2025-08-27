#!/usr/bin/env python3
"""
Test Pi Filter Specific Chart Generation
"""

import sys
import os
from pathlib import Path
import numpy as np

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine
from circuit_sim.reports import ReportGenerator


def test_pi_filter_specific():
    """Test Pi filter with corrected chart generation"""
    print("🔍 Testing Pi Filter Chart Generation")
    print("=" * 45)
    
    # Create Pi filter
    circuit = Circuit("Pi Low-Pass Filter")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="5V")
    circuit.add_capacitor("C1", node1=1, node2="gnd", capacitance="10uF")
    circuit.add_inductor("L1", node1=1, node2=2, inductance="1mH") 
    circuit.add_capacitor("C2", node1=2, node2="gnd", capacitance="10uF")
    circuit.add_resistor("R_load", node1=2, node2="gnd", resistance="50")
    
    print(f"✅ Pi filter: L=1mH, C=10μF, R_load=50Ω")
    
    # Calculate expected cutoff frequency
    # For Pi filter: fc ≈ 1/(2π√(LC)) 
    L = 1e-3  # 1mH
    C = 10e-6  # 10μF
    expected_fc = 1 / (2 * np.pi * np.sqrt(L * C))
    print(f"   Expected cutoff: ~{expected_fc:.0f} Hz")
    
    engine = SimulationEngine()
    
    # Run AC analysis
    ac_results = engine.simulate_ac(circuit, start_frequency=10, stop_frequency=10000, points_per_decade=30)
    
    print(f"\n📊 Nodes: {ac_results.nodes}")
    
    # Check Node 2 response (should show filter response)
    node2_voltage = ac_results.voltage(2)
    if node2_voltage is not None:
        magnitude = np.abs(node2_voltage)
        print(f"   Node 2 magnitude range: {magnitude.min():.6f} to {magnitude.max():.6f}")
        print(f"   Variation: {magnitude.max() - magnitude.min():.6f}")
    
    # Generate report
    generator = ReportGenerator()
    report_path = generator.generate_report(
        circuit=circuit,
        results=ac_results,
        report_type="detailed",
        output_format="html"
    )
    
    if os.path.exists(report_path):
        file_size = os.path.getsize(report_path)
        
        with open(report_path, 'r') as f:
            content = f.read()
        
        chart_count = content.count('Plotly.newPlot')
        node2_charts = content.count('Node 2')
        node1_charts = content.count('Node 1') 
        
        print(f"\n✅ Report: {file_size:,} bytes")
        print(f"📊 Total charts: {chart_count}")
        print(f"📈 Node 1 charts: {node1_charts}")
        print(f"📈 Node 2 charts: {node2_charts}")
        print(f"🔗 File: {report_path}")
        
        # Check if we're now focusing on the right node
        if node2_charts > node1_charts:
            print(f"✅ Correctly prioritizing output node (Node 2)!")
        elif node1_charts == 0:
            print(f"✅ Successfully filtered out flat input node!")
        else:
            print(f"⚠️  Still showing input node charts")
    
    return True


if __name__ == "__main__":
    test_pi_filter_specific()