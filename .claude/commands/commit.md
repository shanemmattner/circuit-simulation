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
4. **Git workflow** - Stage changes, commit with proper message
5. **Validation** - Verify MCP server and core functionality

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

## Notes

- Uses `uv run` for consistent macOS/Apple Silicon execution
- Automatically moves validation scripts to proper directories
- Updates memory-bank context files
- Follows conventional commit message format
- Includes Claude Code attribution in commits