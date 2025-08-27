"""
MCP (Model Context Protocol) server for circuit simulation.

This module provides an MCP interface to the circuit simulation library,
enabling AI assistants to design, simulate, and analyze circuits.
"""

from .server import serve

__all__ = ["serve"]
__version__ = "1.0.0"
