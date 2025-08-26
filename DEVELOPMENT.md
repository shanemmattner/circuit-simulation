# Development Setup

This project supports both `uv` (recommended for speed) and traditional Python environments.

## Option 1: Using UV (Recommended)

[UV](https://github.com/astral-sh/uv) is a fast Python package manager written in Rust.

### Install UV
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setup with UV
```bash
# Clone the repository
git clone https://github.com/circuit-synth/circuit-simulation.git
cd circuit-simulation

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
uv pip install -r requirements-dev.txt
```

### Daily Development with UV
```bash
# Activate environment
source .venv/bin/activate

# Install new dependencies
uv pip install package-name

# Update dependencies
uv pip install --upgrade package-name

# Run tests
pytest

# Format and lint
black .
ruff check .
```

## Option 2: Using Traditional Python/pip

### Setup with venv and pip
```bash
# Clone the repository
git clone https://github.com/circuit-synth/circuit-simulation.git
cd circuit-simulation

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -e .
pip install -r requirements-dev.txt
```

### Setup with conda
```bash
# Create conda environment
conda create -n circuit-sim python=3.11
conda activate circuit-sim

# Install dependencies
pip install -e .
pip install -r requirements-dev.txt
```

## Running Tests

Regardless of your environment choice:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_circuit.py

# Run with verbose output
pytest -v
```

## Code Quality

Before committing, always run:

```bash
# Format code
black .

# Check linting
ruff check .

# Type checking (optional)
mypy src/
```

## Installing Ngspice

The simulator backend needs to be installed separately:

### Ubuntu/Debian
```bash
sudo apt-get install ngspice
```

### macOS
```bash
brew install ngspice
```

### Windows
Download from [Ngspice official site](http://ngspice.sourceforge.net/download.html)

## Troubleshooting

### PySpice Can't Find Ngspice
Set the SPICE_LIBRARY_PATH environment variable:
```bash
export SPICE_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/ngspice  # Linux
export SPICE_LIBRARY_PATH=/opt/homebrew/lib/ngspice  # macOS ARM
```

### Permission Issues with UV
If you get permission errors, try:
```bash
uv venv --python python3.11
```

## IDE Setup

### VS Code
1. Install Python extension
2. Select interpreter: `.venv/bin/python`
3. Enable formatting on save with Black

### PyCharm
1. Set project interpreter to `.venv/bin/python`
2. Configure Black as external tool
3. Enable pytest as test runner