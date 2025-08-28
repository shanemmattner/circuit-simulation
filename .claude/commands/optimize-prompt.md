---
name: optimize-prompt
description: Craft optimal prompts for other agents to maximize development efficiency and outcomes.
tools: [Read, Write, Edit, Grep, Glob, LS]
---

# optimize-prompt

Craft optimal prompts for other agents to maximize development efficiency.

## Usage
```bash
# Optimize prompt for TDD implementation
claude optimize-prompt --for=tdd-implementer "implement user login validation"

# Optimize for work planning
claude optimize-prompt --for=work-planner --prd="user-auth" "break down OAuth integration"

# General prompt optimization
claude optimize-prompt "add error handling to payment processing"
```

## What It Does
- Analyzes tasks and crafts targeted prompts
- Optimizes for specific agent capabilities  
- Includes relevant context and constraints
- Structures requests for maximum clarity
- Ensures prompts lead to actionable outcomes

## Agent-Specific Optimization
- **TDD Implementer**: Structure for test-first development
- **Work Planner**: Emphasize segmentation and dependencies
- **Memory Bank**: Target specific context extraction

Remember: Well-crafted prompts are the foundation of efficient development workflows.