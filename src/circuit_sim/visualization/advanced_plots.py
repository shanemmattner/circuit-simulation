"""Advanced plotting functions for frequency domain analysis."""

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Dict, Any, List, Tuple
from .base import BasePlotter, PlotResult
from .styles import PlotStyle


def count_encirclements_of_point(
    real: np.ndarray, imag: np.ndarray, point_real: float, point_imag: float
) -> int:
    """Count encirclements of a point in the complex plane.

    Args:
        real: Real part of trajectory
        imag: Imaginary part of trajectory
        point_real: Real part of point
        point_imag: Imaginary part of point

    Returns:
        Number of counter-clockwise encirclements
    """
    # Shift trajectory relative to the point
    shifted_real = real - point_real
    shifted_imag = imag - point_imag

    # Calculate angles
    angles = np.arctan2(shifted_imag, shifted_real)

    # Unwrap angles to avoid discontinuities
    angles = np.unwrap(angles)

    # Total angle change divided by 2π gives encirclements
    total_angle_change = angles[-1] - angles[0]
    encirclements = int(np.round(total_angle_change / (2 * np.pi)))

    return encirclements


def analyze_stability(
    real: np.ndarray, imag: np.ndarray, num_poles: int = 0
) -> Dict[str, Any]:
    """Analyze stability using Nyquist criterion.

    Args:
        real: Real part of Nyquist plot
        imag: Imaginary part of Nyquist plot
        num_poles: Number of open-loop poles in right half-plane

    Returns:
        Stability analysis results
    """
    # Count encirclements of (-1, 0)
    encirclements = count_encirclements_of_point(real, imag, -1, 0)

    # Nyquist criterion: Z = N + P
    # Z = closed-loop poles in RHP (want 0 for stability)
    # N = encirclements of (-1, 0)
    # P = open-loop poles in RHP
    closed_loop_rhp_poles = encirclements + num_poles
    is_stable = closed_loop_rhp_poles == 0

    return {
        "encirclements": encirclements,
        "open_loop_rhp_poles": num_poles,
        "closed_loop_rhp_poles": closed_loop_rhp_poles,
        "is_stable": is_stable,
    }


class NyquistPlotter(BasePlotter):
    """Plotter for Nyquist diagrams."""

    def __init__(self, style: Optional[PlotStyle] = None):
        """Initialize Nyquist plotter.

        Args:
            style: Plot style configuration
        """
        super().__init__(style)

    def plot(
        self,
        transfer_function: np.ndarray,
        frequencies: np.ndarray,
        title: str = "Nyquist Plot",
        show_stability: bool = False,
        show_critical_point: bool = True,
        include_negative_freq: bool = True,
        mark_frequencies: Optional[List[float]] = None,
        num_open_loop_poles: int = 0,
    ) -> PlotResult:
        """Generate Nyquist plot.

        Args:
            transfer_function: Complex transfer function H(jω)
            frequencies: Frequency array (Hz)
            title: Plot title
            show_stability: Whether to perform stability analysis
            show_critical_point: Whether to mark (-1, 0)
            include_negative_freq: Whether to plot negative frequencies
            mark_frequencies: List of frequencies to mark on plot
            num_open_loop_poles: Number of open-loop RHP poles

        Returns:
            PlotResult with Nyquist plot data
        """
        # Extract real and imaginary parts
        real = transfer_function.real
        imag = transfer_function.imag

        # Validate data
        if not self.validate_data(real, imag):
            raise ValueError("Invalid data: contains NaN or Inf values")

        # Create figure
        fig, ax = plt.subplots(figsize=self.style.figure_size, dpi=self.style.dpi)

        # Plot positive frequency response
        ax.plot(real, imag, "b-", linewidth=self.style.line_width, label="H(jω)")

        # Plot negative frequency response (complex conjugate)
        if include_negative_freq:
            ax.plot(
                real,
                -imag,
                "b--",
                linewidth=self.style.line_width * 0.7,
                alpha=0.7,
                label="H(-jω)",
            )

        # Mark specific frequencies
        if mark_frequencies:
            marked_data = []
            for freq in mark_frequencies:
                idx = np.argmin(np.abs(frequencies - freq))
                ax.plot(real[idx], imag[idx], "ro", markersize=self.style.marker_size)
                ax.annotate(
                    f"{freq:.1f} Hz",
                    (real[idx], imag[idx]),
                    xytext=(5, 5),
                    textcoords="offset points",
                )
                marked_data.append(
                    {"frequency": freq, "real": real[idx], "imag": imag[idx]}
                )

        # Mark start and end points
        ax.plot(
            real[0], imag[0], "go", markersize=self.style.marker_size, label="Low freq"
        )
        ax.plot(
            real[-1],
            imag[-1],
            "ro",
            markersize=self.style.marker_size,
            label="High freq",
        )

        # Mark critical point (-1, 0)
        if show_critical_point:
            ax.plot(
                -1,
                0,
                "rx",
                markersize=self.style.marker_size * 1.5,
                markeredgewidth=3,
                label="Critical point",
            )
            ax.plot(
                -1,
                0,
                "ro",
                markersize=self.style.marker_size * 2,
                fillstyle="none",
                markeredgewidth=2,
            )

        # Set labels and title
        ax.set_xlabel("Real Part", fontsize=self.style.font_size)
        ax.set_ylabel("Imaginary Part", fontsize=self.style.font_size)
        ax.set_title(title, fontsize=self.style.font_size + 2)

        # Add grid
        ax.grid(True, alpha=self.style.grid_alpha, linestyle=self.style.grid_style)
        ax.axhline(y=0, color="k", linewidth=0.5)
        ax.axvline(x=0, color="k", linewidth=0.5)

        # Equal aspect ratio for proper circular shapes
        ax.set_aspect("equal", adjustable="box")

        # Add legend
        ax.legend(loc="best", fontsize=self.style.font_size - 2)

        # Prepare result data
        result_data = {"real": real, "imag": imag, "frequencies": frequencies}

        if include_negative_freq:
            result_data["real_neg"] = real
            result_data["imag_neg"] = -imag

        # Metadata
        metadata = {}
        if show_critical_point:
            metadata["critical_point"] = (-1, 0)

        if mark_frequencies:
            metadata["marked_frequencies"] = marked_data

        # Perform stability analysis if requested
        if show_stability:
            stability_analysis = analyze_stability(real, imag, num_open_loop_poles)
            metadata["stability_analysis"] = stability_analysis

            # Add stability info to plot
            stability_text = f"Stable: {stability_analysis['is_stable']}\n"
            stability_text += f"Encirclements: {stability_analysis['encirclements']}"
            ax.text(
                0.02,
                0.98,
                stability_text,
                transform=ax.transAxes,
                verticalalignment="top",
                bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
                fontsize=self.style.font_size - 1,
            )

        # Create PlotResult
        result = PlotResult(
            data=result_data,
            plot_type="nyquist",
            title=title,
            metadata=metadata,
            export_formats=["png", "svg", "pdf"],
        )

        # Store figure reference for export
        result.metadata["figure"] = fig

        return result


def extract_magnitude_phase(h: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Extract magnitude (dB) and phase (degrees) from complex response.

    Args:
        h: Complex frequency response array

    Returns:
        Tuple of (magnitude_db, phase_deg)
    """
    magnitude_db = 20 * np.log10(np.maximum(np.abs(h), 1e-10))
    phase_deg = np.degrees(np.angle(h))
    return magnitude_db, phase_deg


def generate_m_circles(m_values: List[float]) -> List[Dict[str, Any]]:
    """Generate M-circles (constant closed-loop magnitude) for Nichols chart.

    Args:
        m_values: Magnitude values in dB

    Returns:
        List of M-circle data
    """
    circles = []

    for m_db in m_values:
        # Convert dB to linear
        m_linear = 10 ** (m_db / 20)

        # Generate circle points
        # M-circles are circles in the open-loop plane that correspond to
        # constant closed-loop magnitude |T| = |L/(1+L)|

        if m_db == 0:  # 0 dB circle
            # Special case: passes through (-1, 0)
            phase_points = np.linspace(-180, 180, 360)
            magnitude_points = np.zeros_like(phase_points)
        else:
            # General M-circle equations
            phase_points = np.linspace(-180, 180, 360)
            phase_rad = np.radians(phase_points)

            # Calculate corresponding magnitude for each phase
            # This is derived from |L/(1+L)| = M
            if m_linear < 1:
                # For M < 1, circle exists
                magnitude_points = []
                for phi in phase_rad:
                    # Solve for |L| given phase and desired |T| = M
                    # Complex equation solving required
                    mag = m_linear / np.sqrt(
                        (1 - m_linear**2) * np.cos(phi) ** 2
                        + (m_linear * np.sin(phi)) ** 2
                    )
                    magnitude_points.append(20 * np.log10(max(mag, 1e-10)))
                magnitude_points = np.array(magnitude_points)
            else:
                # For M > 1, different calculation
                magnitude_points = np.full_like(phase_points, m_db)

        circles.append(
            {
                "magnitude_db": m_db,
                "phase_points": phase_points.tolist(),
                "magnitude_points": magnitude_points.tolist(),
            }
        )

    return circles


def generate_n_circles(n_values: List[float]) -> List[Dict[str, Any]]:
    """Generate N-circles (constant closed-loop phase) for Nichols chart.

    Args:
        n_values: Phase values in degrees

    Returns:
        List of N-circle data
    """
    circles = []

    for n_deg in n_values:
        # N-circles are curves of constant closed-loop phase
        magnitude_points = np.linspace(-40, 40, 200)  # dB range
        phase_points = []

        for mag_db in magnitude_points:
            # Calculate phase for constant closed-loop phase N
            # This involves solving arg(L/(1+L)) = N
            # Simplified approximation for demonstration
            phase = n_deg - mag_db * 0.1  # Simplified relationship
            phase_points.append(phase)

        circles.append(
            {
                "phase_deg": n_deg,
                "phase_points": phase_points,
                "magnitude_points": magnitude_points.tolist(),
            }
        )

    return circles


def nichols_to_bode(
    phase_nichols: np.ndarray, magnitude_nichols: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """Convert Nichols coordinates to Bode coordinates.

    Args:
        phase_nichols: Phase array (degrees)
        magnitude_nichols: Magnitude array (dB)

    Returns:
        Tuple of (phase_bode, magnitude_bode)
    """
    # For Nichols chart, the coordinates are already in Bode format
    return phase_nichols, magnitude_nichols


def calculate_closed_loop_response(
    ol_magnitude_db: np.ndarray, ol_phase_deg: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """Calculate closed-loop response from open-loop data.

    Args:
        ol_magnitude_db: Open-loop magnitude (dB)
        ol_phase_deg: Open-loop phase (degrees)

    Returns:
        Tuple of (cl_magnitude_db, cl_phase_deg)
    """
    # Convert to complex
    ol_linear = 10 ** (ol_magnitude_db / 20)
    ol_phase_rad = np.radians(ol_phase_deg)
    ol_complex = ol_linear * np.exp(1j * ol_phase_rad)

    # Calculate closed-loop: T = L/(1+L)
    cl_complex = ol_complex / (1 + ol_complex)

    # Convert back to magnitude and phase
    cl_magnitude_db = 20 * np.log10(np.maximum(np.abs(cl_complex), 1e-10))
    cl_phase_deg = np.degrees(np.angle(cl_complex))

    return cl_magnitude_db, cl_phase_deg


class NicholsPlotter(BasePlotter):
    """Plotter for Nichols charts."""

    def __init__(self, style: Optional[PlotStyle] = None):
        """Initialize Nichols plotter.

        Args:
            style: Plot style configuration
        """
        super().__init__(style)

    def plot(
        self,
        transfer_function: np.ndarray,
        frequencies: np.ndarray,
        title: str = "Nichols Chart",
        show_grid: bool = False,
        m_circles: Optional[List[float]] = None,
        n_circles: Optional[List[float]] = None,
        show_margins: bool = False,
        show_closed_loop_contours: bool = False,
        contour_values: Optional[List[float]] = None,
        mark_frequencies: Optional[List[float]] = None,
    ) -> PlotResult:
        """Generate Nichols chart.

        Args:
            transfer_function: Complex transfer function H(jω)
            frequencies: Frequency array (Hz)
            title: Plot title
            show_grid: Whether to show M and N circles
            m_circles: M-circle values (dB)
            n_circles: N-circle values (degrees)
            show_margins: Whether to calculate stability margins
            show_closed_loop_contours: Whether to show closed-loop contours
            contour_values: Contour magnitude values (dB)
            mark_frequencies: Frequencies to mark on plot

        Returns:
            PlotResult with Nichols chart data
        """
        # Extract magnitude and phase
        magnitude_db, phase_deg = extract_magnitude_phase(transfer_function)

        # Validate data
        if not self.validate_data(magnitude_db, phase_deg):
            raise ValueError("Invalid data: contains NaN or Inf values")

        # Create figure
        fig, ax = plt.subplots(figsize=self.style.figure_size, dpi=self.style.dpi)

        # Draw grid if requested
        if show_grid:
            if m_circles is None:
                m_circles = [-12, -6, -3, 0, 3, 6, 12]
            if n_circles is None:
                n_circles = [15, 30, 45, 60, 90, 120, 150]

            # Draw M-circles
            m_circle_data = generate_m_circles(m_circles)
            for circle in m_circle_data:
                ax.plot(
                    circle["phase_points"],
                    circle["magnitude_points"],
                    "g--",
                    alpha=0.3,
                    linewidth=0.8,
                )

            # Draw N-circles (simplified)
            n_circle_data = generate_n_circles(n_circles)
            for circle in n_circle_data:
                ax.plot(
                    circle["phase_points"],
                    circle["magnitude_points"],
                    "b--",
                    alpha=0.3,
                    linewidth=0.8,
                )

        # Plot main trace
        ax.plot(phase_deg, magnitude_db, "b-", linewidth=self.style.line_width)

        # Mark frequency points
        marked_data = []
        if mark_frequencies:
            for freq in mark_frequencies:
                idx = np.argmin(np.abs(frequencies - freq))
                ax.plot(
                    phase_deg[idx],
                    magnitude_db[idx],
                    "ro",
                    markersize=self.style.marker_size,
                )
                ax.annotate(
                    f"{freq:.1f} Hz",
                    (phase_deg[idx], magnitude_db[idx]),
                    xytext=(5, 5),
                    textcoords="offset points",
                    fontsize=self.style.font_size - 2,
                )
                marked_data.append(
                    {
                        "frequency": freq,
                        "magnitude_db": magnitude_db[idx],
                        "phase_deg": phase_deg[idx],
                    }
                )

        # Mark start and end points
        ax.plot(
            phase_deg[0],
            magnitude_db[0],
            "go",
            markersize=self.style.marker_size,
            label="Low freq",
        )
        ax.plot(
            phase_deg[-1],
            magnitude_db[-1],
            "ro",
            markersize=self.style.marker_size,
            label="High freq",
        )

        # Set labels and title
        ax.set_xlabel("Phase (degrees)", fontsize=self.style.font_size)
        ax.set_ylabel("Magnitude (dB)", fontsize=self.style.font_size)
        ax.set_title(title, fontsize=self.style.font_size + 2)

        # Add grid
        ax.grid(True, alpha=self.style.grid_alpha, linestyle=self.style.grid_style)

        # Set limits
        ax.set_xlim(-360, 0)
        ax.set_ylim(-40, 40)

        # Add legend
        ax.legend(loc="best", fontsize=self.style.font_size - 2)

        # Prepare result data
        result_data = {
            "magnitude_db": magnitude_db,
            "phase_deg": phase_deg,
            "frequencies": frequencies,
        }

        # Metadata
        metadata = {"figure": fig}

        if show_grid:
            metadata["m_circles"] = m_circles
            metadata["n_circles"] = n_circles

        if mark_frequencies:
            metadata["marked_frequencies"] = marked_data

        if show_margins:
            # Calculate stability margins
            from .plot_utils import calculate_stability_margin

            magnitude_linear = 10 ** (magnitude_db / 20)
            phase_rad = np.radians(phase_deg)
            margins = calculate_stability_margin(
                magnitude_linear, phase_rad, frequencies
            )
            metadata["stability_margins"] = margins

        if show_closed_loop_contours:
            if contour_values is None:
                contour_values = [-3, 0, 3, 6, 12]
            metadata["closed_loop_contours"] = contour_values

        return PlotResult(
            data=result_data,
            plot_type="nichols",
            title=title,
            metadata=metadata,
            export_formats=["png", "svg", "pdf"],
        )
