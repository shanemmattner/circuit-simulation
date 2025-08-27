# How to Test the MCP Server 🧪

## Overview

The Circuit Simulation MCP server enables AI assistants to create and simulate electronic circuits. Here are several ways to test it.

## Method 1: Direct Function Testing ✅ RECOMMENDED

Test the core functions directly without MCP protocol overhead:

```bash
# Test locally (if you have PySpice)
python3 test_circuit_functions.py

# Test in Docker (recommended)
docker-compose run --rm circuit-sim python3 test_circuit_functions.py
```

**Expected Output:**
```
🧪 Testing Circuit Simulation MCP Functions
==================================================

1. Creating voltage divider circuit...
   ✅ Created circuit with ID: 6592435b

2. Adding voltage source...
   ✅ Added voltage source V1

3. Adding resistors...
   ✅ Added resistors R1 and R2

4. Validating circuit...
   ✅ Circuit validation: PASSED

5. Running DC simulation...
   ✅ DC simulation completed successfully!
   📊 Results:
      Node 2: 5.000V
      Node 1: 10.000V
   ✅ Voltage divider working correctly: 5.000V ≈ 5.0V

==================================================
🎉 MCP server functions are working correctly!
✨ Ready for MCP client integration
```

## Method 2: Claude Code Integration 🔧

### Add MCP Server to Claude Code

1. **Add the server to your project:**
```bash
# From the project root directory
claude mcp add circuit-simulation -- python3 run_mcp_server.py
```

2. **Verify it's added:**
```bash
claude mcp list
```

3. **Test with Claude Code:**
Once added, you can use circuit simulation tools directly in Claude Code:
- `circuit.create` - Create new circuits
- `circuit.add_component` - Add components (R, L, C, voltage sources)
- `simulation.run_dc` - Run DC analysis
- `analysis.get_results` - Get simulation results with plots

### Remove Server (if needed)
```bash
claude mcp remove circuit-simulation
```

## Method 3: Claude Desktop Integration

### Add to Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

**Note:** Replace `/path/to/circuit-simulation` with your actual project path.

## Method 4: MCP Server Testing

### Start the Server

```bash
# Start MCP server (waits for stdio connections)
python3 run_mcp_server.py

# Expected output:
INFO:__main__:Starting Circuit Simulation MCP Server
INFO:__main__:Server ready for MCP client connections via stdio
```

The server will run indefinitely, waiting for MCP client connections via stdio.

### Test Server is Running

In another terminal:
```bash
# Check if server process is running
ps aux | grep run_mcp_server

# Check server logs (if configured)
tail -f mcp_server.log
```

## Method 3: Claude Desktop Integration 🤖

### Prerequisites

1. **Install Claude Desktop** from Anthropic
2. **Locate Claude config** file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

### Configuration

Add to your Claude Desktop config:
```json
{
  "mcpServers": {
    "circuit-simulation": {
      "command": "python3",
      "args": ["run_mcp_server.py"],
      "cwd": "/absolute/path/to/circuit-simulation"
    }
  }
}
```

**Important**: Use the absolute path to your circuit-simulation directory!

### Testing with Claude

1. **Restart Claude Desktop** after config change
2. **Start a new conversation**
3. **Test basic commands**:

```
You: Can you list the available MCP tools?

You: Create a voltage divider circuit with 10V input and two 1k resistors

You: Run a DC simulation on the circuit you just created

You: What's the voltage at node 2?

You: Create an RC filter with R=10k and C=100nF

You: Run a transient simulation for 50ms
```

### Expected Claude Responses

Claude should respond with circuit creation confirmations, simulation results, and detailed analysis. If working correctly, you'll see:

- Circuit IDs generated
- Component additions confirmed
- Simulation results with node voltages
- Validation feedback

## Method 4: Custom MCP Client Testing

### Simple Test Client

```python
import asyncio
import json
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters

async def test_mcp_client():
    server_params = StdioServerParameters(
        command="python3",
        args=["run_mcp_server.py"],
        cwd="."
    )
    
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            
            # Test tool listing
            tools = await session.list_tools()
            print(f"Available tools: {len(tools.tools)}")
            
            # Create circuit
            result = await session.call_tool(
                "circuit.create",
                arguments={"name": "Test Circuit"}
            )
            
            circuit_data = json.loads(result.content[0].text)
            print(f"Created circuit: {circuit_data['circuit_id']}")

# Run test
asyncio.run(test_mcp_client())
```

## Method 5: Manual API Testing

### Direct Server Functions

You can test individual server functions:

```python
import asyncio
import sys
sys.path.insert(0, "src")

# Import server functions directly
from circuit_mcp.server import create_circuit, add_component, run_dc_simulation

async def manual_test():
    # Create circuit
    circuit = await create_circuit({"name": "Manual Test"})
    circuit_id = circuit["circuit_id"]
    
    # Add components
    await add_component({
        "circuit_id": circuit_id,
        "type": "voltage_source",
        "name": "V1",
        "value": "5V", 
        "positive": 1,
        "negative": 0
    })
    
    # Add resistor
    await add_component({
        "circuit_id": circuit_id,
        "type": "resistor",
        "name": "R1",
        "value": "1k",
        "positive": 1,
        "negative": 0
    })
    
    # Simulate
    results = await run_dc_simulation({"circuit_id": circuit_id})
    print("Simulation results:", results)

asyncio.run(manual_test())
```

## Troubleshooting 🔧

### Common Issues

1. **"ModuleNotFoundError: No module named 'mcp'"**
   - **Solution**: Install MCP package: `pip install mcp`
   - **Or**: Test functions directly with `test_circuit_functions.py`

2. **"PySpice is not installed"**  
   - **Solution**: Use Docker: `docker-compose run circuit-sim`
   - **Local fix**: Install PySpice and ngspice

3. **"Circuit not found"**
   - **Cause**: Circuit IDs are session-specific
   - **Solution**: Create circuit in same session as simulation

4. **"Server not responding"**
   - **Check**: Server is running and waiting for stdio
   - **Solution**: Connect via proper MCP client

### Verification Commands

```bash
# 1. Check server starts
timeout 3 python3 run_mcp_server.py

# 2. Test core functions 
python3 test_circuit_functions.py

# 3. Test in Docker
docker-compose run --rm circuit-sim python3 test_circuit_functions.py

# 4. Check imports work
python3 -c "import sys; sys.path.insert(0, 'src'); from circuit_mcp.server import serve; print('✅ MCP server imports OK')"
```

## Success Criteria ✅

A working MCP server should:

- ✅ Start without errors
- ✅ Create circuits with unique IDs  
- ✅ Add all component types (R, L, C, V, I)
- ✅ Validate circuit topology
- ✅ Run DC simulations successfully
- ✅ Return structured JSON results
- ✅ Handle errors gracefully

## Example Test Results

When working correctly:
- **Voltage Divider**: 10V input → 5.000V at middle node
- **RC Circuit**: Proper charging curves
- **Validation**: Detects missing sources, floating nodes
- **Response Time**: < 100ms for simple circuits

## Next Steps

Once MCP server testing is successful:

1. **Connect to Claude Desktop** using the config above
2. **Test AI interactions** with circuit design requests
3. **Create more complex circuits** (amplifiers, filters)
4. **Add plotting tools** to MCP interface
5. **Implement AC analysis** for frequency response

---

For detailed API reference, see [MCP_SERVER.md](MCP_SERVER.md)