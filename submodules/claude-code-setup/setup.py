#!/usr/bin/env python3
"""
Universal Claude Code Setup Wizard
Creates customized Claude Code configuration for any repository.

Usage:
    python setup.py
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

class ClaudeSetupWizard:
    """Interactive wizard for setting up Claude Code configuration."""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.setup_root = Path(__file__).parent
        self.config = {}
        
    def run(self):
        """Run the complete setup wizard."""
        print("🤖 Universal Claude Code Setup Wizard")
        print("=" * 50)
        print("This wizard will create a customized Claude Code configuration for your project.")
        print()
        
        # Collect configuration
        self._collect_project_info()
        self._collect_development_preferences()
        self._collect_agent_preferences()
        
        # Generate configuration
        self._create_directory_structure()
        self._generate_claude_md()
        self._copy_agents()
        self._copy_commands()
        self._create_memory_bank()
        self._create_mcp_config()
        
        print("\n✅ Claude Code setup completed successfully!")
        print(f"📁 Configuration created in: {self.project_root / '.claude'}")
        print("\nNext steps:")
        print("1. Review generated CLAUDE.md configuration")
        print("2. Initialize memory-bank with your project context")
        print("3. Test with: claude --help")
        print("\n🚀 Ready for PRD-driven development!")
        
    def _collect_project_info(self):
        """Collect basic project information."""
        print("📋 Project Information")
        print("-" * 30)
        
        # Project name
        default_name = self.project_root.name
        self.config['project_name'] = self._ask(
            "Project name", 
            default=default_name
        )
        
        # Project type
        project_types = [
            "Python Library",
            "Web Application", 
            "API Service",
            "CLI Tool",
            "Research Project",
            "Other"
        ]
        
        self.config['project_type'] = self._ask_choice(
            "Project type",
            choices=project_types,
            default="Python Library"
        )
        
        # Primary language
        languages = ["Python", "JavaScript", "TypeScript", "Go", "Rust", "Java", "Other"]
        self.config['primary_language'] = self._ask_choice(
            "Primary programming language",
            choices=languages,
            default="Python"
        )
        
        # Target users
        user_types = [
            "Professional developers",
            "Students and learners",
            "Researchers",
            "End users",
            "Internal team"
        ]
        
        self.config['target_users'] = self._ask_choice(
            "Primary target users",
            choices=user_types,
            default="Professional developers"
        )
        
        print()
        
    def _collect_development_preferences(self):
        """Collect development workflow preferences."""
        print("⚙️ Development Preferences")
        print("-" * 30)
        
        # Test framework
        if self.config['primary_language'] == "Python":
            test_frameworks = ["pytest", "unittest", "nose2"]
            default_test = "pytest"
        elif self.config['primary_language'] in ["JavaScript", "TypeScript"]:
            test_frameworks = ["jest", "mocha", "vitest", "playwright"]
            default_test = "jest"
        else:
            test_frameworks = ["custom", "builtin", "other"]
            default_test = "custom"
            
        self.config['test_framework'] = self._ask_choice(
            "Test framework",
            choices=test_frameworks,
            default=default_test
        )
        
        # Code quality tools
        if self.config['primary_language'] == "Python":
            self.config['formatter'] = self._ask("Code formatter", default="black")
            self.config['linter'] = self._ask("Linter", default="ruff")
            self.config['type_checker'] = self._ask("Type checker", default="mypy")
        else:
            self.config['formatter'] = self._ask("Code formatter", default="prettier")
            self.config['linter'] = self._ask("Linter", default="eslint")
            self.config['type_checker'] = self._ask("Type checker", default="tsc")
        
        # Coverage target
        coverage_options = ["85%", "90%", "95%", "70%", "No specific target"]
        self.config['coverage_target'] = self._ask_choice(
            "Test coverage target",
            choices=coverage_options,
            default="85%"
        )
        
        print()
        
    def _collect_agent_preferences(self):
        """Collect preferences for agent configuration."""
        print("🤖 Agent Configuration")
        print("-" * 30)
        
        # Model preference
        models = [
            "claude-sonnet-4-20250514",
            "claude-opus-3-20240229", 
            "claude-haiku-3-20240307",
            "gpt-4",
            "other"
        ]
        
        self.config['default_model'] = self._ask_choice(
            "Default AI model",
            choices=models,
            default="claude-sonnet-4-20250514"
        )
        
        # Work style preference
        work_styles = [
            "Small focused chunks (15-minute segments)",
            "Medium tasks (30-60 minutes)",
            "Large features (complete implementation)",
            "Mixed approach"
        ]
        
        self.config['work_style'] = self._ask_choice(
            "Preferred work segmentation",
            choices=work_styles,
            default="Small focused chunks (15-minute segments)"
        )
        
        # Documentation level
        doc_levels = [
            "Minimal (inline comments only)",
            "Standard (docstrings + README)",
            "Comprehensive (full documentation)",
            "Professional (user guides + API docs)"
        ]
        
        self.config['documentation_level'] = self._ask_choice(
            "Documentation level",
            choices=doc_levels,
            default="Standard (docstrings + README)"
        )
        
        print()
    
    def _ask(self, question: str, default: str = None) -> str:
        """Ask a question with optional default."""
        prompt = f"{question}"
        if default:
            prompt += f" [{default}]"
        prompt += ": "
        
        response = input(prompt).strip()
        return response if response else (default or "")
    
    def _ask_choice(self, question: str, choices: List[str], default: str = None) -> str:
        """Ask user to choose from a list of options."""
        print(f"\n{question}:")
        for i, choice in enumerate(choices, 1):
            marker = "→" if choice == default else " "
            print(f"  {marker} {i}. {choice}")
        
        while True:
            try:
                prompt = "Choice"
                if default:
                    default_idx = choices.index(default) + 1
                    prompt += f" [{default_idx}]"
                prompt += ": "
                
                response = input(prompt).strip()
                if not response and default:
                    return default
                
                idx = int(response) - 1
                if 0 <= idx < len(choices):
                    return choices[idx]
                else:
                    print(f"Please enter a number between 1 and {len(choices)}")
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                sys.exit(0)
    
    def _create_directory_structure(self):
        """Create the .claude directory structure."""
        claude_dir = self.project_root / ".claude"
        claude_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (claude_dir / "agents").mkdir(exist_ok=True)
        (claude_dir / "commands").mkdir(exist_ok=True)
        (claude_dir / "templates").mkdir(exist_ok=True)
        
        print(f"📁 Created .claude directory structure")
    
    def _generate_claude_md(self):
        """Generate customized CLAUDE.md file."""
        template_path = self.setup_root / "templates" / "CLAUDE.md.template"
        if not template_path.exists():
            self._create_claude_template()
        
        with open(template_path, 'r') as f:
            template = f.read()
        
        # Replace template variables
        content = template.format(**self.config, 
                                  setup_date=datetime.now().strftime("%Y-%m-%d"))
        
        claude_md_path = self.project_root / "CLAUDE.md"
        with open(claude_md_path, 'w') as f:
            f.write(content)
        
        print(f"📝 Generated CLAUDE.md configuration")
    
    def _create_claude_template(self):
        """Create the CLAUDE.md template if it doesn't exist."""
        template_content = '''# {project_name} - Claude Code Configuration

## 🚨 SESSION START REQUIREMENT
**MANDATORY: Before any work, ALWAYS invoke the memory-bank-agent first to get project context and avoid token waste.**

## Project Overview
**Name**: {project_name}
**Type**: {project_type}
**Language**: {primary_language}
**Target Users**: {target_users}
**Setup Date**: {setup_date}

## PRD-Driven Development Workflow
**CRITICAL REQUIREMENT: PRD First! 🚨**
**BEFORE implementing ANY feature or major change:**
1. **Create a Product Requirements Document (PRD)** in `memory-bank/prds/`
2. **Get explicit user approval** before proceeding with implementation
3. **Reference the approved PRD** in all commits related to that feature

⚠️ **NO CODE WITHOUT PRD APPROVAL** ⚠️

## Development Standards

### Quality Assurance
```bash
# Code formatting
{formatter} .

# Linting
{linter} check .

# Type checking  
{type_checker} --strict

# Run all tests
{test_framework}

# Check coverage (target: {coverage_target})
{test_framework} --cov=src --cov-report=term-missing
```

### Work Style
- **Segmentation**: {work_style}
- **Documentation**: {documentation_level}
- **Default Model**: {default_model}

## Memory Bank System (Communication Between Sessions)
**Structure:**
```
memory-bank/
├── projectbrief.md       # Core requirements and goals
├── productContext.md     # Why project exists, problems solved
├── activeContext.md      # Current focus, recent changes
├── systemPatterns.md     # Architecture, design patterns
├── techContext.md        # Technologies, setup, constraints  
├── progress.md          # What works, what's left, known issues
└── prds/                # Product Requirements Documents
    └── *.md            # Feature-specific PRDs
```

**Workflow:**
- **Start of Session**: ALWAYS use memory-bank-agent first
- **During Work**: Update activeContext.md with decisions
- **After Features**: Update systemPatterns.md and progress.md
- **PRD Storage**: All PRDs in memory-bank/prds/ directory

## Development Workflow
1. User describes issue → memory-bank-agent reads context
2. Ask questions → Create PRD → User reviews → Iterate until complete
3. Smart work segmentation (small, testable, provable chunks)
4. prompt-optimizer crafts prompts for implementation agents
5. TDD implementation with continuous memory-bank updates
6. User manually tests before committing

## Agent Guidelines

### DO
- Follow Test-Driven Development (TDD)
- Ask for clarification when needed
- Check existing patterns before implementing
- Run quality checks before committing
- Keep functions small and focused
- Document design decisions
- Handle errors explicitly

### DON'T
- Skip tests
- Ignore linting errors
- Use print() for debugging (use logging)
- Make assumptions about requirements
- Create large, monolithic functions
- Leave TODO comments without tickets
- Commit broken code

## Memory Bank Management
- **Periodic Condensation**: Compress old memory-bank files to prevent drift
- **PRD Preservation**: Keep PRDs for key features permanently
- **Context Optimization**: <200 token agent handoffs using structured markdown
- **Token Efficiency**: <2000 tokens from memory-bank-agent vs 10,000+ from raw files

---
*Generated by Claude Code Setup Wizard on {setup_date}*
*Configuration optimized for {project_type} development*
'''
        
        template_dir = self.setup_root / "templates"
        template_dir.mkdir(exist_ok=True)
        
        template_path = template_dir / "CLAUDE.md.template"
        with open(template_path, 'w') as f:
            f.write(template_content)
    
    def _copy_agents(self):
        """Copy universal agents to project."""
        agents_source = self.setup_root / "agents"
        agents_dest = self.project_root / ".claude" / "agents"
        
        if agents_source.exists():
            for agent_file in agents_source.glob("*.py"):
                shutil.copy2(agent_file, agents_dest)
            print(f"🤖 Copied {len(list(agents_source.glob('*.py')))} agents")
        else:
            print("⚠️ Agents directory not found, will be created later")
    
    def _copy_commands(self):
        """Copy universal commands to project.""" 
        commands_source = self.setup_root / "commands"
        commands_dest = self.project_root / ".claude" / "commands"
        
        if commands_source.exists():
            for cmd_file in commands_source.glob("*.py"):
                shutil.copy2(cmd_file, commands_dest)
            print(f"⚙️ Copied {len(list(commands_source.glob('*.py')))} commands")
        else:
            print("⚠️ Commands directory not found, will be created later")
    
    def _create_memory_bank(self):
        """Create memory-bank directory structure."""
        memory_bank = self.project_root / "memory-bank"
        memory_bank.mkdir(exist_ok=True)
        
        # Create PRDs directory
        prds_dir = memory_bank / "prds"
        prds_dir.mkdir(exist_ok=True)
        
        # Import template functions
        templates_path = self.setup_root / "templates" / "memory_bank_templates.py"
        if templates_path.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location("memory_bank_templates", templates_path)
            templates_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(templates_module)
            
            # Create initial memory-bank files using templates
            files_to_create = [
                ("projectbrief.md", templates_module.get_project_brief_template(
                    self.config['project_name'], self.config['project_type'], self.config['target_users'])),
                ("productContext.md", templates_module.get_product_context_template(
                    self.config['project_name'], self.config['project_type'], self.config['target_users'])),
                ("activeContext.md", templates_module.get_active_context_template(
                    self.config['project_name'])),
                ("systemPatterns.md", templates_module.get_system_patterns_template(
                    self.config['project_name'], self.config['project_type'], 
                    self.config['primary_language'], self.config.get('test_framework', 'pytest'),
                    self.config.get('formatter', 'black'), self.config.get('linter', 'ruff'),
                    self.config.get('type_checker', 'mypy'))),
                ("techContext.md", templates_module.get_tech_context_template(
                    self.config['project_name'], self.config['primary_language'], self.config['project_type'])),
                ("progress.md", templates_module.get_progress_template(self.config['project_name']))
            ]
        else:
            # Fallback to inline templates
            files_to_create = [
                ("projectbrief.md", self._get_project_brief_template()),
                ("productContext.md", self._get_product_context_template()),
                ("activeContext.md", self._get_active_context_template()),
                ("systemPatterns.md", self._get_system_patterns_template()),
                ("techContext.md", self._get_tech_context_template()),
                ("progress.md", self._get_progress_template())
            ]
        
        for filename, content in files_to_create:
            file_path = memory_bank / filename
            if not file_path.exists():
                with open(file_path, 'w') as f:
                    f.write(content)
        
        # Create example PRD if templates are available
        if templates_path.exists():
            example_prd_path = prds_dir / "example-feature.md"
            if not example_prd_path.exists():
                with open(example_prd_path, 'w') as f:
                    f.write(templates_module.get_example_prd_template(self.config['project_name']))
        
        print(f"🧠 Created memory-bank structure with {len(files_to_create)} files")
    
    def _create_mcp_config(self):
        """Create MCP configuration if applicable."""
        mcp_config = {
            "version": "1.0",
            "project": self.config['project_name'],
            "language": self.config['primary_language'],
            "setup_date": datetime.now().isoformat()
        }
        
        mcp_path = self.project_root / ".mcp.json"
        with open(mcp_path, 'w') as f:
            json.dump(mcp_config, f, indent=2)
        
        print(f"🔗 Created MCP configuration")
    
    def _get_project_brief_template(self):
        return f'''# {self.config['project_name']} - Project Brief

## Mission Statement
*[Describe the core purpose of this project in 1-2 sentences]*

## Project Overview
- **Type**: {self.config['project_type']}
- **Language**: {self.config['primary_language']}
- **Target Users**: {self.config['target_users']}
- **Phase**: Initial Setup

## Success Metrics
*[Define what success looks like for this project]*

## Core Requirements
*[List the essential requirements that define this project]*

---
*Generated by Claude Code Setup - {datetime.now().strftime("%Y-%m-%d")}*
*Update this file as the project evolves*
'''
    
    def _get_product_context_template(self):
        return f'''# {self.config['project_name']} - Product Context

## Why This Project Exists
*[Explain the problem this project solves]*

## Target Audience
- **Primary**: {self.config['target_users']}
- **Use Cases**: *[Describe main use cases]*

## Value Proposition
*[What unique value does this project provide?]*

## Market/Domain Context
*[Relevant context about the domain or market]*

---
*Generated by Claude Code Setup - {datetime.now().strftime("%Y-%m-%d")}*
*This context helps AI agents understand the "why" behind decisions*
'''
    
    def _get_active_context_template(self):
        return f'''# {self.config['project_name']} - Active Context

## Current Focus
*[What are we working on right now?]*

## Recent Decisions
*[Important architectural or design decisions made in recent sessions]*

## Next Steps
*[What needs to happen next?]*

## Blockers/Questions
*[Any current blockers or open questions]*

## Session Notes
*[Update this during development sessions]*

---
*Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M")}*
*This file should be updated frequently during active development*
'''
    
    def _get_system_patterns_template(self):
        return f'''# {self.config['project_name']} - System Patterns

## Architecture Overview
*[High-level architecture description]*

## Design Patterns
*[Key design patterns used in the project]*

## Code Organization
*[How the code is structured and organized]*

## Testing Approach
- **Framework**: {self.config['test_framework']}
- **Coverage Target**: {self.config['coverage_target']}
- **Strategy**: *[Testing strategy and patterns]*

## Quality Standards
- **Formatter**: {self.config.get('formatter', 'TBD')}
- **Linter**: {self.config.get('linter', 'TBD')}
- **Type Checker**: {self.config.get('type_checker', 'TBD')}

## Development Patterns
*[Established patterns for how development happens in this project]*

---
*Generated by Claude Code Setup - {datetime.now().strftime("%Y-%m-%d")}*
*Document established patterns here for consistency*
'''
    
    def _get_tech_context_template(self):
        return f'''# {self.config['project_name']} - Technical Context

## Technology Stack
- **Primary Language**: {self.config['primary_language']}
- **Project Type**: {self.config['project_type']}

## Development Environment
*[Describe setup requirements, dependencies, etc.]*

## Build/Deploy Process
*[How to build and deploy this project]*

## Dependencies
*[Key dependencies and why they were chosen]*

## Infrastructure/Platform
*[Where this runs, what it depends on]*

## Constraints
*[Technical constraints, performance requirements, etc.]*

---
*Generated by Claude Code Setup - {datetime.now().strftime("%Y-%m-%d")}*
*This helps AI agents understand the technical environment*
'''
    
    def _get_progress_template(self):
        return f'''# {self.config['project_name']} - Progress Tracking

## What Works
*[Current working features/functionality]*

## What's Left
*[Major items still to be implemented]*

## Known Issues
*[Current bugs or limitations]*

## Recent Achievements
*[Recent milestones or completed features]*

## Performance Metrics
*[If applicable, track performance over time]*

## Quality Metrics
- **Test Coverage**: *[Current coverage]*
- **Linting Status**: *[Current status]*
- **Type Coverage**: *[If applicable]*

---
*Generated by Claude Code Setup - {datetime.now().strftime("%Y-%m-%d")}*
*Track progress to maintain momentum and identify bottlenecks*
'''

if __name__ == "__main__":
    wizard = ClaudeSetupWizard()
    try:
        wizard.run()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)