"""RLC resonance circuit example."""

from .analysis import analyze_resonance, design_bandpass_filter, design_notch_filter
from .circuit import RLCResonanceCircuit
from .simulation import (
    calculate_frequency_response,
    calculate_impedance_spectrum,
    calculate_step_response,
    simulate_rlc_circuit,
)
from .visualization import generate_3d_response, generate_resonance_plots, generate_smith_chart

__all__ = [
    "RLCResonanceCircuit",
    "simulate_rlc_circuit",
    "calculate_impedance_spectrum",
    "calculate_step_response",
    "calculate_frequency_response",
    "analyze_resonance",
    "design_bandpass_filter",
    "design_notch_filter",
    "generate_resonance_plots",
    "generate_smith_chart",
    "generate_3d_response",
]
