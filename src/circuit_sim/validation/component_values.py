"""
Component value validation module.

Validates electronic component values against specified ranges:
- Resistance: 1mΩ to 1GΩ
- Capacitance: 1pF to 10000µF
- Inductance: 1nH to 10H
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, List, Optional, Tuple

from ..parser import parse_value
from .base import Severity, ValidationIssue, ValidationResult, ValidationRule

if TYPE_CHECKING:
    from ..circuit import Circuit


# Valid component value ranges (in base SI units: ohms, farads, henries)
RESISTANCE_MIN = 0.001  # 1mΩ
RESISTANCE_MAX = 1_000_000_000  # 1GΩ
CAPACITANCE_MIN = 0.000000000001  # 1pF
CAPACITANCE_MAX = 0.01  # 10000µF
INDUCTANCE_MIN = 0.000000001  # 1nH
INDUCTANCE_MAX = 10  # 10H

# Practical (recommended) ranges for extreme value warnings
# Values outside these but within absolute min/max will generate warnings
RESISTANCE_PRACTICAL_MIN = 10  # 10Ω - below this is extreme low
RESISTANCE_PRACTICAL_MAX = 100_000_000  # 100MΩ - above this is extreme high
CAPACITANCE_PRACTICAL_MIN = 0.00000000001  # 10pF - below this is extreme low
CAPACITANCE_PRACTICAL_MAX = 0.001  # 1000µF - above this is extreme high
INDUCTANCE_PRACTICAL_MIN = 0.00000001  # 10nH - below this is extreme low
INDUCTANCE_PRACTICAL_MAX = 1  # 1H - above this is extreme high


@dataclass
class ComponentValueValidationResult:
    """Result of validating a single component value."""

    component_name: str
    component_type: str
    is_valid: bool
    value: Optional[float] = None
    error_message: Optional[str] = None


class ComponentValueValidator(ValidationRule):
    """Validates component values are within acceptable ranges."""

    def __init__(
        self,
        resistance_range: Tuple[float, float] = (RESISTANCE_MIN, RESISTANCE_MAX),
        capacitance_range: Tuple[float, float] = (CAPACITANCE_MIN, CAPACITANCE_MAX),
        inductance_range: Tuple[float, float] = (INDUCTANCE_MIN, INDUCTANCE_MAX),
        resistance_practical_range: Tuple[float, float] = (RESISTANCE_PRACTICAL_MIN, RESISTANCE_PRACTICAL_MAX),
        capacitance_practical_range: Tuple[float, float] = (CAPACITANCE_PRACTICAL_MIN, CAPACITANCE_PRACTICAL_MAX),
        inductance_practical_range: Tuple[float, float] = (INDUCTANCE_PRACTICAL_MIN, INDUCTANCE_PRACTICAL_MAX),
        name: Optional[str] = None,
    ):
        """
        Initialize component value validator.

        Args:
            resistance_range: Min/max resistance in ohms
            capacitance_range: Min/max capacitance in farads
            inductance_range: Min/max inductance in henries
            resistance_practical_range: Practical min/max resistance for extreme warnings
            capacitance_practical_range: Practical min/max capacitance for extreme warnings
            inductance_practical_range: Practical min/max inductance for extreme warnings
            name: Optional custom name for this rule
        """
        super().__init__(name or "ComponentValueValidator")
        self.resistance_range = resistance_range
        self.capacitance_range = capacitance_range
        self.inductance_range = inductance_range
        self.resistance_practical_range = resistance_practical_range
        self.capacitance_practical_range = capacitance_practical_range
        self.inductance_practical_range = inductance_practical_range

    def validate(self, circuit: "Circuit") -> ValidationResult:
        """
        Validate all component values in the circuit.

        Args:
            circuit: Circuit to validate

        Returns:
            ValidationResult with any invalid component values
        """
        issues = []
        warnings = []

        for component in circuit.components:
            result = self._validate_component(component)
            if result:
                if result.severity == Severity.ERROR:
                    issues.append(result)
                elif result.severity == Severity.WARNING:
                    warnings.append(result)

        # Determine overall validity
        is_valid = len(issues) == 0

        return self._create_result_with_warnings(
            is_valid=is_valid,
            issues=issues,
            warnings=warnings,
        )

    def _create_result_with_warnings(
        self,
        is_valid: bool = True,
        issues: Optional[List[ValidationIssue]] = None,
        warnings: Optional[List[ValidationIssue]] = None,
        metadata: Optional[dict] = None,
    ) -> ValidationResult:
        """Helper to create validation result with warnings."""
        issues = issues or []
        warnings = warnings or []
        suggestions = []

        # Extract suggestions from issues
        for issue in issues:
            if issue.suggestion:
                suggestions.append(issue.suggestion)
        for warning in warnings:
            if warning.suggestion:
                suggestions.append(warning.suggestion)

        return ValidationResult(
            rule_name=self.name,
            is_valid=is_valid,
            issues=issues,
            warnings=warnings,
            info=[],
            suggestions=suggestions,
            metadata=metadata,
        )

    def _validate_component(self, component) -> Optional[ValidationIssue]:
        """
        Validate a single component's value.

        Args:
            component: Component dictionary

        Returns:
            ValidationIssue if invalid, None if valid
        """
        component_type = component.get("type", "")
        component_name = component.get("name", "unknown")

        if component_type == "resistor":
            return self._validate_resistance(component)
        elif component_type == "capacitor":
            return self._validate_capacitance(component)
        elif component_type == "inductor":
            return self._validate_inductance(component)

        return None

    def _validate_resistance(self, component) -> Optional[ValidationIssue]:
        """Validate resistor value."""
        name = component.get("name", "unknown")
        resistance = component.get("resistance")

        if resistance is None:
            return None

        # Parse resistance value (handles strings like "1k", "10M")
        try:
            value = parse_value(str(resistance))
        except (ValueError, TypeError):
            return self._create_issue(
                issue_type="invalid_resistance",
                severity=Severity.ERROR,
                message=f"Resistor '{name}' has invalid resistance value: {resistance}",
                components=[name],
                suggestion="Provide a numeric resistance value (e.g., '1k', '10M')",
            )

        min_val, max_val = self.resistance_range

        if value < min_val:
            return self._create_issue(
                issue_type="resistance_too_low",
                severity=Severity.ERROR,
                message=f"Resistor '{name}' resistance ({value}Ω) is below minimum "
                        f"({min_val}Ω = 1mΩ)",
                components=[name],
                suggestion=f"Use a resistance of at least {min_val}Ω",
            )
        elif value > max_val:
            return self._create_issue(
                issue_type="resistance_too_high",
                severity=Severity.ERROR,
                message=f"Resistor '{name}' resistance ({value}Ω) is above maximum "
                        f"({max_val}Ω = 1GΩ)",
                components=[name],
                suggestion=f"Use a resistance of at most {max_val}Ω",
            )

        return None

    def _validate_capacitance(self, component) -> Optional[ValidationIssue]:
        """Validate capacitor value."""
        name = component.get("name", "unknown")
        capacitance = component.get("capacitance")

        if capacitance is None:
            return None

        # Parse capacitance value (handles strings like "1u", "10n")
        try:
            value = parse_value(str(capacitance))
        except (ValueError, TypeError):
            return self._create_issue(
                issue_type="invalid_capacitance",
                severity=Severity.ERROR,
                message=f"Capacitor '{name}' has invalid capacitance value: {capacitance}",
                components=[name],
                suggestion="Provide a numeric capacitance value in farads (e.g., '1u', '10n')",
            )

        min_val, max_val = self.capacitance_range

        if value < min_val:
            return self._create_issue(
                issue_type="capacitance_too_low",
                severity=Severity.ERROR,
                message=f"Capacitor '{name}' capacitance ({value}F) is below minimum "
                        f"({min_val}F = 1pF)",
                components=[name],
                suggestion=f"Use a capacitance of at least {min_val}F",
            )
        elif value > max_val:
            return self._create_issue(
                issue_type="capacitance_too_high",
                severity=Severity.ERROR,
                message=f"Capacitor '{name}' capacitance ({value}F) is above maximum "
                        f"({max_val}F = 10000µF)",
                components=[name],
                suggestion=f"Use a capacitance of at most {max_val}F",
            )

        return None

    def _validate_inductance(self, component) -> Optional[ValidationIssue]:
        """Validate inductor value."""
        name = component.get("name", "unknown")
        inductance = component.get("inductance")

        if inductance is None:
            return None

        # Parse inductance value (handles strings like "1m", "10u")
        try:
            value = parse_value(str(inductance))
        except (ValueError, TypeError):
            return self._create_issue(
                issue_type="invalid_inductance",
                severity=Severity.ERROR,
                message=f"Inductor '{name}' has invalid inductance value: {inductance}",
                components=[name],
                suggestion="Provide a numeric inductance value in henries (e.g., '1m', '10u')",
            )

        min_val, max_val = self.inductance_range

        if value < min_val:
            return self._create_issue(
                issue_type="inductance_too_low",
                severity=Severity.ERROR,
                message=f"Inductor '{name}' inductance ({value}H) is below minimum "
                        f"({min_val}H = 1nH)",
                components=[name],
                suggestion=f"Use an inductance of at least {min_val}H",
            )
        elif value > max_val:
            return self._create_issue(
                issue_type="inductance_too_high",
                severity=Severity.ERROR,
                message=f"Inductor '{name}' inductance ({value}H) is above maximum "
                        f"({max_val}H = 10H)",
                components=[name],
                suggestion=f"Use an inductance of at most {max_val}H",
            )

        return None


def validate_resistance(value: float) -> ComponentValueValidationResult:
    """
    Validate a resistance value.

    Args:
        value: Resistance value in ohms

    Returns:
        ComponentValueValidationResult with validation status
    """
    min_val, max_val = RESISTANCE_MIN, RESISTANCE_MAX

    if value < min_val:
        return ComponentValueValidationResult(
            component_name="",
            component_type="resistor",
            is_valid=False,
            value=value,
            error_message=f"Resistance ({value}Ω) is below minimum ({min_val}Ω = 1mΩ)",
        )
    elif value > max_val:
        return ComponentValueValidationResult(
            component_name="",
            component_type="resistor",
            is_valid=False,
            value=value,
            error_message=f"Resistance ({value}Ω) is above maximum ({max_val}Ω = 1GΩ)",
        )

    return ComponentValueValidationResult(
        component_name="",
        component_type="resistor",
        is_valid=True,
        value=value,
    )


def validate_capacitance(value: float) -> ComponentValueValidationResult:
    """
    Validate a capacitance value.

    Args:
        value: Capacitance value in farads

    Returns:
        ComponentValueValidationResult with validation status
    """
    min_val, max_val = CAPACITANCE_MIN, CAPACITANCE_MAX

    if value < min_val:
        return ComponentValueValidationResult(
            component_name="",
            component_type="capacitor",
            is_valid=False,
            value=value,
            error_message=f"Capacitance ({value}F) is below minimum ({min_val}F = 1pF)",
        )
    elif value > max_val:
        return ComponentValueValidationResult(
            component_name="",
            component_type="capacitor",
            is_valid=False,
            value=value,
            error_message=f"Capacitance ({value}F) is above maximum ({max_val}F = 10000µF)",
        )

    return ComponentValueValidationResult(
        component_name="",
        component_type="capacitor",
        is_valid=True,
        value=value,
    )


def validate_inductance(value: float) -> ComponentValueValidationResult:
    """
    Validate an inductance value.

    Args:
        value: Inductance value in henries

    Returns:
        ComponentValueValidationResult with validation status
    """
    min_val, max_val = INDUCTANCE_MIN, INDUCTANCE_MAX

    if value < min_val:
        return ComponentValueValidationResult(
            component_name="",
            component_type="inductor",
            is_valid=False,
            value=value,
            error_message=f"Inductance ({value}H) is below minimum ({min_val}H = 1nH)",
        )
    elif value > max_val:
        return ComponentValueValidationResult(
            component_name="",
            component_type="inductor",
            is_valid=False,
            value=value,
            error_message=f"Inductance ({value}H) is above maximum ({max_val}H = 10H)",
        )

    return ComponentValueValidationResult(
        component_name="",
        component_type="inductor",
        is_valid=True,
        value=value,
    )
