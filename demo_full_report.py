"""
Demo of the complete report generation system.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
from circuit_sim.reports.generator import ReportGenerator
from circuit_sim.simulator.results import SimulationResults
from circuit_sim.circuit import Circuit

print("🚀 Circuit Analysis Report Generator Demo")
print("=" * 50)

# Create a realistic RC filter circuit
circuit = Circuit("RC Low-Pass Filter with Voltage Divider")
circuit.add_voltage_source("V1", 1, 0, "10V")  # Higher input for clearer demo
circuit.add_resistor("R1", 1, 2, "1k")         # Input resistance
circuit.add_resistor("R2", 2, 0, "2k")         # Voltage divider (creates 6.67V at node 2)
circuit.add_resistor("R3", 2, 3, "100")        # Series resistance for RC filter
circuit.add_capacitor("C1", 3, 0, "10u")       # Filter capacitor

print(f"📋 Circuit: {circuit.name}")
print(f"   Components: {len(circuit.components)}")
print(f"   Nodes: {len(circuit.nodes)}")

# Create realistic RC filter simulation results
time = np.linspace(0, 0.005, 500)  # 5ms simulation, 500 points
tau_rc = 100 * 10e-6  # RC time constant = R3 * C1 = 100Ω * 10μF = 1ms

# Voltage divider analysis: 10V input, R1=1k, R2=2k
# V_divider = 10V * R2/(R1+R2) = 10V * 2k/3k = 6.67V
v_input = 10.0 * np.ones_like(time)  # Step input
v_divider = (10.0 * 2000 / (1000 + 2000)) * np.ones_like(time)  # 6.67V at node 2
v_output = v_divider * (1 - np.exp(-time / tau_rc))  # RC charging to 6.67V

# Component currents (realistic values)
i_total = 10.0 / (1000 + 2000)  # Total current = 10V / 3kΩ = 3.33mA
i_r1 = i_total * np.ones_like(time)  # Same current through series resistors
i_r2 = i_total * np.ones_like(time)
i_r3 = (v_divider - v_output) / 100  # Current through R3
i_c1 = 10e-6 * np.gradient(v_output, time)  # Capacitor current

results = SimulationResults("transient")
results.set_time_vector(time)
results.add_voltage(1, v_input)      # Input node (10V)
results.add_voltage(2, v_divider)    # Voltage divider output (6.67V)
results.add_voltage(3, v_output)     # RC filter output (charging to 6.67V)
results.add_current("R1", i_r1)      # 3.33mA through R1
results.add_current("R2", i_r2)      # 3.33mA through R2
results.add_current("R3", i_r3)      # Variable current through R3
results.add_current("C1", i_c1)      # Capacitor charging current

print(f"📊 Simulation: {results.analysis_type.upper()} analysis")
print(f"   Time points: {len(time)}")
print(f"   Duration: {time[-1]*1000:.1f} ms")
print(f"   Voltage divider: {v_divider[0]:.2f}V (from 10V input)")
print(f"   Final RC output: {v_output[-1]:.2f}V (charging toward {v_divider[0]:.2f}V)")
print(f"   RC time constant: {tau_rc*1000:.1f}ms")

# Generate comprehensive report
generator = ReportGenerator()

print(f"\n📄 Generating Reports...")

# Generate all three report types
report_types = ["detailed", "quick", "executive"]
generated_reports = []

for report_type in report_types:
    print(f"   Creating {report_type} report...")
    
    output_path = f"demo_{report_type}_report.html"
    
    result_path = generator.generate_report(
        circuit=circuit,
        results=results,
        report_type=report_type,
        output_format="html",
        output_path=output_path,
        description="Analysis of an RC low-pass filter with voltage divider input stage, demonstrating step response and time constant behavior"
    )
    
    generated_reports.append((report_type, result_path))
    print(f"     ✅ Saved: {result_path}")

print(f"\n🎉 Report Generation Complete!")
print(f"Generated {len(generated_reports)} professional reports:")

for report_type, path in generated_reports:
    file_size = os.path.getsize(path)
    print(f"   📊 {report_type.title()} Report: {path} ({file_size/1024:.1f} KB)")

print(f"\n💡 Features Included:")
print(f"   ✨ Interactive Plotly charts (hover, zoom, pan)")
print(f"   📈 Performance metrics (rise time, settling time, etc.)")
print(f"   🎨 Professional styling with responsive design")
print(f"   📊 Component analysis and BOM-style tables")
print(f"   💼 Executive dashboards with business impact")
print(f"   🔍 Detailed technical analysis")
print(f"   📱 Mobile-friendly responsive design")

print(f"\n🌐 Next Steps:")
print(f"   1. Open any HTML file in your browser")
print(f"   2. Explore the interactive charts")
print(f"   3. Try different report types for different audiences")
print(f"   4. Use in your own circuit analysis projects!")

print(f"\n🚀 Professional circuit analysis reports ready!")