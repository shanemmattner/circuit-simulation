"""Tests for Nyquist plot visualization."""

import numpy as np
import matplotlib.pyplot as plt


class TestNyquistPlotter:
    """Test Nyquist plot functionality."""

    def test_nyquist_plotter_initialization(self):
        """Test NyquistPlotter initialization."""
        from src.circuit_sim.visualization.advanced_plots import NyquistPlotter

        plotter = NyquistPlotter()
        assert plotter is not None
        assert plotter.style.theme == "default"

    def test_simple_nyquist_plot(self):
        """Test basic Nyquist plot generation."""
        from src.circuit_sim.visualization.advanced_plots import NyquistPlotter

        # Create test transfer function data (simple first-order system)
        frequencies = np.logspace(0, 4, 100)
        omega = 2 * np.pi * frequencies
        # H(jω) = 1/(1 + jωτ) with τ = 0.001
        tau = 0.001
        transfer_function = 1 / (1 + 1j * omega * tau)

        plotter = NyquistPlotter()
        result = plotter.plot(
            transfer_function=transfer_function,
            frequencies=frequencies,
            title="Test Nyquist Plot",
            show_stability=False,
        )

        assert result is not None
        assert result.plot_type == "nyquist"
        assert "real" in result.data
        assert "imag" in result.data
        assert len(result.data["real"]) == len(transfer_function)
        assert len(result.data["imag"]) == len(transfer_function)
        plt.close("all")

    def test_nyquist_with_stability_analysis(self):
        """Test Nyquist plot with stability analysis."""
        from src.circuit_sim.visualization.advanced_plots import NyquistPlotter

        # Create test transfer function with known stability
        frequencies = np.logspace(-1, 3, 200)
        omega = 2 * np.pi * frequencies

        # Stable system: H(jω) = K/(1 + jωτ)² with K=2, τ=0.01
        K = 2
        tau = 0.01
        transfer_function = K / (1 + 1j * omega * tau) ** 2

        plotter = NyquistPlotter()
        result = plotter.plot(
            transfer_function=transfer_function,
            frequencies=frequencies,
            title="Stable System",
            show_stability=True,
        )

        assert "stability_analysis" in result.metadata
        assert "encirclements" in result.metadata["stability_analysis"]
        assert "is_stable" in result.metadata["stability_analysis"]
        assert result.metadata["stability_analysis"]["is_stable"]
        plt.close("all")

    def test_nyquist_critical_point_marking(self):
        """Test that critical point (-1, 0) is marked."""
        from src.circuit_sim.visualization.advanced_plots import NyquistPlotter

        frequencies = np.logspace(0, 3, 50)
        transfer_function = np.ones(len(frequencies), dtype=complex)

        plotter = NyquistPlotter()
        result = plotter.plot(
            transfer_function=transfer_function,
            frequencies=frequencies,
            show_critical_point=True,
        )

        assert "critical_point" in result.metadata
        assert result.metadata["critical_point"] == (-1, 0)
        plt.close("all")

    def test_nyquist_negative_frequencies(self):
        """Test that negative frequencies are handled."""
        from src.circuit_sim.visualization.advanced_plots import NyquistPlotter

        # Only positive frequencies provided
        frequencies = np.logspace(0, 3, 50)
        omega = 2 * np.pi * frequencies
        transfer_function = 1 / (1 + 1j * omega * 0.01)

        plotter = NyquistPlotter()
        result = plotter.plot(
            transfer_function=transfer_function,
            frequencies=frequencies,
            include_negative_freq=True,
        )

        # Should have both positive and negative frequency data
        assert "real_neg" in result.data
        assert "imag_neg" in result.data
        # Negative frequency response should be complex conjugate
        assert np.allclose(result.data["real_neg"], result.data["real"])
        assert np.allclose(result.data["imag_neg"], -result.data["imag"])
        plt.close("all")

    def test_nyquist_with_unstable_system(self):
        """Test Nyquist plot for unstable system."""
        from src.circuit_sim.visualization.advanced_plots import NyquistPlotter

        # Create a system that definitely encircles (-1, 0)
        # Simple example: a circle of radius 2 centered at origin
        theta = np.linspace(0, 2 * np.pi, 300)
        real = 2 * np.cos(theta)
        imag = 2 * np.sin(theta)

        # Convert to transfer function format
        transfer_function = real + 1j * imag
        frequencies = np.linspace(1, 100, 300)

        plotter = NyquistPlotter()
        result = plotter.plot(
            transfer_function=transfer_function,
            frequencies=frequencies,
            show_stability=True,
        )

        # This system should be unstable (encircles -1)
        assert not result.metadata["stability_analysis"]["is_stable"]
        assert result.metadata["stability_analysis"]["encirclements"] == 1
        plt.close("all")

    def test_nyquist_frequency_markers(self):
        """Test frequency marking on Nyquist plot."""
        from src.circuit_sim.visualization.advanced_plots import NyquistPlotter

        frequencies = np.array([1, 10, 100, 1000])  # Specific frequencies
        omega = 2 * np.pi * frequencies
        transfer_function = 1 / (1 + 1j * omega * 0.01)

        plotter = NyquistPlotter()
        result = plotter.plot(
            transfer_function=transfer_function,
            frequencies=frequencies,
            mark_frequencies=[1, 100, 1000],
        )

        assert "marked_frequencies" in result.metadata
        assert len(result.metadata["marked_frequencies"]) == 3
        plt.close("all")

    def test_nyquist_export_formats(self):
        """Test that Nyquist plots support multiple export formats."""
        from src.circuit_sim.visualization.advanced_plots import NyquistPlotter

        frequencies = np.logspace(0, 2, 20)
        transfer_function = np.ones(len(frequencies), dtype=complex)

        plotter = NyquistPlotter()
        result = plotter.plot(transfer_function, frequencies)

        assert "png" in result.export_formats
        assert "svg" in result.export_formats
        plt.close("all")


class TestNyquistStabilityAnalysis:
    """Test Nyquist stability analysis functions."""

    def test_encirclement_counting(self):
        """Test encirclement counting algorithm."""
        from src.circuit_sim.visualization.advanced_plots import (
            count_encirclements_of_point,
        )

        # Create a circle around origin
        theta = np.linspace(0, 2 * np.pi, 100)
        real = np.cos(theta)
        imag = np.sin(theta)

        # Should encircle origin once
        count = count_encirclements_of_point(real, imag, 0, 0)
        assert count == 1

        # Should not encircle point (2, 0)
        count = count_encirclements_of_point(real, imag, 2, 0)
        assert count == 0

        # Should encircle point (-0.5, 0)
        real = 2 * np.cos(theta) - 0.5
        imag = 2 * np.sin(theta)
        count = count_encirclements_of_point(real, imag, -0.5, 0)
        assert count == 1

    def test_nyquist_criterion(self):
        """Test Nyquist stability criterion implementation."""
        from src.circuit_sim.visualization.advanced_plots import analyze_stability

        # Stable system (no encirclements of -1)
        theta = np.linspace(0, 2 * np.pi, 100)
        real = 0.5 * np.cos(theta) + 0.5  # Circle centered at (0.5, 0)
        imag = 0.5 * np.sin(theta)

        analysis = analyze_stability(real, imag, num_poles=0)
        assert analysis["is_stable"]
        assert analysis["encirclements"] == 0

        # Unstable system (encircles -1)
        real = 2 * np.cos(theta)  # Circle centered at origin with radius 2
        imag = 2 * np.sin(theta)

        analysis = analyze_stability(real, imag, num_poles=0)
        assert not analysis["is_stable"]
        assert analysis["encirclements"] == 1
