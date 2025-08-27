"""
Robust Visual Testing Framework for Circuit Simulation

This framework provides comprehensive testing for circuit behavior validation,
visual chart comparison, and physics-based verification specifically designed
to work with Claude Code for intelligent test assessment.

Key Features:
- Visual PNG comparison with intelligent diff analysis
- Circuit behavior validation against theoretical expectations
- AC analysis complex value verification (catches real-only bugs)
- Reference signal generation from known circuit theory
- Claude Code friendly assessment functions
"""

import os
import sys
import json
import hashlib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Configure matplotlib for headless operation
matplotlib.use('Agg')

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine
from circuit_sim.simulator.results import SimulationResults


@dataclass
class CircuitBehaviorExpectation:
    """Defines expected behavior for a circuit type."""
    
    circuit_type: str  # "rc_lowpass", "rc_highpass", "rlc_bandpass", etc.
    frequency_response: Dict[str, float]  # frequency -> expected_magnitude_db
    phase_response: Dict[str, float]     # frequency -> expected_phase_degrees
    dc_values: Dict[str, float]          # node/branch -> expected_dc_value
    transient_characteristics: Dict[str, Any]  # time_constant, rise_time, etc.
    tolerance_magnitude_db: float = 1.0  # ±1dB tolerance
    tolerance_phase_deg: float = 5.0     # ±5° tolerance
    tolerance_dc_percent: float = 5.0    # ±5% tolerance


@dataclass 
class VisualTestResult:
    """Result of a visual/behavioral test."""
    
    test_name: str
    passed: bool
    score: float  # 0.0 to 1.0
    issues: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]
    reference_file: Optional[str] = None
    actual_file: Optional[str] = None
    
    def claude_assessment(self) -> str:
        """Generate Claude Code friendly assessment."""
        status = "✅ PASS" if self.passed else "❌ FAIL"
        
        assessment = f"{status} {self.test_name} (Score: {self.score:.1%})\n"
        
        if self.issues:
            assessment += "Issues found:\n"
            for issue in self.issues:
                assessment += f"  • {issue}\n"
        
        if self.warnings:
            assessment += "Warnings:\n"
            for warning in self.warnings:
                assessment += f"  ⚠️ {warning}\n"
        
        if self.metadata.get('physics_analysis'):
            assessment += f"Physics Analysis: {self.metadata['physics_analysis']}\n"
            
        return assessment


class ReferenceSignalGenerator:
    """Generates theoretical reference signals for comparison."""
    
    @staticmethod
    def rc_lowpass_response(frequencies: np.ndarray, R: float, C: float) -> Tuple[np.ndarray, np.ndarray]:
        """Generate theoretical frequency response for RC low-pass filter.
        
        Returns:
            (magnitude_db, phase_degrees)
        """
        omega = 2 * np.pi * frequencies
        tau = R * C
        
        # Transfer function: H(jω) = 1 / (1 + jωRC)
        H = 1 / (1 + 1j * omega * tau)
        
        magnitude_db = 20 * np.log10(np.abs(H))
        phase_degrees = np.angle(H, deg=True)
        
        return magnitude_db, phase_degrees
    
    @staticmethod
    def rc_highpass_response(frequencies: np.ndarray, R: float, C: float) -> Tuple[np.ndarray, np.ndarray]:
        """Generate theoretical frequency response for RC high-pass filter."""
        omega = 2 * np.pi * frequencies
        tau = R * C
        
        # Transfer function: H(jω) = jωRC / (1 + jωRC)
        H = (1j * omega * tau) / (1 + 1j * omega * tau)
        
        magnitude_db = 20 * np.log10(np.abs(H))
        phase_degrees = np.angle(H, deg=True)
        
        return magnitude_db, phase_degrees
    
    @staticmethod
    def rlc_bandpass_response(frequencies: np.ndarray, R: float, L: float, C: float) -> Tuple[np.ndarray, np.ndarray]:
        """Generate theoretical frequency response for RLC band-pass filter."""
        omega = 2 * np.pi * frequencies
        
        # Resonant frequency and Q factor
        omega_0 = 1 / np.sqrt(L * C)
        Q = omega_0 * L / R
        
        # Transfer function for series RLC: H(jω) = jωL / (R + jωL + 1/(jωC))
        Z = R + 1j * omega * L + 1 / (1j * omega * C)
        H = (1j * omega * L) / Z
        
        magnitude_db = 20 * np.log10(np.abs(H))
        phase_degrees = np.angle(H, deg=True)
        
        return magnitude_db, phase_degrees


class CircuitBehaviorValidator:
    """Validates circuit behavior against theoretical expectations."""
    
    def __init__(self):
        self.reference_gen = ReferenceSignalGenerator()
        self.logger = logging.getLogger(__name__)
    
    def validate_ac_complex_values(self, ac_results: SimulationResults, node_id: Union[int, str] = 1) -> VisualTestResult:
        """Validate that AC results contain proper complex values (not just real)."""
        issues = []
        warnings = []
        metadata = {}
        
        try:
            # Get voltage data for a specific node
            voltage_data = ac_results.get_voltage(node_id)
            if voltage_data is None:
                return VisualTestResult(
                    test_name="AC Complex Values Validation",
                    passed=False,
                    score=0.0,
                    issues=[f"No voltage data found for node {node_id}"],
                    warnings=[],
                    metadata={}
                )
            
            # Check if values are complex
            if not np.iscomplexobj(voltage_data):
                issues.append("AC voltage data is not complex - should contain both magnitude and phase")
                score = 0.0
            else:
                # Check for non-zero imaginary parts
                imaginary_parts = np.imag(voltage_data)
                non_zero_imaginary = np.count_nonzero(imaginary_parts)
                total_points = len(imaginary_parts)
                
                if non_zero_imaginary == 0:
                    issues.append("All AC voltage values have zero imaginary part - phase information is missing")
                    score = 0.0
                elif non_zero_imaginary < total_points * 0.8:  # Less than 80% have imaginary parts
                    warnings.append(f"Only {non_zero_imaginary}/{total_points} points have non-zero imaginary parts")
                    score = 0.6
                else:
                    score = 1.0
                
                # Add analysis metadata
                metadata['complex_analysis'] = {
                    'total_points': total_points,
                    'non_zero_imaginary': non_zero_imaginary,
                    'magnitude_range': f"{np.abs(voltage_data).min():.6f} to {np.abs(voltage_data).max():.6f}",
                    'phase_range_deg': f"{np.angle(voltage_data, deg=True).min():.1f}° to {np.angle(voltage_data, deg=True).max():.1f}°"
                }
            
        except Exception as e:
            issues.append(f"Exception during complex value validation: {str(e)}")
            score = 0.0
        
        return VisualTestResult(
            test_name="AC Complex Values Validation",
            passed=len(issues) == 0,
            score=score,
            issues=issues,
            warnings=warnings,
            metadata=metadata
        )
    
    def validate_rc_lowpass_behavior(self, circuit: Circuit, ac_results: SimulationResults, 
                                   R_ohms: float, C_farads: float, input_node: int = 1, output_node: int = 2) -> VisualTestResult:
        """Validate RC low-pass filter behavior against theoretical expectations."""
        issues = []
        warnings = []
        metadata = {}
        
        try:
            # Get simulation data
            frequencies = ac_results.get_frequency_vector()
            output_voltage = ac_results.get_voltage(output_node)
            
            if output_voltage is None or frequencies is None:
                return VisualTestResult(
                    test_name="RC Low-pass Filter Validation",
                    passed=False,
                    score=0.0,
                    issues=["Missing frequency or voltage data"],
                    warnings=[],
                    metadata={}
                )
            
            # Generate theoretical response
            theoretical_mag, theoretical_phase = self.reference_gen.rc_lowpass_response(
                frequencies, R_ohms, C_farads
            )
            
            # Calculate actual response
            actual_mag_db = 20 * np.log10(np.abs(output_voltage))
            actual_phase_deg = np.angle(output_voltage, deg=True)
            
            # Validate behavior characteristics
            cutoff_freq = 1 / (2 * np.pi * R_ohms * C_farads)
            
            # Find indices closest to key frequencies
            dc_idx = 0  # Lowest frequency
            cutoff_idx = np.argmin(np.abs(frequencies - cutoff_freq))
            high_freq_idx = -1  # Highest frequency
            
            score_components = []
            
            # 1. DC gain should be near 0 dB
            dc_gain_actual = actual_mag_db[dc_idx]
            dc_gain_expected = theoretical_mag[dc_idx]
            if abs(dc_gain_actual - dc_gain_expected) > 1.0:  # 1 dB tolerance
                issues.append(f"DC gain deviation: {dc_gain_actual:.1f} dB (expected ~{dc_gain_expected:.1f} dB)")
                score_components.append(0.0)
            else:
                score_components.append(1.0)
            
            # 2. Cutoff frequency should be -3dB
            cutoff_gain_actual = actual_mag_db[cutoff_idx]
            cutoff_gain_expected = theoretical_mag[cutoff_idx]
            if abs(cutoff_gain_actual - cutoff_gain_expected) > 1.0:
                issues.append(f"Cutoff gain: {cutoff_gain_actual:.1f} dB (expected ~{cutoff_gain_expected:.1f} dB)")
                score_components.append(0.0)
            else:
                score_components.append(1.0)
            
            # 3. High frequency rolloff should show proper attenuation
            high_freq_gain_actual = actual_mag_db[high_freq_idx]
            high_freq_gain_expected = theoretical_mag[high_freq_idx]
            if abs(high_freq_gain_actual - high_freq_gain_expected) > 3.0:  # 3 dB tolerance at high freq
                issues.append(f"High frequency attenuation: {high_freq_gain_actual:.1f} dB (expected ~{high_freq_gain_expected:.1f} dB)")
                score_components.append(0.0)
            else:
                score_components.append(1.0)
            
            # 4. Phase behavior validation
            dc_phase_actual = actual_phase_deg[dc_idx]
            cutoff_phase_actual = actual_phase_deg[cutoff_idx]
            high_freq_phase_actual = actual_phase_deg[high_freq_idx]
            
            # Low-pass filter should have phase from 0° to -90°
            if abs(dc_phase_actual) > 10:  # DC phase should be near 0°
                issues.append(f"DC phase: {dc_phase_actual:.1f}° (expected ~0°)")
                score_components.append(0.0)
            else:
                score_components.append(1.0)
            
            if abs(cutoff_phase_actual - (-45)) > 10:  # Cutoff should be near -45°
                issues.append(f"Cutoff phase: {cutoff_phase_actual:.1f}° (expected ~-45°)")
                score_components.append(0.0)
            else:
                score_components.append(1.0)
            
            if abs(high_freq_phase_actual - (-90)) > 15:  # High freq should approach -90°
                warnings.append(f"High frequency phase: {high_freq_phase_actual:.1f}° (expected ~-90°)")
                score_components.append(0.7)
            else:
                score_components.append(1.0)
            
            # Calculate overall score
            score = np.mean(score_components)
            
            # Metadata for Claude Code analysis
            metadata['physics_analysis'] = {
                'circuit_type': 'RC Low-pass Filter',
                'cutoff_frequency_hz': cutoff_freq,
                'dc_gain_db': dc_gain_actual,
                'cutoff_gain_db': cutoff_gain_actual,
                'high_freq_gain_db': high_freq_gain_actual,
                'phase_at_dc': dc_phase_actual,
                'phase_at_cutoff': cutoff_phase_actual,
                'phase_at_high_freq': high_freq_phase_actual,
                'theoretical_vs_actual_correlation': np.corrcoef(theoretical_mag, actual_mag_db)[0, 1]
            }
            
        except Exception as e:
            issues.append(f"Exception during RC low-pass validation: {str(e)}")
            score = 0.0
        
        return VisualTestResult(
            test_name="RC Low-pass Filter Validation",
            passed=len(issues) == 0,
            score=score,
            issues=issues,
            warnings=warnings,
            metadata=metadata
        )


class VisualTestFramework:
    """Main framework for visual and behavioral testing."""
    
    def __init__(self, test_output_dir: str = "tests/visual_output"):
        self.output_dir = Path(test_output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.references_dir = self.output_dir / "references"
        self.references_dir.mkdir(exist_ok=True)
        
        self.actuals_dir = self.output_dir / "actuals"
        self.actuals_dir.mkdir(exist_ok=True)
        
        self.diffs_dir = self.output_dir / "diffs"
        self.diffs_dir.mkdir(exist_ok=True)
        
        self.validator = CircuitBehaviorValidator()
        self.engine = SimulationEngine()
        
        self.logger = logging.getLogger(__name__)
        
    def generate_reference_bode_plot(self, circuit_type: str, frequencies: np.ndarray,
                                   magnitude_db: np.ndarray, phase_deg: np.ndarray,
                                   title: str = "Reference Bode Plot") -> str:
        """Generate reference Bode plot PNG for comparison."""
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Magnitude plot
        ax1.semilogx(frequencies, magnitude_db, 'b-', linewidth=2, label='Magnitude')
        ax1.set_ylabel('Magnitude (dB)')
        ax1.set_title(f'{title} - Magnitude Response')
        ax1.grid(True, which="both", ls="-", alpha=0.3)
        ax1.legend()
        
        # Phase plot  
        ax2.semilogx(frequencies, phase_deg, 'r-', linewidth=2, label='Phase')
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Phase (degrees)')
        ax2.set_title(f'{title} - Phase Response')
        ax2.grid(True, which="both", ls="-", alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        
        # Save reference plot
        filename = f"reference_{circuit_type}_bode.png"
        filepath = self.references_dir / filename
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close()
        
        return str(filepath)
    
    def generate_actual_bode_plot(self, circuit_name: str, ac_results: SimulationResults,
                                 node_id: Union[int, str] = 2, title: str = "Actual Bode Plot") -> str:
        """Generate actual Bode plot from simulation results."""
        
        frequencies = ac_results.get_frequency_vector()
        voltage_data = ac_results.get_voltage(node_id)
        
        if frequencies is None or voltage_data is None:
            raise ValueError(f"Missing frequency or voltage data for node {node_id}")
        
        magnitude_db = 20 * np.log10(np.abs(voltage_data))
        phase_deg = np.angle(voltage_data, deg=True)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Magnitude plot
        ax1.semilogx(frequencies, magnitude_db, 'b-', linewidth=2, label='Magnitude')
        ax1.set_ylabel('Magnitude (dB)')
        ax1.set_title(f'{title} - Magnitude Response')
        ax1.grid(True, which="both", ls="-", alpha=0.3)
        ax1.legend()
        
        # Phase plot
        ax2.semilogx(frequencies, phase_deg, 'r-', linewidth=2, label='Phase')
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Phase (degrees)')
        ax2.set_title(f'{title} - Phase Response')
        ax2.grid(True, which="both", ls="-", alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        
        # Save actual plot
        filename = f"actual_{circuit_name}_bode.png"
        filepath = self.actuals_dir / filename
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close()
        
        return str(filepath)
    
    def compare_bode_plots(self, reference_path: str, actual_path: str, circuit_name: str) -> VisualTestResult:
        """Compare reference and actual Bode plots using image analysis."""
        
        try:
            from PIL import Image
            import numpy as np
            
            # Load images
            ref_img = np.array(Image.open(reference_path))
            actual_img = np.array(Image.open(actual_path))
            
            # Basic image comparison
            if ref_img.shape != actual_img.shape:
                return VisualTestResult(
                    test_name=f"Bode Plot Comparison ({circuit_name})",
                    passed=False,
                    score=0.0,
                    issues=["Image dimensions don't match"],
                    warnings=[],
                    metadata={},
                    reference_file=reference_path,
                    actual_file=actual_path
                )
            
            # Calculate difference metrics
            diff = np.abs(ref_img.astype(float) - actual_img.astype(float))
            mean_diff = np.mean(diff)
            max_diff = np.max(diff)
            
            # Create difference image
            diff_img = np.clip(diff * 3, 0, 255).astype(np.uint8)  # Amplify differences
            diff_path = self.diffs_dir / f"diff_{circuit_name}_bode.png"
            Image.fromarray(diff_img).save(diff_path)
            
            # Score based on similarity
            similarity = 1.0 - (mean_diff / 255.0)
            
            issues = []
            warnings = []
            
            if similarity < 0.8:
                issues.append(f"Low visual similarity: {similarity:.1%}")
            elif similarity < 0.9:
                warnings.append(f"Moderate visual differences: {similarity:.1%}")
            
            metadata = {
                'similarity_score': similarity,
                'mean_pixel_diff': mean_diff,
                'max_pixel_diff': max_diff,
                'diff_image_path': str(diff_path)
            }
            
            return VisualTestResult(
                test_name=f"Bode Plot Comparison ({circuit_name})",
                passed=similarity >= 0.8,
                score=similarity,
                issues=issues,
                warnings=warnings,
                metadata=metadata,
                reference_file=reference_path,
                actual_file=actual_path
            )
            
        except ImportError:
            return VisualTestResult(
                test_name=f"Bode Plot Comparison ({circuit_name})",
                passed=False,
                score=0.0,
                issues=["PIL (Pillow) not installed - cannot perform image comparison"],
                warnings=["Install Pillow with: pip install pillow"],
                metadata={}
            )
        except Exception as e:
            return VisualTestResult(
                test_name=f"Bode Plot Comparison ({circuit_name})",
                passed=False,
                score=0.0,
                issues=[f"Exception during image comparison: {str(e)}"],
                warnings=[],
                metadata={}
            )
    
    def test_rc_lowpass_circuit_comprehensive(self, R_ohms: float = 1000, C_farads: float = 1e-6) -> List[VisualTestResult]:
        """Comprehensive test of RC low-pass filter including AC analysis complex value validation."""
        
        results = []
        
        # Create RC low-pass filter circuit
        circuit = Circuit("RC Low-pass Filter Test")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="1V")  # AC source will be configured by builder
        circuit.add_resistor("R1", node1=1, node2=2, resistance=f"{R_ohms}")
        circuit.add_capacitor("C1", node1=2, node2=0, capacitance=f"{C_farads}")
        
        try:
            # Run AC analysis
            ac_results = self.engine.simulate_ac(
                circuit,
                start_frequency=1,
                stop_frequency=100000,
                points_per_decade=20
            )
            
            # Test 1: Validate complex values
            complex_test = self.validator.validate_ac_complex_values(ac_results, node_id=2)
            results.append(complex_test)
            
            # Test 2: Validate RC low-pass behavior
            behavior_test = self.validator.validate_rc_lowpass_behavior(
                circuit, ac_results, R_ohms, C_farads, input_node=1, output_node=2
            )
            results.append(behavior_test)
            
            # Test 3: Generate and compare visual plots
            frequencies = ac_results.get_frequency_vector()
            
            # Generate theoretical reference
            ref_mag, ref_phase = ReferenceSignalGenerator.rc_lowpass_response(
                frequencies, R_ohms, C_farads
            )
            
            reference_path = self.generate_reference_bode_plot(
                "rc_lowpass", frequencies, ref_mag, ref_phase,
                f"RC Low-pass Reference (R={R_ohms}Ω, C={C_farads*1e6}μF)"
            )
            
            actual_path = self.generate_actual_bode_plot(
                "rc_lowpass", ac_results, 
                node_id=2,
                title=f"RC Low-pass Simulation (R={R_ohms}Ω, C={C_farads*1e6}μF)"
            )
            
            # Compare plots
            visual_test = self.compare_bode_plots(reference_path, actual_path, "rc_lowpass")
            results.append(visual_test)
            
        except Exception as e:
            error_result = VisualTestResult(
                test_name="RC Low-pass Circuit Test",
                passed=False,
                score=0.0,
                issues=[f"Exception during testing: {str(e)}"],
                warnings=[],
                metadata={"exception_type": type(e).__name__}
            )
            results.append(error_result)
        
        return results
    
    def generate_test_report(self, test_results: List[VisualTestResult], report_title: str = "Visual Test Report") -> str:
        """Generate a comprehensive test report for Claude Code analysis."""
        
        report_lines = [
            f"# {report_title}",
            f"Generated: {datetime.now().isoformat()}",
            "",
            "## Summary",
            ""
        ]
        
        total_tests = len(test_results)
        passed_tests = sum(1 for r in test_results if r.passed)
        average_score = np.mean([r.score for r in test_results]) if test_results else 0.0
        
        report_lines.extend([
            f"- Total Tests: {total_tests}",
            f"- Passed: {passed_tests} ({passed_tests/max(1,total_tests)*100:.1f}%)",
            f"- Average Score: {average_score:.1%}",
            ""
        ])
        
        # Detailed results
        report_lines.extend([
            "## Detailed Results",
            ""
        ])
        
        for i, result in enumerate(test_results, 1):
            report_lines.extend([
                f"### Test {i}: {result.test_name}",
                "",
                result.claude_assessment(),
                ""
            ])
            
            if result.reference_file or result.actual_file:
                report_lines.append("Files:")
                if result.reference_file:
                    report_lines.append(f"  - Reference: {result.reference_file}")
                if result.actual_file:
                    report_lines.append(f"  - Actual: {result.actual_file}")
                report_lines.append("")
            
            if result.metadata:
                report_lines.extend([
                    "Metadata:",
                    json.dumps(result.metadata, indent=2),
                    ""
                ])
        
        # Critical issues summary for Claude Code
        critical_issues = []
        for result in test_results:
            if not result.passed and "complex" in result.test_name.lower():
                critical_issues.append("❌ CRITICAL: AC analysis returning real-only values - phase information missing")
            elif not result.passed and "behavior" in result.test_name.lower():
                critical_issues.append("❌ CRITICAL: Circuit behavior doesn't match theoretical expectations")
            elif not result.passed and "visual" in result.test_name.lower():
                critical_issues.append("❌ WARNING: Visual plots don't match reference - check chart generation")
        
        if critical_issues:
            report_lines.extend([
                "## Critical Issues for Investigation",
                ""
            ])
            report_lines.extend(critical_issues)
            report_lines.append("")
        
        # Recommendations for Claude Code
        report_lines.extend([
            "## Recommendations for Claude Code",
            "",
            "### If AC Complex Values Test Failed:",
            "- Check PySpice AC source configuration in builder.py",
            "- Verify AC analysis is returning complex numpy arrays",
            "- Ensure voltage sources have proper 'DC 0 AC 1' syntax",
            "",
            "### If Behavior Validation Failed:", 
            "- Verify component values are parsed correctly",
            "- Check frequency vector generation",
            "- Compare theoretical calculations with simulation math",
            "",
            "### If Visual Comparison Failed:",
            "- Inspect generated plots for missing data",
            "- Check chart axes and scaling",
            "- Verify Plotly/matplotlib chart generation pipeline",
            ""
        ])
        
        return "\n".join(report_lines)


# Example usage and test suite
def run_ac_analysis_regression_tests() -> List[VisualTestResult]:
    """Run comprehensive AC analysis regression tests."""
    
    framework = VisualTestFramework()
    all_results = []
    
    print("🔬 Running AC Analysis Regression Tests")
    print("=" * 50)
    
    # Test 1: RC Low-pass Filter
    print("Testing RC Low-pass Filter...")
    rc_results = framework.test_rc_lowpass_circuit_comprehensive(R_ohms=1000, C_farads=1e-6)
    all_results.extend(rc_results)
    
    # Generate comprehensive report
    report = framework.generate_test_report(all_results, "AC Analysis Regression Test Report")
    
    # Save report
    report_file = framework.output_dir / "ac_regression_test_report.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\n📊 Test Report saved to: {report_file}")
    
    # Print summary for immediate feedback
    passed = sum(1 for r in all_results if r.passed)
    total = len(all_results)
    print(f"\n✅ Test Summary: {passed}/{total} passed ({passed/max(1,total)*100:.1f}%)")
    
    # Print critical issues
    for result in all_results:
        if not result.passed:
            print(f"❌ {result.test_name}: {', '.join(result.issues)}")
    
    return all_results


if __name__ == "__main__":
    # Run the regression tests
    run_ac_analysis_regression_tests()