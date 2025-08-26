"""
MCP (Model Context Protocol) server for circuit simulation.

This module provides an MCP interface to the circuit simulation library,
enabling AI assistants to design, simulate, and analyze circuits.
"""

from .server import CircuitSimulationMCPServer

__all__ = ["CircuitSimulationMCPServer"]
__version__ = "1.0.0"