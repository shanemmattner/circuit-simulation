# Circuit Simulation Platform

Modern Python-based circuit simulation platform with interactive reporting and AI-ready architecture.

## Features

- 🔌 Simple Python API for circuit definition
- ⚡ Fast simulation with Ngspice/Xyce backends  
- 📊 Interactive Plotly reports
- 🎓 Educational content and tutorials
- 🤖 MCP-ready for AI integration
- 🐳 Docker deployment ready

## Quick Start

```python
from circuit_sim import Circuit

# Create a simple RC circuit
circuit = Circuit("RC Filter")
circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
circuit.add_capacitor("C1", node1=2, node2=0, capacitance="1u")

# Run simulation
results = circuit.simulate(analysis="transient", stop_time="10ms", step_time="10us")

# Plot results
results.plot()
```

## Installation

### Option 1: Using Docker (Recommended - No System Conflicts!)
```bash
# Clone the repository
git clone https://github.com/circuit-synth/circuit-simulation.git
cd circuit-simulation

# Build and run with Docker
./docker/run_simulation.sh build
./docker/run_simulation.sh demo

# Or use docker-compose directly
docker-compose build
docker-compose run circuit-sim python examples/quick_start.py
```

### Option 2: Local Installation
```bash
# Clone the repository
git clone https://github.com/circuit-synth/circuit-simulation.git
cd circuit-simulation

# Install with pip
pip install -e .

# Or use uv (faster)
uv pip install -e .

# Install ngspice (required for simulations)
# Ubuntu/Debian: sudo apt-get install ngspice libngspice0-dev
# macOS: brew install ngspice
# Windows: Download from http://ngspice.sourceforge.net/
```

### Option 3: Using pip (coming soon)
```bash
pip install circuit-sim
```

## Documentation

See the [docs/](docs/) folder for detailed documentation:
- [Product Requirements](docs/PRD.md)
- [Research Notes](docs/RESEARCH_NOTES.md)
- [Simulator Comparison](docs/SIMULATOR_COMPARISON.md)
- [Educational Content](docs/EDUCATION_CONTENT.md)

## Development

See [CLAUDE.md](CLAUDE.md) for development workflow and guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.