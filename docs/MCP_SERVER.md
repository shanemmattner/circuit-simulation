# MCP Server Documentation

## Overview

The Circuit Simulation MCP (Model Context Protocol) server exposes circuit simulation capabilities to AI assistants and other MCP clients. This allows AI agents to design, simulate, and analyze electronic circuits programmatically.

## Features

### Tools Available
1. **Circuit Management**
   - `circuit.create` - Create new circuits
   - `circuit.add_component` - Add components to circuits
   - `circuit.list` - List all active circuits
   - `circuit.get` - Get circuit details
   - `circuit.validate` - Validate circuit connectivity

2. **Simulation**
   - `simulation.run_dc` - DC operating point analysis
   - `simulation.run_transient` - Time-domain analysis
   - `simulation.run_ac` - Frequency analysis (planned)

3. **Analysis**
   - `analysis.get_results` - Retrieve detailed results
   - `analysis.plot` - Generate visualization plots
   - `analysis.export` - Export circuits in various formats

### Resources Available
- Example circuits (voltage divider, RC filter)
- Component reference documentation
- Simulation guides

### Prompts Available
- Circuit design assistant
- Circuit debugging helper
- Electronics learning guide

## Quick Start

### 1. Start the Server

```bash
# Local installation
python3 run_mcp_server.py

# With Docker
docker-compose run circuit-sim python3 run_mcp_server.py
```

### 2. Connect with MCP Client

```python
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters

server_params = StdioServerParameters(
    command="python3",
    args=["run_mcp_server.py"],
    cwd="."
)

async with stdio_client(server_params) as (read_stream, write_stream):
    async with ClientSession(read_stream, write_stream) as session:
        await session.initialize()
        
        # Use the tools
        result = await session.call_tool("circuit.create", {
            "name": "Test Circuit",
            "description": "My first circuit"
        })
```

## Tool Reference

### Circuit Management

#### circuit.create
Create a new circuit.

**Input:**
```json
{
  "name": "Circuit Name",
  "description": "Optional description"
}
```

**Output:**
```json
{
  "status": "success",
  "circuit_id": "abc12345",
  "name": "Circuit Name",
  "created_at": "2024-08-26T15:30:00"
}
```

#### circuit.add_component
Add a component to an existing circuit.

**Input:**
```json
{
  "circuit_id": "abc12345",
  "type": "resistor",
  "name": "R1",
  "value": "1k",
  "positive": 1,
  "negative": 2
}
```

**Supported Types:**
- `resistor` - Resistors (1k, 10k, 1M)
- `capacitor` - Capacitors (10uF, 100nF, 1pF)
- `inductor` - Inductors (100mH, 10uH, 1H)
- `voltage_source` - Voltage sources (5V, 3.3V)
- `current_source` - Current sources (10mA, 1A)

#### circuit.validate
Check circuit for common issues.

**Input:**
```json
{
  "circuit_id": "abc12345"
}
```

**Output:**
```json
{
  "status": "success",
  "valid": true,
  "issues": [],
  "warnings": ["Node 3 has only one connection"],
  "summary": {
    "components": 3,
    "nodes": 4,
    "has_ground": true,
    "has_source": true
  }
}
```

### Simulation Tools

#### simulation.run_dc
Run DC operating point analysis.

**Input:**
```json
{
  "circuit_id": "abc12345"
}
```

**Output:**
```json
{
  "status": "success",
  "simulation_type": "dc",
  "results": {
    "node_voltages": {
      "1": 10.0,
      "2": 5.0
    },
    "branch_currents": {
      "V1": -0.005
    }
  }
}
```

#### simulation.run_transient
Run time-domain simulation.

**Input:**
```json
{
  "circuit_id": "abc12345",
  "stop_time": 0.001,
  "step_time": 0.00001
}
```

**Output:**
```json
{
  "status": "success",
  "simulation_type": "transient",
  "parameters": {
    "stop_time": 0.001,
    "time_points": 100
  },
  "results": {
    "node_voltages": {
      "2": {
        "min": 0.0,
        "max": 4.95,
        "final": 4.95
      }
    }
  }
}
```

### Analysis Tools

#### analysis.get_results
Get detailed simulation results.

**Input:**
```json
{
  "circuit_id": "abc12345",
  "simulation_type": "dc"
}
```

#### analysis.plot
Generate visualization plot.

**Input:**
```json
{
  "circuit_id": "abc12345",
  "simulation_type": "transient",
  "signals": ["V(2)", "I(R1)"]
}
```

**Output:**
```json
{
  "status": "success",
  "plot": {
    "format": "png",
    "encoding": "base64",
    "data": "iVBORw0KGgoAAAANS..."
  }
}
```

## Configuration

Server configuration is stored in `mcp_server_config.json`:

```json
{
  "name": "circuit-simulation-server",
  "limits": {
    "max_circuit_size": 1000,
    "max_simulation_time": 10,
    "rate_limit_per_second": 10
  },
  "security": {
    "allowed_component_types": ["resistor", "capacitor", "inductor"],
    "max_node_value": 10000
  }
}
```

## Example Workflows

### 1. Voltage Divider Analysis

```python
# Create circuit
circuit = await session.call_tool("circuit.create", {
    "name": "Voltage Divider"
})
circuit_id = json.loads(circuit.content[0].text)["circuit_id"]

# Add components
await session.call_tool("circuit.add_component", {
    "circuit_id": circuit_id,
    "type": "voltage_source",
    "name": "V1",
    "value": "10V",
    "positive": 1,
    "negative": 0
})

await session.call_tool("circuit.add_component", {
    "circuit_id": circuit_id,
    "type": "resistor",
    "name": "R1",
    "value": "1k",
    "positive": 1,
    "negative": 2
})

# Simulate
result = await session.call_tool("simulation.run_dc", {
    "circuit_id": circuit_id
})
```

### 2. RC Circuit Transient Response

```python
# Create RC circuit
# ... add voltage source, resistor, capacitor

# Run transient analysis
result = await session.call_tool("simulation.run_transient", {
    "circuit_id": circuit_id,
    "stop_time": 0.05,  # 50ms
    "step_time": 0.0001  # 100µs steps
})

# Generate plot
plot = await session.call_tool("analysis.plot", {
    "circuit_id": circuit_id,
    "simulation_type": "transient",
    "signals": ["V(2)"]  # Capacitor voltage
})
```

## Security & Limits

### Resource Limits
- Maximum 1000 components per circuit
- Maximum 10 seconds simulation time
- Maximum 100MB memory per simulation
- Rate limit: 10 requests per second

### Input Validation
- All component values are validated
- Node numbers must be 0-10000
- Component names must be alphanumeric
- Only allowed component types accepted

### Safety Features
- Automatic timeout for long simulations
- Memory usage monitoring
- Error handling and graceful failure
- Audit logging of all operations

## Troubleshooting

### Common Issues

1. **"Circuit not found"**
   - Circuit IDs are temporary (server session)
   - Check circuit exists with `circuit.list`

2. **"Simulation failed"**
   - Validate circuit first with `circuit.validate`
   - Check for floating nodes or missing ground
   - Ensure circuit has at least one source

3. **"Import errors"**
   - Ensure PySpice and ngspice are installed
   - Check Python path includes src directory

4. **"Connection timeout"**
   - Server runs indefinitely waiting for stdio
   - Connect via MCP client properly
   - Check server logs in `mcp_server.log`

### Debugging

Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check server status:
```bash
tail -f mcp_server.log
```

## Integration Examples

### Claude Desktop Integration

Add to Claude Desktop config:
```json
{
  "mcpServers": {
    "circuit-simulation": {
      "command": "python3",
      "args": ["run_mcp_server.py"],
      "cwd": "/path/to/circuit-simulation"
    }
  }
}
```

### Custom MCP Client

```python
import asyncio
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters

async def simulate_circuit():
    server_params = StdioServerParameters(
        command="python3",
        args=["run_mcp_server.py"]
    )
    
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            
            # Your circuit simulation code here
            pass

asyncio.run(simulate_circuit())
```

## Performance Notes

- DC simulations: ~50ms for 10-node circuits
- Transient simulations: ~200ms for 1000 time points
- Plot generation: ~100ms per figure
- Memory usage: ~10-50MB per active circuit

## Future Enhancements

- AC frequency analysis implementation
- WebSocket transport for remote access
- Circuit schematic generation
- SPICE model library integration
- Collaborative circuit editing
- Real-time simulation streaming

---

For more examples, see `examples/mcp_client_example.py`