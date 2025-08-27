# Circuit Simulation Library 🔌

A professional Python library for electronic circuit simulation with an easy-to-use API, Docker support, and beautiful visualizations.

## Features ✨

- **Simple API**: Define circuits with human-readable component values
- **Real Simulations**: Powered by PySpice and ngspice 
- **🖥️ Professional CLI**: Complete command-line interface with progress bars
- **Docker Support**: No installation conflicts, works everywhere
- **Visualization**: Generate publication-quality plots
- **🤖 MCP Integration**: Full AI assistant integration via Model Context Protocol
- **🔧 Claude Code Ready**: Connect directly to Claude Code with `claude mcp add`
- **Comprehensive Testing**: 85%+ code coverage with validation scripts
- **Production Ready**: Type hints, formatting, linting configured
- **🍎 macOS Native**: Optimized setup and testing for Apple Silicon

## Quick Start 🚀

### Command Line Interface

```bash
# Install the package
pip install circuit-sim

# Initialize a new project
circuit-sim init --name "My Project"

# Create a circuit from netlist
circuit-sim create --netlist examples/rc_filter.cir --name "RC Filter"

# Get system information
circuit-sim info

# Get help
circuit-sim --help
```

### Python API

```python
from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine

# Create a voltage divider
circuit = (
    Circuit("Voltage Divider")
    .add_voltage_source("V1", 1, 0, "10V")
    .add_resistor("R1", 1, 2, "1k")    # 1kΩ
    .add_resistor("R2", 2, 0, "1k")    # 1kΩ
)

# Simulate DC operating point
engine = SimulationEngine()
results = engine.simulate_dc(circuit)

# Display results
print(f"Node 2 voltage: {results.voltage(2)[0]:.2f}V")  # 5.00V
results.plot()
```

## Installation

### Using Docker (Recommended)

```bash
# Build the Docker image
docker-compose build

# Run a simulation
docker-compose run circuit-sim python3 examples/quick_start.py

# Generate plots
docker-compose run circuit-sim python3 examples/generate_plots.py

# View the plots
xdg-open examples/output/
```

### Local Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Install ngspice (required for simulations)
# Ubuntu/Debian: sudo apt-get install ngspice libngspice0-dev
# macOS: brew install ngspice
# Windows: Download from http://ngspice.sourceforge.net/

# Run tests
pytest
```

## Usage Examples 💡

### Voltage Divider
```python
circuit = (
    Circuit("Voltage Divider")
    .add_voltage_source("V1", 1, 0, "10V")
    .add_resistor("R1", 1, 2, "2.2k")
    .add_resistor("R2", 2, 0, "3.3k")
)
```

### RC Filter
```python
circuit = (
    Circuit("RC Filter")
    .add_voltage_source("V1", 1, 0, "5V")
    .add_resistor("R1", 1, 2, "10k")
    .add_capacitor("C1", 2, 0, "100nF")
)
```

## Command Line Interface 🖥️

The `circuit-sim` CLI provides professional circuit simulation tools with progress bars and colored output.

### Available Commands

```bash
# Project Management
circuit-sim init --name "My Project"       # Initialize new project
circuit-sim info                           # Show system information  
circuit-sim list                           # List all circuits
circuit-sim show <circuit-id>              # Show circuit details

# Circuit Operations
circuit-sim create --netlist <file> --name <name>  # Create from netlist

# Simulation
circuit-sim simulate dc --circuit-id <id>           # DC analysis
circuit-sim simulate transient --circuit-id <id>    # Time-domain analysis

# Help
circuit-sim --help                         # Show all commands
circuit-sim simulate --help                # Simulation options
```

### Project Workflow

```bash
# 1. Initialize project
circuit-sim init --name "Audio Amplifier"

# 2. Create circuit from SPICE netlist
circuit-sim create --netlist amplifier.cir --name "Class A Amplifier"
# ✅ Circuit 'Class A Amplifier' created successfully!
# 🆔 Circuit ID: a1b2c3d4
# 📁 Netlist: amplifier.cir

# 3. Get system info
circuit-sim info
```

### Progress Indicators

All operations show beautiful progress bars powered by Rich:

```
🔄 Validating netlist... ████████████████████████████████████████ 100%
🔄 Creating circuit...   ████████████████████████████████████████ 100%
✅ Circuit created successfully!
```

## Supported Components 🔧

- **Resistors**: `add_resistor("R1", n1, n2, "1k")`
- **Capacitors**: `add_capacitor("C1", n1, n2, "10uF")`
- **Inductors**: `add_inductor("L1", n1, n2, "100mH")`
- **Voltage Sources**: `add_voltage_source("V1", n1, n2, "5V")`
- **Current Sources**: `add_current_source("I1", n1, n2, "10mA")`

## 🤖 AI Integration with Claude Code

### Connect MCP Server to Claude Code

```bash
# Add the circuit simulation MCP server
claude mcp add circuit-simulation -- uv run python run_mcp_server.py

# Verify connection
claude mcp list
```

### Available MCP Tools
- **circuit.create** - Create new circuits
- **circuit.add_component** - Add resistors, capacitors, voltage sources, etc.
- **circuit.list** - List all circuits
- **circuit.get** - Get circuit details
- **circuit.validate** - Validate circuit connectivity
- **simulation.run_dc** - Run DC operating point analysis
- **simulation.run_transient** - Run time-domain analysis
- **analysis.get_results** - Get simulation results with plots

### Example Claude Code Usage

Ask Claude Code to:
- "Create a voltage divider circuit and simulate it"
- "Build an RC low-pass filter and analyze its frequency response"
- "Design a precision instrumentation amplifier with guard ring"

## Visualization 📈

Generate and save plots:

```python
# Plot all node voltages
results.plot()

# Plot specific signals
results.plot("V(2)", "V(3)")

# Save to file
results.plot(save_to="output.png", show=False)
```

View example plots in `examples/output/`:
- Voltage divider DC analysis
- RC circuit charging curves
- RL circuit response
- Frequency response plots

## Testing 🧪

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src --cov-report=term-missing

# In Docker
docker-compose run circuit-sim pytest
```

Current test coverage: **76%** ✅

## Development 🛠️

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type checking
mypy src/ --strict
```

### Project Structure

```
circuit-simulation/
├── src/circuit_sim/     # Core library
│   ├── circuit.py       # Circuit definition
│   ├── parser.py        # Value parsing
│   └── simulator/       # Simulation engine
├── examples/            # Example scripts
├── tests/              # Test suite (76% coverage)
├── docker/             # Docker configurations
└── notebooks/          # Jupyter notebooks
```

## MCP Server (AI Integration) 🤖

The library includes a Model Context Protocol server for AI assistant integration:

### Connect to Claude Code
Add the MCP server directly to your Claude Code project:
```bash
# From project root directory
claude mcp add circuit-simulation -- python3 run_mcp_server.py

# Verify it's added
claude mcp list
```

### Connect to Claude Desktop
Add to your Claude Desktop configuration:
```json
{
  "mcpServers": {
    "circuit-simulation": {
      "command": "python3", 
      "args": ["run_mcp_server.py"],
      "cwd": "/path/to/circuit-simulation"
    }
  }
}
```

### Test MCP Server
```bash
# Test core functions
python3 test_circuit_functions.py

# Test in Docker
docker-compose run circuit-sim python3 test_circuit_functions.py
```

### Available MCP Tools
- `circuit.create` - Create new circuits
- `circuit.add_component` - Add R, L, C, voltage/current sources
- `circuit.validate` - Check circuit topology
- `simulation.run_dc` - DC operating point analysis
- `simulation.run_transient` - Time-domain simulation
- `analysis.get_results` - Retrieve simulation data

## Roadmap 🗺️

- [x] Basic circuit API
- [x] DC analysis  
- [x] Transient analysis
- [x] Plotting support
- [x] Docker environment
- [x] **MCP server integration** ✅ NEW!
- [ ] AC frequency analysis
- [ ] Web UI
- [ ] Parameter sweeping
- [ ] Monte Carlo analysis

## Contributing 🤝

See [CLAUDE.md](CLAUDE.md) for development workflow and [DEVELOPMENT.md](DEVELOPMENT.md) for setup instructions.

## License 📄

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments 🙏

Built with:
- [PySpice](https://pyspice.fabrice-salvaire.fr/)
- [ngspice](http://ngspice.sourceforge.net/)
- [matplotlib](https://matplotlib.org/)
- [Docker](https://www.docker.com/)