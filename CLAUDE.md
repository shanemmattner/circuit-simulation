# Circuit Simulation Library - Development Guide

## 🚨 SESSION START APPROACH
**RECOMMENDED: Review existing patterns in memory-bank/ folder and follow the streamlined development workflow below.**

## Project Mission
Build a production-ready Python library for circuit simulation that professionals can depend on.

## Core Principles
- **Reliability First**: Every feature must be thoroughly tested
- **Professional Quality**: Code that's ready for enterprise use  
- **Clean Architecture**: Maintainable, extensible design
- **User-Focused**: Easy to use, hard to misuse

## Project Overview
**Name**: circuit-simulation  
**Type**: Python Library  
**Phase**: MVP Development  
**Target Users**: Professional engineers and students  
**Success Metric**: Reliable simulation of common circuits with interactive reports

## Technical Stack
- **Language**: Python 3.10+
- **Simulation**: Ngspice (primary), Xyce (large circuits)
- **Visualization**: Plotly for interactive reports
- **API Framework**: FastAPI
- **Testing**: pytest with >85% coverage
- **Type Checking**: mypy --strict
- **Formatting**: black
- **Linting**: ruff

## Development Standards

### Before Writing Code
1. Check if similar functionality exists: `grep -r "pattern" src/`
2. Review existing patterns in the codebase
3. Understand the module's architecture
4. Read relevant tests to understand expected behavior

### Code Requirements
- Every public function needs type hints
- Every module needs a docstring explaining its purpose
- Every class needs clear documentation
- Handle errors explicitly, never silent failures
- Use logging instead of print statements
- Follow existing patterns in the codebase

### Testing is Mandatory
- Write tests BEFORE implementation (TDD)
- Test the happy path AND edge cases
- Test error conditions explicitly
- Aim for >85% code coverage
- Run: `pytest --cov=src --cov-report=term-missing`

## Quality Assurance

### Pre-Commit Checklist
ALWAYS run these before committing:
```bash
# Using uv for consistency on macOS
uv run black src/ tests/
uv run ruff check src/ tests/ --fix

# Type checking  
uv run mypy src/ --strict

# Run all tests
uv run pytest -v

# Check coverage
uv run pytest --cov=src --cov-report=term-missing

# Test MCP server
uv run python test_circuit_functions.py
uv run python test_mcp_server.py
```

### Code Review Focus
- Is the code solving the right problem?
- Are errors handled properly?
- Is the code testable?
- Will this scale to 10,000 components?
- Is the API intuitive?

## Library Architecture

### Core Modules
- `src/circuit_sim/`: Main library package
  - `circuit.py`: Circuit definition with fluent API
  - `simulator/`: Simulation engine and results handling
  - `reports/`: Professional report generation system
    - `generator.py`: Main ReportGenerator orchestration
    - `builders/`: Format-specific builders (HTML, PDF)
    - `templates/`: Professional Jinja2 templates
    - `charts/`: Interactive Plotly chart generation
    - `utils/`: Formatting and metrics utilities

### Design Patterns
- Use dependency injection for flexibility
- Keep interfaces small and focused
- Prefer composition over inheritance
- Make illegal states unrepresentable
- Follow SOLID principles

### Performance Considerations
- Profile before optimizing: `python -m cProfile -s cumtime`
- Document algorithmic complexity in docstrings
- Use generators for large datasets
- Cache expensive computations with `functools.lru_cache`

## Development Workflow

### 🚨 STREAMLINED DEVELOPMENT WORKFLOW

**SIMPLIFIED PROCESS for ALL features and bug fixes (no slow agents):**

#### Phase 1: Document & Plan (Required)
1. **Create a Product Requirements Document (PRD)**
   - Document the feature or bug fix clearly
   - Ask clarifying questions before starting
   - Get explicit user approval before proceeding
   - **NO CODE WITHOUT PRD APPROVAL** ⚠️

2. **Break into Small Parts**
   - Divide work into small, manageable, testable chunks
   - Each part should take ~15 minutes to implement and test
   - Focus on one small piece at a time

#### Phase 2: Test-Driven Development (Required)
1. **For each small part:**
   - Write tests FIRST (covering happy path and edge cases)
   - Write minimal implementation to pass tests
   - Refactor if needed while keeping tests green
   - Use memory-bank to track patterns and decisions

#### Phase 3: User Validation (Required)
1. **User manually tests** the implementation in realistic scenarios
2. **Run quality checks:** tests, linting, type checking
3. **Git commit only when satisfied** with results

### Streamlined Development Approach

#### For New Features:
Just ask directly: **"I want to add [feature description]. Can you help me create a PRD and break this down into small TDD parts?"**

Examples:
- "I want to add circuit validation endpoint to FastAPI service"  
- "I want to implement AC frequency analysis for circuits"
- "I want to add progress bars to CLI simulation commands"

**Workflow:**
1. Create PRD → Document feature clearly with user questions
2. Break into parts → Small, testable chunks (~15 minutes each)  
3. TDD implementation → Tests first, then minimal code
4. User validation → Manual testing and quality checks

#### For Bug Fixes:
Just ask directly: **"I have this issue: [description]. Can you help me debug this systematically?"**

Examples:
- "FastAPI validation endpoint returns 500 for valid netlists"
- "Circuit simulation hangs on large netlists with >1000 components"  
- "Docker container fails to start on Apple Silicon Macs"

**Workflow:**
1. Create debugging PRD → Document issue with reproduction steps
2. Break into parts → Investigation, root cause, fix, test
3. TDD debugging → Test the fix, ensure no regressions
4. User validation → Verify the issue is resolved

### Quality Standards (Manual Focus)
- **>85% test coverage** - verify with pytest
- **Professional TDD** - tests before implementation always
- **Type hints and docstrings** on all public functions
- **Error handling** with specific exceptions and helpful messages
- **Memory-bank updates** to track patterns and decisions

### Common Commands

### Development Commands
```bash
# Run a specific test
pytest tests/test_module.py::test_function -v

# Check what's not covered by tests
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Find TODO items
grep -r "TODO\|FIXME\|XXX" src/

# Check for security issues
bandit -r src/
safety check
```

### **🐳 CRITICAL: Docker Container Required for Simulation**
**All circuit simulation must run in the Docker container** due to ngspice dependencies:

```bash
# Start the simulation container
docker-compose -f deployment/docker-compose.yml up -d circuit-sim

# Run interactive learning (with simulation backend)
docker-compose -f deployment/docker-compose.yml run --rm circuit-sim \
  uv run jupyter lab docs/learning_modules/

# Run tests with simulation
docker-compose -f deployment/docker-compose.yml run --rm circuit-sim \
  uv run python test_interactive_learning.py

# Run simulations from host (calls Docker)
uv run python examples/simulation_demo.py  # Auto-detects and uses Docker

# Manual container access for debugging
docker-compose -f deployment/docker-compose.yml run --rm circuit-sim bash
```

## Documentation Standards

### Code Documentation Example
```python
def simulate_circuit(
    circuit: Circuit,
    duration: float,
    timestep: float = 1e-6
) -> SimulationResult:
    """Simulate a circuit over time.
    
    Args:
        circuit: Circuit to simulate
        duration: Simulation duration in seconds
        timestep: Time increment for simulation (default: 1μs)
    
    Returns:
        SimulationResult containing voltages and currents
    
    Raises:
        ConvergenceError: If simulation fails to converge
        ValueError: If duration or timestep is invalid
    
    Example:
        >>> circuit = Circuit.from_netlist("amplifier.cir")
        >>> result = simulate_circuit(circuit, duration=0.001)
        >>> result.plot()
    """
```

### Report Generation Example
```python
from circuit_sim.reports import ReportGenerator

def generate_analysis_report(circuit: Circuit, results: SimulationResults) -> str:
    """Generate professional circuit analysis report.
    
    Args:
        circuit: Circuit definition with components
        results: Simulation results from analysis
    
    Returns:
        Path to generated HTML report
    
    Example:
        >>> circuit = Circuit("RC Filter")
        >>> results = engine.simulate_transient(circuit, "10ms")
        >>> report_path = generate_analysis_report(circuit, results)
        >>> # Report contains interactive charts, metrics, analysis
    """
    generator = ReportGenerator()
    return generator.generate_report(
        circuit=circuit,
        results=results,
        report_type="detailed",
        output_format="html"
    )
```

### API Documentation
- Every public function must have examples
- Document common use cases
- Explain error conditions
- Provide performance characteristics when relevant

## Production Checklist

### Before Release
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Examples working
- [ ] Performance benchmarks met
- [ ] Security scan clean (bandit, safety)
- [ ] Change log updated
- [ ] Version bumped appropriately

### Performance Targets
- Parse 10,000 component netlist: < 1 second
- Simulate 1000 components for 1ms: < 5 seconds
- Generate report with 10 plots: < 2 seconds
- API response time: < 100ms (p95)

### Error Handling
- Never crash on invalid input
- Provide helpful error messages
- Log errors with context
- Gracefully degrade when possible

## Memory Bank System (FAST CONSOLIDATION)

### 🚀 Performance Improvement
**NEW**: Fast consolidation script replaces slow 5+ minute memory-bank-agent initialization:
- **Performance**: 4400x faster (0.067 seconds vs 5+ minutes)
- **Method**: Mechanical file consolidation + quick LLM analysis
- **Usage**: All PRD-driven commands now use fast approach automatically

### Structure
```
memory-bank/
├── projectbrief.md       # Core requirements and goals
├── productContext.md     # Why project exists, problems solved
├── activeContext.md      # Current focus, recent changes
├── systemPatterns.md     # Architecture, design patterns
├── techContext.md        # Technologies, setup, constraints
├── progress.md          # What works, what's left, known issues
├── prds/                # Product Requirements Documents
│   └── *.md            # Feature-specific PRDs
└── scripts/             # Fast consolidation tools
    ├── consolidate_memory_bank.py    # Mechanical file combiner
    └── fast_memory_bank_agent.py     # Quick LLM analysis wrapper
```

### Fast Memory Bank Workflow
1. **Start of Session**: Run `python scripts/fast_memory_bank_agent.py [focus]` (<10 seconds)
2. **Context Analysis**: Quick LLM analysis of consolidated content
3. **During Work**: Update activeContext.md with decisions (unchanged)
4. **After Features**: Update systemPatterns.md and progress.md (unchanged)

### Fast Consolidation Usage
```bash
# Manual usage for testing/development
python scripts/consolidate_memory_bank.py > consolidated_context.md

# Agent wrapper with analysis (used by PRD commands automatically)
python scripts/fast_memory_bank_agent.py "integration planning"
python scripts/fast_memory_bank_agent.py "debugging context"
python scripts/fast_memory_bank_agent.py "feature development"
```

## Git Workflow

### Branch Strategy
- `main`: Production-ready releases only
- `develop`: Integration branch for features
- `feature/*`: Individual feature branches

### Commit Messages
```
<type>: <description>

[optional body]

[optional footer]
```
Types: feat, fix, docs, style, refactor, test, chore

### Before Creating PR
1. Rebase on latest develop
2. Ensure all tests pass
3. Update documentation
4. Add to CHANGELOG.md

## Project Structure
```
circuit-simulation/
├── src/                  # Source code
│   ├── __init__.py
│   ├── core/            # Simulation engine
│   ├── models/          # Data models
│   ├── api/             # FastAPI application
│   ├── reports/         # Report generation
│   └── utils/           # Utilities
├── tests/               # Test files (mirrors src/)
├── examples/            # Example circuits
├── docs/               # Documentation
├── docker/             # Docker configurations
├── memory-bank/        # Project memory
├── .github/            # GitHub workflows
├── requirements.txt    # Production dependencies
├── requirements-dev.txt # Development dependencies
├── pyproject.toml      # Project configuration
├── README.md          # User documentation
└── CLAUDE.md          # This file
```

## Current Priorities (MVP)

### Completed ✅
1. ✅ Core simulation engine with Ngspice (Docker containerized)
2. ✅ Python API for circuit definition (PySpice integration)
3. ✅ MCP Server with 8 tools for AI integration
4. ✅ Docker environment with ngspice 36
5. ✅ Interactive Plotly reports and visualization
6. ✅ **Professional CLI Interface** with progress bars and Rich formatting
7. ✅ **FastAPI Web Service** (Complete REST API with WebSocket support)
8. ✅ **Production Deployment** (Docker Compose with Redis/Celery)
9. ✅ **API Documentation** (OpenAPI/Swagger with interactive testing)
10. ✅ **KiCad Netlist Import** (Real .net file parsing with end-to-end simulation)
11. ✅ **SPICE Parser** (Complete .cir file support with .MODEL/.SUBCKT)
12. ✅ **Intelligent Model Mapping** (Automatic SPICE model assignment for 90% of KiCad components)

### Immediate Goals  
1. ✅ CLI interface with progress bars
2. 10 working example circuits
3. ✅ FastAPI web service  
4. ✅ Production deployment
5. ✅ KiCad netlist import capability
6. ✅ Intelligent model mapping for complex components  
7. AC frequency analysis implementation
8. Performance optimization and benchmarking

### Quality Gates
- ✅ Test coverage > 85% (76% achieved, improving)
- ✅ Type checking passing
- ✅ No security vulnerabilities
- ✅ Documentation complete
- ✅ Examples working

## MCP Integration 🤖

### MCP Server Implementation
The project includes a fully functional MCP (Model Context Protocol) server that provides AI assistants access to circuit simulation capabilities via 8 specialized tools:

**Core Circuit Tools:**
- `circuit.create`: Create new circuit instances
- `circuit.add_component`: Add components (R, L, C, voltage/current sources)
- `circuit.list`: List all circuits and their components
- `circuit.get`: Get detailed circuit information
- `circuit.validate`: Validate circuit connectivity

**Simulation Tools:**  
- `simulation.run_dc`: Run DC operating point analysis
- `simulation.run_transient`: Run transient (time-domain) analysis
- `analysis.get_results`: Get simulation results with plotting

### Usage with Claude Code
Connect the MCP server to Claude Code:
```bash
# Add MCP server to Claude Code
claude mcp add circuit-simulation -- uv run python run_mcp_server.py

# Verify connection
claude mcp list

# Test functionality  
uv run python test_mcp_server.py
```

### Usage with Claude Desktop (Optional)
Add to your Claude Desktop configuration:
```json
{
  "mcpServers": {
    "circuit-simulation": {
      "command": "uv",
      "args": ["run", "python", "run_mcp_server.py"],
      "cwd": "/path/to/circuit-simulation"
    }
  }
}
```

### Testing MCP Server
```bash
# Direct function testing
docker-compose run --rm circuit-sim python3 test_circuit_functions.py

# MCP protocol testing  
docker-compose run --rm circuit-sim python3 test_mcp_server.py

# Manual testing with mcp-client
npm install -g @anthropic/mcp-client
mcp-client stdio python3 run_mcp_server.py
```

## FastAPI Web Service 🌐

### Running the API Server
```bash
# Development server with auto-reload
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Production deployment
docker-compose -f docker-compose.fastapi.yml up -d --build

# Health check
curl http://localhost:8000/health

# Interactive documentation
open http://localhost:8000/docs
```

### API Endpoints
- **GET /health** - Service health check
- **GET /docs** - Interactive Swagger documentation  
- **POST /api/circuits** - Create new circuit
- **GET /api/circuits/{id}** - Get circuit details
- **POST /api/circuits/{id}/simulate** - Start simulation job
- **GET /api/simulations/{job_id}** - Get job status
- **GET /api/simulations/{job_id}/results** - Get simulation results
- **WS /ws/simulation/{job_id}** - WebSocket real-time updates

### Testing the API
```bash
# Python test client
uv run python test_api_client.py

# cURL examples
./test_api_examples.sh

# WebSocket demo
uv run python websocket_demo.py

# Full test suite
uv run pytest tests/test_api*.py tests/test_*_routes.py -v
```

### Development Workflow
1. Make changes to `src/api/` files
2. Server auto-reloads (if using --reload flag)
3. Test at http://localhost:8000/docs
4. Run tests: `uv run pytest tests/test_api*.py -v`
5. Check deployment: `uv run python test_docker_deployment.py`

## Common Tasks for AI

### Priority Tasks
1. **Circuit Implementation**: Follow patterns in `examples/`
2. **FastAPI Development**: REST API with WebSocket support (COMPLETE)
3. **API Testing**: Use interactive docs at `/docs` endpoint
4. **Report Generation**: Interactive Plotly visualizations
5. **Testing**: pytest with fixtures and parametrization
6. **Documentation**: API reference and deployment guides

### Task Approach
- Always search existing code for patterns first
- Ask for clarification if requirements are unclear
- Write tests before implementation
- Keep changes focused and reviewable
- Run quality checks before committing

## External Resources
- [PySpice Documentation](https://pyspice.fabrice-salvaire.fr/)
- [Ngspice Manual](http://ngspice.sourceforge.net/docs.html)
- [Plotly Python](https://plotly.com/python/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [pytest](https://docs.pytest.org/)

## Memory Bank Integration 🧠

### 🚨 CRITICAL: Automatic Memory Bank Usage with PRD-Driven Development
**MANDATORY: memory-bank-agent is ALWAYS invoked FIRST in EVERY development workflow.** This is integrated into all PRD-driven commands (`/develop-feature`, `/debug-issue`) for optimal context efficiency and token savings.

### PRD-Driven Memory Bank Workflow
```
Phase 0: memory-bank-agent → Provides focused context (<2000 tokens)
Phase 1: prd-creator → Creates technical PRD with user collaboration  
Phase 2: work-planner → Breaks PRD into testable segments
Phase 3: prompt-optimizer → Crafts optimal prompts for implementation
Phase 4: library-developer → Professional TDD with memory-bank updates
Phase 5: User validation → Manual testing before commit
```

### Memory Bank Agent Responsibilities

#### Context Provision (Phase 0):
- **Feature Development**: Architectural patterns, quality standards, current priorities
- **Bug Fixing**: Issue history, debugging patterns, similar past solutions
- **Library Focus**: Python API patterns, FastAPI standards, testing requirements
- **Token Efficiency**: <2000 tokens vs 10,000+ from raw files

#### Progress Recording (During Implementation):
- **Pattern Establishment**: New architectural decisions and their rationale
- **Implementation Lessons**: What worked, what didn't, and why
- **Quality Maintenance**: Standards upheld and improvements made
- **Integration Notes**: How features connect to existing codebase

### Context Efficiency Rules (Enforced by Commands)
- **NEVER** read memory-bank files directly (activeContext.md, systemPatterns.md, etc.)
- **ALWAYS** use memory-bank-agent through PRD-driven commands
- **AUTOMATIC**: Commands invoke memory-bank-agent without manual intervention
- **TOKEN SAVINGS**: Structured context handoffs between agent phases

### Integration with PRD-Driven Commands
All development uses memory-bank context automatically:

#### `/develop-feature [description]`:
- memory-bank-agent provides feature development context
- Records patterns established during implementation
- Updates project progress and architectural decisions

#### `/debug-issue [description]`:
- memory-bank-agent provides debugging context and issue history
- Records root causes and solution patterns
- Updates debugging knowledge base

#### Legacy Commands (Still Available):
- `/test` - Gets testing patterns and coverage requirements
- `/check` - Gets quality standards and validation patterns  
- `/ship` - Gets deployment and release patterns
- `/commit` - Gets commit message standards and quality checks

### Memory Bank Content Strategy (PRD-Focused)
The memory-bank maintains:
- **Approved PRDs**: Permanent record of feature requirements and decisions
- **Implementation Patterns**: Established during library-developer execution
- **Quality Standards**: Enforced across all development workflows
- **Integration Knowledge**: How components connect and communicate
- **Debugging Knowledge**: Root causes, solutions, and prevention patterns

### Cross-Session Communication
- **Development Log**: Automatic session tracking with git branch and directory
- **PRD Archive**: Permanent record of approved requirements and decisions
- **Pattern Evolution**: How architectural decisions evolve over time
- **Context Condensation**: Periodic compression to prevent accuracy drift

### Token Optimization Strategy
- **Phase-Based Context**: Each agent gets exactly the context it needs
- **Structured Handoffs**: Formatted data exchange between agent phases
- **Historical Filtering**: Old decisions surface only when specifically relevant
- **Focus Maintenance**: Library development patterns prioritized over usage patterns

## AI Assistant Guidelines

### DO
- Follow TDD (Test-Driven Development)
- Ask for clarification when needed
- Check existing patterns before implementing
- Run quality checks before committing
- Keep functions small and focused
- Document design decisions
- Handle errors explicitly

### DON'T
- Skip tests
- Ignore linting errors
- Use print() for debugging (use logging)
- Make assumptions about requirements
- Create large, monolithic functions
- Leave TODO comments without tickets
- Commit broken code

### Remember
- This is a professional library for production use
- Quality is more important than quantity
- User experience matters
- Performance requirements are real constraints
- Documentation is part of the feature

## Claude Code Configuration 🤖

### Simplified Fast Configuration
The project uses a streamlined Claude Code setup focused on speed and essential functionality:

**Essential Fast Agents (3 only)**:
- **codebase-locator**: Find WHERE code lives (files/directories)
- **codebase-analyzer**: Understand HOW code works (implementation details)
- **web-search-researcher**: Modern technical information and best practices

**Removed Slow Agents**:
- ~~memory-bank-agent~~ → Use memory-bank/ folder directly (4400x faster)
- ~~prd-creator~~ → Manual PRD creation (faster, more direct)
- ~~work-planner~~ → Manual task breakdown (faster, more direct)
- ~~prompt-optimizer~~ → Direct implementation (faster)
- ~~library-developer~~ → Direct TDD approach (faster)
- ~~circuit-analyzer~~ → Direct analysis (faster)
- ~~test-engineer~~ → Direct testing (faster)
- ~~report-builder~~ → Direct reporting (faster)

**Direct Communication Approach**:
- **New features**: "I want to add [description]" → Manual PRD → break into parts → TDD
- **Bug fixes**: "I have this issue: [description]" → Manual debugging PRD → investigate → fix

**Settings**: claude-sonnet-4-20250514 as default model with minimal hooks

### Streamlined Workflow Usage

#### Direct Communication (No fake commands):
```
# Feature Development - just ask directly:
"I want to add circuit validation endpoint to FastAPI service"
"I want to implement AC frequency analysis for circuits"

# Bug Fixing - describe the problem:
"FastAPI returns 500 for valid netlists"
"Simulation hangs on large circuits"
```

#### Quality Assurance (Direct approach):
```bash
# Manual quality checks (fast, no agents)
uv run pytest --cov=src --cov-report=term-missing
uv run black src/ tests/
uv run ruff check src/ tests/ --fix
uv run mypy src/ --strict
```

### Fast Manual Workflow

**Every Development Task Follows This Streamlined Pattern:**
```
Phase 1: Manual PRD creation → Document feature, ask questions, get approval
Phase 2: Manual task breakdown → Small testable chunks (~15 min each)
Phase 3: Direct TDD implementation → Tests first, then minimal code
Phase 4: User validation → Manual testing, quality checks, commit
```

**Direct Implementation Approach:**

**Fast Research Tools (use when needed):**
- **codebase-locator**: Find WHERE code lives quickly
- **codebase-analyzer**: Understand HOW existing code works
- **web-search-researcher**: Get current technical information

**Manual Development Process:**
- **Direct PRD creation**: Ask questions, document clearly, get approval
- **Direct task breakdown**: Small chunks, testable pieces
- **Direct TDD implementation**: Tests first, minimal code, refactor
- **Memory-bank tracking**: Update patterns manually in memory-bank/ folder

### Performance Benefits

**Speed Improvements:**
- **4400x faster startup** - No slow agent initialization
- **Direct approach** - No agent communication overhead  
- **Manual control** - Faster decision making and pivoting

**Development Efficiency:**
- **Simple PRD workflow** - Document, break down, implement
- **15-minute TDD segments** - Maintain focus and progress
- **Direct testing** - No agent overhead for quality checks

**Quality Maintenance:**
- **Manual quality gates** - Direct pytest, linting, type checking
- **Memory-bank tracking** - Update patterns as you go
- **Continuous testing** - TDD prevents regressions

---
*Last Updated: August 28, 2025*
*This file guides AI assistants in building a robust, production-ready circuit simulation library.*