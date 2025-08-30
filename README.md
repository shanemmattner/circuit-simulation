# Circuit Simulation Platform ⚡

Professional circuit simulation with REST API, CLI tools, and AI integration.

## Features

- **⚡ Simulation Engine**: PySpice + ngspice for DC, transient, AC analysis
- **🔍 Circuit Validation**: Advanced short circuit detection with pathfinding algorithms
- **🔋 Power Analysis**: Complete power dissipation analysis with component rating validation
- **🖥️ CLI Interface**: Professional command-line tools with progress bars  
- **🌐 REST API**: FastAPI with WebSocket, job management, interactive docs
- **🎨 Analysis Dashboard**: Web-based GUI for multi-tab analysis (DC/AC/Transient)
- **🤖 AI Integration**: MCP server with 10 tools for Claude Code/Desktop integration
- **📊 Reports**: Interactive Plotly charts, professional HTML reports with power analysis
- **📥 Smart Import**: Intelligent KiCad netlist parsing with automatic SPICE model assignment
- **🧠 Model Intelligence**: 90%+ component coverage - transistors, diodes, op-amps, logic gates auto-mapped
- **🔗 Circuit-Synth Integration**: Seamless integration with circuit-synth for design-to-simulation workflow
- **📚 Example Library**: 10 complete circuits with comprehensive documentation
- **🔌 50k+ Components**: Full KiCad-Spice-Library integration with intelligent component mapping
- **🐳 Production Ready**: Docker deployment, Redis/Celery backend

## Quick Start

### **🚀 Easy Launch Options**

#### **🎓 Interactive Learning (Recommended)**
```bash
# One command to start everything:
./learn.sh
# Opens http://localhost:8888 with working simulation!
```

#### **⚡ Quick Launch (if container exists)**
```bash
make learn-quick
# or
./quick-learn.sh
```

#### **🔧 All Available Commands**
```bash
make help              # Show all available commands
make learn             # Full learning environment setup
make test-sim          # Test simulation backend  
make clean             # Clean up containers
```

### **🐳 Manual Docker Commands (Advanced)**
```bash
# Build container
make build-container

# Test simulation
docker exec circuit-sim python test_interactive_learning.py

# Manual access
docker exec -it circuit-sim bash

# Production API
docker-compose -f deployment/docker-compose.fastapi.yml up -d
```

### Alternative: Local Development (No Simulation)
```bash
# Install dependencies (CLI and educational content work, simulation shows demo mode)
uv install
uv run circuit-sim init --name "My Project"  # CLI works
uv run jupyter lab docs/learning_modules/    # Educational content works
```

## Features

- **⚡ Simulation Engine**: PySpice + ngspice for DC, transient, AC analysis
- **🖥️ CLI Interface**: Professional command-line tools with progress bars  
- **🌐 REST API**: FastAPI with WebSocket, job management, interactive docs
- **🤖 AI Integration**: MCP server for Claude Code/Desktop integration
- **📊 Reports**: Interactive Plotly charts, professional HTML reports
- **📥 Smart Import**: Intelligent KiCad netlist parsing with automatic SPICE model assignment
- **🐳 Production Ready**: Docker deployment, Redis/Celery backend

## Usage

### Python Library
```python
from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine

# Define circuit with advanced components
circuit = (Circuit("Amplifier Circuit")
    .add_voltage_source("VCC", 4, 0, "12V")
    .add_resistor("R1", 1, 2, "10k")
    .add_bjt_transistor("Q1", collector=3, base=2, emitter=0, model="2N3904")
    .add_resistor("RC", 4, 3, "1k")
    .add_capacitor("C1", 1, 0, "100uF"))

# Simulate and plot  
results = SimulationEngine().simulate_dc(circuit)
print(f"Output: {results.voltage(3)[0]:.2f}V")
results.plot()
```

### Smart KiCad Import
```python
from src.io.parsers.kicad_parser import KiCadParser

# Import KiCad netlist with automatic model assignment
parser = KiCadParser()
result = parser.parse_content_with_result(kicad_netlist_content)

print(result.summary())  # Shows what was imported successfully
# ✅ Import successful: 5/5 components
#   ✓ Q1: bjt_transistor (model: 2N3904)  
#   ✓ D1: diode (model: 1N4148)
#   ✓ U1: opamp (model: LM358)

circuit = result.circuit  # Ready for simulation!
```

### Circuit-Synth Plugin-Based Integration 🔗

#### **New! Plugin-Based Simulation System** 🚀

Write normal circuit-synth code and call `simulate()` to get professional reports with plots!

```python
from circuit_synth import circuit, Component, Net

@circuit
def rc_filter():
    """Simple RC low-pass filter."""
    vin = Net("VIN")
    vout = Net("VOUT")
    gnd = Net("GND")
    
    r1 = Component("Device:R", ref="R1", value="1k", pins={1: vin, 2: vout})
    c1 = Component("Device:C", ref="C1", value="100n", pins={1: vout, 2: gnd})

# Your vision realized - just call simulate!
my_circuit = rc_filter()
report = my_circuit.simulate_with_plugins()  # ✨ That's it!
```

**Plugin System Features:**
- **🔌 Extensible Architecture**: Add new analysis types or output formats via plugins
- **📊 Analysis Plugins**: DC, AC (with Bode plots), Transient
- **📄 Format Plugins**: Interactive HTML reports, JSON data export  
- **⚙️ Configuration-Driven**: YAML-based configuration, no hard-coding
- **🎯 Simple API**: Your requested "write circuit → call simulate → get reports" workflow

**Available API Calls:**
```python
# Run all analyses with HTML output (default)
circuit.simulate_with_plugins()

# Specific analysis type
circuit.simulate_with_plugins(analysis='ac')  # Frequency response with Bode plots

# Export as JSON data
circuit.simulate_with_plugins(format='json')

# Multiple analyses
circuit.simulate_with_plugins(analysis=['dc', 'ac', 'transient'])

# Custom configuration
circuit.simulate_with_plugins(config={'ac': {'start_freq': '1Hz', 'stop_freq': '1MHz'}})
```

#### **Legacy Direct Integration**

For direct circuit-simulation backend usage:

```python
from circuit_sim.circuit_synth_integration import simulate_from_circuit_synth

# Load circuit-synth JSON output
with open("amplifier.json", "r") as f:
    circuit_data = json.load(f)

# Direct simulation with intelligent component mapping
results = simulate_from_circuit_synth(circuit_data)

# Smart features:
# ✅ 50,093+ SPICE models from KiCad-Spice-Library
# ✅ Intelligent component resolution (2N3904, 1N4148, etc.)
# ✅ Confidence-scored fallback chain (exact → pattern → default)
# ✅ Professional built-in models for common components
# ✅ Complete independence - libraries communicate via JSON only
```

**Supported Components:**
- **Passive**: R, L, C (direct value mapping)
- **Active**: BJT transistors (NPN/PNP), MOSFETs (N/P-channel), diodes
- **Integrated**: Op-amps with multi-unit support (LM358, etc.)
- **Smart Fallbacks**: Unknown components use intelligent defaults

**Architecture**: Libraries remain completely independent with JSON-only communication, enabling circuit-synth to optionally use circuit-simulation as a simulation backend while maintaining clean separation of concerns.

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

### Power Analysis
```python
# Built-in power analysis
from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine

circuit = Circuit("Power Test")
circuit.add_voltage_source("V1", 1, 0, "12V")
circuit.add_resistor("R1", 1, 0, "100")  # 100Ω

results = SimulationEngine().simulate_dc(circuit)
power_analysis = results.analyze_power(circuit)

print(f"Total Power: {power_analysis.total_power:.3f}W")
for name, info in power_analysis.component_power.items():
    print(f"{name}: {info.power:.3f}W @ {info.voltage:.1f}V")

# Component rating validation
ratings = {"R1": 0.25}  # 1/4W rating
analysis = results.analyze_power(circuit, ratings)
if not analysis.is_valid:
    for issue in analysis.issues:
        print(f"Issue: {issue.message}")
```

### Interactive Power Reports
```bash
# Generate comprehensive power analysis with Plotly visualizations
python test_power_interactive.py
# Opens: power_analysis_report.html (interactive dashboard)
# Opens: power_analysis_detailed_report.html (component tables)
```

### CLI Commands
```bash
circuit-sim init --name "Project"     # Initialize project
circuit-sim create --netlist file.cir # Create from SPICE
circuit-sim list                       # List circuits  
circuit-sim simulate "name" --type dc  # Run simulation
circuit-sim info                       # System info
```

### Analysis Dashboard 🎨
Professional web-based GUI for comprehensive circuit analysis:
```bash
# Start dashboard
python src/gui/app.py
# → Opens http://127.0.0.1:8051

# Current Features (v0.1):
# ✅ Multi-tab interface: DC | AC | Transient | Reports | Jobs
# ✅ Real-time circuit loading from FastAPI backend
# ✅ Professional card-based layouts with Bootstrap styling
# ✅ Comprehensive logging system (logs/gui_session.log)
# ✅ Circuit selection with live API integration

# Coming Soon:
# 🔄 Real-time simulation monitoring with WebSocket progress
# 📊 Interactive Plotly charts embedded in tabs
# 🚀 One-click simulation execution from GUI
# 📋 Professional report generation and export
```

**Architecture**: Complementary analysis dashboard built with Plotly Dash that enhances the programmatic API experience. Uses existing FastAPI endpoints and WebSocket infrastructure to provide professional visualization tools for stakeholders and analysis workflows.

**Test Coverage**: 23/23 GUI tests passing with full TDD implementation.

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
