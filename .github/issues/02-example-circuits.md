# Feature: Comprehensive Example Circuits Library

## 🎯 Objective
Build a library of 10+ production-ready example circuits that demonstrate the full capabilities of the simulation engine and serve as templates for users.

## 📋 Requirements

### Circuit Categories

#### Basic Circuits (3)
- [ ] LED Driver with current limiting
- [ ] Voltage divider with load
- [ ] Wheatstone bridge

#### Filter Circuits (2)
- [ ] 4th-order Butterworth low-pass filter
- [ ] Active bandpass filter (Sallen-Key)

#### Amplifier Circuits (2)
- [ ] Class AB audio amplifier
- [ ] Instrumentation amplifier with guard ring

#### Power Circuits (2)
- [ ] Buck converter (step-down)
- [ ] Linear voltage regulator (LM317 style)

#### Oscillator Circuit (1)
- [ ] Wien bridge oscillator

## 🛠️ Technical Implementation

### File Structure
```
examples/
├── basic/
│   ├── led_driver.py
│   ├── voltage_divider.py
│   └── wheatstone_bridge.py
├── filters/
│   ├── butterworth_lpf.py
│   └── sallen_key_bpf.py
├── amplifiers/
│   ├── class_ab_amp.py
│   └── instrumentation_amp.py
├── power/
│   ├── buck_converter.py
│   └── linear_regulator.py
├── oscillators/
│   └── wien_bridge.py
├── utils/
│   └── circuit_helpers.py
└── README.md
```

### Example Circuit Template
```python
"""
LED Driver Circuit
==================
A constant-current LED driver using a transistor current mirror.

Specifications:
- Input: 5V
- LED current: 20mA ±5%
- Temperature stable
- Multiple LED support
"""

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine

def create_led_driver(num_leds=1, target_current="20mA"):
    """
    Create an LED driver circuit.
    
    Args:
        num_leds: Number of LEDs in series
        target_current: Desired LED current
    
    Returns:
        Configured Circuit object
    """
    circuit = Circuit("LED Driver")
    
    # Power supply
    circuit.add_voltage_source("V1", "vcc", "gnd", "5V")
    
    # Current reference (using bandgap)
    circuit.add_resistor("R_REF", "vcc", "ref", "1.5k")
    circuit.add_component("D_REF", "diode", "ref", "gnd", 
                         model="1N4148")
    
    # Current mirror
    circuit.add_component("Q1", "bjt", "ref", "ref", "gnd",
                         model="2N3904")
    circuit.add_component("Q2", "bjt", "vcc", "ref", "led_cathode",
                         model="2N3904")
    
    # LED chain
    for i in range(num_leds):
        if i == 0:
            pos, neg = "vcc", f"led_{i}"
        else:
            pos, neg = f"led_{i-1}", f"led_{i}"
        
        circuit.add_component(f"LED_{i+1}", "diode", pos, neg,
                             model="LED_RED")
    
    # Connect last LED to current sink
    circuit.add_connection(f"led_{num_leds-1}", "led_cathode")
    
    return circuit

def simulate_led_driver():
    """Run simulation and generate report."""
    circuit = create_led_driver(num_leds=3)
    engine = SimulationEngine()
    
    # DC operating point
    dc_results = engine.simulate_dc(circuit)
    
    # Temperature sweep
    temp_results = []
    for temp in range(-40, 85, 5):
        engine.set_temperature(temp)
        result = engine.simulate_dc(circuit)
        temp_results.append({
            'temp': temp,
            'led_current': result.get_current('LED_1')
        })
    
    # Generate plots
    plot_led_characteristics(dc_results, temp_results)
    
    return dc_results, temp_results

if __name__ == "__main__":
    results = simulate_led_driver()
    print(f"LED Current: {results[0].get_current('LED_1')}")
```

### Documentation Requirements
Each example must include:
- [ ] Circuit schematic (ASCII art or generated)
- [ ] Theory of operation
- [ ] Component selection rationale
- [ ] Simulation results
- [ ] Parametric sweeps
- [ ] Performance metrics
- [ ] Common variations

## 📊 Success Criteria
- [ ] All 10 circuits simulate without errors
- [ ] Results match theoretical predictions (±5%)
- [ ] Examples cover beginner to advanced
- [ ] Code is well-commented and educational
- [ ] Each circuit has complete documentation
- [ ] Jupyter notebooks for interactive exploration

## 🔗 Dependencies
- Depends on: Core simulation engine
- Blocks: None
- Related: #1 (CLI Interface), #5 (Report Generator)

## 📚 Resources
- [Art of Electronics](https://artofelectronics.net/)
- [Analog Devices Circuit Notes](https://www.analog.com/circuits)
- [TI Reference Designs](https://www.ti.com/reference-designs)

## ✅ Acceptance Criteria
1. Each circuit has realistic component values
2. Simulations complete in <5 seconds
3. Results are physically accurate
4. Examples are pedagogically valuable
5. Code follows best practices

## 🏷️ Labels
`enhancement` `examples` `documentation` `priority-high`

## 📝 Branch
`feature/example-circuits`

## ⏱️ Estimated Effort
**Time**: 3-4 days
**Complexity**: Medium
**Priority**: High