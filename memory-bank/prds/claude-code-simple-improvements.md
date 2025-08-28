# PRD: Simple Claude Code Improvements

**Date**: August 28, 2025  
**Status**: Draft - Awaiting Approval  
**Priority**: Medium  

## Current State
- 3 agents: test-engineer, circuit-analyzer, report-builder ✅
- 6 commands: test, check, ship, circuit, commit, regression_test ✅
- Basic settings.json with model configuration ✅

## Simple Improvements Needed

### 1. Add Basic Hooks (15 minutes)
Add simple quality checks that run automatically:
```json
{
  "model": "claude-sonnet-4-20250514",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{"type": "command", "command": "echo 'Editing file...'"}]
      }
    ]
  }
}
```

### 2. Add 2 More Useful Agents (30 minutes)
- **docs-writer**: Writes and updates documentation
- **bug-fixer**: Focuses on debugging and fixing issues

### 3. Add 3 More Commands (20 minutes)
- `/docs`: Generate/update documentation
- `/debug`: Debug specific issues
- `/quick-fix`: Fast bug fixes with tests

### 4. Add Basic MCP Config (10 minutes)
Create `.mcp.json`:
```json
{
  "servers": {
    "circuit-sim": {
      "command": "uv",
      "args": ["run", "python", "run_mcp_server.py"],
      "cwd": "."
    }
  }
}
```

## Total Time: ~75 minutes

## Benefits
- Automated basic quality checks
- Better task specialization with 5 agents total
- More workflow commands for common tasks
- Proper MCP integration

## Implementation
1. Update settings.json with hooks
2. Create 2 new agent files
3. Create 3 new command files  
4. Add .mcp.json file
5. Test everything works

---

**Decision**: Approve to proceed with simple improvements?