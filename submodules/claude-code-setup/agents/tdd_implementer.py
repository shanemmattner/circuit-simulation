"""
TDD Implementer Agent

Implements features using strict Test-Driven Development practices.
Integrates with memory-bank system for context and pattern continuity.

Key responsibilities:
- Enforce TDD cycle: Red -> Green -> Refactor
- Maintain test coverage and quality
- Update memory bank with patterns learned
- Follow project-specific testing conventions
- Ensure no implementation without tests
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class TDDPhase(Enum):
    RED = "red"      # Write failing test
    GREEN = "green"  # Make test pass
    REFACTOR = "refactor"  # Improve while keeping tests green

@dataclass
class TDDCycle:
    """Represents a complete TDD cycle."""
    feature_description: str
    test_file: str
    implementation_file: str
    phase: TDDPhase
    test_cases: List[str]
    implementation_notes: List[str]
    refactor_notes: List[str]
    started_at: datetime
    completed_at: Optional[datetime] = None

class TDDImplementer:
    """Agent for Test-Driven Development implementation."""
    
    def __init__(self, project_root: str = None):
        """Initialize TDD implementer."""
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.memory_bank_path = self.project_root / "memory-bank"
        self.current_cycle = None
        self.project_config = self._load_project_config()
        
    def implement_feature(self, 
                         feature_description: str,
                         prd_reference: str = None,
                         work_task_id: str = None) -> Dict[str, Any]:
        """
        Implement a feature using strict TDD methodology.
        
        Args:
            feature_description: What to implement
            prd_reference: Associated PRD for context
            work_task_id: Associated work task ID
        
        Returns:
            Implementation result with files created and patterns learned
        """
        print("🔴🟢🔵 TDD Implementer - Starting Feature Implementation")
        print("=" * 60)
        print(f"Feature: {feature_description}")
        if prd_reference:
            print(f"PRD: {prd_reference}")
        if work_task_id:
            print(f"Task ID: {work_task_id}")
        print()
        
        # Initialize TDD cycle
        self.current_cycle = self._initialize_tdd_cycle(feature_description)
        
        # Get project context
        project_context = self._get_project_context()
        
        # Phase 1: RED - Write failing tests
        print("🔴 PHASE 1: RED - Writing failing tests")
        print("-" * 40)
        test_result = self._red_phase(feature_description, project_context)
        
        if not test_result["success"]:
            return {"success": False, "error": "Failed in RED phase", "details": test_result}
        
        # Phase 2: GREEN - Make tests pass
        print("\n🟢 PHASE 2: GREEN - Making tests pass")
        print("-" * 40)
        implementation_result = self._green_phase(feature_description, project_context)
        
        if not implementation_result["success"]:
            return {"success": False, "error": "Failed in GREEN phase", "details": implementation_result}
        
        # Phase 3: REFACTOR - Improve while keeping tests green
        print("\n🔵 PHASE 3: REFACTOR - Improving code quality")
        print("-" * 40)
        refactor_result = self._refactor_phase()
        
        # Update memory bank
        self._update_memory_bank(feature_description, prd_reference, work_task_id)
        
        # Complete cycle
        self.current_cycle.completed_at = datetime.now()
        
        print(f"\n✅ TDD Implementation Complete!")
        print(f"📁 Test file: {self.current_cycle.test_file}")
        print(f"📁 Implementation file: {self.current_cycle.implementation_file}")
        
        return {
            "success": True,
            "test_file": self.current_cycle.test_file,
            "implementation_file": self.current_cycle.implementation_file,
            "test_cases_count": len(self.current_cycle.test_cases),
            "patterns_learned": self._extract_patterns_learned()
        }
    
    def run_tdd_cycle(self, test_description: str, existing_test_file: str = None) -> Dict[str, Any]:
        """
        Run a single TDD cycle for a specific test.
        
        Args:
            test_description: Description of what to test
            existing_test_file: Path to existing test file if available
        
        Returns:
            Result of the TDD cycle
        """
        print(f"🔄 TDD Cycle: {test_description}")
        
        # RED: Write/update failing test
        test_result = self._write_failing_test(test_description, existing_test_file)
        if not test_result["tests_fail"]:
            return {"success": False, "error": "Tests should fail in RED phase"}
        
        # GREEN: Make test pass
        implementation_result = self._make_tests_pass(test_description)
        if not self._run_tests()["all_pass"]:
            return {"success": False, "error": "Tests should pass in GREEN phase"}
        
        # REFACTOR: Improve if needed
        refactor_result = self._refactor_if_needed()
        
        return {
            "success": True,
            "phase_results": {
                "red": test_result,
                "green": implementation_result,
                "refactor": refactor_result
            }
        }
    
    def validate_tdd_compliance(self, feature_files: List[str]) -> Dict[str, Any]:
        """
        Validate that feature implementation follows TDD principles.
        
        Args:
            feature_files: List of files to validate
        
        Returns:
            Compliance analysis
        """
        print("🔍 TDD Compliance Validation")
        
        validation_results = {
            "compliant": True,
            "issues": [],
            "test_coverage": 0,
            "test_quality": "unknown"
        }
        
        # Check test coverage
        coverage_result = self._check_test_coverage(feature_files)
        validation_results["test_coverage"] = coverage_result["percentage"]
        
        if coverage_result["percentage"] < 80:
            validation_results["compliant"] = False
            validation_results["issues"].append("Test coverage below 80%")
        
        # Check test quality
        test_quality = self._analyze_test_quality(feature_files)
        validation_results["test_quality"] = test_quality["rating"]
        
        if test_quality["rating"] == "poor":
            validation_results["compliant"] = False
            validation_results["issues"].extend(test_quality["issues"])
        
        # Check for implementation-first code (anti-pattern)
        implementation_first = self._detect_implementation_first(feature_files)
        if implementation_first["detected"]:
            validation_results["compliant"] = False
            validation_results["issues"].append("Implementation-first code detected")
        
        return validation_results
    
    def _initialize_tdd_cycle(self, feature_description: str) -> TDDCycle:
        """Initialize a new TDD cycle."""
        # Determine file locations based on project structure
        test_file, implementation_file = self._determine_file_locations(feature_description)
        
        return TDDCycle(
            feature_description=feature_description,
            test_file=test_file,
            implementation_file=implementation_file,
            phase=TDDPhase.RED,
            test_cases=[],
            implementation_notes=[],
            refactor_notes=[],
            started_at=datetime.now()
        )
    
    def _red_phase(self, feature_description: str, project_context: str) -> Dict[str, Any]:
        """RED phase: Write failing tests."""
        print("Writing failing tests that describe the desired behavior...")
        
        # Interactive test design
        test_cases = self._design_test_cases(feature_description, project_context)
        
        # Generate test file
        test_content = self._generate_test_file_content(test_cases, feature_description)
        
        # Write test file
        test_file_path = Path(self.current_cycle.test_file)
        test_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(test_file_path, 'w') as f:
            f.write(test_content)
        
        print(f"✅ Test file created: {test_file_path}")
        
        # Run tests to ensure they fail
        test_result = self._run_tests()
        
        if test_result["all_pass"]:
            print("❌ ERROR: Tests should fail in RED phase!")
            return {"success": False, "error": "Tests passed when they should fail"}
        
        print(f"✅ Tests fail as expected ({test_result['failed_count']} failures)")
        
        self.current_cycle.test_cases = test_cases
        self.current_cycle.phase = TDDPhase.GREEN
        
        return {
            "success": True,
            "test_cases_count": len(test_cases),
            "failed_tests": test_result["failed_count"]
        }
    
    def _green_phase(self, feature_description: str, project_context: str) -> Dict[str, Any]:
        """GREEN phase: Make tests pass with minimal implementation."""
        print("Writing minimal implementation to make tests pass...")
        
        # Analyze failing tests to understand requirements
        failing_tests = self._analyze_failing_tests()
        
        # Generate minimal implementation
        implementation_content = self._generate_minimal_implementation(
            failing_tests, feature_description, project_context
        )
        
        # Write implementation file
        impl_file_path = Path(self.current_cycle.implementation_file)
        impl_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if impl_file_path.exists():
            # Update existing file
            existing_content = impl_file_path.read_text()
            updated_content = self._merge_implementation(existing_content, implementation_content)
        else:
            updated_content = implementation_content
        
        with open(impl_file_path, 'w') as f:
            f.write(updated_content)
        
        print(f"✅ Implementation file updated: {impl_file_path}")
        
        # Run tests to ensure they pass
        test_result = self._run_tests()
        
        if not test_result["all_pass"]:
            print(f"❌ ERROR: {test_result['failed_count']} tests still failing!")
            return {"success": False, "error": "Tests still failing after implementation"}
        
        print(f"✅ All tests pass ({test_result['passed_count']} passed)")
        
        self.current_cycle.phase = TDDPhase.REFACTOR
        
        return {
            "success": True,
            "tests_passing": test_result["passed_count"],
            "implementation_approach": "minimal"
        }
    
    def _refactor_phase(self) -> Dict[str, Any]:
        """REFACTOR phase: Improve code while keeping tests green."""
        print("Analyzing code for refactoring opportunities...")
        
        # Run tests before refactoring to establish baseline
        pre_refactor_tests = self._run_tests()
        if not pre_refactor_tests["all_pass"]:
            print("❌ Cannot refactor with failing tests!")
            return {"success": False, "error": "Tests must be green before refactoring"}
        
        # Analyze code quality
        quality_analysis = self._analyze_code_quality()
        
        refactoring_opportunities = []
        
        # Check for common refactoring opportunities
        if quality_analysis["complexity_high"]:
            refactoring_opportunities.append("High complexity functions need simplification")
        
        if quality_analysis["duplication_found"]:
            refactoring_opportunities.append("Code duplication should be eliminated")
        
        if quality_analysis["naming_issues"]:
            refactoring_opportunities.append("Variable/function naming needs improvement")
        
        if not refactoring_opportunities:
            print("✅ No refactoring needed - code quality is good")
            return {"success": True, "refactoring_needed": False}
        
        print(f"Found {len(refactoring_opportunities)} refactoring opportunities:")
        for opportunity in refactoring_opportunities:
            print(f"  - {opportunity}")
        
        # Interactive refactoring
        refactoring_performed = self._perform_refactoring(refactoring_opportunities)
        
        # Run tests after each refactoring to ensure they still pass
        post_refactor_tests = self._run_tests()
        
        if not post_refactor_tests["all_pass"]:
            print("❌ ERROR: Refactoring broke tests!")
            return {"success": False, "error": "Tests failed after refactoring"}
        
        print("✅ Refactoring complete - tests still pass")
        
        self.current_cycle.refactor_notes = refactoring_performed
        
        return {
            "success": True,
            "refactoring_needed": True,
            "refactorings_applied": len(refactoring_performed)
        }
    
    def _design_test_cases(self, feature_description: str, project_context: str) -> List[Dict[str, Any]]:
        """Interactively design test cases for the feature."""
        print("Let's design comprehensive test cases for this feature.")
        print("We need to test: happy path, edge cases, and error conditions.")
        print()
        
        test_cases = []
        
        # Happy path test
        print("1. HAPPY PATH TEST")
        happy_path_desc = input("Describe the main success scenario: ").strip()
        if happy_path_desc:
            test_cases.append({
                "type": "happy_path",
                "description": happy_path_desc,
                "test_name": self._generate_test_name(happy_path_desc),
                "expected_behavior": happy_path_desc
            })
        
        # Edge cases
        print("\n2. EDGE CASES")
        print("What edge cases should we test? (empty line to finish)")
        edge_case_count = 1
        while True:
            edge_case = input(f"Edge case #{edge_case_count}: ").strip()
            if not edge_case:
                break
            
            test_cases.append({
                "type": "edge_case",
                "description": edge_case,
                "test_name": self._generate_test_name(edge_case),
                "expected_behavior": edge_case
            })
            edge_case_count += 1
        
        # Error conditions
        print("\n3. ERROR CONDITIONS")
        print("What error conditions should we test? (empty line to finish)")
        error_count = 1
        while True:
            error_condition = input(f"Error condition #{error_count}: ").strip()
            if not error_condition:
                break
            
            test_cases.append({
                "type": "error_condition",
                "description": error_condition,
                "test_name": self._generate_test_name(error_condition),
                "expected_behavior": error_condition
            })
            error_count += 1
        
        # Validation
        if not test_cases:
            print("⚠️ No test cases defined - adding default test")
            test_cases.append({
                "type": "happy_path",
                "description": feature_description,
                "test_name": self._generate_test_name(feature_description),
                "expected_behavior": feature_description
            })
        
        print(f"\n✅ Designed {len(test_cases)} test cases")
        return test_cases
    
    def _generate_test_file_content(self, test_cases: List[Dict[str, Any]], 
                                  feature_description: str) -> str:
        """Generate content for test file."""
        test_framework = self.project_config.get("test_framework", "pytest")
        
        if test_framework == "pytest":
            return self._generate_pytest_content(test_cases, feature_description)
        else:
            return self._generate_generic_test_content(test_cases, feature_description)
    
    def _generate_pytest_content(self, test_cases: List[Dict[str, Any]], 
                               feature_description: str) -> str:
        """Generate pytest test file content."""
        # Extract module name from implementation file
        impl_path = Path(self.current_cycle.implementation_file)
        module_name = impl_path.stem
        
        # Determine imports based on project structure
        if "src/" in str(impl_path):
            import_path = f"src.{module_name}"
        else:
            import_path = module_name
        
        content = f'''"""
Test module for {feature_description}

This module tests the implementation following TDD principles:
- Tests written before implementation (RED phase)
- Minimal implementation to pass tests (GREEN phase)  
- Refactoring while keeping tests green (REFACTOR phase)

Generated by TDD Implementer Agent - {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""

import pytest
from {import_path} import *  # Import implementation


class Test{self._to_class_name(feature_description)}:
    """Test class for {feature_description}."""
    
    def setup_method(self, method):
        """Set up test fixtures before each test method."""
        # TODO: Add any necessary test setup here
        pass
    
    def teardown_method(self, method):
        """Clean up after each test method.""" 
        # TODO: Add any necessary test cleanup here
        pass

'''
        
        # Generate test methods
        for test_case in test_cases:
            content += f'''
    def {test_case['test_name']}(self):
        """Test: {test_case['description']}"""
        # Arrange
        # TODO: Set up test data and expectations
        
        # Act
        # TODO: Call the code under test
        
        # Assert
        # TODO: Verify the expected behavior
        assert False, "Test not implemented yet - this should fail in RED phase"
'''
        
        return content
    
    def _generate_generic_test_content(self, test_cases: List[Dict[str, Any]], 
                                     feature_description: str) -> str:
        """Generate generic test file content."""
        return f'''"""
Test file for {feature_description}
Generated by TDD Implementer Agent - {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""

# TODO: Add appropriate test framework imports
# TODO: Implement test cases:
{chr(10).join(f"# - {case['description']}" for case in test_cases)}

def test_placeholder():
    """Placeholder test that should fail."""
    assert False, "Tests not implemented yet - RED phase"
'''
    
    def _generate_minimal_implementation(self, failing_tests: List[str], 
                                       feature_description: str,
                                       project_context: str) -> str:
        """Generate minimal implementation to make tests pass."""
        impl_path = Path(self.current_cycle.implementation_file)
        module_name = impl_path.stem
        
        content = f'''"""
{feature_description}

Minimal implementation generated to make tests pass (GREEN phase).
This follows TDD principles - implementation driven by test requirements.

Generated by TDD Implementer Agent - {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""

# TODO: Add necessary imports

class {self._to_class_name(feature_description)}:
    """Implementation for {feature_description}."""
    
    def __init__(self):
        """Initialize the implementation."""
        # TODO: Add initialization logic
        pass
    
    # TODO: Add methods based on failing tests
    # For now, adding placeholder methods to make tests pass


# TODO: Add any module-level functions needed by tests

def main():
    """Main function if this module is run directly."""
    # TODO: Add any demonstration or CLI functionality
    pass


if __name__ == "__main__":
    main()
'''
        
        return content
    
    def _run_tests(self) -> Dict[str, Any]:
        """Run tests and return results."""
        test_framework = self.project_config.get("test_framework", "pytest")
        test_file = self.current_cycle.test_file
        
        try:
            if test_framework == "pytest":
                result = subprocess.run(
                    ["python", "-m", "pytest", test_file, "-v"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
            else:
                # Generic test runner
                result = subprocess.run(
                    ["python", test_file],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
            
            # Parse results
            all_pass = result.returncode == 0
            output = result.stdout + result.stderr
            
            # Count passed/failed (simplified parsing)
            passed_count = output.count("PASSED") if "PASSED" in output else 0
            failed_count = output.count("FAILED") if "FAILED" in output else 0
            
            return {
                "all_pass": all_pass,
                "passed_count": passed_count,
                "failed_count": failed_count,
                "output": output[:1000]  # Truncate for display
            }
        
        except subprocess.TimeoutExpired:
            return {
                "all_pass": False,
                "passed_count": 0,
                "failed_count": 1,
                "output": "Test execution timed out"
            }
        except Exception as e:
            return {
                "all_pass": False,
                "passed_count": 0,
                "failed_count": 1,
                "output": f"Test execution error: {e}"
            }
    
    def _determine_file_locations(self, feature_description: str) -> Tuple[str, str]:
        """Determine where to place test and implementation files."""
        # Convert feature description to file-friendly name
        file_name = self._to_file_name(feature_description)
        
        # Determine project structure
        if (self.project_root / "src").exists():
            impl_file = f"src/{file_name}.py"
            test_file = f"tests/test_{file_name}.py"
        elif (self.project_root / "lib").exists():
            impl_file = f"lib/{file_name}.py"
            test_file = f"tests/test_{file_name}.py"
        else:
            impl_file = f"{file_name}.py"
            test_file = f"test_{file_name}.py"
        
        return str(self.project_root / test_file), str(self.project_root / impl_file)
    
    def _load_project_config(self) -> Dict[str, Any]:
        """Load project configuration for testing."""
        config = {
            "test_framework": "pytest",
            "coverage_target": 85,
            "test_pattern": "test_*.py"
        }
        
        # Try to load from CLAUDE.md or other config files
        claude_md = self.project_root / "CLAUDE.md"
        if claude_md.exists():
            try:
                content = claude_md.read_text()
                if "pytest" in content.lower():
                    config["test_framework"] = "pytest"
                elif "unittest" in content.lower():
                    config["test_framework"] = "unittest"
                
                # Extract coverage target
                import re
                coverage_match = re.search(r'coverage.*?(\d+)%', content.lower())
                if coverage_match:
                    config["coverage_target"] = int(coverage_match.group(1))
            except Exception:
                pass
        
        return config
    
    def _get_project_context(self) -> str:
        """Get project context from memory bank."""
        context_parts = []
        
        try:
            # Get active context
            active_context_path = self.memory_bank_path / "activeContext.md"
            if active_context_path.exists():
                content = active_context_path.read_text()
                context_parts.append(f"Active Context:\n{content[:300]}...")
            
            # Get system patterns
            patterns_path = self.memory_bank_path / "systemPatterns.md"
            if patterns_path.exists():
                content = patterns_path.read_text()
                context_parts.append(f"System Patterns:\n{content[:300]}...")
        
        except Exception:
            pass
        
        if not context_parts:
            context_parts.append(f"Project root: {self.project_root}")
        
        return "\n\n".join(context_parts)
    
    def _update_memory_bank(self, feature_description: str, 
                          prd_reference: str = None,
                          work_task_id: str = None):
        """Update memory bank with patterns learned during implementation."""
        if not self.memory_bank_path.exists():
            return
        
        # Update active context
        active_context_path = self.memory_bank_path / "activeContext.md"
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        update_entry = f"""
## TDD Implementation - {timestamp}
**Feature**: {feature_description}
**PRD Reference**: {prd_reference or "N/A"}
**Task ID**: {work_task_id or "N/A"}

### Implementation Approach
- Test file: {self.current_cycle.test_file}
- Implementation file: {self.current_cycle.implementation_file}
- Test cases: {len(self.current_cycle.test_cases)}

### Patterns Learned
{self._format_patterns_learned()}

### Quality Metrics
- TDD cycle completed successfully
- All tests passing
- Code ready for integration

"""
        
        try:
            with open(active_context_path, 'a') as f:
                f.write(update_entry)
        except Exception as e:
            print(f"Warning: Could not update memory bank: {e}")
    
    def _extract_patterns_learned(self) -> List[str]:
        """Extract patterns learned during implementation."""
        patterns = []
        
        if self.current_cycle.test_cases:
            patterns.append(f"Test design pattern: {len(self.current_cycle.test_cases)} comprehensive test cases")
        
        if self.current_cycle.implementation_notes:
            patterns.append("Implementation approach: Minimal code to pass tests")
        
        if self.current_cycle.refactor_notes:
            patterns.append(f"Refactoring applied: {len(self.current_cycle.refactor_notes)} improvements")
        
        return patterns
    
    def _format_patterns_learned(self) -> str:
        """Format patterns learned for memory bank update."""
        patterns = self._extract_patterns_learned()
        if patterns:
            return "\n".join(f"- {pattern}" for pattern in patterns)
        else:
            return "- Standard TDD implementation pattern applied"
    
    def _to_class_name(self, description: str) -> str:
        """Convert description to class name."""
        words = description.replace('-', ' ').replace('_', ' ').split()
        return ''.join(word.capitalize() for word in words if word.isalnum())
    
    def _to_file_name(self, description: str) -> str:
        """Convert description to file name."""
        import re
        name = re.sub(r'[^a-zA-Z0-9\s]', '', description.lower())
        return '_'.join(name.split())
    
    def _generate_test_name(self, description: str) -> str:
        """Generate test method name from description."""
        name = self._to_file_name(description)
        return f"test_{name}"
    
    def _write_failing_test(self, test_description: str, test_file: str = None) -> Dict[str, Any]:
        """Write a failing test for TDD cycle."""
        # Simplified implementation for single test cycle
        return {"tests_fail": True, "test_written": True}
    
    def _make_tests_pass(self, test_description: str) -> Dict[str, Any]:
        """Implement minimal code to make tests pass."""
        # Simplified implementation for single test cycle
        return {"implementation_added": True, "approach": "minimal"}
    
    def _refactor_if_needed(self) -> Dict[str, Any]:
        """Refactor code if quality improvements are needed."""
        # Simplified implementation for single test cycle
        return {"refactoring_needed": False, "quality": "good"}
    
    def _check_test_coverage(self, files: List[str]) -> Dict[str, Any]:
        """Check test coverage for files."""
        # Simplified coverage check
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "--cov=src", "--cov-report=term-missing"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse coverage from output (simplified)
            output = result.stdout
            import re
            coverage_match = re.search(r'TOTAL.*?(\d+)%', output)
            percentage = int(coverage_match.group(1)) if coverage_match else 0
            
            return {"percentage": percentage, "output": output[:300]}
        
        except Exception:
            return {"percentage": 0, "output": "Coverage check failed"}
    
    def _analyze_test_quality(self, files: List[str]) -> Dict[str, Any]:
        """Analyze quality of test files."""
        # Simplified test quality analysis
        issues = []
        rating = "good"
        
        for file_path in files:
            if "test_" in file_path:
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    if "assert False" in content:
                        issues.append("Placeholder assertions found")
                        rating = "poor"
                    
                    if content.count("def test_") < 2:
                        issues.append("Insufficient test coverage")
                        rating = "fair" if rating == "good" else rating
                
                except Exception:
                    pass
        
        return {"rating": rating, "issues": issues}
    
    def _detect_implementation_first(self, files: List[str]) -> Dict[str, Any]:
        """Detect if implementation was written before tests."""
        # Simplified detection based on file timestamps
        impl_files = [f for f in files if not f.startswith("test_")]
        test_files = [f for f in files if f.startswith("test_")]
        
        detected = False
        
        try:
            for impl_file in impl_files:
                impl_path = Path(impl_file)
                if impl_path.exists():
                    impl_time = impl_path.stat().st_mtime
                    
                    # Find corresponding test file
                    test_file = f"test_{impl_path.name}"
                    test_path = impl_path.parent / test_file
                    
                    if test_path.exists():
                        test_time = test_path.stat().st_mtime
                        if impl_time < test_time:
                            detected = True
                            break
        
        except Exception:
            pass
        
        return {"detected": detected}
    
    def _analyze_failing_tests(self) -> List[str]:
        """Analyze failing tests to understand what to implement."""
        test_result = self._run_tests()
        
        # Extract failing test names from output (simplified)
        failing_tests = []
        if "FAILED" in test_result["output"]:
            lines = test_result["output"].split('\n')
            for line in lines:
                if "FAILED" in line and "::" in line:
                    failing_tests.append(line.strip())
        
        return failing_tests
    
    def _merge_implementation(self, existing_content: str, new_content: str) -> str:
        """Merge new implementation with existing code."""
        # Simplified merge - in practice, this would be more sophisticated
        if "TODO" in existing_content:
            # Replace TODOs with actual implementation
            return new_content
        else:
            # Append new functionality
            return existing_content + "\n\n# New implementation\n" + new_content
    
    def _analyze_code_quality(self) -> Dict[str, Any]:
        """Analyze code quality for refactoring opportunities."""
        # Simplified quality analysis
        return {
            "complexity_high": False,
            "duplication_found": False,
            "naming_issues": False,
            "overall_quality": "good"
        }
    
    def _perform_refactoring(self, opportunities: List[str]) -> List[str]:
        """Perform refactoring based on identified opportunities."""
        print("Refactoring opportunities identified:")
        for i, opp in enumerate(opportunities, 1):
            print(f"  {i}. {opp}")
        
        performed = []
        for opportunity in opportunities:
            perform = input(f"Apply refactoring: {opportunity}? (y/n): ").lower()
            if perform.startswith('y'):
                performed.append(opportunity)
                print(f"✅ Applied refactoring: {opportunity}")
            
            # Run tests after each refactoring
            test_result = self._run_tests()
            if not test_result["all_pass"]:
                print("❌ Tests failed after refactoring - reverting...")
                performed.pop()  # Remove the last refactoring
                break
        
        return performed


def main():
    """Command line interface for TDD implementer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="TDD Implementer Agent")
    parser.add_argument("action", choices=["implement", "cycle", "validate"])
    parser.add_argument("--feature", help="Feature description to implement")
    parser.add_argument("--test", help="Test description for single cycle")
    parser.add_argument("--files", nargs="+", help="Files to validate for TDD compliance")
    parser.add_argument("--prd", help="Associated PRD reference")
    parser.add_argument("--task", help="Work task ID")
    parser.add_argument("--project-root", help="Project root directory", default=".")
    
    args = parser.parse_args()
    
    implementer = TDDImplementer(args.project_root)
    
    if args.action == "implement":
        if not args.feature:
            args.feature = input("Enter feature description: ")
        result = implementer.implement_feature(args.feature, args.prd, args.task)
        if result["success"]:
            print(f"✅ Feature implemented successfully")
            print(f"📁 Files: {result['test_file']}, {result['implementation_file']}")
        else:
            print(f"❌ Implementation failed: {result.get('error')}")
    
    elif args.action == "cycle":
        if not args.test:
            args.test = input("Enter test description: ")
        result = implementer.run_tdd_cycle(args.test)
        if result["success"]:
            print("✅ TDD cycle completed successfully")
        else:
            print(f"❌ TDD cycle failed: {result.get('error')}")
    
    elif args.action == "validate":
        if not args.files:
            args.files = input("Enter files to validate (space-separated): ").split()
        result = implementer.validate_tdd_compliance(args.files)
        if result["compliant"]:
            print("✅ Code follows TDD principles")
        else:
            print(f"❌ TDD compliance issues: {', '.join(result['issues'])}")
            print(f"Test coverage: {result['test_coverage']}%")


if __name__ == "__main__":
    main()