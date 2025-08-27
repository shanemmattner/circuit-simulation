# RC Filter Circuit Example

## Overview
RC filters are fundamental frequency-selective circuits that use a resistor and capacitor to create frequency-dependent behavior. They form the basis of many signal processing applications.

## Circuit Theory

### Low-Pass Filter
```
    Vin ---[R]---+--- Vout
                 |
                [C]
                 |
                GND
```
- **Transfer Function**: H(jω) = 1 / (1 + jωRC)
- **Cutoff Frequency**: fc = 1 / (2πRC)
- **Passes low frequencies, attenuates high frequencies**

### High-Pass Filter
```
    Vin ---[C]---+--- Vout
                 |
                [R]
                 |
                GND
```
- **Transfer Function**: H(jω) = jωRC / (1 + jωRC)
- **Cutoff Frequency**: fc = 1 / (2πRC)
- **Passes high frequencies, attenuates low frequencies**

### Key Parameters
- **Time Constant**: τ = RC (seconds)
- **Cutoff Frequency**: fc = 1/(2πτ) (Hz)
- **Rolloff Rate**: -20 dB/decade (-6 dB/octave)
- **Phase at fc**: -45° (lowpass), +45° (highpass)

## Usage Examples

### Basic Low-Pass Filter
```python
from examples.basic.rc_filter import RCFilterCircuit, simulate_rc_filter

# Create a 1kHz low-pass filter
circuit = RCFilterCircuit(
    r=1000,      # 1kΩ
    c=159e-9,    # 159nF for ~1kHz cutoff
    filter_type="lowpass"
)

print(f"Cutoff frequency: {circuit.cutoff_frequency:.1f} Hz")
print(f"Time constant: {circuit.time_constant*1000:.3f} ms")
```

### Frequency Response Analysis
```python
import numpy as np
from examples.basic.rc_filter import calculate_frequency_response, generate_bode_plot

# Analyze frequency response
frequencies = np.logspace(1, 5, 100)  # 10Hz to 100kHz
response = calculate_frequency_response(circuit, frequencies)

# Generate Bode plot
fig = generate_bode_plot(circuit, response, show_cutoff=True)
fig.show()
```

### Step Response Simulation
```python
# Simulate step response
results = simulate_rc_filter(
    circuit,
    analysis_type="transient",
    duration=5e-3,  # 5ms
    input_type="step"
)

# Visualize transient response
from examples.basic.rc_filter import generate_transient_plot
fig = generate_transient_plot(circuit, results)
fig.show()
```

### AC Analysis
```python
# Run AC frequency sweep
results = simulate_rc_filter(
    circuit,
    analysis_type="ac",
    start_freq=1,
    stop_freq=100000,
    points_per_decade=20
)

print(f"Magnitude at fc: {results['magnitude_db'][fc_index]:.2f} dB")  # Should be -3dB
```

### High-Pass Filter
```python
# Create a high-pass filter for audio (20Hz cutoff)
audio_filter = RCFilterCircuit(
    r=8000,      # 8kΩ
    c=1e-6,      # 1µF
    filter_type="highpass"
)

# This blocks DC and very low frequencies
print(f"DC attenuation: {audio_filter.magnitude_db(0):.1f} dB")  # Very large attenuation
print(f"1kHz response: {audio_filter.magnitude_db(1000):.1f} dB")  # Near 0dB
```

## Common Applications

### 1. Anti-Aliasing Filter
Prevent high-frequency noise from corrupting ADC readings:
```python
# Anti-aliasing for 10kHz sampling rate (fc = fs/2.5)
adc_filter = RCFilterCircuit(
    r=3900,      # 3.9kΩ
    c=10e-9,     # 10nF
    filter_type="lowpass"
)
print(f"Cutoff: {adc_filter.cutoff_frequency:.0f} Hz")  # ~4kHz
```

### 2. DC Blocking (AC Coupling)
Remove DC offset from AC signals:
```python
# AC coupling for audio amplifier
dc_block = RCFilterCircuit(
    r=100000,    # 100kΩ input impedance
    c=100e-9,    # 100nF
    filter_type="highpass"
)
print(f"Low frequency cutoff: {dc_block.cutoff_frequency:.1f} Hz")  # ~16Hz
```

### 3. Noise Filter
Reduce high-frequency noise in sensor signals:
```python
# Sensor noise filter (100Hz bandwidth)
sensor_filter = RCFilterCircuit(
    r=1600,      # 1.6kΩ
    c=1e-6,      # 1µF
    filter_type="lowpass"
)
```

### 4. Pulse Shaping
Smooth digital signals:
```python
# Rise time limiting for digital signals
pulse_shaper = RCFilterCircuit(
    r=100,       # 100Ω
    c=100e-12,   # 100pF
    filter_type="lowpass"
)
print(f"Rise time: {pulse_shaper.time_constant * 2.2 * 1e9:.1f} ns")
```

## Design Equations

### Selecting Component Values

Given desired cutoff frequency fc:
1. Choose a standard capacitor value
2. Calculate R = 1 / (2π × fc × C)
3. Select nearest standard resistor value

Example:
```python
def design_rc_filter(fc_desired, c_available):
    """Design RC filter for target cutoff frequency."""
    import numpy as np
    
    r_calculated = 1 / (2 * np.pi * fc_desired * c_available)
    
    # Find nearest E12 series resistor
    e12_values = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]
    decade = 10 ** np.floor(np.log10(r_calculated))
    normalized = r_calculated / decade
    
    closest = min(e12_values, key=lambda x: abs(x - normalized))
    r_standard = closest * decade
    
    fc_actual = 1 / (2 * np.pi * r_standard * c_available)
    
    return r_standard, fc_actual

# Design 1kHz filter with 100nF capacitor
r, fc = design_rc_filter(1000, 100e-9)
print(f"Use R={r:.0f}Ω for fc={fc:.1f}Hz")
```

## Performance Analysis

### Filter Characterization
```python
char = circuit.characterize_filter()
print(f"Type: {char['filter_type']}")
print(f"3dB frequency: {char['3db_frequency']:.1f} Hz")
print(f"Rolloff: {char['attenuation_per_decade']} dB/decade")
```

### Group Delay
```python
frequencies = [100, 1000, 10000]
delays = circuit.calculate_group_delay(frequencies)

for f, d in zip(frequencies, delays):
    print(f"{f:5.0f} Hz: {d*1e6:6.2f} µs delay")
```

### Cascaded Stages
```python
# Two-stage filter for steeper rolloff
stages = 2
response = circuit.calculate_cascade_response(stages, 10000)
print(f"Attenuation at 10kHz: {response['magnitude_db']:.1f} dB")
# Will be approximately 2× the single-stage attenuation in dB
```

## Visualization Options

### Compare Multiple Filters
```python
from examples.basic.rc_filter import generate_comparison_plot

filters = [
    RCFilterCircuit(r=1000, c=1e-6, filter_type="lowpass"),
    RCFilterCircuit(r=1000, c=1e-6, filter_type="highpass"),
    RCFilterCircuit(r=10000, c=100e-9, filter_type="lowpass"),
]

fig = generate_comparison_plot(filters)
fig.show()
```

### Interactive Bode Plot
```python
# Full Bode plot with magnitude and phase
fig = generate_bode_plot(
    circuit,
    response,
    show_cutoff=True,
    show_phase=True,
    title="Custom Filter Analysis"
)
```

## Design Considerations

### Component Selection
1. **Resistor Range**: 100Ω to 1MΩ typical
2. **Capacitor Types**: 
   - Ceramic: High frequency, small values
   - Film: Audio, medium values
   - Electrolytic: Low frequency, large values

### Input/Output Impedance
- **Input Impedance**: Zin ≈ R (at low freq for lowpass)
- **Output Impedance**: Zout ≈ R || (1/jωC)
- Match impedances to avoid loading effects

### Tolerance Effects
- Use 1% resistors for precision applications
- Capacitor tolerance typically ±10-20%
- Temperature coefficient affects stability

### Practical Limitations
1. **Op-amp buffers**: Add for impedance matching
2. **Parasitic capacitance**: Limits high-frequency response
3. **Component self-resonance**: Important above 10MHz
4. **Power dissipation**: I²R losses in resistor

## Troubleshooting

### Common Issues
1. **Wrong cutoff frequency**: Check component values
2. **Poor attenuation**: Verify connections, check for loading
3. **Distortion**: Input signal too large, check power supply
4. **Oscillation**: Parasitic feedback, improve layout

### Testing Methods
```python
# Quick functionality test
test_freqs = [0.1*fc, fc, 10*fc]
for f in test_freqs:
    gain = circuit.magnitude_db(f)
    print(f"{f:.1f} Hz: {gain:.1f} dB")
```

## Further Reading
- [RC Circuit on Wikipedia](https://en.wikipedia.org/wiki/RC_circuit)
- [All About Circuits: Filters](https://www.allaboutcircuits.com/textbook/alternating-current/chpt-8/filters/)
- [Electronics Tutorials: RC Filters](https://www.electronics-tutorials.ws/filter/filter_2.html)

## Next Steps
After mastering RC filters, explore:
1. **RLC Filters**: Add inductance for resonance
2. **Active Filters**: Use op-amps for gain and buffering
3. **Higher-Order Filters**: Butterworth, Chebyshev designs
4. **Digital Filters**: DSP implementation of filter functions