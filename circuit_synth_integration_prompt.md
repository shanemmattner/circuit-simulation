# Circuit-Synth Integration with Circuit-Simulation - Agent Prompt

## Mission
Integrate **circuit-synth** (Python library for KiCad circuit definition) with **circuit-simulation** (Python library for ngspice-based circuit simulation) to create a seamless design-to-simulation workflow.

## Project Context (Fast Memory-Bank Consolidated)

### Circuit-Simulation Capabilities
- **Core**: Production-ready Python library for circuit simulation
- **Engine**: ngspice 36 in Docker containers for reliable simulation
- **APIs**: 
  - Python API for circuit definition (PySpice integration)
  - FastAPI web service with REST endpoints and WebSocket support
  - MCP server with 8 tools for AI integration
- **Formats**: 
  - SPICE netlist parsing (.cir files with .MODEL/.SUBCKT support)
  - KiCad netlist import (.net files) with intelligent model mapping
  - Interactive Plotly reports (HTML/PDF export)
- **Architecture**: 
  - Docker containerized simulation backend
  - Professional CLI with progress bars
  - Report generation system (HTML, PDF, interactive charts)
  - >85% test coverage, strict typing, professional development standards

### Circuit-Synth Context (User-Provided)
- **Type**: Python library submodule for KiCad circuit definition
- **Purpose**: Programmatic creation of KiCad circuits in Python
- **Relationship**: Circuit design/synthesis tool that could benefit from simulation validation

## Integration Objectives

### Primary Goals
1. **Seamless Workflow**: circuit-synth creates circuits → circuit-simulation validates them
2. **Data Bridge**: Efficient translation between circuit-synth definitions and simulation formats
3. **Design Validation**: Integrate simulation results back into design workflow
4. **Professional Quality**: Production-ready integration matching both projects' standards

### Integration Architecture Options

#### Option A: Library Dependency
- circuit-synth depends on circuit-simulation
- Direct Python API calls for simulation
- Tight coupling, simple deployment

#### Option B: Service Integration  
- circuit-synth calls circuit-simulation FastAPI endpoints
- Loose coupling, scalable, language-agnostic
- Requires service deployment and management

#### Option C: Shared Data Layer
- Both libraries work with common circuit representations
- File-based or database-mediated integration
- Maximum flexibility, complex data management

#### Option D: Plugin Architecture
- circuit-simulation provides plugin interface for circuit sources
- circuit-synth implements the plugin interface
- Extensible, clean separation of concerns

## Technical Integration Points

### Data Format Bridging
- **From circuit-synth**: Python circuit definitions → ?
- **To circuit-simulation**: SPICE netlist, KiCad netlist, or Python circuit objects
- **Considerations**: Component mapping, parameter conversion, validation

### Component Library Alignment
- **Circuit-synth components**: KiCad component library
- **Circuit-simulation models**: SPICE models (.MODEL definitions)
- **Challenge**: Map KiCad components to appropriate SPICE models
- **Opportunity**: Leverage existing intelligent model mapping system

### Simulation Integration Patterns
```python
# Pattern 1: Direct API
from circuit_synth import Circuit as SynthCircuit
from circuit_sim import simulate_circuit

synth_circuit = SynthCircuit().add_resistor(...)
sim_result = simulate_circuit(synth_circuit.to_simulation_circuit())

# Pattern 2: File-based
synth_circuit.export_netlist("design.net") 
sim_result = simulate_circuit.from_kicad_netlist("design.net")

# Pattern 3: Service-based
sim_result = await circuit_sim_api.simulate(synth_circuit.to_dict())
```

### Error Handling & Validation
- **Design Rule Checks**: Validate circuit-synth designs before simulation
- **Simulation Errors**: Handle convergence failures, invalid components gracefully
- **User Feedback**: Clear error messages bridging design and simulation domains

## Development Requirements

### Code Quality Standards (Both Projects)
- **Testing**: TDD with >85% coverage, comprehensive integration tests
- **Typing**: Full type hints with mypy --strict validation
- **Documentation**: Clear API docs, examples, integration guides
- **Performance**: Design-time operations <1s, simulation handoff <5s

### Integration Testing Strategy
- **Unit Tests**: Individual bridge components
- **Integration Tests**: End-to-end design-to-simulation workflows
- **Performance Tests**: Realistic circuit size benchmarks
- **Compatibility Tests**: Multiple KiCad versions, SPICE model variations

### Deployment & Distribution
- **Packaging**: How to distribute the integration (pip install, submodules, etc.)
- **Dependencies**: Manage Docker requirements for simulation backend
- **Documentation**: User guides for the integrated workflow
- **Examples**: Complete design-to-simulation tutorials

## Agent Objectives

### Research Phase
1. **Analyze circuit-synth**: Examine the submodule code structure, APIs, component models
2. **Map Integration Points**: Identify exactly where/how the libraries should connect
3. **Assess Data Formats**: Understand circuit-synth's internal representations
4. **Evaluate Options**: Recommend optimal integration architecture

### Planning Phase  
1. **Create Integration PRD**: Detailed technical requirements and implementation plan
2. **Design API Surface**: Clean integration interfaces for both libraries
3. **Plan Development Phases**: Break into testable, iterative development segments
4. **Define Success Metrics**: How to validate successful integration

### Implementation Guidance
1. **Data Bridge Implementation**: Code for converting between circuit representations
2. **API Integration**: Implement chosen integration pattern (service, library, etc.)
3. **Error Handling**: Robust error recovery and user feedback systems
4. **Testing Infrastructure**: Comprehensive test suites for integration

## Key Questions to Answer

### Technical Architecture
1. What is circuit-synth's internal circuit representation format?
2. How does circuit-synth handle component parameters and connections?
3. What's the best data exchange format between the libraries?
4. Should the integration be synchronous or asynchronous?

### User Experience  
1. What does the ideal design-to-simulation workflow look like?
2. How should simulation results be presented to circuit designers?
3. What level of SPICE/simulation knowledge should be required?
4. How to handle simulation failures or convergence issues?

### Development Strategy
1. Which integration architecture provides the best balance of simplicity and flexibility?
2. What's the minimal viable integration for initial release?
3. How to maintain both projects independently while supporting integration?
4. What examples and documentation are needed for adoption?

## Success Criteria

### Functional Requirements
- [ ] circuit-synth circuits can be simulated without manual conversion
- [ ] Simulation results integrate cleanly back into design workflow  
- [ ] Common design patterns (amplifiers, filters, etc.) work end-to-end
- [ ] Error messages are actionable for circuit designers
- [ ] Performance meets professional development standards

### Quality Requirements  
- [ ] Integration maintains >85% test coverage in both projects
- [ ] Type checking passes with mypy --strict
- [ ] Integration examples work reliably
- [ ] Documentation covers complete workflows
- [ ] No regressions in either project's existing functionality

### User Experience Requirements
- [ ] Integration feels natural and seamless
- [ ] Learning curve is reasonable for target users
- [ ] Error recovery is graceful and informative
- [ ] Performance is acceptable for typical design workflows
- [ ] Examples and tutorials support common use cases

## Context for Agent

This integration represents a significant enhancement to both circuit-synth and circuit-simulation, enabling a complete Python-based electronic design workflow. The agent should focus on:

1. **Understanding circuit-synth deeply** - examining its code, APIs, and design patterns
2. **Designing clean integration points** - avoiding tight coupling while enabling seamless workflows  
3. **Maintaining professional standards** - both projects have high quality bars
4. **Planning incremental delivery** - break into testable phases for iterative development

The circuit-simulation project already has robust infrastructure (Docker simulation, API services, MCP integration, professional CLI) that the integration should leverage rather than duplicate.

## Output Expectations

The agent should provide:
1. **Technical Analysis**: Deep understanding of circuit-synth architecture and integration opportunities
2. **Integration Design**: Recommended architecture with clear rationale
3. **Implementation Plan**: Phased development approach with clear milestones
4. **Code Examples**: Concrete integration patterns and API designs
5. **Risk Assessment**: Potential challenges and mitigation strategies

This integration has the potential to create a powerful, Python-native electronic design and simulation ecosystem that serves both professional engineers and students learning circuit design.