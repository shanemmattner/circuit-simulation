#!/usr/bin/env python
"""
Manual testing script for the Circuit API.
Run this to see the Circuit class in action!
"""

from circuit_sim import Circuit

# Test 1: Create a simple resistor circuit
print("=" * 50)
print("Test 1: Simple Resistor Circuit")
print("=" * 50)

simple = Circuit("Simple Test")
simple.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
simple.add_resistor("R1", node1=1, node2=0, resistance="1k")

print(f"Circuit: {simple}")
print(f"Components: {simple.components}")
print(f"Nodes: {simple.nodes}")

# Test 2: Voltage Divider with method chaining
print("\n" + "=" * 50)
print("Test 2: Voltage Divider (Method Chaining)")
print("=" * 50)

divider = (
    Circuit("Voltage Divider")
    .add_voltage_source("V1", 1, 0, "10V")
    .add_resistor("R1", 1, 2, "10k")
    .add_resistor("R2", 2, 0, "10k")
)

print(f"Circuit: {divider}")
for i, comp in enumerate(divider.components):
    print(f"  Component {i+1}: {comp['type']} {comp['name']}")

# Test 3: RC Filter using 'gnd' alias
print("\n" + "=" * 50)
print("Test 3: RC Filter (using 'gnd' alias)")
print("=" * 50)

rc_filter = Circuit("RC Low-Pass Filter")
rc_filter.add_voltage_source("V1", positive=1, negative="gnd", dc_value="5V")
rc_filter.add_resistor("R1", node1=1, node2=2, resistance="1k")
rc_filter.add_capacitor("C1", node1=2, node2="gnd", capacitance="1u")

print(f"Circuit: {rc_filter}")
print("Components:")
for comp in rc_filter.components:
    if comp["type"] == "voltage_source":
        print(f"  {comp['name']}: {comp['positive']} -> {comp['negative']}, {comp['dc_value']}")
    elif comp["type"] == "resistor":
        print(f"  {comp['name']}: {comp['node1']} -> {comp['node2']}, {comp['resistance']}")
    elif comp["type"] == "capacitor":
        print(f"  {comp['name']}: {comp['node1']} -> {comp['node2']}, {comp['capacitance']}")

# Test 4: RLC Circuit with all component types
print("\n" + "=" * 50)
print("Test 4: Complete RLC Circuit")
print("=" * 50)

rlc = Circuit("RLC Circuit")
rlc.add_voltage_source("V1", 1, 0, "12V")
rlc.add_resistor("R1", 1, 2, "100")
rlc.add_inductor("L1", 2, 3, "10m")
rlc.add_capacitor("C1", 3, 0, "100u")
rlc.add_current_source("I1", 4, 0, "50mA")

print(f"Circuit: {rlc}")
print(f"Total components: {len(rlc.components)}")
print(f"Total nodes: {len(rlc.nodes)} -> {rlc.nodes}")

# Test 5: Try simulation (will fail with NotImplementedError for now)
print("\n" + "=" * 50)
print("Test 5: Simulation (Not Yet Implemented)")
print("=" * 50)

try:
    results = simple.simulate(analysis="dc")
except NotImplementedError as e:
    print(f"Expected error: {e}")
    print("✓ Simulation will be implemented in next phase")

print("\n" + "=" * 50)
print("✅ All manual tests completed successfully!")
print("=" * 50)
