"""Op-amp amplifier circuit examples."""

from .circuit import OpAmpCircuit, InstrumentationAmplifier, ActiveFilter, Comparator
from .simulation import simulate_opamp, calculate_frequency_response, calculate_transient_response
from .analysis import analyze_amplifier, calculate_gain_bandwidth, compare_amplifiers
from .report import generate_amplifier_report

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
