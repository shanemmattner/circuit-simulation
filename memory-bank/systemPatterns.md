# System Patterns

## Development Workflow Architecture (NEW - August 28, 2025)
```
┌─────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│   User Request  │────▶│  memory-bank-   │────▶│   PRD Creator    │
│                 │     │     agent       │     │                  │
└─────────────────┘     └─────────────────┘     └──────────────────┘
         │                       │                        │
         │                       ▼                        ▼
         │              ┌─────────────────┐     ┌──────────────────┐
         │              │  Context (<2k   │     │  User Review &   │
         │              │    tokens)      │     │    Approval      │
         │              └─────────────────┘     └──────────────────┘
         │                                             │
         ▼                                             ▼
┌─────────────────┐                         ┌──────────────────┐
│  Work Planner   │◀────────────────────────│  TDD Implementer │
│  (15-min chunks)│                         │   (with tests)   │
└─────────────────┘                         └──────────────────┘
         │                                             │
         ▼                                             ▼
┌─────────────────┐                         ┌──────────────────┐
│ Prompt Optimizer│                         │  Memory Bank     │
│                 │                         │    Updates       │
└─────────────────┘                         └──────────────────┘
```

## Circuit Simulation Architecture (Existing)
```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   REST API  │────▶│  Job Queue   │────▶│  Simulation  │
│  (FastAPI)  │     │(Redis/Celery)│     │   Worker     │
└─────────────┘     └──────────────┘     └──────────────┘
       │                                         │
       ▼                                         ▼
┌─────────────┐                         ┌──────────────┐
│   Report    │◀────────────────────────│   PySpice    │
│  Generator  │                         │   Wrapper    │
└─────────────┘                         └──────────────┘
       │                                         │
       ▼                                    ┌────┴────┐
┌─────────────┐                      ┌──────▼─┐  ┌───▼───┐
│   Plotly    │                      │ Ngspice│  │ Xyce  │
│   Reports   │                      └────────┘  └───────┘
└─────────────┘
```

## Key Design Patterns

### 1. PRD-Driven Development Pattern (NEW - August 28, 2025)
```python
# Universal workflow for any feature development
class PRDDrivenWorkflow:
    def execute_feature(self, user_request: str):
        # Phase 1: Context Acquisition
        context = memory_bank_agent.get_context(focus=user_request)
        
        # Phase 2: Requirements Definition  
        prd = prd_creator.create_interactive_prd(user_request, context)
        user_approval = await get_user_approval(prd)
        
        # Phase 3: Work Planning
        work_plan = work_planner.create_plan(prd, chunks="15-30min")
        
        # Phase 4: Implementation
        for chunk in work_plan.chunks:
            optimized_prompt = prompt_optimizer.optimize(chunk)
            result = tdd_implementer.implement(chunk, optimized_prompt)
            memory_bank_agent.record_progress(chunk, result)
        
        # Phase 5: Integration & Recording
        memory_bank_agent.update_patterns(work_plan.learned_patterns)
        return result
```

### 2. Context Optimization Pattern (Token Efficiency)
```python
# Efficient agent communication pattern
class ContextOptimization:
    def __init__(self):
        self.token_limit = 2000  # vs 10,000+ raw files
    
    def get_focused_context(self, task_type: str) -> str:
        """Return only relevant context for specific task type."""
        context_map = {
            "api": ["systemPatterns.api", "activeContext.current_api_work"],
            "testing": ["systemPatterns.test_patterns", "progress.test_status"],
            "architecture": ["systemPatterns.core", "projectbrief.principles"]
        }
        return self._condense_context(context_map[task_type])
```

### 3. Universal Agent Architecture Pattern
```python
# Agents work with any tech stack
class UniversalAgent(ABC):
    def __init__(self, project_root: Path, project_type: str):
        self.project_root = project_root
        self.project_type = project_type
        self.config = self._load_project_config()
    
    @abstractmethod
    def execute(self, task: str) -> Result:
        pass
    
    def _load_project_config(self) -> dict:
        """Auto-detect project configuration (Python, JS, Go, etc.)"""
        return detect_project_config(self.project_root)
```

### 4. Strategy Pattern (Simulator Backends)
```python
class SimulatorStrategy(ABC):
    @abstractmethod
    def simulate(self, circuit, analysis): pass

class NgspiceSimulator(SimulatorStrategy):
    def simulate(self, circuit, analysis):
        # Ngspice-specific implementation
        
class XyceSimulator(SimulatorStrategy):
    def simulate(self, circuit, analysis):
        # Xyce-specific implementation

class SimulationEngine:
    def __init__(self, strategy: SimulatorStrategy):
        self.strategy = strategy
```

### 2. Builder Pattern (Circuit Construction)
```python
class CircuitBuilder:
    def add_resistor(self, name, n1, n2, value)
    def add_capacitor(self, name, n1, n2, value)
    def add_voltage_source(self, name, n_pos, n_neg, value)
    def build(self) -> Circuit
```

### 3. Factory Pattern (Report Generation)
```python
class ReportFactory:
    @staticmethod
    def create_report(report_type, data):
        if report_type == "transient":
            return TransientReport(data)
        elif report_type == "ac":
            return FrequencyReport(data)
```

## Component Relationships

### Core Components
1. **Circuit Definition Layer**
   - Python API for circuit construction
   - Model library integration
   - Schematic import (future)

2. **Simulation Layer**
   - PySpice wrapper
   - Backend selection logic
   - Convergence handling

3. **Analysis Layer**
   - Result processing
   - Statistical analysis
   - Performance metrics

4. **Visualization Layer**
   - Plotly chart generation
   - Interactive features
   - Export functionality

### Data Flow
1. User defines circuit (API/File)
2. Circuit validated and prepared
3. Backend selected based on complexity
4. Simulation executed
5. Results processed and cached
6. Report generated
7. Interactive visualization served

## Critical Implementation Paths

### Simulation Execution Path
```
User Request → Validation → Queue → Worker → Backend → Results → Cache
```

### Report Generation Path
```
Raw Data → Processing → Plotly Figures → HTML Template → Final Report
```

## Technology Integration Points

### PySpice Integration
- Circuit netlist generation
- Simulator control
- Result extraction
- Error handling

### Plotly Integration
- Time-series plots
- Frequency response (Bode)
- Interactive controls
- Export capabilities

### Docker Integration
- Base image: Ubuntu 22.04
- Multi-stage build
- Volume mounts for models
- Environment configuration

## Error Handling Patterns
1. **Convergence Issues**: Retry with relaxed tolerances
2. **Model Not Found**: Fallback to generic models
3. **Timeout**: Kill simulation, return partial results
4. **Invalid Circuit**: Detailed validation messages

## Performance Patterns
- Cache simulation results (Redis)
- Lazy load model libraries
- Stream large results
- Parallel simulation for parameter sweeps

## Security Patterns
- Sandboxed simulation execution
- Input validation and sanitization
- Rate limiting per user
- Resource limits (CPU, memory, time)