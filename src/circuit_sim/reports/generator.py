"""
Main report generator class for circuit analysis reports.

This module provides the ReportGenerator class that creates professional
circuit analysis reports with interactive visualizations and multiple export formats.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape

from circuit_sim.circuit import Circuit
from circuit_sim.simulator.results import SimulationResults
from .charts.plotly_charts import PlotlyChartGenerator
from .utils.formatting import format_value, format_units, format_time_duration
from .utils.metrics import MetricsCalculator


class ReportGenerator:
    """Generate professional circuit analysis reports with interactive visualizations."""

    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize the report generator.

        Args:
            template_dir: Custom template directory path. If None, uses default templates.
        """
        if template_dir is None:
            template_dir = os.path.join(os.path.dirname(__file__), "templates")
        
        self.template_dir = Path(template_dir)
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )
        
        self.chart_generator = PlotlyChartGenerator()
        self.metrics_calculator = MetricsCalculator()
        
        # Add custom filters to Jinja2
        self.env.filters["format_value"] = format_value
        self.env.filters["format_units"] = format_units
        self.env.filters["format_time_duration"] = format_time_duration

    def generate_report(
        self,
        circuit: Circuit,
        results: SimulationResults,
        report_type: str = "detailed",
        output_format: str = "html",
        output_path: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate a comprehensive circuit analysis report.

        Args:
            circuit: Circuit object containing circuit definition
            results: SimulationResults object with analysis data
            report_type: Type of report ('quick', 'detailed', 'executive', 'comparison')
            output_format: Output format ('html', 'pdf', 'markdown', 'notebook')
            output_path: Custom output file path (optional)
            **kwargs: Additional report configuration options

        Returns:
            Path to the generated report file

        Raises:
            ValueError: If report_type or output_format is not supported
            FileNotFoundError: If template files are missing
        """
        # Validate inputs
        valid_types = ["quick", "detailed", "executive"]
        if report_type not in valid_types:
            raise ValueError(f"report_type must be one of {valid_types}")

        valid_formats = ["html"]  # Start with HTML only, expand later
        if output_format not in valid_formats:
            raise ValueError(f"output_format must be one of {valid_formats}")

        # Generate report data
        report_data = self._prepare_report_data(circuit, results, report_type, **kwargs)

        # Determine output path
        if output_path is None:
            output_path = self._generate_output_path(circuit.name, report_type, output_format)

        # Generate report based on format
        if output_format == "html":
            return self._generate_html(report_data, report_type, output_path)

    def _prepare_report_data(
        self, circuit: Circuit, results: SimulationResults, report_type: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Prepare all data needed for report generation.

        Args:
            circuit: Circuit object
            results: Simulation results
            report_type: Type of report being generated
            **kwargs: Additional options

        Returns:
            Dictionary containing all report data
        """
        # Circuit metadata
        metadata = {
            "circuit_name": circuit.name,
            "description": kwargs.get("description", f"Circuit analysis report for {circuit.name}"),
            "component_count": len(circuit.components),
            "node_count": len(circuit.nodes),
            "analysis_type": results.analysis_type,
            "generated_at": datetime.now(),
            "report_type": report_type,
            "version": "1.0.0",
        }

        # Circuit analysis
        circuit_analysis = self._analyze_circuit(circuit)

        # Process simulation results
        processed_results = self._process_results(results)

        # Generate charts
        charts = self.chart_generator.create_charts(results, circuit)

        # Calculate metrics
        metrics = self.metrics_calculator.calculate_metrics(results, circuit)

        # Generate summary
        summary = self._generate_summary(results, metrics, circuit)

        return {
            "metadata": metadata,
            "circuit": circuit_analysis,
            "results": processed_results,
            "charts": charts,
            "metrics": metrics,
            "summary": summary,
            "raw_circuit": circuit,
            "raw_results": results,
        }

    def _analyze_circuit(self, circuit: Circuit) -> Dict[str, Any]:
        """
        Analyze circuit structure and components.

        Args:
            circuit: Circuit object to analyze

        Returns:
            Dictionary with circuit analysis data
        """
        # Component breakdown by type
        component_types = {}
        for component in circuit.components:
            comp_type = component["type"]
            if comp_type not in component_types:
                component_types[comp_type] = 0
            component_types[comp_type] += 1

        # Create component table data
        component_table = []
        for component in circuit.components:
            row = {
                "name": component["name"],
                "type": component["type"].replace("_", " ").title(),
                "value": self._get_component_value(component),
                "nodes": self._get_component_nodes(component),
            }
            component_table.append(row)

        return {
            "components": component_table,
            "component_types": component_types,
            "total_components": len(circuit.components),
            "total_nodes": len(circuit.nodes),
            "nodes_list": sorted([n for n in circuit.nodes if n != 0]),  # Exclude ground
        }

    def _get_component_value(self, component: Dict[str, Any]) -> str:
        """Extract the main value from a component."""
        if "resistance" in component:
            return component["resistance"]
        elif "capacitance" in component:
            return component["capacitance"]
        elif "inductance" in component:
            return component["inductance"]
        elif "dc_value" in component:
            return component["dc_value"]
        return "N/A"

    def _get_component_nodes(self, component: Dict[str, Any]) -> str:
        """Extract node connections from a component."""
        if "node1" in component and "node2" in component:
            return f"{component['node1']} - {component['node2']}"
        elif "positive" in component and "negative" in component:
            return f"{component['positive']} - {component['negative']}"
        return "N/A"

    def _process_results(self, results: SimulationResults) -> Dict[str, Any]:
        """
        Process simulation results for report display.

        Args:
            results: Raw simulation results

        Returns:
            Processed results dictionary
        """
        processed = {
            "analysis_type": results.analysis_type,
            "execution_time": getattr(results, "execution_time", "N/A"),
        }

        if results.analysis_type == "dc":
            # DC operating points
            dc_data = []
            for node in results.nodes:
                voltage = results.voltage(node)
                if voltage is not None:
                    dc_data.append({
                        "node": f"Node {node}" if node != 0 else "Ground",
                        "voltage": voltage[0] if len(voltage) > 0 else 0.0,
                    })
            processed["dc_operating_points"] = dc_data

        elif results.analysis_type == "transient":
            # Transient analysis summary
            if results.time is not None:
                processed["time_range"] = {
                    "start": float(results.time[0]),
                    "stop": float(results.time[-1]),
                    "points": len(results.time),
                }

        elif results.analysis_type == "ac":
            # AC analysis summary
            if results.frequency is not None:
                processed["frequency_range"] = {
                    "start": float(results.frequency[0]),
                    "stop": float(results.frequency[-1]),
                    "points": len(results.frequency),
                }

        return processed

    def _generate_summary(
        self, results: SimulationResults, metrics: Dict[str, Any], circuit: Circuit
    ) -> Dict[str, Any]:
        """
        Generate executive summary of the analysis.

        Args:
            results: Simulation results
            metrics: Calculated metrics
            circuit: Circuit definition

        Returns:
            Summary dictionary
        """
        summary_text = self._create_summary_text(results, metrics, circuit)
        
        return {
            "text": summary_text,
            "key_findings": self._extract_key_findings(results, metrics),
            "recommendations": self._generate_recommendations(results, metrics, circuit),
        }

    def _create_summary_text(
        self, results: SimulationResults, metrics: Dict[str, Any], circuit: Circuit
    ) -> str:
        """Create human-readable summary text."""
        analysis_type = results.analysis_type.upper()
        component_count = len(circuit.components)
        node_count = len(circuit.nodes)
        
        text = f"This {analysis_type} analysis was performed on a {component_count}-component "
        text += f"circuit with {node_count} nodes. "
        
        if results.analysis_type == "dc":
            text += "The DC operating point analysis shows the steady-state voltages at all circuit nodes."
        elif results.analysis_type == "transient":
            text += "The transient analysis reveals the circuit's time-domain behavior and response characteristics."
        elif results.analysis_type == "ac":
            text += "The AC frequency analysis demonstrates the circuit's frequency response and filtering characteristics."
        
        return text

    def _extract_key_findings(self, results: SimulationResults, metrics: Dict[str, Any]) -> List[str]:
        """Extract key findings from the analysis."""
        findings = []
        
        if results.analysis_type == "dc" and metrics:
            if "power_dissipation" in metrics:
                findings.append(f"Total power dissipation: {format_value(metrics['power_dissipation'], 'W')}")
            if "efficiency" in metrics:
                findings.append(f"Circuit efficiency: {metrics['efficiency']:.1%}")
        
        elif results.analysis_type == "transient" and metrics:
            if "rise_time" in metrics:
                findings.append(f"Rise time: {format_value(metrics['rise_time'], 's')}")
            if "settling_time" in metrics:
                findings.append(f"Settling time: {format_value(metrics['settling_time'], 's')}")
        
        elif results.analysis_type == "ac" and metrics:
            if "bandwidth" in metrics:
                findings.append(f"Bandwidth: {format_value(metrics['bandwidth'], 'Hz')}")
            if "gain" in metrics:
                findings.append(f"Maximum gain: {metrics['gain']:.2f} dB")
        
        if not findings:
            findings.append("Analysis completed successfully with nominal results.")
        
        return findings

    def _generate_recommendations(
        self, results: SimulationResults, metrics: Dict[str, Any], circuit: Circuit
    ) -> List[str]:
        """Generate engineering recommendations based on results."""
        recommendations = []
        
        # Generic recommendations based on circuit complexity
        if len(circuit.components) > 20:
            recommendations.append("Consider circuit optimization to reduce component count.")
        
        if results.analysis_type == "transient":
            recommendations.append("Verify transient response meets timing requirements.")
            recommendations.append("Consider adding damping if overshoot is excessive.")
        
        elif results.analysis_type == "ac":
            recommendations.append("Validate frequency response against specifications.")
            recommendations.append("Check phase margin for stability requirements.")
        
        if not recommendations:
            recommendations.append("Circuit analysis shows nominal performance.")
        
        return recommendations

    def _generate_output_path(self, circuit_name: str, report_type: str, output_format: str) -> str:
        """Generate default output file path."""
        # Create reports directory if it doesn't exist
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        # Clean circuit name for filename
        safe_name = "".join(c for c in circuit_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_')
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_name}_{report_type}_{timestamp}.{output_format}"
        
        return str(reports_dir / filename)

    def _generate_html(self, data: Dict[str, Any], report_type: str, output_path: str) -> str:
        """Generate HTML report."""
        from .builders.html_builder import HTMLBuilder
        builder = HTMLBuilder(self.env)
        return builder.build(data, report_type, output_path)