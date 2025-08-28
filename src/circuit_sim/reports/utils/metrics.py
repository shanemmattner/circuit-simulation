"""
Metrics calculator for circuit analysis reports.

This module provides the MetricsCalculator class that computes
performance metrics from simulation results.
"""

from typing import Any, Dict, Optional

import numpy as np

from ...circuit import Circuit
from ...simulator.results import SimulationResults


class MetricsCalculator:
    """Calculate performance metrics from simulation results."""

    def calculate_metrics(
        self, results: SimulationResults, circuit: Circuit
    ) -> Dict[str, Any]:
        """
        Calculate relevant metrics based on analysis type.

        Args:
            results: Simulation results
            circuit: Circuit definition

        Returns:
            Dictionary of calculated metrics
        """
        metrics = {}

        if results.analysis_type == "dc":
            metrics.update(self._calculate_dc_metrics(results, circuit))
        elif results.analysis_type == "transient":
            metrics.update(self._calculate_transient_metrics(results, circuit))
        elif results.analysis_type == "ac":
            metrics.update(self._calculate_ac_metrics(results, circuit))

        return metrics

    def _calculate_dc_metrics(
        self, results: SimulationResults, circuit: Circuit
    ) -> Dict[str, Any]:
        """Calculate DC analysis metrics."""
        metrics = {}

        # Power dissipation
        power_total = 0.0
        for component in results.components:
            current = results.current(component)
            if current is not None and len(current) > 0:
                # Find component in circuit for voltage calculation
                comp_voltage = self._get_component_voltage(component, circuit, results)
                if comp_voltage is not None:
                    power = abs(comp_voltage * current[0])
                    power_total += power

        metrics["power_dissipation"] = power_total

        # Efficiency (simplified - ratio of output to input power)
        source_power = 0.0
        load_power = 0.0

        for component in circuit.components:
            if component["type"] in ["voltage_source", "current_source"]:
                current = results.current(component["name"])
                if current is not None and len(current) > 0:
                    if "dc_value" in component:
                        voltage = self._parse_dc_value(component["dc_value"])
                        source_power += abs(voltage * current[0])
            else:
                # Consider resistors as load
                current = results.current(component["name"])
                if current is not None and len(current) > 0:
                    comp_voltage = self._get_component_voltage(
                        component["name"], circuit, results
                    )
                    if comp_voltage is not None:
                        load_power += abs(comp_voltage * current[0])

        if source_power > 0:
            metrics["efficiency"] = min(1.0, load_power / source_power)
        else:
            metrics["efficiency"] = 0.0

        return metrics

    def _calculate_transient_metrics(
        self, results: SimulationResults, circuit: Circuit
    ) -> Dict[str, Any]:
        """Calculate transient analysis metrics."""
        metrics = {}

        if results.time is None or len(results.nodes) == 0:
            return metrics

        # Use first non-ground node for step response analysis
        test_node = None
        for node in results.nodes:
            if node != 0:
                test_node = node
                break

        if test_node is None:
            return metrics

        voltage = results.voltage(test_node)
        if voltage is None or len(voltage) == 0:
            return metrics

        time = results.time

        # Rise time (10% to 90% of final value)
        final_value = voltage[-1]
        rise_time = self._calculate_rise_time(time, voltage, final_value)
        if rise_time is not None:
            metrics["rise_time"] = rise_time

        # Settling time (within 2% of final value)
        settling_time = self._calculate_settling_time(time, voltage, final_value)
        if settling_time is not None:
            metrics["settling_time"] = settling_time

        # Overshoot percentage
        overshoot = self._calculate_overshoot(voltage, final_value)
        metrics["overshoot"] = overshoot

        return metrics

    def _calculate_ac_metrics(
        self, results: SimulationResults, circuit: Circuit
    ) -> Dict[str, Any]:
        """Calculate AC frequency analysis metrics."""
        metrics = {}

        if results.frequency is None or len(results.nodes) == 0:
            return metrics

        # Use first non-ground node for frequency response analysis
        test_node = None
        for node in results.nodes:
            if node != 0:
                test_node = node
                break

        if test_node is None:
            return metrics

        voltage = results.voltage(test_node)
        if voltage is None or not np.iscomplexobj(voltage):
            return metrics

        frequency = results.frequency
        magnitude = np.abs(voltage)
        magnitude_db = 20 * np.log10(magnitude + 1e-12)  # Avoid log(0)
        phase = np.angle(voltage, deg=True)

        # Maximum gain
        max_gain = np.max(magnitude_db)
        metrics["gain"] = max_gain

        # Bandwidth (-3dB point)
        bandwidth = self._calculate_bandwidth(frequency, magnitude_db, max_gain)
        if bandwidth is not None:
            metrics["bandwidth"] = bandwidth

        # Phase margin (phase at unity gain crossing)
        phase_margin = self._calculate_phase_margin(frequency, magnitude_db, phase)
        if phase_margin is not None:
            metrics["phase_margin"] = phase_margin

        # Transfer function analysis
        try:
            input_node = self._find_input_node(circuit)
            output_node = self._find_output_node(circuit, results)

            if input_node is not None and output_node is not None:
                tf = results.to_transfer_function(input_node, output_node)

                # Transfer function properties
                metrics["tf_order"] = tf.order
                metrics["tf_dc_gain"] = tf.dc_gain
                metrics["tf_dc_gain_db"] = (
                    20 * np.log10(abs(tf.dc_gain)) if tf.dc_gain != 0 else -float("inf")
                )
                metrics["tf_bandwidth"] = tf.bandwidth / (2 * np.pi)  # Convert to Hz
                metrics["tf_is_stable"] = tf.is_stable
                metrics["tf_num_poles"] = len(tf.poles)
                metrics["tf_num_zeros"] = len(tf.zeros)

                # Mathematical representation
                metrics["tf_numerator_coeffs"] = tf.numerator_coeffs.tolist()
                metrics["tf_denominator_coeffs"] = tf.denominator_coeffs.tolist()
                metrics["tf_latex"] = self._format_transfer_function_latex(tf)
                metrics["tf_readable"] = self._format_transfer_function_readable(tf)

                # Pole/zero locations
                if len(tf.poles) > 0:
                    metrics["tf_dominant_pole"] = complex(
                        tf.poles[np.argmax(np.real(tf.poles))]
                    )
                if len(tf.zeros) > 0:
                    metrics["tf_dominant_zero"] = complex(
                        tf.zeros[np.argmax(np.real(tf.zeros))]
                    )

                # Filter characteristics
                metrics.update(self._analyze_filter_characteristics(tf, results))

        except Exception:
            # If transfer function extraction fails, continue without it
            pass

        return metrics

    def _find_input_node(self, circuit: Circuit) -> int:
        """Find the input node (typically connected to voltage source)."""
        for component in circuit.components:
            if component.get("type") == "voltage_source":
                return component.get("positive")
        return None

    def _find_output_node(self, circuit: Circuit, results: SimulationResults) -> int:
        """Find the output node (node with most interesting frequency response)."""
        best_node = None
        max_variation = 0

        for node in results.nodes:
            if node != 0:  # Skip ground
                voltage = results.voltage(node)
                if voltage is not None and np.iscomplexobj(voltage):
                    # Check for meaningful frequency variation
                    magnitude = np.abs(voltage)
                    variation = magnitude.max() - magnitude.min()
                    if variation > max_variation:
                        max_variation = variation
                        best_node = node

        return best_node

    def _analyze_filter_characteristics(
        self, tf, results: SimulationResults
    ) -> Dict[str, Any]:
        """Analyze filter characteristics from transfer function."""
        characteristics = {}

        # Determine filter type based on poles and zeros
        poles = tf.poles
        zeros = tf.zeros

        # Low-pass filter detection (more poles than zeros)
        if len(poles) > len(zeros):
            characteristics["filter_type"] = "low-pass"
        # High-pass filter detection (more zeros than poles or zeros at origin)
        elif len(zeros) > len(poles) or (
            len(zeros) > 0 and np.any(np.abs(zeros) < 1e-6)
        ):
            characteristics["filter_type"] = "high-pass"
        # Band-pass filter detection (complex poles)
        elif len(poles) >= 2 and np.any(np.imag(poles) != 0):
            characteristics["filter_type"] = "band-pass"
        else:
            characteristics["filter_type"] = "unknown"

        # Calculate quality factor for second-order systems
        if len(poles) >= 2:
            # Find complex conjugate pole pair
            for i, pole in enumerate(poles):
                if np.imag(pole) != 0:
                    wn = np.abs(pole)  # Natural frequency
                    zeta = -np.real(pole) / wn  # Damping ratio
                    characteristics["natural_frequency_hz"] = wn / (2 * np.pi)
                    characteristics["damping_ratio"] = zeta
                    characteristics["quality_factor"] = (
                        1 / (2 * zeta) if zeta > 0 else float("inf")
                    )
                    break

        # Calculate rolloff rate (dB/decade)
        if len(poles) > 0:
            characteristics["rolloff_rate_db_decade"] = -20 * len(poles)

        return characteristics

    def _format_transfer_function_latex(self, tf) -> str:
        """Format transfer function as LaTeX for mathematical display."""
        num_coeffs = tf.numerator_coeffs
        den_coeffs = tf.denominator_coeffs

        def format_polynomial_latex(coeffs):
            if len(coeffs) == 1:
                return f"{coeffs[0]:.3g}"

            terms = []
            degree = len(coeffs) - 1

            for i, coeff in enumerate(coeffs):
                if abs(coeff) < 1e-10:  # Skip near-zero coefficients
                    degree -= 1
                    continue

                power = degree - i

                if power == 0:
                    terms.append(f"{coeff:.3g}")
                elif power == 1:
                    if coeff == 1:
                        terms.append("s")
                    elif coeff == -1:
                        terms.append("-s")
                    else:
                        terms.append(f"{coeff:.3g}s")
                else:
                    if coeff == 1:
                        terms.append(f"s^{power}")
                    elif coeff == -1:
                        terms.append(f"-s^{power}")
                    else:
                        terms.append(f"{coeff:.3g}s^{power}")

            if not terms:
                return "0"

            # Join terms with proper signs
            result = terms[0]
            for term in terms[1:]:
                if term.startswith("-"):
                    result += f" - {term[1:]}"
                else:
                    result += f" + {term}"

            return result

        numerator = format_polynomial_latex(num_coeffs)
        denominator = format_polynomial_latex(den_coeffs)

        return f"H(s) = \\frac{{{numerator}}}{{{denominator}}}"

    def _format_transfer_function_readable(self, tf) -> str:
        """Format transfer function in readable text format."""
        num_coeffs = tf.numerator_coeffs
        den_coeffs = tf.denominator_coeffs

        def format_polynomial_readable(coeffs):
            if len(coeffs) == 1:
                return f"{coeffs[0]:.3g}"

            terms = []
            degree = len(coeffs) - 1

            for i, coeff in enumerate(coeffs):
                if abs(coeff) < 1e-10:  # Skip near-zero coefficients
                    degree -= 1
                    continue

                power = degree - i

                if power == 0:
                    terms.append(f"{coeff:.3g}")
                elif power == 1:
                    if coeff == 1:
                        terms.append("s")
                    elif coeff == -1:
                        terms.append("-s")
                    else:
                        terms.append(f"{coeff:.3g}*s")
                else:
                    if coeff == 1:
                        terms.append(f"s^{power}")
                    elif coeff == -1:
                        terms.append(f"-s^{power}")
                    else:
                        terms.append(f"{coeff:.3g}*s^{power}")

            if not terms:
                return "0"

            # Join terms with proper signs
            result = terms[0]
            for term in terms[1:]:
                if term.startswith("-"):
                    result += f" - {term[1:]}"
                else:
                    result += f" + {term}"

            return result

        numerator = format_polynomial_readable(num_coeffs)
        denominator = format_polynomial_readable(den_coeffs)

        return f"H(s) = ({numerator}) / ({denominator})"

    def _get_component_voltage(
        self, component_name: str, circuit: Circuit, results: SimulationResults
    ) -> Optional[float]:
        """Get voltage across a component."""
        # Find component in circuit
        for component in circuit.components:
            if component["name"] == component_name:
                if "node1" in component and "node2" in component:
                    v1 = results.voltage(component["node1"])
                    v2 = results.voltage(component["node2"])
                    if v1 is not None and v2 is not None:
                        return abs(v1[0] - v2[0])
                elif "positive" in component and "negative" in component:
                    v_pos = results.voltage(component["positive"])
                    v_neg = results.voltage(component["negative"])
                    if v_pos is not None and v_neg is not None:
                        return abs(v_pos[0] - v_neg[0])
        return None

    def _parse_dc_value(self, dc_value: str) -> float:
        """Parse DC value string to float."""
        value_str = dc_value.upper().rstrip("V").rstrip("A")
        try:
            # Handle SI prefixes
            if value_str.endswith("M"):
                return float(value_str[:-1]) * 1e6
            elif value_str.endswith("K"):
                return float(value_str[:-1]) * 1e3
            elif value_str.endswith("U"):
                return float(value_str[:-1]) * 1e-6
            elif value_str.endswith("N"):
                return float(value_str[:-1]) * 1e-9
            elif value_str.endswith("P"):
                return float(value_str[:-1]) * 1e-12
            else:
                return float(value_str)
        except ValueError:
            return 0.0

    def _calculate_rise_time(
        self, time: np.ndarray, voltage: np.ndarray, final_value: float
    ) -> Optional[float]:
        """Calculate 10% to 90% rise time."""
        if abs(final_value) < 1e-12:
            return None

        target_10 = 0.1 * final_value
        target_90 = 0.9 * final_value

        # Find crossing points
        idx_10 = None
        idx_90 = None

        for i in range(len(voltage) - 1):
            if idx_10 is None and voltage[i] <= target_10 < voltage[i + 1]:
                idx_10 = i
            if idx_90 is None and voltage[i] <= target_90 < voltage[i + 1]:
                idx_90 = i
                break

        if idx_10 is not None and idx_90 is not None and idx_90 > idx_10:
            return float(time[idx_90] - time[idx_10])

        return None

    def _calculate_settling_time(
        self, time: np.ndarray, voltage: np.ndarray, final_value: float
    ) -> Optional[float]:
        """Calculate settling time (within 2% of final value)."""
        if abs(final_value) < 1e-12:
            return None

        tolerance = 0.02 * abs(final_value)

        # Work backwards from end
        for i in range(len(voltage) - 1, 0, -1):
            if abs(voltage[i] - final_value) > tolerance:
                if i < len(time) - 1:
                    return float(time[i + 1])
                break

        return float(time[-1])

    def _calculate_overshoot(self, voltage: np.ndarray, final_value: float) -> float:
        """Calculate overshoot percentage."""
        if abs(final_value) < 1e-12:
            return 0.0

        max_voltage = np.max(voltage)
        if final_value > 0:
            overshoot = max(0, (max_voltage - final_value) / final_value * 100)
        else:
            min_voltage = np.min(voltage)
            overshoot = max(0, (final_value - min_voltage) / abs(final_value) * 100)

        return float(overshoot)

    def _calculate_bandwidth(
        self, frequency: np.ndarray, magnitude_db: np.ndarray, max_gain: float
    ) -> Optional[float]:
        """Calculate -3dB bandwidth."""
        cutoff_db = max_gain - 3.0

        # Find frequency where magnitude crosses cutoff
        for i in range(len(magnitude_db) - 1):
            if magnitude_db[i] >= cutoff_db > magnitude_db[i + 1]:
                # Linear interpolation
                f1, f2 = frequency[i], frequency[i + 1]
                m1, m2 = magnitude_db[i], magnitude_db[i + 1]
                freq_cutoff = f1 + (cutoff_db - m1) * (f2 - f1) / (m2 - m1)
                return float(freq_cutoff)

        return None

    def _calculate_phase_margin(
        self, frequency: np.ndarray, magnitude_db: np.ndarray, phase: np.ndarray
    ) -> Optional[float]:
        """Calculate phase margin at unity gain crossing."""
        # Find unity gain crossing (0 dB)
        for i in range(len(magnitude_db) - 1):
            if magnitude_db[i] >= 0 > magnitude_db[i + 1]:
                # Linear interpolation for phase at 0 dB crossing
                m1, m2 = magnitude_db[i], magnitude_db[i + 1]
                p1, p2 = phase[i], phase[i + 1]
                phase_at_unity = p1 + (0 - m1) * (p2 - p1) / (m2 - m1)
                return float(180 + phase_at_unity)  # Phase margin

        # If no 0dB crossing found, calculate phase margin at highest magnitude
        max_idx = np.argmax(magnitude_db)
        return float(180 + phase[max_idx])
