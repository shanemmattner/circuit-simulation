#!/usr/bin/env python
"""
Quick start guide - Shows the simplest way to use the Circuit API
Run with: uv run python examples/quick_start.py
"""

from circuit_sim import Circuit

# Example 1: Simplest possible circuit
print("Example 1: Simple LED Circuit")
led = Circuit("LED Circuit")
led.add_voltage_source("Battery", positive=1, negative=0, dc_value="3V")
led.add_resistor("R_limit", node1=1, node2=2, resistance="330")  # 330 ohms
# Imagine an LED from node 2 to ground
print(led)
print()

# Example 2: Classic voltage divider
print("Example 2: Voltage Divider (outputs 3.3V from 5V)")
divider = (
    Circuit("5V to 3.3V")
    .add_voltage_source("V_in", 1, "gnd", "5V")
    .add_resistor("R1", 1, 2, "680")  # 680 ohms
    .add_resistor("R2", 2, "gnd", "1k")  # 1000 ohms
)
# Output at node 2 will be: 5V * (1000/(680+1000)) = 2.97V ≈ 3V
print(f"Created: {divider}")
print(f"Output node: 2")
print()

# Example 3: RC Filter (smooths signals)
print("Example 3: RC Low-Pass Filter")
filter_circuit = Circuit("Audio Filter")

# Build it step by step
filter_circuit.add_voltage_source("Audio_In", 1, 0, "1V")  # Audio signal
filter_circuit.add_resistor("R", 1, 2, "10k")  # 10k ohms
filter_circuit.add_capacitor("C", 2, 0, "100n")  # 100 nanofarads

# Cutoff frequency = 1/(2*pi*R*C) = 159 Hz
print(f"Built: {filter_circuit}")
print("This would filter out high frequencies above ~159 Hz")
print()

# Show what we can access
print("=" * 50)
print("Circuit API Features:")
print("- Create circuits with readable names")
print("- Add components with human-readable values ('1k', '100n', '5V')")
print("- Use 'gnd' or 0 for ground")
print("- Chain methods for compact code")
print("- Access .components and .nodes to inspect the circuit")
print("\nNext step: PySpice integration for actual simulation!")
print("=" * 50)
