"""
Plotly chart generation for circuit analysis reports.

This module provides interactive chart generation using Plotly for
circuit simulation results including DC, transient, and AC analysis.
"""

from typing import Dict, List

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from circuit_sim.circuit import Circuit
from circuit_sim.simulator.results import SimulationResults


class PlotlyChartGenerator:
    """Generate interactive Plotly charts for circuit analysis."""

    def __init__(self):
        """Initialize the chart generator."""
        self.color_palette = [
            "#1f77b4",
            "#ff7f0e",
            "#2ca02c",
            "#d62728",
            "#9467bd",
            "#8c564b",
            "#e377c2",
            "#7f7f7f",
            "#bcbd22",
            "#17becf",
        ]

    def create_charts(self, results: SimulationResults, circuit: Circuit) -> Dict[str, go.Figure]:
        """
        Create all relevant charts based on analysis type.

        Args:
            results: Simulation results
            circuit: Circuit definition

        Returns:
            Dictionary mapping chart names to Plotly figures
        """
        charts = {}

        if results.analysis_type == "dc":
            charts.update(self._create_dc_charts(results, circuit))
        elif results.analysis_type == "transient":
            charts.update(self._create_transient_charts(results, circuit))
        elif results.analysis_type == "ac":
            charts.update(self._create_ac_charts(results, circuit))

        return charts

    def _create_dc_charts(
        self, results: SimulationResults, circuit: Circuit
    ) -> Dict[str, go.Figure]:
        """Create charts for DC analysis."""
        charts = {}

        # DC Operating Points Bar Chart
        if results.nodes:
            node_names = []
            voltages = []

            for node in results.nodes:
                if node != 0:  # Skip ground
                    voltage = results.voltage(node)
                    if voltage is not None and len(voltage) > 0:
                        node_names.append(f"Node {node}")
                        voltages.append(float(voltage[0]))

            if node_names:
                fig = go.Figure()
                fig.add_trace(
                    go.Bar(
                        x=node_names,
                        y=voltages,
                        text=[f"{v:.3f}V" for v in voltages],
                        textposition="auto",
                        marker_color="#1f77b4",
                        name="Node Voltages",
                    )
                )

                fig.update_layout(
                    title={"text": "DC Operating Points", "x": 0.5, "xanchor": "center"},
                    xaxis_title="Node",
                    yaxis_title="Voltage (V)",
                    showlegend=False,
                    template="plotly_white",
                    height=400,
                )

                charts["dc_voltages"] = fig

        # Component Current Chart (if available)
        if results.components:
            component_names = []
            currents = []

            for component in results.components:
                current = results.current(component)
                if current is not None and len(current) > 0:
                    component_names.append(component)
                    currents.append(float(current[0]))

            if component_names:
                fig = go.Figure()
                fig.add_trace(
                    go.Bar(
                        x=component_names,
                        y=currents,
                        text=[f"{abs(c):.3f}A" for c in currents],
                        textposition="auto",
                        marker_color="#ff7f0e",
                        name="Component Currents",
                    )
                )

                fig.update_layout(
                    title={"text": "Component Currents", "x": 0.5, "xanchor": "center"},
                    xaxis_title="Component",
                    yaxis_title="Current (A)",
                    showlegend=False,
                    template="plotly_white",
                    height=400,
                )

                charts["dc_currents"] = fig

        return charts

    def _get_node_label(self, node: int, circuit: Circuit) -> str:
        """Generate descriptive label for a node based on circuit topology"""
        
        # Check if this node is connected to voltage source (input)
        for component in circuit.components:
            if component.get("type") == "voltage_source":
                if component.get("positive") == node:
                    vs_name = component.get("name", "V1")
                    return f"Circuit Input - V(Node {node}) [{vs_name}+]"
        
        # Check if this node is a filter output (before capacitor to ground)
        for component in circuit.components:
            if component.get("type") == "capacitor":
                node1 = component.get("node1")
                node2 = component.get("node2")
                cap_name = component.get("name", "C")
                
                if node2 in [0, "gnd"] and node1 == node:
                    return f"Filter Output - V(Node {node}) [Before {cap_name}]"
        
        # Check if this node is between resistors (voltage divider output)
        resistor_connections = []
        for component in circuit.components:
            if component.get("type") == "resistor":
                resistor_connections.extend([component.get("node1"), component.get("node2")])
        
        resistor_count = resistor_connections.count(node)
        if resistor_count >= 2:  # Node connects to multiple resistors
            return f"Divider Output - V(Node {node}) [Between Resistors]"
        
        # Default descriptive label
        return f"Circuit Node {node}"

    def _create_transient_charts(
        self, results: SimulationResults, circuit: Circuit
    ) -> Dict[str, go.Figure]:
        """Create charts for transient analysis."""
        charts = {}

        if results.time is None:
            return charts

        # Voltage vs Time Chart
        if results.nodes:
            fig = go.Figure()

            color_idx = 0
            for node in results.nodes:
                if node != 0:  # Skip ground
                    voltage = results.voltage(node)
                    if voltage is not None:
                        fig.add_trace(
                            go.Scatter(
                                x=results.time,
                                y=voltage,
                                mode="lines",
                                name=f"V(Node {node})",
                                line=dict(
                                    color=self.color_palette[color_idx % len(self.color_palette)],
                                    width=2,
                                ),
                                hovertemplate="Time: %{x:.3e}s<br>Voltage: %{y:.3f}V<extra></extra>",
                            )
                        )
                        color_idx += 1

            fig.update_layout(
                title={"text": "Node Voltages vs Time", "x": 0.5, "xanchor": "center"},
                xaxis_title="Time (s)",
                yaxis_title="Voltage (V)",
                template="plotly_white",
                height=500,
                legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
            )

            charts["transient_voltages"] = fig

        # Current vs Time Chart (if available)
        if results.components:
            fig = go.Figure()

            color_idx = 0
            for component in results.components:
                current = results.current(component)
                if current is not None:
                    fig.add_trace(
                        go.Scatter(
                            x=results.time,
                            y=current,
                            mode="lines",
                            name=f"I({component})",
                            line=dict(
                                color=self.color_palette[color_idx % len(self.color_palette)],
                                width=2,
                            ),
                            hovertemplate="Time: %{x:.3e}s<br>Current: %{y:.3f}A<extra></extra>",
                        )
                    )
                    color_idx += 1

            if fig.data:  # Only create chart if we have data
                fig.update_layout(
                    title={"text": "Component Currents vs Time", "x": 0.5, "xanchor": "center"},
                    xaxis_title="Time (s)",
                    yaxis_title="Current (A)",
                    template="plotly_white",
                    height=500,
                    legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
                )

                charts["transient_currents"] = fig

        # Combined Voltage and Current Chart
        if results.nodes or results.components:
            fig = make_subplots(
                rows=2,
                cols=1,
                subplot_titles=("Node Voltages", "Component Currents"),
                shared_xaxes=True,
                vertical_spacing=0.1,
            )

            # Add voltage traces
            color_idx = 0
            for node in results.nodes:
                if node != 0:
                    voltage = results.voltage(node)
                    if voltage is not None:
                        fig.add_trace(
                            go.Scatter(
                                x=results.time,
                                y=voltage,
                                mode="lines",
                                name=f"V(Node {node})",
                                line=dict(
                                    color=self.color_palette[color_idx % len(self.color_palette)],
                                    width=2,
                                ),
                                hovertemplate="Time: %{x:.3e}s<br>Voltage: %{y:.3f}V<extra></extra>",
                            ),
                            row=1,
                            col=1,
                        )
                        color_idx += 1

            # Add current traces
            for component in results.components:
                current = results.current(component)
                if current is not None:
                    fig.add_trace(
                        go.Scatter(
                            x=results.time,
                            y=current,
                            mode="lines",
                            name=f"I({component})",
                            line=dict(
                                color=self.color_palette[color_idx % len(self.color_palette)],
                                width=2,
                            ),
                            hovertemplate="Time: %{x:.3e}s<br>Current: %{y:.3f}A<extra></extra>",
                        ),
                        row=2,
                        col=1,
                    )
                    color_idx += 1

            fig.update_xaxes(title_text="Time (s)", row=2, col=1)
            fig.update_yaxes(title_text="Voltage (V)", row=1, col=1)
            fig.update_yaxes(title_text="Current (A)", row=2, col=1)

            fig.update_layout(
                height=800,
                template="plotly_white",
                title={"text": "Transient Analysis - Complete View", "x": 0.5, "xanchor": "center"},
            )

            charts["transient_combined"] = fig

        return charts

    def _create_ac_charts(
        self, results: SimulationResults, circuit: Circuit
    ) -> Dict[str, go.Figure]:
        """Create charts for AC frequency analysis."""
        charts = {}

        if results.frequency is None:
            return charts

        # Bode Plot (Magnitude and Phase)
        if results.nodes:
            # Find nodes with interesting frequency response (not flat)
            interesting_nodes = []
            
            for node in results.nodes:
                if node != 0:
                    voltage = results.voltage(node)
                    if voltage is not None and np.iscomplexobj(voltage):
                        magnitude = np.abs(voltage)
                        # Check if node has significant frequency variation
                        mag_variation = magnitude.max() - magnitude.min()
                        
                        if mag_variation > 0.01:  # More than 1% variation
                            interesting_nodes.append(node)
            
            # If no interesting nodes, show all (fallback)
            nodes_to_plot = interesting_nodes if interesting_nodes else [n for n in results.nodes if n != 0]
            
            # Prioritize higher-numbered nodes (usually outputs) if we have multiple
            nodes_to_plot = sorted(nodes_to_plot, reverse=True)[:2]  # Max 2 nodes to avoid clutter
            
            for node in nodes_to_plot:
                voltage = results.voltage(node)
                if voltage is not None and np.iscomplexobj(voltage):
                        # Calculate magnitude and phase with proper handling of small values
                        magnitude_linear = np.abs(voltage)
                        
                        # Avoid log of zero by setting minimum value
                        magnitude_linear_safe = np.maximum(magnitude_linear, 1e-12)
                        magnitude_db = 20 * np.log10(magnitude_linear_safe)
                        phase_deg = np.angle(voltage, deg=True)

                        # Determine node role for better labeling
                        node_label = self._get_node_label(node, circuit)
                        
                        fig = make_subplots(
                            rows=2,
                            cols=1,
                            subplot_titles=(
                                f"Magnitude - {node_label}",
                                f"Phase - {node_label}",
                            ),
                            shared_xaxes=True,
                            vertical_spacing=0.1,
                        )

                        # Magnitude plot
                        fig.add_trace(
                            go.Scatter(
                                x=results.frequency,
                                y=magnitude_db,
                                mode="lines",
                                name="Magnitude",
                                line=dict(color="#1f77b4", width=2),
                                hovertemplate="Freq: %{x:.2e}Hz<br>Magnitude: %{y:.2f}dB<extra></extra>",
                            ),
                            row=1,
                            col=1,
                        )

                        # Phase plot
                        fig.add_trace(
                            go.Scatter(
                                x=results.frequency,
                                y=phase_deg,
                                mode="lines",
                                name="Phase",
                                line=dict(color="#ff7f0e", width=2),
                                hovertemplate="Freq: %{x:.2e}Hz<br>Phase: %{y:.2f}°<extra></extra>",
                            ),
                            row=2,
                            col=1,
                        )

                        fig.update_xaxes(type="log", title_text="Frequency (Hz)", row=2, col=1)
                        fig.update_yaxes(title_text="Magnitude (dB)", row=1, col=1)
                        fig.update_yaxes(title_text="Phase (°)", row=2, col=1)

                        fig.update_layout(
                            height=600,
                            template="plotly_white",
                            title={
                                "text": f"Bode Plot - {node_label}",
                                "x": 0.5,
                                "xanchor": "center",
                            },
                            showlegend=False,
                        )

                        charts[f"bode_node_{node}"] = fig

        # Frequency Response Overview
        if results.nodes and len([n for n in results.nodes if n != 0]) > 1:
            fig = go.Figure()

            color_idx = 0
            for node in results.nodes:
                if node != 0:
                    voltage = results.voltage(node)
                    if voltage is not None and np.iscomplexobj(voltage):
                        # Safe magnitude calculation
                        magnitude_linear = np.abs(voltage)
                        magnitude_linear_safe = np.maximum(magnitude_linear, 1e-12)
                        magnitude_db = 20 * np.log10(magnitude_linear_safe)

                        # Get descriptive node label
                        node_description = self._get_node_label(node, circuit).replace(f" - V(Node {node})", "")
                        
                        fig.add_trace(
                            go.Scatter(
                                x=results.frequency,
                                y=magnitude_db,
                                mode="lines",
                                name=node_description,
                                line=dict(
                                    color=self.color_palette[color_idx % len(self.color_palette)],
                                    width=2,
                                ),
                                hovertemplate=f"Freq: %{{x:.2e}}Hz<br>Magnitude: %{{y:.2f}}dB<br>Node: {node_description}<extra></extra>",
                            )
                        )
                        color_idx += 1

            fig.update_layout(
                title={"text": "Frequency Response - All Nodes", "x": 0.5, "xanchor": "center"},
                xaxis_title="Frequency (Hz)",
                yaxis_title="Magnitude (dB)",
                xaxis_type="log",
                template="plotly_white",
                height=500,
                legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
            )

            charts["frequency_response"] = fig

        return charts

    def create_comparison_chart(
        self, results_list: List[SimulationResults], labels: List[str]
    ) -> go.Figure:
        """
        Create comparison chart for multiple simulation results.

        Args:
            results_list: List of simulation results to compare
            labels: Labels for each result set

        Returns:
            Plotly figure with comparison visualization
        """
        if not results_list or len(results_list) != len(labels):
            raise ValueError("results_list and labels must have same length")

        analysis_type = results_list[0].analysis_type

        fig = go.Figure()

        for i, (results, label) in enumerate(zip(results_list, labels, strict=False)):
            if results.analysis_type != analysis_type:
                continue

            color = self.color_palette[i % len(self.color_palette)]

            if analysis_type == "transient" and results.time is not None:
                # Compare first voltage node
                for node in results.nodes:
                    if node != 0:
                        voltage = results.voltage(node)
                        if voltage is not None:
                            fig.add_trace(
                                go.Scatter(
                                    x=results.time,
                                    y=voltage,
                                    mode="lines",
                                    name=f"{label} - V(Node {node})",
                                    line=dict(color=color, width=2),
                                    hovertemplate="Time: %{x:.3e}s<br>Voltage: %{y:.3f}V<extra></extra>",
                                )
                            )
                        break  # Only first node for comparison

            elif analysis_type == "ac" and results.frequency is not None:
                # Compare magnitude response
                for node in results.nodes:
                    if node != 0:
                        voltage = results.voltage(node)
                        if voltage is not None and np.iscomplexobj(voltage):
                            # Safe magnitude calculation
                            magnitude_linear = np.abs(voltage)
                            magnitude_linear_safe = np.maximum(magnitude_linear, 1e-12)
                            magnitude_db = 20 * np.log10(magnitude_linear_safe)
                            fig.add_trace(
                                go.Scatter(
                                    x=results.frequency,
                                    y=magnitude_db,
                                    mode="lines",
                                    name=f"{label} - V(Node {node})",
                                    line=dict(color=color, width=2),
                                    hovertemplate="Freq: %{x:.2e}Hz<br>Magnitude: %{y:.2f}dB<extra></extra>",
                                )
                            )
                        break  # Only first node for comparison

        # Update layout based on analysis type
        if analysis_type == "transient":
            fig.update_layout(
                title="Transient Response Comparison",
                xaxis_title="Time (s)",
                yaxis_title="Voltage (V)",
            )
        elif analysis_type == "ac":
            fig.update_layout(
                title="Frequency Response Comparison",
                xaxis_title="Frequency (Hz)",
                yaxis_title="Magnitude (dB)",
                xaxis_type="log",
            )

        fig.update_layout(
            template="plotly_white",
            height=500,
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
        )

        return fig
