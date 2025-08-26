# Circuit Simulation Project Commands

## Quick Commands

### check
Run all quality checks before committing
```bash
black src/ tests/ examples/
ruff check src/ tests/ examples/
mypy src/ --strict
pytest -v
```

### test
Run tests with coverage report
```bash
pytest --cov=src --cov-report=term-missing --cov-report=html
```

### ship
Prepare code for PR (format, lint, test, and show status)
```bash
black src/ tests/ examples/
ruff check src/ tests/ examples/
mypy src/ --strict
pytest -v
git status
```

### benchmark
Run performance benchmarks on circuit simulations
```bash
python -m cProfile -s cumtime src/core/simulator.py
python -m memory_profiler src/core/simulator.py
```

### circuit-test
Test a specific circuit example
```bash
python examples/$1.py --verbose --plot
```

### doc-build
Build and verify documentation
```bash
sphinx-build -b html docs/ docs/_build/
python -m http.server 8000 --directory docs/_build/
```

### security-check
Run security scans on the codebase
```bash
bandit -r src/
safety check
pip-audit
```

### clean
Clean up temporary files and caches
```bash
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
rm -rf .pytest_cache .ruff_cache .mypy_cache
rm -rf htmlcov/ .coverage
```

### setup-dev
Set up development environment
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
```

### profile-circuit
Profile a circuit simulation for performance
```bash
python -m cProfile -o profile.stats examples/$1.py
python -m pstats profile.stats
```