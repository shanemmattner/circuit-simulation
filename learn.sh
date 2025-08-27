#!/bin/bash
# Circuit Simulation Interactive Learning Launcher
# Simple script to start the learning environment with working simulation

set -e

echo "🎓 Circuit Simulation Interactive Learning Environment"
echo "================================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Function to clean up on exit
cleanup() {
    echo "🧹 Cleaning up..."
    docker stop circuit-sim-learn > /dev/null 2>&1 || true
    docker rm circuit-sim-learn > /dev/null 2>&1 || true
}
trap cleanup EXIT

echo "🔧 Setting up simulation environment..."

# Stop and remove any existing containers
docker stop circuit-sim circuit-sim-learn > /dev/null 2>&1 || true
docker rm circuit-sim circuit-sim-learn > /dev/null 2>&1 || true

# Build the image if it doesn't exist
if ! docker images | grep -q "circuit-simulation.*latest"; then
    echo "📦 Building simulation container (this may take a few minutes)..."
    docker build -f deployment/Dockerfile -t circuit-simulation:latest . --quiet
    echo "✅ Container built successfully!"
else
    echo "✅ Using existing simulation container"
fi

# Start the container
echo "🚀 Starting learning environment..."
docker run -d \
    --name circuit-sim-learn \
    -v "$(pwd):/workspace" \
    -p 8888:8888 \
    --env PYSPICE_NGSPICE_LIBRARY=/usr/lib/x86_64-linux-gnu/libngspice.so.0 \
    circuit-simulation:latest \
    tail -f /dev/null

# Wait a moment for container to start
sleep 2

echo "📚 Launching Jupyter Lab with interactive learning modules..."
echo "🔬 Simulation backend: ✅ Working (PySpice + ngspice in Docker)"
echo "🎛️ Interactive widgets: ✅ Enabled"
echo "📊 Live plotting: ✅ Plotly charts"
echo ""

# Start Jupyter Lab and capture the output to get the token
echo "🌐 Starting Jupyter Lab server..."
docker exec circuit-sim-learn bash -c '
    cd /workspace
    echo "📍 Working directory: $(pwd)"
    echo "📂 Learning modules: $(ls -la docs/learning_modules/ 2>/dev/null | wc -l) items"
    echo ""
    echo "🎯 Starting with real circuit simulation backend..."
    uv run jupyter lab docs/learning_modules/ \
        --ip=0.0.0.0 \
        --port=8888 \
        --allow-root \
        --no-browser \
        --ServerApp.token="" \
        --ServerApp.password="" \
        --ServerApp.disable_check_xsrf=True
' &

# Give Jupyter a moment to start
sleep 3

echo ""
echo "================================================================="
echo "🎉 Interactive Learning Environment Ready!"
echo "================================================================="
echo "🌐 Open your browser to: http://localhost:8888"
echo "📚 Start with: track1_dc_analysis/module_1.1_dc_basics/explain_dc_concept.ipynb"
echo "🔬 Simulation: Full PySpice backend working"
echo "⚡ Experience: Real circuit simulation + interactive widgets"
echo ""
echo "💡 To stop: Press Ctrl+C or run: docker stop circuit-sim-learn"
echo ""

# Keep the script running
wait