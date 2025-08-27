"""
Circuit management tools for MCP server.
"""

import logging
from datetime import datetime
from typing import Any, Dict

logger = logging.getLogger(__name__)


class CircuitTools:
    """Handles circuit-related MCP tool calls."""

    def __init__(self, server):
        """
        Initialize circuit tools handler.

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
        # Remove 'circuit.' prefix
        action = tool_name.replace("circuit.", "")

        if action == "create":
            return await self.create_circuit(arguments)
        elif action == "add_component":
            return await self.add_component(arguments)
        elif action == "list":
            return await self.list_circuits(arguments)
        elif action == "get":
            return await self.get_circuit(arguments)
        elif action == "validate":
            return await self.validate_circuit(arguments)
        else:
            raise ValueError(f"Unknown circuit tool action: {action}")

    async def create_circuit(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new circuit."""
        name = args.get("name", "Untitled Circuit")
        description = args.get("description", "")

        circuit_id = self.server.create_circuit(name, description)

        return {
            "status": "success",
            "circuit_id": circuit_id,
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
        }

    async def add_component(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Add a component to a circuit."""
        circuit_id = args.get("circuit_id")
        component_type = args.get("type")
        name = args.get("name")
        value = args.get("value")
        positive = args.get("positive")
        negative = args.get("negative")

        # Get circuit
        circuit = self.server.get_circuit(circuit_id)
        if not circuit:
            return {"status": "error", "message": f"Circuit {circuit_id} not found"}

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
            session = self.server.get_session(circuit_id)
            if session:
                session.last_modified = datetime.now()

            return {
                "status": "success",
                "message": f"Added {component_type} {name} to circuit",
                "component": {
                    "type": component_type,
                    "name": name,
                    "value": value,
                    "nodes": {"positive": positive, "negative": negative},
                },
            }

        except Exception as e:
            return {"status": "error", "message": f"Failed to add component: {str(e)}"}

    async def list_circuits(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List all active circuits."""
        circuits = []

        for circuit_id, session in self.server.sessions.items():
            circuits.append(
                {
                    "circuit_id": circuit_id,
                    "name": session.circuit.name,
                    "components": len(session.circuit.components),
                    "nodes": len(session.circuit.nodes),
                    "created_at": session.created_at.isoformat(),
                    "last_modified": session.last_modified.isoformat(),
                    "simulations": list(session.simulations.keys()),
                }
            )

        return {"status": "success", "count": len(circuits), "circuits": circuits}

    async def get_circuit(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get details of a specific circuit."""
        circuit_id = args.get("circuit_id")

        session = self.server.get_session(circuit_id)
        if not session:
            return {"status": "error", "message": f"Circuit {circuit_id} not found"}

        circuit = session.circuit

        # Format components
        components = []
        for comp in circuit.components:
            comp_dict = {"type": comp.component_type, "name": comp.name, "nodes": []}

            # Extract node connections
            if hasattr(comp, "positive") and hasattr(comp, "negative"):
                comp_dict["nodes"] = {"positive": comp.positive, "negative": comp.negative}
            elif hasattr(comp, "node1") and hasattr(comp, "node2"):
                comp_dict["nodes"] = {"node1": comp.node1, "node2": comp.node2}

            # Add value if present
            for attr in ["resistance", "capacitance", "inductance", "dc_value", "dc_current"]:
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
                "last_modified": session.last_modified.isoformat(),
            },
        }

    async def validate_circuit(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Validate circuit connectivity and components using new validation system."""
        circuit_id = args.get("circuit_id")
        level = args.get("level", "standard")  # basic, standard, strict
        checks = args.get("checks", ["electrical", "basic"])  # list of check types

        circuit = self.server.get_circuit(circuit_id)
        if not circuit:
            return {"status": "error", "message": f"Circuit {circuit_id} not found"}

        # Import validation system
        try:
            from circuit_sim.validation import CircuitValidator, ShortCircuitDetector, BasicCircuitValidator
        except ImportError:
            # Fallback to old validation if new system not available
            return await self._legacy_validate_circuit(args)

        # Set up validator with requested checks
        validator = CircuitValidator()
        
        if "electrical" in checks:
            # Configure thresholds based on level
            if level == "strict":
                short_threshold = 0.0001  # 0.1mΩ
                warning_threshold = 0.01  # 10mΩ
            elif level == "standard":
                short_threshold = 0.001   # 1mΩ
                warning_threshold = 0.1   # 100mΩ
            else:  # basic
                short_threshold = 0.01    # 10mΩ
                warning_threshold = 1.0   # 1Ω
                
            validator.add_rule(ShortCircuitDetector(
                short_threshold=short_threshold,
                warning_threshold=warning_threshold
            ))
        
        if "basic" in checks:
            validator.add_rule(BasicCircuitValidator())

        # Run validation
        results = validator.validate(circuit)
        
        # Format results for MCP
        all_issues = []
        all_warnings = []
        all_suggestions = []
        
        overall_valid = True
        
        for rule_name, result in results.items():
            if not result.is_valid:
                overall_valid = False
                
            # Collect issues
            for issue in result.issues:
                all_issues.append({
                    "rule": rule_name,
                    "type": issue.type,
                    "severity": issue.severity.value,
                    "message": issue.message,
                    "components": issue.components,
                    "suggestion": issue.suggestion
                })
                
            # Collect warnings
            for warning in result.warnings:
                all_warnings.append({
                    "rule": rule_name,
                    "type": warning.type,
                    "severity": warning.severity.value,
                    "message": warning.message,
                    "components": warning.components,
                    "suggestion": warning.suggestion
                })
                
            # Collect suggestions
            all_suggestions.extend(result.suggestions)

        return {
            "status": "success",
            "valid": overall_valid,
            "level": level,
            "checks_run": checks,
            "issues": all_issues,
            "warnings": all_warnings,
            "suggestions": list(set(all_suggestions)),  # Remove duplicates
            "summary": {
                "components": len(circuit.components),
                "nodes": len(circuit.nodes),
                "has_ground": 0 in circuit.nodes,
                "has_source": any(comp.get('type') in ['voltage_source', 'current_source'] 
                                for comp in circuit.components),
                "rules_run": len(results),
                "rules_passed": sum(1 for r in results.values() if r.is_valid),
                "total_issues": len(all_issues),
                "total_warnings": len(all_warnings)
            },
        }

    async def _legacy_validate_circuit(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy validation method as fallback."""
        circuit_id = args.get("circuit_id")
        circuit = self.server.get_circuit(circuit_id)
        
        issues = []
        warnings = []

        # Check if circuit has components
        if not circuit.components:
            issues.append("Circuit has no components")

        # Check if circuit has at least one source
        has_source = any(
            comp.get('type') in ["voltage_source", "current_source"]
            for comp in circuit.components
        )
        if not has_source:
            issues.append("Circuit has no voltage or current sources")

        # Check for ground connection (node 0)
        if 0 not in circuit.nodes:
            warnings.append("Circuit has no explicit ground (node 0)")

        # Check for floating nodes (nodes with only one connection)
        node_connections = {}
        for comp in circuit.components:
            # Count connections for each node
            for node_key in ['positive', 'negative', 'node1', 'node2']:
                if node_key in comp:
                    node = comp[node_key]
                    node_connections[node] = node_connections.get(node, 0) + 1

        for node, count in node_connections.items():
            if count == 1 and node != 0:
                warnings.append(f"Node {node} has only one connection (might be floating)")

        # Check for duplicate component names
        component_names = [comp.get('name', 'unnamed') for comp in circuit.components]
        if len(component_names) != len(set(component_names)):
            duplicates = [name for name in component_names if component_names.count(name) > 1]
            issues.append(f"Duplicate component names: {set(duplicates)}")

        valid = len(issues) == 0

        return {
            "status": "success",
            "valid": valid,
            "level": "basic",
            "issues": [{"message": issue, "type": "basic_validation"} for issue in issues],
            "warnings": [{"message": warning, "type": "basic_validation"} for warning in warnings],
            "suggestions": [],
            "summary": {
                "components": len(circuit.components),
                "nodes": len(circuit.nodes),
                "has_ground": 0 in circuit.nodes,
                "has_source": has_source,
            },
        }
