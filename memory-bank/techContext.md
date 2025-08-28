# Technical Context

## Universal Claude Code System (NEW - August 28, 2025)

### Agent Architecture
- **memory-bank-agent**: Python-based context management with automatic token optimization
- **prd-creator**: Interactive PRD creation with user collaboration workflows
- **work-planner**: Intelligent task segmentation with 15-30 minute chunk optimization
- **tdd-implementer**: Test-driven development enforcement with pattern recording
- **prompt-optimizer**: AI prompt crafting optimization for maximum effectiveness

### Technical Infrastructure
- **Universal Deployment**: Git submodule or direct copy deployment in 5 minutes
- **Auto-Detection**: Project type detection (Python, JavaScript, Go, Rust, Java, C++)
- **Interactive Setup**: 7-10 question wizard with configuration customization
- **Memory Bank System**: Automatic creation and management of memory-bank/ structure
- **Context Optimization**: <2000 token context delivery vs 10,000+ raw file reading

### Claude Code Integration
```bash
# Universal deployment pattern
cd /path/to/any/project
git clone https://github.com/your-org/claude-code-setup .claude-system
python .claude-system/setup.py
# → Complete Claude Code setup in 5 minutes
```

### Professional Workflow Commands (Generated)
- `claude memory-context` - Get focused project context (MANDATORY first step)
- `claude create-prd` - Interactive PRD creation and management
- `claude plan-work` - Smart work breakdown with time estimation  
- `claude implement-tdd` - Test-driven implementation with memory bank updates
- `claude optimize-prompt` - AI prompt optimization for better outcomes
- `claude quality-check` - Comprehensive code quality validation

### Technology Compatibility Matrix
| Language | Auto-Detect | Formatter | Linter | Testing | Type Check |
|----------|-------------|-----------|--------|---------|------------|
| Python | ✅ pyproject.toml | black | ruff | pytest | mypy |
| JavaScript | ✅ package.json | prettier | eslint | jest | TypeScript |
| TypeScript | ✅ tsconfig.json | prettier | eslint | jest | tsc |
| Go | ✅ go.mod | gofmt | golint | go test | built-in |
| Rust | ✅ Cargo.toml | rustfmt | clippy | cargo test | built-in |
| Java | ✅ pom.xml/build.gradle | google-java-format | spotbugs | junit | built-in |

### Memory Bank Architecture
```
memory-bank/
├── projectbrief.md     # Core project mission and principles (rarely changes)
├── productContext.md   # Why project exists, target users, success metrics
├── activeContext.md    # Current session context, recent decisions, immediate goals
├── systemPatterns.md   # Established architectural patterns, design decisions
├── techContext.md      # Technical environment, dependencies, constraints
├── progress.md         # What works, what's left, known issues, milestones
└── prds/              # Product Requirements Documents
    ├── feature-a.md   # Individual feature PRDs with approval status
    ├── feature-b.md   # Implementation-ready requirements
    └── ...           # Organized by feature/epic
```

### Deployment Options
```bash
# Option 1: Git Submodule (Recommended for teams)
git submodule add https://github.com/circuit-synth/claude-code-setup .claude-system

# Option 2: Direct Copy (Standalone projects)  
git clone https://github.com/circuit-synth/claude-code-setup .claude-system

# Option 3: Download Archive (Offline setup)
curl -L https://github.com/circuit-synth/claude-code-setup/archive/main.zip -o setup.zip
unzip setup.zip && mv claude-code-setup-main .claude-system

# All options result in same 5-minute setup
python .claude-system/setup.py
```

## Circuit Simulation Technology Stack

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