"""
Analysis tools for MCP server.
"""

import logging
import json
import base64
import io
from typing import Any, Dict, List, Optional

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class AnalysisTools:
    """Handles analysis-related MCP tool calls."""
    
    def __init__(self, server):
        """
        Initialize analysis tools handler.
        
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
        # Remove 'analysis.' prefix
        action = tool_name.replace("analysis.", "")
        
        if action == "get_results":
            return await self.get_results(arguments)
        elif action == "plot":
            return await self.generate_plot(arguments)
        elif action == "export":
            return await self.export_circuit(arguments)
        else:
            raise ValueError(f"Unknown analysis tool action: {action}")
    
    async def get_results(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed simulation results."""
        circuit_id = args.get("circuit_id")
        simulation_type = args.get("simulation_type", "dc")
        
        # Get session
        session = self.server.get_session(circuit_id)
        if not session:
            return {
                "status": "error",
                "message": f"Circuit {circuit_id} not found"
            }
        
        # Get results
        results = session.simulations.get(simulation_type)
        if not results:
            return {
                "status": "error",
                "message": f"No {simulation_type} simulation results for circuit {circuit_id}"
            }
        
        # Format results based on type
        if simulation_type == "dc":
            return self._format_dc_results(circuit_id, session.circuit.name, results)
        elif simulation_type == "transient":
            return self._format_transient_results(circuit_id, session.circuit.name, results)
        else:
            return {
                "status": "error",
                "message": f"Unknown simulation type: {simulation_type}"
            }
    
    def _format_dc_results(self, circuit_id: str, circuit_name: str, results) -> Dict[str, Any]:
        """Format DC simulation results."""
        # Extract all node voltages
        node_voltages = {}
        for node in results.nodes:
            voltage = results.voltage(node)
            if voltage is not None:
                node_voltages[f"V({node})"] = {
                    "value": float(voltage[0]),
                    "unit": "V"
                }
        
        # Extract all branch currents
        branch_currents = {}
        for component in results.components:
            current = results.current(component)
            if current is not None:
                branch_currents[f"I({component})"] = {
                    "value": float(current[0]),
                    "unit": "A"
                }
        
        # Calculate power dissipation for resistors
        power_dissipation = {}
        for component in results.components:
            current = results.current(component)
            if current is not None and component.startswith("R"):
                # For resistors, P = I²R (would need resistance value)
                # For now, just note the current
                power_dissipation[component] = {
                    "current": float(current[0]),
                    "unit": "A"
                }
        
        return {
            "status": "success",
            "circuit_id": circuit_id,
            "circuit_name": circuit_name,
            "simulation_type": "dc",
            "results": {
                "node_voltages": node_voltages,
                "branch_currents": branch_currents,
                "power_dissipation": power_dissipation,
                "summary": {
                    "nodes_analyzed": len(node_voltages),
                    "components_analyzed": len(branch_currents)
                }
            }
        }
    
    def _format_transient_results(self, circuit_id: str, circuit_name: str, results) -> Dict[str, Any]:
        """Format transient simulation results."""
        # Get time vector
        time_data = None
        if results.time is not None:
            time_data = {
                "points": len(results.time),
                "start": float(results.time[0]),
                "stop": float(results.time[-1]),
                "step": float(results.time[1] - results.time[0]) if len(results.time) > 1 else 0
            }
        
        # Extract node voltage statistics
        node_voltages = {}
        for node in results.nodes:
            voltage = results.voltage(node)
            if voltage is not None:
                node_voltages[f"V({node})"] = {
                    "min": float(np.min(voltage)),
                    "max": float(np.max(voltage)),
                    "mean": float(np.mean(voltage)),
                    "std": float(np.std(voltage)),
                    "initial": float(voltage[0]),
                    "final": float(voltage[-1]),
                    "unit": "V"
                }
        
        # Extract current statistics
        branch_currents = {}
        for component in results.components:
            current = results.current(component)
            if current is not None:
                branch_currents[f"I({component})"] = {
                    "min": float(np.min(current)),
                    "max": float(np.max(current)),
                    "mean": float(np.mean(current)),
                    "std": float(np.std(current)),
                    "initial": float(current[0]),
                    "final": float(current[-1]),
                    "unit": "A"
                }
        
        return {
            "status": "success",
            "circuit_id": circuit_id,
            "circuit_name": circuit_name,
            "simulation_type": "transient",
            "results": {
                "time_data": time_data,
                "node_voltages": node_voltages,
                "branch_currents": branch_currents,
                "summary": {
                    "duration": time_data["stop"] - time_data["start"] if time_data else 0,
                    "time_points": time_data["points"] if time_data else 0,
                    "nodes_analyzed": len(node_voltages),
                    "components_analyzed": len(branch_currents)
                }
            }
        }
    
    async def generate_plot(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Generate plot of simulation results."""
        circuit_id = args.get("circuit_id")
        simulation_type = args.get("simulation_type", "dc")
        signals = args.get("signals", [])
        
        # Get session
        session = self.server.get_session(circuit_id)
        if not session:
            return {
                "status": "error",
                "message": f"Circuit {circuit_id} not found"
            }
        
        # Get results
        results = session.simulations.get(simulation_type)
        if not results:
            return {
                "status": "error",
                "message": f"No {simulation_type} simulation results for circuit {circuit_id}"
            }
        
        try:
            # Generate plot
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if simulation_type == "dc":
                # DC plot - bar chart
                if not signals:
                    # Default: plot all node voltages
                    signals = [f"V({node})" for node in results.nodes if node != 0]
                
                values = []
                labels = []
                
                for signal in signals:
                    if signal.startswith("V("):
                        node = signal[2:-1]
                        try:
                            node = int(node)
                        except ValueError:
                            pass
                        voltage = results.voltage(node)
                        if voltage is not None:
                            values.append(float(voltage[0]))
                            labels.append(signal)
                    elif signal.startswith("I("):
                        component = signal[2:-1]
                        current = results.current(component)
                        if current is not None:
                            values.append(float(current[0]) * 1000)  # Convert to mA
                            labels.append(signal)
                
                ax.bar(labels, values)
                ax.set_ylabel("Value (V or mA)")
                ax.set_title(f"DC Operating Point - {session.circuit.name}")
                ax.grid(True, alpha=0.3)
                
            elif simulation_type == "transient":
                # Transient plot - time series
                if not signals:
                    # Default: plot all node voltages
                    signals = [f"V({node})" for node in results.nodes if node != 0]
                
                if results.time is not None:
                    time_ms = results.time * 1000  # Convert to ms
                    
                    for signal in signals:
                        if signal.startswith("V("):
                            node = signal[2:-1]
                            try:
                                node = int(node)
                            except ValueError:
                                pass
                            voltage = results.voltage(node)
                            if voltage is not None:
                                ax.plot(time_ms, voltage, label=signal)
                        elif signal.startswith("I("):
                            component = signal[2:-1]
                            current = results.current(component)
                            if current is not None:
                                ax.plot(time_ms, current * 1000, label=f"{signal} (mA)")
                    
                    ax.set_xlabel("Time (ms)")
                    ax.set_ylabel("Voltage (V) / Current (mA)")
                    ax.set_title(f"Transient Analysis - {session.circuit.name}")
                    ax.legend()
                    ax.grid(True, alpha=0.3)
            
            # Save plot to bytes
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            plot_data = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close()
            
            return {
                "status": "success",
                "circuit_id": circuit_id,
                "simulation_type": simulation_type,
                "signals_plotted": signals,
                "plot": {
                    "format": "png",
                    "encoding": "base64",
                    "data": plot_data
                },
                "message": "Plot generated successfully. Display using base64 decoding."
            }
            
        except Exception as e:
            logger.error(f"Plot generation failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to generate plot: {str(e)}"
            }
    
    async def export_circuit(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Export circuit in various formats."""
        circuit_id = args.get("circuit_id")
        format_type = args.get("format", "json")
        
        # Get session
        session = self.server.get_session(circuit_id)
        if not session:
            return {
                "status": "error",
                "message": f"Circuit {circuit_id} not found"
            }
        
        circuit = session.circuit
        
        if format_type == "json":
            # Export as JSON
            components = []
            for comp in circuit.components:
                comp_dict = {
                    "type": comp.component_type,
                    "name": comp.name
                }
                
                # Add nodes
                if hasattr(comp, 'positive'):
                    comp_dict["positive"] = comp.positive
                    comp_dict["negative"] = comp.negative
                elif hasattr(comp, 'node1'):
                    comp_dict["node1"] = comp.node1
                    comp_dict["node2"] = comp.node2
                
                # Add value
                for attr in ['resistance', 'capacitance', 'inductance', 'dc_value', 'dc_current']:
                    if hasattr(comp, attr):
                        comp_dict["value"] = getattr(comp, attr)
                        break
                
                components.append(comp_dict)
            
            export_data = {
                "circuit_name": circuit.name,
                "components": components,
                "nodes": list(circuit.nodes)
            }
            
            return {
                "status": "success",
                "format": "json",
                "data": export_data
            }
        
        elif format_type == "netlist":
            # Export as SPICE netlist (basic)
            netlist_lines = [
                f"* {circuit.name}",
                f"* Generated by MCP Circuit Simulator",
                ""
            ]
            
            for comp in circuit.components:
                if comp.component_type == "resistor":
                    netlist_lines.append(
                        f"{comp.name} {comp.node1} {comp.node2} {comp.resistance}"
                    )
                elif comp.component_type == "capacitor":
                    netlist_lines.append(
                        f"{comp.name} {comp.positive} {comp.negative} {comp.capacitance}"
                    )
                elif comp.component_type == "inductor":
                    netlist_lines.append(
                        f"{comp.name} {comp.positive} {comp.negative} {comp.inductance}"
                    )
                elif comp.component_type == "voltage_source":
                    netlist_lines.append(
                        f"{comp.name} {comp.positive} {comp.negative} DC {comp.dc_value}"
                    )
                elif comp.component_type == "current_source":
                    netlist_lines.append(
                        f"{comp.name} {comp.positive} {comp.negative} DC {comp.dc_current}"
                    )
            
            netlist_lines.append(".end")
            
            return {
                "status": "success",
                "format": "netlist",
                "data": "\n".join(netlist_lines)
            }
        
        else:
            return {
                "status": "error",
                "message": f"Unknown export format: {format_type}",
                "supported_formats": ["json", "netlist"]
            }