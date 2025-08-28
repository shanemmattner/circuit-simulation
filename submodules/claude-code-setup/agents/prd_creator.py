"""
PRD Creator Agent

Creates and refines Product Requirements Documents (PRDs) through user collaboration.
Critical component of PRD-driven development workflow.

Key responsibilities:
- Interactive PRD creation with user input
- Template-based PRD structure
- Iterative refinement process
- Integration with memory bank system
- Ensures no code is written without approved PRD
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

@dataclass
class PRDSection:
    """Represents a section of a PRD."""
    title: str
    content: str
    is_required: bool = True
    is_complete: bool = False

class PRDCreator:
    """Agent for creating and managing Product Requirements Documents."""
    
    def __init__(self, project_root: str = None):
        """Initialize PRD creator."""
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.prds_path = self.project_root / "memory-bank" / "prds"
        self.prds_path.mkdir(parents=True, exist_ok=True)
        
        self.prd_templates = self._load_prd_templates()
        self.current_prd = None
    
    def create_interactive_prd(self, feature_description: str) -> str:
        """
        Create PRD through interactive collaboration with user.
        
        Args:
            feature_description: Initial description of the feature
        
        Returns:
            Path to created PRD file
        """
        print("🚀 PRD Creator - Interactive Mode")
        print("=" * 50)
        print("Creating a Product Requirements Document through collaboration.")
        print("This ensures we build exactly what you need.\n")
        
        # Initialize PRD structure
        prd_name = self._generate_prd_name(feature_description)
        self.current_prd = self._initialize_prd_structure(prd_name, feature_description)
        
        # Interactive refinement process
        self._refine_problem_statement()
        self._refine_goal_statement()
        self._refine_solution_approach()
        self._refine_requirements()
        self._refine_success_criteria()
        self._refine_scope_and_constraints()
        
        # Generate final PRD
        prd_content = self._generate_prd_document()
        prd_file = self._save_prd(prd_name, prd_content)
        
        print(f"\n✅ PRD created: {prd_file}")
        print("\nNext steps:")
        print("1. Review the generated PRD")
        print("2. Make any final edits")
        print("3. Approve for implementation")
        print("\n🔒 No implementation will proceed without PRD approval!")
        
        return str(prd_file)
    
    def refine_existing_prd(self, prd_name: str) -> str:
        """
        Refine an existing PRD based on user feedback.
        
        Args:
            prd_name: Name of existing PRD to refine
        
        Returns:
            Path to updated PRD file
        """
        prd_file = self.prds_path / f"{prd_name}.md"
        if not prd_file.exists():
            raise FileNotFoundError(f"PRD not found: {prd_name}")
        
        # Load existing PRD
        with open(prd_file, 'r') as f:
            existing_content = f.read()
        
        self.current_prd = self._parse_existing_prd(existing_content, prd_name)
        
        print(f"🔄 Refining existing PRD: {prd_name}")
        print("=" * 50)
        
        # Show current state and get feedback
        self._show_current_prd_state()
        
        # Interactive refinement
        sections_to_refine = self._ask_which_sections_to_refine()
        for section in sections_to_refine:
            self._refine_section(section)
        
        # Generate updated PRD
        prd_content = self._generate_prd_document()
        updated_file = self._save_prd(prd_name, prd_content)
        
        print(f"\n✅ PRD updated: {updated_file}")
        return str(updated_file)
    
    def validate_prd_completeness(self, prd_name: str) -> Tuple[bool, List[str]]:
        """
        Validate that a PRD is complete and ready for implementation.
        
        Args:
            prd_name: Name of PRD to validate
        
        Returns:
            Tuple of (is_complete, missing_sections)
        """
        prd_file = self.prds_path / f"{prd_name}.md"
        if not prd_file.exists():
            return False, [f"PRD file not found: {prd_name}"]
        
        with open(prd_file, 'r') as f:
            content = f.read()
        
        required_sections = [
            "Goal", "Problem", "Solution", "Requirements", 
            "Success Metrics", "Scope", "Out of Scope"
        ]
        
        missing_sections = []
        for section in required_sections:
            if not self._section_exists_and_complete(content, section):
                missing_sections.append(section)
        
        return len(missing_sections) == 0, missing_sections
    
    def list_prds(self) -> List[Dict[str, str]]:
        """List all PRDs with their status."""
        prds = []
        for prd_file in self.prds_path.glob("*.md"):
            with open(prd_file, 'r') as f:
                content = f.read()
            
            # Extract basic info
            status = "Draft"
            if "✅ APPROVED FOR IMPLEMENTATION" in content:
                status = "Approved"
            elif "🚧 IN PROGRESS" in content:
                status = "In Progress"
            
            prds.append({
                "name": prd_file.stem,
                "file": str(prd_file),
                "status": status,
                "modified": datetime.fromtimestamp(prd_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            })
        
        return sorted(prds, key=lambda x: x["modified"], reverse=True)
    
    def _generate_prd_name(self, feature_description: str) -> str:
        """Generate a PRD name from feature description."""
        # Clean and normalize the description
        name = re.sub(r'[^a-zA-Z0-9\s]', '', feature_description.lower())
        name = re.sub(r'\s+', '-', name.strip())
        
        # Truncate if too long
        if len(name) > 50:
            name = name[:47] + "..."
        
        # Add timestamp if name already exists
        base_name = name
        counter = 1
        while (self.prds_path / f"{name}.md").exists():
            name = f"{base_name}-{counter}"
            counter += 1
        
        return name
    
    def _initialize_prd_structure(self, name: str, description: str) -> Dict[str, PRDSection]:
        """Initialize PRD structure with basic information."""
        return {
            "problem": PRDSection("Problem Statement", "", True, False),
            "goal": PRDSection("Goal", "", True, False),
            "solution": PRDSection("Solution Approach", "", True, False),
            "requirements": PRDSection("Requirements", "", True, False),
            "success_criteria": PRDSection("Success Metrics", "", True, False),
            "scope": PRDSection("Scope", "", True, False),
            "out_of_scope": PRDSection("Out of Scope", "", False, False),
            "constraints": PRDSection("Constraints", "", False, False),
            "risks": PRDSection("Risks & Mitigation", "", False, False)
        }
    
    def _refine_problem_statement(self):
        """Interactively refine the problem statement."""
        print("\n📋 PROBLEM STATEMENT")
        print("-" * 30)
        print("Let's clearly define the problem we're solving.")
        
        questions = [
            "What specific problem does this feature solve?",
            "Who experiences this problem?",
            "How do they currently handle this situation?",
            "What's the impact of not solving this problem?"
        ]
        
        responses = []
        for question in questions:
            response = input(f"\n{question}\n> ").strip()
            if response:
                responses.append(response)
        
        # Build problem statement
        problem_statement = self._synthesize_problem_statement(responses)
        self.current_prd["problem"].content = problem_statement
        self.current_prd["problem"].is_complete = True
        
        print(f"\n✅ Problem Statement: {problem_statement[:100]}...")
    
    def _refine_goal_statement(self):
        """Interactively refine the goal statement."""
        print("\n🎯 GOAL STATEMENT")
        print("-" * 30)
        print("Let's define what success looks like.")
        
        questions = [
            "What is the primary goal of this feature?",
            "What should users be able to do after implementation?",
            "How will this improve the current situation?"
        ]
        
        responses = []
        for question in questions:
            response = input(f"\n{question}\n> ").strip()
            if response:
                responses.append(response)
        
        goal_statement = self._synthesize_goal_statement(responses)
        self.current_prd["goal"].content = goal_statement
        self.current_prd["goal"].is_complete = True
        
        print(f"\n✅ Goal: {goal_statement[:100]}...")
    
    def _refine_solution_approach(self):
        """Interactively refine the solution approach."""
        print("\n💡 SOLUTION APPROACH")
        print("-" * 30)
        print("Let's outline how we'll solve this problem.")
        
        questions = [
            "What's your preferred approach to solving this?",
            "Are there any specific technologies or patterns to use?",
            "Should this integrate with existing components?",
            "Any architectural considerations?"
        ]
        
        responses = []
        for question in questions:
            response = input(f"\n{question}\n> ").strip()
            if response:
                responses.append(response)
        
        solution = self._synthesize_solution_approach(responses)
        self.current_prd["solution"].content = solution
        self.current_prd["solution"].is_complete = True
        
        print(f"\n✅ Solution approach defined.")
    
    def _refine_requirements(self):
        """Interactively refine functional requirements."""
        print("\n📝 REQUIREMENTS")
        print("-" * 30)
        print("Let's list the specific requirements.")
        print("Enter requirements one by one (empty line to finish):")
        
        requirements = []
        while True:
            req = input(f"\nRequirement #{len(requirements)+1}: ").strip()
            if not req:
                break
            requirements.append(req)
        
        # Categorize requirements
        functional_reqs = []
        non_functional_reqs = []
        
        for req in requirements:
            print(f"\nIs this a functional requirement (what the system does)?")
            print(f"Requirement: {req}")
            is_functional = input("Functional? (y/n): ").lower().startswith('y')
            
            if is_functional:
                functional_reqs.append(req)
            else:
                non_functional_reqs.append(req)
        
        requirements_content = self._format_requirements(functional_reqs, non_functional_reqs)
        self.current_prd["requirements"].content = requirements_content
        self.current_prd["requirements"].is_complete = True
        
        print(f"\n✅ {len(requirements)} requirements defined.")
    
    def _refine_success_criteria(self):
        """Interactively refine success criteria."""
        print("\n🎯 SUCCESS CRITERIA")
        print("-" * 30)
        print("How will we know this feature is successful?")
        print("Enter measurable success criteria (empty line to finish):")
        
        criteria = []
        while True:
            criterion = input(f"\nSuccess criterion #{len(criteria)+1}: ").strip()
            if not criterion:
                break
            criteria.append(criterion)
        
        success_content = self._format_success_criteria(criteria)
        self.current_prd["success_criteria"].content = success_content
        self.current_prd["success_criteria"].is_complete = True
        
        print(f"\n✅ {len(criteria)} success criteria defined.")
    
    def _refine_scope_and_constraints(self):
        """Interactively refine scope and constraints."""
        print("\n🔍 SCOPE & CONSTRAINTS")
        print("-" * 30)
        
        # In scope
        print("What IS included in this feature? (empty line to finish):")
        in_scope = []
        while True:
            item = input(f"\nIn scope #{len(in_scope)+1}: ").strip()
            if not item:
                break
            in_scope.append(item)
        
        # Out of scope
        print("\nWhat is specifically NOT included? (empty line to finish):")
        out_scope = []
        while True:
            item = input(f"\nOut of scope #{len(out_scope)+1}: ").strip()
            if not item:
                break
            out_scope.append(item)
        
        # Constraints
        print("\nAny constraints or limitations? (empty line to finish):")
        constraints = []
        while True:
            constraint = input(f"\nConstraint #{len(constraints)+1}: ").strip()
            if not constraint:
                break
            constraints.append(constraint)
        
        self.current_prd["scope"].content = self._format_list(in_scope)
        self.current_prd["scope"].is_complete = True
        
        self.current_prd["out_of_scope"].content = self._format_list(out_scope)
        self.current_prd["out_of_scope"].is_complete = len(out_scope) > 0
        
        self.current_prd["constraints"].content = self._format_list(constraints)
        self.current_prd["constraints"].is_complete = len(constraints) > 0
        
        print("\n✅ Scope and constraints defined.")
    
    def _generate_prd_document(self) -> str:
        """Generate the final PRD document."""
        template = """# PRD: {title}

**Created**: {date}
**Status**: 🚧 DRAFT - Awaiting Approval

## Problem Statement
{problem}

## Goal
{goal}

## Solution Approach
{solution}

## Requirements

### Functional Requirements
{functional_requirements}

### Non-Functional Requirements
{non_functional_requirements}

## Success Metrics
{success_criteria}

## Scope

### In Scope
{scope}

### Out of Scope
{out_of_scope}

## Constraints
{constraints}

## Implementation Approach
*To be determined during development*

## Test Strategy
*To be determined during development*

---

## Approval Status
- [ ] **Problem Statement Approved**
- [ ] **Requirements Approved**
- [ ] **Solution Approach Approved**
- [ ] **Ready for Implementation**

**⚠️ NO CODE IMPLEMENTATION WITHOUT APPROVAL ⚠️**

---
*Created by PRD Creator Agent - {date}*
"""
        
        # Parse requirements
        req_content = self.current_prd["requirements"].content
        func_reqs, non_func_reqs = self._parse_requirements_content(req_content)
        
        return template.format(
            title=getattr(self, 'prd_title', 'New Feature'),
            date=datetime.now().strftime("%Y-%m-%d %H:%M"),
            problem=self.current_prd["problem"].content,
            goal=self.current_prd["goal"].content,
            solution=self.current_prd["solution"].content,
            functional_requirements=func_reqs,
            non_functional_requirements=non_func_reqs,
            success_criteria=self.current_prd["success_criteria"].content,
            scope=self.current_prd["scope"].content,
            out_of_scope=self.current_prd["out_of_scope"].content,
            constraints=self.current_prd["constraints"].content
        )
    
    def _save_prd(self, name: str, content: str) -> Path:
        """Save PRD to file."""
        prd_file = self.prds_path / f"{name}.md"
        with open(prd_file, 'w') as f:
            f.write(content)
        return prd_file
    
    def _synthesize_problem_statement(self, responses: List[str]) -> str:
        """Synthesize problem statement from responses."""
        if not responses:
            return "Problem statement needs to be defined."
        
        return f"**Problem**: {responses[0]}\n\n" + \
               "\n".join(f"- {response}" for response in responses[1:])
    
    def _synthesize_goal_statement(self, responses: List[str]) -> str:
        """Synthesize goal statement from responses."""
        if not responses:
            return "Goal needs to be defined."
        
        return f"**Primary Goal**: {responses[0]}\n\n" + \
               "\n".join(f"- {response}" for response in responses[1:])
    
    def _synthesize_solution_approach(self, responses: List[str]) -> str:
        """Synthesize solution approach from responses."""
        if not responses:
            return "Solution approach needs to be defined."
        
        return "\n".join(f"- {response}" for response in responses)
    
    def _format_requirements(self, functional: List[str], non_functional: List[str]) -> str:
        """Format requirements into structured content."""
        content = ""
        if functional:
            content += "**Functional:**\n" + "\n".join(f"- {req}" for req in functional)
        if non_functional:
            content += "\n\n**Non-Functional:**\n" + "\n".join(f"- {req}" for req in non_functional)
        return content
    
    def _format_success_criteria(self, criteria: List[str]) -> str:
        """Format success criteria."""
        return "\n".join(f"- {criterion}" for criterion in criteria)
    
    def _format_list(self, items: List[str]) -> str:
        """Format list of items."""
        return "\n".join(f"- {item}" for item in items)
    
    def _parse_requirements_content(self, content: str) -> Tuple[str, str]:
        """Parse requirements content into functional and non-functional."""
        if "**Functional:**" in content:
            parts = content.split("**Non-Functional:**")
            func = parts[0].replace("**Functional:**", "").strip()
            non_func = parts[1].strip() if len(parts) > 1 else ""
        else:
            func = content
            non_func = ""
        
        return func, non_func
    
    def _section_exists_and_complete(self, content: str, section: str) -> bool:
        """Check if a section exists and has content."""
        section_pattern = f"## {section}"
        if section_pattern not in content:
            return False
        
        # Extract section content
        lines = content.split('\n')
        in_section = False
        section_content = []
        
        for line in lines:
            if line.startswith(f"## {section}"):
                in_section = True
                continue
            elif line.startswith("## ") and in_section:
                break
            elif in_section:
                section_content.append(line.strip())
        
        # Check if section has meaningful content
        meaningful_content = [line for line in section_content if line and not line.startswith('*')]
        return len(meaningful_content) > 0
    
    def _load_prd_templates(self) -> Dict[str, str]:
        """Load PRD templates for different feature types."""
        return {
            "feature": "Standard feature template",
            "api": "API-focused template",
            "bug_fix": "Bug fix template",
            "refactor": "Refactoring template"
        }
    
    def _show_current_prd_state(self):
        """Show current state of PRD being edited."""
        print("\nCurrent PRD state:")
        for key, section in self.current_prd.items():
            status = "✅" if section.is_complete else "⏳"
            print(f"  {status} {section.title}")
    
    def _ask_which_sections_to_refine(self) -> List[str]:
        """Ask user which sections to refine."""
        print("\nWhich sections would you like to refine?")
        sections = list(self.current_prd.keys())
        
        for i, key in enumerate(sections, 1):
            section = self.current_prd[key]
            status = "✅" if section.is_complete else "⏳"
            print(f"  {i}. {status} {section.title}")
        
        print("\nEnter section numbers to refine (comma-separated):")
        response = input("> ").strip()
        
        selected_indices = []
        for num in response.split(','):
            try:
                idx = int(num.strip()) - 1
                if 0 <= idx < len(sections):
                    selected_indices.append(sections[idx])
            except ValueError:
                pass
        
        return selected_indices
    
    def _refine_section(self, section_key: str):
        """Refine a specific section."""
        section = self.current_prd[section_key]
        print(f"\n🔄 Refining: {section.title}")
        print(f"Current content: {section.content[:200]}...")
        
        new_content = input("\nNew content (or press Enter to keep current): ").strip()
        if new_content:
            section.content = new_content
            section.is_complete = True
    
    def _parse_existing_prd(self, content: str, name: str) -> Dict[str, PRDSection]:
        """Parse existing PRD content into sections."""
        # This is a simplified parser - in practice, you'd want more robust parsing
        sections = self._initialize_prd_structure(name, "")
        
        # Extract sections from content
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            if line.startswith('## '):
                if current_section:
                    sections[current_section].content = '\n'.join(current_content).strip()
                    sections[current_section].is_complete = True
                
                section_title = line[3:].strip()
                current_section = self._map_title_to_key(section_title)
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # Handle last section
        if current_section and current_content:
            sections[current_section].content = '\n'.join(current_content).strip()
            sections[current_section].is_complete = True
        
        return sections
    
    def _map_title_to_key(self, title: str) -> Optional[str]:
        """Map section title to internal key."""
        mapping = {
            "Problem Statement": "problem",
            "Goal": "goal",
            "Solution Approach": "solution",
            "Requirements": "requirements",
            "Success Metrics": "success_criteria",
            "Scope": "scope",
            "Out of Scope": "out_of_scope",
            "Constraints": "constraints"
        }
        return mapping.get(title)


def main():
    """Command line interface for PRD creator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="PRD Creator Agent")
    parser.add_argument("action", choices=["create", "refine", "list", "validate"])
    parser.add_argument("--feature", help="Feature description for new PRD")
    parser.add_argument("--name", help="PRD name for refine/validate actions")
    parser.add_argument("--project-root", help="Project root directory", default=".")
    
    args = parser.parse_args()
    
    creator = PRDCreator(args.project_root)
    
    if args.action == "create":
        if not args.feature:
            args.feature = input("Enter feature description: ")
        prd_file = creator.create_interactive_prd(args.feature)
        print(f"PRD created: {prd_file}")
    
    elif args.action == "refine":
        if not args.name:
            args.name = input("Enter PRD name to refine: ")
        prd_file = creator.refine_existing_prd(args.name)
        print(f"PRD updated: {prd_file}")
    
    elif args.action == "list":
        prds = creator.list_prds()
        if prds:
            print("Available PRDs:")
            for prd in prds:
                print(f"  {prd['status']} {prd['name']} ({prd['modified']})")
        else:
            print("No PRDs found")
    
    elif args.action == "validate":
        if not args.name:
            args.name = input("Enter PRD name to validate: ")
        is_complete, missing = creator.validate_prd_completeness(args.name)
        if is_complete:
            print(f"✅ PRD '{args.name}' is complete and ready for implementation")
        else:
            print(f"❌ PRD '{args.name}' is missing: {', '.join(missing)}")


if __name__ == "__main__":
    main()