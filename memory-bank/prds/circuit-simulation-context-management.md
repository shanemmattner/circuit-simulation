# PRD: Circuit Simulation Context Management Improvements

## Goal
Improve Claude Code for **library development** (not usage) with focus on **clean context management** and **efficient agent handoffs**.

## Problem
Current agents have mixed purposes and context gets messy. Need clean separation between research → analysis → implementation.

## Solution: PRD-Driven Development with Memory-Bank Communication

### Core Workflow
```
1. User Request → memory-bank-agent reads project context
2. Claude asks questions → Creates PRD → User reviews
3. Iterate PRD until approved
4. Break work into 15-minute TDD segments
5. Implement with continuous memory-bank updates
6. User manually tests before committing
```

### Agent Pattern (PRD-Focused)
```
Phase 0: Memory Bank (ALWAYS FIRST - Communication System)
└── memory-bank-agent → Project context + session communication

Phase 1: PRD Development
└── prd-creator → Question asking, PRD creation, user collaboration

Phase 2: Work Planning  
└── work-planner → Break approved PRD into 15-minute segments

Phase 3: TDD Implementation
└── library-developer → Test-driven development + memory-bank updates
```

### Enhanced Agents (PRD-Driven)

**Memory Bank Agent** (MANDATORY - Session communication):
- **memory-bank-agent**: Project context + cross-session communication system

**Prompt Optimization Agent**:
- **prompt-optimizer**: Crafts optimal prompts for other agents to maximize results

**PRD Development Agent**:
- **prd-creator**: User collaboration, question asking, PRD creation with technical details

**Work Planning Agent**:
- **work-planner**: Smart segmentation into small, testable, provable chunks

**Implementation Agent** (Library Development Focus):
- **library-developer**: Professional TDD implementation + memory-bank updates
- Focus: Building the circuit simulation library (not using it for circuit analysis)
- Style: Small reliable changes, simple patterns, maintainable code

### Key Commands (PRD-Driven)

**`/develop-feature [feature_description]`**
```
1. memory-bank-agent: Read project context (<200 tokens)
2. prd-creator: Ask questions, create technical PRD, iterate with user
3. work-planner: Smart segmentation (small, testable, provable chunks)
4. prompt-optimizer: Craft optimal prompts for implementation
5. library-developer: Professional TDD implementation + memory-bank updates
6. User manually tests before committing
```

**`/debug-issue [issue_description]`**
```
1. memory-bank-agent: Read project context + issue history
2. prd-creator: Create debugging PRD with user collaboration
3. work-planner: Smart segmentation (debugging may need different chunk sizes)
4. prompt-optimizer: Optimize debugging prompts
5. library-developer: Professional fix with TDD + memory-bank updates
6. User manually tests before committing
```

### PRD-Driven Development Principles
- **Memory-bank first**: Always start with memory-bank-agent
- **PRD approval required**: Technical PRDs with implementation details
- **Smart segmentation**: Small, testable, provable chunks (context-aware sizing)
- **Prompt optimization**: Maximize agent performance through optimized prompts
- **Professional implementation**: Simple, reliable patterns over fancy techniques
- **Continuous updates**: Update memory-bank during implementation
- **User testing**: Manual testing before any commits
- **Library development focus**: Building the library, not using it

### Memory Bank Management
- **Periodic condensation**: Compress old files to prevent accuracy drift
- **PRD preservation**: Keep key feature PRDs permanently
- **Context optimization**: <200 token handoffs using structured markdown
- **Token efficiency**: Eliminate waste and irrelevant context for maximum LLM performance

### Current Issues to Fix
- Remove circuit analysis focus from agents
- Add library development patterns (FastAPI, Docker, pytest)
- Improve context efficiency for large codebase
- Clean handoffs between development phases

## Success Metrics
- Context efficiency: 50% reduction in irrelevant context
- Agent focus: Each agent has single, clear purpose  
- Development speed: Faster feature development through clean handoffs
- Quality: Maintain >85% test coverage with focused workflows

## Questions
1. Should research agents be completely read-only?
2. How much context should pass between phases?
3. Should we keep any existing agents or start fresh?

## Next Steps
1. Implement context-curator agent pattern
2. Test agent chain on one feature development
3. Optimize context handoff mechanisms