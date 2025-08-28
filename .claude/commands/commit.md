---
name: commit
description: Streamlined commit workflow with quality checks and cleanup
tools: [Bash, Read, Write, Edit, Grep, Task]
model: claude-sonnet-4-20250514
---

# Commit Command

Streamlined commit workflow with quality checks and cleanup.

## Usage

```bash
/commit [message]
```

## What it does

1. **Clean and organize** - Move temp files, clean up repo
2. **Quality checks** - Format, lint, type check, test  
3. **Documentation** - Update README, CLAUDE.md if needed
4. **Memory Bank Update** - Record decisions and progress via memory-bank-agent
5. **Git workflow** - Stage changes, commit with proper message
6. **Validation** - Verify MCP server and core functionality

```bash
set -e  # Exit on any error

# Parse commit message
COMMIT_MSG="${ARGUMENTS:-}"
if [[ -z "$COMMIT_MSG" ]]; then
    echo "🤖 Auto-generating commit message..."
    # Generate from git diff or use default
    COMMIT_MSG="chore: update code with quality improvements"
fi

echo "📝 Preparing commit: $COMMIT_MSG"

# Run quality checks first
echo "🔍 Running quality checks..."
uv run black src/ tests/ examples/ || exit 1
uv run ruff check src/ tests/ examples/ --fix || exit 1  
uv run mypy src/ --strict || exit 1
uv run pytest --cov=src --cov-report=term-missing -x || exit 1

# Stage changes
echo "📦 Staging changes..."
git add -A

# Create commit with Claude Code attribution
git commit -m "$(cat <<EOF
$COMMIT_MSG

🤖 Generated with Claude Code (https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)" || {
    echo "❌ Commit failed"
    exit 1
}

echo "✅ Commit successful!"
git log --oneline -1
```

## Examples

```bash
# Auto-generate commit message
/commit

# Custom commit message  
/commit "feat: add new circuit analysis features"

# Quick commit with validation
/commit "fix: resolve simulation accuracy issues"
```

## Quality Gates

- ✅ Code formatting (black)
- ✅ Linting (ruff) 
- ✅ Type checking (mypy)
- ✅ Test suite passing
- ✅ MCP server functional
- ✅ Documentation updated

## Implementation Workflow

When executing `/commit`, follow these steps:

1. **Pre-commit Quality Checks** (run all bash commands)
2. **Memory Bank Recording** (use Task tool with memory-bank-agent)
3. **Git Commit** (stage and commit changes)
4. **Final Validation** (verify functionality)

### Memory Bank Integration

After quality checks pass but BEFORE committing:

```
Use Task tool to invoke memory-bank-agent with:
- Description: "Record commit progress and decisions"
- Prompt: "Record the following commit and any important decisions made:
  Commit: [COMMIT_MSG]
  Files changed: [list key files]
  Decisions made: [any architectural or implementation decisions]
  Progress updates: [features completed, milestones reached]"
- subagent_type: memory-bank-agent
```

## Notes

- Uses `uv run` for consistent macOS/Apple Silicon execution
- **MANDATORY**: Uses memory-bank-agent to record progress before committing
- Automatically moves validation scripts to proper directories
- Updates memory-bank context files via specialized agent
- Follows conventional commit message format
- Includes Claude Code attribution in commits