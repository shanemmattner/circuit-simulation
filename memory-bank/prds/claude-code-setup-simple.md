# PRD: Universal Claude Code Setup Repository

## Goal
Create `circuit-synth/claude-code-setup` - a universal Claude Code system that can be copied to any repository and customized through simple configuration.

## Problem
Every repo needs custom Claude Code setup from scratch. Takes hours, gets inconsistent results.

## Solution
**Universal system + project customization**

### Repository Structure
```
claude-code-setup/
├── setup.py           # Interactive wizard (5-10 questions)
├── agents/            # Generic development agents + memory-bank-agent
├── commands/          # Configurable workflows  
├── templates/         # Generic template (includes memory-bank/ structure)
└── README.md          # Copy to any repo instructions
```

### Memory-Bank Integration (Critical)
- **Automatic Setup**: Creates `memory-bank/` structure for any project
- **Universal memory-bank-agent**: Works with any tech stack/project type
- **Context Efficiency**: <2000 tokens vs 10,000+ for raw project files
- **Session Requirement**: ALWAYS invoke memory-bank-agent first in every session

### Key Pattern: PRD-Driven Development Workflow
```
1. User describes issue/feature
2. memory-bank-agent reads project context
3. Claude asks clarifying questions
4. Claude creates PRD → User reviews → Iterate until complete
5. Claude breaks work into 15-minute segments
6. Claude implements with TDD, continuously updating memory-bank
7. User manually tests before committing
```

### Core Agents (Generic)
- **memory-bank-agent**: **CRITICAL** - Session communication system, project context
- **prompt-optimizer**: Crafts optimal prompts for other agents to maximize results
- **prd-creator**: Creates and refines PRDs through user collaboration
- **work-planner**: Smart segmentation (small, testable, provable chunks)
- **tdd-implementer**: Test-driven implementation with memory-bank updates

### Setup Experience
```bash
# Copy to any repository
git clone claude-code-setup .claude-system
.claude-system/setup.py
# Answer 5-10 questions
# ✅ Customized Claude Code ready
```

### Templates
- `generic` - Universal template that works for any project type

### CLAUDE.md Configuration (Auto-generated)
Each setup includes PRD-driven workflow instructions:
```markdown
## 🚨 SESSION START REQUIREMENT
**MANDATORY: Before any work, ALWAYS invoke the memory-bank-agent first.**

## PRD-Driven Development Workflow
**CRITICAL REQUIREMENT: PRD First! 🚨**
**BEFORE implementing ANY feature or major change:**
1. **Create a Product Requirements Document (PRD)** in `memory-bank/prds/`
2. **Get explicit user approval** before proceeding with implementation
3. **Reference the approved PRD** in all commits related to that feature

⚠️ **NO CODE WITHOUT PRD APPROVAL** ⚠️

## Memory Bank System (Communication Between Sessions)
- **Start of Session**: ALWAYS use memory-bank-agent first
- **During Work**: Update activeContext.md with decisions
- **After Features**: Update systemPatterns.md and progress.md
- **PRD Storage**: All PRDs in memory-bank/prds/ directory

## Development Workflow
1. User describes issue → memory-bank-agent reads context
2. Ask questions → Create PRD → User reviews → Iterate
3. Smart work segmentation (small, testable, provable chunks)
4. prompt-optimizer crafts prompts for implementation agents
5. TDD implementation with continuous memory-bank updates
6. User manually tests before committing

## Memory Bank Management
- **Periodic Condensation**: Compress old memory-bank files to prevent drift
- **PRD Preservation**: Keep PRDs for key features permanently
- **Context Optimization**: <200 token agent handoffs using structured markdown
```

## Success Metrics
- Setup time: <5 minutes
- Context efficiency: Clean handoffs between agents
- Universality: Works on Python, JS, Go, any language

## Questions
1. Should this be open source or circuit-synth internal?
2. How many setup questions? (5 simple vs 15 detailed)
3. Git submodule, npm package, or curl install?

## Next Steps
1. Create basic repository structure
2. Build interactive setup wizard
3. Test with circuit-simulation as first deployment