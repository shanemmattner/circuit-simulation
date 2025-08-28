---
name: quality-check
description: Run comprehensive quality checks including tests, coverage, linting, and type checking.
tools: [Bash, Read, Write]
---

# quality-check

Run comprehensive quality assurance checks for the project.

## Usage
```bash
# Run all quality checks
claude quality-check

# Run specific checks
claude quality-check --tests-only
claude quality-check --coverage-only
claude quality-check --lint-only
```

## Quality Checks Performed

### Testing
- Run full test suite with pytest
- Generate coverage reports
- Verify coverage meets threshold (85%+)
- Check test performance

### Code Quality
- Format code with black/prettier
- Lint code with ruff/eslint
- Type checking with mypy/tsc
- Security scanning with bandit

### Performance
- Run performance benchmarks
- Check for performance regressions
- Memory usage analysis

## Error Handling
```bash
set -e  # Exit on any error

echo "🔍 Running Quality Checks"
echo "========================="

# Check if in correct directory
if [[ ! -f "pyproject.toml" && ! -f "package.json" ]]; then
    echo "❌ Error: Must run from project root directory"
    exit 1
fi

# Run quality checks
echo "🧪 Running tests..."
pytest --cov=src --cov-report=term-missing || {
    echo "❌ Tests failed"
    exit 1
}

echo "🎨 Checking code formatting..."
black --check src/ tests/ || {
    echo "❌ Code formatting issues found"
    echo "💡 Run: black src/ tests/"
    exit 1
}

echo "🔍 Running linter..."
ruff check src/ tests/ || {
    echo "❌ Linting issues found"
    exit 1
}

echo "✅ All quality checks passed!"
```

Remember: Quality checks ensure code meets professional standards before deployment.