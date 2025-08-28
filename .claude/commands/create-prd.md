---
name: create-prd
description: Universal command for creating Product Requirements Documents. Ensures no code is written without approved PRD.
tools: [Read, Write, Edit, Grep, Glob, LS]
---

# create-prd

Create or refine Product Requirements Documents through interactive collaboration.

**CRITICAL**: No code implementation is allowed without an approved PRD. This enforces the PRD-driven development workflow.

## Usage
```bash
# Create new PRD
claude create-prd "new user authentication system"

# Refine existing PRD
claude create-prd --refine "user-authentication"

# List available PRDs
claude create-prd --list

# Validate PRD completeness
claude create-prd --validate "user-authentication"
```

## What It Does

### Interactive PRD Creation
- Guides you through structured requirements gathering
- Asks targeted questions to extract complete requirements
- Creates template-based PRD with all required sections
- Facilitates iterative refinement until PRD is complete
- Saves PRD in `memory-bank/prds/` directory

### PRD Refinement
- Load existing PRD for updates
- Show current PRD state with completion status
- Allow focused refinement of specific sections
- Maintain version history and change tracking

### PRD Validation
- Check completeness of all required sections
- Verify requirements are testable and actionable
- Ensure success criteria are measurable
- Validate scope and constraints are defined

## Interactive Questions

### Problem Statement
- What specific problem does this feature solve?
- Who experiences this problem?
- How do they currently handle this situation?
- What's the impact of not solving this problem?

### Goal Definition  
- What is the primary goal of this feature?
- What should users be able to do after implementation?
- How will this improve the current situation?

### Solution Approach
- What's your preferred approach to solving this?
- Are there specific technologies or patterns to use?
- Should this integrate with existing components?
- Any architectural considerations?

### Requirements Gathering
- Functional requirements (what the system does)
- Non-functional requirements (performance, security, usability)
- Edge cases and error conditions
- Integration requirements

### Success Criteria
- How will we know this feature is successful?
- What metrics will indicate success?
- What are the acceptance criteria?

### Scope and Constraints
- What IS included in this feature
- What is specifically NOT included
- Technical limitations and constraints
- Dependencies on other components

## PRD Structure Created

### Required Sections
```markdown
# PRD: [Feature Title]

**Created**: [Date]
**Status**: 🚧 DRAFT - Awaiting Approval

## Problem Statement
[Clear description of problem being solved]

## Goal
[Primary objective and desired outcome]

## Solution Approach
[High-level technical approach]

## Requirements

### Functional Requirements
[What the system should do]

### Non-Functional Requirements
[Performance, security, usability requirements]

## Success Metrics
[Measurable criteria for success]

## Scope

### In Scope
[Features included]

### Out of Scope
[Explicitly excluded features]

## Constraints
[Technical limitations and requirements]

## Approval Status
- [ ] **Problem Statement Approved**
- [ ] **Requirements Approved**  
- [ ] **Solution Approach Approved**
- [ ] **Ready for Implementation**

**⚠️ NO CODE IMPLEMENTATION WITHOUT APPROVAL ⚠️**
```

## Error Handling
```bash
# Ensure memory-bank directory exists
if [[ ! -d "memory-bank/prds" ]]; then
    mkdir -p memory-bank/prds
    echo "📁 Created memory-bank/prds directory"
fi

# Validate feature description provided
if [[ -z "$1" && -z "$refine" ]]; then
    echo "❌ Error: Feature description required"
    echo "Usage: claude create-prd 'feature description'"
    exit 1
fi
```

## PRD Status Management

### Status Levels
- **🚧 DRAFT**: Initial creation, not yet complete
- **📋 REVIEW**: Complete but awaiting user approval  
- **✅ APPROVED**: Ready for implementation
- **🚀 IN PROGRESS**: Currently being implemented
- **✅ COMPLETED**: Implementation finished

### List Command Output
```bash
📋 Available PRDs:
  ✅ user-authentication - Approved (2025-01-28 14:30)
  🚧 payment-integration - Draft (2025-01-28 15:15)
  📋 notification-system - Review (2025-01-27 16:45)
```

### Validation Output
```bash
# Complete PRD
✅ PRD 'user-authentication' is complete and ready for implementation

# Incomplete PRD  
❌ PRD 'payment-integration' is missing: Success Metrics, Scope, Constraints
```

## Integration with Development Process

### PRD-First Workflow
```bash
# 1. Always start with memory context
claude memory-context

# 2. Create PRD for new feature
claude create-prd "implement OAuth 2.0 login"

# 3. Review and approve PRD (manual step)
# Edit the generated PRD file to mark sections as approved

# 4. Only then proceed with implementation
claude develop-feature --prd="oauth-login"
```

### Quality Gates
- **Before Implementation**: PRD must be complete and approved
- **During Implementation**: Reference PRD for requirements clarification
- **After Implementation**: Update PRD status to completed

## File Management

### PRD File Naming
- Descriptive names: `user-authentication.md`
- Lowercase with hyphens: `payment-integration.md`
- Stored in: `memory-bank/prds/`

### Version Control
- All PRDs are version controlled with the project
- Changes tracked through git commits
- Amendment history maintained in PRD files
- Approval decisions recorded with timestamps

## Common PRD Templates

The command includes templates for different feature types:
- **Feature**: Standard new functionality
- **API**: API endpoints and service development
- **Bug Fix**: Problem resolution requirements
- **Refactor**: Code improvement without behavior change
- **Performance**: Optimization and scaling requirements

## Success Metrics

### Effective PRD Creation
- Complete PRDs with all required sections filled
- Clear, testable requirements that developers can implement
- User approval obtained before any code is written
- Successful implementation matching PRD requirements

### Quality Indicators
- No implementation questions about unclear requirements
- Test cases derive directly from PRD acceptance criteria
- Feature meets defined success criteria upon delivery
- User satisfaction with delivered functionality

## Best Practices

### Collaborative Approach
- Include relevant stakeholders in PRD creation
- Ask clarifying questions to extract complete requirements
- Validate understanding by summarizing back to user
- Iterate on PRD until user is satisfied with completeness

### Requirements Quality
- Make requirements specific and testable
- Include both positive and negative test cases
- Define error handling and edge case behavior
- Specify performance and scalability requirements

### Change Management
- Document any changes to requirements with rationale
- Maintain approval status through changes
- Communicate impact of changes to implementation timeline
- Archive superseded versions for historical reference

Remember: The PRD is the contract between user needs and developer implementation. Taking time to create comprehensive, clear PRDs prevents rework and ensures successful outcomes.