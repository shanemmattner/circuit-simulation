"""
Main MCP server implementation for circuit simulation.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from mcp.server import Server
from mcp.types import Tool, TextContent, Resource, Prompt

import sys
from pathlib import Path
# Add parent src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine, SimulationResults

from .tools.circuit_tools import CircuitTools
from .tools.simulation_tools import SimulationTools
from .tools.analysis_tools import AnalysisTools


logger = logging.getLogger(__name__)


@dataclass
class CircuitSession:
    """Represents an active circuit design session."""
    circuit_id: str
    circuit: Circuit
    created_at: datetime
    last_modified: datetime
    simulations: Dict[str, SimulationResults]


class CircuitSimulationMCPServer:
    """MCP server for circuit simulation capabilities."""
    
    def __init__(self, name: str = "circuit-simulation-server"):
        """
        Initialize the MCP server.
        
        Args:
            name: Server name for identification
        """
        self.server = Server(name)
        self.sessions: Dict[str, CircuitSession] = {}
        self.engine = SimulationEngine()
        
        # Initialize tool handlers
        self.circuit_tools = CircuitTools(self)
        self.simulation_tools = SimulationTools(self)
        self.analysis_tools = AnalysisTools(self)
        
        # Register handlers
        self._register_handlers()
        
        logger.info(f"MCP server '{name}' initialized")
    
    def _register_handlers(self):
        """Register all MCP handlers."""
        # Register tool handlers
        self.server.add_list_tools(self._list_tools)
        self.server.add_call_tool(self._call_tool)
        
        # Register resource handlers
        self.server.add_list_resources(self._list_resources)
        self.server.add_read_resource(self._read_resource)
        
        # Register prompt handlers
        self.server.add_list_prompts(self._list_prompts)
        self.server.add_get_prompt(self._get_prompt)
    
    async def _list_tools(self) -> List[Tool]:
        """List all available tools."""
        tools = []
        
        # Circuit management tools
        tools.extend([
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
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
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
        ])
        
        # Simulation tools
        tools.extend([
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
        ])
        
        # Analysis tools
        tools.extend([
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
            Tool(
                name="analysis.plot",
                description="Generate plot of simulation results",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "circuit_id": {"type": "string", "description": "Circuit ID"},
                        "simulation_type": {"type": "string", "enum": ["dc", "transient", "ac"]},
                        "signals": {"type": "array", "items": {"type": "string"}, "description": "Signals to plot (e.g., ['V(2)', 'I(R1)'])"}
                    },
                    "required": ["circuit_id", "simulation_type"]
                }
            ),
        ])
        
        return tools
    
    async def _call_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute a tool and return results."""
        try:
            # Route to appropriate handler
            if name.startswith("circuit."):
                result = await self.circuit_tools.handle(name, arguments)
            elif name.startswith("simulation."):
                result = await self.simulation_tools.handle(name, arguments)
            elif name.startswith("analysis."):
                result = await self.analysis_tools.handle(name, arguments)
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
            error_msg = f"Error executing {name}: {str(e)}"
            return [TextContent(type="text", text=error_msg)]
    
    async def _list_resources(self) -> List[Resource]:
        """List available resources."""
        resources = [
            Resource(
                uri="circuits://examples/voltage_divider",
                name="Voltage Divider Example",
                description="Simple voltage divider circuit",
                mimeType="application/json"
            ),
            Resource(
                uri="circuits://examples/rc_filter",
                name="RC Filter Example",
                description="RC low-pass filter circuit",
                mimeType="application/json"
            ),
            Resource(
                uri="circuits://docs/components",
                name="Component Reference",
                description="Documentation for available components",
                mimeType="text/markdown"
            ),
            Resource(
                uri="circuits://docs/simulation",
                name="Simulation Guide",
                description="Guide to running simulations",
                mimeType="text/markdown"
            ),
        ]
        return resources
    
    async def _read_resource(self, uri: str) -> TextContent:
        """Read a resource by URI."""
        if uri == "circuits://examples/voltage_divider":
            example = {
                "name": "Voltage Divider",
                "components": [
                    {"type": "voltage_source", "name": "V1", "value": "10V", "positive": 1, "negative": 0},
                    {"type": "resistor", "name": "R1", "value": "1k", "positive": 1, "negative": 2},
                    {"type": "resistor", "name": "R2", "value": "1k", "positive": 2, "negative": 0}
                ],
                "expected_output": {
                    "V(2)": "5V"
                }
            }
            return TextContent(type="text", text=json.dumps(example, indent=2))
        
        elif uri == "circuits://examples/rc_filter":
            example = {
                "name": "RC Low-Pass Filter",
                "components": [
                    {"type": "voltage_source", "name": "V1", "value": "5V", "positive": 1, "negative": 0},
                    {"type": "resistor", "name": "R1", "value": "10k", "positive": 1, "negative": 2},
                    {"type": "capacitor", "name": "C1", "value": "100nF", "positive": 2, "negative": 0}
                ],
                "cutoff_frequency": "159.15 Hz"
            }
            return TextContent(type="text", text=json.dumps(example, indent=2))
        
        elif uri == "circuits://docs/components":
            docs = """# Component Reference

## Resistor
- Type: `resistor`
- Value format: `1k`, `10k`, `1M`
- Nodes: positive, negative

## Capacitor
- Type: `capacitor`
- Value format: `10uF`, `100nF`, `1pF`
- Nodes: positive, negative

## Inductor
- Type: `inductor`
- Value format: `100mH`, `10uH`, `1H`
- Nodes: positive, negative

## Voltage Source
- Type: `voltage_source`
- Value format: `5V`, `3.3V`, `-12V`
- Nodes: positive, negative

## Current Source
- Type: `current_source`
- Value format: `10mA`, `1A`
- Nodes: positive, negative
"""
            return TextContent(type="text", text=docs)
        
        else:
            return TextContent(type="text", text=f"Resource not found: {uri}")
    
    async def _list_prompts(self) -> List[Prompt]:
        """List available prompts."""
        prompts = [
            Prompt(
                name="circuit_design",
                description="Help me design a circuit",
                arguments=[
                    {"name": "requirements", "description": "Circuit requirements", "required": True},
                    {"name": "constraints", "description": "Design constraints", "required": False}
                ]
            ),
            Prompt(
                name="debug_circuit",
                description="Help me debug a circuit problem",
                arguments=[
                    {"name": "circuit_id", "description": "Circuit to debug", "required": True},
                    {"name": "problem", "description": "Description of the problem", "required": True}
                ]
            ),
            Prompt(
                name="learn_electronics",
                description="Teach me about electronic circuits",
                arguments=[
                    {"name": "topic", "description": "Topic to learn", "required": True},
                    {"name": "level", "description": "Experience level (beginner/intermediate/advanced)", "required": False}
                ]
            ),
        ]
        return prompts
    
    async def _get_prompt(self, name: str, arguments: Dict[str, str]) -> Prompt:
        """Get a prompt template with filled arguments."""
        if name == "circuit_design":
            requirements = arguments.get("requirements", "")
            constraints = arguments.get("constraints", "none specified")
            
            messages = [
                {
                    "role": "user",
                    "content": f"""Please help me design a circuit with these requirements:
                    
Requirements: {requirements}
Constraints: {constraints}

Please:
1. Suggest appropriate components
2. Provide the circuit topology
3. Calculate component values
4. Explain the design choices
5. Simulate the circuit to verify it meets requirements"""
                }
            ]
            
            return Prompt(
                name="circuit_design",
                description="Circuit design assistant",
                arguments=[],
                messages=messages
            )
        
        elif name == "debug_circuit":
            circuit_id = arguments.get("circuit_id", "")
            problem = arguments.get("problem", "")
            
            messages = [
                {
                    "role": "user", 
                    "content": f"""Help me debug this circuit problem:

Circuit ID: {circuit_id}
Problem: {problem}

Please:
1. Analyze the circuit configuration
2. Run appropriate simulations
3. Identify potential issues
4. Suggest fixes
5. Verify the solution works"""
                }
            ]
            
            return Prompt(
                name="debug_circuit",
                description="Circuit debugging assistant",
                arguments=[],
                messages=messages
            )
        
        else:
            return Prompt(
                name=name,
                description="Unknown prompt",
                arguments=[],
                messages=[]
            )
    
    def create_circuit(self, name: str, description: str = "") -> str:
        """Create a new circuit and return its ID."""
        import uuid
        circuit_id = str(uuid.uuid4())[:8]
        
        session = CircuitSession(
            circuit_id=circuit_id,
            circuit=Circuit(name),
            created_at=datetime.now(),
            last_modified=datetime.now(),
            simulations={}
        )
        
        self.sessions[circuit_id] = session
        logger.info(f"Created circuit '{name}' with ID: {circuit_id}")
        
        return circuit_id
    
    def get_circuit(self, circuit_id: str) -> Optional[Circuit]:
        """Get a circuit by ID."""
        session = self.sessions.get(circuit_id)
        return session.circuit if session else None
    
    def get_session(self, circuit_id: str) -> Optional[CircuitSession]:
        """Get a circuit session by ID."""
        return self.sessions.get(circuit_id)
    
    async def run(self):
        """Run the MCP server."""
        logger.info("Starting MCP server...")
        async with self.server.run_stdio():
            # Keep server running
            await asyncio.Event().wait()


async def main():
    """Main entry point for the MCP server."""
    logging.basicConfig(level=logging.INFO)
    
    server = CircuitSimulationMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())