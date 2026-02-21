"""
Component value validation module.

Validates electronic component values against specified ranges:
- Resistance: 1mΩ to 1GΩ
- Capacitance: 1pF to 10000µF
- Inductance: 1nH to 10H
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Tuple, Union

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


# Standard component value series for suggestions

# E24 resistor series (ohms) - most common
E24_RESISTOR_VALUES = [
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1,
]

# Multipliers for E24 series (to get full range)
RESISTOR_MULTIPLIERS = [1, 10, 100, 1000, 10000, 100000, 1000000, 100000000]

# Common capacitor values (farads)
COMMON_CAPACITOR_VALUES = [
    1e-12, 2.2e-12, 4.7e-12, 10e-12, 22e-12, 47e-12, 100e-12, 220e-12, 470e-12,
    1e-9, 2.2e-9, 4.7e-9, 10e-9, 22e-9, 47e-9, 100e-9, 220e-9, 470e-9,
    1e-6, 2.2e-6, 4.7e-6, 10e-6, 22e-6, 47e-6, 100e-6, 220e-6, 470e-6,
    1000e-6, 2200e-6, 4700e-6,
]

# Common inductor values (henries)
COMMON_INDUCTOR_VALUES = [
    1e-9, 2.2e-9, 4.7e-9, 10e-9, 22e-9, 47e-9, 100e-9, 220e-9, 470e-9,
    1e-6, 2.2e-6, 4.7e-6, 10e-6, 22e-6, 47e-6, 100e-6, 220e-6, 470e-6,
    1e-3, 2.2e-3, 4.7e-3, 10e-3, 22e-3, 47e-3, 100e-3,
]


def format_resistance(value: float) -> str:
    """Format resistance value with appropriate SI prefix."""
    if value == 0:
        return "0 Ω"
    
    abs_value = abs(value)
    
    # Handle different ranges with appropriate formatting
    if abs_value >= 1e9:
        return f"{value / 1e9:.0f} GΩ"
    elif abs_value >= 1e6:
        return f"{value / 1e6:.0f} MΩ"
    elif abs_value >= 1e3:
        return f"{value / 1e3:.0f} kΩ"
    elif abs_value >= 1:
        return f"{value:.0f} Ω"
    elif abs_value >= 1e-3:
        # Milliohms - format as mΩ with 3 decimal places
        return f"{value / 1e-3:.0f} mΩ"
    elif abs_value >= 1e-6:
        # Microohms - format as µΩ
        return f"{value / 1e-6:.0f} µΩ"
    else:
        return f"{value:.3e} Ω"


def format_capacitance(value: float) -> str:
    """Format capacitance value with appropriate SI prefix."""
    if value == 0:
        return "0 F"
    
    abs_value = abs(value)
    
    if abs_value >= 1e-3:
        return f"{value / 1e-3:.0f} mF"
    elif abs_value >= 1e-6:
        return f"{value / 1e-6:.0f} µF"
    elif abs_value >= 1e-9:
        return f"{value / 1e-9:.0f} nF"
    elif abs_value >= 1e-12:
        return f"{value / 1e-12:.0f} pF"
    else:
        return f"{value:.3e} F"


def format_inductance(value: float) -> str:
    """Format inductance value with appropriate SI prefix."""
    if value == 0:
        return "0 H"
    
    abs_value = abs(value)
    
    if abs_value >= 1:
        return f"{value:.0f} H"
    elif abs_value >= 1e-3:
        return f"{value / 1e-3:.0f} mH"
    elif abs_value >= 1e-6:
        return f"{value / 1e-6:.0f} µH"
    elif abs_value >= 1e-9:
        return f"{value / 1e-9:.0f} nH"
    else:
        return f"{value:.3e} H"


def get_typical_resistance_suggestion(is_too_low: bool) -> str:
    """Get a suggestion for typical resistor values."""
    if is_too_low:
        return "Consider using standard E24 values like: 10 Ω, 100 Ω, 1 kΩ, 10 kΩ"
    else:
        return "Consider using standard E24 values like: 100 kΩ, 1 MΩ, 10 MΩ, 100 MΩ"


def get_typical_capacitance_suggestion(is_too_low: bool) -> str:
    """Get a suggestion for typical capacitor values."""
    if is_too_low:
        return "Consider using common values like: 10 pF, 100 pF, 1 nF, 10 nF"
    else:
        return "Consider using common values like: 1 µF, 10 µF, 100 µF, 1000 µF"


def get_typical_inductance_suggestion(is_too_low: bool) -> str:
    """Get a suggestion for typical inductor values."""
    if is_too_low:
        return "Consider using common values like: 10 µH, 100 µH, 1 mH, 10 mH"
    else:
        return "Consider using common values like: 1 mH, 10 mH, 100 mH, 1 H"


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
        practical_min, practical_max = self.resistance_practical_range

        # Check for negative values (ERROR)
        if value < 0:
            return self._create_issue(
                issue_type="resistance_negative",
                severity=Severity.ERROR,
                message=f"Resistor '{name}' resistance cannot be negative ({format_resistance(value)})",
                components=[name],
                suggestion="Use a positive resistance value greater than 0",
            )

        # Check for zero values (ERROR)
        if value == 0:
            return self._create_issue(
                issue_type="resistance_zero",
                severity=Severity.ERROR,
                message=f"Resistor '{name}' resistance cannot be zero",
                components=[name],
                suggestion="Use a positive resistance value greater than 0",
            )

        # Check for extreme low values (WARNING) - between practical_min and min_val
        if value < practical_min:
            if value < min_val:
                # Already out of absolute range - this is an ERROR
                return self._create_issue(
                    issue_type="resistance_too_low",
                    severity=Severity.ERROR,
                    message=f"Resistor '{name}' resistance ({format_resistance(value)}) is below minimum "
                            f"({format_resistance(min_val)} = 1mΩ)",
                    components=[name],
                    suggestion=get_typical_resistance_suggestion(is_too_low=True),
                )
            else:
                # Within absolute range but below practical minimum - WARNING
                return self._create_issue(
                    issue_type="resistance_extreme_low",
                    severity=Severity.WARNING,
                    message=f"Resistor '{name}' resistance ({format_resistance(value)}) is extremely low "
                            f"(recommended: >{format_resistance(practical_min)})",
                    components=[name],
                    suggestion=f"Consider using a resistance of at least {format_resistance(practical_min)} for practical circuits",
                )

        # Check for extreme high values (WARNING) - between practical_max and max_val
        if value > practical_max:
            if value > max_val:
                # Already out of absolute range - this is an ERROR
                return self._create_issue(
                    issue_type="resistance_too_high",
                    severity=Severity.ERROR,
                    message=f"Resistor '{name}' resistance ({format_resistance(value)}) is above maximum "
                            f"({format_resistance(max_val)} = 1GΩ)",
                    components=[name],
                    suggestion=get_typical_resistance_suggestion(is_too_low=False),
                )
            else:
                # Within absolute range but above practical maximum - WARNING
                return self._create_issue(
                    issue_type="resistance_extreme_high",
                    severity=Severity.WARNING,
                    message=f"Resistor '{name}' resistance ({format_resistance(value)}) is extremely high "
                            f"(recommended: <{format_resistance(practical_max)})",
                    components=[name],
                    suggestion=f"Consider using a resistance of at most {format_resistance(practical_max)} for practical circuits",
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
        practical_min, practical_max = self.capacitance_practical_range

        # Check for negative values (ERROR)
        if value < 0:
            return self._create_issue(
                issue_type="capacitance_negative",
                severity=Severity.ERROR,
                message=f"Capacitor '{name}' capacitance cannot be negative ({format_capacitance(value)})",
                components=[name],
                suggestion="Use a positive capacitance value greater than 0",
            )

        # Check for zero values (ERROR)
        if value == 0:
            return self._create_issue(
                issue_type="capacitance_zero",
                severity=Severity.ERROR,
                message=f"Capacitor '{name}' capacitance cannot be zero",
                components=[name],
                suggestion="Use a positive capacitance value greater than 0",
            )

        # Check for extreme low values (WARNING) - between practical_min and min_val
        if value < practical_min:
            if value < min_val:
                # Already out of absolute range - this is an ERROR
                return self._create_issue(
                    issue_type="capacitance_too_low",
                    severity=Severity.ERROR,
                    message=f"Capacitor '{name}' capacitance ({format_capacitance(value)}) is below minimum "
                            f"({format_capacitance(min_val)})",
                    components=[name],
                    suggestion=get_typical_capacitance_suggestion(is_too_low=True),
                )
            else:
                # Within absolute range but below practical minimum - WARNING
                return self._create_issue(
                    issue_type="capacitance_extreme_low",
                    severity=Severity.WARNING,
                    message=f"Capacitor '{name}' capacitance ({format_capacitance(value)}) is extremely low "
                            f"(recommended: >{format_capacitance(practical_min)})",
                    components=[name],
                    suggestion=f"Consider using a capacitance of at least {format_capacitance(practical_min)} for practical circuits",
                )

        # Check for extreme high values (WARNING) - between practical_max and max_val
        if value > practical_max:
            if value > max_val:
                # Already out of absolute range - this is an ERROR
                return self._create_issue(
                    issue_type="capacitance_too_high",
                    severity=Severity.ERROR,
                    message=f"Capacitor '{name}' capacitance ({format_capacitance(value)}) is above maximum "
                            f"({format_capacitance(max_val)})",
                    components=[name],
                    suggestion=get_typical_capacitance_suggestion(is_too_low=False),
                )
            else:
                # Within absolute range but above practical maximum - WARNING
                return self._create_issue(
                    issue_type="capacitance_extreme_high",
                    severity=Severity.WARNING,
                    message=f"Capacitor '{name}' capacitance ({format_capacitance(value)}) is extremely high "
                            f"(recommended: <{format_capacitance(practical_max)})",
                    components=[name],
                    suggestion=f"Consider using a capacitance of at most {format_capacitance(practical_max)} for practical circuits",
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
        practical_min, practical_max = self.inductance_practical_range

        # Check for negative values (ERROR)
        if value < 0:
            return self._create_issue(
                issue_type="inductance_negative",
                severity=Severity.ERROR,
                message=f"Inductor '{name}' inductance cannot be negative ({format_inductance(value)})",
                components=[name],
                suggestion="Use a positive inductance value greater than 0",
            )

        # Check for zero values (ERROR)
        if value == 0:
            return self._create_issue(
                issue_type="inductance_zero",
                severity=Severity.ERROR,
                message=f"Inductor '{name}' inductance cannot be zero",
                components=[name],
                suggestion="Use a positive inductance value greater than 0",
            )

        # Check for extreme low values (WARNING) - between practical_min and min_val
        if value < practical_min:
            if value < min_val:
                # Already out of absolute range - this is an ERROR
                return self._create_issue(
                    issue_type="inductance_too_low",
                    severity=Severity.ERROR,
                    message=f"Inductor '{name}' inductance ({format_inductance(value)}) is below minimum "
                            f"({format_inductance(min_val)})",
                    components=[name],
                    suggestion=get_typical_inductance_suggestion(is_too_low=True),
                )
            else:
                # Within absolute range but below practical minimum - WARNING
                return self._create_issue(
                    issue_type="inductance_extreme_low",
                    severity=Severity.WARNING,
                    message=f"Inductor '{name}' inductance ({format_inductance(value)}) is extremely low "
                            f"(recommended: >{format_inductance(practical_min)})",
                    components=[name],
                    suggestion=f"Consider using an inductance of at least {format_inductance(practical_min)} for practical circuits",
                )

        # Check for extreme high values (WARNING) - between practical_max and max_val
        if value > practical_max:
            if value > max_val:
                # Already out of absolute range - this is an ERROR
                return self._create_issue(
                    issue_type="inductance_too_high",
                    severity=Severity.ERROR,
                    message=f"Inductor '{name}' inductance ({format_inductance(value)}) is above maximum "
                            f"({format_inductance(max_val)})",
                    components=[name],
                    suggestion=get_typical_inductance_suggestion(is_too_low=False),
                )
            else:
                # Within absolute range but above practical maximum - WARNING
                return self._create_issue(
                    issue_type="inductance_extreme_high",
                    severity=Severity.WARNING,
                    message=f"Inductor '{name}' inductance ({format_inductance(value)}) is extremely high "
                            f"(recommended: <{format_inductance(practical_max)})",
                    components=[name],
                    suggestion=f"Consider using an inductance of at most {format_inductance(practical_max)} for practical circuits",
                )

        return None


def validate_resistance(value: Union[str, float]) -> ComponentValueValidationResult:
    """
    Validate a resistance value.

    Args:
        value: Resistance value in ohms (accepts string with SI prefixes like "1k", "10M")

    Returns:
        ComponentValueValidationResult with validation status
    """
    # Parse string values (handles strings like "1k", "10M")
    if isinstance(value, str):
        try:
            value = parse_value(value)
        except (ValueError, TypeError):
            return ComponentValueValidationResult(
                component_name="",
                component_type="resistor",
                is_valid=False,
                value=None,
                error_message=f"Invalid resistance value: {value}. Provide a numeric value (e.g., '1k', '10M')",
            )

    min_val, max_val = RESISTANCE_MIN, RESISTANCE_MAX

    # Explicit checks for zero and negative values
    if value < 0:
        return ComponentValueValidationResult(
            component_name="",
            component_type="resistor",
            is_valid=False,
            value=value,
            error_message=f"Resistance cannot be negative ({format_resistance(value)}). "
                           f"Resistance must be a positive value.",
        )
    if value == 0:
        return ComponentValueValidationResult(
            component_name="",
            component_type="resistor",
            is_valid=False,
            value=value,
            error_message=f"Resistance cannot be zero. Resistance must be a positive value "
                           f"greater than {format_resistance(min_val)}.",
        )

    if value < min_val:
        return ComponentValueValidationResult(
            component_name="",
            component_type="resistor",
            is_valid=False,
            value=value,
            error_message=f"Resistance ({format_resistance(value)}) is below minimum ({format_resistance(min_val)})",
        )
    elif value > max_val:
        return ComponentValueValidationResult(
            component_name="",
            component_type="resistor",
            is_valid=False,
            value=value,
            error_message=f"Resistance ({format_resistance(value)}) is above maximum ({format_resistance(max_val)})",
        )

    return ComponentValueValidationResult(
        component_name="",
        component_type="resistor",
        is_valid=True,
        value=value,
    )


def validate_capacitance(value: Union[str, float]) -> ComponentValueValidationResult:
    """
    Validate a capacitance value.

    Args:
        value: Capacitance value in farads (accepts string with SI prefixes like "1u", "10n")

    Returns:
        ComponentValueValidationResult with validation status
    """
    # Parse string values (handles strings like "1u", "10n")
    if isinstance(value, str):
        try:
            value = parse_value(value)
        except (ValueError, TypeError):
            return ComponentValueValidationResult(
                component_name="",
                component_type="capacitor",
                is_valid=False,
                value=None,
                error_message=f"Invalid capacitance value: {value}. Provide a numeric value (e.g., '1u', '10n')",
            )

    min_val, max_val = CAPACITANCE_MIN, CAPACITANCE_MAX

    # Explicit checks for zero and negative values
    if value < 0:
        return ComponentValueValidationResult(
            component_name="",
            component_type="capacitor",
            is_valid=False,
            value=value,
            error_message=f"Capacitance cannot be negative ({format_capacitance(value)}). "
                           f"Capacitance must be a positive value.",
        )
    if value == 0:
        return ComponentValueValidationResult(
            component_name="",
            component_type="capacitor",
            is_valid=False,
            value=value,
            error_message=f"Capacitance cannot be zero. Capacitance must be a positive value "
                           f"greater than {format_capacitance(min_val)}.",
        )

    if value < min_val:
        return ComponentValueValidationResult(
            component_name="",
            component_type="capacitor",
            is_valid=False,
            value=value,
            error_message=f"Capacitance ({format_capacitance(value)}) is below minimum ({format_capacitance(min_val)})",
        )
    elif value > max_val:
        return ComponentValueValidationResult(
            component_name="",
            component_type="capacitor",
            is_valid=False,
            value=value,
            error_message=f"Capacitance ({format_capacitance(value)}) is above maximum ({format_capacitance(max_val)})",
        )

    return ComponentValueValidationResult(
        component_name="",
        component_type="capacitor",
        is_valid=True,
        value=value,
    )


def validate_inductance(value: Union[str, float]) -> ComponentValueValidationResult:
    """
    Validate an inductance value.

    Args:
        value: Inductance value in henries (accepts string with SI prefixes like "1m", "10u")

    Returns:
        ComponentValueValidationResult with validation status
    """
    # Parse string values (handles strings like "1m", "10u")
    if isinstance(value, str):
        try:
            value = parse_value(value)
        except (ValueError, TypeError):
            return ComponentValueValidationResult(
                component_name="",
                component_type="inductor",
                is_valid=False,
                value=None,
                error_message=f"Invalid inductance value: {value}. Provide a numeric value (e.g., '1m', '10u')",
            )

    min_val, max_val = INDUCTANCE_MIN, INDUCTANCE_MAX

    # Explicit checks for zero and negative values
    if value < 0:
        return ComponentValueValidationResult(
            component_name="",
            component_type="inductor",
            is_valid=False,
            value=value,
            error_message=f"Inductance cannot be negative ({format_inductance(value)}). "
                           f"Inductance must be a positive value.",
        )
    if value == 0:
        return ComponentValueValidationResult(
            component_name="",
            component_type="inductor",
            is_valid=False,
            value=value,
            error_message=f"Inductance cannot be zero. Inductance must be a positive value "
                           f"greater than {format_inductance(min_val)}.",
        )

    if value < min_val:
        return ComponentValueValidationResult(
            component_name="",
            component_type="inductor",
            is_valid=False,
            value=value,
            error_message=f"Inductance ({format_inductance(value)}) is below minimum ({format_inductance(min_val)})",
        )
    elif value > max_val:
        return ComponentValueValidationResult(
            component_name="",
            component_type="inductor",
            is_valid=False,
            value=value,
            error_message=f"Inductance ({format_inductance(value)}) is above maximum ({format_inductance(max_val)})",
        )

    return ComponentValueValidationResult(
        component_name="",
        component_type="inductor",
        is_valid=True,
        value=value,
    )
