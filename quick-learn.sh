#!/bin/bash
# Quick launcher for interactive learning (assumes container is already built)

echo "🎓 Quick Launch: Interactive Circuit Learning"
echo "=============================================="

# Use existing container or create new one
if docker ps -a | grep -q "circuit-sim"; then
    echo "🔄 Using existing container..."
    docker start circuit-sim > /dev/null 2>&1 || true
else
    echo "🚀 Creating new container..."
    docker run -d \
        --name circuit-sim \
        -v "$(pwd):/workspace" \
        -p 8888:8888 \
        circuit-simulation:latest \
        tail -f /dev/null
fi

echo "📚 Launching Jupyter Lab..."
echo "🌐 Will open at: http://localhost:8888"
echo ""

# Launch Jupyter with no authentication for easy access
docker exec circuit-sim bash -c '
    cd /workspace
    uv run jupyter lab docs/learning_modules/ \
        --ip=0.0.0.0 \
        --port=8888 \
        --allow-root \
        --no-browser \
        --ServerApp.token="" \
        --ServerApp.password="" \
        --ServerApp.disable_check_xsrf=True
'