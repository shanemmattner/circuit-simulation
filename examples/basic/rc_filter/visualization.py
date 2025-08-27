"""Visualization functions for RC filter circuit."""

from typing import Any, Dict, Optional

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .circuit import RCFilterCircuit


def generate_bode_plot(
    circuit: RCFilterCircuit,
    response: Dict[str, Any],
    show_cutoff: bool = True,
    show_phase: bool = True,
    title: Optional[str] = None,
) -> go.Figure:
    """Generate Bode plot for frequency response.

    Args:
        circuit: RC filter circuit
        response: Frequency response data
        show_cutoff: Whether to show cutoff frequency marker
        show_phase: Whether to include phase plot
        title: Custom title (optional)

    Returns:
        Plotly figure with Bode plot
    """
    if title is None:
        title = f"Bode Plot - RC {circuit.filter_type.title()}-Pass Filter"

    # Create subplots
    if show_phase:
        fig = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=("Magnitude", "Phase"),
            shared_xaxes=True,
            vertical_spacing=0.1,
        )
    else:
        fig = go.Figure()

    # Magnitude plot
    freq = response["frequency"]
    mag_db = response["magnitude_db"]

    mag_trace = go.Scatter(
        x=freq,
        y=mag_db,
        mode="lines",
        name="Magnitude",
        line=dict(color="blue", width=2),
        hovertemplate="%{x:.1f} Hz<br>%{y:.2f} dB<extra></extra>",
    )

    if show_phase:
        fig.add_trace(mag_trace, row=1, col=1)
    else:
        fig.add_trace(mag_trace)

    # Add cutoff frequency marker
    if show_cutoff:
        fc = circuit.cutoff_frequency
        # Find magnitude at cutoff
        fc_index = np.argmin(np.abs(np.array(freq) - fc))
        fc_mag = mag_db[fc_index]

        cutoff_trace = go.Scatter(
            x=[fc],
            y=[fc_mag],
            mode="markers+text",
            name="Cutoff (-3dB)",
            marker=dict(size=10, color="red", symbol="x"),
            text=[f"{fc:.1f} Hz"],
            textposition="top right",
            showlegend=True,
            hovertemplate=f"Cutoff: {fc:.1f} Hz<br>-3 dB<extra></extra>",
        )

        # Add cutoff frequency annotation
        fig.add_annotation(
            x=np.log10(fc),
            y=fc_mag,
            text=f"Cutoff: {fc:.1f} Hz",
            showarrow=True,
            arrowhead=2,
            arrowcolor="red",
            ax=20,
            ay=-30,
        )

        if show_phase:
            fig.add_trace(cutoff_trace, row=1, col=1)

            # Add -3dB line
            fig.add_hline(
                y=-3, line_dash="dash", line_color="gray", annotation_text="-3dB", row=1, col=1
            )
        else:
            fig.add_trace(cutoff_trace)
            fig.add_hline(y=-3, line_dash="dash", line_color="gray")

    # Phase plot
    if show_phase:
        phase = response["phase"]

        phase_trace = go.Scatter(
            x=freq,
            y=phase,
            mode="lines",
            name="Phase",
            line=dict(color="green", width=2),
            hovertemplate="%{x:.1f} Hz<br>%{y:.1f}°<extra></extra>",
        )
        fig.add_trace(phase_trace, row=2, col=1)

        # Add cutoff frequency marker for phase
        if show_cutoff:
            fc_phase_index = np.argmin(np.abs(np.array(freq) - fc))
            fc_phase = phase[fc_phase_index]

            phase_cutoff = go.Scatter(
                x=[fc],
                y=[fc_phase],
                mode="markers",
                name="Cutoff Phase",
                marker=dict(size=10, color="red", symbol="x"),
                showlegend=False,
                hovertemplate=f"{fc:.1f} Hz<br>{fc_phase:.1f}°<extra></extra>",
            )
            fig.add_trace(phase_cutoff, row=2, col=1)

            # Add -45° line for reference
            fig.add_hline(
                y=-45, line_dash="dash", line_color="gray", annotation_text="-45°", row=2, col=1
            )

    # Update layout
    fig.update_xaxes(type="log", title_text="Frequency (Hz)")

    if show_phase:
        fig.update_yaxes(title_text="Magnitude (dB)", row=1, col=1)
        fig.update_yaxes(title_text="Phase (degrees)", row=2, col=1)
        fig.update_xaxes(title_text="Frequency (Hz)", row=2, col=1)
    else:
        fig.update_yaxes(title_text="Magnitude (dB)")

    fig.update_layout(
        title=title,
        hovermode="x unified",
        height=600 if show_phase else 400,
        showlegend=True,
        legend=dict(x=0.7, y=0.95),
    )

    # Add annotations with filter parameters
    params_text = (
        f"R = {circuit.r} Ω<br>"
        f"C = {circuit.c*1e6:.2f} µF<br>"
        f"fc = {circuit.cutoff_frequency:.1f} Hz<br>"
        f"τ = {circuit.time_constant*1000:.2f} ms"
    )

    fig.add_annotation(
        text=params_text,
        xref="paper",
        yref="paper",
        x=0.02,
        y=0.98,
        showarrow=False,
        bordercolor="black",
        borderwidth=1,
        bgcolor="white",
        align="left",
    )

    return fig


def generate_transient_plot(
    circuit: RCFilterCircuit, results: Dict[str, Any], title: Optional[str] = None
) -> go.Figure:
    """Generate transient response plot.

    Args:
        circuit: RC filter circuit
        results: Transient simulation results
        title: Custom title (optional)

    Returns:
        Plotly figure with transient response
    """
    if title is None:
        input_type = results.get("input_type", "step")
        title = f"RC {circuit.filter_type.title()}-Pass Filter - {input_type.title()} Response"

    fig = go.Figure()

    time = np.array(results["time"]) * 1000  # Convert to ms
    input_signal = results["input"]
    output_signal = results["output"]

    # Input signal
    fig.add_trace(
        go.Scatter(
            x=time,
            y=input_signal,
            mode="lines",
            name="Input",
            line=dict(color="blue", width=2),
            hovertemplate="%{x:.3f} ms<br>%{y:.3f} V<extra></extra>",
        )
    )

    # Output signal
    fig.add_trace(
        go.Scatter(
            x=time,
            y=output_signal,
            mode="lines",
            name="Output",
            line=dict(color="red", width=2),
            hovertemplate="%{x:.3f} ms<br>%{y:.3f} V<extra></extra>",
        )
    )

    # Add time constant markers
    tau_ms = circuit.time_constant * 1000

    # Mark tau (63.2% for lowpass step response)
    if results.get("input_type") == "step":
        fig.add_vline(x=tau_ms, line_dash="dash", line_color="gray", annotation_text="τ")

        # Mark 5τ (99.3% settling)
        fig.add_vline(x=5 * tau_ms, line_dash="dot", line_color="gray", annotation_text="5τ")

    fig.update_layout(
        title=title,
        xaxis_title="Time (ms)",
        yaxis_title="Voltage (V)",
        hovermode="x unified",
        height=500,
        showlegend=True,
    )

    # Add circuit parameters annotation
    params_text = (
        f"R = {circuit.r} Ω<br>"
        f"C = {circuit.c*1e6:.2f} µF<br>"
        f"τ = {tau_ms:.2f} ms<br>"
        f"fc = {circuit.cutoff_frequency:.1f} Hz"
    )

    fig.add_annotation(
        text=params_text,
        xref="paper",
        yref="paper",
        x=0.7,
        y=0.95,
        showarrow=False,
        bordercolor="black",
        borderwidth=1,
        bgcolor="white",
        align="left",
    )

    return fig


def generate_comparison_plot(
    circuits: list, frequency_range: tuple = (1, 100000), points: int = 100
) -> go.Figure:
    """Compare multiple RC filter configurations.

    Args:
        circuits: List of RCFilterCircuit instances
        frequency_range: (start, stop) frequencies in Hz
        points: Number of frequency points

    Returns:
        Plotly figure comparing filters
    """
    fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=("Magnitude Response", "Phase Response"),
        shared_xaxes=True,
        vertical_spacing=0.1,
    )

    # Generate frequency points
    frequencies = np.logspace(np.log10(frequency_range[0]), np.log10(frequency_range[1]), points)

    colors = ["blue", "red", "green", "orange", "purple"]

    for i, circuit in enumerate(circuits):
        color = colors[i % len(colors)]
        label = f"{circuit.filter_type.title()} (fc={circuit.cutoff_frequency:.1f}Hz)"

        # Calculate response
        mags = []
        phases = []
        for freq in frequencies:
            h = circuit.transfer_function(freq)
            mags.append(20 * np.log10(abs(h)) if abs(h) > 0 else -100)
            phases.append(np.degrees(np.angle(h)))

        # Magnitude
        fig.add_trace(
            go.Scatter(
                x=frequencies, y=mags, mode="lines", name=label, line=dict(color=color, width=2)
            ),
            row=1,
            col=1,
        )

        # Phase
        fig.add_trace(
            go.Scatter(
                x=frequencies,
                y=phases,
                mode="lines",
                name=label,
                line=dict(color=color, width=2),
                showlegend=False,
            ),
            row=2,
            col=1,
        )

    # Update axes
    fig.update_xaxes(type="log", title_text="Frequency (Hz)", row=2, col=1)
    fig.update_xaxes(type="log", row=1, col=1)
    fig.update_yaxes(title_text="Magnitude (dB)", row=1, col=1)
    fig.update_yaxes(title_text="Phase (degrees)", row=2, col=1)

    # Add reference lines
    fig.add_hline(y=-3, line_dash="dash", line_color="gray", row=1, col=1)
    fig.add_hline(y=-45, line_dash="dash", line_color="gray", row=2, col=1)

    fig.update_layout(title="RC Filter Comparison", height=700, hovermode="x unified")

    return fig
