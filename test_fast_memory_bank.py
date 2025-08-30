#!/usr/bin/env python3
"""
Test Fast Memory Bank Integration

Comprehensive test suite for the new fast memory-bank consolidation system.
Tests both individual scripts and end-to-end integration with development workflow.
"""

import subprocess
import time
import sys
import os
from pathlib import Path


def run_command_with_timing(cmd: list[str], description: str) -> tuple[str, float]:
    """Run a command and return (output, execution_time)."""
    print(f"\n🔍 Testing: {description}")
    print(f"Command: {' '.join(cmd)}")
    
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=True,
            cwd=Path.cwd()
        )
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"✅ Success in {execution_time:.3f} seconds")
        return result.stdout, execution_time
    except subprocess.CalledProcessError as e:
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"❌ Failed in {execution_time:.3f} seconds")
        print(f"Error: {e.stderr}")
        return "", execution_time


def test_consolidation_script():
    """Test the basic consolidation script."""
    print("\n" + "="*60)
    print("TEST 1: Basic Memory Bank Consolidation")
    print("="*60)
    
    output, exec_time = run_command_with_timing([
        "python", "scripts/consolidate_memory_bank.py"
    ], "Memory bank consolidation")
    
    # Validate output content
    if output:
        lines = output.split('\n')
        total_lines = len(lines)
        has_header = "Circuit-Simulation Memory Bank Consolidation" in output
        has_sections = "##" in output
        has_prds = "Product Requirements Documents" in output
        
        print(f"📊 Output Analysis:")
        print(f"   - Total lines: {total_lines}")
        print(f"   - Has header: {has_header}")
        print(f"   - Has sections: {has_sections}")
        print(f"   - Has PRDs: {has_prds}")
        print(f"   - Execution time: {exec_time:.3f}s")
        
        return exec_time < 1.0 and has_header and has_sections
    return False


def test_fast_agent():
    """Test the fast memory-bank agent wrapper."""
    print("\n" + "="*60)
    print("TEST 2: Fast Memory Bank Agent")
    print("="*60)
    
    # Test with different focus areas
    focus_areas = [
        "integration planning",
        "debugging context", 
        "feature development",
        ""  # No focus
    ]
    
    results = []
    for focus in focus_areas:
        cmd = ["python", "scripts/fast_memory_bank_agent.py"]
        if focus:
            cmd.append(focus)
            
        output, exec_time = run_command_with_timing(
            cmd, f"Fast agent with focus: '{focus}'"
        )
        
        # Validate output
        if output:
            has_analysis = "Fast Memory Bank Analysis" in output
            has_context = "Consolidated Content" in output
            has_focus = focus in output if focus else True
            
            print(f"📊 Analysis:")
            print(f"   - Has analysis header: {has_analysis}")
            print(f"   - Has consolidated content: {has_context}")
            print(f"   - Focus reflected: {has_focus}")
            print(f"   - Execution time: {exec_time:.3f}s")
            
            results.append(exec_time < 1.0 and has_analysis and has_context)
        else:
            results.append(False)
    
    return all(results)


def test_memory_bank_files_exist():
    """Test that required memory-bank files exist."""
    print("\n" + "="*60)
    print("TEST 3: Memory Bank File Structure")
    print("="*60)
    
    memory_bank = Path("memory-bank")
    if not memory_bank.exists():
        print("❌ Memory bank directory doesn't exist")
        return False
    
    required_files = [
        "projectbrief.md",
        "productContext.md", 
        "activeContext.md",
        "systemPatterns.md",
        "techContext.md",
        "progress.md"
    ]
    
    existing_files = []
    for file_name in required_files:
        file_path = memory_bank / file_name
        exists = file_path.exists()
        size = file_path.stat().st_size if exists else 0
        
        print(f"📄 {file_name}: {'✅' if exists else '❌'} ({size} bytes)")
        if exists:
            existing_files.append(file_name)
    
    # Check PRDs directory
    prds_dir = memory_bank / "prds"
    if prds_dir.exists():
        prd_files = list(prds_dir.glob("*.md"))
        print(f"📁 PRDs directory: ✅ ({len(prd_files)} PRD files)")
    else:
        print(f"📁 PRDs directory: ❌")
        prd_files = []
    
    # Check scripts directory
    scripts_exist = Path("scripts/consolidate_memory_bank.py").exists()
    agent_exists = Path("scripts/fast_memory_bank_agent.py").exists()
    
    print(f"🔧 Scripts:")
    print(f"   - consolidate_memory_bank.py: {'✅' if scripts_exist else '❌'}")
    print(f"   - fast_memory_bank_agent.py: {'✅' if agent_exists else '❌'}")
    
    return len(existing_files) >= 4 and scripts_exist and agent_exists


def test_claude_code_integration():
    """Test Claude Code configuration is updated."""
    print("\n" + "="*60)
    print("TEST 4: Claude Code Integration")
    print("="*60)
    
    # Check memory-bank-agent configuration
    agent_file = Path(".claude/agents/memory-bank-agent.md")
    if agent_file.exists():
        content = agent_file.read_text()
        has_fast_approach = "FAST CONSOLIDATION APPROACH" in content
        has_script_reference = "fast_memory_bank_agent.py" in content
        has_performance_note = "4400x faster" in content
        
        print(f"🤖 Memory Bank Agent:")
        print(f"   - Has fast approach: {'✅' if has_fast_approach else '❌'}")
        print(f"   - References script: {'✅' if has_script_reference else '❌'}")
        print(f"   - Performance note: {'✅' if has_performance_note else '❌'}")
        
        agent_ok = has_fast_approach and has_script_reference
    else:
        print("❌ Memory bank agent configuration not found")
        agent_ok = False
    
    # Check PRD commands
    develop_cmd = Path(".claude/commands/develop-feature.md")
    debug_cmd = Path(".claude/commands/debug-issue.md")
    
    commands_ok = True
    for cmd_file in [develop_cmd, debug_cmd]:
        if cmd_file.exists():
            content = cmd_file.read_text()
            has_fast_flag = "use_fast_consolidation" in content
            print(f"📋 {cmd_file.name}: {'✅' if has_fast_flag else '❌'} fast consolidation")
            commands_ok = commands_ok and has_fast_flag
        else:
            print(f"❌ {cmd_file.name} not found")
            commands_ok = False
    
    # Check CLAUDE.md documentation
    claude_md = Path("CLAUDE.md")
    if claude_md.exists():
        content = claude_md.read_text()
        has_fast_section = "FAST CONSOLIDATION" in content
        has_performance_info = "4400x faster" in content
        
        print(f"📚 CLAUDE.md:")
        print(f"   - Fast consolidation section: {'✅' if has_fast_section else '❌'}")
        print(f"   - Performance information: {'✅' if has_performance_info else '❌'}")
        
        docs_ok = has_fast_section and has_performance_info
    else:
        print("❌ CLAUDE.md not found")
        docs_ok = False
    
    return agent_ok and commands_ok and docs_ok


def test_performance_comparison():
    """Test performance improvement vs theoretical old approach."""
    print("\n" + "="*60)
    print("TEST 5: Performance Validation")
    print("="*60)
    
    # Time the consolidation script multiple times
    times = []
    for i in range(3):
        output, exec_time = run_command_with_timing([
            "python", "scripts/consolidate_memory_bank.py"
        ], f"Performance test run {i+1}")
        times.append(exec_time)
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"📊 Performance Results:")
    print(f"   - Average time: {avg_time:.3f}s")
    print(f"   - Min time: {min_time:.3f}s")
    print(f"   - Max time: {max_time:.3f}s")
    print(f"   - Target: < 1.0s")
    
    # Calculate improvement vs old approach (5+ minutes = 300s)
    old_time = 300  # 5 minutes
    improvement = old_time / avg_time
    print(f"   - Improvement factor: {improvement:.0f}x faster than old approach")
    
    return avg_time < 1.0 and improvement > 100


def main():
    """Run all tests and provide summary."""
    print("🚀 Fast Memory Bank Integration Test Suite")
    print("="*60)
    
    tests = [
        ("File Structure", test_memory_bank_files_exist),
        ("Consolidation Script", test_consolidation_script),
        ("Fast Agent Wrapper", test_fast_agent),
        ("Claude Code Integration", test_claude_code_integration),
        ("Performance Validation", test_performance_comparison),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} {test_name}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Fast memory bank integration is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Review the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())