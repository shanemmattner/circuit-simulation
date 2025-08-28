"""Tests for interactive Plotly visualizations."""

import numpy as np


class TestInteractivePlotter:
    """Test interactive plotting with Plotly."""

    def test_interactive_plotter_initialization(self):
        """Test InteractivePlotter initialization."""
        from src.circuit_sim.visualization.interactive_plots import InteractivePlotter

        plotter = InteractivePlotter()
        assert plotter is not None
        assert plotter.theme == "plotly_white"

        plotter = InteractivePlotter(theme="plotly_dark")
        assert plotter.theme == "plotly_dark"

    def test_interactive_bode_plot_creation(self):
        """Test creation of interactive Bode plots."""
        from src.circuit_sim.visualization.interactive_plots import InteractivePlotter

        # Create test frequency response data
        frequencies = np.logspace(0, 4, 100)
        omega = 2 * np.pi * frequencies
        transfer_function = 1 / (1 + 1j * omega * 0.001)

        plotter = InteractivePlotter()
        html_output = plotter.create_bode_plot(
            frequencies=frequencies,
            transfer_function=transfer_function,
            title="Interactive Bode Plot Test",
        )

        assert isinstance(html_output, str)
        assert "plotly" in html_output.lower()
        assert "Interactive Bode Plot Test" in html_output
        assert len(html_output) > 1000  # Should be substantial HTML

    def test_interactive_nyquist_plot(self):
        """Test creation of interactive Nyquist plots."""
        from src.circuit_sim.visualization.interactive_plots import InteractivePlotter

        frequencies = np.logspace(0, 3, 50)
        omega = 2 * np.pi * frequencies
        transfer_function = 1 / (1 + 1j * omega * 0.01)

        plotter = InteractivePlotter()
        html_output = plotter.create_nyquist_plot(
            transfer_function=transfer_function,
            frequencies=frequencies,
            title="Interactive Nyquist Test",
        )

        assert isinstance(html_output, str)
        assert (
            "nyquist" in html_output.lower()
            or "Interactive Nyquist Test" in html_output
        )
        assert len(html_output) > 500

    def test_interactive_smith_chart(self):
        """Test creation of interactive Smith charts."""
        from src.circuit_sim.visualization.interactive_plots import InteractivePlotter

        frequencies = np.linspace(1e6, 100e6, 30)
        impedances = 50 + 1j * np.linspace(-25, 25, 30)

        plotter = InteractivePlotter()
        html_output = plotter.create_smith_chart(
            impedances=impedances,
            frequencies=frequencies,
            z0=50.0,
            title="Interactive Smith Chart Test",
        )

        assert isinstance(html_output, str)
        assert (
            "smith" in html_output.lower()
            or "Interactive Smith Chart Test" in html_output
        )
        assert len(html_output) > 500

    def test_plotly_hover_data(self):
        """Test that hover data is properly configured."""
        from src.circuit_sim.visualization.interactive_plots import InteractivePlotter

        frequencies = np.array([1, 10, 100, 1000])
        transfer_function = np.array([1 + 0j, 0.7 - 0.7j, 0.1 - 0.1j, 0.01 - 0.01j])

        plotter = InteractivePlotter()
        html_output = plotter.create_bode_plot(
            frequencies=frequencies,
            transfer_function=transfer_function,
            show_hover=True,
        )

        # Should contain hover template configuration
        assert "hovertemplate" in html_output.lower()
        assert len(html_output) > 800

    def test_plotly_theme_configuration(self):
        """Test different Plotly themes."""
        from src.circuit_sim.visualization.interactive_plots import InteractivePlotter

        frequencies = np.logspace(1, 3, 20)
        transfer_function = np.ones(20, dtype=complex)

        themes = ["plotly_white", "plotly_dark", "simple_white"]

        for theme in themes:
            plotter = InteractivePlotter(theme=theme)
            html_output = plotter.create_bode_plot(
                frequencies=frequencies, transfer_function=transfer_function
            )

            assert isinstance(html_output, str)
            assert len(html_output) > 500

    def test_plotly_export_configuration(self):
        """Test Plotly export button configuration."""
        from src.circuit_sim.visualization.interactive_plots import InteractivePlotter

        frequencies = np.logspace(0, 2, 30)
        transfer_function = 1 / (1j * 2 * np.pi * frequencies)

        plotter = InteractivePlotter()
        html_output = plotter.create_bode_plot(
            frequencies=frequencies,
            transfer_function=transfer_function,
            show_export_buttons=True,
        )

        # Should contain export/download functionality
        assert (
            "toImageButtonOptions" in html_output
            or "modeBarButtonsToAdd" in html_output
        )

    def test_multi_trace_plots(self):
        """Test plots with multiple traces."""
        from src.circuit_sim.visualization.interactive_plots import InteractivePlotter

        frequencies = np.logspace(0, 3, 50)
        omega = 2 * np.pi * frequencies

        # Multiple transfer functions
        tf1 = 1 / (1 + 1j * omega * 0.001)
        tf2 = 1 / (1 + 1j * omega * 0.01)
        tf3 = 1 / (1 + 1j * omega * 0.1)

        transfer_functions = {"τ = 1ms": tf1, "τ = 10ms": tf2, "τ = 100ms": tf3}

        plotter = InteractivePlotter()
        html_output = plotter.create_multi_trace_bode(
            frequencies=frequencies,
            transfer_functions=transfer_functions,
            title="Multi-Trace Bode Plot",
        )

        assert isinstance(html_output, str)
        # Check for presence of the traces (names may be encoded)
        assert "1ms" in html_output
        assert "10ms" in html_output
        assert "100ms" in html_output
        assert len(html_output) > 1200


class TestPlotlyUtilities:
    """Test Plotly utility functions."""

    def test_frequency_axis_formatting(self):
        """Test frequency axis formatting for log scale."""
        from src.circuit_sim.visualization.interactive_plots import (
            format_frequency_axis,
        )

        frequencies = np.array([1, 10, 100, 1000, 10000])

        formatted = format_frequency_axis(frequencies)

        assert "type" in formatted
        assert formatted["type"] == "log"
        assert "title" in formatted
        assert formatted["title"] == "Frequency (Hz)"

    def test_magnitude_phase_data_preparation(self):
        """Test data preparation for Bode plots."""
        from src.circuit_sim.visualization.interactive_plots import prepare_bode_data

        frequencies = np.logspace(0, 3, 100)
        omega = 2 * np.pi * frequencies
        transfer_function = 1 / (1 + 1j * omega * 0.01)

        mag_data, phase_data = prepare_bode_data(transfer_function, frequencies)

        assert "x" in mag_data and "y" in mag_data
        assert "x" in phase_data and "y" in phase_data
        assert len(mag_data["x"]) == len(frequencies)
        assert len(phase_data["x"]) == len(frequencies)

        # Check that magnitude is in dB
        assert np.all(mag_data["y"] <= 0)  # Should be <= 0 dB for this system

        # Check that phase is in degrees
        assert np.all(phase_data["y"] <= 0)  # Should be negative for this system
        assert np.all(phase_data["y"] >= -90)  # Should be >= -90° for first-order

    def test_smith_chart_data_preparation(self):
        """Test data preparation for Smith charts."""
        from src.circuit_sim.visualization.interactive_plots import prepare_smith_data

        frequencies = np.linspace(1e6, 100e6, 20)
        impedances = 50 + 1j * np.linspace(-30, 30, 20)

        smith_data = prepare_smith_data(impedances, frequencies, z0=50.0)

        assert "real" in smith_data and "imag" in smith_data
        assert "frequencies" in smith_data
        assert "vswr" in smith_data
        assert len(smith_data["real"]) == len(frequencies)
        assert len(smith_data["imag"]) == len(frequencies)

        # Check that reflection coefficients are within unit circle
        gamma_mag = np.sqrt(
            np.array(smith_data["real"]) ** 2 + np.array(smith_data["imag"]) ** 2
        )
        assert np.all(gamma_mag <= 1.0)

    def test_plotly_color_scheme(self):
        """Test color scheme generation for multiple traces."""
        from src.circuit_sim.visualization.interactive_plots import get_plotly_colors

        colors_3 = get_plotly_colors(3)
        colors_10 = get_plotly_colors(10)

        assert len(colors_3) == 3
        assert len(colors_10) == 10

        # Colors should be valid CSS colors or hex
        for color in colors_3:
            assert isinstance(color, str)
            assert len(color) > 0

    def test_hover_template_generation(self):
        """Test hover template generation."""
        from src.circuit_sim.visualization.interactive_plots import (
            create_hover_template,
        )

        # Bode magnitude template
        template_mag = create_hover_template("magnitude")
        assert "Frequency" in template_mag
        assert "Magnitude" in template_mag
        assert "dB" in template_mag

        # Bode phase template
        template_phase = create_hover_template("phase")
        assert "Frequency" in template_phase
        assert "Phase" in template_phase
        assert "°" in template_phase

        # Nyquist template
        template_nyquist = create_hover_template("nyquist")
        assert "Real" in template_nyquist
        assert "Imag" in template_nyquist

        # Smith chart template
        template_smith = create_hover_template("smith")
        assert "VSWR" in template_smith or "Impedance" in template_smith
