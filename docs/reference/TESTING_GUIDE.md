# 🧪 Manual Testing Guide

This guide will help you test each major feature of the circuit simulation platform manually.

## Prerequisites

```bash
# Ensure Docker is not blocking ports
docker stop $(docker ps -aq) 2>/dev/null || true

# Install dependencies  
uv install

# Verify installation
uv run circuit-sim --help
```

## 🖥️ Test 1: CLI Interface

### Basic Commands
```bash
# Initialize project
uv run circuit-sim init --name "Test Project" --force

# Show system info
uv run circuit-sim info

# List available commands
uv run circuit-sim --help
```

### Circuit Creation from SPICE
```bash
# Create circuit from netlist (should work now)
uv run circuit-sim create --netlist examples/rc_filter.cir --name "RC Filter"

# List created circuits
uv run circuit-sim list

# Show circuit details
uv run circuit-sim show "RC Filter"  # Or use circuit ID
```

### Simulation via CLI
```bash
# Run DC simulation
uv run circuit-sim simulate "RC Filter" --type dc

# Run transient simulation  
uv run circuit-sim simulate "RC Filter" --type transient --stop-time 0.01
```

**Expected Results:**
- ✅ All commands run without errors
- ✅ Circuit shows 3 components (V1, R1, C1)
- ✅ DC simulation shows Node 2 voltage ~3.16V (RC filter loaded)
- ✅ Progress bars display properly

---

## 🌐 Test 2: FastAPI Web Service

### Start API Server
```bash
# Development mode
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Open browser to docs
open http://localhost:8000/docs
```

### Test Health Endpoints
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Readiness check  
curl http://localhost:8000/api/v1/health/ready

# Root endpoint
curl http://localhost:8000/
```

### Test Circuit API
```bash
# Create circuit
CIRCUIT_ID=$(curl -s -X POST http://localhost:8000/api/circuits \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test RC Filter", 
    "components": [
      {"type": "voltage_source", "name": "V1", "positive_node": "1", "negative_node": "0", "value": "5V"},
      {"type": "resistor", "name": "R1", "positive_node": "1", "negative_node": "2", "value": "1k"},
      {"type": "capacitor", "name": "C1", "positive_node": "2", "negative_node": "0", "value": "1u"}
    ]
  }' | jq -r '.id')

echo "Created circuit: $CIRCUIT_ID"

# Get circuit details
curl "http://localhost:8000/api/circuits/$CIRCUIT_ID"

# Start DC simulation
JOB_ID=$(curl -s -X POST "http://localhost:8000/api/circuits/$CIRCUIT_ID/simulate" \
  -H "Content-Type: application/json" \
  -d '{"type": "dc", "parameters": {}}' | jq -r '.job_id')

echo "Started job: $JOB_ID"

# Check job status  
curl "http://localhost:8000/api/simulations/$JOB_ID"

# Get results
curl "http://localhost:8000/api/simulations/$JOB_ID/results"
```

**Expected Results:**
- ✅ Health endpoints return JSON with status "healthy"
- ✅ Circuit creation returns ID
- ✅ Simulation job starts and completes  
- ✅ Results contain voltage data for nodes

---

## 🤖 Test 3: MCP Server

### Test MCP Functions
```bash
# Test MCP server directly
uv run python test_mcp_server.py
```

### Connect to Claude Code (Optional)
```bash
# Add MCP server to Claude Code
claude mcp add circuit-simulation -- uv run python run_mcp_server.py

# Test connection
claude mcp list
```

**Expected Results:**
- ✅ All MCP tests pass with green checkmarks
- ✅ Voltage divider shows 5.000V (correct voltage division)
- ✅ No errors in circuit creation or simulation

---

## 🐳 Test 4: Docker Deployment

### Build and Deploy
```bash
# Clean environment
docker system prune -f

# Build and start services
docker-compose -f docker-compose.fastapi.yml up -d --build

# Wait for services to start
sleep 30

# Check service health
docker-compose -f docker-compose.fastapi.yml ps
```

### Test Docker API
```bash
# Test through nginx proxy (port 80)
curl http://localhost/api/v1/health

# Test direct API (port 8000) 
curl http://localhost:8000/api/v1/health

# Create circuit via Docker
curl -X POST http://localhost:8000/api/circuits \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Docker Test",
    "components": [
      {"type": "voltage_source", "name": "V1", "positive_node": "1", "negative_node": "0", "value": "10V"},
      {"type": "resistor", "name": "R1", "positive_node": "1", "negative_node": "0", "value": "1k"}
    ]
  }'
```

### View Logs
```bash
# API logs
docker-compose -f docker-compose.fastapi.yml logs api

# Worker logs  
docker-compose -f docker-compose.fastapi.yml logs worker

# All logs
docker-compose -f docker-compose.fastapi.yml logs
```

**Expected Results:**
- ✅ All containers start successfully
- ✅ Health endpoint accessible on both ports
- ✅ No errors in service logs
- ✅ Circuit creation works through Docker

---

## 📊 Test 5: Report Generation

### Generate Reports via Python
```bash
# Run report demo
uv run python demo_full_report.py

# Check generated files
ls -la demo_*.html
open demo_detailed_report.html  # Should open interactive report
```

### Test Report API
```bash
# After creating a circuit and simulation (from Test 2):
curl "http://localhost:8000/api/simulations/$JOB_ID/report" > test_report.html
open test_report.html
```

**Expected Results:**
- ✅ HTML reports generate without errors
- ✅ Interactive Plotly charts display properly
- ✅ Reports contain circuit analysis and metrics

---

## 📥 Test 6: KiCad Import

### Test KiCad Netlist Import
```bash
# Test KiCad import demo
uv run python examples/demo_kicad_import.py

# Test with real KiCad file
uv run python test_quick_kicad.py
```

**Expected Results:**
- ✅ KiCad netlist parses successfully
- ✅ Components extracted correctly
- ✅ Simulation runs with imported circuit
- ✅ Results match expected values (1.650V for resistor divider)

---

## 📜 Test 7: SPICE Parser

### Test SPICE File Parsing
```bash
# Test SPICE parser
uv run python -c "
from src.io.parsers.spice_parser import SpiceParser
parser = SpiceParser()
circuit = parser.parse_file('examples/rc_filter.cir')
print(f'Parsed {len(circuit.components)} components')
for comp in circuit.components:
    print(f'  {comp.name}: {comp.value}')
"
```

**Expected Results:**
- ✅ SPICE file parses without errors
- ✅ Components show correct names and values
- ✅ Circuit object created successfully

---

## 🔧 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Kill processes on port 8000
   lsof -ti:8000 | xargs kill -9
   
   # Or use different port
   uv run uvicorn src.api.main:app --port 8001
   ```

2. **Docker Build Failures**
   ```bash
   # Clean Docker completely
   docker system prune -a -f
   docker-compose -f docker-compose.fastapi.yml build --no-cache
   ```

3. **Missing Dependencies**
   ```bash
   # Reinstall everything
   uv sync --frozen
   ```

4. **Test Failures**
   ```bash
   # Run specific test modules
   uv run pytest tests/test_circuit_routes.py -v
   uv run pytest tests/test_simulation_routes.py -v
   ```

### Success Criteria

Each test should demonstrate:
- ✅ **Functionality**: Feature works as expected
- ✅ **Performance**: Reasonable response times (< 5s)
- ✅ **Reliability**: No crashes or errors
- ✅ **Integration**: Components work together

### Next Steps

Once manual testing confirms everything works:
1. Fix remaining unit test failures (mostly timing/mocking issues)
2. Optimize performance for larger circuits
3. Add more comprehensive integration tests
4. Update documentation based on findings

---

**Need Help?** Check logs, verify ports, ensure Docker isn't blocking resources.