"""
Demo of transient analysis chart generation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
from circuit_sim.reports.charts.plotly_charts import PlotlyChartGenerator
from circuit_sim.simulator.results import SimulationResults
from circuit_sim.circuit import Circuit

# Create RC charging circuit
circuit = Circuit("RC Charging Circuit")
circuit.add_voltage_source("V1", 1, 0, "5V")
circuit.add_resistor("R1", 1, 2, "1k")
circuit.add_capacitor("C1", 2, 0, "1u")

print("🔋 Creating RC Charging Simulation...")

# Generate realistic RC charging curve
time = np.linspace(0, 0.005, 200)  # 5ms simulation
tau = 1e3 * 1e-6  # RC = 1k * 1uF = 1ms time constant
voltage_input = 5.0 * np.ones_like(time)  # Step input
voltage_cap = 5.0 * (1 - np.exp(-time / tau))  # Exponential charging
current = (5.0 / 1000) * np.exp(-time / tau)  # Exponential decay

# Create transient simulation results
results = SimulationResults("transient")
results.set_time_vector(time)
results.add_voltage(1, voltage_input)    # Input node
results.add_voltage(2, voltage_cap)      # Capacitor node
results.add_current("R1", current)      # Resistor current
results.add_current("C1", current)      # Capacitor current (same as resistor)

# Generate charts
chart_generator = PlotlyChartGenerator()
charts = chart_generator.create_charts(results, circuit)

print(f"📈 Generated {len(charts)} transient chart(s):")
for chart_name in charts.keys():
    print(f"   - {chart_name}")

# Save the main transient chart
if "transient_voltages" in charts:
    voltage_chart = charts["transient_voltages"]
    print(f"\n📊 Voltage Chart:")
    print(f"   Title: {voltage_chart.layout.title.text}")
    print(f"   Number of traces: {len(voltage_chart.data)}")
    print(f"   Time points: {len(time)}")
    print(f"   Time range: {time[0]:.3f}s to {time[-1]:.3f}s")
    print(f"   Final capacitor voltage: {voltage_cap[-1]:.2f}V (should approach 5V)")
    
    voltage_chart.write_html("demo_transient_voltages.html", include_plotlyjs='cdn')
    print(f"💾 Voltage chart saved as 'demo_transient_voltages.html'")

# Save the combined chart if available
if "transient_combined" in charts:
    combined_chart = charts["transient_combined"]
    print(f"\n🔗 Combined Chart (Voltages + Currents):")
    print(f"   Title: {combined_chart.layout.title.text}")
    print(f"   Height: {combined_chart.layout.height}px")
    
    combined_chart.write_html("demo_transient_combined.html", include_plotlyjs='cdn')
    print(f"💾 Combined chart saved as 'demo_transient_combined.html'")

print(f"\n✨ Interactive charts created! Open the HTML files to see:")
print(f"   • Hover over data points for exact values")
print(f"   • Zoom and pan to explore the data")
print(f"   • Legend to toggle traces on/off")
print(f"   • Professional styling with Plotly")