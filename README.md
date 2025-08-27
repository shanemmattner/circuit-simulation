# Circuit Simulation Platform ⚡

Professional circuit simulation with REST API, CLI tools, and AI integration.

## Features

- **⚡ Simulation Engine**: PySpice + ngspice for DC, transient, AC analysis
- **🖥️ CLI Interface**: Professional command-line tools with progress bars  
- **🌐 REST API**: FastAPI with WebSocket, job management, interactive docs
- **🤖 AI Integration**: MCP server for Claude Code/Desktop integration
- **📊 Reports**: Interactive Plotly charts, professional HTML reports
- **📥 Import**: KiCad netlists, SPICE files, circuit-synth JSON
- **📚 Example Library**: 10 complete circuits with comprehensive documentation
- **🔌 50k+ Components**: KiCad-Spice-Library integration with real models
- **🐳 Production Ready**: Docker deployment, Redis/Celery backend

## Quick Start

```bash
# Install and test
uv install
uv run circuit-sim init --name "My Project"
uv run circuit-sim create --netlist examples/rc_filter.cir --name "RC Filter"

# Start API server  
uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000
open http://localhost:8000/docs

# Docker deployment
docker-compose -f deployment/docker-compose.fastapi.yml up -d --build
```

## Features

- **⚡ Simulation Engine**: PySpice + ngspice for DC, transient, AC analysis
- **🖥️ CLI Interface**: Professional command-line tools with progress bars  
- **🌐 REST API**: FastAPI with WebSocket, job management, interactive docs
- **🤖 AI Integration**: MCP server for Claude Code/Desktop integration
- **📊 Reports**: Interactive Plotly charts, professional HTML reports
- **📥 Import**: KiCad netlists, SPICE files, circuit-synth JSON
- **🐳 Production Ready**: Docker deployment, Redis/Celery backend

## Usage

### Python Library
```python
from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine

# Define circuit
circuit = (Circuit("RC Filter")
    .add_voltage_source("V1", 1, 0, "5V")
    .add_resistor("R1", 1, 2, "1k") 
    .add_capacitor("C1", 2, 0, "1u"))

# Simulate and plot
results = SimulationEngine().simulate_dc(circuit)
print(f"Output: {results.voltage(2)[0]:.2f}V")
results.plot()
```

### Advanced Visualizations
```python
from circuit_sim.visualization import (
    NyquistPlotter, SmithChartPlotter, NicholsPlotter, InteractivePlotter,
    PlotStyle
)

# Professional Nyquist plot for stability analysis
nyquist = NyquistPlotter(style=PlotStyle.professional())
result = nyquist.plot(
    transfer_function=tf, 
    frequencies=frequencies, 
    show_stability=True,
    mark_frequencies=[1, 10, 100]
)
print(f"System stable: {result.metadata['stability_analysis']['is_stable']}")
print(f"Encirclements: {result.metadata['stability_analysis']['encirclements']}")

# Smith chart for RF impedance matching (50Ω reference)
smith = SmithChartPlotter(z0=50.0) 
smith_result = smith.plot(
    impedances=impedances,
    frequencies=rf_frequencies,
    show_vswr_circles=True,
    vswr_values=[1.5, 2.0, 3.0]
)
print(f"Best VSWR: {min(smith_result.data['vswr']):.2f}")

# Nichols chart for control system design
nichols = NicholsPlotter()
nichols.plot(
    transfer_function=open_loop_tf,
    frequencies=frequencies,
    show_margins=True,
    show_grid=True
)

# Interactive multi-trace Bode plots
interactive = InteractivePlotter()
html = interactive.create_multi_trace_bode(
    frequencies=frequencies,
    transfer_functions={
        "Original": tf1,
        "Compensated": tf2,
        "Final": tf3
    },
    title="Control System Comparison"
)
with open("analysis.html", "w") as f:
    f.write(html)
# Open in browser for interactive exploration
```

### REST API
```bash
# Create circuit
curl -X POST http://localhost:8000/api/circuits \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "components": [...]}'

# Start simulation  
curl -X POST http://localhost:8000/api/circuits/{id}/simulate \
  -d '{"type": "dc"}'
```

### CLI Commands
```bash
circuit-sim init --name "Project"     # Initialize project
circuit-sim create --netlist file.cir # Create from SPICE
circuit-sim list                       # List circuits  
circuit-sim simulate "name" --type dc  # Run simulation
circuit-sim info                       # System info
```

## Installation

### Docker (Recommended)
```bash
git clone <repo>
cd circuit-simulation
docker-compose -f deployment/docker-compose.fastapi.yml up -d --build
```

### Local Development
```bash
# Dependencies
uv install  # or pip install -r requirements.txt

# Install ngspice
# macOS: brew install ngspice  
# Ubuntu: sudo apt install ngspice libngspice0-dev

# Run tests
uv run pytest
```

## Architecture

- **`src/circuit_sim/`** - Core library (Circuit, SimulationEngine)
- **`src/api/`** - FastAPI web service  
- **`src/circuit_mcp/`** - MCP server for AI integration
- **`src/io/`** - Import/export (KiCad, SPICE, circuit-synth)
- **`tests/`** - Comprehensive test suite
- **`examples/`** - Demos, tests, sample circuits
- **`deployment/`** - Docker, compose files
- **`docs/`** - Documentation, guides

## API Endpoints

- **`GET /health`** - Health check
- **`GET /docs`** - Interactive API docs
- **`POST /api/circuits`** - Create circuit  
- **`POST /api/circuits/{id}/simulate`** - Start simulation
- **`GET /api/simulations/{job_id}`** - Job status
- **`WS /ws/simulation/{job_id}`** - Real-time updates

## Testing

- **Manual Testing**: See `TESTING_GUIDE.md`
- **Unit Tests**: `uv run pytest` 
- **API Tests**: `uv run python examples/tests/test_api_client.py`
- **MCP Tests**: `uv run python examples/tests/test_mcp_server.py`

## Documentation

- **`TESTING_GUIDE.md`** - Comprehensive manual testing
- **`CLAUDE.md`** - Development guidelines  
- **`docs/`** - Technical documentation
- **`/docs`** endpoint - Interactive API reference

## Development

```bash
# Quality checks
uv run black src/ tests/           # Format code
uv run ruff check src/ tests/      # Lint code  
uv run mypy src/ --strict          # Type check
uv run pytest --cov=src           # Test with coverage

# MCP integration
claude mcp add circuit-simulation -- uv run python run_mcp_server.py
```

## Testing

- **Manual Testing**: See `TESTING_GUIDE.md`
- **Unit Tests**: `uv run pytest` 
- **API Tests**: `uv run python examples/tests/test_api_client.py`
- **MCP Tests**: `uv run python examples/tests/test_mcp_server.py`
- **Regression Test**: Use `.claude/commands/regression_test.md`

## Documentation

- **`TESTING_GUIDE.md`** - Comprehensive manual testing
- **`CLAUDE.md`** - Development guidelines  
- **`docs/`** - Technical documentation
- **`/docs`** endpoint - Interactive API reference

## License

MIT License - see LICENSE file.
