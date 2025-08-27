# PRD: Hybrid MCP + Python Library Architecture

**Status**: DRAFT 📝  
**Version**: 1.0  
**Created**: August 26, 2024  
**Owner**: Circuit Simulation Team  

## Executive Summary

Enhance the circuit simulation platform to serve both AI-assisted workflows (via MCP) and direct Python development (via library) by creating a hybrid architecture where MCP tools generate equivalent Python code alongside their operations.

## Problem Statement

### Current State
- **MCP Server**: Works great for AI agents, but creates black-box experience
- **Python Library**: Provides transparency and flexibility, but requires more setup knowledge
- **User Fragmentation**: Different user types need different interfaces

### User Pain Points
- **Students/Engineers**: Want to understand the underlying code, learn APIs
- **AI Workflows**: Need simple, consistent interfaces for automation
- **Production Users**: Want to start with prototypes, then customize deeply
- **Learning Progression**: No clear path from AI-assisted → self-sufficient

## Vision Statement

> "Enable seamless progression from AI-assisted circuit design to professional Python development, serving both immediate productivity and long-term learning goals."

## Success Metrics

### Primary KPIs
- **User Adoption**: 70% of MCP users also use generated Python code
- **Educational Impact**: Users transition from MCP-only to Python library usage within 30 days
- **Code Quality**: Generated Python code passes all quality checks (black, ruff, mypy)
- **User Satisfaction**: 4.5/5 rating for "learning progression" experience

### Secondary KPIs
- **Integration Success**: MCP + Python hybrid workflows work seamlessly
- **Documentation Coverage**: 100% of MCP tools have Python code examples
- **Performance**: Code generation adds <100ms to MCP tool execution
- **Maintainability**: Single codebase powers both MCP and Python interfaces

## Target Users

### Primary Personas

**🎓 Engineering Student (Alex)**
- Needs: Learn circuit simulation, understand APIs, build portfolio projects
- Journey: MCP prototype → Study generated code → Write own Python
- Success: Graduates to independent Python development

**🤖 AI Workflow User (Taylor)**  
- Needs: Quick circuit generation, consistent results, automation
- Journey: Uses MCP for rapid prototyping, occasionally inspects generated code
- Success: Builds complex automated design workflows

**👨‍💼 Professional Engineer (Jordan)**
- Needs: Production-quality code, customization, performance optimization  
- Journey: MCP proof-of-concept → Export to Python → Customize for production
- Success: Ships production circuits with custom analysis tools

### Secondary Personas
- **📚 Educator**: Teaches with generated code examples
- **🔬 Researcher**: Uses MCP for rapid experimentation, Python for publications

## Functional Requirements

### Core Features

#### FR1: Dual-Mode MCP Tools
**Requirement**: All MCP tools support both standard operation and code generation mode

```json
{
  "generate_code": true,
  "save_to_file": true,
  "file_path": "circuits/rc_filter.py",
  "include_comments": true
}
```

**Acceptance Criteria**:
- MCP tools accept `generate_code` parameter
- Returns both standard result AND equivalent Python code
- Generated code is syntactically correct and executable
- Code follows project style guidelines (black, ruff compatible)

#### FR2: Python Code Templates
**Requirement**: Generated code uses consistent, idiomatic patterns

**Standards**:
- Type hints on all functions
- Descriptive variable names
- Educational comments explaining concepts
- Error handling with clear messages
- Follows existing library patterns

#### FR3: File Management Integration
**Requirement**: Generated code integrates seamlessly with project structure

**Capabilities**:
- Save generated files to appropriate directories
- Avoid filename conflicts with versioning
- Maintain imports and dependencies
- Generate complete, runnable examples

#### FR4: Progressive Learning Path
**Requirement**: Clear progression from MCP → Python mastery

**Components**:
- Generated code includes "Next Steps" comments
- Documentation links to relevant Python library sections  
- Examples show how to extend/modify the generated code
- Complexity progression (basic → intermediate → advanced)

### Technical Requirements

#### TR1: Architecture Consistency
**Requirement**: Both MCP and Python library use same core engine

**Implementation**:
- Shared simulation engine (`src/core/`)
- MCP server imports Python library classes
- Generated code uses public Python library APIs
- No code duplication between interfaces

#### TR2: Code Generation Engine
**Requirement**: Robust, testable code generation system

**Components**:
- Template engine for Python code generation
- AST validation for generated code
- Automated testing of generated examples
- Version compatibility handling

#### TR3: Performance Standards
**Requirement**: Code generation doesn't impact MCP responsiveness

**Targets**:
- Code generation: <100ms overhead
- File I/O operations: Non-blocking
- Memory usage: <10MB additional per circuit
- Concurrent request handling maintained

## User Experience Requirements

### UX1: Seamless Mode Switching
Users can easily toggle between MCP-only and hybrid modes:

```bash
# MCP only (existing behavior)
circuit.create "RC Filter"

# Hybrid mode (new capability)
circuit.create "RC Filter" --generate-code --save-file
```

### UX2: Educational Code Quality
Generated Python code serves as learning material:

- Clear variable names explaining circuit concepts
- Comments explaining why each step is necessary
- Links to documentation for deeper learning
- Examples showing common variations/extensions

### UX3: Production Readiness
Generated code is immediately useful for production:

- Proper error handling and validation
- Performance-conscious implementations
- Extensible architecture
- Integration with testing frameworks

## Technical Design

### Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Server    │───▶│   Core Library   │◀───│  Direct Python  │
│                 │    │                  │    │     Usage       │
│ • JSON-RPC API  │    │ • Circuit Class  │    │ • Import library│
│ • Code Gen      │    │ • Simulation     │    │ • Write custom  │
│ • File Output   │    │ • Validation     │    │ • Full control  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌──────────────────────┐
                    │   Generated Python   │
                    │                      │
                    │ • Educational        │
                    │ • Executable         │
                    │ • Customizable       │
                    │ • Version controlled │
                    └──────────────────────┘
```

### Code Generation Pipeline

1. **MCP Tool Execution**: Standard operation + capture parameters
2. **Template Selection**: Choose appropriate Python template
3. **Code Generation**: Fill template with circuit-specific data
4. **Validation**: AST parsing, syntax checking, style verification
5. **File Output**: Save to project structure with proper naming
6. **Response**: Return both MCP result and generated code info

### Generated Code Structure

```python
#!/usr/bin/env python3
"""
RC Low-Pass Filter Circuit
Generated by Circuit Simulation MCP Server
Created: 2024-08-26 16:53:07

Filter Characteristics:
- Cutoff Frequency: ~1.59 kHz  
- Input Impedance: 1 kΩ
- Applications: Audio filtering, noise reduction
"""

from circuit_sim import Circuit, VoltageSource, Resistor, Capacitor
from circuit_sim.analysis import DCAnalysis, ACAnalysis


def create_rc_filter() -> Circuit:
    """Create an RC low-pass filter circuit.
    
    Returns:
        Circuit: Configured RC filter ready for simulation
    """
    # Create circuit container
    circuit = Circuit("RC Low-Pass Filter")
    
    # Add voltage source (1V DC for testing)
    circuit.add(VoltageSource("V1", voltage="1V", 
                              positive=1, negative=0))
    
    # Add filter components
    circuit.add(Resistor("R1", resistance="1k", 
                         node1=1, node2=2))
    circuit.add(Capacitor("C1", capacitance="100nF", 
                          node1=2, node2=0))
    
    return circuit


def analyze_filter(circuit: Circuit) -> None:
    """Perform comprehensive filter analysis."""
    # DC Analysis - steady-state response
    dc_result = DCAnalysis(circuit).run()
    print(f"DC Output Voltage: {dc_result.node_voltage(2):.3f}V")
    
    # AC Analysis - frequency response  
    ac_result = ACAnalysis(circuit).frequency_sweep(
        start_freq="10Hz", stop_freq="100kHz", points=100)
    ac_result.plot_bode_plot(output_node=2)


if __name__ == "__main__":
    # Create and analyze the RC filter
    filter_circuit = create_rc_filter()
    
    # Validate circuit before analysis
    if filter_circuit.validate():
        print("✅ Circuit validation passed")
        analyze_filter(filter_circuit)
    else:
        print("❌ Circuit validation failed")
        
    # Next Steps:
    # 1. Modify component values to change cutoff frequency
    # 2. Add multiple stages for steeper rolloff  
    # 3. Compare with high-pass filter (swap R and C)
    # 4. Add noise analysis for real-world performance
    #
    # Documentation: https://circuit-sim.readthedocs.io/filters/
```

## Open Questions & Decisions Needed

### Technical Decisions

#### Q1: Code Generation Approach
**Question**: Template-based vs AST-based code generation?

**Options**:
- **Template-based**: Jinja2 templates, easier to maintain/customize
- **AST-based**: Python `ast` module, more flexible but complex
- **Hybrid**: Templates for structure, AST for dynamic parts

**Decision Criteria**: Maintainability, flexibility, performance
**Recommendation**: Template-based for MVP, evaluate AST for v2

#### Q2: File Management Strategy  
**Question**: How should generated files be organized and named?

**Options**:
- **Timestamp-based**: `rc_filter_20240826_165307.py`
- **Increment-based**: `rc_filter_v1.py`, `rc_filter_v2.py`  
- **User-specified**: Let users choose filenames
- **Git-integrated**: Use git commits for versioning

**Decision Criteria**: User workflow, conflict avoidance, discoverability
**Recommendation**: User-specified with smart defaults + increment fallback

#### Q3: Template Complexity
**Question**: How sophisticated should generated code be?

**Levels**:
- **Basic**: Just the circuit creation, minimal comments
- **Educational**: Extensive comments, learning resources, next steps
- **Production**: Error handling, logging, optimization, tests
- **Configurable**: User chooses complexity level

**Decision Criteria**: User needs, maintenance burden, code quality
**Recommendation**: Configurable with "educational" as default

### Product Decisions

#### Q4: Integration Points
**Question**: Where should code generation be exposed?

**Options**:
- **MCP-only**: Keep Python library separate, MCP generates code  
- **Library-integrated**: Python library can also generate MCP server code
- **Bidirectional**: Full round-trip code ↔ MCP conversion
- **CLI-integrated**: `circuit-sim generate` command

**Decision Criteria**: User workflows, complexity, maintenance
**Recommendation**: Start MCP-only, evaluate CLI integration

#### Q5: Learning Path Design
**Question**: How do we guide users from MCP → Python mastery?

**Components**:
- **Progressive Examples**: Basic → intermediate → advanced
- **Challenge Problems**: "Try modifying this circuit to..."
- **Tutorial Integration**: Generated code links to specific tutorials  
- **Community Features**: Share and discuss generated circuits

**Decision Criteria**: Educational effectiveness, engagement, resource constraints
**Recommendation**: Progressive examples + challenge problems for MVP

### Business/Strategy Questions

#### Q6: User Onboarding
**Question**: Which interface should new users see first?

**Approaches**:
- **MCP-first**: Start with AI assistance, graduate to Python
- **Python-first**: Learn fundamentals, then use AI acceleration
- **Choose-your-path**: Let users self-select based on experience
- **Guided-assessment**: Quiz users to recommend starting point

**Decision Criteria**: Learning outcomes, user satisfaction, retention
**Recommendation**: Guided assessment with MCP-first for most users

#### Q7: Documentation Strategy
**Question**: How do we document this hybrid approach?

**Sections Needed**:
- **Quick Start**: Get working circuit in 5 minutes (MCP)
- **Learning Path**: Progression from MCP → Python mastery
- **API Reference**: Complete Python library documentation  
- **Code Examples**: Generated code gallery with explanations
- **Best Practices**: When to use MCP vs Python

**Decision Criteria**: User success, support burden, maintenance cost
**Recommendation**: Parallel docs structure with clear navigation between modes

## Implementation Phases

### Phase 1: Core Code Generation (2 weeks)
**Scope**: Basic code generation for existing MCP tools

**Deliverables**:
- Code generation engine with templates
- Updated MCP tools with `generate_code` parameter
- File output management system
- Basic template for circuit creation
- Unit tests for code generation

**Success Criteria**:
- All 8 MCP tools can generate equivalent Python code
- Generated code passes linting and type checking
- Files saved to appropriate project structure

### Phase 2: Enhanced Templates (1 week)
**Scope**: Improve generated code quality and educational value

**Deliverables**:
- Educational comments and documentation links
- Error handling and validation in generated code
- "Next Steps" suggestions in generated files
- Multiple complexity levels (basic/educational/production)

**Success Criteria**:
- Generated code suitable for learning progression
- Code examples demonstrate best practices
- Clear path for user customization

### Phase 3: Integration & Testing (1 week)  
**Scope**: End-to-end testing and documentation

**Deliverables**:
- Comprehensive test suite for generated code
- Updated documentation with hybrid approach
- Example learning progression workflows
- Performance optimization and monitoring

**Success Criteria**:
- Generated code executes successfully in fresh environments
- Documentation demonstrates clear learning path
- Performance meets specified targets

### Phase 4: Advanced Features (2 weeks)
**Scope**: Enhanced user experience and advanced capabilities

**Deliverables**:
- CLI integration (`circuit-sim generate`)
- Advanced templates (production-ready, with tests)
- Code modification suggestions
- Integration with external tools (Jupyter, VS Code)

**Success Criteria**:
- Users can generate production-quality Python code
- Seamless workflow integration
- Advanced users have full customization control

## Risk Assessment

### High Risk
- **Code Quality**: Generated code might not meet professional standards
  - **Mitigation**: Extensive testing, AST validation, style checking
  
- **Maintenance Burden**: Two interfaces = double maintenance cost
  - **Mitigation**: Shared core engine, automated testing, template-based approach

### Medium Risk  
- **User Confusion**: Two interfaces might fragment user base
  - **Mitigation**: Clear documentation, guided onboarding, progressive disclosure

- **Performance Impact**: Code generation adds latency to MCP tools
  - **Mitigation**: Async generation, caching, performance monitoring

### Low Risk
- **Template Complexity**: Code generation templates become unwieldy  
  - **Mitigation**: Modular templates, template inheritance, regular refactoring

## Conclusion

The hybrid MCP + Python library approach addresses real user needs for both immediate productivity (MCP) and long-term learning/customization (Python). The phased implementation plan allows us to validate the concept quickly while building toward a comprehensive solution.

**Key Decision Required**: Approval to proceed with Phase 1 implementation.

---

**Next Steps**:
1. Get stakeholder approval for this PRD
2. Set up development branch for hybrid implementation  
3. Begin Phase 1: Core code generation engine
4. User testing with engineering students for educational effectiveness
