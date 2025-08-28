"""Report generation for voltage divider circuit."""

from pathlib import Path
from typing import Any, Dict, List

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .circuit import VoltageDividerCircuit


class VoltageDividerReport:
    """Interactive report for voltage divider analysis."""

    def __init__(self, title: str = "Voltage Divider Analysis"):
        """Initialize report.

        Args:
            title: Report title
        """
        self.title = title
        self.figures: List[go.Figure] = []
        self.text_sections: List[str] = []

    def add_figure(self, figure: go.Figure):
        """Add a plotly figure to the report."""
        self.figures.append(figure)

    def add_text(self, text: str):
        """Add a text section to the report."""
        self.text_sections.append(text)

    def save(self, filepath: Path):
        """Save report to HTML file.

        Args:
            filepath: Path to save the HTML report
        """
        html_content = f"<html><head><title>{self.title}</title></head><body>"
        html_content += f"<h1>{self.title}</h1>"

        for text in self.text_sections:
            html_content += f"<p>{text}</p>"

        for fig in self.figures:
            html_content += fig.to_html(include_plotlyjs="cdn")

        html_content += "</body></html>"
        filepath.write_text(html_content)


def generate_report(
    circuit: VoltageDividerCircuit,
    results: Dict[str, Any],
    include_sweep: bool = False,
    include_tolerance: bool = False,
) -> VoltageDividerReport:
    """Generate interactive report for voltage divider.

    Args:
        circuit: Voltage divider circuit
        results: Simulation results
        include_sweep: Include parameter sweep plots
        include_tolerance: Include tolerance analysis

    Returns:
        VoltageDividerReport instance
    """
    report = VoltageDividerReport()

    # Add circuit description
    report.add_text(
        f"""
    <h2>Circuit Configuration</h2>
    <ul>
        <li>R1: {circuit.r1} Ω</li>
        <li>R2: {circuit.r2} Ω</li>
        <li>Input Voltage: {circuit.vin} V</li>
        <li>Theoretical Output: {circuit.calculate_theoretical_output():.3f} V</li>
    </ul>
    """
    )

    # Create main analysis figure
    if "output_voltage" in results:
        fig = _create_dc_analysis_plot(circuit, results)
        report.add_figure(fig)

    # Add sweep plot if available
    if include_sweep and "sweep_values" in results:
        fig = _create_sweep_plot(results)
        report.add_figure(fig)

    # Add power dissipation plot
    if "power_dissipation" in results:
        fig = _create_power_plot(results["power_dissipation"])
        report.add_figure(fig)

    return report


def _create_dc_analysis_plot(
    circuit: VoltageDividerCircuit, results: Dict[str, Any]
) -> go.Figure:
    """Create DC analysis visualization.

    Args:
        circuit: Voltage divider circuit
        results: DC analysis results

    Returns:
        Plotly figure
    """
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Voltage Distribution",
            "Current Flow",
            "Circuit Schematic",
            "Power Dissipation",
        ),
    )

    # Voltage bar chart
    components = ["Input", "R1", "R2", "Output"]
    voltages = [
        circuit.vin,
        results["r1_voltage"],
        results["r2_voltage"],
        results["output_voltage"],
    ]

    fig.add_trace(go.Bar(x=components, y=voltages, name="Voltage"), row=1, col=1)

    # Current flow
    components_i = ["R1", "R2"]
    currents = [results["r1_current"], results["r2_current"]]

    if circuit.r_load and "load_current" in results:
        components_i.append("Load")
        currents.append(results["load_current"])

    fig.add_trace(
        go.Bar(x=components_i, y=[c * 1000 for c in currents], name="Current (mA)"),
        row=1,
        col=2,
    )

    # Circuit schematic (simplified representation)
    # This would be better with actual circuit drawing
    schematic_text = f"""
    Vin ({circuit.vin}V) ---[R1={circuit.r1}Ω]---+--- Vout ({results['output_voltage']:.2f}V)
                                                  |
                                                 [R2={circuit.r2}Ω]
                                                  |
                                                 GND
    """

    fig.add_annotation(
        text=schematic_text,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.25,
        showarrow=False,
        font=dict(family="Courier New", size=10),
        row=2,
        col=1,
    )

    # Power dissipation bar chart (pie charts don't work well in subplots)
    if "power_dissipation" in results:
        power = results["power_dissipation"]
        labels = [k for k in power.keys() if k != "total"]
        values = [power[k] * 1000 for k in labels]  # Convert to mW

        fig.add_trace(
            go.Bar(x=labels, y=values, name="Power (mW)", marker_color="orange"),
            row=2,
            col=2,
        )

    fig.update_layout(title="Voltage Divider DC Analysis", showlegend=False, height=800)

    return fig


def _create_sweep_plot(results: Dict[str, Any]) -> go.Figure:
    """Create parameter sweep plot.

    Args:
        results: Sweep simulation results

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=results["sweep_values"],
            y=results["output_voltages"],
            mode="lines+markers",
            name="Output Voltage",
            line=dict(color="blue", width=2),
            marker=dict(size=6),
        )
    )

    # Add theoretical line if sweeping input voltage
    if results["sweep_param"] == "vin":
        # For voltage sweep, add ideal ratio line
        ideal_ratio = (
            results["output_voltages"][1] / results["sweep_values"][1]
            if results["sweep_values"][1] > 0
            else 0
        )
        fig.add_trace(
            go.Scatter(
                x=results["sweep_values"],
                y=[v * ideal_ratio for v in results["sweep_values"]],
                mode="lines",
                name="Theoretical",
                line=dict(color="red", width=2, dash="dash"),
            )
        )

    param_labels = {
        "vin": "Input Voltage (V)",
        "r1": "R1 Resistance (Ω)",
        "r2": "R2 Resistance (Ω)",
    }

    fig.update_layout(
        title=f"Parameter Sweep: {results['sweep_param'].upper()}",
        xaxis_title=param_labels.get(results["sweep_param"], results["sweep_param"]),
        yaxis_title="Output Voltage (V)",
        hovermode="x unified",
        height=500,
    )

    return fig


def _create_power_plot(power_data: Dict[str, float]) -> go.Figure:
    """Create power dissipation plot.

    Args:
        power_data: Power dissipation data

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    # Remove 'total' for component plot
    components = [k for k in power_data.keys() if k != "total"]
    powers = [power_data[k] * 1000 for k in components]  # Convert to mW

    fig.add_trace(
        go.Bar(
            x=components,
            y=powers,
            text=[f"{p:.2f} mW" for p in powers],
            textposition="auto",
            marker_color=["red", "orange", "yellow"][: len(components)],
        )
    )

    fig.update_layout(
        title="Power Dissipation by Component",
        xaxis_title="Component",
        yaxis_title="Power (mW)",
        showlegend=False,
        height=400,
    )

    # Add total power annotation
    fig.add_annotation(
        text=f"Total Power: {power_data.get('total', 0) * 1000:.2f} mW",
        xref="paper",
        yref="paper",
        x=1,
        y=1,
        showarrow=False,
        bgcolor="lightgray",
        bordercolor="black",
        borderwidth=1,
    )

    return fig
