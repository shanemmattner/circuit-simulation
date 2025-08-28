"""Op-amp amplifier circuit examples."""

from .analysis import analyze_amplifier, calculate_gain_bandwidth, compare_amplifiers
from .circuit import ActiveFilter, Comparator, InstrumentationAmplifier, OpAmpCircuit
from .report import generate_amplifier_report
from .simulation import (
    calculate_frequency_response,
    calculate_transient_response,
    simulate_opamp,
)

__all__ = [
    "OpAmpCircuit",
    "InstrumentationAmplifier",
    "ActiveFilter",
    "Comparator",
    "simulate_opamp",
    "calculate_frequency_response",
    "calculate_transient_response",
    "analyze_amplifier",
    "calculate_gain_bandwidth",
    "compare_amplifiers",
    "generate_amplifier_report",
]
