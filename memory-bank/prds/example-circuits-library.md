# PRD: Example Circuits Library
**Feature**: Comprehensive Circuit Examples Collection  
**Issue**: #2  
**Priority**: High (MVP)  
**Created**: 2025-01-27  
**Status**: Pending Approval

## Executive Summary
Create a comprehensive library of 10 working circuit examples that demonstrate the full capabilities of the circuit-simulation library. These examples will serve as both educational resources and practical templates for users building their own circuits.

## Problem Statement
Currently, the library lacks comprehensive examples that:
- Show real-world circuit applications
- Demonstrate proper API usage patterns
- Provide learning resources for different skill levels
- Serve as validation of the library's capabilities
- Act as templates for common circuit designs

## Goals & Success Metrics

### Primary Goals
1. **Educational**: Provide clear, well-documented circuit examples for learning
2. **Practical**: Offer ready-to-use templates for common circuit designs
3. **Validation**: Demonstrate that the library can handle diverse circuit types
4. **Documentation**: Show best practices for using the library API

### Success Metrics
- ✅ All 10 circuits simulate without errors
- ✅ 100% test coverage for example circuits
- ✅ Each example generates interactive Plotly reports
- ✅ Documentation clarity score >90% (based on user feedback)
- ✅ Examples used as templates in >50% of user projects

## User Stories

### As a Student
- I want to learn circuit fundamentals through working examples
- I need to understand how simulation parameters affect results
- I want to visualize circuit behavior interactively

### As a Professional Engineer
- I need templates for common circuit designs
- I want to validate the library against known circuit behaviors
- I need examples of advanced analysis techniques

### As a Hobbyist
- I want easy-to-understand examples I can modify
- I need visual feedback to understand what's happening
- I want practical circuits I can actually build

## Proposed Solution

### Circuit Collection (10 Examples)

#### 1. **Voltage Divider** (Basic)
- **Purpose**: Fundamental resistor network
- **Learning**: Ohm's law, voltage division
- **Variants**: Fixed ratio, potentiometer
- **Analysis**: DC operating point

#### 2. **RC Filter** (Basic)
- **Purpose**: Frequency-dependent filtering
- **Learning**: Time constants, frequency response
- **Variants**: Low-pass, high-pass
- **Analysis**: AC frequency sweep, transient response

#### 3. **RLC Resonance** (Intermediate)
- **Purpose**: Resonant behavior demonstration
- **Learning**: Q factor, bandwidth, resonance
- **Variants**: Series, parallel
- **Analysis**: Frequency response, impedance plots

#### 4. **Op-Amp Amplifier** (Intermediate)
- **Purpose**: Active amplification
- **Learning**: Gain, feedback, virtual ground
- **Variants**: Inverting, non-inverting, differential
- **Analysis**: Gain-bandwidth, slew rate

#### 5. **555 Timer** (Advanced)
- **Purpose**: Timing and oscillation
- **Learning**: RC timing, duty cycle
- **Variants**: Astable, monostable, bistable
- **Analysis**: Frequency, duty cycle variation

#### 6. **Bridge Rectifier** (Power)
- **Purpose**: AC to DC conversion
- **Learning**: Rectification, ripple, filtering
- **Components**: Diodes, capacitors
- **Analysis**: Ripple voltage, efficiency

#### 7. **Transistor Amplifier** (Advanced)
- **Purpose**: Discrete amplification
- **Learning**: Biasing, small-signal analysis
- **Variants**: Common emitter, common collector
- **Analysis**: Gain, input/output impedance

#### 8. **Active Filter** (Advanced)
- **Purpose**: Precision frequency filtering
- **Learning**: Filter design, order, rolloff
- **Variants**: Butterworth, Chebyshev
- **Analysis**: Frequency response, phase

#### 9. **Linear Power Supply** (Power)
- **Purpose**: Voltage regulation
- **Learning**: Regulation, ripple rejection
- **Components**: Transformer, rectifier, regulator
- **Analysis**: Load regulation, efficiency

#### 10. **Logic Gates** (Digital)
- **Purpose**: Digital circuit fundamentals
- **Learning**: Boolean logic, switching
- **Variants**: AND, OR, NOT, XOR
- **Analysis**: Truth tables, propagation delay

### Implementation Structure

```python
examples/
├── __init__.py
├── basic/
│   ├── __init__.py
│   ├── voltage_divider/
│   │   ├── __init__.py
│   │   ├── circuit.py        # Circuit definition
│   │   ├── simulation.py     # Simulation setup
│   │   ├── analysis.py       # Results analysis
│   │   ├── report.py         # Plotly report generation
│   │   ├── netlist.cir       # SPICE netlist
│   │   └── README.md         # Documentation
│   ├── rc_filter/
│   └── rlc_resonance/
├── amplifiers/
│   ├── op_amp/
│   └── transistor/
├── power/
│   ├── bridge_rectifier/
│   └── power_supply/
├── timing/
│   └── timer_555/
├── digital/
│   └── logic_gates/
└── utils/
    ├── validation.py         # Common validation
    └── reporting.py          # Shared reporting utilities
```

### Model Integration Strategy

We'll create a model loader utility to access the KiCad-Spice-Library:

```python
# src/models/spice_loader.py
class SpiceModelLoader:
    """Load SPICE models from KiCad library."""
    
    def __init__(self):
        self.library_path = Path("submodules/KiCad-Spice-Library/Models")
        self.model_cache = {}
    
    def load_opamp(self, model: str) -> str:
        """Load op-amp model (e.g., 'LM358', 'TL072')."""
        # Search in manufacturer libs first
        # Fall back to generic models
    
    def load_transistor(self, model: str) -> str:
        """Load transistor model (e.g., '2N2222', 'BC547')."""
    
    def load_555_timer(self) -> str:
        """Load NE555 timer model."""
        return self._load_from_file("uncategorized/spice_complete/SGS555.LIB")
```

### Each Example Includes

1. **Circuit Module** (`circuit.py`)
```python
class VotageDividerCircuit:
    """Voltage divider circuit implementation."""
    
    def __init__(self, r1: float = 1000, r2: float = 1000):
        """Initialize with resistor values in ohms."""
        self.r1 = r1
        self.r2 = r2
        self.circuit = self._build_circuit()
    
    def _build_circuit(self) -> Circuit:
        """Build the circuit using the library API."""
        # Implementation
```

2. **Simulation Script** (`simulation.py`)
```python
def run_simulation(circuit: Circuit) -> SimulationResult:
    """Run standard simulation with progress tracking."""
    with Progress() as progress:
        # Simulation implementation
```

3. **Interactive Report** (`report.py`)
```python
def generate_report(results: SimulationResult) -> PlotlyReport:
    """Generate interactive Plotly report."""
    # Report generation
```

4. **Comprehensive Tests** (`test_*.py`)
```python
def test_voltage_divider_ratio():
    """Test voltage division ratio."""
    # Test implementation
```

5. **Documentation** (`README.md`)
- Circuit theory explanation
- Component selection guide
- Simulation parameters
- Expected results
- Common variations
- Real-world applications

## Technical Requirements

### Component Library Integration
- **KiCad-Spice-Library**: Leverage 50,000+ SPICE models from submodules/KiCad-Spice-Library
  - Use manufacturer models when available (TI, Infineon, Linear Tech)
  - Real op-amp models: LM358, TL072, LF351, NE5534
  - Real transistor models: 2N2222, 2N3904, BC547, 2N3906
  - 555 timer models from SGS555.LIB
  - Diode models including zeners and LEDs
- **Model Selection Priority**:
  1. Manufacturer-specific models (most accurate)
  2. spice_complete library (comprehensive)
  3. Generic/uncategorized models (fallback)

### Performance
- Simulation time <1s for basic circuits
- Report generation <2s
- Memory usage <100MB per example

### Quality
- Test coverage >95% per example
- Type hints on all functions
- Docstrings following NumPy style
- No linting errors (black, ruff, mypy)

### Compatibility
- Python 3.10+
- Works in Docker environment
- Compatible with MCP server
- Runs on macOS, Linux, Windows

## Development Timeline

### Phase 1: Basic Circuits (Week 1)
- [ ] Voltage divider
- [ ] RC filter  
- [ ] RLC resonance

### Phase 2: Amplifiers (Week 2)
- [ ] Op-amp circuits
- [ ] Transistor amplifier

### Phase 3: Advanced (Week 3)
- [ ] 555 timer
- [ ] Active filters
- [ ] Logic gates

### Phase 4: Power Circuits (Week 4)
- [ ] Bridge rectifier
- [ ] Power supply

### Phase 5: Polish (Week 5)
- [ ] Interactive reports for all
- [ ] Complete documentation
- [ ] Integration testing

## Testing Strategy

### Unit Tests
- Component values validation
- Circuit connectivity
- Simulation parameters

### Integration Tests
- End-to-end simulation
- Report generation
- MCP server compatibility

### Validation Tests
- Compare against theoretical values
- Verify against SPICE references
- Cross-check with textbook examples

## Documentation Plan

### For Each Circuit
1. **Theory Section**: Mathematical background
2. **Build Guide**: Step-by-step construction
3. **Simulation Guide**: Parameter selection
4. **Results Interpretation**: Understanding outputs
5. **Troubleshooting**: Common issues
6. **Extensions**: Modifications and experiments

### Master Documentation
- Quick start guide
- Circuit selection guide
- API patterns showcase
- Performance benchmarks

## Risk Analysis

### Technical Risks
- **Convergence Issues**: Some circuits may not simulate
  - *Mitigation*: Careful parameter selection, fallback options
  
- **Performance**: Complex circuits may be slow
  - *Mitigation*: Optimization, caching, parallel processing

### User Experience Risks  
- **Complexity**: Examples too advanced for beginners
  - *Mitigation*: Progressive difficulty, clear documentation
  
- **Incomplete Coverage**: Missing common use cases
  - *Mitigation*: Community feedback, expandable structure

## Success Criteria

### Must Have
- ✅ All 10 circuits simulate successfully
- ✅ Complete test coverage
- ✅ Interactive reports for each
- ✅ Comprehensive documentation

### Should Have
- ✅ Video tutorials
- ✅ Parameter sweep examples
- ✅ Optimization examples
- ✅ Real component models

### Nice to Have
- ✅ PCB layout examples
- ✅ BOM generation
- ✅ 3D visualization
- ✅ AR/VR support

## Alternatives Considered

1. **Fewer Examples (5)**: Rejected - insufficient coverage
2. **More Examples (20)**: Rejected - scope too large for MVP
3. **Only Basic Circuits**: Rejected - doesn't showcase capabilities
4. **External Examples**: Rejected - need integrated, tested examples

## Open Questions

1. Should we include mixed-signal circuits?
2. Do we need temperature analysis examples?
3. Should examples include tolerance analysis?
4. How much theory vs. practical focus?

## Approval

**Status**: ⏳ Awaiting Approval

**Approvers**:
- [ ] @user - Product Owner
- [ ] Technical Lead
- [ ] Documentation Team

---

## Next Steps

Once approved:
1. Create detailed implementation plan
2. Set up example structure
3. Begin with voltage divider as template
4. Iterate based on pattern success

**Please review and approve this PRD before implementation begins.**