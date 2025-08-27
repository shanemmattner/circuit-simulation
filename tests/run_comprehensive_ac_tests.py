#!/usr/bin/env python3
"""
Comprehensive AC Analysis Test Runner

This script runs all AC analysis tests and generates Claude Code friendly reports
that help identify and fix issues with:
1. Complex value handling in AC analysis
2. Circuit behavior validation  
3. Visual chart generation and comparison
4. Regression prevention

Usage:
    python tests/run_comprehensive_ac_tests.py
    python tests/run_comprehensive_ac_tests.py --visual --slow
    python tests/run_comprehensive_ac_tests.py --report-only
"""

import sys
import os
import argparse
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "tests"))

from visual_testing_framework import (
    VisualTestFramework, 
    run_ac_analysis_regression_tests,
    VisualTestResult
)


class ComprehensiveACTestRunner:
    """Runs comprehensive AC analysis tests and generates actionable reports."""
    
    def __init__(self, output_dir: str = "tests/comprehensive_ac_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_categories": {},
            "summary": {},
            "claude_recommendations": [],
            "critical_issues": [],
            "files_generated": []
        }
        
    def run_pytest_ac_tests(self, visual: bool = False, slow: bool = False) -> Dict[str, Any]:
        """Run pytest-based AC analysis tests."""
        
        print("🧪 Running PyTest AC Analysis Tests")
        print("=" * 50)
        
        # Build pytest command
        cmd = [
            sys.executable, "-m", "pytest", 
            "tests/test_ac_analysis_behavior.py",
            "-v", "--tb=short", 
            f"--junitxml={self.output_dir}/pytest_ac_results.xml"
        ]
        
        if visual:
            cmd.append("--run-visual")
        if slow:
            cmd.append("--run-slow")
            
        # Add coverage if available
        try:
            import coverage
            cmd.extend(["--cov=src/circuit_sim/simulator", 
                       f"--cov-report=html:{self.output_dir}/coverage_html",
                       f"--cov-report=json:{self.output_dir}/coverage.json"])
        except ImportError:
            print("ℹ️  Coverage not available (pip install coverage for coverage reports)")
        
        # Run pytest
        try:
            result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
            
            pytest_results = {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "passed": result.returncode == 0
            }
            
            print(f"PyTest Exit Code: {result.returncode}")
            if result.returncode != 0:
                print("❌ Some tests failed:")
                print(result.stdout)
                if result.stderr:
                    print("Errors:")
                    print(result.stderr)
            else:
                print("✅ All PyTest tests passed!")
                
            return pytest_results
            
        except Exception as e:
            return {
                "returncode": -1,
                "error": str(e),
                "passed": False
            }
    
    def run_visual_framework_tests(self) -> List[VisualTestResult]:
        """Run visual framework tests."""
        
        print("\n🎨 Running Visual Framework Tests")
        print("=" * 50)
        
        return run_ac_analysis_regression_tests()
    
    def run_docker_simulation_test(self) -> Dict[str, Any]:
        """Test AC analysis specifically in Docker environment."""
        
        print("\n🐳 Testing Docker Simulation Environment")
        print("=" * 50)
        
        try:
            # Check if we can run simulations
            from circuit_sim import Circuit
            from circuit_sim.simulator import SimulationEngine
            
            # Create simple test circuit
            circuit = Circuit("Docker AC Test")
            circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="1V")
            circuit.add_resistor("R1", node1=1, node2=2, resistance="1000")
            circuit.add_capacitor("C1", node1=2, node2=0, capacitance="1e-6")
            
            engine = SimulationEngine()
            
            # Test DC analysis
            dc_results = engine.simulate_dc(circuit)
            dc_success = dc_results is not None
            
            # Test AC analysis
            ac_results = engine.simulate_ac(circuit, 1, 10000, points_per_decade=10)
            ac_success = ac_results is not None
            
            if ac_success:
                # Check for complex values
                voltage_data = ac_results.get_voltage(2)
                complex_values = voltage_data is not None and hasattr(voltage_data, 'dtype') and voltage_data.dtype == complex
            else:
                complex_values = False
                
            return {
                "docker_available": True,
                "dc_simulation_success": dc_success,
                "ac_simulation_success": ac_success,
                "complex_values_present": complex_values,
                "passed": dc_success and ac_success and complex_values
            }
            
        except ImportError as e:
            return {
                "docker_available": False,
                "error": f"PySpice/ngspice not available: {e}",
                "passed": False,
                "recommendation": "Run tests in Docker environment with: docker-compose run --rm circuit-sim python tests/run_comprehensive_ac_tests.py"
            }
        except Exception as e:
            return {
                "docker_available": True,
                "error": str(e),
                "passed": False
            }
    
    def analyze_results_for_claude(self, pytest_results: Dict, visual_results: List[VisualTestResult], 
                                 docker_results: Dict) -> None:
        """Analyze all test results and generate Claude Code recommendations."""
        
        # Store results
        self.results["test_categories"] = {
            "pytest": pytest_results,
            "visual_framework": [
                {
                    "test_name": r.test_name,
                    "passed": r.passed,
                    "score": r.score,
                    "issues": r.issues,
                    "warnings": r.warnings,
                    "metadata": r.metadata
                }
                for r in visual_results
            ],
            "docker_environment": docker_results
        }
        
        # Calculate summary
        total_tests = 0
        passed_tests = 0
        
        if pytest_results.get("passed"):
            # Estimate pytest results (would need XML parsing for exact count)
            passed_tests += 10  # Approximate
            total_tests += 10
        else:
            total_tests += 10
            
        passed_tests += sum(1 for r in visual_results if r.passed)
        total_tests += len(visual_results)
        
        if docker_results.get("passed"):
            passed_tests += 1
            total_tests += 1
        else:
            total_tests += 1
            
        self.results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": passed_tests / max(1, total_tests),
            "overall_status": "PASS" if passed_tests == total_tests else "FAIL"
        }
        
        # Analyze critical issues
        critical_issues = []
        recommendations = []
        
        # Check for AC complex value issues
        complex_issues = [r for r in visual_results if not r.passed and "complex" in r.test_name.lower()]
        if complex_issues:
            critical_issues.append("❌ CRITICAL: AC analysis returning real-only values instead of complex")
            recommendations.extend([
                "1. Check PySpice AC source configuration in src/circuit_sim/simulator/builder.py",
                "2. Verify voltage sources use 'DC 0 AC 1' syntax for AC analysis", 
                "3. Ensure AC analysis results are stored as complex numpy arrays",
                "4. Test AC analysis directly with PySpice to isolate the issue"
            ])
        
        # Check for behavior validation issues  
        behavior_issues = [r for r in visual_results if not r.passed and "behavior" in r.test_name.lower()]
        if behavior_issues:
            critical_issues.append("❌ CRITICAL: Circuit behavior doesn't match theoretical expectations")
            recommendations.extend([
                "5. Verify component value parsing in circuit builder",
                "6. Check frequency vector generation in simulate_ac()",
                "7. Compare simulation results with hand calculations",
                "8. Validate transfer function implementation"
            ])
        
        # Check for visual/charting issues
        visual_issues = [r for r in visual_results if not r.passed and "visual" in r.test_name.lower()]
        if visual_issues:
            critical_issues.append("⚠️  WARNING: Visual chart generation has issues")
            recommendations.extend([
                "9. Check Plotly chart generation with complex AC data",
                "10. Verify magnitude and phase extraction from complex values",
                "11. Test chart templates with actual simulation results",
                "12. Validate chart axes and scaling"
            ])
        
        # Docker environment issues
        if not docker_results.get("passed"):
            if not docker_results.get("docker_available"):
                critical_issues.append("❌ CRITICAL: Simulation environment not available")
                recommendations.append("13. Run tests in Docker environment: docker-compose run --rm circuit-sim python tests/run_comprehensive_ac_tests.py")
            else:
                critical_issues.append("❌ CRITICAL: Simulation engine failing in current environment")
        
        self.results["critical_issues"] = critical_issues
        self.results["claude_recommendations"] = recommendations
    
    def generate_claude_report(self) -> str:
        """Generate comprehensive report for Claude Code analysis."""
        
        report_lines = [
            "# Comprehensive AC Analysis Test Report",
            f"Generated: {self.results['timestamp']}",
            "",
            "## Executive Summary",
            ""
        ]
        
        summary = self.results["summary"]
        status_emoji = "✅" if summary["overall_status"] == "PASS" else "❌"
        
        report_lines.extend([
            f"{status_emoji} **Overall Status: {summary['overall_status']}**",
            f"- Tests Passed: {summary['passed_tests']}/{summary['total_tests']} ({summary['success_rate']:.1%})",
            f"- Test Categories: PyTest, Visual Framework, Docker Environment",
            ""
        ])
        
        # Critical Issues Section
        if self.results["critical_issues"]:
            report_lines.extend([
                "## 🚨 Critical Issues Requiring Immediate Attention",
                ""
            ])
            for issue in self.results["critical_issues"]:
                report_lines.append(f"- {issue}")
            report_lines.append("")
        
        # Recommendations for Claude Code
        if self.results["claude_recommendations"]:
            report_lines.extend([
                "## 🤖 Recommendations for Claude Code",
                "",
                "### Immediate Actions:",
                ""
            ])
            for rec in self.results["claude_recommendations"][:5]:
                report_lines.append(f"- {rec}")
            
            if len(self.results["claude_recommendations"]) > 5:
                report_lines.extend([
                    "",
                    "### Additional Actions:",
                    ""
                ])
                for rec in self.results["claude_recommendations"][5:]:
                    report_lines.append(f"- {rec}")
            
            report_lines.append("")
        
        # Detailed Results
        report_lines.extend([
            "## Detailed Test Results",
            ""
        ])
        
        # PyTest Results
        pytest_results = self.results["test_categories"]["pytest"]
        pytest_status = "✅ PASS" if pytest_results.get("passed") else "❌ FAIL"
        report_lines.extend([
            f"### PyTest AC Analysis Tests: {pytest_status}",
            ""
        ])
        
        if pytest_results.get("returncode") != 0:
            report_lines.extend([
                "Output:",
                "```",
                pytest_results.get("stdout", "No output"),
                "```",
                ""
            ])
        
        # Visual Framework Results
        visual_results = self.results["test_categories"]["visual_framework"]
        visual_passed = sum(1 for r in visual_results if r["passed"])
        visual_total = len(visual_results)
        visual_status = "✅ PASS" if visual_passed == visual_total else "❌ FAIL"
        
        report_lines.extend([
            f"### Visual Framework Tests: {visual_status} ({visual_passed}/{visual_total})",
            ""
        ])
        
        for result in visual_results:
            status = "✅" if result["passed"] else "❌"
            report_lines.append(f"- {status} {result['test_name']} (Score: {result['score']:.1%})")
            if result["issues"]:
                for issue in result["issues"]:
                    report_lines.append(f"  - Issue: {issue}")
        
        report_lines.append("")
        
        # Docker Environment Results
        docker_results = self.results["test_categories"]["docker_environment"]
        docker_status = "✅ PASS" if docker_results.get("passed") else "❌ FAIL"
        
        report_lines.extend([
            f"### Docker Environment Test: {docker_status}",
            ""
        ])
        
        if docker_results.get("error"):
            report_lines.append(f"- Error: {docker_results['error']}")
        if docker_results.get("recommendation"):
            report_lines.append(f"- Recommendation: {docker_results['recommendation']}")
        
        report_lines.append("")
        
        # Files Generated
        if self.results["files_generated"]:
            report_lines.extend([
                "## Generated Files",
                ""
            ])
            for file_path in self.results["files_generated"]:
                report_lines.append(f"- {file_path}")
        
        return "\n".join(report_lines)
    
    def run_comprehensive_tests(self, visual: bool = False, slow: bool = False, 
                              report_only: bool = False) -> None:
        """Run all comprehensive AC analysis tests."""
        
        print("🚀 Starting Comprehensive AC Analysis Testing")
        print("=" * 60)
        
        if not report_only:
            # Run pytest tests
            pytest_results = self.run_pytest_ac_tests(visual=visual, slow=slow)
            
            # Run visual framework tests
            visual_results = self.run_visual_framework_tests()
            
            # Run Docker environment test
            docker_results = self.run_docker_simulation_test()
            
            # Analyze results
            self.analyze_results_for_claude(pytest_results, visual_results, docker_results)
            
            # Save raw results
            results_file = self.output_dir / "test_results.json"
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            
            self.results["files_generated"].append(str(results_file))
        
        # Generate Claude report
        claude_report = self.generate_claude_report()
        report_file = self.output_dir / "claude_ac_analysis_report.md"
        with open(report_file, 'w') as f:
            f.write(claude_report)
        
        self.results["files_generated"].append(str(report_file))
        
        print(f"\n📊 Comprehensive test complete!")
        print(f"📁 Report saved to: {report_file}")
        
        # Print immediate summary
        if not report_only:
            summary = self.results["summary"]
            print(f"\n{summary['overall_status']}: {summary['passed_tests']}/{summary['total_tests']} tests passed")
            
            if self.results["critical_issues"]:
                print("\n🚨 Critical issues found:")
                for issue in self.results["critical_issues"]:
                    print(f"  {issue}")
        
        return self.results


def main():
    parser = argparse.ArgumentParser(description="Run comprehensive AC analysis tests")
    parser.add_argument("--visual", action="store_true", help="Run visual comparison tests")
    parser.add_argument("--slow", action="store_true", help="Run slow parameter sweep tests")
    parser.add_argument("--report-only", action="store_true", help="Only generate report from existing results")
    parser.add_argument("--output-dir", default="tests/comprehensive_ac_output", help="Output directory")
    
    args = parser.parse_args()
    
    runner = ComprehensiveACTestRunner(args.output_dir)
    results = runner.run_comprehensive_tests(
        visual=args.visual,
        slow=args.slow,
        report_only=args.report_only
    )
    
    # Exit with non-zero code if tests failed
    if results["summary"].get("overall_status") != "PASS":
        sys.exit(1)


if __name__ == "__main__":
    main()