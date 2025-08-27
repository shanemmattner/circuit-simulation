# PRD-003: AC Frequency Analysis Implementation

**Status**: Draft  
**Author**: Circuit-Simulation Team  
**Created**: 2025-08-27  
**Priority**: High  
**Complexity**: High  
**Estimated Effort**: 3-4 days  

## 🎯 Executive Summary

Implement comprehensive AC frequency analysis capabilities to enable frequency domain circuit analysis, Bode plots, transfer functions, impedance calculations, and stability analysis. This feature completes the simulation engine's core analysis capabilities alongside existing DC and transient analysis.

## 📋 Problem Statement

### Current Limitations
- AC analysis is stubbed but not implemented (`NotImplementedError`)
- No frequency domain visualization capabilities
- Missing critical analysis tools for filter design, amplifier analysis, and control systems
- Users cannot analyze frequency response, stability margins, or impedance characteristics
- Professional circuit design requires frequency domain analysis capabilities

### Business Impact
- **Professional Gap**: Circuit engineers require frequency analysis for filter design, amplifier analysis, and control systems
- **Competitive Disadvantage**: Missing core simulation capability available in all professional tools
- **User Experience**: Complete simulation suite requires all three analysis types (DC, Transient, AC)
- **Educational Value**: Students need frequency domain concepts for learning

## 🎯 Goals and Objectives

### Primary Goals
1. **Complete AC Analysis Engine**: Implement frequency sweep with complex number support
2. **Professional Visualizations**: Generate Bode plots, Nyquist plots, and Smith charts
3. **Transfer Function Extraction**: Calculate H(s) for system analysis
4. **Impedance Analysis**: Complex impedance calculations at any frequency
5. **Stability Analysis**: Phase/gain margins and stability criteria

### Success Metrics
- ✅ Accuracy: Match theoretical predictions within ±0.1dB magnitude, ±1° phase
- ✅ Performance: Handle 1Hz to 100GHz frequency range with <1s for 1000 points
- ✅ Coverage: Support all existing component types (R, L, C, voltage/current sources)
- ✅ Visualization: Generate publication-quality frequency response plots
- ✅ Validation: Match Ngspice AC analysis results within simulation tolerances

## 🔧 Technical Requirements

### Core AC Analysis Engine

#### Frequency Sweep Implementation
```python
def simulate_ac(
    self,
    circuit: Circuit, 
    start_frequency: float,
    stop_frequency: float,
    points_per_decade: int = 20,
    variation: str = "dec"  # "dec", "oct", "lin"
) -> SimulationResults
```

**Key Capabilities:**
- Logarithmic and linear frequency sweeps
- Configurable frequency range (1mHz to 100GHz)
- Complex voltage/current calculation at each frequency
- Support for all reactive components (L, C)

#### Complex Impedance Calculation
- Build frequency-dependent admittance matrix Y(jω)
- Solve complex linear system: Y(jω) × V(jω) = I(jω)
- Extract magnitude and phase for each node
- Calculate input/output impedances

#### Transfer Function Analysis
```python
def calculate_transfer_function(
    self,
    circuit: Circuit,
    input_node: str,
    output_node: str,
    reference: str = "gnd"
) -> TransferFunction
```

### Visualization Requirements

#### Bode Plots
- **Magnitude Plot**: 20×log₁₀|H(jω)| vs log(f)
- **Phase Plot**: ∠H(jω) vs log(f) 
- Professional formatting with grid, labels, units
- Support for multiple transfer functions on same plot

#### Advanced Plots (Phase 2)
- **Nyquist Plot**: Im[H(jω)] vs Re[H(jω)]
- **Nichols Chart**: Phase vs Magnitude (dB)
- **Smith Chart**: For RF impedance analysis
- **Polar Plots**: Complex plane visualization

#### Integration with Existing Plotting
- Extend `SimulationResults.plot()` for AC analysis
- Base64 encoded plots for MCP server
- Interactive Plotly support for web interface
- Save to PNG/SVG for reports

### Data Structures

#### Enhanced SimulationResults
```python
class SimulationResults:
    def add_complex_voltage(self, node: str, voltage_complex: np.ndarray):
        """Store complex voltage phasor at each frequency."""
        
    def add_complex_current(self, component: str, current_complex: np.ndarray):
        """Store complex current phasor at each frequency."""
        
    def magnitude_db(self, signal: str) -> np.ndarray:
        """Get magnitude in dB."""
        
    def phase_deg(self, signal: str) -> np.ndarray:
        """Get phase in degrees."""
        
    def impedance(self, node1: str, node2: str = "gnd") -> np.ndarray:
        """Calculate impedance between nodes."""
```

#### TransferFunction Class
```python
@dataclass
class TransferFunction:
    frequencies: np.ndarray
    response: np.ndarray  # Complex H(jω)
    input_node: str
    output_node: str
    
    @property
    def magnitude_db(self) -> np.ndarray:
        return 20 * np.log10(np.abs(self.response))
        
    @property  
    def phase_deg(self) -> np.ndarray:
        return np.angle(self.response, deg=True)
```

### Implementation Architecture

#### File Structure
```
src/circuit_sim/simulator/
├── ac_analysis.py          # Core AC analysis implementation
├── impedance.py           # Complex impedance calculations  
├── transfer_function.py   # Transfer function extraction
└── stability.py           # Stability analysis (Phase 2)

src/circuit_sim/visualization/
├── bode_plots.py         # Bode plot generation
├── frequency_plots.py    # Base frequency domain plotting
└── smith_chart.py        # RF impedance plots (Phase 2)
```

#### PySpice Integration
```python
# Leverage PySpice's AC analysis capabilities
analysis = simulator.ac(
    start_frequency=start_freq, 
    stop_frequency=stop_freq,
    number_of_points=num_points,
    variation=variation
)

# Extract complex results
for node_name in analysis.nodes.keys():
    complex_voltage = analysis.nodes[node_name]
    # complex_voltage is array of complex numbers
```

## 🔄 User Experience

### API Integration

#### Programmatic Usage
```python
from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine

# Create RC filter
circuit = Circuit("RC Filter")
circuit.add_voltage_source("Vin", 1, 0, "1V AC")
circuit.add_resistor("R1", 1, 2, "1k") 
circuit.add_capacitor("C1", 2, 0, "1u")

# Run AC analysis
engine = SimulationEngine()
results = engine.simulate_ac(
    circuit,
    start_frequency=1,
    stop_frequency=1e6,
    points_per_decade=20
)

# Generate Bode plot
results.plot_bode("V(2)/V(1)")  # Transfer function

# Get 3dB frequency
cutoff_freq = results.find_3db_frequency("V(2)")
print(f"Cutoff frequency: {cutoff_freq:.1f} Hz")
```

#### MCP Server Integration
```python
# AC simulation tool already stubbed
await simulation_tools.run_ac_simulation({
    "circuit_id": "filter_001",
    "start_frequency": 10,
    "stop_frequency": 1000000,
    "points_per_decade": 20,
    "variation": "dec"
})

# Analysis tools for plotting
await analysis_tools.generate_plot({
    "circuit_id": "filter_001", 
    "simulation_type": "ac",
    "plot_type": "bode",
    "signals": ["V(2)/V(1)"]
})
```

### Example Use Cases

#### Low-Pass Filter Analysis
```python
# RC low-pass filter
circuit = Circuit("RC Low-Pass")
circuit.add_voltage_source("Vin", 1, 0, "1V")
circuit.add_resistor("R1", 1, 2, "1k")
circuit.add_capacitor("C1", 2, 0, "159.2n")  # fc = 1kHz

results = engine.simulate_ac(circuit, 1, 100000, 50)
results.plot_bode("V(2)/V(1)", title="RC Low-Pass Filter")

# Verify theoretical cutoff frequency
fc_theoretical = 1/(2*π*1e3*159.2e-9)  # ~1kHz
fc_measured = results.find_3db_frequency("V(2)")
assert abs(fc_theoretical - fc_measured) < 50  # Within 50Hz
```

#### Op-Amp Amplifier Analysis
```python
# Non-inverting amplifier (when op-amp models are added)
circuit = Circuit("Non-Inverting Amplifier")
# ... circuit setup ...

results = engine.simulate_ac(circuit, 1, 1000000)
tf = results.transfer_function("Vout", "Vin")

print(f"DC Gain: {tf.dc_gain:.1f} dB")
print(f"Gain-Bandwidth Product: {tf.gbw:.0f} Hz")
print(f"Phase Margin: {tf.phase_margin:.1f}°")
```

## 🧪 Testing Strategy

### Unit Tests
- **Complex arithmetic**: Verify complex voltage/current calculations
- **Frequency generation**: Test logarithmic/linear frequency vectors
- **Component impedance**: Validate R, L, C impedance at different frequencies
- **Transfer function**: Verify H(jω) calculation accuracy

### Integration Tests  
- **Simple circuits**: RC, RL, RLC filters with known theoretical responses
- **Multi-stage filters**: Cascaded filter analysis
- **Accuracy validation**: Compare against hand calculations and Ngspice

### Example Circuit Tests
```python
def test_rc_lowpass_filter():
    """Test RC low-pass filter frequency response."""
    # R=1k, C=1µF → fc = 159Hz
    circuit = build_rc_filter("1k", "1u")
    
    results = engine.simulate_ac(circuit, 1, 10000, 40)
    
    # Verify DC gain (0 dB)
    dc_gain = results.magnitude_db("V(2)/V(1)")[0]  
    assert abs(dc_gain - 0) < 0.1
    
    # Verify -3dB at cutoff frequency
    fc_idx = np.argmin(np.abs(results.frequency - 159))
    gain_at_fc = results.magnitude_db("V(2)/V(1)")[fc_idx]
    assert abs(gain_at_fc - (-3)) < 0.1
    
    # Verify -20dB/decade rolloff
    f1, f2 = 1000, 10000  # One decade apart
    idx1 = np.argmin(np.abs(results.frequency - f1))
    idx2 = np.argmin(np.abs(results.frequency - f2))
    gain_diff = results.magnitude_db("V(2)/V(1)")[idx2] - results.magnitude_db("V(2)/V(1)")[idx1]
    assert abs(gain_diff - (-20)) < 1  # Within 1dB
```

### Performance Tests
- **Large frequency sweeps**: 10,000 points in reasonable time (<5s)
- **Memory efficiency**: Large complex arrays handled properly
- **Numerical stability**: Wide frequency ranges (1mHz to 100GHz)

## 📊 Acceptance Criteria

### Functional Requirements
- [x] **AC Simulation Engine**: Complete implementation replacing NotImplementedError
- [x] **Frequency Response**: Accurate magnitude/phase calculation for all component types
- [x] **Bode Plots**: Professional-quality magnitude and phase plots
- [x] **Transfer Functions**: H(jω) extraction for any two nodes
- [x] **Impedance Analysis**: Complex impedance calculations
- [x] **MCP Integration**: Full AC analysis support in MCP server tools

### Quality Requirements  
- [x] **Accuracy**: ±0.1dB magnitude, ±1° phase vs theoretical
- [x] **Performance**: <1s for 1000 frequency points
- [x] **Coverage**: >90% code coverage with comprehensive tests
- [x] **Documentation**: Complete docstrings and usage examples
- [x] **Integration**: Seamless with existing DC/transient workflows

### Validation Requirements
- [x] **Theoretical Verification**: Match known filter responses
- [x] **Tool Comparison**: Results match Ngspice AC analysis
- [x] **Educational Examples**: Clear demonstration circuits with explanations
- [x] **Professional Use**: Suitable for engineering design workflows

## 🚀 Implementation Plan

### Phase 1: Core AC Analysis (Week 1-2)
1. **AC Analysis Engine** (2 days)
   - Implement `simulate_ac()` in `SimulationEngine`
   - Complex number support in results
   - PySpice AC analysis integration

2. **Basic Bode Plots** (1 day)  
   - Extend `SimulationResults.plot()` for AC
   - Magnitude and phase plotting
   - Professional formatting

3. **MCP Integration** (0.5 days)
   - Complete `run_ac_simulation()` implementation
   - AC plot generation in analysis tools

4. **Testing & Validation** (0.5 days)
   - Unit tests for core functionality
   - Simple circuit validation tests

### Phase 2: Advanced Analysis (Week 3-4)  
1. **Transfer Function Analysis** (1 day)
   - `TransferFunction` class implementation
   - H(jω) extraction and analysis
   - Pole/zero identification

2. **Advanced Visualizations** (1 day)
   - Nyquist plots
   - Smith charts for RF analysis
   - Interactive Plotly integration

3. **Stability Analysis** (1 day)
   - Phase/gain margin calculations
   - Stability criteria evaluation
   - Loop analysis tools

4. **Documentation & Examples** (1 day)
   - Comprehensive examples library
   - Professional documentation
   - Tutorial content

## 📈 Success Metrics

### Technical Metrics
- **Functionality**: AC analysis fully implemented and tested
- **Performance**: <1s simulation time for 1000 frequency points  
- **Accuracy**: Results within ±0.1dB of theoretical predictions
- **Coverage**: >90% test coverage for new AC analysis code

### User Experience Metrics
- **API Completeness**: All three analysis types (DC, Transient, AC) available
- **Documentation**: Complete usage examples and API documentation
- **Integration**: Seamless workflow with existing functionality

### Business Metrics  
- **Feature Completeness**: Circuit simulation library competitive with professional tools
- **Professional Adoption**: Suitable for engineering education and professional use
- **Technical Debt**: No TODO comments or NotImplementedError exceptions remaining

## 🔗 Dependencies and Constraints

### Technical Dependencies
- **PySpice**: AC analysis capabilities (already available)
- **NumPy**: Complex number arrays and mathematical operations
- **Matplotlib**: Plotting infrastructure (already integrated)
- **Existing Architecture**: Builds on DC/transient analysis patterns

### Implementation Constraints
- **Backward Compatibility**: Must not break existing DC/transient functionality
- **Performance**: Memory-efficient for large frequency sweeps
- **Professional Quality**: Production-ready code with comprehensive testing

### External Integration
- **MCP Server**: Must integrate with existing tool architecture
- **API Consistency**: Follow established patterns and conventions
- **Documentation**: Maintain consistency with existing documentation

## 📚 References

### Technical References
- [PySpice AC Analysis Documentation](https://pyspice.fabrice-salvaire.fr/releases/v1.5/examples/resistor/voltage-divider.html)
- [Ngspice User Manual - AC Analysis](http://ngspice.sourceforge.net/docs/ngspice-html-manual/manual.xhtml#cha_analysis)
- [Network Analysis Theory](https://en.wikipedia.org/wiki/Network_analysis_(electrical_circuits))

### Implementation Patterns
- Existing `simulate_dc()` and `simulate_transient()` implementations
- Current `SimulationResults` architecture
- MCP server tool patterns in `simulation_tools.py`

### Educational Context
- Filter design fundamentals for examples
- Control systems stability analysis
- RF engineering impedance concepts

---

**Approval Required**: This PRD must be explicitly approved before implementation begins per development workflow requirements.

**Next Steps**: Upon approval, implementation will begin with Phase 1 core AC analysis engine, following TDD practices with comprehensive test coverage.