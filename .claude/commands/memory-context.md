---
name: memory-context
description: Provides project context through memory-bank-agent. This is the CRITICAL first step in any session.
tools: [Read, Write, Edit, Grep, Glob, LS]
---

# memory-context

Get project context from memory-bank for development session.

**CRITICAL**: This should be run FIRST in every development session to get focused project context and avoid token waste.

## Usage
```bash
claude memory-context [--focus=area]
```

**Arguments**:
- `--focus`: Optional focus area (api, testing, features, performance, deployment)

## What It Does

### Automatic Context Extraction
Uses the memory-bank-agent to provide condensed project context (~2000 tokens) instead of requiring you to read raw memory-bank files (~10,000+ tokens).

### Focus Areas Supported
- **api**: API development patterns, FastAPI standards, error handling
- **testing**: Testing requirements, TDD patterns, coverage standards
- **features**: Feature implementation patterns, user requirements
- **performance**: Optimization patterns, benchmarks, profiling
- **deployment**: Docker setup, production deployment, infrastructure

### Output Provides
- Project overview and mission
- Current development focus
- Established architectural patterns
- Recent progress and status
- PRD summaries for active development
- Relevant quality standards
- Next steps guidance

## Error Handling
```bash
# Check if memory-bank exists
if [[ ! -d "memory-bank" ]]; then
    echo "❌ No memory-bank directory found"
    echo "💡 Run: python .claude/setup.py to initialize memory-bank"
    exit 1
fi

# Invoke memory-bank-agent for context
echo "🧠 Getting project context from memory-bank..."
```

## Integration with Development Workflow

### Session Start Pattern
```bash
# Always start with memory context
claude memory-context --focus=api

# Then proceed with specific development commands
claude develop-feature "new user authentication"
claude plan-work "implement JWT token handling"
```

### Focus-Specific Workflows
```bash
# For API development
claude memory-context --focus=api

# For testing work
claude memory-context --focus=testing

# For performance optimization
claude memory-context --focus=performance
```

## Sample Output Format
```
# Memory Bank Context - 2025-01-28 15:30
**Token Efficiency**: This condensed context (~2000 tokens) replaces reading raw memory-bank files (~10,000+ tokens)
**Project Root**: /path/to/project

## Project Overview
**Mission**: Build production-ready circuit simulation library
**Purpose**: Enable professional engineers to simulate circuits reliably

## Active Context
### Current Focus
- Implementing FastAPI web service with WebSocket support
- Adding KiCad netlist import capability
- Performance optimization for large circuits

### Recent Decisions
- Adopted Docker containerization for ngspice dependencies
- Implemented MCP server with 8 specialized tools
- Established 85% test coverage requirement

## System Patterns
### Architecture
- Modular design with separate simulation engine
- PySpice integration for Python API
- Docker-based simulation backend

### Testing Approach
- Test-Driven Development (TDD) mandatory
- pytest framework with fixtures
- >85% coverage target

## Memory Bank Status
- Files Available: 6 of 6 core files
- PRDs Available: 3 PRDs in memory-bank/prds/
- Last Updated: Memory bank updated after FastAPI implementation

## Next Steps for AI Agent
1. Use this context to understand project state
2. Reference established patterns for consistency
3. Create/update PRD if implementing new feature
4. Follow TDD approach for implementation
5. Update memory-bank with new patterns and decisions
```

## Memory Bank File Sources
Extracts information from:
- **projectbrief.md**: Core requirements and mission
- **activeContext.md**: Current development focus
- **systemPatterns.md**: Established architecture patterns
- **progress.md**: Implementation status and achievements
- **memory-bank/prds/**: Product requirements documents
- **CLAUDE.md**: Quality standards and workflow requirements

## Benefits

### Token Efficiency
- **Memory Context**: ~2000 tokens of focused, relevant information  
- **Raw Files**: 10,000+ tokens with lots of irrelevant historical context
- **Savings**: 80% reduction in context tokens while improving relevance

### Development Efficiency
- Immediate understanding of project state
- Clear guidance on what to work on next
- Established patterns to follow for consistency
- Quality standards and requirements upfront

### Cross-Session Continuity
- Maintains context across different development sessions
- Records important decisions and their rationale
- Preserves architectural insights and lessons learned
- Enables effective collaboration with multiple agents

Remember: This command is the foundation of efficient development sessions. Always run it first to get the context you need for productive work.