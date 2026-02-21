"""Circuit validation module."""

from .base import ValidationResult, ValidationRule
from .basic import BasicCircuitValidator
from .component_values import (
    CAPACITANCE_MAX,
    CAPACITANCE_MIN,
    INDUCTANCE_MAX,
    INDUCTANCE_MIN,
    RESISTANCE_MAX,
    RESISTANCE_MIN,
    ComponentValueValidationResult,
    ComponentValueValidator,
    validate_capacitance,
    validate_inductance,
    validate_resistance,
)
from .electrical import ShortCircuitDetector
from .power import PowerAnalyzer, PowerAnalysisResult, ComponentPowerInfo
from .validator import CircuitValidator

__all__ = [
    "ValidationRule",
    "ValidationResult",
    "ShortCircuitDetector",
    "BasicCircuitValidator",
    "PowerAnalyzer",
    "PowerAnalysisResult",
    "ComponentPowerInfo",
    "CircuitValidator",
    "ComponentValueValidator",
    "ComponentValueValidationResult",
    "validate_resistance",
    "validate_capacitance",
    "validate_inductance",
    "RESISTANCE_MIN",
    "RESISTANCE_MAX",
    "CAPACITANCE_MIN",
    "CAPACITANCE_MAX",
    "INDUCTANCE_MIN",
    "INDUCTANCE_MAX",
]
