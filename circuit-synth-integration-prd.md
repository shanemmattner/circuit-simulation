# Circuit-Synth + Circuit-Simulation Integration PRD

## Product Vision

Create two independent, professional Python libraries that work seamlessly together:
- **circuit-synth**: Define circuits in elegant Python syntax
- **circuit-simulation**: Simulate circuits with Python-native results and visualization
- **Integration**: Dead-simple, one-line connection between them

**Target Users**: Professional engineers who want Python-native circuit design and simulation workflow.

## Architecture Strategy

### Independent Libraries with Clean Interface

```
┌─────────────────┐    SPICE     ┌─────────────────────┐
│   circuit-synth │   Netlist    │ circuit-simulation  │
│                 │ ──────────► │                     │
│ • Circuit def   │              │ • Python simulation │
│ • Component lib │              │ • Interactive plots │
│ • SPICE export  │              │ • Professional reports │
└─────────────────┘              └─────────────────────┘
```

### Key Principles

1. **Zero Coupling**: Libraries have no import dependencies on each other
2. **SPICE Contract**: SPICE netlist is the interface between libraries
3. **Python Native**: Users stay in Python, get Python objects back
4. **Professional Quality**: Industrial-strength simulation with interactive visualization
5. **Simple Integration**: One line of code to connect circuit-synth to circuit-simulation

## User Workflow (Target Experience)

### Simple Example: Voltage Divider Analysis

```python
# Step 1: Define circuit in circuit-synth
from circuit_synth import circuit, Component, Net

@circuit
def voltage_divider():
    """Simple 2:1 voltage divider"""
    r1 = Component("Device:R", ref="R", value="10k")
    r2 = Component("Device:R", ref="R", value="10k")
    
    vin = Net("VIN")
    vout = Net("VOUT")
    gnd = Net("GND")
    
    r1[1] += vin
    r1[2] += vout
    r2[1] += vout
    r2[2] += gnd

# Step 2: Export to SPICE
circuit = voltage_divider()
spice_netlist = circuit.to_spice()
print("Generated SPICE netlist - ready for any simulator")

# Step 3: Simulate with circuit-simulation
from circuit_simulation import Simulator

sim = Simulator.from_spice(spice_netlist)
dc_result = sim.dc_analysis(vin_sweep=(0, 5, 0.1))
ac_result = sim.ac_analysis(start="1Hz", stop="1MHz")

# Step 4: Analyze results in Python
print(f"VOUT at VIN=3.3V: {dc_result.get_voltage('VOUT', vin=3.3):.2f}V")
print(f"Gain at 1kHz: {ac_result.get_gain('VOUT', 'VIN', '1kHz'):.1f}dB")

# Step 5: Interactive visualization
dc_result.plot_sweep("VOUT")  # Interactive voltage sweep
ac_result.plot_frequency_response("VOUT")  # Bode plot

# Step 6: Professional report
report = sim.generate_report([dc_result, ac_result])
report.save("voltage_divider_analysis.html")
print("Professional report saved!")
```

### Professional Example: Op-Amp Circuit

```python
@circuit
def non_inverting_amplifier():
    """Non-inverting op-amp with gain = 11"""
    opamp = Component("Amplifier_Operational:LM358", ref="U")
    r1 = Component("Device:R", ref="R", value="1k")
    r2 = Component("Device:R", ref="R", value="10k")
    
    # Circuit connections...
    return circuit

# Complete analysis workflow
circuit = non_inverting_amplifier()
sim = Simulator.from_spice(circuit.to_spice())

# Professional analysis suite
analyses = {
    "dc": sim.dc_analysis(),
    "ac": sim.ac_analysis("0.1Hz", "10MHz", points_per_decade=20),
    "transient": sim.transient_analysis("10ms", "1us"),
    "noise": sim.noise_analysis("VOUT", "GND")
}

# Interactive dashboard
dashboard = sim.create_dashboard(analyses)
dashboard.show()  # Opens browser with interactive plots

# Export for documentation
report = sim.generate_professional_report(analyses)
report.include_schematic(circuit.to_svg())  # Include circuit diagram
report.include_bom(circuit.get_bom())       # Bill of materials
report.save("opamp_design_validation.pdf")
```

## Implementation Plan

### Phase 1: Minimal Working Example (This Week)

**Goal**: Prove the architecture with voltage divider example

#### circuit-synth Changes Required:
1. **Add SPICE Export Method**
   ```python
   class Circuit:
       def to_spice(self) -> str:
           """Export circuit to SPICE netlist format"""
           # Generate .subckt or .net file
   ```

2. **SPICE Component Mapping**
   ```python
   # Map circuit-synth components to SPICE models
   SPICE_COMPONENT_MAP = {
       "Device:R": "R{ref} {pin1} {pin2} {value}",
       "Device:C": "C{ref} {pin1} {pin2} {value}",
       "Device:L": "L{ref} {pin1} {pin2} {value}",
   }
   ```

#### circuit-simulation Changes Required:
1. **SPICE Import Method**
   ```python
   class Simulator:
       @classmethod
       def from_spice(cls, netlist: str) -> 'Simulator':
           """Create simulator from SPICE netlist"""
   ```

2. **Hardcoded Analysis Methods** (remove plugin system)
   ```python
   def dc_analysis(self, **params) -> DCResult:
   def ac_analysis(self, start, stop, points=100) -> ACResult:
   def transient_analysis(self, duration, timestep) -> TransientResult:
   ```

3. **Result Objects with Python API**
   ```python
   class ACResult:
       def get_magnitude(self, node: str, freq: str) -> float:
       def get_phase(self, node: str, freq: str) -> float:
       def plot_bode(self, nodes: List[str]) -> None:
   ```

### Phase 2: Professional Features (Next 2 Weeks)

1. **Extended Analysis Types**
   - Noise analysis
   - Sensitivity analysis
   - Temperature sweep

2. **Interactive Visualization**
   - Plotly integration
   - Dashboard view with multiple plots
   - Export to PNG/PDF

3. **Professional Reporting**
   - HTML reports with embedded plots
   - Include circuit schematics
   - BOM integration

### Phase 3: Production Ready (Following Month)

1. **Component Libraries**
   - Real SPICE models for common components
   - Manufacturer model integration

2. **Advanced Features**
   - Monte Carlo analysis
   - Optimization loops
   - Batch simulation

3. **Documentation & Examples**
   - Complete API documentation
   - Circuit design patterns
   - Professional use cases

## Technical Specifications

### SPICE Netlist Format

```spice
* Generated by circuit-synth v1.0
* Circuit: voltage_divider

.title Voltage Divider

* Components
R1 VIN VOUT 10k
R2 VOUT GND 10k

* Analysis
.dc VIN 0 5 0.1
.ac dec 10 1 1MEG
.print dc v(VOUT)
.print ac vdb(VOUT) vp(VOUT)

.end
```

### API Design Principles

#### circuit-synth API (No changes to existing syntax)
- Keep existing `@circuit`, `Component`, `Net`, `+=` syntax
- Add export methods: `to_spice()`, `to_json()`
- Maintain KiCad integration

#### circuit-simulation API (Simplified from current)
- Remove plugin system complexity
- Hardcode essential analysis types
- Return rich Python objects
- Plotly for interactive visualization

### Error Handling Strategy

```python
# Fail fast with clear messages
try:
    sim = Simulator.from_spice(netlist)
    result = sim.ac_analysis("1Hz", "1MHz")
except SPICEParseError as e:
    print(f"Invalid SPICE netlist at line {e.line_number}: {e.message}")
    print(f"Suggestion: {e.suggestion}")
except ConvergenceError as e:
    print(f"Simulation failed to converge: {e.message}")
    print(f"Try: {e.suggestions}")
except SimulationError as e:
    print(f"Simulation error: {e.message}")
```

## Testing Strategy

### Integration Tests (No circular dependencies)

```python
def test_voltage_divider_integration():
    """Test complete workflow with fixture"""
    # Use known-good SPICE netlist as fixture
    netlist = load_test_fixture("voltage_divider.spice")
    
    sim = Simulator.from_spice(netlist)
    result = sim.dc_analysis(vin_sweep=(0, 5, 1))
    
    # Verify expected behavior
    assert abs(result.get_voltage("VOUT", vin=4.0) - 2.0) < 0.01
```

### Contract Tests
- Define SPICE format expectations
- Test both libraries against same fixture
- Ensure compatibility

## Success Metrics

### Phase 1 Success Criteria:
- [ ] Voltage divider example works end-to-end
- [ ] SPICE export from circuit-synth works
- [ ] SPICE import to circuit-simulation works  
- [ ] Basic DC and AC analysis functional
- [ ] Interactive plot displays correctly

### Phase 2 Success Criteria:
- [ ] Professional op-amp example works
- [ ] All analysis types implemented (DC, AC, Transient, Noise)
- [ ] HTML report generation functional
- [ ] Dashboard view working

### Phase 3 Success Criteria:
- [ ] Component library with real SPICE models
- [ ] Documentation complete
- [ ] Performance benchmarks met
- [ ] Ready for professional use

## File Structure

```
circuit-simulation/
├── src/circuit_sim/
│   ├── simulator.py          # Main Simulator class
│   ├── results/             
│   │   ├── dc_result.py      # DC analysis results
│   │   ├── ac_result.py      # AC analysis results
│   │   └── transient_result.py
│   ├── visualization/        # Plotly integration
│   ├── reports/             # HTML/PDF generation
│   └── models/              # SPICE model library
├── examples/
│   ├── voltage_divider.py   # Phase 1 example
│   ├── opamp_circuit.py     # Phase 2 example
│   └── professional_workflow.py
└── tests/
    ├── fixtures/            # Test SPICE netlists
    └── integration/         # End-to-end tests

circuit-synth/ (submodule)
├── src/circuit_synth/
│   ├── core/circuit.py      # Add to_spice() method
│   ├── spice/               # New: SPICE export
│   │   ├── exporter.py      # SPICE netlist generation
│   │   └── component_map.py # Component to SPICE mapping
└── examples/
    └── integration_demo.py  # Show circuit-synth → circuit-simulation
```

## Next Steps

### Immediate (This Week):
1. **Create voltage_divider.py example** in circuit-simulation
2. **Add to_spice() method** to circuit-synth
3. **Add from_spice() method** to circuit-simulation  
4. **Test end-to-end workflow manually**
5. **Document any issues or refinements needed**

### This Sprint:
1. **Implement basic result objects** (DCResult, ACResult)
2. **Add Plotly visualization**
3. **Create integration documentation**
4. **Build professional op-amp example**

### Following Sprint:
1. **Add remaining analysis types**
2. **Implement HTML report generation**
3. **Create component SPICE model library**
4. **Performance testing and optimization**

## Risk Mitigation

### Technical Risks:
- **SPICE format compatibility**: Use standard SPICE syntax, test with ngspice
- **Result parsing complexity**: Use PySpice or build simple parser
- **Performance concerns**: Profile and optimize after basic functionality works

### User Experience Risks:
- **Integration complexity**: Keep it to one line of code
- **Error messages**: Test with real circuits, improve error text iteratively
- **Documentation gaps**: Write examples first, docs follow

This PRD provides the complete roadmap for creating two independent, professional libraries with seamless integration. The key insight is that the "integration" is so simple it barely needs to exist - just clear data exchange via SPICE netlists.