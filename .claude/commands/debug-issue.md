---
name: debug-issue
description: PRD-driven debugging workflow for library development issues. Creates debugging PRD, breaks into focused segments, and implements professional fixes with comprehensive testing. Always starts with memory-bank-agent for context.
---

# /debug-issue Command

Implements PRD-driven debugging workflow for library development issues in the circuit simulation library.

## Usage
```
/debug-issue [issue_description]
```

## Workflow Phases

### Phase 0: Memory Bank Context (MANDATORY)
**Agent**: `memory-bank-agent`
- Reads project context and issue history
- Provides focused context for bug type
- Retrieves related patterns and past solutions

### Phase 1: Debugging PRD Development
**Agent**: `prd-creator` (specialized for debugging)
- Collaborates with user to understand the issue
- Asks targeted questions for complete problem specification
- Creates debugging PRD with reproduction steps and fix strategy
- Iterates until user approves debugging approach

### Phase 2: Debug Work Planning
**Agent**: `work-planner` (adapted for debugging)
- Breaks debugging into focused investigation segments
- Plans reproduction, root cause analysis, and fix implementation
- May use different segment sizes based on debugging complexity
- Creates systematic approach to problem resolution

### Phase 3: Debug Prompt Optimization
**Agent**: `prompt-optimizer`
- Crafts optimal debugging prompts for library-developer
- Ensures systematic investigation approach
- Prepares focused instructions for fix implementation

### Phase 4: Professional Debug Implementation
**Agent**: `library-developer` (debugging mode)
- Systematically reproduces and investigates issue
- Implements comprehensive fix with tests
- Ensures no regressions and validates solution
- Updates memory-bank with debugging patterns

### Phase 5: User Validation
**Manual Step**: User testing before commit
- User validates fix resolves the issue
- Runs comprehensive tests to ensure no regressions
- Creates git commit when satisfied

## Example Usage

```bash
# Example 1: API Bug
/debug-issue "FastAPI circuit validation endpoint returns 500 for valid netlists"

# Example 2: Core Library Bug
/debug-issue "Circuit simulation hangs on large netlists with >1000 components"

# Example 3: Integration Bug
/debug-issue "Docker container fails to start on Apple Silicon Macs"

# Example 4: Performance Issue
/debug-issue "AC analysis takes >30 seconds for simple RC circuits"
```

## Command Implementation

The command orchestrates the debugging workflow:

```python
async def debug_issue(issue_description: str):
    print(f"🐛 Starting PRD-driven debugging: {issue_description}")
    
    # Phase 0: Memory Bank Context (MANDATORY - FAST APPROACH)
    print("\n📚 Phase 0: Loading debugging context...")
    context = await invoke_agent("memory-bank-agent", {
        "task": f"provide debugging context for issue: {issue_description}",
        "type": "debugging_context_request",
        "use_fast_consolidation": True,
        "focus_area": "debugging"
    })
    
    # Phase 1: Debugging PRD Development
    print("\n🔍 Phase 1: Creating debugging PRD...")
    debug_prd = await invoke_agent("prd-creator", {
        "issue_description": issue_description,
        "context": context,
        "mode": "debugging"
    })
    
    if not debug_prd["approved"]:
        print("❌ Debug PRD development incomplete. Please iterate with prd-creator.")
        return
    
    # Phase 2: Debug Work Planning
    print("\n🗓️ Phase 2: Planning debugging segments...")
    debug_plan = await invoke_agent("work-planner", {
        "debug_prd_path": debug_prd["prd_path"],
        "context": context,
        "mode": "debugging"
    })
    
    # Phase 3: Debug Prompt Optimization
    print("\n🎯 Phase 3: Optimizing debugging prompts...")
    debug_prompts = await invoke_agent("prompt-optimizer", {
        "debug_plan": debug_plan,
        "agent_target": "library-developer",
        "mode": "debugging"
    })
    
    # Phase 4: Professional Debug Implementation
    print("\n⚡ Phase 4: Systematic debugging and fix...")
    fix_result = await invoke_agent("library-developer", {
        "debug_plan": debug_plan,
        "debug_prompts": debug_prompts,
        "context": context,
        "mode": "debugging"
    })
    
    # Phase 5: User Validation Prompt
    print("\n✅ Phase 5: Ready for validation")
    print(f"""
Debug implementation complete! Please validate the fix:

1. **Verify the fix**:
   - Reproduce original issue to confirm it's resolved
   - Test the specific scenario that was failing
   - Run relevant test suite: `pytest tests/[relevant]/ -v`

2. **Regression testing**:
   - Run full test suite: `pytest --cov=src --cov-report=term-missing`
   - Test related functionality manually
   - Check edge cases and error conditions

3. **Code quality check**:
   - Type checking: `mypy src/ --strict`
   - Formatting: `black src/ tests/`
   - Linting: `ruff check src/ tests/ --fix`

4. **Performance validation** (if applicable):
   - Benchmark the fix if performance-related
   - Ensure no performance regressions

5. **Commit when satisfied**:
   - `git add .`
   - `git commit -m "fix: {issue_description}"`

Fix summary: {fix_result["summary"]}
Files modified: {fix_result["files_modified"]}
Root cause: {fix_result["root_cause"]}
""")

    # Update memory-bank with debugging completion
    await invoke_agent("memory-bank-agent", {
        "task": "record debugging completion",
        "type": "update_request",
        "data": {
            "issue": issue_description,
            "debug_prd_path": debug_prd["prd_path"],
            "root_cause": fix_result["root_cause"],
            "solution_patterns": fix_result["patterns"],
            "status": "ready_for_commit"
        }
    })
```

## Debugging PRD Template

The debugging PRD has specialized sections:

```markdown
# Debug PRD: [Issue Title]

## Problem Statement
[Clear description of the issue and its impact]

## Reproduction Steps
1. [Step 1 to reproduce the issue]
2. [Step 2]
3. [Expected vs. actual behavior]

## Environment Details
- OS: [Operating system and version]
- Python: [Python version]
- Dependencies: [Relevant package versions]
- Docker: [Container information if relevant]

## Investigation Strategy

### Hypothesis Generation
- [Possible cause 1 and how to test it]
- [Possible cause 2 and how to test it]
- [Possible cause 3 and how to test it]

### Debugging Approach
1. [Reproduction with logging/debugging]
2. [Systematic elimination of causes]
3. [Root cause identification]
4. [Fix implementation with tests]

## Success Criteria
- [ ] Issue is reproducibly fixed
- [ ] Root cause is identified and documented
- [ ] Fix includes comprehensive tests
- [ ] No regressions introduced
- [ ] Performance impact is acceptable

## Testing Strategy
- [Unit tests to prevent regression]
- [Integration tests if needed]
- [Performance tests if applicable]
- [Manual testing scenarios]

## Out of Scope
- [Related issues not addressed in this fix]
- [Future improvements not included]
```

## Debugging Work Segments

Debugging segments may vary in size based on complexity:

### Investigation Segments (10-20 minutes):
- Reproduce the issue with minimal test case
- Add logging and debugging information
- Eliminate one possible root cause
- Gather diagnostic information

### Implementation Segments (15-30 minutes):
- Implement fix for identified root cause
- Add tests to prevent regression
- Validate fix with original test case
- Check for edge cases

### Validation Segments (10-15 minutes):
- Run comprehensive test suite
- Check for performance regressions
- Validate error handling improvements
- Update documentation if needed

## Debugging-Specific Agent Behaviors

### prd-creator (Debugging Mode):
- Focus on reproduction steps and environment details
- Ask about error messages, logs, and symptoms
- Investigate similar past issues from memory-bank
- Create systematic investigation approach

### work-planner (Debugging Mode):
- May use adaptive segment sizing based on issue complexity
- Plan investigation before implementation
- Include validation and regression testing segments
- Account for multiple hypothesis testing

### library-developer (Debugging Mode):
- Systematic reproduction with detailed logging
- Hypothesis-driven investigation
- Comprehensive fix with regression tests
- Clear documentation of root cause

## Quality Gates

### After Debugging PRD:
- Issue is reproducible with clear steps
- Investigation strategy is systematic
- Success criteria include regression prevention
- Fix scope is clearly bounded

### After Debug Planning:
- Investigation segments are focused and testable
- Fix implementation has clear validation criteria
- Regression testing is comprehensive
- Documentation updates are planned

### After Fix Implementation:
- Original issue is verifiably resolved
- Root cause is identified and documented
- Comprehensive tests prevent regression
- No new issues are introduced

## Common Debugging Patterns

### Library Development Issues:
- **API Bugs**: FastAPI routing, validation, error handling
- **Core Logic Bugs**: Simulation engine, data processing, algorithms
- **Integration Bugs**: Docker, external dependencies, file I/O
- **Performance Issues**: Optimization, caching, resource usage
- **Testing Issues**: Flaky tests, missing coverage, fixture problems

### Investigation Techniques:
- **Reproduction**: Minimal failing test case
- **Logging**: Strategic debug output and tracing
- **Isolation**: Component-by-component testing
- **Comparison**: Working vs. failing scenarios
- **Profiling**: Performance and resource analysis

### Fix Validation:
- **Regression Tests**: Specific tests for the bug
- **Integration Tests**: End-to-end scenario testing
- **Performance Tests**: Benchmarks if applicable
- **Manual Testing**: User scenario validation
- **Documentation**: Update relevant documentation

## Error Recovery

### Investigation Dead Ends:
- Document eliminated hypotheses in memory-bank
- Pivot to alternative investigation approaches
- Consider seeking additional user input
- Review similar past issues for insights

### Complex Root Causes:
- Break complex fixes into smaller segments
- Implement incremental fixes with validation
- Consider temporary workarounds if needed
- Plan follow-up improvements if appropriate

### Regression Introduction:
- Immediately roll back problematic changes
- Analyze why regressions weren't caught
- Improve testing coverage for affected areas
- Implement additional validation steps

## Integration with Development Workflow

### Before using /debug-issue:
- Gather relevant error messages, logs, and symptoms
- Check git history for recent changes that might be related
- Review existing issues for similar problems

### After using /debug-issue:
- Validate the fix thoroughly in realistic scenarios
- Update documentation if the bug revealed gaps
- Consider adding monitoring or logging for early detection
- Share lessons learned with team

Remember: This command focuses on systematic, professional debugging of library development issues using PRD-driven workflow with comprehensive testing and validation.