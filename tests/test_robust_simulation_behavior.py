#!/usr/bin/env python3
"""
Robust Unit Tests for Simulation Behavior

These tests auto-detect the types of errors we've encountered:
1. AC analysis returning real-only values (should be complex)
2. Bode plots showing flat lines when they should show rolloff
3. Phase plots showing zeros when they should show shifts
4. Chart generation issues with incorrect data rendering

This framework prevents regression and catches physics violations automatically.
"""

import pytest
import numpy as np
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
import tempfile
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine
from circuit_sim.reports import ReportGenerator


class CircuitBehaviorValidator:
    """Validates that circuit simulations behave according to circuit theory"""
    
    @staticmethod
    def validate_rc_lowpass_theory(frequencies: np.ndarray, output_voltage: np.ndarray, 
                                  R: float, C: float) -> Dict[str, Any]:
        """Validate RC low-pass filter against theoretical transfer function"""
        # Theoretical transfer function: H(jw) = 1 / (1 + jwRC)
        omega = 2 * np.pi * frequencies
        H_theory = 1 / (1 + 1j * omega * R * C)
        
        mag_theory = np.abs(H_theory)
        phase_theory = np.angle(H_theory, deg=True)
        
        # Compare simulation vs theory
        mag_sim = np.abs(output_voltage)
        phase_sim = np.angle(output_voltage, deg=True)
        
        # Calculate errors
        mag_error_rms = np.sqrt(np.mean((mag_sim - mag_theory)**2))
        phase_error_rms = np.sqrt(np.mean((phase_sim - phase_theory)**2))
        
        # Validate key characteristics
        cutoff_freq = 1 / (2 * np.pi * R * C)
        cutoff_idx = np.argmin(np.abs(frequencies - cutoff_freq))
        
        results = {
            "mag_error_rms": mag_error_rms,
            "phase_error_rms": phase_error_rms,
            "cutoff_magnitude": mag_sim[cutoff_idx],
            "cutoff_phase": phase_sim[cutoff_idx],
            "expected_cutoff_mag": mag_theory[cutoff_idx],
            "expected_cutoff_phase": phase_theory[cutoff_idx],
            "has_rolloff": mag_sim[-1] < mag_sim[0] * 0.1,  # At least 20dB rolloff
            "has_phase_shift": abs(phase_sim[-1] - phase_sim[0]) > 10,  # At least 10° shift
            "is_monotonic_mag": np.all(np.diff(mag_sim) <= 0.001),  # Magnitude decreases (mostly)
        }
        
        return results
    
    @staticmethod
    def validate_complex_ac_data(voltage_data: np.ndarray) -> Dict[str, Any]:
        """Validate that AC analysis returns proper complex data"""
        return {
            "is_complex_array": np.iscomplexobj(voltage_data),
            "dtype": str(voltage_data.dtype),
            "has_imaginary_parts": np.any(voltage_data.imag != 0),
            "max_imaginary": np.abs(voltage_data.imag).max(),
            "real_part_range": (voltage_data.real.min(), voltage_data.real.max()),
            "imag_part_range": (voltage_data.imag.min(), voltage_data.imag.max()),
        }


class TestACAnalysisBehavior:
    """Test AC analysis for correct complex number handling and physics"""
    
    def test_ac_returns_complex_values(self):
        """CRITICAL: AC analysis must return complex values, not just real"""
        circuit = Circuit("RC Filter Complex Test")
        circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        circuit.add_capacitor("C1", node1=2, node2="gnd", capacitance="1uF")
        
        engine = SimulationEngine()
        results = engine.simulate_ac(circuit, start_frequency=1, stop_frequency=10000, points_per_decade=10)
        
        # Check output node (should have phase shift)
        output_voltage = results.voltage(2)
        
        assert output_voltage is not None, "No voltage data for output node"
        
        validation = CircuitBehaviorValidator.validate_complex_ac_data(output_voltage)
        
        # CRITICAL CHECKS
        assert validation["is_complex_array"], "AC analysis must return complex array"
        assert "complex" in validation["dtype"], f"Expected complex dtype, got {validation['dtype']}"
        
        # For RC filter, should have imaginary components (phase shift)
        assert validation["has_imaginary_parts"], "RC filter should have imaginary voltage components"
        assert validation["max_imaginary"] > 1e-10, f"Imaginary parts too small: {validation['max_imaginary']}"
    
    def test_rc_filter_physics_validation(self):
        """Validate RC filter follows theoretical behavior"""
        R = 1000  # 1k ohm
        C = 1e-6  # 1uF
        
        circuit = Circuit("RC Physics Test")
        circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        circuit.add_capacitor("C1", node1=2, node2="gnd", capacitance="1uF")
        
        engine = SimulationEngine()
        results = engine.simulate_ac(circuit, start_frequency=1, stop_frequency=100000, points_per_decade=30)
        
        frequencies = np.array(results.frequency)
        output_voltage = results.voltage(2)
        
        validation = CircuitBehaviorValidator.validate_rc_lowpass_theory(
            frequencies, output_voltage, R, C
        )
        
        # Physics-based assertions
        assert validation["has_rolloff"], "RC filter must show magnitude rolloff at high frequencies"
        assert validation["has_phase_shift"], "RC filter must show phase shift (0° to -90°)"
        
        # Cutoff frequency behavior (should be -3dB point)
        expected_cutoff_mag = 1 / np.sqrt(2)  # 0.707 (-3dB)
        cutoff_error = abs(validation["cutoff_magnitude"] - expected_cutoff_mag)
        assert cutoff_error < 0.1, f"Cutoff magnitude error too large: {cutoff_error:.3f}"
        
        # Overall accuracy
        assert validation["mag_error_rms"] < 0.05, f"Magnitude accuracy poor: {validation['mag_error_rms']:.3f}"
        assert validation["phase_error_rms"] < 10, f"Phase accuracy poor: {validation['phase_error_rms']:.1f}°"
    
    def test_voltage_divider_ac_behavior(self):
        """Voltage divider should be flat at -6dB across all frequencies"""
        circuit = Circuit("Voltage Divider AC Test")
        circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")  # 1V AC for testing
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        circuit.add_resistor("R2", node1=2, node2="gnd", resistance="1k")
        
        engine = SimulationEngine()
        results = engine.simulate_ac(circuit, start_frequency=1, stop_frequency=10000, points_per_decade=10)
        
        output_voltage = results.voltage(2)
        magnitude = np.abs(output_voltage)
        
        # Should be flat at 0.5V (= -6.02dB) across all frequencies
        expected_magnitude = 0.5
        magnitude_variation = magnitude.max() - magnitude.min()
        
        assert magnitude_variation < 0.01, f"Voltage divider too much variation: {magnitude_variation:.6f}"
        assert abs(magnitude[0] - expected_magnitude) < 0.01, f"Incorrect voltage division: {magnitude[0]:.6f} vs {expected_magnitude}"
    
    def test_rlc_resonance_detection(self):
        """RLC circuit should show resonance peak"""
        circuit = Circuit("RLC Resonance Test")
        circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="10")
        circuit.add_inductor("L1", node1=2, node2=3, inductance="1mH")
        circuit.add_capacitor("C1", node1=3, node2="gnd", capacitance="10nF")
        
        # Expected resonant frequency
        L = 1e-3
        C = 10e-9
        f_res = 1 / (2 * np.pi * np.sqrt(L * C))
        
        engine = SimulationEngine()
        results = engine.simulate_ac(circuit, start_frequency=100, stop_frequency=100000, points_per_decade=50)
        
        output_voltage = results.voltage(3)
        magnitude = np.abs(output_voltage)
        frequencies = np.array(results.frequency)
        
        # Find resonance peak
        peak_idx = np.argmax(magnitude)
        peak_frequency = frequencies[peak_idx]
        peak_magnitude = magnitude[peak_idx]
        
        # Validate resonance behavior
        freq_error = abs(peak_frequency - f_res) / f_res
        assert freq_error < 0.2, f"Resonant frequency error too large: {freq_error:.3f} ({peak_frequency:.0f} vs {f_res:.0f} Hz)"
        
        # Should have clear peak (Q > 1)
        low_freq_mag = magnitude[0]
        assert peak_magnitude > low_freq_mag * 1.5, f"Resonance peak not prominent: {peak_magnitude:.3f} vs {low_freq_mag:.3f}"


class TestChartGenerationRobustness:
    """Test chart generation for correct data handling"""
    
    def test_bode_plots_contain_real_data(self):
        """Bode plots must contain varying data, not flat lines or zeros"""
        circuit = Circuit("Chart Data Test")
        circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        circuit.add_capacitor("C1", node1=2, node2="gnd", capacitance="1uF")
        
        engine = SimulationEngine()
        results = engine.simulate_ac(circuit, start_frequency=1, stop_frequency=10000, points_per_decade=20)
        
        # Generate chart
        from circuit_sim.reports.charts.plotly_charts import PlotlyChartGenerator
        chart_gen = PlotlyChartGenerator()
        charts = chart_gen.create_charts(results, circuit)
        
        assert len(charts) > 0, "No charts generated"
        
        # Check each chart for real data
        for chart_name, chart_fig in charts.items():
            assert hasattr(chart_fig, 'data'), f"Chart {chart_name} has no data attribute"
            
            for i, trace in enumerate(chart_fig.data):
                if hasattr(trace, 'y'):
                    y_data = np.array(trace.y)
                    
                    # Check for problematic patterns
                    assert not np.all(y_data == 0), f"Chart {chart_name} trace {i} is all zeros"
                    assert not np.all(y_data == y_data[0]), f"Chart {chart_name} trace {i} is flat line at {y_data[0]}"
                    
                    # For AC magnitude plots, should see rolloff
                    if "magnitude" in trace.name.lower() and "node 2" in str(trace.name).lower():
                        data_range = y_data.max() - y_data.min()
                        assert data_range > 10, f"Insufficient magnitude rolloff in {chart_name}: {data_range:.1f}dB"
    
    def test_phase_plots_for_reactive_circuits(self):
        """Phase plots for reactive circuits must show non-zero phase shift"""
        test_circuits = [
            ("RC Filter", lambda: Circuit("RC Test")
                .add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
                .add_resistor("R1", node1=1, node2=2, resistance="1k")
                .add_capacitor("C1", node1=2, node2="gnd", capacitance="1uF")),
            
            ("RL Circuit", lambda: Circuit("RL Test")
                .add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
                .add_resistor("R1", node1=1, node2=2, resistance="100")
                .add_inductor("L1", node1=2, node2="gnd", inductance="10mH")),
        ]
        
        for circuit_name, circuit_func in test_circuits:
            circuit = circuit_func()
            engine = SimulationEngine()
            results = engine.simulate_ac(circuit, start_frequency=1, stop_frequency=10000, points_per_decade=20)
            
            # Check that output node has complex values
            output_voltage = results.voltage(2)
            assert np.iscomplexobj(output_voltage), f"{circuit_name}: AC voltage should be complex"
            
            # For reactive circuits, phase should vary significantly
            phase = np.angle(output_voltage, deg=True)
            phase_range = phase.max() - phase.min()
            
            # RC should go from 0° to ~-90°, RL should go from 0° to ~+90°
            assert phase_range > 10, f"{circuit_name}: Insufficient phase shift {phase_range:.1f}° (expected >10°)"


class TestReportQualityAssurance:
    """Test that generated reports meet quality standards"""
    
    def test_reports_contain_interactive_charts(self):
        """All AC reports must contain interactive Plotly charts with real data"""
        circuit = Circuit("Report Quality Test")
        circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        circuit.add_capacitor("C1", node1=2, node2="gnd", capacitance="1uF")
        
        engine = SimulationEngine()
        results = engine.simulate_ac(circuit, start_frequency=1, stop_frequency=10000, points_per_decade=20)
        
        generator = ReportGenerator()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            temp_path = f.name
        
        try:
            report_path = generator.generate_report(
                circuit=circuit,
                results=results,
                report_type="detailed",
                output_format="html",
                output_path=temp_path
            )
            
            assert os.path.exists(report_path), "Report file not created"
            
            # Read and analyze report content
            with open(report_path, 'r') as f:
                content = f.read()
            
            # Quality checks
            assert len(content) > 10000, f"Report too small: {len(content)} chars (expected >10k)"
            assert "Plotly.newPlot" in content, "Report missing Plotly charts"
            assert content.count("Plotly.newPlot") >= 2, f"Too few charts: {content.count('Plotly.newPlot')}"
            
            # Check for error indicators
            assert "No charts available" not in content, "Report shows 'No charts available' error"
            assert "Chart not available" not in content, "Report has chart generation errors"
            
            # Check for real data (not all zeros)
            assert not ('y":[0,0,0' in content and content.count('y":[0,0,0') > 1), "Charts contain zero data"
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_bode_plot_data_integrity(self):
        """Test that Bode plots contain mathematically correct data"""
        # Test multiple circuit types
        test_cases = [
            ("Voltage Divider", lambda: Circuit("VD Test")
                .add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
                .add_resistor("R1", node1=1, node2=2, resistance="1k")
                .add_resistor("R2", node1=2, node2="gnd", resistance="1k"), -6.02),  # Expected -6dB
            
            ("RC Low-Pass", lambda: Circuit("RC Test") 
                .add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
                .add_resistor("R1", node1=1, node2=2, resistance="1k")
                .add_capacitor("C1", node1=2, node2="gnd", capacitance="1uF"), None),  # Variable
        ]
        
        for circuit_name, circuit_func, expected_low_freq_db in test_cases:
            circuit = circuit_func()
            engine = SimulationEngine()
            results = engine.simulate_ac(circuit, start_frequency=1, stop_frequency=1000, points_per_decade=10)
            
            output_voltage = results.voltage(2)
            magnitude_db = 20 * np.log10(np.maximum(np.abs(output_voltage), 1e-12))
            
            # Validate data integrity
            assert not np.any(np.isinf(magnitude_db)), f"{circuit_name}: Infinite dB values detected"
            assert not np.any(np.isnan(magnitude_db)), f"{circuit_name}: NaN values detected"
            
            if expected_low_freq_db is not None:
                low_freq_error = abs(magnitude_db[0] - expected_low_freq_db)
                assert low_freq_error < 0.5, f"{circuit_name}: Low freq error {low_freq_error:.2f}dB"


class TestLLMInformedValidation:
    """LLM-informed tests that use circuit knowledge to validate behavior"""
    
    def test_circuit_behavior_makes_sense(self):
        """Use circuit theory to validate that simulation results make physical sense"""
        
        # Test cases with expected behaviors
        test_scenarios = [
            {
                "name": "RC Low-Pass Filter",
                "circuit": lambda: Circuit("RC LPF")
                    .add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
                    .add_resistor("R1", node1=1, node2=2, resistance="1k")
                    .add_capacitor("C1", node1=2, node2="gnd", capacitance="1uF"),
                "expected_behavior": {
                    "type": "low_pass",
                    "cutoff_freq": 159.2,  # 1/(2πRC)
                    "rolloff_rate": 20,    # dB/decade
                    "phase_at_cutoff": -45,  # degrees
                    "phase_range": (-90, 0)
                }
            },
            {
                "name": "RL High-Pass Behavior",
                "circuit": lambda: Circuit("RL HPF")
                    .add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
                    .add_inductor("L1", node1=1, node2=2, inductance="10mH")
                    .add_resistor("R1", node1=2, node2="gnd", resistance="100"),
                "expected_behavior": {
                    "type": "high_pass",
                    "cutoff_freq": 1592,  # R/(2πL)
                    "rolloff_rate": 20,   # dB/decade (below cutoff)
                    "phase_at_cutoff": 45, # degrees
                    "phase_range": (0, 90)
                }
            }
        ]
        
        for scenario in test_scenarios:
            circuit = scenario["circuit"]()
            expected = scenario["expected_behavior"]
            
            engine = SimulationEngine()
            results = engine.simulate_ac(
                circuit, 
                start_frequency=max(1, expected["cutoff_freq"]/100), 
                stop_frequency=expected["cutoff_freq"]*100, 
                points_per_decade=30
            )
            
            frequencies = np.array(results.frequency)
            output_voltage = results.voltage(2)
            magnitude = np.abs(output_voltage)
            phase = np.angle(output_voltage, deg=True)
            
            # Find cutoff frequency behavior
            cutoff_idx = np.argmin(np.abs(frequencies - expected["cutoff_freq"]))
            
            # Validate physics-based expectations
            if expected["type"] == "low_pass":
                # Low-pass: should attenuate high frequencies
                high_freq_mag = magnitude[-1]
                low_freq_mag = magnitude[0]
                assert high_freq_mag < low_freq_mag * 0.5, f"{scenario['name']}: No high frequency attenuation"
                
            elif expected["type"] == "high_pass":
                # High-pass: should attenuate low frequencies  
                low_freq_mag = magnitude[0]
                high_freq_mag = magnitude[-1]
                assert low_freq_mag < high_freq_mag * 0.5, f"{scenario['name']}: No low frequency attenuation"
            
            # Phase range validation
            phase_min, phase_max = expected["phase_range"]
            actual_phase_range = (phase.min(), phase.max())
            
            # Allow some tolerance but ensure we're in the right ballpark
            assert phase.min() >= phase_min - 20, f"{scenario['name']}: Phase too negative {phase.min():.1f}° (min expected {phase_min}°)"
            assert phase.max() <= phase_max + 20, f"{scenario['name']}: Phase too positive {phase.max():.1f}° (max expected {phase_max}°)"


class VisualRegressionTester:
    """Visual regression testing using chart comparison"""
    
    @staticmethod
    def generate_reference_bode_data(R: float, C: float, frequencies: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Generate theoretical Bode plot data for RC low-pass filter"""
        omega = 2 * np.pi * frequencies
        H = 1 / (1 + 1j * omega * R * C)
        
        magnitude_db = 20 * np.log10(np.abs(H))
        phase_deg = np.angle(H, deg=True)
        
        return magnitude_db, phase_deg
    
    def test_chart_data_vs_theory(self):
        """Compare chart data against theoretical calculations"""
        R, C = 1000, 1e-6  # 1kΩ, 1μF
        
        circuit = Circuit("Theory Comparison Test")
        circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        circuit.add_capacitor("C1", node1=2, node2="gnd", capacitance="1uF")
        
        engine = SimulationEngine()
        results = engine.simulate_ac(circuit, start_frequency=1, stop_frequency=10000, points_per_decade=20)
        
        # Get simulation data
        frequencies = np.array(results.frequency)
        sim_voltage = results.voltage(2)
        sim_magnitude_db = 20 * np.log10(np.maximum(np.abs(sim_voltage), 1e-12))
        sim_phase = np.angle(sim_voltage, deg=True)
        
        # Get theoretical data
        theory_magnitude_db, theory_phase = self.generate_reference_bode_data(R, C, frequencies)
        
        # Compare accuracy
        mag_error = np.sqrt(np.mean((sim_magnitude_db - theory_magnitude_db)**2))
        phase_error = np.sqrt(np.mean((sim_phase - theory_phase)**2))
        
        # Validation thresholds
        assert mag_error < 1.0, f"Magnitude error too large: {mag_error:.3f}dB RMS"
        assert phase_error < 5.0, f"Phase error too large: {phase_error:.1f}° RMS"


# Auto-detection utility functions
def detect_ac_analysis_issues(circuit: Circuit) -> List[str]:
    """Auto-detect common AC analysis issues"""
    issues = []
    
    try:
        engine = SimulationEngine()
        results = engine.simulate_ac(circuit, start_frequency=1, stop_frequency=1000, points_per_decade=10)
        
        for node in results.nodes:
            if node != 0:
                voltage = results.voltage(node)
                if voltage is not None:
                    # Check for real-only values
                    if not np.any(voltage.imag != 0):
                        issues.append(f"Node {node}: AC analysis returning real-only values (missing phase information)")
                    
                    # Check for all-zero data
                    if np.all(voltage == 0):
                        issues.append(f"Node {node}: All voltage values are zero")
                    
                    # Check for flat response where variation expected
                    magnitude = np.abs(voltage)
                    if magnitude.max() - magnitude.min() < 1e-6:
                        issues.append(f"Node {node}: No frequency variation (flat response)")
        
    except Exception as e:
        issues.append(f"AC analysis failed completely: {e}")
    
    return issues


# Pytest markers for different test categories (commented out for now)
# pytestmark = [
#     pytest.mark.simulation,
#     pytest.mark.ac_analysis, 
#     pytest.mark.robust_testing
# ]


if __name__ == "__main__":
    """Run basic validation checks"""
    print("🧪 Running Basic AC Analysis Validation")
    print("=" * 50)
    
    # Test a simple RC filter
    circuit = Circuit("Basic Validation")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
    circuit.add_capacitor("C1", node1=2, node2="gnd", capacitance="1uF")
    
    issues = detect_ac_analysis_issues(circuit)
    
    if issues:
        print("❌ Issues detected:")
        for issue in issues:
            print(f"   • {issue}")
    else:
        print("✅ No issues detected - AC analysis appears healthy")
    
    print(f"\n💡 Run with pytest for full test suite:")
    print(f"   uv run pytest tests/test_robust_simulation_behavior.py -v")