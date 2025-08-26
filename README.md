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

### Using pip (coming soon)
```bash
pip install circuit-sim
```

### From source
```bash
git clone https://github.com/circuit-synth/circuit-simulation.git
cd circuit-simulation
pip install -e .
```

### Using Docker (coming soon)
```bash
docker run -p 8000:8000 circuit-simulation
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