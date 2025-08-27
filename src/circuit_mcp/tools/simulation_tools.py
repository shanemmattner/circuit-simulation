"""
Simulation tools for MCP server.
"""

import logging
from datetime import datetime
from typing import Any, Dict

logger = logging.getLogger(__name__)


class SimulationTools:
    """Handles simulation-related MCP tool calls."""

    def __init__(self, server):
        """
        Initialize simulation tools handler.

        Args:
            server: Reference to main MCP server
        """
        self.server = server

    async def handle(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route tool calls to appropriate handlers.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments

        Returns:
            Tool execution results
        """
        # Remove 'simulation.' prefix
        action = tool_name.replace("simulation.", "")

        if action == "run_dc":
            return await self.run_dc_simulation(arguments)
        elif action == "run_transient":
            return await self.run_transient_simulation(arguments)
        elif action == "run_ac":
            return await self.run_ac_simulation(arguments)
        else:
            raise ValueError(f"Unknown simulation tool action: {action}")

    async def run_dc_simulation(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Run DC operating point analysis."""
        circuit_id = args.get("circuit_id")

        # Get circuit
        session = self.server.get_session(circuit_id)
        if not session:
            return {"status": "error", "message": f"Circuit {circuit_id} not found"}

        circuit = session.circuit

        try:
            # Run simulation
            results = self.server.engine.simulate_dc(circuit)

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
                    "convergence": True,
                },
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"DC simulation failed: {e}")
            return {
                "status": "error",
                "message": f"DC simulation failed: {str(e)}",
                "circuit_id": circuit_id,
            }

    async def run_transient_simulation(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Run transient (time-domain) analysis."""
        circuit_id = args.get("circuit_id")
        stop_time = args.get("stop_time", 0.001)  # Default 1ms
        step_time = args.get("step_time", stop_time / 1000)  # Default 1000 points

        # Get circuit
        session = self.server.get_session(circuit_id)
        if not session:
            return {"status": "error", "message": f"Circuit {circuit_id} not found"}

        circuit = session.circuit

        try:
            # Run simulation
            results = self.server.engine.simulate_transient(
                circuit, stop_time=stop_time, step_time=step_time
            )

            # Store results in session
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
                        "points": len(voltage),
                    }

            return {
                "status": "success",
                "simulation_type": "transient",
                "circuit_id": circuit_id,
                "circuit_name": circuit.name,
                "parameters": {
                    "stop_time": stop_time,
                    "step_time": step_time,
                    "time_points": len(time_points),
                },
                "results": {
                    "node_voltages": node_voltages,
                    "time_range": {
                        "start": time_points[0] if time_points else 0,
                        "stop": time_points[-1] if time_points else 0,
                    },
                },
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Transient simulation failed: {e}")
            return {
                "status": "error",
                "message": f"Transient simulation failed: {str(e)}",
                "circuit_id": circuit_id,
            }

    async def run_ac_simulation(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Run AC frequency response analysis."""
        circuit_id = args.get("circuit_id")
        # start_freq = args.get("start_frequency", 10)  # Default 10Hz
        # stop_freq = args.get("stop_frequency", 1e6)  # Default 1MHz
        # points_per_decade = args.get("points_per_decade", 20)

        # AC analysis not yet implemented
        return {
            "status": "error",
            "message": "AC analysis is not yet implemented",
            "circuit_id": circuit_id,
            "note": "This feature is planned for Phase 2",
        }
