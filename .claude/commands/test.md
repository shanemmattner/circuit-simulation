---
name: test
description: Run comprehensive test suite with coverage analysis for circuit simulation library
tools: [Bash, Read, Write]
model: claude-sonnet-4-20250514
---

# test

Run the test suite with detailed coverage report for $ARGUMENTS.

If no arguments provided, run all tests. Otherwise, run specific test file or directory.

## Error Handling
```bash
set -e  # Exit on any error

# Check if in correct directory
if [[ ! -f "pyproject.toml" ]]; then
    echo "❌ Error: Must run from project root directory"
    exit 1
fi

# Use uv for consistency on macOS
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv not found. Install with: pip install uv"
    exit 1
fi

echo "🧪 Running test suite with coverage..."
uv run pytest $ARGUMENTS --cov=src --cov-report=term-missing --cov-report=html -v || {
    echo "❌ Tests failed. Check output above."
    exit 1
}

# Check coverage threshold
COVERAGE=$(uv run coverage report --format=total 2>/dev/null || echo "0")
if [[ $COVERAGE -lt 85 ]]; then
    echo "⚠️  Coverage is ${COVERAGE}% (target: 85%)"
    echo "📋 Review htmlcov/index.html for uncovered lines"
fi
```

## Output
- ✅ Coverage percentage and detailed report
- 📊 HTML report in `htmlcov/index.html`  
- 🎯 Suggestions if coverage below 85%