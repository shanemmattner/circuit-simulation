# Circuit Simulation Platform - Project Brief

## Project Overview
**Name**: circuit-simulation  
**Goal**: Build a modern, accessible circuit simulation platform that serves both professional engineers and students  
**Core Value**: Make SPICE simulation easy to use with beautiful, interactive reports

## Core Requirements

### Must Have (MVP)
1. **Simulation Engine**
   - PySpice wrapper around Ngspice
   - Support basic components (R, L, C, diodes, transistors)
   - DC, AC, and transient analysis
   - Python API for circuit definition

2. **Reporting**
   - Plotly-based interactive visualizations
   - Professional report generation
   - Export to HTML, PDF, PNG

3. **Deployment**
   - Docker container (Ubuntu base)
   - Self-hosted capability
   - Python 3.10+ support

4. **Education**
   - Tutorial circuits with explanations
   - "Why simulate?" documentation
   - Professional use case examples

### Future Goals
- Xyce backend for large circuits (>10k components)
- MCP server for AI integration
- KiCad schematic import
- Cloud-hosted option
- Monte Carlo analysis
- Temperature sweeps

## Target Users
1. **Professional Engineers**: Pre-fabrication validation, debugging, optimization
2. **Students**: Learning circuit theory, building intuition
3. **Educators**: Teaching tool with interactive examples
4. **AI Developers**: MCP integration for circuit analysis

## Success Criteria
- Simulate common circuits in <5 seconds
- Generate interactive reports users actually want to use
- One-command installation via Docker
- Clear educational path from beginner to professional

## Technical Decisions
- **Language**: Python (accessible, great scientific ecosystem)
- **Primary Backend**: Ngspice (mature, well-supported)
- **Visualization**: Plotly (interactive, professional)
- **Deployment**: Docker (consistency, portability)
- **Architecture**: API-first (enables multiple interfaces)

## Business Model (TBD)
Considering open core model:
- Core simulation: Open source
- Premium: Advanced features, cloud compute, support

## Constraints
- Must be easier to use than existing tools
- Reports must be professional quality
- Must handle both simple and complex circuits
- Must provide educational value

## Timeline
ASAP delivery for MVP, with iterative improvements based on user feedback