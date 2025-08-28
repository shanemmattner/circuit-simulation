---
name: implement-tdd
description: Implement features using strict Test-Driven Development practices. Integrates with PRD and memory-bank systems.
tools: [Read, Write, Edit, Grep, Glob, LS, Bash]
---

# implement-tdd

Implement features using strict Test-Driven Development methodology.

**CRITICAL**: Requires approved PRD before implementation. Follows Red-Green-Refactor cycle strictly.

## Usage
```bash
# Implement from approved PRD
claude implement-tdd --prd="user-authentication"

# Implement specific work task
claude implement-tdd --task="implement-jwt-validation" --prd="user-authentication"

# Continue existing implementation
claude implement-tdd --continue="feature-branch"
```

## TDD Process Enforced

### Phase 1: RED (Write Failing Test)
```bash
echo "🔴 RED: Writing failing test for [behavior]"

# 1. Extract behavior from PRD requirements
# 2. Write test that describes desired behavior  
# 3. Run test to verify it fails
# 4. Commit failing test before implementation
```

### Phase 2: GREEN (Make Test Pass)
```bash
echo "🟢 GREEN: Making test pass with minimal code"

# 1. Write simplest code to make test pass
# 2. Avoid over-engineering
# 3. Run all tests to ensure nothing breaks
# 4. Commit working implementation
```

### Phase 3: REFACTOR (Improve Design)
```bash
echo "🔵 REFACTOR: Improving code while keeping tests green"

# 1. Identify code smells and improvements
# 2. Refactor safely while maintaining behavior
# 3. Run all tests after each change
# 4. Commit improved code
```

## Error Handling
```bash
# Verify PRD exists and is approved
if [[ -n "$PRD_NAME" ]]; then
    if [[ ! -f "memory-bank/prds/${PRD_NAME}.md" ]]; then
        echo "❌ Error: PRD not found: $PRD_NAME"
        exit 1
    fi
    
    if ! grep -q "Ready for Implementation" "memory-bank/prds/${PRD_NAME}.md"; then
        echo "❌ Error: PRD not approved for implementation"
        echo "💡 Run: claude create-prd --validate $PRD_NAME"
        exit 1
    fi
fi

# Check test framework is available
if ! command -v pytest &> /dev/null; then
    echo "❌ Error: pytest not found"
    echo "💡 Install with: pip install pytest"
    exit 1
fi
```

## Implementation Pattern
```bash
#!/bin/bash

echo "🔴🟢🔵 Starting TDD Implementation"
echo "Feature: $FEATURE_DESCRIPTION"
echo "PRD: $PRD_NAME"
echo

# Get memory-bank context
echo "🧠 Getting implementation context..."
claude memory-context --focus=testing

# TDD Cycle Loop
for CYCLE in {1..10}; do
    echo
    echo "=== TDD Cycle $CYCLE ==="
    
    # RED: Write failing test
    echo "🔴 RED Phase: Writing failing test..."
    # Implementation will write test file
    
    # Verify test fails
    if ! pytest path/to/test_file.py::test_name -v; then
        echo "✅ Test fails as expected"
    else
        echo "❌ Test should fail but passed - check test logic"
        exit 1
    fi
    
    # GREEN: Make test pass
    echo "🟢 GREEN Phase: Making test pass..."
    # Implementation will write minimal code
    
    # Verify test passes
    if pytest path/to/test_file.py::test_name -v; then
        echo "✅ Test now passes"
    else
        echo "❌ Test still fails - need to fix implementation"
        exit 1
    fi
    
    # REFACTOR: Improve design
    echo "🔵 REFACTOR Phase: Improving code quality..."
    # Implementation may refactor while keeping tests green
    
    # Verify all tests still pass
    if pytest -v; then
        echo "✅ All tests pass after refactoring"
    else
        echo "❌ Refactoring broke tests - need to fix"
        exit 1
    fi
    
    # Check if feature is complete
    if [[ -f ".tdd_complete" ]]; then
        echo "🎉 Feature implementation complete!"
        rm .tdd_complete
        break
    fi
    
    echo "↻ Continuing to next TDD cycle..."
done

# Final validation
echo
echo "🎯 Final Validation"
echo "==================="

# Run full test suite
pytest --cov=src --cov-report=term-missing

# Check coverage threshold
COVERAGE=$(coverage report --format=total 2>/dev/null || echo "0")
if [[ $COVERAGE -lt 95 ]]; then
    echo "⚠️  Coverage is ${COVERAGE}% (target: 95%)"
    echo "📋 Add more tests to reach coverage target"
fi

# Update memory-bank with patterns learned
echo "📝 Recording implementation patterns in memory-bank..."
# Update activeContext.md with new patterns

echo "✅ TDD Implementation completed successfully"
```

## Quality Standards Enforced
- **Test Coverage**: >95% for new code
- **Test Independence**: Each test runs in isolation  
- **Descriptive Names**: Tests clearly describe behavior
- **Fast Execution**: Unit tests complete in <1 second
- **Error Testing**: All error conditions have tests

## Memory Bank Integration
Records successful patterns:
- Test structures that worked well
- Implementation approaches that emerged
- Refactoring insights and improvements  
- Integration points and dependencies
- Performance considerations

## Integration with Development Process
- Requires approved PRD before starting
- References PRD requirements for test cases
- Updates memory-bank with new patterns
- Integrates with existing CI/CD workflows
- Maintains traceability from tests to requirements

Remember: TDD is about design through testing. Let the tests guide your implementation toward better modularity and maintainability.