#!/usr/bin/env python3
"""
Debug Chart Rendering

Check if the chart generation is using the correct data and rendering properly.
"""

import sys
import os
from pathlib import Path
import numpy as np

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine
from circuit_sim.reports.charts.plotly_charts import PlotlyChartGenerator


def debug_chart_generation_directly():
    """Test chart generation directly to see what's happening"""
    print("🔍 Debugging Chart Generation Directly")
    print("=" * 50)
    
    # Create RC filter
    circuit = Circuit("RC Low-Pass Filter Debug")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
    circuit.add_capacitor("C1", node1=2, node2="gnd", capacitance="1uF")
    
    engine = SimulationEngine()
    
    # Run AC analysis
    print("🌊 Running AC analysis...")
    ac_results = engine.simulate_ac(circuit, start_frequency=1, stop_frequency=10000, points_per_decade=20)
    
    print(f"✅ AC analysis complete")
    print(f"   Analysis type: '{ac_results.analysis_type}'")
    print(f"   Nodes: {ac_results.nodes}")
    
    # Check Node 2 data in detail
    node2_voltage = ac_results.voltage(2)
    print(f"\n📊 Node 2 raw data:")
    print(f"   Type: {type(node2_voltage)}")
    print(f"   Shape: {np.array(node2_voltage).shape}")
    print(f"   First 5 values: {node2_voltage[:5]}")
    
    magnitude = np.abs(node2_voltage)
    phase = np.angle(node2_voltage, deg=True)
    
    print(f"\n📈 Processed data:")
    print(f"   Magnitude range: {magnitude.min():.6f} to {magnitude.max():.6f}")
    print(f"   Phase range: {phase.min():.2f}° to {phase.max():.2f}°")
    
    # Test chart generator directly
    print(f"\n🎨 Testing Chart Generator...")
    chart_gen = PlotlyChartGenerator()
    
    try:
        charts = chart_gen.create_charts(ac_results, circuit)
        print(f"✅ Charts created: {len(charts)} charts")
        
        for chart_name, chart_fig in charts.items():
            print(f"\n📊 Chart: {chart_name}")
            
            # Extract data from Plotly figure
            if hasattr(chart_fig, 'data'):
                for i, trace in enumerate(chart_fig.data):
                    print(f"   Trace {i}: {getattr(trace, 'name', 'unnamed')}")
                    if hasattr(trace, 'y'):
                        y_data = np.array(trace.y)
                        print(f"      Y data range: {y_data.min():.3f} to {y_data.max():.3f}")
                        print(f"      First 3 Y values: {y_data[:3]}")
                        print(f"      Last 3 Y values: {y_data[-3:]}")
                        
                        # Check for problematic values
                        if np.all(y_data == 0):
                            print(f"      ❌ All zeros!")
                        elif np.all(y_data == y_data[0]):
                            print(f"      ⚠️  All same value: {y_data[0]}")
                        else:
                            print(f"      ✅ Data varies properly")
            
            # Save chart for inspection
            if hasattr(chart_fig, 'to_html'):
                html_content = chart_fig.to_html(include_plotlyjs="cdn")
                debug_file = f"debug_chart_{chart_name}.html"
                with open(debug_file, 'w') as f:
                    f.write(html_content)
                print(f"   💾 Saved: {debug_file}")
                
    except Exception as e:
        print(f"❌ Chart generation failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_chart_generation_directly()