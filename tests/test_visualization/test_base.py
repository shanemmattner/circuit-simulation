"""Tests for base visualization classes and utilities."""

import numpy as np


class TestPlotStyle:
    """Test PlotStyle configuration."""

    def test_default_style_creation(self):
        """Test creation of default plot style."""
        from src.circuit_sim.visualization.styles import PlotStyle

        style = PlotStyle()
        assert style.figure_size == (10, 8)
        assert style.dpi == 100
        assert style.grid_alpha == 0.3
        assert style.line_width == 2.0
        assert style.font_size == 12
        assert style.theme == "default"

    def test_professional_style(self):
        """Test professional style preset."""
        from src.circuit_sim.visualization.styles import PlotStyle

        style = PlotStyle.professional()
        assert style.dpi == 300
        assert style.grid_alpha == 0.2
        assert style.theme == "professional"
        assert style.font_family == "serif"

    def test_interactive_style(self):
        """Test interactive style for Plotly."""
        from src.circuit_sim.visualization.styles import PlotStyle

        style = PlotStyle.interactive()
        assert style.theme == "plotly_white"
        assert style.hover_data
        assert style.enable_zoom


class TestPlotResult:
    """Test PlotResult data structure."""

    def test_plot_result_creation(self):
        """Test creation of plot result."""
        from src.circuit_sim.visualization.base import PlotResult

        data = {"x": [1, 2, 3], "y": [4, 5, 6]}
        result = PlotResult(
            data=data, plot_type="test", title="Test Plot", metadata={"test": True}
        )

        assert result.data == data
        assert result.plot_type == "test"
        assert result.title == "Test Plot"
        assert result.metadata["test"]

    def test_plot_result_export_info(self):
        """Test plot result export information."""
        from src.circuit_sim.visualization.base import PlotResult

        result = PlotResult(
            data={"x": [1], "y": [2]},
            plot_type="bode",
            export_formats=["png", "svg", "html"],
        )

        assert "png" in result.export_formats
        assert "svg" in result.export_formats
        assert "html" in result.export_formats
        assert len(result.export_formats) == 3


class TestBasePlotter:
    """Test base plotter functionality."""

    def test_base_plotter_initialization(self):
        """Test base plotter initialization."""
        from src.circuit_sim.visualization.base import BasePlotter
        from src.circuit_sim.visualization.styles import PlotStyle

        plotter = BasePlotter()
        assert isinstance(plotter.style, PlotStyle)
        assert plotter.style.theme == "default"

    def test_base_plotter_with_custom_style(self):
        """Test base plotter with custom style."""
        from src.circuit_sim.visualization.base import BasePlotter
        from src.circuit_sim.visualization.styles import PlotStyle

        custom_style = PlotStyle(theme="dark", dpi=150)
        plotter = BasePlotter(style=custom_style)
        assert plotter.style.theme == "dark"
        assert plotter.style.dpi == 150

    def test_validate_data(self):
        """Test data validation in base plotter."""
        from src.circuit_sim.visualization.base import BasePlotter

        plotter = BasePlotter()

        # Valid data
        x = np.array([1, 2, 3])
        y = np.array([4, 5, 6])
        assert plotter.validate_data(x, y)

        # Invalid - different lengths
        x = np.array([1, 2, 3])
        y = np.array([4, 5])
        assert not plotter.validate_data(x, y)

        # Invalid - contains NaN
        x = np.array([1, np.nan, 3])
        y = np.array([4, 5, 6])
        assert not plotter.validate_data(x, y)

        # Invalid - contains Inf
        x = np.array([1, 2, 3])
        y = np.array([4, np.inf, 6])
        assert not plotter.validate_data(x, y)

    def test_format_label(self):
        """Test label formatting."""
        from src.circuit_sim.visualization.base import BasePlotter

        plotter = BasePlotter()

        # Test frequency formatting
        assert plotter.format_label(1000, "frequency") == "1.0 kHz"
        assert plotter.format_label(1e6, "frequency") == "1.0 MHz"
        assert plotter.format_label(1e9, "frequency") == "1.0 GHz"

        # Test magnitude formatting
        assert plotter.format_label(0.001, "magnitude") == "-60.0 dB"
        assert plotter.format_label(1.0, "magnitude") == "0.0 dB"
        assert plotter.format_label(10.0, "magnitude") == "20.0 dB"

        # Test phase formatting
        assert plotter.format_label(np.pi, "phase") == "180.0°"
        assert plotter.format_label(-np.pi / 2, "phase") == "-90.0°"
        assert plotter.format_label(0, "phase") == "0.0°"


class TestPlotUtils:
    """Test plotting utilities."""

    def test_create_grid_lines(self):
        """Test grid line generation."""
        from src.circuit_sim.visualization.plot_utils import create_grid_lines

        # Log scale grid
        lines = create_grid_lines(1, 1000, scale="log", num_lines=3)
        assert len(lines) == 3
        assert np.isclose(lines[0], 1)
        assert np.isclose(lines[-1], 1000)
        assert np.isclose(lines[1], 31.622776601683793)  # Geometric mean

        # Linear scale grid
        lines = create_grid_lines(0, 100, scale="linear", num_lines=5)
        assert len(lines) == 5
        assert lines[0] == 0
        assert lines[-1] == 100
        assert lines[2] == 50  # Linear midpoint

    def test_calculate_stability_margin(self):
        """Test stability margin calculations."""
        from src.circuit_sim.visualization.plot_utils import calculate_stability_margin

        # Create test transfer function data
        frequencies = np.logspace(0, 4, 100)
        # Stable system: -20dB/decade slope
        magnitude = 1.0 / frequencies
        phase = -np.pi / 2 * np.ones_like(frequencies)

        margins = calculate_stability_margin(magnitude, phase, frequencies)

        assert "gain_margin_db" in margins
        assert "phase_margin_deg" in margins
        assert "gain_crossover_freq" in margins
        assert "phase_crossover_freq" in margins
        assert margins["is_stable"]

    def test_color_palette(self):
        """Test color palette generation."""
        from src.circuit_sim.visualization.plot_utils import get_color_palette

        # Default palette
        colors = get_color_palette("default", 5)
        assert len(colors) == 5
        assert all(c.startswith("#") for c in colors)

        # Professional palette
        colors = get_color_palette("professional", 3)
        assert len(colors) == 3

        # Colorblind-safe palette
        colors = get_color_palette("colorblind", 4)
        assert len(colors) == 4
