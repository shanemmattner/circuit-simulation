#!/usr/bin/env python3
"""
Run the MCP server for circuit simulation.

Usage:
    python run_mcp_server.py
    
Or with Docker:
    docker-compose run circuit-sim python3 run_mcp_server.py
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from circuit_mcp.server import serve


def main():
    """Main entry point for the MCP server."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Circuit Simulation MCP Server")
    logger.info("Server ready for MCP client connections via stdio")
    
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()