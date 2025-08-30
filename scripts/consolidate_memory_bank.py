#!/usr/bin/env python3
"""
Memory Bank Consolidation Script

Fast mechanical combination of all memory-bank files into a single context document.
Designed to replace slow memory-bank-agent initialization with instant file consolidation.
"""

import os
import sys
from pathlib import Path
from datetime import datetime


def consolidate_memory_bank(memory_bank_dir: str = "memory-bank") -> str:
    """
    Consolidate all memory-bank files into a single context document.
    
    Args:
        memory_bank_dir: Path to memory-bank directory
        
    Returns:
        Consolidated context as a string
    """
    memory_bank_path = Path(memory_bank_dir)
    
    if not memory_bank_path.exists():
        return f"# Memory Bank Not Found\n\nMemory bank directory '{memory_bank_dir}' does not exist."
    
    # Define file processing order (most important first)
    priority_files = [
        "projectbrief.md",
        "productContext.md", 
        "activeContext.md",
        "systemPatterns.md",
        "techContext.md",
        "progress.md",
        "development-log.md"
    ]
    
    consolidated = []
    consolidated.append(f"# Circuit-Simulation Memory Bank Consolidation")
    consolidated.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    consolidated.append("")
    
    # Process priority files first
    processed_files = set()
    for filename in priority_files:
        file_path = memory_bank_path / filename
        if file_path.exists():
            consolidated.extend(_process_file(file_path, filename))
            processed_files.add(filename)
    
    # Process remaining .md files in memory-bank root
    for file_path in sorted(memory_bank_path.glob("*.md")):
        if file_path.name not in processed_files:
            consolidated.extend(_process_file(file_path, file_path.name))
            processed_files.add(file_path.name)
    
    # Process PRD files
    prds_dir = memory_bank_path / "prds"
    if prds_dir.exists():
        consolidated.append("\n---\n")
        consolidated.append("# Product Requirements Documents (PRDs)")
        consolidated.append("")
        
        prd_files = sorted(prds_dir.glob("*.md"))
        if prd_files:
            for prd_file in prd_files:
                consolidated.extend(_process_file(prd_file, f"prds/{prd_file.name}"))
        else:
            consolidated.append("No PRD files found.")
    
    return "\n".join(consolidated)


def _process_file(file_path: Path, display_name: str) -> list[str]:
    """Process a single memory bank file."""
    try:
        content = file_path.read_text(encoding='utf-8').strip()
        if not content:
            return [f"## {display_name}", "", "*File is empty*", ""]
        
        return [
            f"## {display_name}",
            "",
            content,
            "",
            "---",
            ""
        ]
    except Exception as e:
        return [
            f"## {display_name}",
            "",
            f"*Error reading file: {e}*",
            "",
            "---", 
            ""
        ]


def main():
    """Main entry point for script execution."""
    # Support optional memory-bank directory argument
    memory_bank_dir = sys.argv[1] if len(sys.argv) > 1 else "memory-bank"
    
    # Consolidate memory bank
    consolidated_context = consolidate_memory_bank(memory_bank_dir)
    
    # Output to stdout for piping or capture
    print(consolidated_context)


if __name__ == "__main__":
    main()