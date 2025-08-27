# PRD: SPICE Netlist Import/Export System

**Status**: DRAFT 📝  
**Version**: 1.0  
**Created**: August 27, 2025  
**Owner**: Circuit Simulation Team  
**GitHub Issue**: [#8](https://github.com/circuit-synth/circuit-simulation/issues/8)

## Executive Summary

Implement SPICE and KiCad netlist import/export with deep integration to circuit-synth and circuit-intelligence repositories, enabling hierarchical circuit analysis and subcircuit simulation while maintaining standalone utility.

## Problem Statement

### Current State
- Circuit simulation library uses proprietary Python API
- circuit-synth has KiCad netlist → hierarchical JSON conversion
- No SPICE format support for academic/industry standard circuits
- No integration between circuit-synth hierarchy and simulation capabilities
- Subcircuit simulation requires manual extraction

### User Pain Points
- **circuit-synth users**: Cannot simulate extracted hierarchical designs
- **Academic users**: Cannot import textbook SPICE examples
- **circuit-intelligence integration**: Missing netlist analysis pipeline
- **Hierarchical analysis**: No way to simulate subcircuits individually

## Vision Statement

> "Enable seamless circuit portability across the entire EDA ecosystem, from academic SPICE examples to professional design flows, making our simulation library the universal translator for circuit designs."

## Success Metrics

### Primary KPIs
- **Import Success Rate**: 95%+ of standard SPICE files parse correctly
- **Format Coverage**: Support 5+ major EDA formats (SPICE, LTSpice, KiCad, PSpice, Spectre)
- **Performance**: Parse 1000+ component netlists in <1 second
- **User Adoption**: 70% of new users start by importing existing circuits

### Secondary KPIs
- **Error Reporting**: Clear, actionable error messages for 100% of parse failures
- **Model Preservation**: Maintain 100% of component models and parameters
- **Export Quality**: Generated netlists simulate identically in target tools
- **Documentation**: Complete format support matrix with examples

## Target Users

### Primary Personas

**🎓 Academic Researcher (Dr. Sarah)**
- Needs: Import textbook examples, share results in papers
- Pain: Manually transcribing SPICE from literature
- Success: One-click import of any academic circuit

**👨‍💻 Hardware Engineer (Mike)**  
- Needs: Import legacy designs, export to production tools
- Pain: Tool lock-in prevents design reuse
- Success: Seamless workflow integration

**📚 Student (Alex)**
- Needs: Work with course materials, submit in required formats
- Pain: Learning multiple tool syntaxes
- Success: Focus on circuit design, not file formats

## Functional Requirements

### Core Import Features

#### FR1: SPICE Format Support
**Requirement**: Parse standard SPICE variants with high fidelity

**Supported Formats** (Phase 1 Focus):
- Standard SPICE (.cir, .sp) - Priority 1
- KiCad netlist (.net) - Priority 1
- PSpice (.cir with extensions) - Priority 2

**Acceptance Criteria**:
- Parse component definitions (R, L, C, V, I, M, Q, D)
- Handle subcircuit definitions (.SUBCKT)
- Extract model definitions (.MODEL)
- Process parameter definitions (.PARAM)
- Resolve include files (.INCLUDE)
- Maintain node naming and connectivity

#### FR2: circuit-synth Integration
**Requirement**: Deep integration with existing circuit-synth KiCad processing

**Integration Points**:
- Use circuit-synth's hierarchical JSON as intermediate format
- Enable simulation of extracted subcircuits
- Preserve circuit-synth's component mapping logic
- Support circuit-intelligence analysis pipeline

**Acceptance Criteria**:
- Import circuit-synth JSON hierarchy directly
- Simulate individual subcircuits from hierarchy
- Maintain compatibility with existing circuit-synth workflows
- Export results back to circuit-synth format

#### FR3: Robust Error Handling
**Requirement**: Provide actionable feedback for parsing issues

**Features**:
- Line-by-line error reporting
- Syntax validation with suggestions
- Component model validation
- Node connectivity verification

### Export Capabilities

#### FR4: Multi-Format Export
**Requirement**: Generate netlists compatible with target simulators

**Export Formats**:
- Standard SPICE netlist
- Spectre netlist for Cadence
- Verilog-A behavioral models
- KiCad netlist for PCB layout
- Python circuit definition (round-trip)

#### FR5: Template System
**Requirement**: Customizable export templates for different use cases

**Templates**:
- Academic submission format
- Production netlist with headers
- Simulation testbench wrapper
- Documentation format

## Technical Architecture

### System Design with circuit-synth Integration

```
src/io/
├── parsers/
│   ├── base_parser.py          # Common parsing interface
│   ├── spice_parser.py         # Standard SPICE (.cir, .sp)
│   ├── kicad_parser.py         # KiCad netlist (.net)
│   └── circuit_synth_bridge.py # Bridge to circuit-synth JSON
├── exporters/
│   ├── base_exporter.py        # Common export interface
│   ├── spice_exporter.py       # Standard SPICE output
│   ├── kicad_exporter.py       # KiCad netlist generation
│   └── python_exporter.py     # Circuit definition code
├── hierarchical/
│   ├── subcircuit_manager.py   # Hierarchical circuit handling
│   ├── port_interface.py       # Subcircuit port management
│   ├── testbench_generator.py  # Individual subcircuit testing
│   └── hierarchy_simulator.py  # Multi-level simulation
├── models/
│   ├── netlist.py             # Intermediate representation
│   ├── component.py           # Component abstraction
│   ├── subcircuit.py          # Hierarchical designs
│   └── circuit_synth_json.py   # circuit-synth JSON format
└── utils/
    ├── tokenizer.py           # SPICE tokenization
    ├── validator.py           # Netlist validation
    └── model_library.py       # Component model database
```

### Data Flow with Hierarchical Support

```
Input Files → Parser → Hierarchical IR → Individual/Group Simulation
     ├── SPICE (.cir) → SPICE Parser → Circuit API → Flat Simulation
     ├── KiCad (.net) → KiCad Parser → Circuit API → Hierarchical Simulation  
     └── circuit-synth JSON → Bridge → Subcircuit Groups → Individual Tests

Export: Circuit API → Exporter → Output Format
         └── Subcircuit API → Testbench Generator → Individual Tests
```

### circuit-synth Integration Points

Based on research, circuit-synth provides:
1. **Hierarchical JSON Structure**: Nested subcircuits with component/net data
2. **Component Mapping**: Symbol, footprint, pin information preserved  
3. **Bidirectional Conversion**: Python ↔ KiCad ↔ JSON workflows
4. **Pin-Level Connectivity**: Exact pin mappings with names, numbers, types
5. **Testable Architecture**: Individual .py files for each subcircuit

### Subcircuit Interface Strategy (Based on SPICE Standards)

**Port Definition Standard**:
```spice
.SUBCKT POWER_SUPPLY VIN VOUT GND ENABLE
* VIN: Input voltage port (typ 5V-15V)
* VOUT: Regulated output (3.3V)
* GND: Ground reference 
* ENABLE: Logic enable input
... circuit implementation ...
.ENDS
```

**Testbench Generation Strategy**:
```python
def create_subcircuit_testbench(subcircuit: Circuit, ports: Dict[str, str]):
    """Create isolated testbench for subcircuit simulation"""
    testbench = Circuit(f"{subcircuit.name}_testbench")
    
    # Add test sources for each input port
    for port_name, port_type in ports.items():
        if port_type == "input":
            testbench.add_voltage_source(f"V_{port_name}", port_name, "gnd", "test_value")
        elif port_type == "power":
            testbench.add_voltage_source(f"V_{port_name}", port_name, "gnd", "supply_voltage")
        elif port_type == "output":
            testbench.add_resistor(f"R_LOAD_{port_name}", port_name, "gnd", "load_resistance")
    
    # Include subcircuit instance
    testbench.add_subcircuit(subcircuit)
    
    return testbench
```

**Group Simulation Strategy**:
- **Individual Mode**: Simulate each subcircuit with generated testbench
- **Hierarchical Mode**: Simulate subcircuits within parent context
- **Integration Mode**: Full system simulation with all subcircuits

### Parser Architecture

```python
class NetlistParser:
    def parse(self, filepath: str) -> Netlist:
        """Parse netlist file to intermediate representation"""
        
    def validate(self, netlist: Netlist) -> ValidationResult:
        """Validate netlist for completeness and correctness"""
        
class CircuitConverter:
    def to_circuit(self, netlist: Netlist) -> Circuit:
        """Convert netlist to internal Circuit format"""
        
    def from_circuit(self, circuit: Circuit) -> Netlist:
        """Convert Circuit back to netlist representation"""
```

## Risk Assessment

### Technical Risks

**High Risk - Format Complexity**
- **Risk**: SPICE syntax variations cause parse failures
- **Mitigation**: Comprehensive test suite with real-world files
- **Contingency**: Graceful degradation with manual override options

**Medium Risk - Model Translation**
- **Risk**: Component models don't translate between formats
- **Mitigation**: Extensive model mapping database
- **Contingency**: Generic model fallbacks with warnings

**Low Risk - Performance**
- **Risk**: Large netlists cause memory/speed issues
- **Mitigation**: Streaming parser with lazy evaluation
- **Contingency**: Chunked processing for very large files

### Business Risks

**Medium Risk - User Expectations**
- **Risk**: Users expect 100% compatibility with every variant
- **Mitigation**: Clear documentation of supported features
- **Contingency**: Community contribution for edge cases

## Implementation Plan

### Phase 1: Core SPICE Parser (Week 1-2)
- [ ] Basic SPICE tokenizer and grammar
- [ ] Component parsing (R, L, C, V, I)
- [ ] Node connectivity resolution
- [ ] Unit tests with sample files

### Phase 2: Advanced Features (Week 2-3)
- [ ] Subcircuit support (.SUBCKT)
- [ ] Model definitions (.MODEL)
- [ ] Parameter handling (.PARAM)
- [ ] Include file resolution

### Phase 3: Multi-Format Support (Week 3-4)
- [ ] LTSpice ASC parser
- [ ] KiCad netlist parser
- [ ] Export functionality
- [ ] Template system

### Phase 4: Polish & Integration (Week 4-5)
- [ ] Error handling and validation
- [ ] Performance optimization
- [ ] Documentation and examples
- [ ] CI/CD integration

## Testing Strategy

### Test Coverage Requirements
- **Unit Tests**: 95% coverage for all parsers
- **Integration Tests**: Round-trip conversion accuracy
- **Performance Tests**: 1000+ component files
- **Compatibility Tests**: Real-world file corpus

### Test File Library
```
tests/fixtures/
├── spice/
│   ├── basic_circuits/         # Simple R, L, C examples
│   ├── amplifiers/             # Op-amp designs
│   ├── complex/                # Large hierarchical designs
│   └── edge_cases/             # Unusual syntax variants
├── ltspice/
├── kicad/
└── reference_outputs/          # Expected parse results
```

## Quality Gates

### Definition of Done
- [ ] Parses 95% of test file corpus
- [ ] All exported netlists simulate correctly
- [ ] Performance benchmarks met
- [ ] Documentation complete with examples
- [ ] No critical or high-severity bugs

### Performance Benchmarks
- Parse 100 components: <100ms
- Parse 1000 components: <1s
- Parse 10,000 components: <10s
- Memory usage: <100MB for largest files

## Documentation Requirements

### User Documentation
- Format support matrix
- Import/export tutorials
- Troubleshooting guide
- Best practices for each format

### Developer Documentation
- Parser architecture overview
- Adding new format support
- Component model mapping
- Testing new parsers

## Future Enhancements

### Phase 2 Features (Next Quarter)
- Verilog-A behavioral model export
- IBIS model support
- Real-time format conversion API
- Web-based netlist viewer

### Community Features
- Format plugin architecture
- Community parser contributions
- Crowdsourced test file library
- Format support voting

## Success Criteria

### Launch Criteria
1. Support 3+ major formats (SPICE, LTSpice, KiCad)
2. 90%+ parse success rate on test corpus
3. Complete round-trip conversion
4. Performance targets met
5. Documentation published

### Long-term Success
1. Become the de facto converter for academic use
2. Integration requests from commercial EDA vendors
3. Community contributions for niche formats
4. Citation in research papers as standard tool

## Key Integration Questions for Implementation

### **1. circuit-synth JSON Format Specifics**
From the research, I see circuit-synth uses a specific JSON structure:
- **Components**: `{"J1": {"symbol": "Connector:USB_C_Receptacle", "ref": "J1", "pins": [...]}}`
- **Nets**: `{"net_name": [{"component": "R1", "pin": {"number": "1", "name": "in", "type": "passive"}}]}`
- **Subcircuits**: Nested hierarchy with individual `.py` files

**Questions**:
- Should we use circuit-synth's `json_loader.py` directly as a dependency?
- Do we need to preserve the exact JSON format for round-trip compatibility?
- How should we handle circuit-synth's pin mapping vs SPICE node numbering?

### **2. Subcircuit Simulation Strategy**
Research shows three common approaches:
- **Individual Testbenches**: Each subcircuit tested in isolation with generated test sources
- **Hierarchical Context**: Subcircuits simulated within their parent circuit
- **Port Replacement**: Replace subcircuits with behavioral models based on simulation results

**Questions**:
- Which simulation modes are most valuable for your circuit-synth/circuit-intelligence workflow?
- Should we auto-generate testbenches for each subcircuit in circuit-synth JSON?
- Do you want individual subcircuit analysis (power consumption, transfer function) or full system simulation?

### **3. Interface Handling for KiCad Hierarchical Sheets**
KiCad hierarchical sheets use:
- **Global nets**: Power, ground that span all sheets
- **Hierarchical pins**: Explicit connections between sheets
- **Local nets**: Nets contained within a sheet

**Questions**:
- Should we treat KiCad hierarchical pins as SPICE `.SUBCKT` ports?
- How should we handle global nets (VCC, GND) that appear in multiple subcircuits?
- Do you want simulation results aggregated back to the parent level?

### **4. Integration with circuit-intelligence**  
**Questions**:
- What kind of netlist analysis does circuit-intelligence need from this parser?
- Should the parser output structured data for circuit-intelligence consumption?
- Do you need critical path analysis or just connectivity information?

### **5. Available SPICE Models (KiCad-Spice-Library Research)**
**Model Library Scale**: 537+ SPICE model files across 7 categories

**Available Models**:
- **Digital Logic**: 74xx series (13 families: HC, LS, ALS, etc.)
- **Diodes**: General diodes, LEDs, Zener diodes  
- **Op-Amps**: LM358, TL072, TL082, Op07, and manufacturer collections
- **Transistors**: BJT (BC546, 2N3904/6, power), FET (JFET, MOSFET)
- **Manufacturer Libraries**:
  - Texas Instruments (80+ op-amp models)
  - Maxim Integrated (50+ precision models) 
  - Linear Technology (precision analog)
  - Infineon Technologies (power devices)

**Integration Strategy**:
- Use KiCad-Spice-Library as authoritative model source
- Map KiCad symbols to specific SPICE models automatically
- Support both basic models (Device:R) and advanced manufacturer models

**Questions**:
- Should we auto-map common symbols (Device:R → generic resistor, TI:LM358 → TI model)?
- Do you want manufacturer-specific models prioritized over generic ones?
- Should `.MODEL` parsing handle both simple and complex manufacturer models?

---

**Approval Required**: Please review and approve this PRD before beginning implementation.

**Next Steps**: Upon approval, create detailed technical specifications and begin Phase 1 implementation with circuit-synth integration.