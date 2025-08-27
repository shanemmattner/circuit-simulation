#!/usr/bin/env python3
"""
Claude Code Visual Testing Framework

This framework generates circuit test cases, creates visual outputs (PNG charts),
and provides structured data for Claude Code to assess simulation correctness.

The system enables Claude Code to:
1. Generate reference circuit behaviors
2. Compare simulation outputs against theory
3. Make intelligent decisions about test results
4. Identify specific failure modes and suggest fixes
"""

import sys
import os
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import json
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

# Add src to path for imports  
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine


@dataclass
class CircuitTestCase:
    """Defines a circuit test case with expected behavior"""
    name: str
    circuit_func: callable
    expected_behavior: Dict[str, Any]
    test_frequencies: Tuple[float, float, int]  # start, stop, points


@dataclass
class TestResult:
    """Results of a circuit test with assessment data for Claude Code"""
    test_name: str
    success: bool
    simulation_data: Dict[str, Any]
    theoretical_data: Dict[str, Any]
    visual_outputs: Dict[str, str]  # paths to generated images
    assessment: Dict[str, Any]
    issues_found: List[str]
    confidence_score: float


class VisualTestGenerator:
    """Generates visual tests and assessment data for Claude Code"""
    
    def __init__(self, output_dir: str = "tests/visual_outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_reference_plots(self, test_case: CircuitTestCase) -> Dict[str, str]:
        """Generate reference plots based on circuit theory"""
        plots = {}
        
        # Generate frequency vector
        start_freq, stop_freq, points = test_case.test_frequencies
        frequencies = np.logspace(np.log10(start_freq), np.log10(stop_freq), points)
        
        behavior = test_case.expected_behavior
        
        if behavior["type"] == "low_pass":
            # RC low-pass filter reference
            R = behavior.get("R", 1000)
            C = behavior.get("C", 1e-6)
            omega = 2 * np.pi * frequencies
            H = 1 / (1 + 1j * omega * R * C)
            
            # Create reference Bode plot
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            
            # Magnitude plot
            magnitude_db = 20 * np.log10(np.abs(H))
            ax1.semilogx(frequencies, magnitude_db, 'b-', linewidth=2, label='Theory')
            ax1.set_ylabel('Magnitude (dB)')
            ax1.grid(True, alpha=0.3)
            ax1.set_title(f'{test_case.name} - Reference Bode Plot')
            
            # Phase plot
            phase_deg = np.angle(H, deg=True)
            ax2.semilogx(frequencies, phase_deg, 'r-', linewidth=2, label='Theory')
            ax2.set_xlabel('Frequency (Hz)')
            ax2.set_ylabel('Phase (°)')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Save reference plot
            ref_path = self.output_dir / f"{test_case.name.replace(' ', '_')}_reference.png"
            plt.savefig(ref_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            plots["reference_bode"] = str(ref_path)
            
        return plots
    
    def run_simulation_test(self, test_case: CircuitTestCase) -> TestResult:
        """Run a complete simulation test with visual output generation"""
        
        try:
            # Create circuit
            circuit = test_case.circuit_func()
            
            # Run simulation
            engine = SimulationEngine()
            start_freq, stop_freq, points = test_case.test_frequencies
            
            ac_results = engine.simulate_ac(
                circuit, 
                start_frequency=start_freq, 
                stop_frequency=stop_freq, 
                points_per_decade=points//20
            )
            
            # Extract simulation data
            frequencies = np.array(ac_results.frequency)
            output_voltage = ac_results.voltage(2)  # Assume node 2 is output
            
            simulation_data = {
                "frequencies": frequencies.tolist(),
                "complex_voltages": [complex(v) for v in output_voltage],
                "magnitude": np.abs(output_voltage).tolist(),
                "phase": np.angle(output_voltage, deg=True).tolist(),
                "is_complex": np.iscomplexobj(output_voltage),
                "has_imaginary": np.any(output_voltage.imag != 0),
            }
            
            # Generate theoretical data for comparison
            behavior = test_case.expected_behavior
            theoretical_data = {}
            
            if behavior["type"] == "low_pass":
                R = behavior.get("R", 1000)
                C = behavior.get("C", 1e-6)
                omega = 2 * np.pi * frequencies
                H_theory = 1 / (1 + 1j * omega * R * C)
                
                theoretical_data = {
                    "magnitude_db": (20 * np.log10(np.abs(H_theory))).tolist(),
                    "phase_deg": np.angle(H_theory, deg=True).tolist(),
                    "cutoff_frequency": 1 / (2 * np.pi * R * C),
                    "expected_rolloff": "20 dB/decade",
                    "expected_phase_range": "0° to -90°"
                }
            
            # Generate visual outputs
            visual_outputs = self.generate_simulation_plots(test_case, frequencies, output_voltage)
            visual_outputs.update(self.generate_reference_plots(test_case))
            
            # Assess results
            assessment = self.assess_simulation_quality(simulation_data, theoretical_data, test_case)
            
            return TestResult(
                test_name=test_case.name,
                success=len(assessment["critical_issues"]) == 0,
                simulation_data=simulation_data,
                theoretical_data=theoretical_data,
                visual_outputs=visual_outputs,
                assessment=assessment,
                issues_found=assessment["critical_issues"] + assessment["warnings"],
                confidence_score=assessment["confidence_score"]
            )
            
        except Exception as e:
            return TestResult(
                test_name=test_case.name,
                success=False,
                simulation_data={},
                theoretical_data={},
                visual_outputs={},
                assessment={"error": str(e)},
                issues_found=[f"Simulation failed: {e}"],
                confidence_score=0.0
            )
    
    def generate_simulation_plots(self, test_case: CircuitTestCase, frequencies: np.ndarray, 
                                voltage: np.ndarray) -> Dict[str, str]:
        """Generate simulation plots for visual inspection"""
        plots = {}
        
        # Create simulation Bode plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        magnitude = np.abs(voltage)
        magnitude_db = 20 * np.log10(np.maximum(magnitude, 1e-12))
        phase = np.angle(voltage, deg=True)
        
        # Magnitude plot
        ax1.semilogx(frequencies, magnitude_db, 'g-', linewidth=2, label='Simulation')
        ax1.set_ylabel('Magnitude (dB)')
        ax1.grid(True, alpha=0.3)
        ax1.set_title(f'{test_case.name} - Simulation Results')
        
        # Phase plot  
        ax2.semilogx(frequencies, phase, 'm-', linewidth=2, label='Simulation')
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Phase (°)')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save simulation plot
        sim_path = self.output_dir / f"{test_case.name.replace(' ', '_')}_simulation.png"
        plt.savefig(sim_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        plots["simulation_bode"] = str(sim_path)
        
        return plots
    
    def assess_simulation_quality(self, sim_data: Dict, theory_data: Dict, 
                                test_case: CircuitTestCase) -> Dict[str, Any]:
        """Assess simulation quality with detailed feedback for Claude Code"""
        
        assessment = {
            "critical_issues": [],
            "warnings": [],
            "recommendations": [],
            "confidence_score": 1.0,
            "physics_validation": {},
            "data_quality": {}
        }
        
        # Check for critical issues
        if not sim_data.get("is_complex", False):
            assessment["critical_issues"].append("AC analysis returned real-only values (should be complex)")
            assessment["confidence_score"] -= 0.5
        
        if not sim_data.get("has_imaginary", False):
            assessment["critical_issues"].append("No imaginary voltage components (missing phase information)")
            assessment["confidence_score"] -= 0.3
        
        # Check phase data quality
        phase_range = max(sim_data["phase"]) - min(sim_data["phase"])
        if phase_range < 1.0:
            assessment["warnings"].append(f"Very small phase variation: {phase_range:.2f}° (reactive circuits should show phase shift)")
            assessment["confidence_score"] -= 0.2
        
        # Physics validation (if we have theory data)
        if theory_data and "magnitude_db" in theory_data:
            sim_mag_db = 20 * np.log10(np.maximum(sim_data["magnitude"], 1e-12))
            theory_mag_db = theory_data["magnitude_db"]
            
            # Compare magnitude accuracy
            if len(sim_mag_db) == len(theory_mag_db):
                mag_error = np.sqrt(np.mean((np.array(sim_mag_db) - np.array(theory_mag_db))**2))
                assessment["physics_validation"]["magnitude_rms_error"] = mag_error
                
                if mag_error > 2.0:
                    assessment["warnings"].append(f"High magnitude error: {mag_error:.2f}dB RMS")
                    assessment["confidence_score"] -= 0.1
            
            # Compare phase accuracy
            if len(sim_data["phase"]) == len(theory_data["phase_deg"]):
                phase_error = np.sqrt(np.mean((np.array(sim_data["phase"]) - np.array(theory_data["phase_deg"]))**2))
                assessment["physics_validation"]["phase_rms_error"] = phase_error
                
                if phase_error > 10.0:
                    assessment["warnings"].append(f"High phase error: {phase_error:.1f}° RMS")
                    assessment["confidence_score"] -= 0.1
        
        # Data quality metrics
        assessment["data_quality"] = {
            "frequency_points": len(sim_data["frequencies"]),
            "magnitude_range": (min(sim_data["magnitude"]), max(sim_data["magnitude"])),
            "phase_range": (min(sim_data["phase"]), max(sim_data["phase"])),
            "has_variation": max(sim_data["magnitude"]) - min(sim_data["magnitude"]) > 0.01,
        }
        
        # Generate recommendations
        if assessment["critical_issues"]:
            assessment["recommendations"].append("Fix AC voltage source configuration in PySpice builder")
            assessment["recommendations"].append("Verify complex number handling in simulation engine")
        
        if phase_range < 10 and test_case.expected_behavior.get("type") in ["low_pass", "high_pass"]:
            assessment["recommendations"].append("Check capacitor/inductor models - reactive components should cause phase shift")
        
        return assessment


def create_standard_test_cases() -> List[CircuitTestCase]:
    """Create standard test cases that catch common simulation issues"""
    
    return [
        CircuitTestCase(
            name="RC Low-Pass Filter",
            circuit_func=lambda: Circuit("RC LPF Test")
                .add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
                .add_resistor("R1", node1=1, node2=2, resistance="1k")
                .add_capacitor("C1", node1=2, node2="gnd", capacitance="1uF"),
            expected_behavior={
                "type": "low_pass",
                "R": 1000,
                "C": 1e-6,
                "cutoff_freq": 159.2,
                "phase_range": (-90, 0),
                "rolloff_rate": 20
            },
            test_frequencies=(1, 10000, 100)
        ),
        
        CircuitTestCase(
            name="Voltage Divider",
            circuit_func=lambda: Circuit("Voltage Divider Test")
                .add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
                .add_resistor("R1", node1=1, node2=2, resistance="1k")  
                .add_resistor("R2", node1=2, node2="gnd", resistance="1k"),
            expected_behavior={
                "type": "flat_response",
                "expected_magnitude": 0.5,  # Half voltage
                "expected_db": -6.02,
                "phase_range": (-5, 5),  # Should be nearly 0°
                "tolerance": 0.01
            },
            test_frequencies=(1, 1000, 50)
        ),
        
        CircuitTestCase(
            name="RL High-Pass Equivalent",
            circuit_func=lambda: Circuit("RL HPF Test")
                .add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
                .add_inductor("L1", node1=1, node2=2, inductance="10mH")
                .add_resistor("R1", node1=2, node2="gnd", resistance="100"),
            expected_behavior={
                "type": "high_pass",
                "L": 10e-3,
                "R": 100,
                "cutoff_freq": 1592,  # R/(2πL)
                "phase_range": (0, 90),
                "rolloff_rate": 20
            },
            test_frequencies=(100, 100000, 100)
        ),
    ]


def run_comprehensive_visual_tests() -> List[TestResult]:
    """Run all visual tests and generate assessment data for Claude Code"""
    print("🧪 Running Comprehensive Visual Tests for Claude Code")
    print("=" * 60)
    
    test_cases = create_standard_test_cases()
    tester = VisualTestGenerator()
    results = []
    
    for test_case in test_cases:
        print(f"\n🔬 Testing: {test_case.name}")
        print("-" * 40)
        
        result = tester.run_simulation_test(test_case)
        results.append(result)
        
        # Print assessment for immediate feedback
        print(f"   Status: {'✅ PASS' if result.success else '❌ FAIL'}")
        print(f"   Confidence: {result.confidence_score:.1%}")
        
        if result.issues_found:
            print(f"   Issues ({len(result.issues_found)}):")
            for issue in result.issues_found[:3]:  # Show first 3
                print(f"     • {issue}")
            if len(result.issues_found) > 3:
                print(f"     ... and {len(result.issues_found) - 3} more")
        
        # Show generated visuals
        if result.visual_outputs:
            print(f"   Generated visuals:")
            for name, path in result.visual_outputs.items():
                print(f"     📊 {name}: {path}")
    
    return results


def generate_claude_assessment_report(test_results: List[TestResult]) -> str:
    """Generate structured report for Claude Code to assess overall simulation health"""
    
    timestamp = datetime.now().isoformat()
    
    # Overall statistics
    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results if r.success)
    avg_confidence = np.mean([r.confidence_score for r in test_results])
    
    # Collect all issues
    all_issues = []
    for result in test_results:
        all_issues.extend(result.issues_found)
    
    # Categorize issues
    critical_keywords = ["real-only", "missing phase", "failed", "complex"]
    warning_keywords = ["variation", "error", "accuracy"]
    
    critical_issues = [issue for issue in all_issues if any(kw in issue.lower() for kw in critical_keywords)]
    warning_issues = [issue for issue in all_issues if any(kw in issue.lower() for kw in warning_keywords)]
    
    # Generate Claude-friendly report
    report = f"""# Circuit Simulation Quality Assessment Report

**Generated**: {timestamp}
**Test Suite**: AC Analysis & Circuit Physics Validation

## 🎯 Executive Summary

- **Overall Health**: {passed_tests}/{total_tests} tests passing ({passed_tests/total_tests:.1%})
- **Confidence Level**: {avg_confidence:.1%}
- **Critical Issues**: {len(critical_issues)} detected
- **Warnings**: {len(warning_issues)} detected

## 🚨 Critical Issues Found

"""
    
    if critical_issues:
        for i, issue in enumerate(critical_issues, 1):
            report += f"{i}. {issue}\n"
    else:
        report += "✅ No critical issues detected\n"
    
    report += f"""
## ⚠️ Warnings

"""
    
    if warning_issues:
        for i, issue in enumerate(warning_issues, 1):
            report += f"{i}. {issue}\n"
    else:
        report += "✅ No warnings\n"
    
    report += f"""
## 📊 Detailed Test Results

"""
    
    for result in test_results:
        status_icon = "✅" if result.success else "❌"
        report += f"### {status_icon} {result.test_name}\n"
        report += f"- **Confidence**: {result.confidence_score:.1%}\n"
        
        if result.visual_outputs:
            report += f"- **Visual Outputs**:\n"
            for name, path in result.visual_outputs.items():
                report += f"  - {name}: `{path}`\n"
        
        if result.assessment and "physics_validation" in result.assessment:
            physics = result.assessment["physics_validation"]
            if physics:
                report += f"- **Physics Validation**:\n"
                for key, value in physics.items():
                    report += f"  - {key}: {value}\n"
        
        report += "\n"
    
    # Claude Code action recommendations
    report += f"""
## 🤖 Recommendations for Claude Code

### Immediate Actions
"""
    
    if critical_issues:
        report += f"""
1. **Fix AC Analysis**: The simulation engine is returning real-only values instead of complex values
   - **File to fix**: `src/circuit_sim/simulator/builder.py` (AC voltage source configuration)  
   - **Expected**: Complex voltages with magnitude AND phase information
   - **Current**: Real voltages with zero phase everywhere

2. **Validate Fix**: After fixing, re-run tests to verify complex values are returned
   - **Command**: `python tests/claude_visual_tester.py`
"""
    else:
        report += "✅ No immediate actions required - simulation engine appears healthy\n"
    
    report += f"""
### Testing Strategy
- **Run tests after any changes** to AC analysis or chart generation
- **Visual plots generated** for manual inspection if needed
- **Physics-based validation** ensures circuits behave according to theory
- **Auto-detection** prevents regression of these specific issues

### Files Generated for Review
"""
    
    # List all generated visual outputs
    all_visual_files = []
    for result in test_results:
        all_visual_files.extend(result.visual_outputs.values())
    
    for file_path in sorted(set(all_visual_files)):
        report += f"- {file_path}\n"
    
    return report


def main():
    """Main testing function"""
    # Run comprehensive tests
    test_results = run_comprehensive_visual_tests()
    
    # Generate assessment report
    claude_report = generate_claude_assessment_report(test_results)
    
    # Save report
    report_path = Path("tests") / "claude_assessment_report.md"
    with open(report_path, 'w') as f:
        f.write(claude_report)
    
    print(f"\n📋 Claude Code Assessment Report: {report_path}")
    
    # Save JSON data for programmatic access
    json_data = {
        "timestamp": datetime.now().isoformat(),
        "test_results": [
            {
                "name": r.test_name,
                "success": r.success,
                "confidence": r.confidence_score,
                "issues": r.issues_found,
                "visual_outputs": r.visual_outputs,
                "assessment": r.assessment
            }
            for r in test_results
        ]
    }
    
    json_path = Path("tests") / "test_results.json"
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"📊 Test Data (JSON): {json_path}")
    
    # Summary for immediate action
    critical_count = sum(len(r.issues_found) for r in test_results if not r.success)
    if critical_count > 0:
        print(f"\n🚨 {critical_count} critical issues detected!")
        print(f"📋 Review the assessment report for specific fixes needed")
    else:
        print(f"\n✅ All tests passing - simulation engine appears healthy")


if __name__ == "__main__":
    main()