#!/usr/bin/env python3
"""
Test AC Charts Fix

Generate a single AC report to verify the Bode plot fix works properly.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine
from circuit_sim.reports import ReportGenerator
import numpy as np


def test_rc_filter_ac_fix():
    """Test AC chart fix on RC filter"""
    print("🔍 Testing AC Chart Fix on RC Low-Pass Filter")
    print("=" * 55)
    
    # Create RC low-pass filter
    circuit = Circuit("RC Low-Pass Filter Test")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
    circuit.add_capacitor("C1", node1=2, node2="gnd", capacitance="1uF")
    
    expected_cutoff = 1 / (2 * np.pi * 1000 * 1e-6)
    print(f"✅ RC Filter: R=1kΩ, C=1μF, fc={expected_cutoff:.1f} Hz")
    
    engine = SimulationEngine()
    
    # Run AC analysis
    print("\n🌊 Running AC analysis...")
    ac_results = engine.simulate_ac(
        circuit, 
        start_frequency=1, 
        stop_frequency=100000,  # 100kHz for good rolloff view
        points_per_decade=50    # More points for smoother curves
    )
    
    print(f"✅ AC simulation complete: {len(ac_results.frequency)} frequency points")
    
    # Check the actual voltage data
    print(f"\n📊 AC Response Analysis:")
    for node in ac_results.nodes:
        if node != 0:
            voltage = ac_results.voltage(node)
            if voltage is not None:
                magnitude = np.abs(voltage)
                phase = np.angle(voltage, deg=True)
                
                print(f"\n   Node {node}:")
                print(f"   📈 Magnitude range: {magnitude.min():.6f} to {magnitude.max():.6f}")
                print(f"   📐 Phase range: {phase.min():.1f}° to {phase.max():.1f}°")
                
                # Find response at different frequencies
                frequencies = np.array(ac_results.frequency)
                
                # Low frequency (should be ~1.0 for input, ~1.0 for output)
                low_idx = 0
                print(f"   At {frequencies[low_idx]:.1f} Hz: |V| = {magnitude[low_idx]:.3f}, ∠ = {phase[low_idx]:.1f}°")
                
                # Around cutoff frequency
                cutoff_idx = np.argmin(np.abs(frequencies - expected_cutoff))
                print(f"   At {frequencies[cutoff_idx]:.1f} Hz: |V| = {magnitude[cutoff_idx]:.3f}, ∠ = {phase[cutoff_idx]:.1f}°")
                
                # High frequency
                high_idx = -1
                print(f"   At {frequencies[high_idx]:.1f} Hz: |V| = {magnitude[high_idx]:.3f}, ∠ = {phase[high_idx]:.1f}°")
    
    # Generate AC report
    print(f"\n📄 Generating AC report with fixed charts...")
    generator = ReportGenerator()
    
    report_path = generator.generate_report(
        circuit=circuit,
        results=ac_results,
        report_type="detailed",
        output_format="html"
    )
    
    if os.path.exists(report_path):
        file_size = os.path.getsize(report_path)
        
        # Check chart content
        with open(report_path, 'r') as f:
            content = f.read()
            
        chart_count = content.count('Plotly.newPlot')
        has_data = 'y":[' in content and not content.count('y":[0,0,0') == chart_count
        
        print(f"✅ Report generated: {file_size:,} bytes")
        print(f"📊 Contains {chart_count} Plotly charts")
        print(f"📈 Has real data: {'✅' if has_data else '❌'}")
        
        # Check for flat line indicators
        if 'y":[0,' in content:
            print(f"⚠️  Warning: May contain flat lines at zero")
        
        print(f"🔗 Report: {report_path}")
        
        return True
    else:
        print(f"❌ Report file not found: {report_path}")
        return False


if __name__ == "__main__":
    test_rc_filter_ac_fix()