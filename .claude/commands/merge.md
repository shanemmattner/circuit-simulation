---
name: merge
description: Merge current branch to main
tools: [Bash]
model: claude-sonnet-4-20250514
---

# merge

Merge current branch to main with quality checks.

## Process
1. Run final quality checks
2. Show branch status
3. Switch to main, merge, push

```bash
set -e

current_branch=$(git branch --show-current)
echo "🔄 Merging branch '$current_branch' to main..."

# Final quality checks
echo "🔍 Running final quality checks..."
uv run black src/ tests/
uv run ruff check src/ tests/ --fix  
uv run mypy src/ --strict
uv run pytest --cov=src --cov-report=term-missing

# Show branch status
echo "📋 Branch status:"
git log main..$current_branch --oneline

# Merge process
echo "🔀 Merging to main..."
git checkout main
git pull origin main
git merge $current_branch --no-ff
git push origin main

echo "✅ Successfully merged '$current_branch' to main!"
echo "🧹 Clean up: git branch -d $current_branch"
```