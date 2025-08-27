# Voltage Divider Circuit Example

## Overview
The voltage divider is one of the most fundamental circuits in electronics. It uses two resistors in series to reduce an input voltage to a desired output voltage level.

## Circuit Theory

### Basic Operation
```
    Vin ---[R1]---+--- Vout
                  |
                 [R2]
                  |
                 GND
```

The output voltage is determined by the ratio of the resistors:
```
Vout = Vin × R2 / (R1 + R2)
```

### Key Concepts
1. **Voltage Division Ratio**: The fraction of input voltage appearing at the output
2. **Loading Effect**: How a load resistor affects the output voltage
3. **Power Dissipation**: Energy lost as heat in the resistors
4. **Thevenin Equivalent**: Simplified representation for circuit analysis

## Usage

### Basic Example
```python
from examples.basic.voltage_divider import VoltageDividerCircuit, simulate_voltage_divider, generate_report

# Create a voltage divider with equal resistors
circuit = VoltageDividerCircuit(r1=1000, r2=1000, vin=5.0)

# Calculate theoretical output
print(f"Theoretical output: {circuit.calculate_theoretical_output():.2f}V")

# Run simulation
results = simulate_voltage_divider(circuit, analysis_type="dc")
print(f"Simulated output: {results['output_voltage']:.2f}V")

# Generate interactive report
report = generate_report(circuit, results)
report.save("voltage_divider_report.html")
```

### With Load Resistor
```python
# Voltage divider with 1kΩ load
circuit = VoltageDividerCircuit(r1=1000, r2=1000, vin=5.0, r_load=1000)

# The load affects the output voltage
print(f"Output with load: {circuit.calculate_theoretical_output():.2f}V")
```

### Parameter Sweep
```python
# Sweep input voltage from 0 to 10V
results = simulate_voltage_divider(
    circuit,
    analysis_type="sweep",
    sweep_param="vin",
    sweep_range=(0, 10, 0.5)
)

# Generate report with sweep results
report = generate_report(circuit, results, include_sweep=True)
```

### Tolerance Analysis
```python
from examples.basic.voltage_divider import analyze_divider_ratio

# Analyze with 5% resistor tolerance
tolerance_results = analyze_divider_ratio(circuit, tolerance=0.05)
print(f"Nominal output: {tolerance_results['nominal_output']:.3f}V")
print(f"Min output: {tolerance_results['min_output']:.3f}V")
print(f"Max output: {tolerance_results['max_output']:.3f}V")
print(f"Variation: ±{tolerance_results['variation_percent']:.1f}%")
```

## Common Applications

### 1. Reference Voltage Generation
Create a stable reference voltage from a supply:
```python
# 3.3V reference from 5V supply
circuit = VoltageDividerCircuit(r1=1000, r2=2000, vin=5.0)
```

### 2. Sensor Signal Conditioning
Scale sensor outputs to ADC input range:
```python
# Scale 0-10V sensor to 0-3.3V for microcontroller
circuit = VoltageDividerCircuit(r1=20000, r2=10000, vin=10.0)
```

### 3. LED Current Limiting
Combined with current limiting resistor:
```python
# Voltage divider for LED bias
circuit = VoltageDividerCircuit(r1=330, r2=220, vin=5.0)
```

## Design Considerations

### Choosing Resistor Values
1. **Power Consumption**: Higher resistance = lower power consumption
2. **Output Impedance**: Lower resistance = better drive capability
3. **Noise Immunity**: Balance between power and noise performance

### Common Pitfalls
1. **Loading Effect**: Output voltage changes when load is connected
2. **Power Rating**: Ensure resistors can handle the power dissipation
3. **Tolerance Stack-up**: Consider worst-case component variations
4. **Temperature Coefficients**: Resistor values change with temperature

## Simulation Parameters

### DC Analysis
- Calculates operating point voltages and currents
- Determines power dissipation
- Shows loading effects

### Parameter Sweep
- Vary input voltage, R1, or R2
- Observe output response
- Identify optimal component values

### Tolerance Analysis
- Monte Carlo simulation with component variations
- Worst-case analysis
- Sensitivity analysis

## Files in This Example

- `circuit.py`: Voltage divider circuit class
- `simulation.py`: Simulation and analysis functions
- `report.py`: Interactive report generation
- `netlist.cir`: SPICE netlist for the circuit
- `test_voltage_divider.py`: Unit tests

## Further Reading

- [Voltage Divider on Wikipedia](https://en.wikipedia.org/wiki/Voltage_divider)
- [All About Circuits: Voltage Divider](https://www.allaboutcircuits.com/tools/voltage-divider-calculator/)
- [Electronics Tutorials: Voltage Divider](https://www.electronics-tutorials.ws/dccircuits/voltage-divider.html)

## Next Steps

After understanding the voltage divider, explore:
1. **RC Filter**: Add capacitance for frequency-dependent behavior
2. **Wheatstone Bridge**: Four-resistor configuration for precision measurement
3. **Potentiometer Circuits**: Variable voltage division