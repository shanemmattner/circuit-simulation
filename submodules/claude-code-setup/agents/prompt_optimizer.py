"""
Prompt Optimizer Agent

Crafts optimal prompts for other agents to maximize development efficiency.
Focuses on clear, context-rich prompts that lead to better outcomes.

Key responsibilities:
- Analyze tasks and craft targeted prompts
- Optimize for specific agent capabilities
- Include relevant context and constraints
- Structure requests for best results
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PromptContext:
    """Context information for prompt optimization."""
    task_type: str
    target_agent: str
    project_context: str
    constraints: List[str]
    success_criteria: List[str]
    examples: List[str] = None

class PromptOptimizer:
    """Agent for crafting optimal prompts for development tasks."""
    
    def __init__(self, project_root: str = None):
        """Initialize prompt optimizer."""
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.prompt_templates = self._load_prompt_templates()
        self.agent_capabilities = self._define_agent_capabilities()
    
    def optimize_prompt(self, 
                       task_description: str,
                       target_agent: str = "tdd-implementer",
                       context: Optional[PromptContext] = None) -> str:
        """
        Create an optimized prompt for a specific task and agent.
        
        Args:
            task_description: What needs to be done
            target_agent: Which agent will receive this prompt
            context: Additional context for optimization
        
        Returns:
            Optimized prompt string
        """
        if not context:
            context = self._analyze_task(task_description, target_agent)
        
        # Select appropriate template
        template = self._select_template(context.task_type, target_agent)
        
        # Build optimized prompt
        optimized = self._build_prompt(template, task_description, context)
        
        return optimized
    
    def optimize_for_tdd(self, feature_description: str, prd_context: str = None) -> str:
        """
        Create TDD-optimized prompt for feature implementation.
        
        Args:
            feature_description: What feature to implement
            prd_context: Relevant PRD content
        
        Returns:
            TDD-focused implementation prompt
        """
        context = PromptContext(
            task_type="tdd_implementation",
            target_agent="tdd-implementer",
            project_context=self._get_project_context(),
            constraints=self._get_tdd_constraints(),
            success_criteria=self._get_tdd_success_criteria(),
            examples=self._get_tdd_examples()
        )
        
        template = """# TDD Implementation Request

## Feature Description
{feature_description}

{prd_section}

## TDD Process Requirements
**CRITICAL**: Follow strict Test-Driven Development:
1. **Red**: Write failing test that describes the desired behavior
2. **Green**: Write minimal code to make the test pass
3. **Refactor**: Improve code while keeping tests green

## Project Context
{project_context}

## Implementation Constraints
{constraints}

## Success Criteria
{success_criteria}

## Expected Deliverables
1. Test file with comprehensive test cases
2. Implementation that passes all tests
3. Documentation of design decisions
4. Memory bank updates with patterns learned

## Test Strategy
- Write tests BEFORE implementation
- Test happy path AND edge cases
- Test error conditions explicitly
- Maintain existing test suite integrity

## Implementation Approach
- Start with the simplest possible solution
- Refactor only when tests are green
- Follow existing project patterns
- Update memory bank with decisions

{examples_section}

Please begin with writing the tests, then implement the feature following TDD principles.
"""
        
        # Format the template
        prd_section = f"## PRD Context\n{prd_context}\n" if prd_context else ""
        examples_section = self._format_examples(context.examples) if context.examples else ""
        
        return template.format(
            feature_description=feature_description,
            prd_section=prd_section,
            project_context=context.project_context,
            constraints=self._format_list(context.constraints),
            success_criteria=self._format_list(context.success_criteria),
            examples_section=examples_section
        )
    
    def optimize_for_planning(self, goal: str, complexity: str = "medium") -> str:
        """
        Create work-planning optimized prompt.
        
        Args:
            goal: High-level goal to plan for
            complexity: Expected complexity level
        
        Returns:
            Work planning focused prompt
        """
        template = """# Work Planning Request

## Goal
{goal}

## Planning Requirements
**CRITICAL**: Break work into small, manageable, testable chunks.

### Segmentation Principles
- Each chunk should be completable in 15-30 minutes
- Each chunk should have clear success criteria
- Each chunk should be independently testable
- Dependencies should be clearly identified

## Project Context
{project_context}

## Planning Constraints
- Work must follow established project patterns
- Each segment must have tests
- Progress must be demonstrable
- Memory bank must be updated

## Expected Output
1. **Work Breakdown**: List of specific, actionable tasks
2. **Dependencies**: Clear dependency mapping
3. **Success Criteria**: How to verify each chunk is complete
4. **Risk Assessment**: Potential blockers or challenges
5. **Time Estimates**: Realistic time estimates for each chunk

## Planning Quality Standards
- No task should take more than 45 minutes
- Each task should have clear acceptance criteria
- Dependencies should be minimal and well-defined
- Each task should advance the overall goal

Please create a detailed work plan that follows these principles.
"""
        
        return template.format(
            goal=goal,
            project_context=self._get_project_context()
        )
    
    def optimize_for_debugging(self, issue_description: str, error_info: str = None) -> str:
        """
        Create debugging-optimized prompt.
        
        Args:
            issue_description: Description of the problem
            error_info: Any error messages or stack traces
        
        Returns:
            Debugging focused prompt
        """
        template = """# Debugging Request

## Issue Description
{issue_description}

{error_section}

## Debugging Process
**SYSTEMATIC APPROACH REQUIRED**:
1. **Reproduce**: Ensure the issue can be consistently reproduced
2. **Isolate**: Identify the minimal case that triggers the issue
3. **Hypothesize**: Form hypotheses about root causes
4. **Test**: Test each hypothesis systematically
5. **Fix**: Implement minimal fix that addresses root cause
6. **Verify**: Ensure fix works and doesn't break other functionality

## Project Context
{project_context}

## Debugging Constraints
- Must maintain all existing functionality
- Fix should address root cause, not symptoms
- All existing tests must continue to pass
- New tests should prevent regression

## Expected Output
1. **Root Cause Analysis**: Clear explanation of what caused the issue
2. **Fix Implementation**: Minimal code changes to resolve the issue  
3. **Test Coverage**: New tests to prevent this issue from recurring
4. **Verification**: Confirmation that fix works and doesn't break anything

## Quality Standards
- Fix must be minimal and targeted
- Must include regression test
- Must not introduce new issues
- Must follow project coding standards

Please start by reproducing the issue and working through the systematic debugging process.
"""
        
        error_section = f"## Error Information\n```\n{error_info}\n```\n" if error_info else ""
        
        return template.format(
            issue_description=issue_description,
            error_section=error_section,
            project_context=self._get_project_context()
        )
    
    def _analyze_task(self, task_description: str, target_agent: str) -> PromptContext:
        """Analyze task to determine optimal prompt context."""
        # Determine task type based on keywords
        task_type = "general"
        if any(keyword in task_description.lower() for keyword in ["implement", "add", "create", "build"]):
            task_type = "implementation"
        elif any(keyword in task_description.lower() for keyword in ["test", "tdd", "coverage"]):
            task_type = "testing"
        elif any(keyword in task_description.lower() for keyword in ["fix", "bug", "error", "debug"]):
            task_type = "debugging"
        elif any(keyword in task_description.lower() for keyword in ["plan", "design", "architecture"]):
            task_type = "planning"
        
        return PromptContext(
            task_type=task_type,
            target_agent=target_agent,
            project_context=self._get_project_context(),
            constraints=self._get_general_constraints(),
            success_criteria=self._get_general_success_criteria()
        )
    
    def _select_template(self, task_type: str, target_agent: str) -> str:
        """Select appropriate prompt template."""
        key = f"{task_type}_{target_agent}"
        return self.prompt_templates.get(key, self.prompt_templates.get("general_default"))
    
    def _build_prompt(self, template: str, task_description: str, context: PromptContext) -> str:
        """Build the final optimized prompt."""
        return template.format(
            task_description=task_description,
            project_context=context.project_context,
            constraints=self._format_list(context.constraints),
            success_criteria=self._format_list(context.success_criteria),
            examples=self._format_examples(context.examples) if context.examples else ""
        )
    
    def _get_project_context(self) -> str:
        """Get condensed project context."""
        # Try to get context from memory bank agent if available
        try:
            memory_bank_path = self.project_root / "memory-bank"
            if memory_bank_path.exists():
                return f"Memory bank available at {memory_bank_path}. Use memory-bank-agent for detailed context."
            else:
                return f"Project root: {self.project_root}. No memory bank found - consider setting up memory bank system."
        except Exception:
            return f"Project root: {self.project_root}"
    
    def _get_tdd_constraints(self) -> List[str]:
        """Get TDD-specific constraints."""
        return [
            "Must write tests BEFORE implementation",
            "Tests must fail initially (Red phase)",
            "Implementation must be minimal to pass tests (Green phase)",
            "Refactoring only allowed when tests are green",
            "All existing tests must continue to pass",
            "Follow established project testing patterns",
            "Use appropriate test frameworks and fixtures"
        ]
    
    def _get_tdd_success_criteria(self) -> List[str]:
        """Get TDD success criteria."""
        return [
            "All new tests pass",
            "All existing tests still pass",
            "Code coverage maintained or improved",
            "Feature works as specified in tests",
            "Code follows project quality standards",
            "Memory bank updated with patterns learned"
        ]
    
    def _get_tdd_examples(self) -> List[str]:
        """Get TDD examples."""
        return [
            "Write test_feature_behavior() that describes expected behavior",
            "Run tests - confirm they fail (Red)",
            "Write minimal implementation to make tests pass (Green)",
            "Refactor implementation while keeping tests green",
            "Add edge case tests and ensure they pass"
        ]
    
    def _get_general_constraints(self) -> List[str]:
        """Get general development constraints."""
        return [
            "Follow established project patterns",
            "Maintain code quality standards",
            "Update relevant documentation",
            "Consider backwards compatibility",
            "Use appropriate error handling"
        ]
    
    def _get_general_success_criteria(self) -> List[str]:
        """Get general success criteria."""
        return [
            "Task completed as specified",
            "Code quality maintained",
            "No regressions introduced",
            "Appropriate tests included",
            "Documentation updated if needed"
        ]
    
    def _format_list(self, items: List[str]) -> str:
        """Format list of items for prompt inclusion."""
        return '\n'.join(f"- {item}" for item in items)
    
    def _format_examples(self, examples: List[str]) -> str:
        """Format examples for prompt inclusion."""
        if not examples:
            return ""
        
        formatted = "## Examples\n"
        for i, example in enumerate(examples, 1):
            formatted += f"{i}. {example}\n"
        return formatted
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """Load prompt templates for different scenarios."""
        return {
            "general_default": """# Development Task

## Task Description
{task_description}

## Project Context
{project_context}

## Constraints
{constraints}

## Success Criteria
{success_criteria}

{examples}

Please proceed with implementing this task following the project's established patterns and quality standards.
""",
            
            "implementation_tdd-implementer": """# TDD Implementation Task

## Feature to Implement
{task_description}

## TDD Process (MANDATORY)
1. **Red**: Write failing tests that describe desired behavior
2. **Green**: Write minimal code to make tests pass
3. **Refactor**: Improve code while keeping tests green

## Project Context
{project_context}

## Implementation Constraints
{constraints}

## Success Criteria
{success_criteria}

{examples}

**Start with writing the tests first, then implement the feature.**
""",
            
            "debugging_general": """# Debugging Task

## Issue to Resolve
{task_description}

## Systematic Debugging Process
1. Reproduce the issue consistently
2. Isolate the root cause
3. Implement minimal fix
4. Verify fix and test for regressions

## Project Context
{project_context}

## Debugging Constraints
{constraints}

## Success Criteria
{success_criteria}

{examples}

**Begin by reproducing the issue before implementing any fixes.**
"""
        }
    
    def _define_agent_capabilities(self) -> Dict[str, List[str]]:
        """Define capabilities of different agents for prompt optimization."""
        return {
            "tdd-implementer": [
                "Test-driven development",
                "Code implementation", 
                "Refactoring",
                "Testing patterns",
                "Quality assurance"
            ],
            "work-planner": [
                "Task breakdown",
                "Dependency analysis",
                "Time estimation",
                "Risk assessment",
                "Project planning"
            ],
            "prd-creator": [
                "Requirements gathering",
                "Problem definition",
                "Solution design",
                "User story creation",
                "Acceptance criteria"
            ],
            "memory-bank-agent": [
                "Context management",
                "Knowledge persistence", 
                "Pattern recognition",
                "Decision recording",
                "Cross-session continuity"
            ]
        }


def main():
    """Command line interface for prompt optimizer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Prompt Optimizer Agent")
    parser.add_argument("task", help="Task description to optimize prompt for")
    parser.add_argument("--agent", default="tdd-implementer", help="Target agent for the prompt")
    parser.add_argument("--type", choices=["tdd", "planning", "debugging", "general"], 
                       help="Optimization type")
    parser.add_argument("--project-root", help="Project root directory", default=".")
    
    args = parser.parse_args()
    
    optimizer = PromptOptimizer(args.project_root)
    
    if args.type == "tdd":
        optimized_prompt = optimizer.optimize_for_tdd(args.task)
    elif args.type == "planning":
        optimized_prompt = optimizer.optimize_for_planning(args.task)
    elif args.type == "debugging":
        optimized_prompt = optimizer.optimize_for_debugging(args.task)
    else:
        optimized_prompt = optimizer.optimize_prompt(args.task, args.agent)
    
    print(optimized_prompt)


if __name__ == "__main__":
    main()