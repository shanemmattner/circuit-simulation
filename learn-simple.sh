#!/bin/bash
# Simplified Circuit Learning Launcher (works with current container)

set -e

echo "🎓 Circuit Simulation Interactive Learning"
echo "=========================================="

# Check if container exists
if ! docker ps -a | grep -q "circuit-sim"; then
    echo "❌ No circuit-sim container found. Run './learn.sh' for full setup."
    exit 1
fi

# Check if container has port mapping
echo "🔄 Checking container setup..."
if ! docker port circuit-sim 8888 > /dev/null 2>&1; then
    echo "🔄 Recreating container with proper port mapping..."
    docker stop circuit-sim > /dev/null 2>&1 || true
    docker rm circuit-sim > /dev/null 2>&1 || true
    
    # Create new container with port mapping
    docker run -d \
        --name circuit-sim \
        -v "$(pwd):/workspace" \
        -p 8888:8888 \
        circuit-simulation:latest \
        tail -f /dev/null
else
    echo "🔄 Starting existing container..."
    docker start circuit-sim > /dev/null 2>&1 || true
fi

# Wait a moment
sleep 2

echo "🚀 Launching Jupyter Lab with working simulation..."
echo "📍 URL will be: http://localhost:8888"
echo "📚 Start with: track1_dc_analysis/module_1.1_dc_basics/explain_dc_concept.ipynb"
echo ""

# Use direct python instead of uv
docker exec -it circuit-sim bash -c '
    cd /workspace
    export PYTHONPATH=/workspace
    echo "🔬 Testing simulation backend..."
    python -c "from circuit_sim import Circuit; c=Circuit(\"test\"); c.add_voltage_source(\"V1\",1,0,\"5V\"); print(\"✅ Simulation ready\")"
    echo "📚 Starting Jupyter Lab..."
    python -m jupyter lab docs/learning_modules/ \
        --ip=0.0.0.0 \
        --port=8888 \
        --allow-root \
        --no-browser \
        --ServerApp.token="" \
        --ServerApp.password="" \
        --ServerApp.disable_check_xsrf=True
'