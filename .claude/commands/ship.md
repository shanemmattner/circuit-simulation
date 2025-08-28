---
name: ship
description: Complete pre-PR workflow with quality gates and git status
tools: [Bash, Read, Write, Grep]
model: claude-sonnet-4-20250514
---

# ship

Prepare code for PR by running all quality checks and showing git status.

## Complete Pre-PR Workflow
```bash
set -e  # Exit on any error
echo "🚀 Preparing code for shipment..."

# 1. Clean workspace
echo "1️⃣ Cleaning workspace..."
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# 2. Format all Python code
echo "2️⃣ Formatting code..."
uv run black src/ tests/ examples/ || {
    echo "❌ Code formatting failed"
    exit 1
}

# 3. Lint and auto-fix
echo "3️⃣ Linting and fixing..."
uv run ruff check src/ tests/ examples/ --fix || {
    echo "❌ Linting failed"
    exit 1
}

# 4. Type checking
echo "4️⃣ Type checking..."
uv run mypy src/ --strict || {
    echo "❌ Type checking failed"
    exit 1
}

# 5. Run full test suite
echo "5️⃣ Running test suite..."
uv run pytest --cov=src --cov-report=term-missing -v || {
    echo "❌ Tests failed"
    exit 1
}

# 6. Project-specific validation
echo "6️⃣ Validating MCP server..."
uv run python test_circuit_functions.py || {
    echo "⚠️  MCP validation warning (non-blocking)"
}

# 7. Git status for review
echo "7️⃣ Git status review:"
git status --porcelain

if [[ -n $(git status --porcelain) ]]; then
    echo ""
    echo "📋 Files ready to commit:"
    git status --short
else
    echo "✅ Working directory clean"
fi

echo ""
echo "🎉 Code ready for PR!"
echo "Next steps:"
echo "  1. Review changes: git diff --staged"
echo "  2. Commit: git commit -m 'your message'"
echo "  3. Push: git push origin feature-branch"
```