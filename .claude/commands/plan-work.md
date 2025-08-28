---
name: plan-work
description: Break down complex features into small, manageable, testable chunks using the work-planner agent.
tools: [Read, Write, Edit, Grep, Glob, LS]
---

# plan-work

Break down complex features into small, manageable, testable work segments.

## Usage
```bash
# Create work plan from approved PRD
claude plan-work --prd="user-authentication"

# Plan specific feature
claude plan-work "implement JWT token validation"

# Show existing work plans
claude plan-work --list
```

## What It Does
- Creates 15-30 minute work segments
- Identifies dependencies and sequencing
- Defines clear acceptance criteria for each segment
- Estimates effort and timeline
- Plans for TDD implementation approach

## Work Segmentation Strategy
- **Single Responsibility**: Each segment has one clear outcome
- **Testable**: Can verify segment completion
- **Independent**: Minimal dependencies on other work
- **Demonstrable**: Shows concrete progress
- **Reversible**: Can be backed out if needed

Remember: Good work planning makes complex development tractable through intelligent breakdown.