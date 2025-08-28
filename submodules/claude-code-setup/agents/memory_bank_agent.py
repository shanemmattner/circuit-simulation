"""
Universal Memory Bank Agent

This agent is CRITICAL for token efficiency and context management.
ALWAYS invoke this agent FIRST in every session before any other work.

Provides condensed project context (<2000 tokens) instead of reading 
raw memory-bank files directly (10,000+ tokens).

Works with any project type and tech stack.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class MemoryBankAgent:
    """Universal memory bank agent for any project type."""
    
    def __init__(self, project_root: str = None):
        """Initialize agent with project root directory."""
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.memory_bank_path = self.project_root / "memory-bank"
        self.context = {}
        
    def get_session_context(self, focus_area: str = None) -> str:
        """
        Get condensed project context for a new session.
        
        Args:
            focus_area: Optional area of focus (e.g., "api", "testing", "features")
        
        Returns:
            Condensed context string optimized for AI consumption
        """
        if not self.memory_bank_path.exists():
            return self._no_memory_bank_response()
        
        # Read all memory bank files
        self._read_memory_bank_files()
        
        # Generate condensed context
        context_sections = []
        
        # Project overview (always included)
        context_sections.append(self._get_project_overview())
        
        # Current focus and active context
        context_sections.append(self._get_active_context())
        
        # Architecture and patterns (relevant to most work)
        context_sections.append(self._get_system_patterns())
        
        # Recent progress and status
        context_sections.append(self._get_progress_summary())
        
        # Focus-specific context if requested
        if focus_area:
            focus_context = self._get_focus_specific_context(focus_area)
            if focus_context:
                context_sections.append(focus_context)
        
        # PRD summary (critical for development decisions)
        context_sections.append(self._get_prd_summary())
        
        # Combine all sections
        full_context = "\n\n".join(filter(None, context_sections))
        
        return self._format_session_context(full_context)
    
    def update_active_context(self, update_type: str, content: str) -> bool:
        """
        Update active context with new information.
        
        Args:
            update_type: Type of update ("decision", "progress", "blocker", "completion")
            content: Content to add
        
        Returns:
            True if update was successful
        """
        active_context_path = self.memory_bank_path / "activeContext.md"
        
        if not active_context_path.exists():
            return False
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        update_entry = f"\n## {update_type.title()} - {timestamp}\n{content}\n"
        
        try:
            with open(active_context_path, 'a') as f:
                f.write(update_entry)
            return True
        except Exception as e:
            print(f"Failed to update active context: {e}")
            return False
    
    def record_prd_decision(self, prd_name: str, decision: str, rationale: str) -> bool:
        """
        Record a PRD-related decision in the memory bank.
        
        Args:
            prd_name: Name of the PRD
            decision: The decision made
            rationale: Why this decision was made
        
        Returns:
            True if recorded successfully
        """
        decision_content = f"""
### PRD Decision: {prd_name}
**Decision**: {decision}
**Rationale**: {rationale}
**Context**: This decision impacts the implementation approach and should be considered in future related work.
"""
        
        return self.update_active_context("PRD Decision", decision_content)
    
    def get_prd_list(self) -> List[str]:
        """Get list of available PRDs."""
        prds_path = self.memory_bank_path / "prds"
        if not prds_path.exists():
            return []
        
        return [prd.stem for prd in prds_path.glob("*.md")]
    
    def get_prd_summary(self, prd_name: str) -> Optional[str]:
        """Get summary of a specific PRD."""
        prd_path = self.memory_bank_path / "prds" / f"{prd_name}.md"
        if not prd_path.exists():
            return None
        
        try:
            with open(prd_path, 'r') as f:
                content = f.read()
            
            # Extract key sections (goal, solution, requirements)
            lines = content.split('\n')
            summary_lines = []
            current_section = None
            
            for line in lines[:50]:  # Limit to first 50 lines for summary
                if line.startswith('## Goal') or line.startswith('## Problem') or line.startswith('## Solution'):
                    current_section = line
                    summary_lines.append(line)
                elif current_section and line.strip() and not line.startswith('#'):
                    summary_lines.append(line)
                elif line.startswith('##'):
                    current_section = None
            
            return '\n'.join(summary_lines[:20])  # Keep it concise
        except Exception:
            return None
    
    def _read_memory_bank_files(self):
        """Read all memory bank files into context."""
        files_to_read = [
            "projectbrief.md",
            "productContext.md", 
            "activeContext.md",
            "systemPatterns.md",
            "techContext.md",
            "progress.md"
        ]
        
        for filename in files_to_read:
            file_path = self.memory_bank_path / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        self.context[filename] = f.read()
                except Exception as e:
                    self.context[filename] = f"Error reading {filename}: {e}"
            else:
                self.context[filename] = None
    
    def _get_project_overview(self) -> str:
        """Extract project overview from memory bank."""
        sections = []
        
        # Project brief
        if self.context.get("projectbrief.md"):
            brief_lines = self.context["projectbrief.md"].split('\n')
            mission = next((line for line in brief_lines if '**Mission' in line or 'Mission Statement' in line), '')
            if mission:
                sections.append(f"**Mission**: {mission.split(':', 1)[-1].strip()}")
        
        # Product context
        if self.context.get("productContext.md"):
            context_lines = self.context["productContext.md"].split('\n')
            why_exists = next((line for line in context_lines if 'Why This Project Exists' in line), '')
            if why_exists:
                # Get next non-empty line after "Why This Project Exists"
                idx = context_lines.index(why_exists)
                for i in range(idx + 1, min(idx + 5, len(context_lines))):
                    line = context_lines[i].strip()
                    if line and not line.startswith('#') and not line.startswith('*'):
                        sections.append(f"**Purpose**: {line}")
                        break
        
        return "## Project Overview\n" + '\n'.join(sections) if sections else ""
    
    def _get_active_context(self) -> str:
        """Extract current active context."""
        if not self.context.get("activeContext.md"):
            return ""
        
        lines = self.context["activeContext.md"].split('\n')
        active_sections = []
        
        # Look for current focus, recent decisions, next steps
        current_section = None
        for line in lines:
            if any(keyword in line.lower() for keyword in ['current focus', 'recent decisions', 'next steps']):
                current_section = line
                active_sections.append(line)
            elif current_section and line.strip() and not line.startswith('##'):
                active_sections.append(line)
                if len(active_sections) > 10:  # Keep it concise
                    break
            elif line.startswith('##'):
                current_section = None
        
        return "## Active Context\n" + '\n'.join(active_sections[:10]) if active_sections else ""
    
    def _get_system_patterns(self) -> str:
        """Extract key system patterns and architecture."""
        if not self.context.get("systemPatterns.md"):
            return ""
        
        lines = self.context["systemPatterns.md"].split('\n')
        pattern_sections = []
        
        # Look for architecture, patterns, standards
        current_section = None
        for line in lines:
            if any(keyword in line.lower() for keyword in ['architecture', 'design patterns', 'quality standards', 'testing']):
                current_section = line
                pattern_sections.append(line)
            elif current_section and line.strip() and not line.startswith('##'):
                pattern_sections.append(line)
                if len(pattern_sections) > 15:  # Keep it focused
                    break
            elif line.startswith('##'):
                current_section = None
        
        return "## System Patterns\n" + '\n'.join(pattern_sections[:15]) if pattern_sections else ""
    
    def _get_progress_summary(self) -> str:
        """Extract progress summary."""
        if not self.context.get("progress.md"):
            return ""
        
        lines = self.context["progress.md"].split('\n')
        progress_sections = []
        
        # Look for what works, what's left, known issues
        current_section = None
        for line in lines:
            if any(keyword in line.lower() for keyword in ['what works', 'what\'s left', 'known issues', 'recent achievements']):
                current_section = line
                progress_sections.append(line)
            elif current_section and line.strip() and not line.startswith('##'):
                progress_sections.append(line)
                if len(progress_sections) > 12:  # Keep it manageable
                    break
            elif line.startswith('##'):
                current_section = None
        
        return "## Progress Summary\n" + '\n'.join(progress_sections[:12]) if progress_sections else ""
    
    def _get_focus_specific_context(self, focus_area: str) -> Optional[str]:
        """Get context specific to the focus area."""
        focus_keywords = {
            'api': ['api', 'endpoint', 'route', 'service', 'fastapi', 'rest'],
            'testing': ['test', 'coverage', 'pytest', 'tdd', 'quality'],
            'features': ['feature', 'functionality', 'requirement', 'user'],
            'performance': ['performance', 'optimization', 'benchmark', 'speed'],
            'deployment': ['deploy', 'docker', 'production', 'infrastructure']
        }
        
        keywords = focus_keywords.get(focus_area.lower(), [focus_area.lower()])
        
        relevant_sections = []
        for filename, content in self.context.items():
            if content and any(keyword in content.lower() for keyword in keywords):
                # Extract relevant lines
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if any(keyword in line.lower() for keyword in keywords):
                        # Include this line and a few context lines
                        start = max(0, i-1)
                        end = min(len(lines), i+3)
                        relevant_sections.extend(lines[start:end])
                        break
        
        if relevant_sections:
            return f"## Focus: {focus_area.title()}\n" + '\n'.join(relevant_sections[:10])
        return None
    
    def _get_prd_summary(self) -> str:
        """Get summary of recent/active PRDs."""
        prds_path = self.memory_bank_path / "prds"
        if not prds_path.exists():
            return ""
        
        prd_files = list(prds_path.glob("*.md"))
        if not prd_files:
            return ""
        
        # Sort by modification time, get most recent 3
        recent_prds = sorted(prd_files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]
        
        prd_summaries = []
        for prd_file in recent_prds:
            summary = self.get_prd_summary(prd_file.stem)
            if summary:
                prd_summaries.append(f"### {prd_file.stem}\n{summary[:200]}...")
        
        return "## Recent PRDs\n" + '\n'.join(prd_summaries) if prd_summaries else ""
    
    def _format_session_context(self, context: str) -> str:
        """Format the final session context for optimal AI consumption."""
        header = f"""# Memory Bank Context - {datetime.now().strftime('%Y-%m-%d %H:%M')}

**Token Efficiency**: This condensed context (~2000 tokens) replaces reading raw memory-bank files (~10,000+ tokens)

**Usage**: Use this context to understand the project before starting any work. Always reference memory-bank for decisions.

**Project Root**: {self.project_root}

---

"""
        
        footer = f"""

---

## Memory Bank Status
- **Files Available**: {len([f for f in self.context.values() if f])} of 6 core files
- **PRDs Available**: {len(self.get_prd_list())} PRDs in memory-bank/prds/
- **Last Updated**: Memory bank files should be updated after each significant work session

## Next Steps for AI Agent
1. Use this context to understand project state
2. Ask clarifying questions if needed
3. Create/update PRD if this is a new feature
4. Proceed with implementation using established patterns
5. Update memory-bank with decisions and progress

**Remember**: Always update activeContext.md with decisions and progress during the session.
"""
        
        return header + context + footer
    
    def _no_memory_bank_response(self) -> str:
        """Response when no memory bank exists."""
        return f"""# Memory Bank Agent - No Memory Bank Found

**Project Root**: {self.project_root}

**Status**: No memory-bank directory found at {self.memory_bank_path}

## Recommendation
This project should have a memory-bank system for optimal Claude Code integration.

To create one:
1. Run the setup wizard: `python .claude-system/setup.py`
2. Or manually create: `memory-bank/` directory with core files
3. Then invoke this agent again for project context

## Minimal Setup
If you need to proceed without full setup:
1. Create `memory-bank/` directory
2. Add basic `projectbrief.md` and `activeContext.md` files  
3. Start documenting decisions and patterns immediately

**Note**: Without memory-bank, you'll lose the token efficiency benefits (~2000 vs 10,000+ tokens) and cross-session context continuity.
"""


def main():
    """Command line interface for memory bank agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Universal Memory Bank Agent")
    parser.add_argument("--focus", help="Focus area (api, testing, features, etc.)")
    parser.add_argument("--update", help="Update active context with new information")
    parser.add_argument("--list-prds", action="store_true", help="List available PRDs")
    parser.add_argument("--project-root", help="Project root directory", default=".")
    
    args = parser.parse_args()
    
    agent = MemoryBankAgent(args.project_root)
    
    if args.list_prds:
        prds = agent.get_prd_list()
        if prds:
            print("Available PRDs:")
            for prd in prds:
                print(f"  - {prd}")
        else:
            print("No PRDs found")
        return
    
    if args.update:
        success = agent.update_active_context("Manual Update", args.update)
        if success:
            print("✅ Active context updated")
        else:
            print("❌ Failed to update active context")
        return
    
    # Default: get session context
    context = agent.get_session_context(args.focus)
    print(context)


if __name__ == "__main__":
    main()