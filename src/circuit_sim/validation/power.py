"""
Power dissipation analysis for circuits.
"""

from dataclasses import dataclass
from typing import Dict, Optional, List
import logging

from ..circuit import Circuit
from ..simulator.results import SimulationResults
from .base import ValidationRule, ValidationResult, ValidationIssue, Severity

logger = logging.getLogger(__name__)


@dataclass
class ComponentPowerInfo:
    """Power information for a single component."""

    power: float  # Power in watts (positive = dissipated, negative = supplied)
    voltage: float  # Voltage across component in volts
    current: float  # Current through component in amperes
    method: str  # Calculation method used ("I²R", "V²/R", "VI")
    component_type: str  # Type of component
    rating: Optional[float] = None  # Power rating if known


@dataclass
class PowerAnalysisResult:
    """Result of power analysis."""

    is_valid: bool
    component_power: Dict[str, ComponentPowerInfo]
    source_power: Dict[str, ComponentPowerInfo]
    total_power: float  # Total power dissipated
    power_budget: Dict[str, float]  # Power budget summary
    issues: List[ValidationIssue]
    warnings: List[ValidationIssue]
    metadata: Optional[Dict] = None


class PowerAnalyzer(ValidationRule):
    """Analyzes power dissipation in DC circuits."""

    def __init__(
        self,
        power_warning_threshold: float = 1.0,  # Watts
        power_error_threshold: float = 10.0,  # Watts
        name: str = "PowerAnalyzer",
    ):
        """
        Initialize power analyzer.

        Args:
            power_warning_threshold: Power above which to warn (W)
            power_error_threshold: Power above which to error (W)
            name: Name for this analyzer
        """
        super().__init__(name)
        self.power_warning_threshold = power_warning_threshold
        self.power_error_threshold = power_error_threshold

    def validate(self, circuit: Circuit) -> ValidationResult:
        """
        Validate power levels in circuit (requires simulation results).
        This is primarily for integration with validation framework.

        Args:
            circuit: Circuit to validate

        Returns:
            ValidationResult (will indicate simulation needed)
        """
        # Power analysis requires simulation results, so this just checks structure
        issues = []

        if not circuit.components:
            issues.append(
                self._create_issue(
                    issue_type="no_components",
                    severity=Severity.ERROR,
                    message="Cannot analyze power - circuit has no components",
                    components=[],
                )
            )

        # Check if circuit has power sources
        has_source = any(
            comp.get("type") in ["voltage_source", "current_source"]
            for comp in circuit.components
        )

        if not has_source:
            issues.append(
                self._create_issue(
                    issue_type="no_power_sources",
                    severity=Severity.WARNING,
                    message="Circuit has no power sources - power analysis will show zero",
                    components=[],
                )
            )

        is_valid = len([i for i in issues if i.severity == Severity.ERROR]) == 0
        return self._create_result(is_valid=is_valid, issues=issues)

    def analyze_power(
        self,
        circuit: Circuit,
        results: SimulationResults,
        component_ratings: Optional[Dict[str, float]] = None,
    ) -> PowerAnalysisResult:
        """
        Analyze power dissipation using simulation results.

        Args:
            circuit: Circuit definition
            results: Simulation results (must be DC analysis)
            component_ratings: Optional component power ratings (name -> watts)

        Returns:
            PowerAnalysisResult with power information
        """
        if results.analysis_type != "dc":
            raise NotImplementedError(
                "Power analysis currently only supports DC analysis"
            )

        component_ratings = component_ratings or {}

        # Calculate power for each component
        component_power = {}
        source_power = {}
        issues = []
        warnings = []

        for component in circuit.components:
            name = component.get("name", "unnamed")
            comp_type = component.get("type", "unknown")

            try:
                power_info = self._calculate_component_power(component, results)

                if comp_type in ["voltage_source", "current_source"]:
                    source_power[name] = power_info
                else:
                    component_power[name] = power_info

                # Check power rating if provided
                if name in component_ratings:
                    rating = component_ratings[name]
                    power_info.rating = rating

                    if abs(power_info.power) > rating:
                        issues.append(
                            ValidationIssue(
                                type="power_rating_exceeded",
                                severity=Severity.ERROR,
                                message=f"Component {name} dissipates {power_info.power:.3f}W, exceeds {rating}W rating",
                                components=[name],
                                suggestion=f"Use component rated for at least {power_info.power:.3f}W",
                            )
                        )

                # Check general power thresholds
                abs_power = abs(power_info.power)
                if abs_power > self.power_error_threshold:
                    issues.append(
                        ValidationIssue(
                            type="excessive_power",
                            severity=Severity.ERROR,
                            message=f"Component {name} has excessive power: {power_info.power:.3f}W",
                            components=[name],
                            suggestion="Consider higher voltage/lower current design",
                        )
                    )
                elif abs_power > self.power_warning_threshold:
                    warnings.append(
                        ValidationIssue(
                            type="high_power",
                            severity=Severity.WARNING,
                            message=f"Component {name} has high power dissipation: {power_info.power:.3f}W",
                            components=[name],
                            suggestion="Verify component can handle this power level",
                        )
                    )

            except Exception as e:
                logger.warning(f"Failed to calculate power for {name}: {e}")
                warnings.append(
                    ValidationIssue(
                        type="power_calculation_failed",
                        severity=Severity.WARNING,
                        message=f"Could not calculate power for {name}: {str(e)}",
                        components=[name],
                        suggestion="Check component connections and simulation results",
                    )
                )

        # Calculate totals and power budget
        total_dissipated = sum(p.power for p in component_power.values() if p.power > 0)
        total_supplied = sum(abs(p.power) for p in source_power.values())

        power_budget = {
            "total_supplied": total_supplied,
            "total_dissipated": total_dissipated,
            "efficiency": (
                total_dissipated / total_supplied if total_supplied > 0 else 0.0
            ),
            "balance": abs(total_supplied - total_dissipated),
        }

        # Check power balance
        if power_budget["balance"] > 0.001:  # 1mW tolerance
            warnings.append(
                ValidationIssue(
                    type="power_imbalance",
                    severity=Severity.WARNING,
                    message=f"Power imbalance: {power_budget['balance']:.6f}W difference between supply and dissipation",
                    components=[],
                    suggestion="Check simulation convergence and component models",
                )
            )

        is_valid = len(issues) == 0

        return PowerAnalysisResult(
            is_valid=is_valid,
            component_power=component_power,
            source_power=source_power,
            total_power=total_dissipated,
            power_budget=power_budget,
            issues=issues,
            warnings=warnings,
            metadata={
                "analysis_type": results.analysis_type,
                "component_count": len(circuit.components),
                "calculation_method": "DC operating point",
            },
        )

    def _calculate_component_power(
        self, component: Dict, results: SimulationResults
    ) -> ComponentPowerInfo:
        """
        Calculate power for a single component.

        Args:
            component: Component definition
            results: Simulation results

        Returns:
            ComponentPowerInfo with power calculation
        """
        name = component.get("name")
        comp_type = component.get("type", "unknown")

        # Get voltage across component
        voltage = self._get_component_voltage(component, results)

        # Get current through component
        current = self._get_component_current(component, results, name)

        # Calculate power based on component type
        if comp_type == "resistor":
            # For resistors, prefer I²R method for accuracy
            resistance = self._parse_resistance(component.get("resistance", "0"))
            if resistance > 0 and current is not None:
                power = current * current * resistance
                method = "I²R"
            elif voltage is not None and resistance > 0:
                power = (voltage * voltage) / resistance
                method = "V²/R"
            elif voltage is not None and current is not None:
                power = voltage * current
                method = "VI"
            else:
                power = 0.0
                method = "unknown"

        elif comp_type in ["voltage_source", "current_source"]:
            # Sources: negative power = supplying, positive = consuming
            if voltage is not None and current is not None:
                # The current from simulation is already in the correct sign convention
                # For voltage sources: negative current means supplying current
                power = voltage * current  # This will be negative when supplying power
                method = "VI"
            else:
                power = 0.0
                method = "unknown"

        elif comp_type in ["capacitor", "inductor"]:
            # Reactive components have zero average power in DC
            power = 0.0
            method = "DC reactive"

        else:
            # Unknown component type
            if voltage is not None and current is not None:
                power = voltage * current
                method = "VI"
            else:
                power = 0.0
                method = "unknown"

        return ComponentPowerInfo(
            power=power,
            voltage=voltage or 0.0,
            current=current or 0.0,
            method=method,
            component_type=comp_type,
        )

    def _get_component_voltage(
        self, component: Dict, results: SimulationResults
    ) -> Optional[float]:
        """Get voltage across a component."""
        # Get component nodes
        if "positive" in component and "negative" in component:
            pos_node = component["positive"]
            neg_node = component["negative"]
        elif "node1" in component and "node2" in component:
            pos_node = component["node1"]
            neg_node = component["node2"]
        else:
            return None

        # Get node voltages
        try:
            pos_voltage = results.voltage(pos_node)
            neg_voltage = results.voltage(neg_node)

            if pos_voltage is not None and neg_voltage is not None:
                return float(pos_voltage[0] - neg_voltage[0])
        except:
            pass

        return None

    def _get_component_current(
        self, component: Dict, results: SimulationResults, name: str
    ) -> Optional[float]:
        """Get current through a component."""
        # Try different name variations (case insensitive, etc)
        for candidate_name in [name, name.lower(), name.upper()]:
            try:
                current = results.current(candidate_name)
                if current is not None:
                    return float(current[0])
            except:
                continue

        # For resistors, current might not be directly available
        # Use Ohm's law: I = V/R
        comp_type = component.get("type")
        if comp_type == "resistor":
            voltage = self._get_component_voltage(component, results)
            resistance = self._parse_resistance(component.get("resistance", "0"))
            if voltage is not None and resistance > 0:
                return voltage / resistance

        return None

    def _parse_resistance(self, resistance_str: str) -> float:
        """Parse resistance value from string."""
        try:
            # Handle string values like "1k", "10M", "1.5k"
            resistance_str = str(resistance_str).upper().strip()
            resistance_str = resistance_str.replace("Ω", "").replace("OHM", "")

            # Handle k and M multipliers properly
            if "K" in resistance_str:
                base = float(resistance_str.replace("K", ""))
                return base * 1000.0
            elif "M" in resistance_str:
                base = float(resistance_str.replace("M", ""))
                return base * 1000000.0
            else:
                return float(resistance_str)
        except (ValueError, AttributeError):
            return 0.0
