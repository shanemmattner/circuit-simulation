"""
Quick demo of the Plotly chart generation functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
from circuit_sim.reports.charts.plotly_charts import PlotlyChartGenerator
from circuit_sim.simulator.results import SimulationResults
from circuit_sim.circuit import Circuit

# Create a simple voltage divider circuit
circuit = Circuit("Voltage Divider Demo")
circuit.add_voltage_source("V1", 1, 0, "9V")
circuit.add_resistor("R1", 1, 2, "2k")
circuit.add_resistor("R2", 2, 0, "1k")

# Create mock DC analysis results
results = SimulationResults("dc")
results.add_voltage(1, 9.0)    # Input voltage
results.add_voltage(2, 3.0)    # Output voltage (1/3 of input due to voltage divider)
results.add_current("V1", 0.003)  # 3mA source current
results.add_current("R1", 0.003)  # Same current through R1
results.add_current("R2", 0.003)  # Same current through R2

print("🎯 Creating DC Analysis Chart...")

# Generate charts
chart_generator = PlotlyChartGenerator()
charts = chart_generator.create_charts(results, circuit)

print(f"📊 Generated {len(charts)} chart(s):")
for chart_name in charts.keys():
    print(f"   - {chart_name}")

# Show the DC voltages chart
if "dc_voltages" in charts:
    dc_chart = charts["dc_voltages"]
    print(f"\n✨ DC Voltages Chart:")
    print(f"   Title: {dc_chart.layout.title.text}")
    print(f"   Data points: {len(dc_chart.data[0].x)}")
    print(f"   Voltages: {dc_chart.data[0].y}")
    print(f"   Nodes: {list(dc_chart.data[0].x)}")
    
    # Save as HTML file to view in browser
    dc_chart.write_html("demo_dc_chart.html", include_plotlyjs='cdn')
    print(f"\n💾 Chart saved as 'demo_dc_chart.html' - open in browser to view!")

# Show the DC currents chart too
if "dc_currents" in charts:
    current_chart = charts["dc_currents"]
    print(f"\n⚡ DC Currents Chart:")
    print(f"   Title: {current_chart.layout.title.text}")
    print(f"   Components: {list(current_chart.data[0].x)}")
    print(f"   Currents (A): {current_chart.data[0].y}")
    
    current_chart.write_html("demo_current_chart.html", include_plotlyjs='cdn')
    print(f"💾 Current chart saved as 'demo_current_chart.html'")

print(f"\n🚀 Demo complete! Open the HTML files in your browser to see interactive charts.")