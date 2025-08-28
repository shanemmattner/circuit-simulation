"""Tests for Smith chart visualization."""

import numpy as np
import matplotlib.pyplot as plt


class TestSmithChartGrid:
    """Test Smith chart grid generation."""

    def test_resistance_circles(self):
        """Test generation of constant resistance circles."""
        from src.circuit_sim.visualization.smith_chart import (
            generate_resistance_circles,
        )

        # Generate circles for normalized resistances
        r_values = [0.5, 1.0, 2.0]
        circles = generate_resistance_circles(r_values)

        assert len(circles) == len(r_values)

        for i, r in enumerate(r_values):
            circle = circles[i]
            assert "center" in circle
            assert "radius" in circle
            assert "value" in circle

            # Check circle properties for normalized resistance r
            # Center should be at (r/(r+1), 0)
            expected_center = (r / (r + 1), 0)
            assert np.isclose(circle["center"][0], expected_center[0])
            assert np.isclose(circle["center"][1], expected_center[1])

            # Radius should be 1/(r+1)
            expected_radius = 1 / (r + 1)
            assert np.isclose(circle["radius"], expected_radius)

    def test_reactance_arcs(self):
        """Test generation of constant reactance arcs."""
        from src.circuit_sim.visualization.smith_chart import generate_reactance_arcs

        # Generate arcs for normalized reactances
        x_values = [-2, -1, 0, 1, 2]
        arcs = generate_reactance_arcs(x_values)

        assert len(arcs) == len(x_values) - 1  # x=0 is the horizontal axis

        for arc in arcs:
            assert "center" in arc
            assert "radius" in arc
            assert "value" in arc
            assert "start_angle" in arc
            assert "end_angle" in arc

    def test_smith_chart_boundary(self):
        """Test Smith chart unit circle boundary."""
        from src.circuit_sim.visualization.smith_chart import generate_smith_boundary

        boundary = generate_smith_boundary()

        assert "x" in boundary
        assert "y" in boundary

        # Check it's a unit circle
        x = np.array(boundary["x"])
        y = np.array(boundary["y"])
        radius = np.sqrt(x**2 + y**2)

        assert np.allclose(radius, 1.0, atol=1e-6)
        assert len(x) >= 100  # Sufficient points for smooth circle

    def test_impedance_to_reflection_coefficient(self):
        """Test impedance to reflection coefficient conversion."""
        from src.circuit_sim.visualization.smith_chart import impedance_to_reflection

        z0 = 50.0  # Reference impedance

        # Test matched impedance (Z = Z0)
        gamma = impedance_to_reflection(50 + 0j, z0)
        assert np.isclose(np.abs(gamma), 0.0)

        # Test open circuit (Z = ∞)
        gamma = impedance_to_reflection(1e10 + 0j, z0)
        assert np.isclose(np.abs(gamma), 1.0)
        assert np.isclose(np.angle(gamma), 0.0)

        # Test short circuit (Z = 0)
        gamma = impedance_to_reflection(0 + 0j, z0)
        assert np.isclose(np.abs(gamma), 1.0)
        assert np.isclose(np.abs(np.angle(gamma)), np.pi)

        # Test inductive impedance
        gamma = impedance_to_reflection(50 + 50j, z0)
        assert 0 < np.abs(gamma) < 1
        assert np.angle(gamma) > 0

        # Test capacitive impedance
        gamma = impedance_to_reflection(50 - 50j, z0)
        assert 0 < np.abs(gamma) < 1
        assert np.angle(gamma) < 0

    def test_reflection_to_impedance(self):
        """Test reflection coefficient to impedance conversion."""
        from src.circuit_sim.visualization.smith_chart import reflection_to_impedance

        z0 = 50.0

        # Test center (matched)
        z = reflection_to_impedance(0 + 0j, z0)
        assert np.isclose(z, z0)

        # Test right edge (open circuit)
        z = reflection_to_impedance(1 + 0j, z0)
        assert np.real(z) > 1e6  # Very large resistance

        # Test left edge (short circuit)
        z = reflection_to_impedance(-1 + 0j, z0)
        assert np.isclose(z, 0)

        # Test upper hemisphere (inductive)
        z = reflection_to_impedance(0.5j, z0)
        assert np.imag(z) > 0

        # Test lower hemisphere (capacitive)
        z = reflection_to_impedance(-0.5j, z0)
        assert np.imag(z) < 0


class TestSmithChartPlotter:
    """Test Smith chart plotter functionality."""

    def test_smith_chart_initialization(self):
        """Test SmithChartPlotter initialization."""
        from src.circuit_sim.visualization.smith_chart import SmithChartPlotter

        plotter = SmithChartPlotter()
        assert plotter.z0 == 50.0  # Default reference impedance

        plotter = SmithChartPlotter(z0=75.0)
        assert plotter.z0 == 75.0

    def test_basic_smith_chart_plot(self):
        """Test basic Smith chart plotting."""
        from src.circuit_sim.visualization.smith_chart import SmithChartPlotter

        # Create test impedance data
        frequencies = np.linspace(1e6, 100e6, 50)
        # Impedance varying from capacitive to inductive
        impedances = 50 + 1j * np.linspace(-30, 30, 50)

        plotter = SmithChartPlotter()
        result = plotter.plot(
            impedances=impedances, frequencies=frequencies, title="Test Smith Chart"
        )

        assert result is not None
        assert result.plot_type == "smith_chart"
        assert "reflection_coefficients" in result.data
        assert "impedances" in result.data
        assert len(result.data["reflection_coefficients"]) == len(impedances)
        plt.close("all")

    def test_smith_chart_with_vswr(self):
        """Test Smith chart with VSWR circles."""
        from src.circuit_sim.visualization.smith_chart import SmithChartPlotter

        frequencies = np.linspace(1e6, 10e6, 20)
        impedances = np.array([25, 50, 75, 100, 150]) + 0j
        impedances = np.repeat(impedances, 4)  # Repeat to match frequencies length

        plotter = SmithChartPlotter()
        result = plotter.plot(
            impedances=impedances,
            frequencies=frequencies[:20],
            show_vswr_circles=True,
            vswr_values=[1.5, 2.0, 3.0],
        )

        assert "vswr" in result.data
        assert "vswr_circles" in result.metadata
        assert len(result.metadata["vswr_circles"]) == 3

        # Check VSWR calculation
        vswr = result.data["vswr"]
        assert np.all(vswr >= 1.0)  # VSWR is always >= 1
        plt.close("all")

    def test_smith_chart_frequency_markers(self):
        """Test frequency marking on Smith chart."""
        from src.circuit_sim.visualization.smith_chart import SmithChartPlotter

        frequencies = np.array([1e6, 10e6, 50e6, 100e6])
        impedances = np.array([50 + 10j, 75 - 20j, 100 + 0j, 25 + 30j])

        plotter = SmithChartPlotter()
        result = plotter.plot(
            impedances=impedances,
            frequencies=frequencies,
            mark_frequencies=[1e6, 100e6],
        )

        assert "marked_frequencies" in result.metadata
        assert len(result.metadata["marked_frequencies"]) == 2
        plt.close("all")

    def test_smith_chart_admittance_mode(self):
        """Test Smith chart in admittance mode."""
        from src.circuit_sim.visualization.smith_chart import SmithChartPlotter

        frequencies = np.linspace(1e6, 10e6, 30)
        admittances = 1 / (50 + 1j * np.linspace(-20, 20, 30))

        plotter = SmithChartPlotter(y0=1 / 50.0)  # Reference admittance
        result = plotter.plot_admittance(
            admittances=admittances,
            frequencies=frequencies,
            title="Admittance Smith Chart",
        )

        assert result.plot_type == "smith_chart_admittance"
        assert "reflection_coefficients" in result.data
        assert "admittances" in result.data
        plt.close("all")

    def test_vswr_calculation(self):
        """Test VSWR calculation from reflection coefficient."""
        from src.circuit_sim.visualization.smith_chart import calculate_vswr

        # Perfect match (Γ = 0)
        vswr = calculate_vswr(0.0)
        assert np.isclose(vswr, 1.0)

        # Total reflection (|Γ| = 1)
        vswr = calculate_vswr(1.0)
        assert np.isinf(vswr)

        # Partial reflection
        vswr = calculate_vswr(0.5)
        assert np.isclose(vswr, 3.0)  # (1 + 0.5)/(1 - 0.5) = 3

        # Complex reflection coefficient
        gamma = 0.3 + 0.4j  # |Γ| = 0.5
        vswr = calculate_vswr(gamma)
        assert np.isclose(vswr, 3.0)

    def test_return_loss_calculation(self):
        """Test return loss calculation."""
        from src.circuit_sim.visualization.smith_chart import calculate_return_loss

        # Perfect match
        rl = calculate_return_loss(0.0)
        assert np.isinf(rl)  # Infinite return loss

        # Total reflection
        rl = calculate_return_loss(1.0)
        assert np.isclose(rl, 0.0)  # 0 dB return loss

        # -10 dB return loss (|Γ| = 0.316)
        gamma = 10 ** (-10 / 20)
        rl = calculate_return_loss(gamma)
        assert np.isclose(rl, 10.0, atol=0.01)
