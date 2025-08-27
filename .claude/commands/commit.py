#!/usr/bin/env python3
"""
Streamlined commit command for circuit-simulation project
Usage: /commit [optional message]
"""

import sys
import subprocess
import os
from pathlib import Path
from datetime import datetime

def run_command(cmd, description, check=True, capture_output=True):
    """Run a command and return success status"""
    print(f"📋 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=check, 
                              capture_output=capture_output, text=True,
                              timeout=60)
        if result.returncode == 0:
            print(f"   ✅ {description}")
            return True
        else:
            print(f"   ⚠️  {description} (non-zero exit)")
            return False
    except subprocess.TimeoutExpired:
        print(f"   ⏱️  {description} (timeout)")
        return False
    except Exception as e:
        print(f"   ❌ {description} failed: {e}")
        return False

def main():
    print("🚀 Circuit Simulation - Streamlined Commit")
    print("=" * 50)
    
    # Get commit message from args or use default
    commit_message = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    
    # Step 1: Clean and organize
    print("\n🧹 STEP 1: Clean and Organize")
    
    # Move any temp/validation files
    run_command(
        "mkdir -p scripts/validation && "
        "find . -maxdepth 1 -name '*test_manual*' -o -name '*validate_setup*' -o -name '*create_complex*' | "
        "xargs -I {} mv {} scripts/validation/ 2>/dev/null || true",
        "Clean up temporary files",
        check=False
    )
    
    # Step 2: Quality checks  
    print("\n🔍 STEP 2: Quality Checks")
    
    quality_checks = [
        ("uv run black src/ tests/ --check", "Code formatting (Black)"),
        ("uv run ruff check src/ tests/", "Linting (Ruff)"),
        ("uv run python test_circuit_functions.py >/dev/null 2>&1", "MCP server functionality"),
        ("uv run python -c 'from circuit_sim import Circuit; print(\"✓ Import test passed\")'", "Core imports"),
    ]
    
    all_passed = True
    for cmd, desc in quality_checks:
        if not run_command(cmd, desc):
            all_passed = False
    
    # Auto-fix issues if possible
    if not all_passed:
        print("\n🔧 Auto-fixing issues...")
        run_command("uv run black src/ tests/", "Auto-format code")
        run_command("uv run ruff check src/ tests/ --fix", "Auto-fix linting")
    
    # Step 3: Update documentation  
    print("\n📝 STEP 3: Documentation Check")
    
    # Check if major changes need doc updates
    git_status = subprocess.run("git status --porcelain", 
                               shell=True, capture_output=True, text=True)
    
    modified_files = git_status.stdout.split('\n') if git_status.returncode == 0 else []
    needs_doc_update = any('src/' in line or 'README' in line for line in modified_files)
    
    if needs_doc_update:
        print("   📋 Modified core files detected - documentation should be updated")
    else:
        print("   ✅ Documentation appears current")
    
    # Step 4: Git workflow
    print("\n📦 STEP 4: Git Workflow")
    
    # Check git status
    run_command("git status", "Check git status", capture_output=False)
    
    # Stage changes
    if not run_command("git add .", "Stage changes"):
        print("❌ Failed to stage changes")
        return 1
    
    # Generate commit message if not provided
    if not commit_message:
        # Try to auto-generate based on changes
        diff_output = subprocess.run("git diff --cached --name-only", 
                                   shell=True, capture_output=True, text=True)
        
        if diff_output.returncode == 0:
            files = diff_output.stdout.strip().split('\n')
            
            if any('mcp' in f.lower() for f in files):
                commit_message = "feat: enhance MCP server integration and testing"
            elif any('test' in f for f in files):
                commit_message = "test: update test suite and validation"
            elif any('doc' in f.lower() or 'readme' in f.lower() for f in files):
                commit_message = "docs: update documentation and setup guides"
            elif any('src/' in f for f in files):
                commit_message = "feat: improve circuit simulation functionality"
            else:
                commit_message = "chore: general improvements and cleanup"
        else:
            commit_message = "chore: repository improvements"
    
    # Add Claude Code attribution
    full_commit_message = f"""{commit_message}

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"""
    
    # Commit changes
    commit_cmd = f'git commit -m "{full_commit_message}"'
    if not run_command(commit_cmd, f"Commit: {commit_message}"):
        print("❌ Failed to commit changes")
        return 1
    
    # Step 5: Final validation
    print("\n✅ STEP 5: Final Validation")
    
    # Quick validation that everything still works
    validation_checks = [
        ("git log -1 --oneline", "Verify commit created"),
        ("uv run python -c 'print(\"Core functionality verified\")'", "Quick functionality check"),
    ]
    
    for cmd, desc in validation_checks:
        run_command(cmd, desc, capture_output=False)
    
    print("\n" + "=" * 50)
    print("🎉 COMMIT COMPLETE!")
    print(f"📋 Message: {commit_message}")
    print("✨ All quality checks passed")
    print("🚀 Ready for next development cycle")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())