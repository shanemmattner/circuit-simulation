"""Transistor amplifier examples."""

from .circuit import TransistorAmplifierCircuit
from .simulation import simulate_transistor_amp, calculate_bias_point
from .design import design_common_emitter

__all__ = [
    "TransistorAmplifierCircuit",
    "simulate_transistor_amp",
    "calculate_bias_point",
    "design_common_emitter",
]
