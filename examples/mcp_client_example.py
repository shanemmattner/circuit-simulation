#!/usr/bin/env python3
"""
Example MCP client for testing the circuit simulation server.

This demonstrates how to connect to the MCP server and use its tools.
"""

import asyncio
import json
import sys
from typing import Any, Dict

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_circuit_simulation():
    """Test the circuit simulation MCP server."""
    
    # Connect to server via stdio
    server_params = StdioServerParameters(
        command="python3",
        args=["run_mcp_server.py"],
        cwd="."
    )
    
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            print("Connected to MCP server")
            
            # Initialize session
            await session.initialize()
            
            # List available tools
            print("\n=== Available Tools ===")
            tools_response = await session.list_tools()
            for tool in tools_response.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Create a voltage divider circuit
            print("\n=== Creating Voltage Divider ===")
            
            # 1. Create circuit
            create_result = await session.call_tool(
                "circuit.create",
                arguments={
                    "name": "Voltage Divider Test",
                    "description": "Simple resistor divider for testing"
                }
            )
            result_data = json.loads(create_result.content[0].text)
            circuit_id = result_data["circuit_id"]
            print(f"Created circuit with ID: {circuit_id}")
            
            # 2. Add components
            components = [
                {
                    "type": "voltage_source",
                    "name": "V1",
                    "value": "10V",
                    "positive": 1,
                    "negative": 0
                },
                {
                    "type": "resistor",
                    "name": "R1",
                    "value": "1k",
                    "positive": 1,
                    "negative": 2
                },
                {
                    "type": "resistor",
                    "name": "R2",
                    "value": "1k",
                    "positive": 2,
                    "negative": 0
                }
            ]
            
            for comp in components:
                result = await session.call_tool(
                    "circuit.add_component",
                    arguments={
                        "circuit_id": circuit_id,
                        **comp
                    }
                )
                result_data = json.loads(result.content[0].text)
                print(f"Added {comp['type']} {comp['name']}: {result_data['status']}")
            
            # 3. Validate circuit
            print("\n=== Validating Circuit ===")
            validation = await session.call_tool(
                "circuit.validate",
                arguments={"circuit_id": circuit_id}
            )
            validation_data = json.loads(validation.content[0].text)
            print(f"Circuit valid: {validation_data['valid']}")
            if validation_data.get('warnings'):
                print(f"Warnings: {validation_data['warnings']}")
            
            # 4. Run DC simulation
            print("\n=== Running DC Simulation ===")
            dc_result = await session.call_tool(
                "simulation.run_dc",
                arguments={"circuit_id": circuit_id}
            )
            dc_data = json.loads(dc_result.content[0].text)
            
            if dc_data["status"] == "success":
                print("DC Operating Point:")
                for node, voltage in dc_data["results"]["node_voltages"].items():
                    print(f"  Node {node}: {voltage:.3f}V")
            
            # 5. Create RC circuit for transient
            print("\n=== Creating RC Circuit ===")
            rc_result = await session.call_tool(
                "circuit.create",
                arguments={
                    "name": "RC Circuit",
                    "description": "RC circuit for transient analysis"
                }
            )
            rc_data = json.loads(rc_result.content[0].text)
            rc_id = rc_data["circuit_id"]
            
            # Add RC components
            rc_components = [
                {
                    "type": "voltage_source",
                    "name": "V1",
                    "value": "5V",
                    "positive": 1,
                    "negative": 0
                },
                {
                    "type": "resistor",
                    "name": "R1",
                    "value": "10k",
                    "positive": 1,
                    "negative": 2
                },
                {
                    "type": "capacitor",
                    "name": "C1",
                    "value": "1uF",
                    "positive": 2,
                    "negative": 0
                }
            ]
            
            for comp in rc_components:
                await session.call_tool(
                    "circuit.add_component",
                    arguments={
                        "circuit_id": rc_id,
                        **comp
                    }
                )
            
            # 6. Run transient simulation
            print("\n=== Running Transient Simulation ===")
            transient_result = await session.call_tool(
                "simulation.run_transient",
                arguments={
                    "circuit_id": rc_id,
                    "stop_time": 0.05,  # 50ms
                    "step_time": 0.0001  # 100us
                }
            )
            transient_data = json.loads(transient_result.content[0].text)
            
            if transient_data["status"] == "success":
                print(f"Transient simulation completed")
                print(f"Time points: {transient_data['parameters']['time_points']}")
                for node, stats in transient_data["results"]["node_voltages"].items():
                    print(f"  Node {node}: min={stats['min']:.3f}V, max={stats['max']:.3f}V, final={stats['final']:.3f}V")
            
            # 7. Get detailed results
            print("\n=== Getting Detailed Results ===")
            results = await session.call_tool(
                "analysis.get_results",
                arguments={
                    "circuit_id": rc_id,
                    "simulation_type": "transient"
                }
            )
            results_data = json.loads(results.content[0].text)
            print(f"Analysis summary: {results_data['results']['summary']}")
            
            # 8. Generate plot
            print("\n=== Generating Plot ===")
            plot_result = await session.call_tool(
                "analysis.plot",
                arguments={
                    "circuit_id": rc_id,
                    "simulation_type": "transient",
                    "signals": ["V(2)"]
                }
            )
            plot_data = json.loads(plot_result.content[0].text)
            if plot_data["status"] == "success":
                print(f"Plot generated successfully (base64 encoded PNG)")
                # In a real application, you would decode and save/display the image
                print(f"Plot data length: {len(plot_data['plot']['data'])} characters")
            
            # 9. List all circuits
            print("\n=== All Circuits ===")
            list_result = await session.call_tool(
                "circuit.list",
                arguments={}
            )
            list_data = json.loads(list_result.content[0].text)
            print(f"Total circuits: {list_data['count']}")
            for circuit in list_data["circuits"]:
                print(f"  - {circuit['name']} (ID: {circuit['circuit_id']})")
                print(f"    Components: {circuit['components']}, Nodes: {circuit['nodes']}")
            
            # 10. Test resources
            print("\n=== Available Resources ===")
            resources = await session.list_resources()
            for resource in resources.resources:
                print(f"  - {resource.name}: {resource.description}")
            
            # Read an example resource
            print("\n=== Reading Example Resource ===")
            example = await session.read_resource("circuits://examples/voltage_divider")
            print("Voltage Divider Example:")
            print(example.content[0].text)
            
            print("\n=== Test Complete ===")


async def main():
    """Main entry point."""
    try:
        await test_circuit_simulation()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("MCP Client Test for Circuit Simulation Server")
    print("=" * 50)
    asyncio.run(main())