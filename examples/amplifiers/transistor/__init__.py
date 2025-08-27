"""Transistor amplifier examples."""

from .circuit import TransistorAmplifierCircuit
from .design import design_common_emitter
from .simulation import calculate_bias_point, simulate_transistor_amp

__all__ = [
    "TransistorAmplifierCircuit",
    "simulate_transistor_amp",
    "calculate_bias_point",
    "design_common_emitter",
]
