"""Tests for Nichols chart visualization."""

import numpy as np
import matplotlib.pyplot as plt


class TestNicholsChart:
    """Test Nichols chart functionality."""

    def test_nichols_plotter_initialization(self):
        """Test NicholsPlotter initialization."""
        from src.circuit_sim.visualization.advanced_plots import NicholsPlotter

        plotter = NicholsPlotter()
        assert plotter is not None
        assert plotter.style.theme == "default"

    def test_basic_nichols_plot(self):
        """Test basic Nichols chart generation."""
        from src.circuit_sim.visualization.advanced_plots import NicholsPlotter

        # Create test frequency response data
        frequencies = np.logspace(0, 3, 100)
        omega = 2 * np.pi * frequencies

        # Second-order system: H(jω) = ωn²/(s² + 2ζωns + ωn²)
        wn = 10  # Natural frequency
        zeta = 0.3  # Damping ratio
        s = 1j * omega
        transfer_function = wn**2 / (s**2 + 2 * zeta * wn * s + wn**2)

        plotter = NicholsPlotter()
        result = plotter.plot(
            transfer_function=transfer_function,
            frequencies=frequencies,
            title="Test Nichols Chart",
        )

        assert result is not None
        assert result.plot_type == "nichols"
        assert "magnitude_db" in result.data
        assert "phase_deg" in result.data
        assert len(result.data["magnitude_db"]) == len(transfer_function)
        plt.close("all")

    def test_nichols_with_grid(self):
        """Test Nichols chart with M and N circles."""
        from src.circuit_sim.visualization.advanced_plots import NicholsPlotter

        frequencies = np.logspace(-1, 2, 50)
        # Simple integrator response
        transfer_function = 1 / (1j * 2 * np.pi * frequencies)

        plotter = NicholsPlotter()
        result = plotter.plot(
            transfer_function=transfer_function,
            frequencies=frequencies,
            show_grid=True,
            m_circles=[0, 3, 6, 12],  # dB values
            n_circles=[30, 45, 60, 90],  # Phase values in degrees
        )

        assert "m_circles" in result.metadata
        assert "n_circles" in result.metadata
        assert result.metadata["m_circles"] == [0, 3, 6, 12]
        assert result.metadata["n_circles"] == [30, 45, 60, 90]
        plt.close("all")

    def test_nichols_stability_margins(self):
        """Test stability margin calculations on Nichols chart."""
        from src.circuit_sim.visualization.advanced_plots import NicholsPlotter

        frequencies = np.logspace(-1, 3, 200)
        omega = 2 * np.pi * frequencies

        # Third-order system with known margins
        # H(s) = K/(s(s+1)(s+10)) with K=5
        K = 5
        s = 1j * omega
        transfer_function = K / (s * (s + 1) * (s + 10))

        plotter = NicholsPlotter()
        result = plotter.plot(
            transfer_function=transfer_function,
            frequencies=frequencies,
            show_margins=True,
        )

        assert "stability_margins" in result.metadata
        margins = result.metadata["stability_margins"]
        assert "gain_margin_db" in margins
        assert "phase_margin_deg" in margins
        assert "gain_crossover_freq" in margins
        assert "phase_crossover_freq" in margins
        plt.close("all")

    def test_nichols_frequency_markers(self):
        """Test frequency marking on Nichols chart."""
        from src.circuit_sim.visualization.advanced_plots import NicholsPlotter

        frequencies = np.array([0.1, 1, 10, 100])
        omega = 2 * np.pi * frequencies
        transfer_function = 10 / (1j * omega * (1 + 1j * omega * 0.1))

        plotter = NicholsPlotter()
        result = plotter.plot(
            transfer_function=transfer_function,
            frequencies=frequencies,
            mark_frequencies=[0.1, 10, 100],
        )

        assert "marked_frequencies" in result.metadata
        assert len(result.metadata["marked_frequencies"]) == 3
        plt.close("all")

    def test_magnitude_phase_conversion(self):
        """Test magnitude and phase extraction."""
        from src.circuit_sim.visualization.advanced_plots import extract_magnitude_phase

        # Test complex numbers
        h = np.array([1 + 1j, 2 + 0j, 0 + 3j, -1 - 1j])

        mag_db, phase_deg = extract_magnitude_phase(h)

        # Check magnitude in dB
        expected_mag_db = 20 * np.log10([np.sqrt(2), 2, 3, np.sqrt(2)])
        assert np.allclose(mag_db, expected_mag_db)

        # Check phase in degrees
        expected_phase_deg = [45, 0, 90, -135]
        assert np.allclose(phase_deg, expected_phase_deg)

    def test_nichols_closed_loop_contours(self):
        """Test closed-loop magnitude contours."""
        from src.circuit_sim.visualization.advanced_plots import NicholsPlotter

        frequencies = np.logspace(-1, 2, 100)
        omega = 2 * np.pi * frequencies
        transfer_function = 1 / (1j * omega * (1 + 1j * omega * 0.01))

        plotter = NicholsPlotter()
        result = plotter.plot(
            transfer_function=transfer_function,
            frequencies=frequencies,
            show_closed_loop_contours=True,
            contour_values=[-3, 0, 3, 6, 12],  # dB values
        )

        assert "closed_loop_contours" in result.metadata
        assert result.metadata["closed_loop_contours"] == [-3, 0, 3, 6, 12]
        plt.close("all")


class TestNicholsGrid:
    """Test Nichols chart grid generation."""

    def test_m_circles_generation(self):
        """Test M-circles (constant magnitude) generation."""
        from src.circuit_sim.visualization.advanced_plots import generate_m_circles

        m_values = [0, 3, 6]  # dB values
        circles = generate_m_circles(m_values)

        assert len(circles) == len(m_values)

        for i, m_db in enumerate(m_values):
            circle = circles[i]
            assert "magnitude_db" in circle
            assert "phase_points" in circle
            assert "magnitude_points" in circle
            assert circle["magnitude_db"] == m_db

            # Check that points form a closed curve
            phase_points = np.array(circle["phase_points"])
            mag_points = np.array(circle["magnitude_points"])
            assert len(phase_points) == len(mag_points)
            assert len(phase_points) > 10  # Sufficient points

    def test_n_circles_generation(self):
        """Test N-circles (constant phase) generation."""
        from src.circuit_sim.visualization.advanced_plots import generate_n_circles

        n_values = [30, 45, 60]  # Degree values
        circles = generate_n_circles(n_values)

        assert len(circles) == len(n_values)

        for i, n_deg in enumerate(n_values):
            circle = circles[i]
            assert "phase_deg" in circle
            assert "phase_points" in circle
            assert "magnitude_points" in circle
            assert circle["phase_deg"] == n_deg

    def test_nichols_grid_coordinates(self):
        """Test Nichols chart grid coordinate system."""
        from src.circuit_sim.visualization.advanced_plots import nichols_to_bode

        # Test conversion from Nichols to Bode coordinates
        # Nichols: phase vs magnitude (dB)
        # Bode: frequency vs magnitude/phase

        phase_nichols = np.array([-180, -90, 0])
        magnitude_nichols = np.array([0, 6, -20])

        phase_bode, magnitude_bode = nichols_to_bode(phase_nichols, magnitude_nichols)

        assert np.array_equal(phase_bode, phase_nichols)
        assert np.array_equal(magnitude_bode, magnitude_nichols)

    def test_closed_loop_response_calculation(self):
        """Test closed-loop response from open-loop Nichols data."""
        from src.circuit_sim.visualization.advanced_plots import (
            calculate_closed_loop_response,
        )

        # Open-loop response
        ol_magnitude_db = np.array([20, 0, -20])  # dB
        ol_phase_deg = np.array([-90, -180, -270])  # degrees

        # Calculate closed-loop response: T = L/(1+L)
        cl_magnitude_db, cl_phase_deg = calculate_closed_loop_response(
            ol_magnitude_db, ol_phase_deg
        )

        assert len(cl_magnitude_db) == len(ol_magnitude_db)
        assert len(cl_phase_deg) == len(ol_phase_deg)

        # Check that closed-loop magnitude is finite
        assert np.all(np.isfinite(cl_magnitude_db))
        assert np.all(np.isfinite(cl_phase_deg))
