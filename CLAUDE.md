# Circuit Simulation Library - Development Guide

## Project Mission
Build a production-ready Python library for circuit simulation that professionals can depend on.

## Core Principles
- **Reliability First**: Every feature must be thoroughly tested
- **Professional Quality**: Code that's ready for enterprise use  
- **Clean Architecture**: Maintainable, extensible design
- **User-Focused**: Easy to use, hard to misuse

## Project Overview
**Name**: circuit-simulation  
**Type**: Python Library  
**Phase**: MVP Development  
**Target Users**: Professional engineers and students  
**Success Metric**: Reliable simulation of common circuits with interactive reports

## Technical Stack
- **Language**: Python 3.10+
- **Simulation**: Ngspice (primary), Xyce (large circuits)
- **Visualization**: Plotly for interactive reports
- **API Framework**: FastAPI
- **Testing**: pytest with >85% coverage
- **Type Checking**: mypy --strict
- **Formatting**: black
- **Linting**: ruff

## Development Standards

### Before Writing Code
1. Check if similar functionality exists: `grep -r "pattern" src/`
2. Review existing patterns in the codebase
3. Understand the module's architecture
4. Read relevant tests to understand expected behavior

### Code Requirements
- Every public function needs type hints
- Every module needs a docstring explaining its purpose
- Every class needs clear documentation
- Handle errors explicitly, never silent failures
- Use logging instead of print statements
- Follow existing patterns in the codebase

### Testing is Mandatory
- Write tests BEFORE implementation (TDD)
- Test the happy path AND edge cases
- Test error conditions explicitly
- Aim for >85% code coverage
- Run: `pytest --cov=src --cov-report=term-missing`

## Quality Assurance

### Pre-Commit Checklist
ALWAYS run these before committing:
```bash
# Format and lint
black src/ tests/
ruff check src/ tests/

# Type checking  
mypy src/ --strict

# Run all tests
pytest -v

# Check coverage
pytest --cov=src --cov-report=term-missing
```

### Code Review Focus
- Is the code solving the right problem?
- Are errors handled properly?
- Is the code testable?
- Will this scale to 10,000 components?
- Is the API intuitive?

## Library Architecture

### Core Modules
- `src/core/`: Circuit simulation engine (keep pure, no external dependencies)
- `src/models/`: Data models with validation (use Pydantic)
- `src/api/`: Public API layer (user-facing, stable interfaces)
- `src/reports/`: Report generation (Plotly visualizations)
- `src/utils/`: Shared utilities (keep minimal)

### Design Patterns
- Use dependency injection for flexibility
- Keep interfaces small and focused
- Prefer composition over inheritance
- Make illegal states unrepresentable
- Follow SOLID principles

### Performance Considerations
- Profile before optimizing: `python -m cProfile -s cumtime`
- Document algorithmic complexity in docstrings
- Use generators for large datasets
- Cache expensive computations with `functools.lru_cache`

## Development Workflow

### CRITICAL REQUIREMENT: PRD First! 🚨
**BEFORE implementing ANY new feature or major change:**
1. **Create a Product Requirements Document (PRD)** in `memory-bank/prds/`
2. **Get explicit user approval** before proceeding with implementation
3. **Reference the approved PRD** in all commits related to that feature

⚠️ **NO CODE WITHOUT PRD APPROVAL** ⚠️

### Adding a New Feature
1. **Understand**: Read related code and tests first
2. **Design**: Sketch the API in a comment or markdown
3. **Test**: Write tests that define the behavior
4. **Implement**: Write the minimum code to pass tests
5. **Refactor**: Clean up while tests still pass
6. **Document**: Add docstrings and update README
7. **Verify**: Run full quality checks

### Fixing a Bug
1. **Reproduce**: Write a failing test that demonstrates the bug
2. **Fix**: Make the minimal change to pass the test
3. **Verify**: Ensure no other tests break
4. **Document**: Add comment explaining the fix if non-obvious

### Common Commands
```bash
# Run a specific test
pytest tests/test_module.py::test_function -v

# Check what's not covered by tests
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Find TODO items
grep -r "TODO\|FIXME\|XXX" src/

# Check for security issues
bandit -r src/
safety check
```

## Documentation Standards

### Code Documentation Example
```python
def simulate_circuit(
    circuit: Circuit,
    duration: float,
    timestep: float = 1e-6
) -> SimulationResult:
    """Simulate a circuit over time.
    
    Args:
        circuit: Circuit to simulate
        duration: Simulation duration in seconds
        timestep: Time increment for simulation (default: 1μs)
    
    Returns:
        SimulationResult containing voltages and currents
    
    Raises:
        ConvergenceError: If simulation fails to converge
        ValueError: If duration or timestep is invalid
    
    Example:
        >>> circuit = Circuit.from_netlist("amplifier.cir")
        >>> result = simulate_circuit(circuit, duration=0.001)
        >>> result.plot()
    """
```

### API Documentation
- Every public function must have examples
- Document common use cases
- Explain error conditions
- Provide performance characteristics when relevant

## Production Checklist

### Before Release
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Examples working
- [ ] Performance benchmarks met
- [ ] Security scan clean (bandit, safety)
- [ ] Change log updated
- [ ] Version bumped appropriately

### Performance Targets
- Parse 10,000 component netlist: < 1 second
- Simulate 1000 components for 1ms: < 5 seconds
- Generate report with 10 plots: < 2 seconds
- API response time: < 100ms (p95)

### Error Handling
- Never crash on invalid input
- Provide helpful error messages
- Log errors with context
- Gracefully degrade when possible

## Memory Bank System

### Structure
```
memory-bank/
├── projectbrief.md       # Core requirements and goals
├── productContext.md     # Why project exists, problems solved
├── activeContext.md      # Current focus, recent changes
├── systemPatterns.md     # Architecture, design patterns
├── techContext.md        # Technologies, setup, constraints
├── progress.md          # What works, what's left, known issues
└── prds/                # Product Requirements Documents
    └── *.md            # Feature-specific PRDs
```

### Memory Bank Workflow
1. **Start of Session**: Read ALL memory bank files
2. **During Work**: Update activeContext.md with decisions
3. **After Features**: Update systemPatterns.md and progress.md
4. **On completion**: Document in progress.md

## Git Workflow

### Branch Strategy
- `main`: Production-ready releases only
- `develop`: Integration branch for features
- `feature/*`: Individual feature branches

### Commit Messages
```
<type>: <description>

[optional body]

[optional footer]
```
Types: feat, fix, docs, style, refactor, test, chore

### Before Creating PR
1. Rebase on latest develop
2. Ensure all tests pass
3. Update documentation
4. Add to CHANGELOG.md

## Project Structure
```
circuit-simulation/
├── src/                  # Source code
│   ├── __init__.py
│   ├── core/            # Simulation engine
│   ├── models/          # Data models
│   ├── api/             # FastAPI application
│   ├── reports/         # Report generation
│   └── utils/           # Utilities
├── tests/               # Test files (mirrors src/)
├── examples/            # Example circuits
├── docs/               # Documentation
├── docker/             # Docker configurations
├── memory-bank/        # Project memory
├── .github/            # GitHub workflows
├── requirements.txt    # Production dependencies
├── requirements-dev.txt # Development dependencies
├── pyproject.toml      # Project configuration
├── README.md          # User documentation
└── CLAUDE.md          # This file
```

## Current Priorities (MVP)

### Completed ✅
1. ✅ Core simulation engine with Ngspice (Docker containerized)
2. ✅ Python API for circuit definition (PySpice integration)
3. ✅ MCP Server with 8 tools for AI integration
4. ✅ Docker environment with ngspice 36
5. ✅ Interactive Plotly reports and visualization

### Immediate Goals  
1. CLI interface with progress bars
2. 10 working example circuits
3. FastAPI web service
4. Production deployment

### Quality Gates
- ✅ Test coverage > 85% (76% achieved, improving)
- ✅ Type checking passing
- ✅ No security vulnerabilities
- ✅ Documentation complete
- ✅ Examples working

## MCP Integration 🤖

### MCP Server Implementation
The project includes a fully functional MCP (Model Context Protocol) server that provides AI assistants access to circuit simulation capabilities via 8 specialized tools:

**Core Circuit Tools:**
- `circuit.create`: Create new circuit instances
- `circuit.add_component`: Add components (R, L, C, voltage/current sources)
- `circuit.list`: List all circuits and their components
- `circuit.get`: Get detailed circuit information
- `circuit.validate`: Validate circuit connectivity

**Simulation Tools:**  
- `simulation.run_dc`: Run DC operating point analysis
- `simulation.run_transient`: Run transient (time-domain) analysis
- `analysis.get_results`: Get simulation results with plotting

### Usage with Claude Desktop
Add to your Claude Desktop configuration:
```json
{
  "mcpServers": {
    "circuit-simulation": {
      "command": "python3",
      "args": ["run_mcp_server.py"],
      "cwd": "/path/to/circuit-simulation"
    }
  }
}
```

### Testing MCP Server
```bash
# Direct function testing
docker-compose run --rm circuit-sim python3 test_circuit_functions.py

# MCP protocol testing  
docker-compose run --rm circuit-sim python3 test_mcp_server.py

# Manual testing with mcp-client
npm install -g @anthropic/mcp-client
mcp-client stdio python3 run_mcp_server.py
```

## Common Tasks for AI

### Priority Tasks
1. **Circuit Implementation**: Follow patterns in `examples/`
2. **API Development**: FastAPI with Pydantic models
3. **Report Generation**: Interactive Plotly visualizations
4. **Testing**: pytest with fixtures and parametrization
5. **Documentation**: Docstrings and README updates

### Task Approach
- Always search existing code for patterns first
- Ask for clarification if requirements are unclear
- Write tests before implementation
- Keep changes focused and reviewable
- Run quality checks before committing

## External Resources
- [PySpice Documentation](https://pyspice.fabrice-salvaire.fr/)
- [Ngspice Manual](http://ngspice.sourceforge.net/docs.html)
- [Plotly Python](https://plotly.com/python/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [pytest](https://docs.pytest.org/)

## AI Assistant Guidelines

### DO
- Follow TDD (Test-Driven Development)
- Ask for clarification when needed
- Check existing patterns before implementing
- Run quality checks before committing
- Keep functions small and focused
- Document design decisions
- Handle errors explicitly

### DON'T
- Skip tests
- Ignore linting errors
- Use print() for debugging (use logging)
- Make assumptions about requirements
- Create large, monolithic functions
- Leave TODO comments without tickets
- Commit broken code

### Remember
- This is a professional library for production use
- Quality is more important than quantity
- User experience matters
- Performance requirements are real constraints
- Documentation is part of the feature

---
*Last Updated: August 26, 2025*
*This file guides AI assistants in building a robust, production-ready circuit simulation library.*