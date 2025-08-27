"""Visualization functions for RLC resonance circuit."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
from .circuit import RLCResonanceCircuit


def generate_resonance_plots(
    circuit: RLCResonanceCircuit,
    spectrum: Optional[Dict[str, Any]] = None,
    plot_type: str = "bode",
    **kwargs,
) -> go.Figure:
    """Generate resonance visualization plots.

    Args:
        circuit: RLC resonance circuit
        spectrum: Pre-calculated spectrum data (optional)
        plot_type: Type of plot ("bode", "nyquist", "3d_surface", "impedance")
        **kwargs: Additional plot parameters

    Returns:
        Plotly figure
    """
    if plot_type == "bode":
        return _create_bode_plot(circuit, spectrum)
    elif plot_type == "nyquist":
        return _create_nyquist_plot(circuit, spectrum)
    elif plot_type == "3d_surface":
        return generate_3d_response(circuit, **kwargs)
    elif plot_type == "impedance":
        return _create_impedance_plot(circuit, spectrum)
    else:
        raise ValueError(f"Unknown plot type: {plot_type}")


def _create_bode_plot(
    circuit: RLCResonanceCircuit, spectrum: Optional[Dict[str, Any]] = None
) -> go.Figure:
    """Create Bode plot for RLC resonance.

    Args:
        circuit: RLC circuit
        spectrum: Frequency response data

    Returns:
        Bode plot figure
    """
    if spectrum is None:
        # Generate default spectrum
        frequencies = np.logspace(
            np.log10(circuit.resonant_frequency / 100),
            np.log10(circuit.resonant_frequency * 100),
            200,
        )
        from .simulation import calculate_frequency_response

        spectrum = calculate_frequency_response(circuit, frequencies)

    fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=(f"Magnitude Response - {circuit.topology.title()} RLC", "Phase Response"),
        shared_xaxes=True,
        vertical_spacing=0.12,
    )

    # Magnitude plot - handle both formats
    if "magnitude_db" not in spectrum:
        # Generate frequency response if we only have impedance data
        if "impedance_mag" in spectrum and "magnitude" not in spectrum:
            # This is impedance spectrum, need to generate transfer function
            from .simulation import calculate_frequency_response

            freq_response = calculate_frequency_response(circuit, np.array(spectrum["frequency"]))
            spectrum.update(freq_response)

        # Convert magnitude to dB if needed
        if "magnitude" in spectrum:
            spectrum["magnitude_db"] = [
                20 * np.log10(m) if m > 0 else -100 for m in spectrum["magnitude"]
            ]

    mag_key = "magnitude_db"

    fig.add_trace(
        go.Scatter(
            x=spectrum["frequency"],
            y=spectrum[mag_key],
            mode="lines",
            name="Magnitude",
            line=dict(color="blue", width=2),
            hovertemplate="%{x:.1f} Hz<br>%{y:.2f} dB<extra></extra>",
        ),
        row=1,
        col=1,
    )

    # Mark resonant frequency
    f0_index = np.argmin(np.abs(np.array(spectrum["frequency"]) - circuit.resonant_frequency))
    f0_mag = spectrum["magnitude_db"][f0_index]

    fig.add_trace(
        go.Scatter(
            x=[circuit.resonant_frequency],
            y=[f0_mag],
            mode="markers+text",
            name=f"f₀ = {circuit.resonant_frequency:.1f} Hz",
            marker=dict(size=10, color="red", symbol="x"),
            text=[f"f₀"],
            textposition="top center",
            hovertemplate=f"Resonance: {circuit.resonant_frequency:.1f} Hz<br>{f0_mag:.2f} dB<extra></extra>",
        ),
        row=1,
        col=1,
    )

    # Mark -3dB points
    f_lower, f_upper = circuit.calculate_half_power_frequencies()

    # Add bandwidth annotation
    fig.add_shape(
        type="line",
        x0=f_lower,
        y0=f0_mag - 3,
        x1=f_upper,
        y1=f0_mag - 3,
        line=dict(color="gray", dash="dash"),
        row=1,
        col=1,
    )

    fig.add_annotation(
        x=circuit.resonant_frequency,
        y=f0_mag - 3,
        text=f"BW = {circuit.bandwidth:.1f} Hz",
        showarrow=False,
        row=1,
        col=1,
    )

    # Phase plot
    fig.add_trace(
        go.Scatter(
            x=spectrum["frequency"],
            y=spectrum["phase"],
            mode="lines",
            name="Phase",
            line=dict(color="green", width=2),
            hovertemplate="%{x:.1f} Hz<br>%{y:.1f}°<extra></extra>",
        ),
        row=2,
        col=1,
    )

    # Mark phase at resonance
    f0_phase = spectrum["phase"][f0_index]
    fig.add_trace(
        go.Scatter(
            x=[circuit.resonant_frequency],
            y=[f0_phase],
            mode="markers",
            name="Phase at f₀",
            marker=dict(size=10, color="red", symbol="x"),
            showlegend=False,
            hovertemplate=f"{circuit.resonant_frequency:.1f} Hz<br>{f0_phase:.1f}°<extra></extra>",
        ),
        row=2,
        col=1,
    )

    # Update axes
    fig.update_xaxes(type="log", title_text="Frequency (Hz)", row=2, col=1)
    fig.update_xaxes(type="log", row=1, col=1)
    fig.update_yaxes(title_text="Magnitude (dB)", row=1, col=1)
    fig.update_yaxes(title_text="Phase (degrees)", row=2, col=1)

    # Add circuit parameters
    params_text = (
        f"R = {circuit.r} Ω<br>"
        f"L = {circuit.l*1e3:.2f} mH<br>"
        f"C = {circuit.c*1e6:.2f} µF<br>"
        f"Q = {circuit.q_factor:.2f}<br>"
        f"ζ = {circuit.damping_ratio:.3f}"
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

    fig.update_layout(
        title=f"RLC {circuit.topology.title()} Resonance - Bode Plot",
        height=700,
        hovermode="x unified",
        showlegend=True,
    )

    return fig


def _create_nyquist_plot(
    circuit: RLCResonanceCircuit, spectrum: Optional[Dict[str, Any]] = None
) -> go.Figure:
    """Create Nyquist plot (impedance in complex plane).

    Args:
        circuit: RLC circuit
        spectrum: Impedance spectrum data

    Returns:
        Nyquist plot figure
    """
    if spectrum is None or "real_part" not in spectrum:
        # Generate impedance spectrum
        frequencies = np.logspace(
            np.log10(circuit.resonant_frequency / 100),
            np.log10(circuit.resonant_frequency * 100),
            200,
        )
        from .simulation import calculate_impedance_spectrum

        spectrum = calculate_impedance_spectrum(circuit, frequencies)

    fig = go.Figure()

    # Main Nyquist trace
    fig.add_trace(
        go.Scatter(
            x=spectrum["real_part"],
            y=spectrum["imaginary_part"],
            mode="lines+markers",
            name="Impedance",
            line=dict(color="blue", width=2),
            marker=dict(size=4, color=spectrum["frequency"], colorscale="Viridis", showscale=True),
            text=[f"{f:.1f} Hz" for f in spectrum["frequency"]],
            hovertemplate="%{text}<br>Z = %{x:.2f} + j%{y:.2f} Ω<extra></extra>",
        )
    )

    # Mark resonant frequency
    f0_index = np.argmin(np.abs(np.array(spectrum["frequency"]) - circuit.resonant_frequency))

    fig.add_trace(
        go.Scatter(
            x=[spectrum["real_part"][f0_index]],
            y=[spectrum["imaginary_part"][f0_index]],
            mode="markers+text",
            name=f"f₀ = {circuit.resonant_frequency:.1f} Hz",
            marker=dict(size=12, color="red", symbol="x"),
            text=["f₀"],
            textposition="top center",
        )
    )

    # Add zero reference
    fig.add_trace(
        go.Scatter(
            x=[0],
            y=[0],
            mode="markers",
            name="Origin",
            marker=dict(size=8, color="black", symbol="cross"),
        )
    )

    fig.update_layout(
        title=f"Nyquist Plot - RLC {circuit.topology.title()} Impedance",
        xaxis_title="Real Part (Ω)",
        yaxis_title="Imaginary Part (Ω)",
        height=600,
        width=700,
        hovermode="closest",
        showlegend=True,
        yaxis=dict(scaleanchor="x", scaleratio=1),
    )

    return fig


def _create_impedance_plot(
    circuit: RLCResonanceCircuit, spectrum: Optional[Dict[str, Any]] = None
) -> go.Figure:
    """Create impedance magnitude and phase plot.

    Args:
        circuit: RLC circuit
        spectrum: Impedance spectrum data

    Returns:
        Impedance plot figure
    """
    if spectrum is None:
        frequencies = np.logspace(
            np.log10(circuit.resonant_frequency / 100),
            np.log10(circuit.resonant_frequency * 100),
            200,
        )
        from .simulation import calculate_impedance_spectrum

        spectrum = calculate_impedance_spectrum(circuit, frequencies)

    fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=("Impedance Magnitude", "Impedance Phase"),
        shared_xaxes=True,
        vertical_spacing=0.12,
    )

    # Magnitude plot
    fig.add_trace(
        go.Scatter(
            x=spectrum["frequency"],
            y=spectrum["impedance_mag"],
            mode="lines",
            name="|Z|",
            line=dict(color="purple", width=2),
        ),
        row=1,
        col=1,
    )

    # Mark minimum/maximum impedance
    if circuit.topology == "series":
        # Series has minimum at resonance
        min_index = np.argmin(spectrum["impedance_mag"])
        fig.add_trace(
            go.Scatter(
                x=[spectrum["frequency"][min_index]],
                y=[spectrum["impedance_mag"][min_index]],
                mode="markers+text",
                name="Min Z",
                marker=dict(size=10, color="red"),
                text=[f'Z={spectrum["impedance_mag"][min_index]:.1f}Ω'],
                textposition="top center",
            ),
            row=1,
            col=1,
        )
    else:
        # Parallel has maximum at resonance
        max_index = np.argmax(spectrum["impedance_mag"])
        fig.add_trace(
            go.Scatter(
                x=[spectrum["frequency"][max_index]],
                y=[spectrum["impedance_mag"][max_index]],
                mode="markers+text",
                name="Max Z",
                marker=dict(size=10, color="red"),
                text=[f'Z={spectrum["impedance_mag"][max_index]:.1f}Ω'],
                textposition="bottom center",
            ),
            row=1,
            col=1,
        )

    # Phase plot
    fig.add_trace(
        go.Scatter(
            x=spectrum["frequency"],
            y=spectrum["impedance_phase"],
            mode="lines",
            name="∠Z",
            line=dict(color="orange", width=2),
        ),
        row=2,
        col=1,
    )

    # Add zero phase line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)

    # Update axes
    fig.update_xaxes(type="log", title_text="Frequency (Hz)", row=2, col=1)
    fig.update_xaxes(type="log", row=1, col=1)
    fig.update_yaxes(title_text="Impedance (Ω)", type="log", row=1, col=1)
    fig.update_yaxes(title_text="Phase (degrees)", row=2, col=1)

    fig.update_layout(
        title=f"Impedance Analysis - RLC {circuit.topology.title()}",
        height=700,
        hovermode="x unified",
    )

    return fig


def generate_smith_chart(
    circuit: RLCResonanceCircuit, frequencies: Optional[np.ndarray] = None
) -> go.Figure:
    """Generate Smith chart for impedance visualization.

    Args:
        circuit: RLC circuit
        frequencies: Frequency array (optional)

    Returns:
        Smith chart figure
    """
    # This is a simplified Smith chart
    # Full implementation would include constant resistance and reactance circles

    if frequencies is None:
        frequencies = np.logspace(
            np.log10(circuit.resonant_frequency / 10),
            np.log10(circuit.resonant_frequency * 10),
            100,
        )

    # Calculate normalized impedance
    z0 = circuit.characteristic_impedance
    reflection_coefficients = []

    for freq in frequencies:
        z = circuit.calculate_impedance(freq)
        # Reflection coefficient: Γ = (Z - Z0) / (Z + Z0)
        gamma = (z - z0) / (z + z0)
        reflection_coefficients.append(gamma)

    fig = go.Figure()

    # Plot reflection coefficient
    fig.add_trace(
        go.Scatter(
            x=[g.real for g in reflection_coefficients],
            y=[g.imag for g in reflection_coefficients],
            mode="lines+markers",
            name="Γ(f)",
            marker=dict(size=4, color=frequencies, colorscale="Viridis"),
            text=[f"{f:.1f} Hz" for f in frequencies],
            hovertemplate="%{text}<br>Γ = %{x:.3f} + j%{y:.3f}<extra></extra>",
        )
    )

    # Add unit circle
    theta = np.linspace(0, 2 * np.pi, 100)
    fig.add_trace(
        go.Scatter(
            x=np.cos(theta),
            y=np.sin(theta),
            mode="lines",
            name="Unit Circle",
            line=dict(color="gray", dash="dash"),
            showlegend=False,
        )
    )

    # Mark resonance
    z_res = circuit.calculate_impedance(circuit.resonant_frequency)
    gamma_res = (z_res - z0) / (z_res + z0)

    fig.add_trace(
        go.Scatter(
            x=[gamma_res.real],
            y=[gamma_res.imag],
            mode="markers+text",
            name="f₀",
            marker=dict(size=10, color="red"),
            text=["f₀"],
            textposition="top center",
        )
    )

    fig.update_layout(
        title="Smith Chart - Normalized Impedance",
        xaxis_title="Real(Γ)",
        yaxis_title="Imag(Γ)",
        height=600,
        width=600,
        yaxis=dict(scaleanchor="x", scaleratio=1),
        xaxis=dict(range=[-1.2, 1.2]),
        yaxis_range=[-1.2, 1.2],
    )

    return fig


def generate_3d_response(
    circuit: RLCResonanceCircuit,
    vary_param: str = "r",
    param_range: Tuple[float, float, int] = None,
    frequency_range: Tuple[float, float, int] = None,
) -> go.Figure:
    """Generate 3D surface plot varying a parameter.

    Args:
        circuit: RLC circuit
        vary_param: Parameter to vary ("r", "l", "c", or "q")
        param_range: (min, max, steps) for parameter
        frequency_range: (min, max, steps) for frequency

    Returns:
        3D surface plot
    """
    # Default ranges
    if param_range is None:
        original_value = getattr(circuit, vary_param) if vary_param != "q" else circuit.q_factor
        param_range = (original_value * 0.1, original_value * 10, 20)

    if frequency_range is None:
        frequency_range = (circuit.resonant_frequency / 100, circuit.resonant_frequency * 100, 50)

    # Create parameter and frequency arrays
    if vary_param == "q":
        # Special case for Q factor
        q_values = np.linspace(param_range[0], param_range[1], param_range[2])
        param_values = []
        for q in q_values:
            # Calculate R for desired Q
            r = circuit.characteristic_impedance / q
            param_values.append(r)
        param_display = q_values
        param_label = "Q Factor"
    else:
        param_values = np.linspace(param_range[0], param_range[1], param_range[2])
        param_display = param_values
        param_label = {"r": "Resistance (Ω)", "l": "Inductance (H)", "c": "Capacitance (F)"}[
            vary_param
        ]

    frequencies = np.logspace(
        np.log10(frequency_range[0]), np.log10(frequency_range[1]), frequency_range[2]
    )

    # Calculate response surface
    Z = np.zeros((len(param_values), len(frequencies)))

    original_value = getattr(circuit, vary_param if vary_param != "q" else "r")

    for i, param_val in enumerate(param_values):
        # Set parameter value
        setattr(circuit, vary_param if vary_param != "q" else "r", param_val)
        circuit._calculate_parameters()

        for j, freq in enumerate(frequencies):
            h = circuit.transfer_function(freq)
            Z[i, j] = 20 * np.log10(abs(h)) if abs(h) > 0 else -100

    # Restore original value
    setattr(circuit, vary_param if vary_param != "q" else "r", original_value)
    circuit._calculate_parameters()

    # Create 3D surface plot
    fig = go.Figure(
        data=[
            go.Surface(
                x=frequencies,
                y=param_display,
                z=Z,
                colorscale="Viridis",
                showscale=True,
                colorbar=dict(title="Magnitude (dB)"),
            )
        ]
    )

    fig.update_layout(
        title=f"3D Response Surface - Varying {param_label}",
        scene=dict(
            xaxis_title="Frequency (Hz)",
            xaxis_type="log",
            yaxis_title=param_label,
            zaxis_title="Magnitude (dB)",
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)),
        ),
        height=700,
    )

    return fig
