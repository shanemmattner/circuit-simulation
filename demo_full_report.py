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

# Create an amplifier circuit
circuit = Circuit("Op-Amp Non-Inverting Amplifier")
circuit.add_voltage_source("V1", 1, 0, "1V")
circuit.add_resistor("R1", 1, 2, "10k")
circuit.add_resistor("R2", 2, 0, "1k")
circuit.add_resistor("R3", 2, 3, "100")
circuit.add_capacitor("C1", 3, 0, "1u")

print(f"📋 Circuit: {circuit.name}")
print(f"   Components: {len(circuit.components)}")
print(f"   Nodes: {len(circuit.nodes)}")

# Create realistic transient simulation results
time = np.linspace(0, 0.01, 500)  # 10ms simulation, 500 points
tau_rc = 100 * 1e-6  # RC time constant for output
gain = 11  # Non-inverting amplifier gain (1 + R1/R2) = 1 + 10k/1k

# Input and amplified signals with RC filtering
v_input = 1.0 * np.ones_like(time)  # Step input
v_amplified = gain * (1 - np.exp(-time / tau_rc))  # Amplified with RC response
v_output = v_amplified * 0.95  # Slight attenuation due to loading

# Component currents
i_r1 = (v_amplified - v_output) / 10000  # Current through R1
i_r2 = v_output / 1000  # Current through R2
i_c1 = (1e-6) * np.gradient(v_output, time)  # Capacitor current

results = SimulationResults("transient")
results.set_time_vector(time)
results.add_voltage(1, v_input)      # Input node
results.add_voltage(2, v_amplified)  # Amplifier output
results.add_voltage(3, v_output)     # Final output after RC
results.add_current("R1", i_r1)
results.add_current("R2", i_r2) 
results.add_current("C1", i_c1)

print(f"📊 Simulation: {results.analysis_type.upper()} analysis")
print(f"   Time points: {len(time)}")
print(f"   Duration: {time[-1]*1000:.1f} ms")
print(f"   Final output: {v_output[-1]:.2f}V (gain: {v_output[-1]/v_input[0]:.1f}x)")

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
        description=f"Performance analysis of a non-inverting operational amplifier circuit with {gain}x gain and RC output filtering"
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