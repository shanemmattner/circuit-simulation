# Streamlined Development Workflow Example

## Example: Adding a New Circuit Validation Feature

### Step 1: Document & Plan (PRD Creation)

**Command**: `/develop-feature "Add comprehensive circuit validation with detailed error reporting"`

**Manual PRD Process**:
1. **Document the feature clearly**:
   - What: Add validation that checks for floating nodes, short circuits, missing values
   - Why: Prevent simulation failures and provide helpful error messages
   - Success criteria: Validate 90% of common circuit errors before simulation

2. **Ask clarifying questions**:
   - Should validation be automatic or on-demand?
   - What error message format do users prefer?
   - Should validation integrate with the FastAPI endpoint?

3. **Get explicit user approval**: ✅ User approves the PRD

### Step 2: Break into Small Parts

**Manual Task Breakdown** (~15 minutes each):
1. Create basic validator class structure
2. Add floating node detection
3. Add short circuit detection  
4. Add missing component value detection
5. Create detailed error reporting format
6. Integrate with Circuit class
7. Add FastAPI endpoint integration
8. Create comprehensive test suite

### Step 3: Test-Driven Development

**For each small part (example: floating node detection)**:

1. **Write tests FIRST**:
```python
def test_floating_node_detection():
    # Test case: circuit with floating node
    circuit = Circuit("test")
    circuit.add_resistor("R1", "node1", "0", "1k")
    circuit.add_resistor("R2", "node2", "floating_node", "2k")  # floating!
    
    validator = CircuitValidator()
    result = validator.validate(circuit)
    
    assert not result.is_valid
    assert "floating_node" in result.errors[0].node_name
    assert "floating" in result.errors[0].message.lower()
```

2. **Write minimal implementation**:
```python
class CircuitValidator:
    def validate(self, circuit):
        errors = []
        nodes = self._collect_all_nodes(circuit)
        connections = self._collect_connections(circuit)
        
        for node in nodes:
            if connections[node] < 2 and node != "0":  # Ground is exception
                errors.append(ValidationError(
                    node_name=node,
                    message=f"Node '{node}' appears to be floating"
                ))
        
        return ValidationResult(errors=errors)
```

3. **Refactor if needed**: Clean up code while keeping tests green

### Step 4: User Validation

**Manual Testing**:
- Test with real circuit files
- Verify error messages are helpful
- Check API integration works
- Run quality checks:
  ```bash
  uv run pytest --cov=src --cov-report=term-missing
  uv run black src/ tests/
  uv run ruff check src/ tests/ --fix
  uv run mypy src/ --strict
  ```

**Update Memory-Bank**:
- Document validation patterns in `memory-bank/systemPatterns.md`
- Update progress in `memory-bank/progress.md`

**Commit**: Only when user is satisfied with results

## Key Benefits of This Approach

**Speed**: No waiting for slow agents - direct implementation
**Control**: User decides when to proceed at each step  
**Quality**: Same TDD standards, comprehensive testing
**Clarity**: Simple, understandable workflow

## Time Comparison

**Old Agent-Driven Approach**: 5+ minutes initialization + agent overhead
**New Streamlined Approach**: <10 seconds + direct implementation

**Result**: 4400x faster startup, same quality output