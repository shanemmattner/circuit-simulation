# Circuit Simulation Platform - AI Assistant Context

## Project Overview
**Name**: circuit-simulation  
**Description**: Modern Python-based circuit simulation platform with interactive reporting and AI-ready architecture  
**Phase**: MVP Development  
**Target Users**: Professional engineers and students  
**Success Metric**: Easy simulation of common circuits with awesome interactive and useful output reports  

## Technical Stack
- **Language**: Python 3.10+
- **Simulation Backends**: Ngspice (primary), Xyce (large circuits)
- **Visualization**: Plotly for interactive reports
- **Deployment**: Docker (Ubuntu base)
- **API**: FastAPI
- **Queue**: Redis/Celery
- **Testing**: pytest
- **Documentation**: Google style docstrings

## Memory Bank System

### CRITICAL: Memory persists between sessions via documentation

The AI assistant's memory resets between sessions. The Memory Bank ensures continuity by maintaining comprehensive project documentation. **ALWAYS read ALL memory bank files at the start of EVERY session.**

### Memory Bank Structure
```
memory-bank/
├── projectbrief.md       # Core requirements and goals
├── productContext.md     # Why project exists, problems solved
├── activeContext.md      # Current focus, recent changes, next steps
├── systemPatterns.md     # Architecture, design patterns, components
├── techContext.md        # Technologies, setup, constraints
└── progress.md          # What works, what's left, known issues
```

### Memory Bank Workflow
1. **Start of Session**: Read ALL memory bank files
2. **During Work**: Update activeContext.md with decisions/insights
3. **After Features**: Update systemPatterns.md and progress.md
4. **On "update memory bank"**: Review and update ALL files

## Development Workflow

### CRITICAL: Follow this workflow strictly

1. **Research Phase**
   - Thoroughly research the problem/feature
   - Understand existing solutions and best practices
   - Document findings

2. **Requirements Gathering**
   - Ask user clarifying questions
   - Understand success criteria
   - Identify edge cases

3. **PRD Creation**
   - Create detailed Product Requirements Document
   - Include acceptance criteria
   - Define scope clearly

4. **User Review**
   - Present PRD to user
   - Incorporate feedback
   - Get explicit approval before proceeding

5. **Task Breakdown**
   - Break PRD into ~15 minute tasks
   - Create todo list
   - Prioritize tasks

6. **Feature Branch Development**
   ```bash
   git checkout develop
   git pull
   git checkout -b feature/<feature-name>
   ```

7. **Test-Driven Development**
   - Write comprehensive unit tests FIRST
   - Cover edge cases
   - Aim for >80% coverage

8. **Implementation**
   - Develop working code
   - Follow existing patterns
   - Keep changes focused

9. **Quality Checks**
   ```bash
   # Always run before committing:
   black .  # formatter
   ruff check .  # linter
   pytest  # tests
   ```

10. **Manual Testing**
    - Have user test manually
    - Document test results
    - Gather feedback

11. **Merge Process**
    - Fix any issues from feedback
    - Merge to feature branch
    - Eventually merge feature → develop → main

## Git Workflow
- **main**: Production-ready releases only
- **develop**: Integration branch for features
- **feature/\***: Individual feature branches

### Commit Messages
```
<type>: <description>

[optional body]

[optional footer]
```

Types: feat, fix, docs, style, refactor, test, chore

## Project Structure
```
circuit-simulation/
├── docs/                 # Documentation
│   ├── PRD.md
│   ├── RESEARCH_NOTES.md
│   ├── SIMULATOR_COMPARISON.md
│   └── EDUCATION_CONTENT.md
├── src/                  # Source code
│   ├── api/             # FastAPI application
│   ├── core/            # Core simulation logic
│   ├── models/          # Data models
│   ├── reports/         # Report generation
│   └── utils/           # Utilities
├── tests/               # Test files
├── examples/            # Example circuits
├── submodules/          # Git submodules
│   ├── circuit-synth/
│   ├── KiCad-Spice-Library/
│   └── wingel-simulation/
├── docker/              # Docker configurations
├── requirements.txt     # Python dependencies
└── CLAUDE.md           # This file
```

## Current Priorities (MVP Phase)

### Immediate Goals
1. Docker container with PySpice + Ngspice
2. Basic Python API for circuit definition
3. Simple CLI interface
4. 10 working example circuits
5. Basic Plotly report generation

### Next Phase
1. REST API with FastAPI
2. Job queue system
3. Model library integration
4. Professional report templates
5. Educational content

## Key Design Decisions
- **Dual Backend**: Ngspice for <10k components, Xyce for larger
- **API First**: All features accessible via API
- **Docker Primary**: Ensures consistency and portability
- **MCP Ready**: Architecture supports future MCP integration
- **Open Core Model**: Basic features free, premium additions later

## Common Tasks for AI Assistance
1. Implement new circuit analysis types
2. Create example circuits
3. Develop report visualizations
4. Write unit tests
5. Optimize simulation performance
6. Create educational content
7. Document APIs
8. Debug convergence issues

## Code Style Guidelines
- Use type hints for function signatures
- Google style docstrings
- Descriptive variable names
- Keep functions small and focused
- DRY (Don't Repeat Yourself)
- SOLID principles where applicable

## Testing Requirements
- Write tests BEFORE implementation
- Use pytest fixtures for common setups
- Mock external dependencies
- Test edge cases and error conditions
- Aim for >80% code coverage

## Important Commands
```bash
# Development setup
pip install -r requirements-dev.txt

# Quality checks (run before EVERY commit)
black .                    # Format code
ruff check .              # Lint code  
pytest                    # Run tests
pytest --cov=src          # Check coverage

# Docker operations
docker build -t circuit-simulation .
docker run -p 8000:8000 circuit-simulation

# Git workflow
git checkout develop
git pull
git checkout -b feature/new-feature
# ... make changes ...
git add .
git commit -m "feat: add new feature"
git push -u origin feature/new-feature
```

## External Resources
- [PySpice Documentation](https://pyspice.fabrice-salvaire.fr/)
- [Ngspice Manual](http://ngspice.sourceforge.net/docs.html)
- [Plotly Python](https://plotly.com/python/)
- [MCP Specification](https://modelcontextprotocol.io/)

## Notes for AI Assistants

### DO:
- Always follow the development workflow
- Ask for clarification when requirements are ambiguous
- Write tests before code
- Run quality checks before committing
- Break complex tasks into small chunks
- Document your design decisions
- Consider both professional and educational use cases

### DON'T:
- Skip the research phase
- Implement without tests
- Merge directly to main
- Make large, unfocused changes
- Ignore user feedback
- Assume requirements - always confirm

### Remember:
- This is both a professional tool and educational platform
- Reports should be beautiful AND functional
- Performance matters but correctness is critical
- We're building for MCP integration from day one
- User experience is paramount - make it easy!

## Contact & Support
- Primary Use: Circuit simulation for professionals and students
- Timeline: ASAP delivery for MVP
- Business Model: TBD (considering open core)

## Last Updated
August 26, 2025

---
*This file helps AI assistants understand the project context and work effectively. Update it as the project evolves.*