"""Plot styling and theming configuration."""

from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict, Any


@dataclass
class PlotStyle:
    """Configuration for plot styling and theming."""
    
    # Figure settings
    figure_size: Tuple[float, float] = (10, 8)
    dpi: int = 100
    
    # Grid settings
    grid_alpha: float = 0.3
    grid_style: str = "-"
    
    # Line settings
    line_width: float = 2.0
    marker_size: float = 8.0
    
    # Font settings
    font_size: int = 12
    font_family: str = "sans-serif"
    
    # Theme
    theme: str = "default"
    
    # Interactive settings (for Plotly)
    hover_data: bool = False
    enable_zoom: bool = False
    
    @classmethod
    def professional(cls) -> "PlotStyle":
        """Create professional publication-quality style."""
        return cls(
            figure_size=(12, 9),
            dpi=300,
            grid_alpha=0.2,
            grid_style="--",
            line_width=2.5,
            font_size=14,
            font_family="serif",
            theme="professional"
        )
    
    @classmethod
    def interactive(cls) -> "PlotStyle":
        """Create interactive style for Plotly plots."""
        return cls(
            figure_size=(10, 8),
            dpi=100,
            theme="plotly_white",
            hover_data=True,
            enable_zoom=True
        )
    
    @classmethod
    def dark(cls) -> "PlotStyle":
        """Create dark theme style."""
        return cls(
            theme="dark",
            grid_alpha=0.2,
            grid_style=":"
        )
    
    def to_matplotlib_params(self) -> Dict[str, Any]:
        """Convert to matplotlib rcParams."""
        params = {
            "figure.figsize": self.figure_size,
            "figure.dpi": self.dpi,
            "axes.grid": True,
            "grid.alpha": self.grid_alpha,
            "grid.linestyle": self.grid_style,
            "lines.linewidth": self.line_width,
            "lines.markersize": self.marker_size,
            "font.size": self.font_size,
            "font.family": self.font_family,
        }
        
        if self.theme == "dark":
            params.update({
                "axes.facecolor": "#1e1e1e",
                "figure.facecolor": "#1e1e1e",
                "axes.edgecolor": "white",
                "text.color": "white",
                "axes.labelcolor": "white",
                "xtick.color": "white",
                "ytick.color": "white",
                "grid.color": "white"
            })
        
        return params
    
    def to_plotly_params(self) -> Dict[str, Any]:
        """Convert to Plotly template parameters."""
        template = self.theme if self.theme.startswith("plotly") else "plotly_white"
        
        return {
            "template": template,
            "width": self.figure_size[0] * 100,
            "height": self.figure_size[1] * 100,
            "hovermode": "closest" if self.hover_data else False,
            "dragmode": "zoom" if self.enable_zoom else "pan"
        }