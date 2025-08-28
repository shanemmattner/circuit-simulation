"""Base classes for visualization module."""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import numpy as np
from .styles import PlotStyle


@dataclass
class PlotResult:
    """Result container for generated plots."""

    data: Dict[str, Any]
    plot_type: str
    title: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    export_formats: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Initialize export formats if not provided."""
        if not self.export_formats:
            self.export_formats = ["png", "svg"]


class BasePlotter:
    """Base class for all plotters."""

    def __init__(self, style: Optional[PlotStyle] = None):
        """Initialize base plotter.

        Args:
            style: Plot style configuration
        """
        self.style = style or PlotStyle()

    def validate_data(self, x: np.ndarray, y: np.ndarray) -> bool:
        """Validate input data arrays.

        Args:
            x: X-axis data
            y: Y-axis data

        Returns:
            True if data is valid, False otherwise
        """
        # Check lengths match
        if len(x) != len(y):
            return False

        # Check for NaN values
        if np.any(np.isnan(x)) or np.any(np.isnan(y)):
            return False

        # Check for Inf values
        if np.any(np.isinf(x)) or np.any(np.isinf(y)):
            return False

        return True

    def format_label(self, value: float, label_type: str) -> str:
        """Format axis labels based on type.

        Args:
            value: Numeric value to format
            label_type: Type of label (frequency, magnitude, phase)

        Returns:
            Formatted label string
        """
        if label_type == "frequency":
            if value >= 1e9:
                return f"{value/1e9:.1f} GHz"
            elif value >= 1e6:
                return f"{value/1e6:.1f} MHz"
            elif value >= 1e3:
                return f"{value/1e3:.1f} kHz"
            else:
                return f"{value:.1f} Hz"

        elif label_type == "magnitude":
            # Convert to dB
            if value <= 0:
                return "-∞ dB"
            db_value = 20 * np.log10(value)
            return f"{db_value:.1f} dB"

        elif label_type == "phase":
            # Convert radians to degrees
            degrees = np.degrees(value)
            return f"{degrees:.1f}°"

        else:
            return str(value)
