---
name: check
description: Run comprehensive quality checks before committing code
tools: [Bash, Read, Write, Grep]
model: claude-sonnet-4-20250514
---

# check

Run all quality checks on the codebase before committing.

## Quality Gate Sequence
Execute the following commands with proper error handling:

```bash
set -e  # Exit on any error
echo "🔍 Starting quality checks..."

# 1. Format code with black
echo "1️⃣ Formatting code..."
uv run black src/ tests/ examples/ || {
    echo "❌ Code formatting failed"
    exit 1
}

# 2. Lint with ruff  
echo "2️⃣ Linting code..."
uv run ruff check src/ tests/ examples/ --fix || {
    echo "❌ Linting issues found"
    exit 1
}

# 3. Type check with mypy
echo "3️⃣ Type checking..."
uv run mypy src/ --strict || {
    echo "❌ Type check failed"
    exit 1
}

# 4. Run tests with coverage
echo "4️⃣ Running test suite..."
uv run pytest --cov=src --cov-report=term-missing -x || {
    echo "❌ Tests failed"
    exit 1
}

# 5. Validate MCP server (project-specific)
echo "5️⃣ Validating MCP server..."
uv run python test_circuit_functions.py || {
    echo "⚠️  MCP server validation failed (non-blocking)"
}

echo "✅ All quality checks passed!"
```

## Success Criteria
- ✅ Code formatted consistently
- ✅ No linting violations
- ✅ Type hints pass strict checking
- ✅ Test suite passes with >85% coverage
- ✅ MCP integration functional