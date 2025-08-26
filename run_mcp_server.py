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
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from circuit_mcp.server import CircuitSimulationMCPServer


def setup_logging():
    """Configure logging for the server."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr),
            logging.FileHandler('mcp_server.log')
        ]
    )


def load_config():
    """Load server configuration."""
    config_path = Path(__file__).parent / "mcp_server_config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}


async def main():
    """Main entry point."""
    setup_logging()
    config = load_config()
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Circuit Simulation MCP Server")
    logger.info(f"Configuration: {config.get('name', 'default')}")
    
    # Create and run server
    server = CircuitSimulationMCPServer(
        name=config.get("name", "circuit-simulation-server")
    )
    
    logger.info("Server initialized, ready for connections")
    logger.info("Connect via stdio - waiting for MCP client...")
    
    try:
        await server.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        logger.info("Server stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)