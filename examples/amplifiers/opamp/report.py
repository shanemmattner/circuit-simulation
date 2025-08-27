"""Report generation for op-amp amplifier circuits."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, Any, Optional
from pathlib import Path


class AmplifierReport:
    """Report for amplifier analysis."""
    
    def __init__(self, title: str = "Op-Amp Amplifier Analysis"):
        self.title = title
        self.figures = []
        
    def add_figure(self, fig):
        self.figures.append(fig)


def generate_amplifier_report(
    circuit,
    results: Dict[str, Any],
    analysis: Dict[str, Any]
) -> AmplifierReport:
    """Generate comprehensive amplifier report.
    
    Args:
        circuit: Op-amp circuit
        results: Simulation results
        analysis: Analysis results
        
    Returns:
        AmplifierReport instance
    """
    report = AmplifierReport(
        title=f"Op-Amp {circuit.config.replace('_', ' ').title()} Amplifier Analysis"
    )
    
    # Create frequency response plot if AC results available
    if "frequency" in results and results.get("analysis_type") == "ac":
        fig = _create_bode_plot(results, circuit.config)
        report.add_figure(fig)
    
    # Create DC transfer characteristic if available
    if "input_voltage" in results and results.get("analysis_type") == "dc":
        fig = _create_dc_transfer_plot(results)
        report.add_figure(fig)
    
    # Create summary figure
    fig = _create_summary_figure(circuit, analysis)
    report.add_figure(fig)
    
    return report


def _create_bode_plot(results: Dict[str, Any], config: str) -> go.Figure:
    """Create Bode plot from frequency response.
    
    Args:
        results: AC simulation results
        config: Circuit configuration
        
    Returns:
        Plotly figure
    """
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(f"Magnitude Response - {config.title()}", "Phase Response"),
        shared_xaxes=True,
        vertical_spacing=0.12
    )
    
    # Magnitude plot
    fig.add_trace(
        go.Scatter(
            x=results["frequency"],
            y=results["gain_db"],
            mode='lines',
            name='Gain',
            line=dict(color='blue', width=2)
        ),
        row=1, col=1
    )
    
    # Phase plot
    fig.add_trace(
        go.Scatter(
            x=results["frequency"],
            y=results["phase"],
            mode='lines',
            name='Phase',
            line=dict(color='green', width=2)
        ),
        row=2, col=1
    )
    
    # Update axes
    fig.update_xaxes(type="log", title_text="Frequency (Hz)", row=2, col=1)
    fig.update_xaxes(type="log", row=1, col=1)
    fig.update_yaxes(title_text="Gain (dB)", row=1, col=1)
    fig.update_yaxes(title_text="Phase (degrees)", row=2, col=1)
    
    fig.update_layout(
        title="Frequency Response",
        height=600,
        hovermode='x unified'
    )
    
    return fig


def _create_dc_transfer_plot(results: Dict[str, Any]) -> go.Figure:
    """Create DC transfer characteristic plot.
    
    Args:
        results: DC simulation results
        
    Returns:
        Plotly figure
    """
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=results["input_voltage"],
            y=results["output_voltages"],
            mode='lines',
            name='Transfer Characteristic',
            line=dict(color='red', width=2)
        )
    )
    
    # Add ideal line if gain is available
    if "gain" in results and results["gain"] is not None:
        vin = np.array(results["input_voltage"])
        ideal_vout = results["gain"] * vin
        
        fig.add_trace(
            go.Scatter(
                x=results["input_voltage"],
                y=ideal_vout.tolist(),
                mode='lines',
                name='Ideal Response',
                line=dict(color='gray', width=1, dash='dash')
            )
        )
    
    fig.update_layout(
        title="DC Transfer Characteristic",
        xaxis_title="Input Voltage (V)",
        yaxis_title="Output Voltage (V)",
        height=500,
        hovermode='x unified'
    )
    
    return fig


def _create_summary_figure(circuit, analysis: Dict[str, Any]) -> go.Figure:
    """Create summary figure with key parameters.
    
    Args:
        circuit: Op-amp circuit
        analysis: Analysis results
        
    Returns:
        Plotly figure
    """
    fig = go.Figure()
    
    # Create text summary
    summary_text = f"""
    <b>Configuration:</b> {circuit.config.replace('_', ' ').title()}<br>
    <b>Model:</b> {circuit.model}<br>
    <b>Ideal Gain:</b> {analysis.get('ideal_gain', 'N/A'):.2f}<br>
    <b>Input Impedance:</b> {analysis.get('input_impedance', 0):.2e} Ω<br>
    <b>Output Impedance:</b> {analysis.get('output_impedance', 0):.2f} Ω<br>
    """
    
    if 'bandwidth' in analysis:
        summary_text += f"<b>Bandwidth:</b> {analysis['bandwidth']:.2e} Hz<br>"
    
    if 'slew_rate' in analysis:
        summary_text += f"<b>Slew Rate:</b> {analysis['slew_rate_v_us']:.2f} V/µs<br>"
    
    if 'phase_margin' in analysis:
        summary_text += f"<b>Phase Margin:</b> {analysis['phase_margin']:.1f}°<br>"
    
    if 'is_stable' in analysis:
        stability = "Stable" if analysis['is_stable'] else "Unstable"
        summary_text += f"<b>Stability:</b> {stability}<br>"
    
    fig.add_annotation(
        text=summary_text,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=14),
        align="left"
    )
    
    fig.update_layout(
        title="Amplifier Summary",
        height=400,
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )
    
    return fig