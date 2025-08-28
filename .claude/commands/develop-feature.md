---
name: develop-feature
description: PRD-driven feature development workflow. Creates technical PRD through user collaboration, breaks into testable segments, and implements using professional TDD. Always starts with memory-bank-agent for context.
---

# /develop-feature Command

Implements complete PRD-driven feature development workflow for the circuit simulation library.

## Usage
```
/develop-feature [feature_description]
```

## Workflow Phases

### Phase 0: Memory Bank Context (MANDATORY)
**Agent**: `memory-bank-agent`
- Reads project context and development patterns
- Provides focused context for feature type
- Ensures development aligns with library goals

### Phase 1: PRD Development
**Agent**: `prd-creator`
- Collaborates with user to understand requirements
- Asks targeted questions for complete specifications
- Creates technical PRD with implementation details
- Iterates until user approves PRD

### Phase 2: Work Planning
**Agent**: `work-planner`
- Breaks approved PRD into 15-minute TDD segments
- Ensures segments are small, testable, and provable
- Maps dependencies and integration points
- Creates detailed implementation roadmap

### Phase 3: Prompt Optimization
**Agent**: `prompt-optimizer`
- Crafts optimal prompts for implementation phase
- Ensures context efficiency and clarity
- Prepares focused instructions for library-developer

### Phase 4: TDD Implementation
**Agent**: `library-developer`
- Implements segments using professional TDD
- Tests first, minimal implementation, refactor
- Updates memory-bank with patterns established
- Maintains library development focus

### Phase 5: User Validation
**Manual Step**: User testing before commit
- User validates implementation meets requirements
- Runs quality checks: tests, linting, type checking
- Creates git commit when satisfied

## Example Usage

```bash
# Example 1: API Feature
/develop-feature "Add circuit validation endpoint to FastAPI service"

# Example 2: Core Library Feature  
/develop-feature "Implement AC frequency analysis for circuits"

# Example 3: Developer Experience Feature
/develop-feature "Add progress bars to CLI simulation commands"
```

## Command Implementation

The command orchestrates the agent workflow:

```python
async def develop_feature(feature_description: str):
    print(f"🚀 Starting PRD-driven development: {feature_description}")
    
    # Phase 0: Memory Bank Context (MANDATORY)
    print("\n📚 Phase 0: Loading project context...")
    context = await invoke_agent("memory-bank-agent", {
        "task": f"provide context for feature development: {feature_description}",
        "type": "context_request"
    })
    
    # Phase 1: PRD Development
    print("\n📋 Phase 1: Creating technical PRD...")
    prd_result = await invoke_agent("prd-creator", {
        "feature_request": feature_description,
        "context": context
    })
    
    if not prd_result["approved"]:
        print("❌ PRD development incomplete. Please iterate with prd-creator.")
        return
    
    # Phase 2: Work Planning
    print("\n🗓️ Phase 2: Breaking into development segments...")
    work_plan = await invoke_agent("work-planner", {
        "prd_path": prd_result["prd_path"],
        "context": context
    })
    
    # Phase 3: Prompt Optimization
    print("\n🎯 Phase 3: Optimizing implementation prompts...")
    optimized_prompts = await invoke_agent("prompt-optimizer", {
        "work_plan": work_plan,
        "agent_target": "library-developer"
    })
    
    # Phase 4: TDD Implementation
    print("\n⚡ Phase 4: Professional TDD implementation...")
    implementation_result = await invoke_agent("library-developer", {
        "work_plan": work_plan,
        "optimized_prompts": optimized_prompts,
        "context": context
    })
    
    # Phase 5: User Validation Prompt
    print("\n✅ Phase 5: Ready for user validation")
    print(f"""
Implementation complete! Please validate:

1. **Test the implementation**:
   - Run specific tests: `pytest tests/test_[relevant]/ -v`
   - Run full test suite: `pytest --cov=src --cov-report=term-missing`

2. **Check code quality**:
   - Type checking: `mypy src/ --strict`
   - Formatting: `black src/ tests/`
   - Linting: `ruff check src/ tests/ --fix`

3. **Manual testing**:
   - Try the new feature in relevant scenarios
   - Verify it integrates properly with existing code
   - Test error conditions and edge cases

4. **Commit when satisfied**:
   - `git add .`
   - `git commit -m "feat: {feature_description}"`

Implementation summary: {implementation_result["summary"]}
Files modified: {implementation_result["files_modified"]}
""")

    # Update memory-bank with completion
    await invoke_agent("memory-bank-agent", {
        "task": "record feature development completion",
        "type": "update_request", 
        "data": {
            "feature": feature_description,
            "prd_path": prd_result["prd_path"],
            "patterns_established": implementation_result["patterns"],
            "status": "ready_for_commit"
        }
    })
```

## Success Criteria

The command succeeds when:
- [ ] PRD is approved by user with complete technical details
- [ ] Work plan breaks feature into manageable segments
- [ ] Implementation follows professional TDD practices
- [ ] All tests pass with >85% coverage maintained
- [ ] Code follows library quality standards
- [ ] Memory-bank is updated with patterns and progress
- [ ] User can manually validate and commit changes

## Quality Gates

### After PRD Phase:
- Technical requirements are specific and testable
- Implementation approach is clearly defined
- Integration points with existing code are identified
- Success criteria are measurable

### After Work Planning:
- Segments are appropriately sized (15 minutes each)
- Dependencies are clearly mapped
- Testing strategy is comprehensive
- Integration points are well-defined

### After Implementation:
- All segment tests pass
- No regressions in existing functionality
- Code quality standards are maintained
- Library development focus is preserved (not circuit analysis)

## Agent Coordination

### memory-bank-agent → prd-creator:
- Project context and quality standards
- Current development priorities
- Architectural constraints that apply

### prd-creator → work-planner:
- Approved PRD with technical details
- Implementation requirements and constraints
- Integration points identified

### work-planner → prompt-optimizer:
- Detailed work plan with segments
- Implementation requirements
- Testing and validation needs

### prompt-optimizer → library-developer:
- Optimized prompts for each development segment
- Clear implementation guidelines
- Context-efficient instructions

### library-developer → memory-bank-agent:
- Patterns established during implementation
- Integration decisions made
- Progress updates and completion status

## Error Handling

### PRD Not Approved:
- Return control to user for PRD iteration
- Don't proceed to implementation without approval
- Maintain PRD in draft state for future reference

### Implementation Failures:
- Record partial progress in memory-bank
- Provide clear error context to user
- Allow resumption from failed segment

### Quality Gate Failures:
- Stop implementation and report specific failures
- Provide remediation guidance
- Allow manual fixes before continuing

## Library Development Focus

This command is specifically designed for:
- **Python API development** (circuit_sim library)
- **FastAPI web service** enhancements
- **Testing infrastructure** and patterns
- **Docker deployment** improvements
- **CLI interface** enhancements
- **Performance optimization** of library functions
- **MCP server** functionality for AI integration

This command does NOT handle:
- Circuit analysis or design tasks
- Electrical engineering calculations
- Circuit-specific tutorials or documentation
- SPICE model creation

## Integration with Development Workflow

### Before using /develop-feature:
- Ensure development environment is ready
- Check that current git state is clean
- Review existing issues or PRDs for context

### After using /develop-feature:
- Manual validation and testing by user
- Quality checks (tests, linting, type checking)
- Git commit when satisfied with results
- Consider updating documentation if needed

### Follow-up Actions:
- Update project roadmap with completed feature
- Consider creating examples or tutorials if appropriate
- Plan integration testing with other components
- Update deployment if API changes were made

Remember: This command focuses on professional library development using PRD-driven workflow with optimal context management and TDD practices.