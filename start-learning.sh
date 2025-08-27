#!/bin/bash
# Ultimate Simple Circuit Learning Launcher

echo "🎓 Starting Circuit Learning with Working Simulation"
echo "===================================================="

# Clean up any existing containers
docker rm -f circuit-sim-learning > /dev/null 2>&1 || true

# Start fresh container with everything mapped properly
echo "🚀 Starting simulation container..."
docker run -d \
    --name circuit-sim-learning \
    -v "$(pwd):/workspace" \
    -p 8888:8888 \
    --env PYTHONPATH=/workspace \
    circuit-simulation:latest \
    tail -f /dev/null

echo "⏳ Waiting for container to be ready..."
sleep 3

echo "📚 Launching Jupyter Lab..."
# Launch Jupyter and show the URL
docker exec circuit-sim-learning bash -c "
    cd /workspace
    echo '🔬 Testing simulation:'
    python -c 'from circuit_sim import Circuit; print(\"✅ Simulation backend ready\")'
    echo ''
    echo '🌐 Starting Jupyter Lab at http://localhost:8888'
    echo '📂 Learning modules directory: docs/learning_modules/'
    echo '🎯 Start with: track1_dc_analysis/module_1.1_dc_basics/explain_dc_concept.ipynb'
    echo ''
    python -m jupyter lab docs/learning_modules/ \
        --ip=0.0.0.0 \
        --port=8888 \
        --allow-root \
        --no-browser \
        --ServerApp.token='' \
        --ServerApp.password='' \
        --ServerApp.disable_check_xsrf=True
" &

echo ""
echo "================================================================="
echo "🎉 Interactive Learning Environment Started!"
echo "================================================================="
echo "🌐 Open your browser to: http://localhost:8888"
echo "📚 Navigate to: track1_dc_analysis/module_1.1_dc_basics/"
echo "🎯 Start with: explain_dc_concept.ipynb"
echo "🔬 Backend: Working simulation (PySpice + ngspice)"
echo ""
echo "💡 To stop: docker rm -f circuit-sim-learning"
echo ""

# Open browser automatically (macOS)
sleep 5
if command -v open > /dev/null; then
    echo "🌐 Opening browser..."
    open http://localhost:8888
fi