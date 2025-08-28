"""
Power analysis tools for MCP server.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class PowerTools:
    """Handles power analysis MCP tool calls."""

    def __init__(self, server):
        """
        Initialize power analysis tools.

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
        # Remove 'power.' prefix
        action = tool_name.replace("power.", "")

        if action == "analyze":
            return await self.analyze_power(arguments)
        elif action == "validate_ratings":
            return await self.validate_power_ratings(arguments)
        else:
            raise ValueError(f"Unknown power tool action: {action}")

    async def analyze_power(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze power dissipation in a simulated circuit."""
        circuit_id = args.get("circuit_id")
        simulation_type = args.get("simulation_type", "dc")
        component_ratings = args.get("component_ratings", {})
        thresholds = args.get("thresholds", {})

        # Get circuit and session
        circuit = self.server.get_circuit(circuit_id)
        if not circuit:
            return {"status": "error", "message": f"Circuit {circuit_id} not found"}

        session = self.server.get_session(circuit_id)
        if not session:
            return {"status": "error", "message": f"Session {circuit_id} not found"}

        # Get simulation results
        results = session.simulations.get(simulation_type)
        if not results:
            return {
                "status": "error",
                "message": f"No {simulation_type} simulation results for circuit {circuit_id}. Run simulation first.",
            }

        try:
            # Import power analyzer
            from circuit_sim.validation import PowerAnalyzer

            # Configure analyzer with custom thresholds
            analyzer = PowerAnalyzer(
                power_warning_threshold=thresholds.get("warning", 1.0),
                power_error_threshold=thresholds.get("error", 10.0),
            )

            # Perform power analysis
            power_analysis = analyzer.analyze_power(circuit, results, component_ratings)

            # Format results for MCP response
            return self._format_power_analysis_response(circuit_id, power_analysis)

        except ImportError:
            return {
                "status": "error",
                "message": "Power analysis requires validation module",
            }
        except Exception as e:
            logger.error(f"Power analysis failed: {e}")
            return {"status": "error", "message": f"Power analysis failed: {str(e)}"}

    async def validate_power_ratings(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Validate component power ratings against actual power dissipation."""
        circuit_id = args.get("circuit_id")
        component_ratings = args.get("component_ratings", {})

        if not component_ratings:
            return {"status": "error", "message": "No component ratings provided"}

        # Use the analyze_power method with ratings
        analysis_args = {
            "circuit_id": circuit_id,
            "component_ratings": component_ratings,
        }

        result = await self.analyze_power(analysis_args)

        if result["status"] == "success":
            # Focus on rating-related issues
            rating_issues = [
                issue
                for issue in result.get("issues", [])
                if issue.get("type") == "power_rating_exceeded"
            ]

            return {
                "status": "success",
                "circuit_id": circuit_id,
                "rating_validation": {
                    "valid": len(rating_issues) == 0,
                    "violations": rating_issues,
                    "component_count": len(component_ratings),
                    "components_checked": list(component_ratings.keys()),
                },
            }
        else:
            return result

    def _format_power_analysis_response(
        self, circuit_id: str, analysis
    ) -> Dict[str, Any]:
        """Format power analysis result for MCP response."""
        # Format component power information
        component_power = {}
        for name, info in analysis.component_power.items():
            component_power[name] = {
                "power": info.power,
                "voltage": info.voltage,
                "current": info.current,
                "method": info.method,
                "type": info.component_type,
                "rating": info.rating,
                "utilization": (
                    (info.power / info.rating * 100) if info.rating else None
                ),
            }

        # Format source power information
        source_power = {}
        for name, info in analysis.source_power.items():
            source_power[name] = {
                "power": info.power,
                "voltage": info.voltage,
                "current": info.current,
                "method": info.method,
                "type": info.component_type,
                "supplying": info.power < 0,
            }

        # Format issues and warnings
        issues = []
        for issue in analysis.issues:
            issues.append(
                {
                    "type": issue.type,
                    "severity": issue.severity.value,
                    "message": issue.message,
                    "components": issue.components,
                    "suggestion": issue.suggestion,
                }
            )

        warnings = []
        for warning in analysis.warnings:
            warnings.append(
                {
                    "type": warning.type,
                    "severity": warning.severity.value,
                    "message": warning.message,
                    "components": warning.components,
                    "suggestion": warning.suggestion,
                }
            )

        return {
            "status": "success",
            "circuit_id": circuit_id,
            "analysis_type": analysis.metadata.get("analysis_type", "unknown"),
            "valid": analysis.is_valid,
            "power_analysis": {
                "component_power": component_power,
                "source_power": source_power,
                "power_budget": {
                    "total_supplied": analysis.power_budget["total_supplied"],
                    "total_dissipated": analysis.power_budget["total_dissipated"],
                    "efficiency": analysis.power_budget["efficiency"]
                    * 100,  # Convert to percentage
                    "balance": analysis.power_budget["balance"],
                },
                "summary": {
                    "total_components": len(component_power),
                    "total_sources": len(source_power),
                    "max_component_power": max(
                        [info.power for info in analysis.component_power.values()],
                        default=0,
                    ),
                    "total_dissipated": analysis.total_power,
                },
            },
            "issues": issues,
            "warnings": warnings,
            "suggestions": (
                [
                    "Monitor high-power components for thermal management",
                    "Consider power ratings when selecting components",
                    "Verify power supply capacity meets circuit requirements",
                ]
                if analysis.total_power > 1.0
                else []
            ),
        }
