# macOS Setup Guide for Circuit Simulation Library

## System Requirements

- **macOS**: 12.0+ (Monterey or later)
- **Architecture**: Intel (x86_64) or Apple Silicon (ARM64/M1/M2/M3)
- **Python**: 3.10+ 
- **Docker Desktop**: 4.0+ (optional, for containerized environment)
- **Homebrew**: Latest version

## Quick Start (Native Installation)

### 1. Install ngspice via Homebrew

```bash
brew install ngspice
```

Verify installation:
```bash
ngspice --version
# Should show: ngspice-44.2 or similar
```

### 2. Set up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 3. Install Dependencies

```bash
# Install project requirements
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install circuit-sim in development mode
pip install -e .
```

### 4. Test the Installation

```bash
# Test basic functionality
python test_circuit_functions.py

# Run comprehensive tests
python examples/test_docker_ngspice.py

# Run simulation demo
python examples/simulation_demo.py
```

## MCP Server Setup

### Running the MCP Server

```bash
source venv/bin/activate
python run_mcp_server.py
```

### Testing MCP Server

In a new terminal:
```bash
source venv/bin/activate
python test_mcp_server.py
```

### Claude Desktop Integration

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "circuit-simulation": {
      "command": "python3",
      "args": ["run_mcp_server.py"],
      "cwd": "/Users/YOUR_USERNAME/Desktop/circuit-simulation",
      "env": {
        "PYTHONPATH": "/Users/YOUR_USERNAME/Desktop/circuit-simulation"
      }
    }
  }
}
```

## Docker Setup (Optional)

### Building Docker Image

The Docker setup provides a consistent environment across platforms:

```bash
# Clean Docker cache if needed
docker system prune -a

# Build the image
docker-compose build circuit-sim

# Run tests in Docker
docker-compose run --rm circuit-sim python test_circuit_functions.py
```

### Docker Issues on Apple Silicon

If you encounter issues on M1/M2/M3 Macs:

1. Docker runs x86_64 containers via Rosetta 2 emulation
2. Performance may be slower than native
3. Use `--platform=linux/amd64` in Dockerfile

## Known Issues & Solutions

### Issue 1: "Warning: can't find the initialization file spinit"

**Solution**: This is a harmless warning. Create an empty spinit file to suppress:
```bash
touch ~/.spiceinit
```

### Issue 2: "Unsupported Ngspice version 44"

**Solution**: This is a PySpice compatibility notice. The library still works correctly with ngspice 44.

### Issue 3: KiCad Conflicts

If you have KiCad installed, it may conflict with ngspice:
```bash
# Check which ngspice is being used
which ngspice

# Ensure Homebrew's ngspice is used
export PATH="/opt/homebrew/bin:$PATH"
```

### Issue 4: Python 3.13 Compatibility

If using Python 3.13, you may see deprecation warnings. These can be safely ignored or use Python 3.11:
```bash
brew install python@3.11
python3.11 -m venv venv
```

## Development Workflow

### 1. Running Tests

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/ --fix

# Run tests with coverage
pytest --cov=src --cov-report=term-missing -v
```

### 2. Running Examples

```bash
# Generate circuit plots
python examples/generate_plots.py

# Run plotting demo
python examples/plotting_demo.py

# Test MCP integration
python examples/mcp_client_example.py
```

### 3. Starting Services

```bash
# Start MCP server
python run_mcp_server.py

# Start FastAPI (when implemented)
uvicorn src.api.main:app --reload

# Start Jupyter notebook
jupyter notebook
```

## Performance Tips

### Native vs Docker

- **Native installation**: ~10x faster on Apple Silicon
- **Docker**: Better isolation, consistent environment
- **Recommendation**: Use native for development, Docker for testing

### Optimizations for Apple Silicon

1. Use native ARM64 packages when available
2. Avoid x86_64 emulation in Docker
3. Use `scipy` and `numpy` with Apple Accelerate framework:
   ```bash
   pip install numpy scipy --no-binary :all: --no-cache-dir
   ```

## Troubleshooting

### Check Installation

```bash
# Verify all components
python -c "
import PySpice
import numpy as np
import matplotlib
from circuit_sim import Circuit
print('✅ All imports successful')
"
```

### Reset Environment

```bash
# Clean and reinstall
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pip install -e .
```

### Debug MCP Server

```bash
# Run with debug output
MCP_DEBUG=1 python run_mcp_server.py

# Check server is responding
echo '{"jsonrpc": "2.0", "method": "list_tools", "id": 1}' | python run_mcp_server.py
```

## Support

For issues specific to macOS:
1. Check this guide first
2. Review [GitHub Issues](https://github.com/circuit-simulation/issues)
3. Post detailed error messages including:
   - macOS version
   - Python version
   - ngspice version
   - Full error traceback

## Next Steps

1. ✅ Circuit simulation working
2. ✅ MCP server operational
3. 🚧 Implement CLI with progress bars
4. 🚧 Create 10 working example circuits
5. 🚧 Build FastAPI web service
6. 🚧 Production deployment

---
*Last Updated: November 2024*
*Tested on: macOS 15.0, Apple M2, Python 3.13, ngspice 44.2*