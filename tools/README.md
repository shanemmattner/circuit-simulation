# Tools and Configuration

This directory contains operational tools and configuration:

## Structure

- **config/** - Configuration files (MCP server, nginx)
- **deployment/** - Docker and deployment configurations  
- **scripts/** - Utility scripts and tools
- **run_mcp_server.py** - MCP server for AI integration

## Usage

### MCP Server
```bash
# Start MCP server
python tools/run_mcp_server.py

# Connect to Claude Code
claude mcp add circuit-simulation -- python tools/run_mcp_server.py
```

### Docker Deployment
```bash
# Development
docker-compose -f tools/deployment/docker-compose.yml up

# Production API
docker-compose -f tools/deployment/docker-compose.fastapi.yml up -d
```

### Scripts
```bash
# Validate setup
python tools/scripts/validation/validate_setup.py

# Run robust tests  
python tools/scripts/run_robust_tests.py
```