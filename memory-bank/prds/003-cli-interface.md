# PRD-003: Command Line Interface (CLI) Implementation

**Date**: August 27, 2025  
**Status**: Draft  
**Priority**: High (MVP Critical)  
**GitHub Issue**: [#1](https://github.com/circuit-synth/circuit-simulation/issues/1)

## Executive Summary

Implement a professional command-line interface for the circuit simulation library that enables users to perform circuit operations directly from the terminal with progress feedback and clear error handling.

## Problem Statement

Currently, users can only interact with the circuit simulation library through Python code. To make the library truly professional and user-friendly, we need a CLI that allows:
- Quick circuit validation and simulation from netlists
- Progress feedback for long-running operations
- Easy integration into automation scripts and workflows
- Clear error messages for debugging

## Success Metrics

- ✅ CLI installable via `pip install circuit-sim` → `circuit-sim --help` works
- ✅ All simulation operations show progress bars
- ✅ Commands complete successfully for valid inputs
- ✅ Clear, actionable error messages for invalid inputs
- ✅ Help documentation accessible for all commands
- 📊 Target: <100ms response time for help/validation commands
- 📊 Target: Progress updates every 100ms during simulations

## User Stories

### Primary Users: Professional Engineers
- **As a circuit designer**, I want to validate netlists quickly without writing Python code
- **As an automation engineer**, I want to integrate circuit simulation into CI/CD pipelines
- **As a student**, I want simple commands to learn circuit behavior

### Secondary Users: DevOps/Integration
- **As a DevOps engineer**, I want predictable CLI behavior for scripting
- **As a tool integrator**, I want consistent exit codes and output formats

## Technical Requirements

### Core Commands
```bash
# Circuit operations
circuit-sim create --netlist path/to/circuit.cir --name "My Circuit"
circuit-sim validate --netlist path/to/circuit.cir
circuit-sim list  # List all circuits in current project
circuit-sim info --circuit-id <id>  # Get circuit details

# Simulation operations  
circuit-sim simulate dc --circuit-id <id> [--output results.json]
circuit-sim simulate transient --circuit-id <id> --duration 10ms [--timestep 1us]

# Report generation
circuit-sim report --results results.json [--format html|pdf|png]
circuit-sim plot --results results.json --type voltage|current [--nodes 1,2,3]

# Project management
circuit-sim init  # Initialize new circuit project
circuit-sim status  # Show project status
```

### Progress & User Experience
- **Progress Bars**: All operations >1s show Rich progress bars
- **Colored Output**: Success (green), warnings (yellow), errors (red)
- **Spinner Animations**: For indeterminate operations (parsing, validation)
- **Clear Error Messages**: Include file paths, line numbers, and suggestions

### Integration Requirements
- **Exit Codes**: 0=success, 1=user error, 2=system error, 3=simulation error
- **Output Formats**: JSON for scripting, human-readable for interactive use
- **Configuration**: Support `.circuit-sim.yml` project config files
- **Logging**: Debug logs to `~/.circuit-sim/logs/` with rotation

## Technical Design

### Architecture
```
src/circuit_sim/
├── cli/
│   ├── __init__.py
│   ├── main.py           # Entry point & CLI app setup
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── create.py     # Circuit creation commands
│   │   ├── simulate.py   # Simulation commands  
│   │   ├── report.py     # Report generation
│   │   └── project.py    # Project management
│   ├── utils/
│   │   ├── progress.py   # Progress bar utilities
│   │   ├── output.py     # Colored output helpers
│   │   └── config.py     # Configuration management
│   └── exceptions.py     # CLI-specific exceptions
```

### Technology Stack
- **Click** 8.1+: CLI framework for command definition
- **Rich** 13.0+: Progress bars, colored output, formatting
- **Pydantic**: Configuration validation
- **PySpice Integration**: Leverage existing simulation engine

### Error Handling Strategy
```python
# Error hierarchy
CLIError (base)
├── UserError (exit code 1)
│   ├── FileNotFoundError
│   ├── InvalidNetlistError  
│   └── InvalidArgumentError
├── SystemError (exit code 2)
│   ├── DependencyError
│   └── PermissionError
└── SimulationError (exit code 3)
    ├── ConvergenceError
    └── CircuitError
```

## Implementation Plan

### Phase 1: Core CLI Framework (Week 1)
- [ ] Set up Click application structure
- [ ] Implement basic commands: `init`, `help`, `version`
- [ ] Add Rich console setup with colored output
- [ ] Create error handling framework
- [ ] Write unit tests for CLI commands

### Phase 2: Circuit Operations (Week 1)  
- [ ] Implement `create` command with netlist parsing
- [ ] Add `validate` command with detailed error reporting
- [ ] Implement `list` and `info` commands
- [ ] Add progress bars for file I/O operations
- [ ] Integration tests with sample circuits

### Phase 3: Simulation Commands (Week 2)
- [ ] Implement `simulate dc` with progress tracking
- [ ] Add `simulate transient` with real-time updates
- [ ] Connect to existing PySpice simulation engine
- [ ] Add result caching and output options
- [ ] Performance testing with large circuits

### Phase 4: Reporting & Polish (Week 2)
- [ ] Implement `report` and `plot` commands
- [ ] Add configuration file support
- [ ] Comprehensive error message improvements
- [ ] Documentation and examples
- [ ] End-to-end testing

## Risk Assessment

### High Risk
- **Performance**: Large circuit simulations may block CLI responsiveness
  - *Mitigation*: Implement async progress tracking, consider background processing
  
### Medium Risk  
- **Complex Error Messages**: PySpice errors may be cryptic for end users
  - *Mitigation*: Error translation layer, user-friendly error database

### Low Risk
- **CLI Framework Choice**: Click is mature and stable
- **Progress Bar Library**: Rich is well-established

## Success Criteria

### MVP Acceptance Criteria
- [ ] `circuit-sim --help` shows all commands
- [ ] Can create circuit from netlist file
- [ ] Can run DC and transient simulations
- [ ] All operations >1s show progress bars
- [ ] Clear error messages for common mistakes
- [ ] Full test coverage of CLI commands

### Quality Gates
- [ ] All CLI commands have `--help` documentation  
- [ ] Error messages include actionable suggestions
- [ ] Exit codes follow standard conventions
- [ ] CLI response time <100ms for validation commands
- [ ] Memory usage <50MB for typical operations

## Future Enhancements (Post-MVP)

### Advanced Features
- Interactive mode with command suggestions
- Batch processing of multiple circuits
- Integration with version control (diff netlists)
- Cloud simulation backend support
- Plugin system for custom analyses

### Integration Opportunities  
- VS Code extension using CLI backend
- GitHub Actions for circuit validation
- Docker container with CLI pre-installed
- Jupyter notebook magic commands

## Appendix

### Example Usage Scenarios

**Scenario 1: Quick Circuit Validation**
```bash
$ circuit-sim validate examples/rc_filter.cir
✅ Circuit validation passed
📊 Components: 3 (1 voltage source, 1 resistor, 1 capacitor)  
📊 Nodes: 3 (including ground)
```

**Scenario 2: Automated Simulation**
```bash
$ circuit-sim simulate transient --circuit examples/rc_filter.cir --duration 10ms --output results.json
🔄 Parsing netlist... ████████████████████████████████████████ 100% 0:00:00
🔄 Running simulation... ████████████████████████░░░░░░░░░░░░ 75% 0:00:03
✅ Simulation complete! Results saved to results.json
```

**Scenario 3: Error Handling**  
```bash
$ circuit-sim simulate dc --circuit broken.cir
❌ Simulation failed: Circuit convergence error
💡 Suggestion: Check for floating nodes or unrealistic component values
📍 Problem may be near line 15: R1 n1 n2 1e-20
```

---
**Approval Required**: This PRD requires explicit approval before implementation begins.