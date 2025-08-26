#!/usr/bin/env python
"""
Interactive demo - run with: python -i examples/interactive_demo.py
This will drop you into an interactive Python session with a circuit loaded.
"""

from circuit_sim import Circuit

# Create a sample circuit
circuit = Circuit("My Circuit")
circuit.add_voltage_source("V1", 1, 0, "5V")
circuit.add_resistor("R1", 1, 2, "1k")
circuit.add_capacitor("C1", 2, 0, "10u")

print("\n" + "="*60)
print("🔌 Circuit Simulation Interactive Demo")
print("="*60)
print("\nA sample RC circuit has been created as 'circuit'")
print("\nTry these commands:")
print("  >>> circuit")
print("  >>> circuit.components")
print("  >>> circuit.nodes")
print("  >>> circuit.add_resistor('R2', 2, 3, '2.2k')")
print("  >>> circuit")
print("\nOr create your own:")
print("  >>> my_circuit = Circuit('Test')")
print("  >>> my_circuit.add_voltage_source('V1', 1, 'gnd', '12V')")
print("\n" + "="*60 + "\n")