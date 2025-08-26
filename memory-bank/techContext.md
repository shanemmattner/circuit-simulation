# Technical Context

## Technology Stack

### Core Technologies
- **Python 3.10+**: Type hints, modern async support
- **PySpice**: Python interface to SPICE simulators
- **Ngspice**: Primary simulation backend
- **Xyce**: Large circuit simulation backend (optional)
- **Plotly**: Interactive visualization library
- **FastAPI**: Modern async web framework
- **Docker**: Containerization platform
- **Redis**: Caching and job queue
- **Celery**: Distributed task queue

### Development Tools
- **pytest**: Testing framework
- **black**: Code formatter
- **ruff**: Fast Python linter
- **mypy**: Static type checking (optional)
- **coverage**: Test coverage reporting

## Development Setup

### Local Development
```bash
# Clone repository
git clone git@github.com:circuit-synth/circuit-simulation.git
cd circuit-simulation

# Initialize submodules
git submodule update --init --recursive

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements-dev.txt

# Run quality checks
black .
ruff check .
pytest
```

### Docker Development
```bash
# Build image
docker build -t circuit-simulation .

# Run container
docker run -p 8000:8000 circuit-simulation

# Development with mounted volume
docker run -p 8000:8000 -v $(pwd):/app circuit-simulation
```

## Technical Constraints

### Performance Requirements
- Simple circuits (<100 components): <1 second
- Medium circuits (100-1000): <10 seconds  
- Large circuits (1000-10000): <1 minute
- Very large (10000+): Use Xyce backend

### Memory Constraints
- Docker image size: Target <2GB
- Runtime memory: <4GB for typical use
- Model library: Lazy loading required

### Compatibility Requirements
- Python: 3.10, 3.11, 3.12
- Operating Systems: Linux, macOS, Windows (via Docker)
- Browsers: Chrome, Firefox, Safari (latest 2 versions)

## Dependencies

### Python Package Versions (Pinned)
```
pyspice==1.5.*
plotly==5.18.*
fastapi==0.104.*
redis==5.0.*
celery==5.3.*
numpy==1.24.*
pandas==2.1.*
pytest==7.4.*
black==23.12.*
ruff==0.1.*
```

### System Dependencies
- Ngspice 40+ (included in Docker)
- Xyce 7.7+ (optional, manual install)
- Redis server 7.0+

## Tool Usage Patterns

### PySpice Patterns
```python
# Basic circuit creation
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('Example')
circuit.V('input', 1, circuit.gnd, 10@u_V)
circuit.R('1', 1, 2, 1@u_kOhm)
circuit.C('1', 2, circuit.gnd, 1@u_uF)

# Simulation
simulator = circuit.simulator()
analysis = simulator.transient(
    step_time=1@u_us,
    end_time=1@u_ms
)
```

### Plotly Patterns
```python
import plotly.graph_objects as go

# Time series plot
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=time_values,
    y=voltage_values,
    mode='lines',
    name='Output Voltage'
))

# Make interactive
fig.update_layout(
    hovermode='x unified',
    xaxis_title='Time (ms)',
    yaxis_title='Voltage (V)'
)
```

### FastAPI Patterns
```python
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

app = FastAPI()

class SimulationRequest(BaseModel):
    circuit: dict
    analysis: dict

@app.post("/simulate")
async def simulate(
    request: SimulationRequest,
    background_tasks: BackgroundTasks
):
    job_id = create_job()
    background_tasks.add_task(run_simulation, job_id, request)
    return {"job_id": job_id}
```

## Configuration Management

### Environment Variables
```bash
# Simulation settings
MAX_SIMULATION_TIME=300  # seconds
DEFAULT_BACKEND=ngspice
ENABLE_XYCE=false

# API settings  
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Redis settings
REDIS_HOST=localhost
REDIS_PORT=6379

# Model library
MODEL_LIBRARY_PATH=/app/models
```

### Docker Configuration
- Multi-stage builds for size optimization
- Non-root user for security
- Health checks for orchestration
- Volume mounts for models and output

## Integration Points

### External Services
- GitHub: Source control, CI/CD
- Docker Hub: Image registry
- PyPI: Package distribution (future)
- MCP Registry: Tool registration (future)

### File Formats
- Input: JSON, SPICE netlist, KiCad schematic (future)
- Output: JSON, HTML, PDF, PNG, CSV
- Models: SPICE .lib, .mod, .subckt files