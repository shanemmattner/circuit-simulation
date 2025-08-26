# PRD-002: PySpice Integration

## Feature Overview
**Name**: PySpice Simulation Backend  
**Status**: In Development  
**Priority**: P0 - Core functionality required for MVP  
**Target Release**: MVP v0.2.0  

## Problem Statement
The Circuit API can define circuits but cannot simulate them. Users need actual simulation results (voltages, currents, frequency response) to validate their designs.

## User Story
As a developer, I want my defined circuits to be automatically simulated using PySpice, so I can get real numerical results without writing SPICE netlists or understanding PySpice's complex API.

## Success Metrics
- Voltage divider simulation matches hand calculations within 0.1%
- RC circuit time constant verified within 1%
- Simulation completes in <1 second for circuits with <100 components
- Zero PySpice knowledge required from users

## Requirements

### Functional Requirements

#### 1. Value Parser
- Convert human-readable values to numeric
  - Resistance: "1k" → 1000, "4.7M" → 4.7e6
  - Capacitance: "10u" → 10e-6, "100n" → 100e-9
  - Inductance: "1m" → 1e-3, "100u" → 100e-6
  - Voltage/Current: "5V" → 5, "10mA" → 10e-3
- Handle scientific notation: "1e3", "2.2e-6"
- Case insensitive units

#### 2. PySpice Circuit Generation
- Convert our Circuit to PySpice Circuit
- Map components to PySpice equivalents
- Handle node naming/numbering
- Preserve component names

#### 3. Simulation Capabilities
- **DC Operating Point**
  - Calculate steady-state voltages
  - Calculate branch currents
- **Transient Analysis**
  - Time-domain simulation
  - Configurable time step and duration
  - Initial conditions support
- **AC Analysis** (Phase 2)
  - Frequency response
  - Magnitude and phase

#### 4. Results Extraction
- SimulationResults class with:
  - Node voltages as numpy arrays
  - Branch currents as numpy arrays
  - Time/frequency vectors
  - Metadata (analysis type, parameters)

#### 5. Basic Plotting
- Simple matplotlib plots
- Time-domain waveforms
- Automatic axis labels
- Multiple signals on same plot

### Non-Functional Requirements
- Performance: <100ms overhead for PySpice conversion
- Memory: Handle results for 1M data points
- Error handling: Clear messages for convergence failures
- Compatibility: Work with PySpice 1.5+
- Testing: Mock PySpice for unit tests

## Technical Design

### Architecture
```
Circuit (user API)
    ↓
ValueParser (convert "1k" → 1000)
    ↓
PySpiceBuilder (create PySpice circuit)
    ↓
SimulationEngine (run simulation)
    ↓
ResultsExtractor (extract data)
    ↓
SimulationResults (user-facing results)
```

### Key Components

#### 1. Value Parser Module
```python
# src/circuit_sim/parser.py
def parse_value(value_str: str) -> float:
    """Parse human-readable value to float."""
    # Handle suffixes: k, M, G, m, u, n, p
    # Handle units: V, A, Ohm, F, H
```

#### 2. PySpice Builder
```python
# src/circuit_sim/simulator/builder.py
class PySpiceBuilder:
    def build_circuit(self, circuit: Circuit) -> PySpiceCircuit:
        """Convert our Circuit to PySpice Circuit."""
```

#### 3. Simulation Engine
```python
# src/circuit_sim/simulator/engine.py
class SimulationEngine:
    def simulate_dc(self, circuit: Circuit) -> SimulationResults:
    def simulate_transient(self, circuit: Circuit, **params) -> SimulationResults:
```

#### 4. Results Class
```python
# src/circuit_sim/results.py
class SimulationResults:
    @property
    def time(self) -> np.ndarray:
    def voltage(self, node: Union[int, str]) -> np.ndarray:
    def current(self, component: str) -> np.ndarray:
    def plot(self, *signals) -> None:
```

## Implementation Plan

### Phase 1: Foundation (2 hours)
1. Create value parser with tests
2. Set up simulator package structure
3. Create PySpiceBuilder skeleton
4. Mock PySpice for testing

### Phase 2: PySpice Integration (3 hours)
5. Implement component mapping
6. Build PySpice netlist generation
7. Add DC operating point
8. Extract DC results

### Phase 3: Transient Analysis (2 hours)
9. Add transient simulation
10. Handle time vectors
11. Extract time-domain results
12. Add initial conditions

### Phase 4: Results & Plotting (2 hours)
13. Complete SimulationResults class
14. Add matplotlib plotting
15. Create plot formatting
16. Add multi-signal plots

### Phase 5: Testing & Examples (2 hours)
17. Integration tests with real circuits
18. Voltage divider verification
19. RC circuit time constant test
20. Update example scripts
21. Documentation

## Test Cases

### Unit Tests
1. **Value Parser**
   - "1k" → 1000
   - "10uF" → 10e-6
   - "3.3V" → 3.3
   - Invalid format raises ValueError

2. **Component Mapping**
   - Resistor → PySpice R
   - Capacitor → PySpice C
   - Voltage source → PySpice V

### Integration Tests
1. **Voltage Divider**
   - 10V source, two 1k resistors
   - Output = 5V ±0.1%

2. **RC Circuit**
   - Step response
   - Time constant τ = RC ±1%

3. **Current Source**
   - 1mA into 1k resistor
   - Voltage = 1V ±0.1%

## Acceptance Criteria
- [ ] Value parser handles all common formats
- [ ] DC simulation produces correct voltages
- [ ] Transient simulation shows correct waveforms
- [ ] Results can be plotted
- [ ] All tests pass
- [ ] Examples work with real simulation

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| PySpice API changes | High | Pin version, abstract interface |
| Convergence failures | Medium | Provide convergence hints, clear errors |
| Large memory usage | Medium | Stream results, limit data points |
| Ngspice not installed | High | Check at import, provide install instructions |

## Dependencies
- PySpice >= 1.5
- numpy >= 1.24
- matplotlib >= 3.6

## Future Enhancements
- AC analysis with Bode plots
- Monte Carlo simulation
- Parameter sweeps
- SPICE model library integration
- Export to SPICE netlist

---
**Created**: 2024-08-26  
**Author**: AI Assistant  
**Approval**: PENDING