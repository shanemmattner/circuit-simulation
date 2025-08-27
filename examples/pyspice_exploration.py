"""
Exploration of PySpice API to understand how it works.
This is research code to inform our integration design.
"""

from PySpice.Spice.Netlist import Circuit as PySpiceCircuit
from PySpice.Unit import *

# Create a simple voltage divider in PySpice
circuit = PySpiceCircuit("Voltage Divider Test")

# Add components - PySpice uses special unit notation
circuit.V("input", 1, circuit.gnd, 10 @ u_V)  # 10V source
circuit.R(1, 1, 2, 1 @ u_kOhm)  # 1k resistor
circuit.R(2, 2, circuit.gnd, 1 @ u_kOhm)  # 1k resistor

print("Circuit created!")
print(f"Circuit title: {circuit.title}")
print(f"Number of elements: {len(circuit.elements)}")

# Try to run simulation
try:
    # Create simulator
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    print("Simulator created!")

    # Run operating point (DC) analysis
    analysis = simulator.operating_point()
    print("DC analysis complete!")

    # Extract results
    for node in analysis.nodes.values():
        print(f"Node {node}: {float(node)} V")

except Exception as e:
    print(f"Simulation failed (expected if ngspice not installed): {e}")

print("\n" + "=" * 50)
print("Key observations:")
print("1. PySpice uses @ operator for units (10@u_V)")
print("2. Components are added with circuit.R(), circuit.V(), etc")
print("3. Node 0 is circuit.gnd")
print("4. simulator.operating_point() runs DC analysis")
print("5. Results are in analysis.nodes")
print("=" * 50)
