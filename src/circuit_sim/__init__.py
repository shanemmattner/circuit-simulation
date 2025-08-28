"""
Circuit Simulation Library

A simple, intuitive Python API for electronic circuit simulation.
"""

__version__ = "0.1.0"

from .circuit import Circuit, SimulationResults
from .simulator import SimulationEngine

__all__ = [
    "Circuit",
    "SimulationResults",
    "SimulationEngine",
]
