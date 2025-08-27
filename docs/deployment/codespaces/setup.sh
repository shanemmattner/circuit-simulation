#!/bin/bash
# GitHub Codespaces setup script for Circuit Simulation Learning Environment

set -e  # Exit on any error

echo "🚀 Setting up Circuit Simulation Learning Environment in Codespaces..."
echo "======================================================================"

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update -qq

# Install system dependencies for circuit simulation
echo "🔧 Installing system dependencies..."
sudo apt-get install -qq -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    python3-dev \
    graphviz \
    graphviz-dev

# Upgrade pip
echo "⬆️ Upgrading pip..."
python -m pip install --upgrade pip

# Install circuit simulation learning dependencies
echo "📚 Installing Python dependencies..."
pip install -q \
    PySpice>=1.5 \
    numpy>=1.24.0 \
    matplotlib>=3.6.0 \
    plotly>=6.3.0 \
    pandas>=2.3.2 \
    ipywidgets>=8.1.1 \
    jupyter>=1.0.0 \
    jupyterlab>=4.0.0 \
    voila>=0.5.0 \
    jupyter-dash>=0.4.2 \
    ipython>=8.12.0 \
    nbformat>=5.9.0 \
    nbconvert>=7.0.0 \
    pyyaml>=6.0.2 \
    jinja2>=3.1.6 \
    rich>=13.0.0

# Install circuit-sim package in development mode
echo "🔌 Installing circuit-sim package..."
pip install -e . --no-deps

# Set up JupyterLab extensions
echo "🎛️ Setting up JupyterLab extensions..."
jupyter labextension install @jupyter-widgets/jupyterlab-manager --no-build 2>/dev/null || true
jupyter labextension install jupyterlab-plotly --no-build 2>/dev/null || true
jupyter lab build --dev-build=False --minimize=True 2>/dev/null || true

# Enable notebook widgets
echo "✨ Enabling interactive widgets..."
jupyter nbextension enable --py widgetsnbextension --sys-prefix 2>/dev/null || true

# Create convenient symlinks
echo "🔗 Creating convenient navigation..."
ln -sf /workspaces/circuit-simulation/docs/learning_modules /workspaces/learning_modules || true
ln -sf /workspaces/circuit-simulation /workspaces/circuit-sim || true

# Set up Git configuration helpers
echo "⚙️ Configuring development environment..."
git config --global --add safe.directory /workspaces/circuit-simulation 2>/dev/null || true

# Create a startup script for Jupyter
echo "📓 Creating Jupyter startup script..."
cat > /workspaces/start-jupyter.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting JupyterLab for Interactive Circuit Learning..."
echo "📚 Navigate to learning_modules/ to begin!"
echo "🌐 JupyterLab will be available at the forwarded port"
cd /workspaces/circuit-simulation
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root
EOF
chmod +x /workspaces/start-jupyter.sh

# Create a startup script for Voila dashboard
cat > /workspaces/start-dashboard.sh << 'EOF'
#!/bin/bash
echo "🎛️ Starting Voila Dashboard..."
echo "📊 Interactive learning dashboard will be available at the forwarded port"
cd /workspaces/circuit-simulation/docs/learning_modules
voila --ip=0.0.0.0 --port=8080 --no-browser
EOF
chmod +x /workspaces/start-dashboard.sh

# Test the installation
echo "🧪 Testing installation..."
python -c "
import sys
try:
    from circuit_sim import Circuit
    import ipywidgets as widgets
    import plotly.graph_objects as go
    import jupyter
    print('✅ All core packages imported successfully')
except ImportError as e:
    print(f'❌ Import test failed: {e}')
    sys.exit(1)
"

# Create welcome message
echo "📝 Creating welcome message..."
cat > /workspaces/WELCOME.md << 'EOF'
# 🎓 Circuit Simulation Interactive Learning Environment

Welcome to your Codespaces development environment!

## 🚀 Quick Start

### Option 1: JupyterLab (Recommended)
```bash
./start-jupyter.sh
```
Then click on the forwarded port 8888 to access JupyterLab.

### Option 2: Voila Dashboard
```bash
./start-dashboard.sh
```
Then click on the forwarded port 8080 for the interactive dashboard.

### Option 3: VS Code Jupyter Extension
Open any `.ipynb` file in the `learning_modules/` directory directly in VS Code.

## 📚 Learning Path

1. **Start here**: `learning_modules/track1_dc_analysis/module_1.1_dc_basics/`
2. **Follow the sequence**: Explain → Try → Build → Challenge → Reflect
3. **Interactive features**: All widgets and simulations work!

## 🛠️ Development Tools Available

- **Python 3.10** with full circuit simulation stack
- **JupyterLab** for interactive notebooks  
- **VS Code** with Python extensions
- **Interactive widgets** (ipywidgets) enabled
- **Plotly** for interactive visualizations
- **Circuit-sim library** installed in development mode

## 🔧 Useful Commands

```bash
# Run tests
python test_interactive_learning.py

# Start learning environment
./start-jupyter.sh

# Check package installation
pip list | grep circuit

# Run a specific notebook
jupyter nbconvert --execute path/to/notebook.ipynb
```

Happy Learning! 🎉
EOF

echo ""
echo "======================================================================"
echo "✅ Setup Complete!"
echo "======================================================================"
echo "🎓 Interactive Circuit Learning Environment is ready!"
echo "📚 Learning modules available at: /workspaces/learning_modules/"
echo "🚀 Start JupyterLab with: ./start-jupyter.sh"
echo "🎛️ Start dashboard with: ./start-dashboard.sh"  
echo "📖 Read WELCOME.md for detailed instructions"
echo ""
echo "🎯 Ready to learn circuit simulation!"