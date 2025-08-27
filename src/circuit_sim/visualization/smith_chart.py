"""Smith chart visualization for RF impedance analysis."""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Optional, Dict, Any, List, Tuple
from .base import BasePlotter, PlotResult
from .styles import PlotStyle


def impedance_to_reflection(z: complex, z0: float) -> complex:
    """Convert impedance to reflection coefficient.
    
    Args:
        z: Complex impedance
        z0: Reference impedance
        
    Returns:
        Reflection coefficient Γ = (Z - Z0)/(Z + Z0)
    """
    return (z - z0) / (z + z0)


def reflection_to_impedance(gamma: complex, z0: float) -> complex:
    """Convert reflection coefficient to impedance.
    
    Args:
        gamma: Reflection coefficient
        z0: Reference impedance
        
    Returns:
        Impedance Z = Z0 * (1 + Γ)/(1 - Γ)
    """
    if np.abs(1 - gamma) < 1e-10:
        # Handle edge case where |γ| ≈ 1 (infinite impedance)
        return complex(np.inf, 0)
    return z0 * (1 + gamma) / (1 - gamma)


def calculate_vswr(gamma: complex) -> float:
    """Calculate VSWR from reflection coefficient.
    
    Args:
        gamma: Reflection coefficient
        
    Returns:
        Voltage Standing Wave Ratio
    """
    mag = np.abs(gamma)
    if mag >= 1.0:
        return np.inf
    return (1 + mag) / (1 - mag)


def calculate_return_loss(gamma: complex) -> float:
    """Calculate return loss in dB.
    
    Args:
        gamma: Reflection coefficient
        
    Returns:
        Return loss in dB
    """
    mag = np.abs(gamma)
    if mag == 0:
        return np.inf
    return -20 * np.log10(mag)


def generate_resistance_circles(r_values: List[float]) -> List[Dict[str, Any]]:
    """Generate constant resistance circles for Smith chart.
    
    Args:
        r_values: Normalized resistance values
        
    Returns:
        List of circle definitions
    """
    circles = []
    for r in r_values:
        # For normalized resistance r, circle center is at (r/(r+1), 0)
        # with radius 1/(r+1)
        center_x = r / (r + 1)
        center_y = 0
        radius = 1 / (r + 1)
        
        circles.append({
            "center": (center_x, center_y),
            "radius": radius,
            "value": r
        })
    
    return circles


def generate_reactance_arcs(x_values: List[float]) -> List[Dict[str, Any]]:
    """Generate constant reactance arcs for Smith chart.
    
    Args:
        x_values: Normalized reactance values
        
    Returns:
        List of arc definitions
    """
    arcs = []
    for x in x_values:
        if x == 0:
            continue  # x=0 is the horizontal axis
        
        # For normalized reactance x, arc center is at (1, 1/x)
        # with radius |1/x|
        center_x = 1
        center_y = 1 / x
        radius = abs(1 / x)
        
        # Calculate arc angles
        if x > 0:
            # Inductive (upper hemisphere)
            start_angle = 180 - np.degrees(np.arctan(1/x))
            end_angle = 0
        else:
            # Capacitive (lower hemisphere)
            start_angle = 0
            end_angle = 180 + np.degrees(np.arctan(1/abs(x)))
        
        arcs.append({
            "center": (center_x, center_y),
            "radius": radius,
            "value": x,
            "start_angle": start_angle,
            "end_angle": end_angle
        })
    
    return arcs


def generate_smith_boundary() -> Dict[str, List[float]]:
    """Generate Smith chart unit circle boundary.
    
    Returns:
        Dictionary with x and y coordinates
    """
    theta = np.linspace(0, 2*np.pi, 200)
    x = np.cos(theta)
    y = np.sin(theta)
    
    return {"x": x.tolist(), "y": y.tolist()}


class SmithChartPlotter(BasePlotter):
    """Plotter for Smith charts."""
    
    def __init__(self, z0: float = 50.0, y0: Optional[float] = None, 
                 style: Optional[PlotStyle] = None):
        """Initialize Smith chart plotter.
        
        Args:
            z0: Reference impedance (Ohms)
            y0: Reference admittance (Siemens)
            style: Plot style configuration
        """
        super().__init__(style)
        self.z0 = z0
        self.y0 = y0 or (1 / z0)
    
    def draw_smith_grid(self, ax: plt.Axes, 
                       resistance_values: Optional[List[float]] = None,
                       reactance_values: Optional[List[float]] = None) -> None:
        """Draw Smith chart grid.
        
        Args:
            ax: Matplotlib axes
            resistance_values: Normalized resistance values for circles
            reactance_values: Normalized reactance values for arcs
        """
        # Default grid values
        if resistance_values is None:
            resistance_values = [0.2, 0.5, 1.0, 2.0, 5.0]
        if reactance_values is None:
            reactance_values = [-5, -2, -1, -0.5, -0.2, 0.2, 0.5, 1, 2, 5]
        
        # Draw resistance circles
        r_circles = generate_resistance_circles(resistance_values)
        for circle in r_circles:
            circ = patches.Circle(
                circle["center"], circle["radius"],
                fill=False, edgecolor='gray', linewidth=0.5, alpha=0.5
            )
            ax.add_patch(circ)
        
        # Draw reactance arcs
        x_arcs = generate_reactance_arcs(reactance_values)
        for arc in x_arcs:
            arc_patch = patches.Arc(
                arc["center"], 2*arc["radius"], 2*arc["radius"],
                angle=0, theta1=arc["start_angle"], theta2=arc["end_angle"],
                color='gray', linewidth=0.5, alpha=0.5
            )
            ax.add_patch(arc_patch)
        
        # Draw boundary circle
        boundary = generate_smith_boundary()
        ax.plot(boundary["x"], boundary["y"], 'k-', linewidth=2)
        
        # Draw horizontal axis (real axis)
        ax.plot([-1, 1], [0, 0], 'k-', linewidth=0.8)
    
    def draw_vswr_circles(self, ax: plt.Axes, vswr_values: List[float]) -> None:
        """Draw constant VSWR circles.
        
        Args:
            ax: Matplotlib axes
            vswr_values: VSWR values for circles
        """
        for vswr in vswr_values:
            # Calculate reflection coefficient magnitude from VSWR
            if vswr <= 1:
                continue
            gamma_mag = (vswr - 1) / (vswr + 1)
            
            # Draw circle
            circ = patches.Circle(
                (0, 0), gamma_mag,
                fill=False, edgecolor='blue', linewidth=1,
                linestyle='--', alpha=0.7
            )
            ax.add_patch(circ)
            
            # Add label
            ax.text(gamma_mag * 0.7, gamma_mag * 0.7, 
                   f'VSWR={vswr:.1f}',
                   fontsize=8, color='blue', alpha=0.7)
    
    def plot(self, impedances: np.ndarray, frequencies: np.ndarray,
            title: str = "Smith Chart",
            show_vswr_circles: bool = False,
            vswr_values: Optional[List[float]] = None,
            mark_frequencies: Optional[List[float]] = None) -> PlotResult:
        """Generate Smith chart plot.
        
        Args:
            impedances: Complex impedance array
            frequencies: Frequency array
            title: Plot title
            show_vswr_circles: Whether to show VSWR circles
            vswr_values: VSWR values for circles
            mark_frequencies: Frequencies to mark on plot
            
        Returns:
            PlotResult with Smith chart data
        """
        # Calculate reflection coefficients
        reflection_coeffs = impedance_to_reflection(impedances, self.z0)
        
        # Calculate VSWR
        vswr = np.array([calculate_vswr(g) for g in reflection_coeffs])
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.style.figure_size, dpi=self.style.dpi)
        
        # Draw Smith chart grid
        self.draw_smith_grid(ax)
        
        # Draw VSWR circles if requested
        if show_vswr_circles:
            if vswr_values is None:
                vswr_values = [1.5, 2.0, 3.0, 5.0]
            self.draw_vswr_circles(ax, vswr_values)
        
        # Plot impedance trajectory
        real_gamma = reflection_coeffs.real
        imag_gamma = reflection_coeffs.imag
        
        # Create color map based on frequency
        colors = plt.cm.viridis(np.linspace(0, 1, len(frequencies)))
        for i in range(len(frequencies) - 1):
            ax.plot(real_gamma[i:i+2], imag_gamma[i:i+2], 
                   color=colors[i], linewidth=self.style.line_width)
        
        # Mark specific frequencies
        marked_data = []
        if mark_frequencies:
            for freq in mark_frequencies:
                idx = np.argmin(np.abs(frequencies - freq))
                ax.plot(real_gamma[idx], imag_gamma[idx], 
                       'ro', markersize=self.style.marker_size)
                ax.annotate(f'{freq/1e6:.1f} MHz',
                          (real_gamma[idx], imag_gamma[idx]),
                          xytext=(5, 5), textcoords='offset points',
                          fontsize=self.style.font_size - 2)
                marked_data.append({
                    "frequency": freq,
                    "reflection": reflection_coeffs[idx],
                    "impedance": impedances[idx]
                })
        
        # Mark start and end points
        ax.plot(real_gamma[0], imag_gamma[0], 
               'go', markersize=self.style.marker_size, label='Start')
        ax.plot(real_gamma[-1], imag_gamma[-1], 
               'ro', markersize=self.style.marker_size, label='End')
        
        # Set labels and title
        ax.set_xlabel('Real(Γ)', fontsize=self.style.font_size)
        ax.set_ylabel('Imag(Γ)', fontsize=self.style.font_size)
        ax.set_title(title, fontsize=self.style.font_size + 2)
        
        # Set limits and aspect
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        ax.set_aspect('equal')
        
        # Add legend
        ax.legend(loc='upper left', fontsize=self.style.font_size - 2)
        
        # Prepare result data
        result_data = {
            "reflection_coefficients": reflection_coeffs,
            "impedances": impedances,
            "frequencies": frequencies,
            "vswr": vswr
        }
        
        # Metadata
        metadata = {}
        if show_vswr_circles:
            metadata["vswr_circles"] = vswr_values
        if mark_frequencies:
            metadata["marked_frequencies"] = marked_data
        metadata["reference_impedance"] = self.z0
        metadata["figure"] = fig
        
        return PlotResult(
            data=result_data,
            plot_type="smith_chart",
            title=title,
            metadata=metadata,
            export_formats=["png", "svg", "pdf"]
        )
    
    def plot_admittance(self, admittances: np.ndarray, frequencies: np.ndarray,
                       title: str = "Admittance Smith Chart") -> PlotResult:
        """Generate admittance Smith chart.
        
        Args:
            admittances: Complex admittance array
            frequencies: Frequency array
            title: Plot title
            
        Returns:
            PlotResult with admittance Smith chart data
        """
        # Convert admittances to impedances for plotting
        impedances = 1 / admittances
        
        # Use regular plot method
        result = self.plot(impedances, frequencies, title)
        
        # Update data and type
        result.data["admittances"] = admittances
        result.plot_type = "smith_chart_admittance"
        
        return result