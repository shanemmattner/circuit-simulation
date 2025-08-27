#!/usr/bin/env python3
"""
Claude Code Test Helper

This module provides utilities specifically designed for Claude Code to:
1. Understand test results and failures
2. Make intelligent decisions about what to fix
3. Generate targeted test cases for specific issues
4. Assess the quality of circuit simulation behavior

This is the interface Claude Code should use to interact with the testing framework.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "tests"))

from visual_testing_framework import (
    VisualTestFramework, 
    CircuitBehaviorValidator, 
    ReferenceSignalGenerator,
    VisualTestResult
)


class ClaudeTestHelper:
    """Helper class for Claude Code to interact with the testing framework."""
    
    def __init__(self):
        self.framework = VisualTestFramework()
        self.validator = CircuitBehaviorValidator()
        self.reference_gen = ReferenceSignalGenerator()
    
    def diagnose_ac_analysis_issue(self) -> Dict[str, Any]:
        """
        Diagnose AC analysis issues by running targeted tests.
        
        Returns a diagnosis that Claude Code can act on.
        """
        print("🔍 Diagnosing AC Analysis Issues...")
        
        diagnosis = {
            "timestamp": str(Path(__file__).stat().st_mtime),
            "issues_found": [],
            "recommendations": [],
            "test_results": {},
            "confidence": "unknown"
        }
        
        try:
            # Test 1: Basic RC filter AC analysis
            results = self.framework.test_rc_lowpass_circuit_comprehensive()
            diagnosis["test_results"]["rc_lowpass"] = results
            
            # Analyze specific issues
            for result in results:
                if not result.passed:
                    if "complex" in result.test_name.lower():
                        diagnosis["issues_found"].append({
                            "type": "complex_values_missing",
                            "severity": "critical",
                            "description": "AC analysis returning real-only values instead of complex",
                            "evidence": result.issues,
                            "likely_cause": "PySpice AC source configuration issue",
                            "files_to_check": [
                                "src/circuit_sim/simulator/builder.py",
                                "src/circuit_sim/simulator/engine.py"
                            ]
                        })
                        diagnosis["recommendations"].append(
                            "Check PySpice voltage source AC configuration - should use 'DC 0 AC 1' syntax"
                        )
                    
                    elif "behavior" in result.test_name.lower():
                        diagnosis["issues_found"].append({
                            "type": "physics_validation_failed", 
                            "severity": "critical",
                            "description": "Circuit behavior doesn't match theoretical expectations",
                            "evidence": result.issues,
                            "likely_cause": "Simulation math or component value parsing issue",
                            "files_to_check": [
                                "src/circuit_sim/simulator/engine.py",
                                "src/circuit_sim/parser.py"
                            ]
                        })
                        diagnosis["recommendations"].append(
                            "Verify component values are parsed correctly and simulation math is accurate"
                        )
                    
                    elif "visual" in result.test_name.lower():
                        diagnosis["issues_found"].append({
                            "type": "chart_generation_issue",
                            "severity": "warning", 
                            "description": "Visual charts don't match reference",
                            "evidence": result.issues,
                            "likely_cause": "Chart generation or data formatting issue",
                            "files_to_check": [
                                "src/circuit_sim/reports/charts/",
                                "src/circuit_sim/visualization/"
                            ]
                        })
                        diagnosis["recommendations"].append(
                            "Check chart generation pipeline for complex AC data handling"
                        )
            
            # Determine overall confidence
            if not diagnosis["issues_found"]:
                diagnosis["confidence"] = "high - no issues detected"
            elif len(diagnosis["issues_found"]) == 1:
                diagnosis["confidence"] = "high - single issue identified"
            else:
                diagnosis["confidence"] = "medium - multiple issues need investigation"
                
        except Exception as e:
            diagnosis["issues_found"].append({
                "type": "testing_framework_error",
                "severity": "critical", 
                "description": f"Testing framework failed: {str(e)}",
                "likely_cause": "Missing dependencies or environment issue",
                "files_to_check": ["tests/visual_testing_framework.py"]
            })
            diagnosis["confidence"] = "low - testing failed"
        
        return diagnosis
    
    def assess_circuit_behavior(self, circuit_name: str, ac_results, 
                              expected_behavior: str) -> str:
        """
        Assess whether a circuit's behavior matches expectations.
        
        Args:
            circuit_name: Name of the circuit being tested
            ac_results: SimulationResults from AC analysis
            expected_behavior: Expected behavior type ("rc_lowpass", "rc_highpass", etc.)
            
        Returns:
            Human-readable assessment for Claude Code
        """
        
        assessment_lines = [
            f"🔬 Circuit Behavior Assessment: {circuit_name}",
            f"Expected Behavior: {expected_behavior}",
            "=" * 50
        ]
        
        try:
            # First, check if we have complex values
            complex_test = self.validator.validate_ac_complex_values(ac_results, node_id=2)
            
            if not complex_test.passed:
                assessment_lines.extend([
                    "❌ CRITICAL ISSUE: AC analysis not returning complex values",
                    "   This means phase information is missing from frequency response",
                    "   Issue: " + ", ".join(complex_test.issues),
                    "   Action: Fix PySpice AC source configuration immediately",
                    ""
                ])
                return "\n".join(assessment_lines)
            
            assessment_lines.extend([
                "✅ Complex values present - AC analysis working correctly",
                f"   Magnitude range: {complex_test.metadata.get('complex_analysis', {}).get('magnitude_range', 'unknown')}",
                f"   Phase range: {complex_test.metadata.get('complex_analysis', {}).get('phase_range_deg', 'unknown')}",
                ""
            ])
            
            # Now check specific behavior
            if expected_behavior == "rc_lowpass":
                # Test RC low-pass behavior (assuming 1kΩ, 1μF for now)
                behavior_test = self.validator.validate_rc_lowpass_behavior(
                    None, ac_results, 1000, 1e-6  # Circuit object not needed for this test
                )
                
                if behavior_test.passed:
                    assessment_lines.extend([
                        "✅ RC Low-pass behavior validated successfully",
                        f"   Score: {behavior_test.score:.1%}",
                        ""
                    ])
                    
                    # Add specific physics analysis
                    physics = behavior_test.metadata.get('physics_analysis', {})
                    if physics:
                        assessment_lines.extend([
                            "📊 Physics Analysis:",
                            f"   Cutoff frequency: {physics.get('cutoff_frequency_hz', 'unknown'):.1f} Hz",
                            f"   DC gain: {physics.get('dc_gain_db', 'unknown'):.1f} dB",
                            f"   Cutoff gain: {physics.get('cutoff_gain_db', 'unknown'):.1f} dB",
                            f"   Phase at DC: {physics.get('phase_at_dc', 'unknown'):.1f}°", 
                            f"   Phase at cutoff: {physics.get('phase_at_cutoff', 'unknown'):.1f}°",
                            ""
                        ])
                else:
                    assessment_lines.extend([
                        "❌ RC Low-pass behavior validation failed",
                        f"   Score: {behavior_test.score:.1%}",
                        "   Issues:"
                    ])
                    for issue in behavior_test.issues:
                        assessment_lines.append(f"     - {issue}")
                    
                    assessment_lines.append("")
            
            else:
                assessment_lines.extend([
                    f"⚠️  Behavior type '{expected_behavior}' not yet implemented",
                    "   Available: rc_lowpass",
                    ""
                ])
        
        except Exception as e:
            assessment_lines.extend([
                f"❌ Assessment failed with exception: {str(e)}",
                "   This indicates a problem with the testing framework",
                ""
            ])
        
        return "\n".join(assessment_lines)
    
    def generate_targeted_test_for_issue(self, issue_type: str) -> str:
        """
        Generate a targeted test case for a specific issue type.
        
        Args:
            issue_type: Type of issue ("complex_values", "rc_behavior", "chart_generation")
            
        Returns:
            Python test code that Claude Code can run
        """
        
        if issue_type == "complex_values":
            return '''
def test_ac_complex_values_targeted():
    """Targeted test for AC analysis complex value issue."""
    from circuit_sim import Circuit
    from circuit_sim.simulator import SimulationEngine
    import numpy as np
    
    # Create simple RC circuit
    circuit = Circuit("AC Complex Test")
    circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="1V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="1000")
    circuit.add_capacitor("C1", node1=2, node2=0, capacitance="1e-6")
    
    # Run AC analysis
    engine = SimulationEngine()
    results = engine.simulate_ac(circuit, 10, 1000, points_per_decade=10)
    
    # Check results
    voltage_data = results.get_voltage(2)
    
    print(f"Voltage data type: {type(voltage_data)}")
    print(f"Voltage data dtype: {voltage_data.dtype if hasattr(voltage_data, 'dtype') else 'No dtype'}")
    print(f"Is complex: {np.iscomplexobj(voltage_data)}")
    
    if np.iscomplexobj(voltage_data):
        phase = np.angle(voltage_data, deg=True)
        print(f"Phase range: {phase.min():.1f}° to {phase.max():.1f}°")
        print("✅ Complex values working correctly")
    else:
        print("❌ Getting real-only values - AC source configuration issue")
        
    return np.iscomplexobj(voltage_data)

# Run the test
if __name__ == "__main__":
    test_ac_complex_values_targeted()
'''
        
        elif issue_type == "rc_behavior":
            return '''
def test_rc_behavior_targeted():
    """Targeted test for RC filter behavior validation."""
    from circuit_sim import Circuit
    from circuit_sim.simulator import SimulationEngine
    import numpy as np
    
    # Create RC low-pass filter
    circuit = Circuit("RC Behavior Test")
    circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="1V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="1000")  # 1kΩ
    circuit.add_capacitor("C1", node1=2, node2=0, capacitance="1e-6")  # 1μF
    
    # Run AC analysis
    engine = SimulationEngine()
    results = engine.simulate_ac(circuit, 1, 100000, points_per_decade=20)
    
    # Check specific behavior
    frequencies = results.get_frequency_vector()
    voltage_data = results.get_voltage(2)
    
    magnitude_db = 20 * np.log10(np.abs(voltage_data))
    phase_deg = np.angle(voltage_data, deg=True)
    
    # Expected cutoff frequency
    expected_cutoff = 1 / (2 * np.pi * 1000 * 1e-6)  # ~159 Hz
    cutoff_idx = np.argmin(np.abs(frequencies - expected_cutoff))
    
    print(f"Expected cutoff: {expected_cutoff:.1f} Hz")
    print(f"Actual frequency at cutoff index: {frequencies[cutoff_idx]:.1f} Hz")
    print(f"Magnitude at cutoff: {magnitude_db[cutoff_idx]:.1f} dB (should be ~-3 dB)")
    print(f"Phase at cutoff: {phase_deg[cutoff_idx]:.1f}° (should be ~-45°)")
    
    # DC gain
    print(f"DC gain: {magnitude_db[0]:.1f} dB (should be ~0 dB)")
    
    # High frequency attenuation
    print(f"High freq gain: {magnitude_db[-1]:.1f} dB (should be well below 0 dB)")
    
    return True

# Run the test  
if __name__ == "__main__":
    test_rc_behavior_targeted()
'''
        
        elif issue_type == "chart_generation":
            return '''
def test_chart_generation_targeted():
    """Targeted test for chart generation with complex AC data."""
    from circuit_sim import Circuit
    from circuit_sim.simulator import SimulationEngine
    import numpy as np
    import matplotlib.pyplot as plt
    
    # Create circuit and run analysis
    circuit = Circuit("Chart Test")
    circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="1V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="1000")
    circuit.add_capacitor("C1", node1=2, node2=0, capacitance="1e-6")
    
    engine = SimulationEngine()
    results = engine.simulate_ac(circuit, 10, 10000, points_per_decade=20)
    
    # Test chart data extraction
    frequencies = results.get_frequency_vector()
    voltage_data = results.get_voltage(2)
    
    if voltage_data is None or frequencies is None:
        print("❌ Missing data for charting")
        return False
    
    # Test Bode plot generation
    try:
        magnitude_db = 20 * np.log10(np.abs(voltage_data))
        phase_deg = np.angle(voltage_data, deg=True)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
        
        ax1.semilogx(frequencies, magnitude_db)
        ax1.set_ylabel('Magnitude (dB)')
        ax1.set_title('Magnitude Response')
        ax1.grid(True)
        
        ax2.semilogx(frequencies, phase_deg)
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Phase (degrees)')
        ax2.set_title('Phase Response')
        ax2.grid(True)
        
        plt.tight_layout()
        plt.savefig('test_bode_plot.png')
        plt.close()
        
        print("✅ Chart generation successful")
        print(f"Magnitude range: {magnitude_db.min():.1f} to {magnitude_db.max():.1f} dB")
        print(f"Phase range: {phase_deg.min():.1f} to {phase_deg.max():.1f} degrees")
        
        return True
        
    except Exception as e:
        print(f"❌ Chart generation failed: {e}")
        return False

# Run the test
if __name__ == "__main__":
    test_chart_generation_targeted()
'''
        
        else:
            return f'print("Unknown issue type: {issue_type}")'
    
    def suggest_next_steps(self, diagnosis: Dict[str, Any]) -> List[str]:
        """
        Suggest concrete next steps for Claude Code based on diagnosis.
        
        Args:
            diagnosis: Diagnosis results from diagnose_ac_analysis_issue()
            
        Returns:
            List of specific actions Claude Code should take
        """
        
        steps = []
        
        if not diagnosis["issues_found"]:
            steps.extend([
                "✅ No AC analysis issues detected",
                "1. Run comprehensive test suite to ensure all functionality works",
                "2. Consider adding more test cases for edge conditions",
                "3. Update documentation with working examples"
            ])
            return steps
        
        # Prioritize by severity
        critical_issues = [i for i in diagnosis["issues_found"] if i["severity"] == "critical"]
        
        if critical_issues:
            steps.append("🚨 Address critical issues first:")
            
            for i, issue in enumerate(critical_issues, 1):
                steps.append(f"{i}. {issue['description']}")
                steps.append(f"   → Check: {', '.join(issue['files_to_check'])}")
                
                if issue["type"] == "complex_values_missing":
                    steps.extend([
                        "   → Look for voltage source configuration in builder.py",
                        "   → Ensure AC sources use 'DC 0 AC 1' syntax",
                        "   → Verify results are stored as complex numpy arrays"
                    ])
                elif issue["type"] == "physics_validation_failed":
                    steps.extend([
                        "   → Verify component value parsing",
                        "   → Check simulation math against theoretical calculations",
                        "   → Test with known good circuit parameters"
                    ])
        
        # Add testing steps
        steps.extend([
            "",
            "🧪 Immediate testing actions:",
            "1. Run targeted test: python -c \"$(python tests/claude_test_helper.py --generate-test complex_values)\"",
            "2. Generate full AC analysis report: python tests/run_comprehensive_ac_tests.py",
            "3. Compare results with theoretical expectations"
        ])
        
        return steps
    
    def get_test_command_for_claude(self, test_type: str = "quick") -> str:
        """Get the exact command Claude Code should run for testing."""
        
        if test_type == "quick":
            return "python tests/run_comprehensive_ac_tests.py"
        elif test_type == "full":
            return "python tests/run_comprehensive_ac_tests.py --visual --slow"
        elif test_type == "visual_only":
            return "python tests/run_comprehensive_ac_tests.py --visual"
        elif test_type == "pytest_only":
            return "pytest tests/test_ac_analysis_behavior.py -v"
        else:
            return "python tests/claude_test_helper.py --help"


def main():
    """Command line interface for Claude Code."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Claude Code test helper")
    parser.add_argument("--diagnose", action="store_true", help="Diagnose AC analysis issues")
    parser.add_argument("--generate-test", help="Generate targeted test (complex_values, rc_behavior, chart_generation)")
    parser.add_argument("--get-command", help="Get test command (quick, full, visual_only, pytest_only)")
    
    args = parser.parse_args()
    
    helper = ClaudeTestHelper()
    
    if args.diagnose:
        diagnosis = helper.diagnose_ac_analysis_issue()
        print(json.dumps(diagnosis, indent=2))
        
        steps = helper.suggest_next_steps(diagnosis)
        print("\n" + "=" * 50)
        print("RECOMMENDED NEXT STEPS:")
        print("=" * 50)
        for step in steps:
            print(step)
            
    elif args.generate_test:
        test_code = helper.generate_targeted_test_for_issue(args.generate_test)
        print(test_code)
        
    elif args.get_command:
        command = helper.get_test_command_for_claude(args.get_command)
        print(command)
        
    else:
        print("Claude Code Test Helper")
        print("Usage:")
        print("  --diagnose              : Diagnose AC analysis issues")
        print("  --generate-test TYPE    : Generate targeted test code")
        print("  --get-command TYPE      : Get exact test command to run")


if __name__ == "__main__":
    main()