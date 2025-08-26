# Circuit Simulation Platform Research Notes

## Executive Summary
Building a portable, easy-to-use circuit simulation platform leveraging PySpice and existing tools, potentially exposed via MCP.

## Existing Assets Analysis

### circuit-synth Repository
- **Core Value**: Python-based KiCad integration with AI assistance
- **Key Features**:
  - Hierarchical circuit design via Python decorators
  - KiCad schematic generation
  - AI agents for design assistance (circuit-architect, simulation-expert)
  - SPICE simulation support built-in
- **Integration Potential**: HIGH - Already has SPICE integration and Python API

### KiCad-Spice-Library
- **Core Value**: 50,000+ SPICE models centralized
- **Key Features**:
  - Model search/extraction scripts
  - GUI for model browsing
  - Organized by manufacturer/component type
- **Integration Potential**: HIGH - Essential model library

### wingel/simulation
- **Core Value**: Direct KiCad schematic → SPICE simulation
- **Key Features**:
  - Multiple backend support (Ngspice, Xyce, LTspice)
  - Jupyter notebook integration
  - Matplotlib visualization
- **Integration Potential**: MEDIUM - Early stage but good architecture ideas

## Technology Stack Analysis

### PySpice
**Pros:**
- Mature, well-documented
- Ngspice/Xyce backend support
- Numpy integration for analysis
- Active conda-forge packaging

**Cons:**
- Limited to Ngspice v34
- Complex installation on some platforms

**Docker Status:** No official container, but feasible via conda-forge

### Alternative Libraries
- **Lcapy**: Symbolic analysis, good for education/theory
- **Ahkab**: Pure Python but unmaintained (2015)
- **scikit-rf**: RF/microwave specific

### MCP Integration
- Open standard (Nov 2024) for AI-tool integration
- Rapid adoption (OpenAI, Google, Microsoft)
- Perfect for exposing simulation capabilities to AI agents
- Client-server architecture fits simulation workflow

## Architecture Recommendations

### Core Design
```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   MCP API   │────▶│  Simulation  │────▶│   PySpice    │
│   Server    │     │   Manager    │     │   Backend    │
└─────────────┘     └──────────────┘     └──────────────┘
                            │
                    ┌───────┴────────┐
                    │                 │
            ┌───────▼──────┐ ┌───────▼──────┐
            │    KiCad     │ │    Model     │
            │  Integration │ │   Library    │
            └──────────────┘ └──────────────┘
```

### Key Components
1. **Simulation Manager**: Orchestrates simulation requests
2. **Backend Abstraction**: Support multiple engines (Ngspice, Xyce)
3. **Model Library**: Integrated SPICE model management
4. **KiCad Bridge**: Import/export schematics
5. **MCP Server**: Expose capabilities to AI/external tools

### Deployment Strategy
- **Docker Primary**: All-in-one container with PySpice + dependencies
- **Conda Alternative**: For direct installation
- **MCP Interface**: Standard protocol for tool integration

## Implementation Priorities

### Phase 1: Core Infrastructure
- PySpice setup with Docker
- Basic simulation API
- Model library integration

### Phase 2: Enhanced Features
- KiCad schematic import
- Multi-backend support
- Result visualization

### Phase 3: MCP Integration
- MCP server implementation
- Tool registration
- AI agent integration

## Open Questions

### Technical
1. Ngspice vs Xyce as primary backend?
2. Docker base image preference (Ubuntu/Alpine/Debian)?
3. Python version requirement (3.10+ for better typing)?

### Product
1. Primary use cases to optimize for?
2. GUI requirements or CLI/API only?
3. Real-time simulation needs?
4. Circuit complexity targets (component count)?

### Integration
1. Authentication/authorization needs for MCP?
2. Result format preferences (JSON/HDF5/CSV)?
3. Existing workflow integration points?

## Risk Assessment

### High Priority
- Ngspice version limitations in PySpice
- Docker image size (could be 1GB+)
- Model library licensing/distribution

### Medium Priority
- Performance for large circuits
- Cross-platform compatibility
- MCP specification changes (still evolving)

### Mitigation Strategies
- Abstract backend interface for flexibility
- Layer Docker images for size optimization
- Cache model libraries locally