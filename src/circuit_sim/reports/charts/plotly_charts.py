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
            for node in results.nodes:
                if node != 0:
                    voltage = results.voltage(node)
                    if voltage is not None and np.iscomplexobj(voltage):
                        magnitude_db = 20 * np.log10(np.abs(voltage))
                        phase_deg = np.angle(voltage, deg=True)

                        fig = make_subplots(
                            rows=2,
                            cols=1,
                            subplot_titles=(
                                f"Magnitude - V(Node {node})",
                                f"Phase - V(Node {node})",
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
                                "text": f"Bode Plot - V(Node {node})",
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
                        magnitude_db = 20 * np.log10(np.abs(voltage))

                        fig.add_trace(
                            go.Scatter(
                                x=results.frequency,
                                y=magnitude_db,
                                mode="lines",
                                name=f"V(Node {node})",
                                line=dict(
                                    color=self.color_palette[color_idx % len(self.color_palette)],
                                    width=2,
                                ),
                                hovertemplate="Freq: %{x:.2e}Hz<br>Magnitude: %{y:.2f}dB<extra></extra>",
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
                            magnitude_db = 20 * np.log10(np.abs(voltage))
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
