"""
Main MCP server implementation for circuit simulation.
"""

import asyncio
import json
import logging
import uuid
from typing import Any, Dict, List, Optional, Sequence
from dataclasses import dataclass
from datetime import datetime

import sys
from pathlib import Path
# Add parent src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine, SimulationResults


logger = logging.getLogger(__name__)


@dataclass
class CircuitSession:
    """Represents an active circuit design session."""
    circuit_id: str
    circuit: Circuit
    created_at: datetime
    last_modified: datetime
    simulations: Dict[str, SimulationResults]


# Global storage for circuit sessions
SESSIONS: Dict[str, CircuitSession] = {}
ENGINE = SimulationEngine()


async def serve() -> None:
    """Main server function."""
    server = Server("circuit-simulation-server")
    
    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List all available tools."""
        return [
            Tool(
                name="circuit.create",
                description="Create a new circuit",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Circuit name"},
                        "description": {"type": "string", "description": "Circuit description"}
                    },
                    "required": ["name"]
                }
            ),
            Tool(
                name="circuit.add_component",
                description="Add a component to a circuit",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "circuit_id": {"type": "string", "description": "Circuit ID"},
                        "type": {"type": "string", "enum": ["resistor", "capacitor", "inductor", "voltage_source", "current_source"]},
                        "name": {"type": "string", "description": "Component name (e.g., R1, C1)"},
                        "value": {"type": "string", "description": "Component value (e.g., 1k, 10uF)"},
                        "positive": {"type": "integer", "description": "Positive node"},
                        "negative": {"type": "integer", "description": "Negative node"}
                    },
                    "required": ["circuit_id", "type", "name", "value", "positive", "negative"]
                }
            ),
            Tool(
                name="circuit.list",
                description="List all active circuits",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="circuit.get",
                description="Get circuit details",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "circuit_id": {"type": "string", "description": "Circuit ID"}
                    },
                    "required": ["circuit_id"]
                }
            ),
            Tool(
                name="circuit.validate",
                description="Validate circuit connectivity and components",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "circuit_id": {"type": "string", "description": "Circuit ID"}
                    },
                    "required": ["circuit_id"]
                }
            ),
            Tool(
                name="simulation.run_dc",
                description="Run DC operating point analysis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "circuit_id": {"type": "string", "description": "Circuit ID"}
                    },
                    "required": ["circuit_id"]
                }
            ),
            Tool(
                name="simulation.run_transient",
                description="Run transient (time-domain) analysis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "circuit_id": {"type": "string", "description": "Circuit ID"},
                        "stop_time": {"type": "number", "description": "Simulation stop time in seconds"},
                        "step_time": {"type": "number", "description": "Time step in seconds"}
                    },
                    "required": ["circuit_id", "stop_time"]
                }
            ),
            Tool(
                name="analysis.get_results",
                description="Get simulation results",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "circuit_id": {"type": "string", "description": "Circuit ID"},
                        "simulation_type": {"type": "string", "enum": ["dc", "transient", "ac"], "description": "Type of simulation"}
                    },
                    "required": ["circuit_id", "simulation_type"]
                }
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Execute a tool and return results."""
        try:
            # Route to appropriate handler
            if name.startswith("circuit."):
                result = await handle_circuit_tool(name, arguments)
            elif name.startswith("simulation."):
                result = await handle_simulation_tool(name, arguments)
            elif name.startswith("analysis."):
                result = await handle_analysis_tool(name, arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
            
            # Format result as TextContent
            if isinstance(result, dict):
                content = json.dumps(result, indent=2)
            else:
                content = str(result)
            
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            error_result = {
                "status": "error",
                "message": f"Error executing {name}: {str(e)}",
                "tool": name
            }
            return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

    # Run the server
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)


async def handle_circuit_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle circuit-related tools."""
    action = tool_name.replace("circuit.", "")
    
    if action == "create":
        return await create_circuit(arguments)
    elif action == "add_component":
        return await add_component(arguments)
    elif action == "list":
        return await list_circuits()
    elif action == "get":
        return await get_circuit(arguments)
    elif action == "validate":
        return await validate_circuit(arguments)
    else:
        raise ValueError(f"Unknown circuit action: {action}")


async def handle_simulation_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle simulation-related tools."""
    action = tool_name.replace("simulation.", "")
    
    if action == "run_dc":
        return await run_dc_simulation(arguments)
    elif action == "run_transient":
        return await run_transient_simulation(arguments)
    else:
        raise ValueError(f"Unknown simulation action: {action}")


async def handle_analysis_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle analysis-related tools."""
    action = tool_name.replace("analysis.", "")
    
    if action == "get_results":
        return await get_results(arguments)
    else:
        raise ValueError(f"Unknown analysis action: {action}")


async def create_circuit(args: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new circuit."""
    name = args.get("name", "Untitled Circuit")
    description = args.get("description", "")
    
    circuit_id = str(uuid.uuid4())[:8]
    
    session = CircuitSession(
        circuit_id=circuit_id,
        circuit=Circuit(name),
        created_at=datetime.now(),
        last_modified=datetime.now(),
        simulations={}
    )
    
    SESSIONS[circuit_id] = session
    logger.info(f"Created circuit '{name}' with ID: {circuit_id}")
    
    return {
        "status": "success",
        "circuit_id": circuit_id,
        "name": name,
        "description": description,
        "created_at": datetime.now().isoformat()
    }


async def add_component(args: Dict[str, Any]) -> Dict[str, Any]:
    """Add a component to a circuit."""
    circuit_id = args.get("circuit_id")
    component_type = args.get("type")
    name = args.get("name")
    value = args.get("value")
    positive = args.get("positive")
    negative = args.get("negative")
    
    # Get circuit
    session = SESSIONS.get(circuit_id)
    if not session:
        return {"status": "error", "message": f"Circuit {circuit_id} not found"}
    
    circuit = session.circuit
    
    # Add component based on type
    try:
        if component_type == "resistor":
            circuit.add_resistor(name, positive, negative, value)
        elif component_type == "capacitor":
            circuit.add_capacitor(name, positive, negative, value)
        elif component_type == "inductor":
            circuit.add_inductor(name, positive, negative, value)
        elif component_type == "voltage_source":
            circuit.add_voltage_source(name, positive, negative, value)
        elif component_type == "current_source":
            circuit.add_current_source(name, positive, negative, value)
        else:
            return {"status": "error", "message": f"Unknown component type: {component_type}"}
        
        # Update session
        session.last_modified = datetime.now()
        
        return {
            "status": "success",
            "message": f"Added {component_type} {name} to circuit",
            "component": {
                "type": component_type,
                "name": name,
                "value": value,
                "nodes": {"positive": positive, "negative": negative}
            }
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Failed to add component: {str(e)}"}


async def list_circuits() -> Dict[str, Any]:
    """List all active circuits."""
    circuits = []
    
    for circuit_id, session in SESSIONS.items():
        circuits.append({
            "circuit_id": circuit_id,
            "name": session.circuit.name,
            "components": len(session.circuit.components),
            "nodes": len(session.circuit.nodes),
            "created_at": session.created_at.isoformat(),
            "last_modified": session.last_modified.isoformat(),
            "simulations": list(session.simulations.keys())
        })
    
    return {"status": "success", "count": len(circuits), "circuits": circuits}


async def get_circuit(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get details of a specific circuit."""
    circuit_id = args.get("circuit_id")
    
    session = SESSIONS.get(circuit_id)
    if not session:
        return {"status": "error", "message": f"Circuit {circuit_id} not found"}
    
    circuit = session.circuit
    
    # Format components
    components = []
    for comp in circuit.components:
        comp_dict = {
            "type": comp.component_type,
            "name": comp.name,
        }
        
        # Extract node connections
        if hasattr(comp, 'positive') and hasattr(comp, 'negative'):
            comp_dict["nodes"] = {"positive": comp.positive, "negative": comp.negative}
        elif hasattr(comp, 'node1') and hasattr(comp, 'node2'):
            comp_dict["nodes"] = {"node1": comp.node1, "node2": comp.node2}
        
        # Add value
        for attr in ['resistance', 'capacitance', 'inductance', 'dc_value', 'dc_current']:
            if hasattr(comp, attr):
                comp_dict["value"] = getattr(comp, attr)
                break
        
        components.append(comp_dict)
    
    return {
        "status": "success",
        "circuit": {
            "id": circuit_id,
            "name": circuit.name,
            "components": components,
            "nodes": list(circuit.nodes),
            "created_at": session.created_at.isoformat(),
            "last_modified": session.last_modified.isoformat()
        }
    }


async def validate_circuit(args: Dict[str, Any]) -> Dict[str, Any]:
    """Validate circuit connectivity and components."""
    circuit_id = args.get("circuit_id")
    
    session = SESSIONS.get(circuit_id)
    if not session:
        return {"status": "error", "message": f"Circuit {circuit_id} not found"}
    
    circuit = session.circuit
    issues = []
    warnings = []
    
    # Check if circuit has components
    if not circuit.components:
        issues.append("Circuit has no components")
    
    # Check if circuit has at least one source
    has_source = any(
        comp.component_type in ["voltage_source", "current_source"]
        for comp in circuit.components
    )
    if not has_source:
        issues.append("Circuit has no voltage or current sources")
    
    # Check for ground connection (node 0)
    if 0 not in circuit.nodes:
        warnings.append("Circuit has no explicit ground (node 0)")
    
    valid = len(issues) == 0
    
    return {
        "status": "success",
        "valid": valid,
        "issues": issues,
        "warnings": warnings,
        "summary": {
            "components": len(circuit.components),
            "nodes": len(circuit.nodes),
            "has_ground": 0 in circuit.nodes,
            "has_source": has_source
        }
    }


async def run_dc_simulation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Run DC operating point analysis."""
    circuit_id = args.get("circuit_id")
    
    session = SESSIONS.get(circuit_id)
    if not session:
        return {"status": "error", "message": f"Circuit {circuit_id} not found"}
    
    circuit = session.circuit
    
    try:
        # Run simulation
        results = ENGINE.simulate_dc(circuit)
        
        # Store results in session
        session.simulations["dc"] = results
        session.last_modified = datetime.now()
        
        # Extract node voltages
        node_voltages = {}
        for node in results.nodes:
            voltage = results.voltage(node)
            if voltage is not None:
                node_voltages[str(node)] = float(voltage[0])
        
        # Extract branch currents if available
        branch_currents = {}
        for component in results.components:
            current = results.current(component)
            if current is not None:
                branch_currents[component] = float(current[0])
        
        return {
            "status": "success",
            "simulation_type": "dc",
            "circuit_id": circuit_id,
            "circuit_name": circuit.name,
            "results": {
                "node_voltages": node_voltages,
                "branch_currents": branch_currents,
                "convergence": True
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"DC simulation failed: {e}")
        return {"status": "error", "message": f"DC simulation failed: {str(e)}", "circuit_id": circuit_id}


async def run_transient_simulation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Run transient analysis."""
    circuit_id = args.get("circuit_id")
    stop_time = args.get("stop_time", 0.001)
    step_time = args.get("step_time", stop_time / 1000)
    
    session = SESSIONS.get(circuit_id)
    if not session:
        return {"status": "error", "message": f"Circuit {circuit_id} not found"}
    
    circuit = session.circuit
    
    try:
        results = ENGINE.simulate_transient(circuit, stop_time=stop_time, step_time=step_time)
        
        session.simulations["transient"] = results
        session.last_modified = datetime.now()
        
        # Get time vector
        time_points = []
        if results.time is not None:
            time_points = results.time.tolist()
        
        # Extract node voltages over time
        node_voltages = {}
        for node in results.nodes:
            voltage = results.voltage(node)
            if voltage is not None:
                node_voltages[str(node)] = {
                    "min": float(voltage.min()),
                    "max": float(voltage.max()),
                    "final": float(voltage[-1]),
                    "points": len(voltage)
                }
        
        return {
            "status": "success",
            "simulation_type": "transient",
            "circuit_id": circuit_id,
            "circuit_name": circuit.name,
            "parameters": {
                "stop_time": stop_time,
                "step_time": step_time,
                "time_points": len(time_points)
            },
            "results": {
                "node_voltages": node_voltages,
                "time_range": {
                    "start": time_points[0] if time_points else 0,
                    "stop": time_points[-1] if time_points else 0
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Transient simulation failed: {e}")
        return {"status": "error", "message": f"Transient simulation failed: {str(e)}", "circuit_id": circuit_id}


async def get_results(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get detailed simulation results."""
    circuit_id = args.get("circuit_id")
    simulation_type = args.get("simulation_type", "dc")
    
    session = SESSIONS.get(circuit_id)
    if not session:
        return {"status": "error", "message": f"Circuit {circuit_id} not found"}
    
    results = session.simulations.get(simulation_type)
    if not results:
        return {"status": "error", "message": f"No {simulation_type} simulation results for circuit {circuit_id}"}
    
    # Format results
    if simulation_type == "dc":
        node_voltages = {}
        for node in results.nodes:
            voltage = results.voltage(node)
            if voltage is not None:
                node_voltages[f"V({node})"] = {"value": float(voltage[0]), "unit": "V"}
        
        return {
            "status": "success",
            "circuit_id": circuit_id,
            "circuit_name": session.circuit.name,
            "simulation_type": "dc",
            "results": {"node_voltages": node_voltages}
        }
    
    return {"status": "error", "message": f"Analysis for {simulation_type} not yet implemented"}