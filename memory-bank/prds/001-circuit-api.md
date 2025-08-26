# PRD-001: Basic Circuit Simulation API

## Feature Overview
**Name**: Basic Circuit Simulation API  
**Status**: In Review  
**Priority**: P0 - Foundation for all other features  
**Target Release**: MVP v0.1.0  

## Problem Statement
Users need a simple, intuitive way to define electronic circuits in Python and run simulations without learning SPICE syntax or dealing with complex configuration.

## User Story
As a developer, I want to define circuits in Python code and run simulations with minimal complexity, so I can quickly validate circuit behavior and get results in a format I can work with.

## Success Metrics
- User can define a simple RC circuit in <5 lines of code
- Simulation runs in <1 second for circuits with <100 components
- 100% of basic components (R, C, L, V, I) supported
- Zero SPICE knowledge required to use

## Requirements

### Functional Requirements

#### 1. Circuit Definition
- **Create Circuit**: Initialize circuit with a descriptive name
- **Add Components**: Support basic passive and source components
  - Resistors (R)
  - Capacitors (C)
  - Inductors (L)
  - Voltage sources (V)
  - Current sources (I)
- **Node Management**: 
  - Integer node numbering (0, 1, 2, ...)
  - Node 0 is ground by convention
  - Support 'gnd' as alias for node 0
- **Value Parsing**: Accept human-readable values
  - Resistances: "1k", "10k", "4.7M"
  - Capacitances: "10u", "100n", "1p"
  - Inductances: "1m", "100u", "10n"
  - Voltages: "5V", "3.3V", "-12V"
  - Currents: "10mA", "1A", "50uA"

#### 2. Simulation Capabilities
- **DC Operating Point**: Calculate steady-state voltages and currents
- **Transient Analysis**: Time-domain simulation with configurable time steps
- **AC Analysis**: Frequency response (magnitude and phase)
- **Auto Backend Selection**: Choose Ngspice for all initial simulations

#### 3. Results Interface
- **Data Access**:
  - Get voltage at any node
  - Get current through any component
  - Access time/frequency vectors
- **Data Format**: Return numpy arrays for compatibility
- **Basic Visualization**: Simple plot method for quick viewing

### Non-Functional Requirements
- **Performance**: <1 second for circuits with <100 components
- **Usability**: Intuitive API that follows Python conventions
- **Reliability**: Clear error messages for invalid circuits
- **Maintainability**: Clean separation between API and backend
- **Documentation**: Docstrings for all public methods
- **Type Safety**: Type hints for better IDE support

## API Design

### Core Interface
```python
from circuit_sim import Circuit

# Create circuit
circuit = Circuit("RC Low-Pass Filter")

# Add components using method chaining (optional)
circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
circuit.add_capacitor("C1", node1=2, node2=0, capacitance="1u")

# Run simulation
results = circuit.simulate(
    analysis="transient",
    stop_time="10ms",
    step_time="10us"
)

# Access results
time = results.time  # numpy array
v_out = results.voltage(2)  # Voltage at node 2
i_r1 = results.current("R1")  # Current through R1

# Quick visualization
results.plot()  # Opens matplotlib/plotly figure
```

### Method Signatures
```python
class Circuit:
    def __init__(self, name: str) -> None
    
    def add_voltage_source(
        self, 
        name: str, 
        positive: int, 
        negative: int, 
        dc_value: str
    ) -> 'Circuit'
    
    def add_resistor(
        self, 
        name: str, 
        node1: int, 
        node2: int, 
        resistance: str
    ) -> 'Circuit'
    
    def simulate(
        self, 
        analysis: str, 
        **kwargs
    ) -> SimulationResults

class SimulationResults:
    @property
    def time(self) -> np.ndarray
    
    def voltage(self, node: int) -> np.ndarray
    def current(self, component: str) -> np.ndarray
    def plot(self) -> None
```

## Implementation Plan

### Task Breakdown (~15 min each)

#### Setup Tasks
1. Create project structure (src/, tests/)
2. Set up virtual environment and dependencies
3. Create initial Circuit class skeleton
4. Set up pytest infrastructure

#### Core Implementation
5. Implement value parser for human-readable units
6. Create component classes (Resistor, Capacitor, etc.)
7. Implement Circuit.add_resistor method
8. Implement Circuit.add_capacitor method
9. Implement Circuit.add_inductor method
10. Implement Circuit.add_voltage_source method
11. Implement Circuit.add_current_source method

#### PySpice Integration
12. Create PySpice wrapper module
13. Implement netlist generation from Circuit
14. Implement DC operating point simulation
15. Implement transient analysis simulation
16. Implement AC analysis simulation

#### Results Processing
17. Create SimulationResults class
18. Implement voltage extraction
19. Implement current extraction
20. Add basic plotting with matplotlib

#### Testing & Documentation
21. Write tests for value parser
22. Write tests for component creation
23. Write tests for circuit building
24. Write tests for simulations
25. Write integration test for complete flow
26. Add docstrings and type hints
27. Create example circuits

## Test Cases

### Unit Tests
1. **Value Parser**:
   - Parse "1k" → 1000
   - Parse "10uF" → 1e-5
   - Handle invalid formats

2. **Component Creation**:
   - Create resistor with valid nodes
   - Reject negative resistance
   - Validate node numbers

3. **Circuit Building**:
   - Add multiple components
   - Detect missing ground
   - Handle duplicate names

### Integration Tests
1. **Voltage Divider**: 
   - Two resistors, DC source
   - Verify output voltage = Vin * R2/(R1+R2)

2. **RC Filter**:
   - Step response
   - Verify time constant τ = RC

3. **RLC Circuit**:
   - AC analysis
   - Verify resonant frequency

## Acceptance Criteria
- [ ] All component types can be added to circuit
- [ ] All three analysis types work
- [ ] Results match hand calculations for test circuits
- [ ] API requires zero SPICE knowledge
- [ ] All tests pass with >80% coverage
- [ ] Documentation complete with examples

## Out of Scope
- Advanced components (transistors, op-amps)
- Subcircuits and hierarchical designs
- Parameter sweeps and optimization
- Monte Carlo analysis
- Temperature analysis
- Custom models
- SPICE netlist import/export

## Dependencies
- PySpice >= 1.5
- numpy >= 1.24
- matplotlib >= 3.6 (for basic plotting)

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| PySpice complexity | High | Medium | Create thin wrapper, extensive testing |
| Value parsing errors | Medium | Medium | Robust parser with clear error messages |
| Performance issues | Medium | Low | Profile and optimize critical paths |
| User confusion | Medium | Medium | Clear examples and documentation |

## Timeline
- Setup & Structure: 1 hour
- Core Implementation: 2 hours  
- Testing & Documentation: 1 hour
- **Total**: 4 hours

## Future Enhancements
- Support for transistors and IC models
- Subcircuit definitions
- Parameter sweeps
- Interactive Plotly visualizations
- Export to SPICE netlist
- Import from KiCad schematics

---
**Created**: 2024-08-26  
**Author**: AI Assistant  
**Approval**: PENDING