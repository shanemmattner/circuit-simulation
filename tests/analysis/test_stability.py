"""
Tests for stability analysis functionality.
"""

import numpy as np
import pytest

from circuit_sim.analysis import TransferFunction, StabilityMetrics


class TestStabilityAnalysis:
    """Test stability margin calculations."""

    def test_stable_system_margins(self):
        """Test stability margins for a stable system."""
        # Simple first-order system H(s) = 10/(s+1)
        tf = TransferFunction([10], [1, 1])

        margins = tf.stability_margins()

        assert isinstance(margins, StabilityMetrics)
        assert margins.is_stable is True
        # First-order system has infinite phase margin
        assert margins.phase_margin > 45  # Should be ~90 degrees

    def test_second_order_margins(self):
        """Test margins for second-order system."""
        # H(s) = 100/(s^2 + 10s + 100)
        tf = TransferFunction([100], [1, 10, 100])

        margins = tf.stability_margins()

        assert margins.is_stable is True
        assert margins.phase_margin > 0
        assert margins.gain_margin > 0

    def test_unstable_system(self):
        """Test detection of unstable system."""
        # Unstable: pole in right half-plane
        tf = TransferFunction([1], [1, -1])  # H(s) = 1/(s-1)

        assert tf.is_stable is False

        margins = tf.stability_margins()
        assert margins.is_stable is False


class TestTimeResponse:
    """Test time-domain response calculations."""

    def test_step_response_first_order(self):
        """Test step response of first-order system."""
        # H(s) = 1/(s+1) with time constant τ = 1
        tf = TransferFunction([1], [1, 1])

        time, response = tf.step_response()

        # Check array sizes match
        assert len(time) == len(response)

        # Check initial and final values
        assert response[0] == pytest.approx(0, abs=0.01)
        assert response[-1] == pytest.approx(1, rel=0.02)  # Within 2% of final value

        # Check time constant (63.2% of final value at t=1)
        t1_idx = np.argmin(np.abs(time - 1.0))
        assert response[t1_idx] == pytest.approx(0.632, rel=0.05)

    def test_rise_time(self):
        """Test rise time calculation."""
        # First-order system
        tf = TransferFunction([1], [1, 1])

        rise_time = tf.rise_time()

        # For H(s) = 1/(s+1), rise time ≈ 2.2 seconds
        assert rise_time == pytest.approx(2.2, rel=0.1)

    def test_settling_time(self):
        """Test settling time calculation."""
        tf = TransferFunction([1], [1, 1])

        settling_time = tf.settling_time(tolerance=0.02)

        # For 2% tolerance, settling time ≈ 4 time constants = 4 seconds
        assert settling_time == pytest.approx(4.0, rel=0.2)

    def test_overshoot(self):
        """Test overshoot calculation."""
        # First-order has no overshoot
        tf1 = TransferFunction([1], [1, 1])
        assert tf1.overshoot() == pytest.approx(0, abs=0.01)

        # Underdamped second-order has overshoot
        # H(s) = ωn²/(s² + 2ζωn*s + ωn²) with ζ = 0.3
        wn = 10  # Natural frequency
        zeta = 0.3  # Damping ratio (underdamped)
        tf2 = TransferFunction([wn**2], [1, 2 * zeta * wn, wn**2])

        overshoot = tf2.overshoot()
        # Theoretical overshoot for ζ=0.3 is about 37%
        assert overshoot == pytest.approx(37, rel=0.2)

    def test_impulse_response(self):
        """Test impulse response calculation."""
        tf = TransferFunction([1], [1, 1])

        time, response = tf.impulse_response()

        # For H(s) = 1/(s+1), impulse response is e^(-t)
        assert response[0] == pytest.approx(1.0, rel=0.1)

        # Check exponential decay
        t1_idx = np.argmin(np.abs(time - 1.0))
        assert response[t1_idx] == pytest.approx(np.exp(-1), rel=0.05)
