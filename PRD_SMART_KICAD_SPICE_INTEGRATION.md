# PRD: Smart KiCad-Spice Integration Algorithm

## Overview

Replace the current hardcoded component mapping (4 components) with an intelligent algorithm that leverages the KiCad-Spice-Library (50,000+ SPICE models) for scalable circuit-synth → circuit-simulation integration.

## Problem Statement

### Current Limitations
- **Only 4 component types** supported (R, L, C, V)
- **Hardcoded 1-to-1 mappings** don't scale
- **Manual coding required** for each new component type
- **No real-world circuit support** (transistors, op-amps, diodes)

### Impact
- Circuit-synth users can't simulate realistic circuits
- Integration limited to basic academic examples
- No path to professional circuit simulation

## Solution

### Smart SPICE Model Mapping Algorithm
Intelligent component → SPICE model resolution using:
1. **KiCad-Spice-Library database** (50K+ models)
2. **Pattern matching** on component values
3. **Symbol-based fallbacks**
4. **Smart defaults** for unknown components

## Success Metrics

- **Component Coverage**: Support 95%+ of common electronic components
- **Model Accuracy**: Correct SPICE model selection >90% of the time
- **Performance**: Model lookup <10ms per component
- **Reliability**: Graceful fallbacks for unknown components
- **User Experience**: Zero manual configuration required

## User Stories

### Story 1: Transistor Circuit Simulation
**As a** circuit-synth user
**I want** to simulate circuits with BJT transistors
**So that** I can validate amplifier and switching circuits

```python
# User writes in circuit-synth:
transistor = Component(symbol="Device:Q_NPN_CBE", value="2N3904", ref="Q1")

# System automatically maps to:
circuit.add_bjt_transistor("Q1", collector, base, emitter, model="2N3904")
# With full SPICE parameters loaded from KiCad-Spice-Library
```

### Story 2: Op-Amp Circuit Simulation
**As a** circuit-synth user
**I want** to simulate op-amp circuits
**So that** I can design and validate analog signal processing

```python
# User writes:
opamp = Component(symbol="Amplifier_Operational:LM358", value="LM358", ref="U1")

# System maps to:
circuit.add_opamp("U1", out, in_neg, in_pos, vdd, vss, model="LM358")
```

### Story 3: Mixed Analog Circuit
**As a** circuit-synth user
**I want** to simulate complete analog circuits
**So that** I can validate filter + amplifier + power supply designs

## Technical Requirements

### Core Algorithm Components

#### 1. SPICE Model Database Loader
- **Input**: KiCad-Spice-Library/Supported.txt (50K+ model names)
- **Output**: In-memory searchable model index
- **Performance**: Load database <1 second on startup

#### 2. Smart Model Resolver
- **Input**: Component (symbol, value, ref, footprint)
- **Output**: SPICE model name + confidence score
- **Fallback chain**:
  1. Exact value match (`value="2N3904"` → `2N3904`)
  2. Pattern extraction (`value="BC546B-Generic"` → `BC546B`)
  3. Symbol-based defaults (`Device:Q_NPN_CBE` → `DefaultNPN`)
  4. Reference-based guessing (`ref="Q1"` + NPN symbol → `2N3904`)

#### 3. SPICE Library File Loader
- **Input**: Model name (`"2N3904"`)
- **Output**: SPICE model definition from .lib files
- **Caching**: Cache loaded models for performance
- **Search paths**: Models/{Transistor,Diode,Operational Amplifier}/

#### 4. Component Type Detector
- **Input**: KiCad symbol (`Device:Q_NPN_CBE`)
- **Output**: Circuit-simulation component type + pin mapping
- **Pin mappings**:
  - `Device:Q_NPN_CBE` → `(collector=1, base=2, emitter=3)`
  - `Device:D` → `(anode=1, cathode=2)`
  - `Amplifier_Operational:*` → `(out=1, in_neg=2, in_pos=3, vdd=4, vss=5)`

### Integration Points

#### Replace circuit_synth_integration.py
Current hardcoded approach:
```python
if symbol == "Device:R":
    circuit.add_resistor(comp_name, pins[0], pins[1], value)
elif symbol == "Device:C":
    # ... hardcoded for 4 component types
```

New smart approach:
```python
model_info = smart_mapper.resolve_component(symbol, value, ref, footprint)
if model_info:
    add_method = getattr(circuit, model_info.circuit_method)
    add_method(comp_name, *model_info.pins, model=model_info.spice_model)
```

#### Enhanced Error Handling
```python
@dataclass
class ComponentMapping:
    component_name: str
    spice_model: Optional[str]
    circuit_method: str  # "add_bjt_transistor"
    pins: List[str]
    confidence: float  # 0.0-1.0
    fallback_used: bool
    error_message: Optional[str]
```

## Technical Questions & Decisions Needed

### 1. Pin Mapping Strategy
**Question**: How should we handle complex pin mappings?

**Answer**: Circuit-synth json pin data is based directly on kicad symbol file data, so we can use the pin mapping of circuit-synth json

### 2. Model Confidence Scoring
**Question**: How do we score mapping confidence?

**Scoring system**:
- **1.0**: Exact value match (`value="2N3904"` found in library)
- **0.9**: Pattern match (`value="2N3904-SOT23"` → `2N3904`)
- **0.7**: Symbol-specific default (`Device:Q_NPN_CBE` → `DefaultNPN`)
- **0.5**: Generic fallback (`ref="Q1"` → guess transistor)
- **0.0**: No mapping found

**Answer**: This sounds good

### 3. Performance Optimization
**Question**: How do we handle 50K+ model database efficiently?


- **Answer**: Load all models in memory (fast lookup, high memory)

### 4. Fallback Strategy for Unknown Components
**Question**: What happens when we can't find a SPICE model?

- **Answer**: User is responsible for providing a valid parts, don't analyze subcircuits where parts are not found

### 5. Multi-Package Component Handling
**Question**: How do we handle components like LM358 (dual op-amp)?

Circuit-synth might define:
```python
opamp = Component(symbol="Amplifier_Operational:LM358", ref="U1")
```

**Answer**: automatically create U1A and U1B instances

### 6. SPICE Model Parameter Validation
**Question**: Should we validate loaded SPICE models?

Many .lib files have errors or non-standard formats. Should we:
- **A**: Load models blindly (fast, may cause ngspice errors)
- **B**: Validate SPICE syntax before using (slower, more reliable)
- **C**: Use model whitelist of known-good models

**Recommendation**: A with good error handling in simulation engine

### 7. Custom Model Support
**Question**: How should users add custom SPICE models?

**Options**:
- **A**: Only use KiCad-Spice-Library models
- **B**: Allow custom .lib file paths in configuration
- **C**: Support inline SPICE models in circuit-synth

**Recommendation**: B - configurable additional model directories

### 8. Component Value Parsing
**Question**: How do we parse complex component values?

Examples:
- `"2N3904-SOT23"` → model=`2N3904`, package info ignored
- `"BC546B/100"` → model=`BC546B`, gain info ignored
- `"LM358-SOIC"` → model=`LM358`, package info ignored

**Strategy**: Extract known model patterns, ignore packaging/variant suffixes

## Implementation Plan

### Phase 1: Core Algorithm (Week 1-2)
- [ ] Implement SmartSpiceMapper class
- [ ] Load KiCad-Spice-Library/Supported.txt database
- [ ] Pattern matching for common component types
- [ ] Basic pin mapping for R/L/C/V/D/Q/U components

### Phase 2: Integration (Week 2-3)
- [ ] Replace hardcoded integration in circuit_synth_integration.py
- [ ] Add enhanced error handling and confidence scoring
- [ ] Test with real circuit-synth circuits
- [ ] Performance optimization

### Phase 3: Advanced Features (Week 3-4)
- [ ] SPICE .lib file loading on-demand
- [ ] Custom model directory support
- [ ] Component mapping validation and reporting
- [ ] Documentation and examples

### Phase 4: Production Ready (Week 4)
- [ ] Comprehensive test suite
- [ ] Performance benchmarks
- [ ] Error handling for edge cases
- [ ] User documentation

## Testing Strategy

### Unit Tests
- Model resolution accuracy for common components
- Pin mapping correctness for each symbol type
- Performance benchmarks for database operations
- Error handling for malformed inputs

### Integration Tests
- End-to-end circuit-synth → simulation with complex circuits
- Model loading from KiCad-Spice-Library files
- Fallback behavior for unknown components

### Test Circuits
1. **Basic Analog**: Op-amp amplifier with transistor output stage
2. **Mixed Signal**: ADC reference with voltage regulation
3. **Power Electronics**: Buck converter with MOSFET switching
4. **RF Circuit**: Simple transistor amplifier at high frequency

## Risks & Mitigations

### Risk 1: KiCad-Spice-Library Model Quality
**Risk**: Some SPICE models may be incorrect or outdated
**Mitigation**: Start with curated whitelist of known-good models, expand gradually

### Risk 2: Performance with Large Circuits
**Risk**: 50K+ model database may slow down large circuit processing
**Mitigation**: Implement caching and lazy loading, profile performance

### Risk 3: Pin Mapping Errors
**Risk**: Incorrect pin assignments could cause simulation failures
**Mitigation**: Extensive testing with known circuit topologies, validation against KiCad

### Risk 4: Complex Component Types
**Risk**: Multi-unit packages, sub-circuits may not map correctly
**Mitigation**: Phase implementation, handle simple cases first

## Success Criteria

### Minimum Viable Product
- [ ] Support 20+ common component types (BJT, MOSFET, diode, op-amp)
- [ ] 90%+ model resolution success rate for standard parts
- [ ] Performance: <50ms total mapping time for 100-component circuit
- [ ] Zero crashes on malformed inputs

### Full Success
- [ ] Support 95%+ of components in typical analog circuits
- [ ] Automatic fallback handling for edge cases
- [ ] User-friendly error reporting with suggestions
- [ ] Production-quality error handling and logging

---

**Questions for Review:**
1. Should we prioritize model accuracy or coverage breadth?
2. How important is performance vs. reliability for the initial release?
3. Should we include digital component support (logic gates) or focus on analog?
4. What's the acceptable failure rate for unknown/new components?
5. Should this integrate with the existing MCP server for AI assistant access?

*PRD Version 1.0 - Ready for technical review and implementation planning*
