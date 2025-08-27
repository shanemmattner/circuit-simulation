"""Interactive plotting with Plotly."""

import numpy as np
from typing import Dict, Any, List, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .smith_chart import impedance_to_reflection, calculate_vswr


def format_frequency_axis(frequencies: np.ndarray) -> Dict[str, Any]:
    """Format frequency axis for log scale.
    
    Args:
        frequencies: Frequency array
        
    Returns:
        Plotly axis configuration
    """
    return {
        "type": "log",
        "title": "Frequency (Hz)",
        "showgrid": True,
        "gridcolor": "rgba(128,128,128,0.2)"
    }


def prepare_bode_data(transfer_function: np.ndarray, frequencies: np.ndarray) -> tuple:
    """Prepare data for Bode plots.
    
    Args:
        transfer_function: Complex frequency response
        frequencies: Frequency array
        
    Returns:
        Tuple of (magnitude_data, phase_data)
    """
    # Calculate magnitude in dB and phase in degrees
    magnitude_db = 20 * np.log10(np.maximum(np.abs(transfer_function), 1e-10))
    phase_deg = np.degrees(np.angle(transfer_function))
    
    mag_data = {
        "x": frequencies,
        "y": magnitude_db,
        "name": "Magnitude"
    }
    
    phase_data = {
        "x": frequencies,
        "y": phase_deg,
        "name": "Phase"
    }
    
    return mag_data, phase_data


def prepare_smith_data(impedances: np.ndarray, frequencies: np.ndarray, z0: float) -> Dict[str, Any]:
    """Prepare data for Smith charts.
    
    Args:
        impedances: Complex impedance array
        frequencies: Frequency array
        z0: Reference impedance
        
    Returns:
        Smith chart data dictionary
    """
    # Convert to reflection coefficients
    reflection_coeffs = impedance_to_reflection(impedances, z0)
    
    # Calculate VSWR
    vswr = np.array([calculate_vswr(gamma) for gamma in reflection_coeffs])
    
    return {
        "real": reflection_coeffs.real.tolist(),
        "imag": reflection_coeffs.imag.tolist(),
        "frequencies": frequencies.tolist(),
        "impedances": impedances.tolist(),
        "vswr": vswr.tolist()
    }


def get_plotly_colors(num_colors: int) -> List[str]:
    """Get Plotly color palette.
    
    Args:
        num_colors: Number of colors needed
        
    Returns:
        List of color strings
    """
    # Plotly default colors
    plotly_colors = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ]
    
    # Extend if more colors needed
    colors = plotly_colors * ((num_colors // len(plotly_colors)) + 1)
    return colors[:num_colors]


def create_hover_template(plot_type: str) -> str:
    """Create hover template for different plot types.
    
    Args:
        plot_type: Type of plot (magnitude, phase, nyquist, smith)
        
    Returns:
        Hover template string
    """
    templates = {
        "magnitude": (
            "Frequency: %{x:.2f} Hz<br>"
            "Magnitude: %{y:.2f} dB<br>"
            "<extra></extra>"
        ),
        "phase": (
            "Frequency: %{x:.2f} Hz<br>"
            "Phase: %{y:.1f}°<br>"
            "<extra></extra>"
        ),
        "nyquist": (
            "Real: %{x:.3f}<br>"
            "Imag: %{y:.3f}<br>"
            "<extra></extra>"
        ),
        "smith": (
            "Real(Γ): %{x:.3f}<br>"
            "Imag(Γ): %{y:.3f}<br>"
            "VSWR: %{customdata:.2f}<br>"
            "<extra></extra>"
        )
    }
    
    return templates.get(plot_type, "%{x}, %{y}<extra></extra>")


class InteractivePlotter:
    """Interactive plotter using Plotly."""
    
    def __init__(self, theme: str = "plotly_white"):
        """Initialize interactive plotter.
        
        Args:
            theme: Plotly theme name
        """
        self.theme = theme
        self.config = {
            "displayModeBar": True,
            "modeBarButtonsToRemove": ["pan2d", "lasso2d"],
            "toImageButtonOptions": {
                "format": "png",
                "filename": "plot",
                "height": 600,
                "width": 800,
                "scale": 2
            }
        }
    
    def create_bode_plot(self, 
                        frequencies: np.ndarray,
                        transfer_function: np.ndarray,
                        title: str = "Interactive Bode Plot",
                        show_hover: bool = True,
                        show_export_buttons: bool = False) -> str:
        """Create interactive Bode plot.
        
        Args:
            frequencies: Frequency array
            transfer_function: Complex frequency response
            title: Plot title
            show_hover: Whether to show hover data
            show_export_buttons: Whether to show export buttons
            
        Returns:
            HTML string
        """
        # Prepare data
        mag_data, phase_data = prepare_bode_data(transfer_function, frequencies)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=["Magnitude", "Phase"],
            vertical_spacing=0.1,
            specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
        )
        
        # Magnitude plot
        hover_template_mag = create_hover_template("magnitude") if show_hover else None
        fig.add_trace(
            go.Scatter(
                x=mag_data["x"],
                y=mag_data["y"],
                mode="lines",
                name="Magnitude",
                line=dict(color="#1f77b4", width=2),
                hovertemplate=hover_template_mag
            ),
            row=1, col=1
        )
        
        # Phase plot
        hover_template_phase = create_hover_template("phase") if show_hover else None
        fig.add_trace(
            go.Scatter(
                x=phase_data["x"],
                y=phase_data["y"],
                mode="lines",
                name="Phase",
                line=dict(color="#ff7f0e", width=2),
                hovertemplate=hover_template_phase
            ),
            row=2, col=1
        )
        
        # Update layout
        fig.update_xaxes(type="log", title_text="", row=1, col=1)
        fig.update_xaxes(type="log", title_text="Frequency (Hz)", row=2, col=1)
        fig.update_yaxes(title_text="Magnitude (dB)", row=1, col=1)
        fig.update_yaxes(title_text="Phase (°)", row=2, col=1)
        
        fig.update_layout(
            title=title,
            template=self.theme,
            height=600,
            showlegend=False,
            hovermode="x unified" if show_hover else False
        )
        
        # Configure export options
        config = self.config.copy()
        if not show_export_buttons:
            config["modeBarButtonsToRemove"].extend(["toImage", "downloadPlot"])
        
        return fig.to_html(include_plotlyjs="cdn", config=config)
    
    def create_nyquist_plot(self,
                          transfer_function: np.ndarray,
                          frequencies: np.ndarray,
                          title: str = "Interactive Nyquist Plot") -> str:
        """Create interactive Nyquist plot.
        
        Args:
            transfer_function: Complex frequency response
            frequencies: Frequency array
            title: Plot title
            
        Returns:
            HTML string
        """
        real = transfer_function.real
        imag = transfer_function.imag
        
        fig = go.Figure()
        
        # Main trace
        fig.add_trace(
            go.Scatter(
                x=real,
                y=imag,
                mode="lines+markers",
                name="H(jω)",
                line=dict(color="#1f77b4", width=2),
                marker=dict(size=4),
                hovertemplate=create_hover_template("nyquist")
            )
        )
        
        # Add critical point
        fig.add_trace(
            go.Scatter(
                x=[-1],
                y=[0],
                mode="markers",
                name="Critical Point",
                marker=dict(
                    symbol="x",
                    size=15,
                    color="red",
                    line=dict(width=3)
                ),
                hovertemplate="Critical Point (-1, 0)<extra></extra>"
            )
        )
        
        # Update layout
        fig.update_layout(
            title=title,
            template=self.theme,
            xaxis_title="Real Part",
            yaxis_title="Imaginary Part",
            height=600,
            width=600,
            yaxis=dict(scaleanchor="x", scaleratio=1),  # Equal aspect ratio
            hovermode="closest"
        )
        
        return fig.to_html(include_plotlyjs="cdn", config=self.config)
    
    def create_smith_chart(self,
                          impedances: np.ndarray,
                          frequencies: np.ndarray,
                          z0: float = 50.0,
                          title: str = "Interactive Smith Chart") -> str:
        """Create interactive Smith chart.
        
        Args:
            impedances: Complex impedance array
            frequencies: Frequency array
            z0: Reference impedance
            title: Plot title
            
        Returns:
            HTML string
        """
        # Prepare Smith chart data
        smith_data = prepare_smith_data(impedances, frequencies, z0)
        
        fig = go.Figure()
        
        # Add Smith chart boundary (unit circle)
        theta = np.linspace(0, 2*np.pi, 100)
        boundary_x = np.cos(theta)
        boundary_y = np.sin(theta)
        
        fig.add_trace(
            go.Scatter(
                x=boundary_x,
                y=boundary_y,
                mode="lines",
                name="Smith Chart Boundary",
                line=dict(color="black", width=2),
                hoverinfo="skip"
            )
        )
        
        # Main impedance trajectory
        fig.add_trace(
            go.Scatter(
                x=smith_data["real"],
                y=smith_data["imag"],
                mode="lines+markers",
                name="Impedance",
                line=dict(color="#1f77b4", width=2),
                marker=dict(size=6),
                customdata=smith_data["vswr"],
                hovertemplate=create_hover_template("smith")
            )
        )
        
        # Update layout
        fig.update_layout(
            title=title,
            template=self.theme,
            xaxis_title="Real(Γ)",
            yaxis_title="Imag(Γ)",
            height=600,
            width=600,
            yaxis=dict(scaleanchor="x", scaleratio=1),  # Equal aspect ratio
            xaxis=dict(range=[-1.2, 1.2]),
            yaxis_range=[-1.2, 1.2],
            hovermode="closest"
        )
        
        return fig.to_html(include_plotlyjs="cdn", config=self.config)
    
    def create_multi_trace_bode(self,
                               frequencies: np.ndarray,
                               transfer_functions: Dict[str, np.ndarray],
                               title: str = "Multi-Trace Bode Plot") -> str:
        """Create Bode plot with multiple traces.
        
        Args:
            frequencies: Frequency array
            transfer_functions: Dictionary of {name: transfer_function}
            title: Plot title
            
        Returns:
            HTML string
        """
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=["Magnitude", "Phase"],
            vertical_spacing=0.1
        )
        
        colors = get_plotly_colors(len(transfer_functions))
        
        for i, (name, tf) in enumerate(transfer_functions.items()):
            mag_data, phase_data = prepare_bode_data(tf, frequencies)
            color = colors[i]
            
            # Magnitude trace
            fig.add_trace(
                go.Scatter(
                    x=mag_data["x"],
                    y=mag_data["y"],
                    mode="lines",
                    name=f"{name} (Mag)",
                    line=dict(color=color, width=2),
                    legendgroup=name,
                    hovertemplate=create_hover_template("magnitude")
                ),
                row=1, col=1
            )
            
            # Phase trace
            fig.add_trace(
                go.Scatter(
                    x=phase_data["x"],
                    y=phase_data["y"],
                    mode="lines",
                    name=f"{name} (Phase)",
                    line=dict(color=color, width=2, dash="dash"),
                    legendgroup=name,
                    showlegend=False,  # Only show magnitude in legend
                    hovertemplate=create_hover_template("phase")
                ),
                row=2, col=1
            )
        
        # Update layout
        fig.update_xaxes(type="log", title_text="", row=1, col=1)
        fig.update_xaxes(type="log", title_text="Frequency (Hz)", row=2, col=1)
        fig.update_yaxes(title_text="Magnitude (dB)", row=1, col=1)
        fig.update_yaxes(title_text="Phase (°)", row=2, col=1)
        
        fig.update_layout(
            title=title,
            template=self.theme,
            height=700,
            hovermode="x unified"
        )
        
        return fig.to_html(include_plotlyjs="cdn", config=self.config)