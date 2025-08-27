# Product Requirements Document: Transfer Function Analysis

## Document Control
- **PRD ID**: 004-transfer-function-analysis
- **Created**: 2025-08-27
- **Status**: DRAFT - Awaiting Approval
- **Issue**: [#12](https://github.com/circuit-synth/circuit-simulation/issues/12)
- **Estimated Effort**: 1-2 days
- **Priority**: Medium

## Executive Summary

This PRD outlines the implementation of symbolic transfer function analysis capabilities for the circuit simulation library. This feature will enable professional engineers and students to extract H(s) transfer functions, identify poles and zeros, and perform stability analysis for control systems applications.

## Problem Statement

### Current Limitations
1. **No Symbolic Analysis**: Users cannot extract mathematical transfer functions from circuits
2. **Limited Control System Support**: No pole/zero identification for stability analysis
3. **Missing Educational Tools**: Cannot demonstrate fundamental control theory concepts
4. **Manual Calculation Required**: Engineers must manually derive H(s) from frequency response

### User Impact
- Control system engineers need automated stability margin calculations
- Students require visual tools to understand pole-zero relationships
- Filter designers need quick transfer function extraction
- System architects require cascaded system analysis capabilities

## Solution Overview

Implement a comprehensive `TransferFunction` class that:
1. Extracts H(s) from AC simulation frequency response data
2. Identifies poles and zeros through polynomial fitting
3. Calculates stability margins (phase/gain)
4. Provides time-domain response from frequency-domain data
5. Enables symbolic mathematics for theoretical analysis

## Functional Requirements

### FR1: Transfer Function Class
```python
class TransferFunction:
    """Represents H(s) = N(s)/D(s) transfer function."""
    
    def __init__(self, numerator: np.ndarray, denominator: np.ndarray):
        """Create from polynomial coefficients."""
        
    @classmethod
    def from_frequency_response(cls, frequencies: np.ndarray, 
                               response: np.ndarray) -> 'TransferFunction':
        """Create from AC simulation data using rational function fitting."""
        
    @classmethod
    def from_poles_zeros(cls, poles: List[complex], zeros: List[complex], 
                        gain: float) -> 'TransferFunction':
        """Create from pole-zero-gain representation."""
```

### FR2: Mathematical Properties
```python
@property
def poles(self) -> np.ndarray:
    """System poles (roots of denominator)."""
    
@property
def zeros(self) -> np.ndarray:
    """System zeros (roots of numerator)."""
    
@property
def dc_gain(self) -> float:
    """DC gain H(0)."""
    
@property
def bandwidth(self) -> float:
    """3dB bandwidth in Hz."""
    
def evaluate(self, s: Union[float, complex, np.ndarray]) -> np.ndarray:
    """Evaluate H(s) at given s values."""
```

### FR3: Stability Analysis
```python
def stability_margins(self) -> StabilityMetrics:
    """Calculate comprehensive stability metrics."""
    return StabilityMetrics(
        phase_margin=self._calculate_phase_margin(),
        gain_margin=self._calculate_gain_margin(),
        crossover_frequency=self._find_crossover(),
        is_stable=self._check_stability()
    )

def nyquist_plot(self) -> PlotlyFigure:
    """Generate interactive Nyquist plot."""
    
def root_locus(self, k_range: np.ndarray) -> PlotlyFigure:
    """Generate root locus plot for varying gain k."""
```

### FR4: Time Domain Analysis
```python
def step_response(self, time: np.ndarray) -> np.ndarray:
    """Calculate unit step response."""
    
def impulse_response(self, time: np.ndarray) -> np.ndarray:
    """Calculate impulse response."""
    
def rise_time(self) -> float:
    """Calculate 10-90% rise time."""
    
def settling_time(self, tolerance: float = 0.02) -> float:
    """Calculate settling time to within tolerance."""
    
def overshoot(self) -> float:
    """Calculate percent overshoot."""
```

### FR5: Integration with Simulation Engine
```python
# Extension to SimulationEngine
def extract_transfer_function(
    self,
    circuit: Circuit,
    input_port: str,
    output_port: str,
    reference: str = "0"
) -> TransferFunction:
    """
    Extract transfer function from circuit.
    
    Args:
        circuit: Circuit to analyze
        input_port: Input node/port name
        output_port: Output node/port name  
        reference: Reference node (default: ground)
    
    Returns:
        TransferFunction object with H(s) representation
    """
    
# Extension to SimulationResults
def to_transfer_function(
    self,
    input_signal: str,
    output_signal: str
) -> TransferFunction:
    """Convert AC results to transfer function."""
```

### FR6: Visualization Requirements
```python
def plot_pole_zero_map(self, title: str = None) -> PlotlyFigure:
    """S-plane pole-zero constellation."""
    
def plot_bode(self, frequencies: np.ndarray = None) -> PlotlyFigure:
    """Magnitude and phase Bode plots."""
    
def plot_step_response(self, time: np.ndarray = None) -> PlotlyFigure:
    """Time domain step response."""
    
def plot_frequency_response(self) -> PlotlyFigure:
    """3D frequency response surface."""
```

## Non-Functional Requirements

### NFR1: Performance
- Pole/zero extraction < 100ms for 10th order system
- Frequency response evaluation < 10ms for 1000 points
- Step response calculation < 50ms for 1000 time points

### NFR2: Accuracy
- Pole/zero identification within ±1% of theoretical values
- Transfer function fit within ±0.5dB of original response
- Stability margins accurate to ±0.1° (phase) and ±0.1dB (gain)

### NFR3: Scalability
- Support transfer functions up to 20th order
- Handle MIMO systems (future enhancement path)
- Efficient memory usage for large frequency vectors

### NFR4: Usability
- Intuitive API matching control theory conventions
- Clear error messages for numerical instabilities
- Comprehensive documentation with examples

## Technical Architecture

### Component Structure
```
src/circuit_sim/analysis/
├── __init__.py
├── transfer_function.py      # Core TransferFunction class
├── pole_zero.py             # Extraction algorithms
├── stability.py             # Stability analysis tools
├── time_domain.py           # Time response calculations
├── symbolic_math.py         # SymPy integration
└── fitting.py               # Rational function fitting
```

### Dependencies
- **NumPy**: Polynomial operations and numerical computations
- **SciPy**: Signal processing (scipy.signal) and optimization
- **SymPy**: Symbolic mathematics for H(s) representation
- **Plotly**: Interactive visualizations

### Algorithm Selection

#### Rational Function Fitting
Use Vector Fitting (VF) algorithm for robust fitting:
1. Iterative pole relocation for stability
2. Least squares fitting for residues
3. Passivity enforcement for physical systems

#### Pole/Zero Extraction
1. Primary: NumPy polynomial root finding
2. Fallback: Companion matrix eigenvalues
3. Verification: Evaluate at test frequencies

#### Stability Analysis
1. Routh-Hurwitz for polynomial stability
2. Nyquist criterion for closed-loop stability
3. Root locus for parameter sensitivity

## Implementation Plan

### Phase 1: Core Foundation (Day 1)
1. **TransferFunction class** with basic properties
2. **Polynomial representation** and evaluation
3. **Pole/zero extraction** from coefficients
4. **Unit tests** for mathematical operations

### Phase 2: Integration (Day 1)
1. **Frequency response fitting** algorithm
2. **SimulationEngine integration** 
3. **SimulationResults extension**
4. **Integration tests** with real circuits

### Phase 3: Analysis Tools (Day 2)
1. **Stability margin** calculations
2. **Time domain** response functions
3. **Visualization** methods
4. **Example circuits** demonstrating features

### Phase 4: Documentation (Day 2)
1. **API documentation** with examples
2. **Tutorial notebook** for control systems
3. **Performance benchmarks**
4. **User guide** for common tasks

## Success Criteria

### Acceptance Tests
1. ✅ Extract transfer function from RC filter circuit
2. ✅ Identify poles/zeros within 1% accuracy
3. ✅ Calculate correct stability margins for feedback amplifier
4. ✅ Generate accurate step response from H(s)
5. ✅ Create interactive pole-zero and Bode plots

### Performance Benchmarks
- 5th order Butterworth filter analysis < 200ms total
- 10-stage cascaded system composition < 500ms
- Stability analysis of feedback system < 100ms

### Quality Metrics
- Test coverage > 90% for analysis module
- All public methods documented with examples
- Type hints complete with mypy validation
- No performance regressions in existing features

## Example Usage

### Basic Transfer Function Analysis
```python
# Create circuit
circuit = Circuit("Active Filter")
circuit.add_resistor("R1", "in", "n1", 10e3)
circuit.add_capacitor("C1", "n1", "0", 100e-9)
circuit.add_opamp("U1", "n1", "0", "out")

# Run AC analysis
engine = SimulationEngine()
results = engine.simulate_ac(circuit, 1, 100e3, 30)

# Extract transfer function
tf = results.to_transfer_function("in", "out")

# Analyze properties
print(f"DC Gain: {tf.dc_gain:.1f} dB")
print(f"Poles: {tf.poles}")
print(f"Bandwidth: {tf.bandwidth:.1f} Hz")

# Check stability
margins = tf.stability_margins()
print(f"Phase Margin: {margins.phase_margin:.1f}°")
print(f"Stable: {margins.is_stable}")

# Visualize
tf.plot_bode().show()
tf.plot_pole_zero_map().show()
```

### Control System Design
```python
# Design compensator from requirements
tf = TransferFunction.from_poles_zeros(
    poles=[-100, -1000],
    zeros=[-10],
    gain=100
)

# Analyze time response
time = np.linspace(0, 0.1, 1000)
step = tf.step_response(time)

print(f"Rise Time: {tf.rise_time()*1000:.2f} ms")
print(f"Overshoot: {tf.overshoot():.1f}%")
print(f"Settling Time: {tf.settling_time()*1000:.2f} ms")

# Plot comprehensive analysis
fig = tf.create_analysis_report()
fig.show()
```

## Risks and Mitigations

### Risk 1: Numerical Instability
**Risk**: Polynomial fitting may be ill-conditioned for high-order systems  
**Mitigation**: Use robust Vector Fitting algorithm with iterative refinement

### Risk 2: Performance Degradation
**Risk**: Complex calculations may slow down simulation workflow  
**Mitigation**: Cache computed properties, use lazy evaluation

### Risk 3: Accuracy Issues
**Risk**: Fitting may not capture all dynamics accurately  
**Mitigation**: Provide quality metrics, allow manual pole/zero adjustment

## Dependencies and Integration

### Prerequisites
- ✅ AC frequency analysis (complete)
- ✅ SimulationResults framework (complete)
- ✅ Plotly visualization infrastructure (complete)

### Enables Future Features
- Advanced stability analysis (Phase/Gain margins)
- Control system design tools
- Filter synthesis capabilities
- Symbolic circuit analysis

## Testing Strategy

### Unit Tests
```python
def test_transfer_function_creation():
    """Test various creation methods."""
    
def test_pole_zero_extraction():
    """Verify accurate pole/zero identification."""
    
def test_stability_analysis():
    """Test stability margin calculations."""
    
def test_time_response():
    """Verify step and impulse responses."""
```

### Integration Tests
```python
def test_rc_filter_transfer_function():
    """End-to-end test with RC circuit."""
    
def test_active_filter_analysis():
    """Test with operational amplifier circuit."""
    
def test_feedback_system_stability():
    """Test closed-loop stability analysis."""
```

### Example Circuits
1. First-order RC filter
2. Second-order RLC circuit
3. Butterworth active filter
4. PID controller
5. Feedback amplifier

## Documentation Requirements

### API Reference
- Comprehensive docstrings for all public methods
- Type hints for all parameters and returns
- Usage examples in docstrings

### User Guide
- Tutorial: "Introduction to Transfer Functions"
- How-to: "Extracting H(s) from Circuits"
- How-to: "Stability Analysis for Control Systems"
- Reference: "Transfer Function API"

### Technical Notes
- Algorithm implementation details
- Numerical considerations
- Performance optimization tips

## Approval

**Status**: ⏳ AWAITING APPROVAL

### Review Checklist
- [ ] Requirements complete and clear
- [ ] Technical approach validated
- [ ] Timeline realistic
- [ ] Dependencies identified
- [ ] Success criteria measurable

### Sign-off Required From
- [ ] Project Owner
- [ ] Technical Lead  
- [ ] User Representative

---

*This PRD requires approval before implementation begins. Please review and provide feedback or approval.*