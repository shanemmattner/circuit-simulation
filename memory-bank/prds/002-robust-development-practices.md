# PRD: CLAUDE.md for Robust Library Development

## Objective

Update CLAUDE.md to guide AI assistants in building a professional, robust circuit simulation library that's production-ready and maintainable.

## Core Focus

Transform the current CLAUDE.md into a development guide that ensures:
- High-quality, well-tested code
- Professional library architecture
- Consistent development practices
- Production-ready features

## Proposed Improvements

### 1. Library Development Focus

```markdown
# Circuit Simulation Library - Development Guide

## Project Mission
Build a production-ready Python library for circuit simulation that professionals can depend on.

## Core Principles
- **Reliability First**: Every feature must be thoroughly tested
- **Professional Quality**: Code that's ready for enterprise use
- **Clean Architecture**: Maintainable, extensible design
- **User-Focused**: Easy to use, hard to misuse
```

### 2. Robust Development Practices

```markdown
## Development Standards

### Before Writing Code
1. Check if similar functionality exists: `grep -r "function_name" src/`
2. Review existing patterns in the codebase
3. Understand the module's architecture

### Code Requirements
- Every public function needs type hints
- Every module needs a docstring explaining its purpose
- Every class needs clear documentation
- Handle errors explicitly, never silent failures
- Use logging instead of print statements

### Testing is Mandatory
- Write tests BEFORE implementation (TDD)
- Test the happy path AND edge cases
- Test error conditions explicitly
- Aim for >85% code coverage
- Run: `pytest --cov=src --cov-report=term-missing`
```

### 3. Quality Checkpoints

```markdown
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

# Check for common issues
python -m pip check
safety check
```

### Code Review Focus
- Is the code solving the right problem?
- Are errors handled properly?
- Is the code testable?
- Will this scale to 10,000 components?
- Is the API intuitive?
```

### 4. Library Architecture

```markdown
## Library Structure

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
- Profile before optimizing
- Document algorithmic complexity
- Use generators for large datasets
- Cache expensive computations
```

### 5. Practical Development Workflow

```markdown
## Development Workflow

### Adding a New Feature
1. **Understand**: Read related code and tests first
2. **Design**: Sketch the API in a comment
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
# Run a specific test
pytest tests/test_module.py::test_function -v

# Check what's not covered by tests
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Profile performance
python -m cProfile -s cumtime src/main.py

# Find TODO items
grep -r "TODO\|FIXME\|XXX" src/
```

### 6. Professional Documentation

```markdown
## Documentation Standards

### Code Documentation
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
```

### 7. Production Readiness

```markdown
## Production Checklist

### Before Release
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Examples working
- [ ] Performance benchmarks met
- [ ] Security scan clean
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
```

## Implementation Steps

### Week 1: Foundation
1. Update CLAUDE.md with new structure
2. Add quality checklist
3. Document architecture decisions

### Week 2: Enforcement
1. Set up pre-commit hooks
2. Add CI/CD checks
3. Create issue templates

### Week 3: Polish
1. Add example workflows
2. Create troubleshooting guide
3. Document common patterns

## Success Metrics

- **Code Quality**: 0 critical issues in linting
- **Test Coverage**: > 85% coverage
- **Performance**: Meets all target benchmarks
- **Documentation**: All public APIs documented
- **Reliability**: < 1 bug per 1000 lines of code

## Benefits

### For Development
- Consistent, high-quality code
- Fewer bugs in production
- Easier maintenance
- Faster onboarding

### For Users
- Reliable library they can trust
- Clear, helpful error messages
- Good performance
- Comprehensive documentation

## Summary

This approach focuses on building a **robust, professional library** rather than complex AI features. The emphasis is on:

1. **Quality over quantity** - Better to have fewer, well-tested features
2. **Clarity over cleverness** - Simple, maintainable code
3. **User experience** - Making the library easy and safe to use
4. **Production readiness** - Code that's ready for real-world use

The updated CLAUDE.md will guide development toward building a circuit simulation library that professionals can confidently use in production environments.

---
*Focused on robust library development - Ready for review*