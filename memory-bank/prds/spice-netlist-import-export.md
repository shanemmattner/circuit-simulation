# PRD: SPICE Netlist Export & circuit-synth Integration

**Issue**: #8  
**Created**: August 27, 2025  
**Author**: Claude  
**Status**: Draft

## Executive Summary

Add SPICE netlist export capability to circuit-simulation and create a bridge to circuit-synth for comprehensive EDA workflow integration. Leverage existing circuit-synth JSON format and KiCad export capabilities rather than duplicating functionality.

## Problem Statement

Currently, the platform has:
- **Basic SPICE import** via `SpiceParser` for simple circuits
- **No SPICE export** - Cannot generate SPICE netlists from Circuit objects  
- **No circuit-synth integration** - Missing bridge to leverage existing JSON format and KiCad export

**circuit-synth already provides**:
- ✅ JSON circuit format with hierarchical support
- ✅ KiCad netlist export functionality  
- ✅ Professional circuit representation (Circuit, Component, Net, Pin)

**What's missing**: Integration layer and SPICE export functionality.

## Goals & Success Criteria

### Primary Goals
1. **SPICE Export Engine** - Generate industry-standard SPICE netlists from Circuit objects
2. **circuit-synth Bridge** - Bidirectional conversion: Circuit ↔ circuit-synth JSON ↔ KiCad
3. **Enhanced Import** - Use circuit-synth as intermediate format for complex circuits
4. **Professional Integration** - CLI and MCP tools for complete EDA workflow

### Success Metrics
- Export 10+ example circuits to valid SPICE netlists
- Seamless Circuit → circuit-synth JSON → KiCad netlist workflow
- Import circuit-synth JSON projects for simulation
- Integration with existing CLI and MCP tools

## Technical Requirements

### SPICE Export Engine
```python
class SpiceExporter:
    def export_circuit(self, circuit: Circuit) -> str:
        """Generate SPICE netlist from circuit-simulation Circuit object"""
        
    def export_to_file(self, circuit: Circuit, filepath: str):
        """Export circuit to .cir/.sp file"""
        
    def export_with_analysis(self, circuit: Circuit, analysis_commands: List[str]) -> str:
        """Export with SPICE analysis commands (.TRAN, .AC, .DC)"""
```

### circuit-synth Integration Bridge
```python
class CircuitSynthBridge:
    def to_circuit_synth_json(self, circuit: Circuit) -> Dict[str, Any]:
        """Convert Circuit to circuit-synth JSON format"""
        
    def from_circuit_synth_json(self, json_data: Dict[str, Any]) -> Circuit:
        """Import circuit-synth JSON for simulation"""
        
    def to_kicad_via_circuit_synth(self, circuit: Circuit, output_dir: str):
        """Generate KiCad project via circuit-synth (leverages existing export)"""
```

### Enhanced Import via circuit-synth
```python
class CircuitSynthImporter:
    def import_json_project(self, json_path: str) -> Circuit:
        """Import circuit-synth JSON project for simulation"""
        
    def import_kicad_netlist_via_circuit_synth(self, netlist_path: str) -> Circuit:
        """Import KiCad netlist using circuit-synth as intermediate format"""
```

### Integration Points
- **SPICE → Circuit**: Direct import (existing SpiceParser)
- **Circuit → SPICE**: New export functionality  
- **Circuit → circuit-synth JSON → KiCad**: Complete EDA workflow
- **circuit-synth JSON → Circuit**: Import existing projects for simulation

## Architecture

### Module Structure
```
src/io/
├── exporters/
│   ├── spice_exporter.py           # SPICE netlist export engine
│   └── circuit_synth_bridge.py     # Bridge to circuit-synth
├── importers/
│   ├── circuit_synth_importer.py   # Import circuit-synth JSON
│   └── enhanced_spice_parser.py    # Enhanced SPICE parser
└── integration/
    ├── format_converter.py         # Multi-format conversion
    └── workflow_manager.py         # End-to-end workflows
```

### Data Flow Architecture
```
SPICE Files → SpiceParser → Circuit Objects → Simulation
                                ↓
Circuit Objects → SpiceExporter → SPICE Files

Circuit Objects → CircuitSynthBridge → circuit-synth JSON → KiCad Project
                                                          ↓
circuit-synth JSON ← CircuitSynthImporter ← Circuit Objects

Multi-format workflow:
SPICE → Circuit → circuit-synth JSON → KiCad → PCB Design
```

### API Integration
```python
# CLI commands
circuit-sim export --format spice circuit.json
circuit-sim export --format circuit-synth circuit.json  
circuit-sim import circuit-synth-project.json

# MCP tools (3 new)
- export.to_spice(circuit_id, include_analysis=True)
- export.to_circuit_synth(circuit_id)
- import.from_circuit_synth(json_path)

# FastAPI endpoints
POST /api/circuits/export/{circuit_id}?format=spice
POST /api/circuits/export/{circuit_id}?format=circuit-synth
POST /api/circuits/import/circuit-synth
```

## Implementation Plan

### Phase 1: SPICE Export Engine (2 days)
**Chunk 1**: Basic SpiceExporter class - convert Circuit components to SPICE syntax
**Chunk 2**: Analysis command integration (.TRAN, .AC, .DC statements)
**Chunk 3**: Professional SPICE formatting with comments and validation

### Phase 2: circuit-synth Bridge (2 days)  
**Chunk 4**: CircuitSynthBridge - Circuit to circuit-synth JSON conversion
**Chunk 5**: CircuitSynthImporter - JSON to Circuit conversion
**Chunk 6**: Integration testing with existing circuit-synth projects

### Phase 3: Enhanced Workflows (2 days)
**Chunk 7**: Multi-format converter (Circuit → SPICE/JSON/KiCad workflows)
**Chunk 8**: CLI integration (export/import commands)
**Chunk 9**: MCP tools integration (3 new tools)

### Phase 4: Integration & Polish (2 days)
**Chunk 10**: FastAPI endpoint implementation  
**Chunk 11**: Comprehensive testing with example circuits
**Chunk 12**: Documentation and workflow examples

## User Stories

**As a professional engineer**, I want to:
- Export simulation-ready circuits to SPICE format for other SPICE simulators
- Import circuit-synth JSON projects to run simulations and analysis
- Generate KiCad projects from my simulation circuits for PCB design

**As a system integrator**, I want to:
- Use circuit-simulation as the analysis engine for circuit-synth projects
- Convert between SPICE, circuit-synth JSON, and KiCad formats seamlessly
- Leverage existing circuit-synth component intelligence and KiCad export

**As an EDA workflow user**, I want to:
- Complete workflow: SPICE → simulate → optimize → circuit-synth JSON → KiCad → PCB
- Import existing circuit-synth projects for validation and analysis
- Use MCP tools for AI-powered circuit analysis and optimization

## Technical Considerations

### SPICE Compliance
- **SPICE 3f5** compatibility as baseline standard
- **Ngspice extensions** support for enhanced functionality
- **Industry conventions** for component naming and organization

### Performance
- Export 1000+ component circuits in <2 seconds
- Streaming export for very large netlists (>10k components)  
- Memory-efficient import with lazy evaluation

### Quality Assurance
- Round-trip testing with 10 example circuits
- SPICE syntax validation against industry parsers
- Integration testing with existing simulation workflows

## Risks & Mitigation

**Risk**: SPICE syntax complexity and edge cases
**Mitigation**: Focus on 90% common use cases, extensive testing

**Risk**: Round-trip data loss or corruption  
**Mitigation**: Comprehensive integrity checking and validation

**Risk**: Performance with large netlists
**Mitigation**: Streaming I/O and memory optimization

## Dependencies

- Existing `SpiceParser` class as foundation
- `Circuit` API for component access  
- **circuit-synth submodule** for JSON format and KiCad export
- CLI framework for command integration
- MCP server for AI tool integration

## Definition of Done

- [ ] SpiceExporter generates valid SPICE netlists from Circuit objects
- [ ] CircuitSynthBridge converts Circuit ↔ circuit-synth JSON format
- [ ] CircuitSynthImporter loads existing circuit-synth projects for simulation
- [ ] CLI commands: `export --format spice/circuit-synth`, `import circuit-synth`
- [ ] MCP tools: `export.to_spice`, `export.to_circuit_synth`, `import.from_circuit_synth`
- [ ] FastAPI endpoints for multi-format export/import
- [ ] Complete workflow: Circuit → circuit-synth JSON → KiCad project generation
- [ ] Integration testing with circuit-synth example projects
- [ ] Documentation with EDA workflow examples

**Timeline**: 8 days total  
**Approval Required**: Yes - before implementation begins