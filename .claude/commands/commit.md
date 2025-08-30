---
name: commit
description: Commit changes with quality checks
tools: [Bash]
model: claude-sonnet-4-20250514
---

# commit

Run quality checks and commit changes.

## Process
1. Run quality checks (format, lint, type check, test)
2. Show git status and diff
3. Create commit with proper message format

```bash
set -e

echo "🔍 Running quality checks..."

# Quality checks
uv run black src/ tests/ 
uv run ruff check src/ tests/ --fix
uv run mypy src/ --strict
uv run pytest --cov=src --cov-report=term-missing

echo "📋 Git status:"
git status

echo "📝 Changes to commit:"
git diff --staged --stat

echo "✅ Ready to commit!"
```

After quality checks pass, create commit with format:
```
<type>: <description>

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```