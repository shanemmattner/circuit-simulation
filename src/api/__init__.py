"""
FastAPI web service for circuit simulation.

This module provides REST API endpoints for circuit creation, simulation,
and result retrieval with WebSocket support for real-time updates.
"""

try:
    from .app import app

    __all__ = ["app"]
except ImportError:
    # For compatibility - main app is in main.py
    from .main import app

    __all__ = ["app"]
