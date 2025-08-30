"""
Circuit Simulation Library

A simple, intuitive Python API for electronic circuit simulation.
"""

__version__ = "0.1.0"

from .circuit import Circuit, SimulationResults
from .simulator import SimulationEngine
from .circuit_synth_integration import simulate_from_circuit_synth, CircuitSynthError

__all__ = [
    "Circuit",
    "SimulationResults",
    "SimulationEngine",
    "simulate_from_circuit_synth",
    "CircuitSynthError",
]
