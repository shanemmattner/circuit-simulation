"""
Tests for TransferFunction class - TDD approach.
"""

import numpy as np
import pytest

from circuit_sim.analysis.transfer_function import TransferFunction


class TestFactoryMethods:
    """Test factory methods for creating transfer functions."""

    def test_from_poles_zeros(self):
        """Test creating transfer function from poles and zeros."""
        # H(s) = k * (s - z1) / ((s - p1)(s - p2))
        poles = [-1, -2]
        zeros = [-3]
        gain = 2.0

        tf = TransferFunction.from_poles_zeros(poles, zeros, gain)

        # Check poles and zeros
        assert np.allclose(sorted(tf.poles.real), [-2, -1])
        assert np.allclose(tf.zeros.real, [-3])

        # Check DC gain: H(0) = 2 * (0 - (-3)) / ((0 - (-1))(0 - (-2))) = 2 * 3 / 2 = 3
        assert tf.dc_gain == pytest.approx(3.0)

    def test_from_poles_zeros_complex(self):
        """Test with complex conjugate poles."""
        poles = [-1 + 2j, -1 - 2j]  # Complex conjugate pair
        zeros = [0]  # Zero at origin
        gain = 5.0

        tf = TransferFunction.from_poles_zeros(poles, zeros, gain)

        # Verify poles are preserved
        assert len(tf.poles) == 2
        pole_real = tf.poles[0].real
        pole_imag = abs(tf.poles[0].imag)
        assert pole_real == pytest.approx(-1, rel=1e-6)
        assert pole_imag == pytest.approx(2, rel=1e-6)

        # Check that s=0 is a zero
        assert tf.evaluate(0) == pytest.approx(0)

    def test_from_poles_zeros_no_zeros(self):
        """Test creating transfer function with no zeros."""
        poles = [-10, -20]
        gain = 100

        tf = TransferFunction.from_poles_zeros(poles, [], gain)

        assert len(tf.zeros) == 0
        assert len(tf.poles) == 2
        # DC gain = 100 / (10 * 20) = 0.5
        assert tf.dc_gain == pytest.approx(0.5)

    def test_from_frequency_response(self):
        """Test creating transfer function from frequency response data."""
        # Create a known transfer function
        tf_original = TransferFunction([1], [1, 1])  # H(s) = 1/(s+1)

        # Generate frequency response
        frequencies = np.logspace(-2, 2, 50)  # 0.01 to 100 rad/s
        response = tf_original.frequency_response(frequencies)

        # Fit transfer function
        tf_fitted = TransferFunction.from_frequency_response(
            frequencies, response, order=1
        )

        # Check that fitted response matches original
        fitted_response = tf_fitted.frequency_response(frequencies)
        np.testing.assert_allclose(
            np.abs(fitted_response),
            np.abs(response),
            rtol=0.1,  # 10% tolerance for simple fitting
        )


class TestTransferFunctionBasics:
    """Test basic TransferFunction creation and properties."""

    def test_create_from_coefficients(self):
        """Test creating transfer function from polynomial coefficients."""
        # H(s) = (s + 1) / (s^2 + 3s + 2) = (s + 1) / ((s + 1)(s + 2))
        numerator = [1, 1]  # s + 1
        denominator = [1, 3, 2]  # s^2 + 3s + 2

        tf = TransferFunction(numerator, denominator)

        assert tf.numerator_coeffs == pytest.approx([1, 1])
        assert tf.denominator_coeffs == pytest.approx([1, 3, 2])
        assert tf.order == 2  # Order is denominator degree

    def test_invalid_coefficients(self):
        """Test that invalid coefficients raise appropriate errors."""
        with pytest.raises(ValueError, match="must be non-empty"):
            TransferFunction([], [1, 2])

        with pytest.raises(ValueError, match="must be non-empty"):
            TransferFunction([1], [])

        # All zeros in denominator
        with pytest.raises(ValueError, match="leading coefficient.*non-zero"):
            TransferFunction([1], [0, 0, 0])

    def test_normalize_coefficients(self):
        """Test that coefficients are normalized (leading denominator coeff = 1)."""
        numerator = [2, 4]  # 2(s + 2)
        denominator = [3, 9, 6]  # 3(s^2 + 3s + 2)

        tf = TransferFunction(numerator, denominator)

        # Should normalize by dividing by leading denominator coefficient (3)
        assert tf.numerator_coeffs == pytest.approx([2 / 3, 4 / 3])
        assert tf.denominator_coeffs == pytest.approx([1, 3, 2])

    def test_string_representation(self):
        """Test string representation of transfer function."""
        tf = TransferFunction([1, 2], [1, 3, 2])
        str_repr = str(tf)

        assert "Transfer Function" in str_repr
        assert "Order: 2" in str_repr


class TestPolynomialOperations:
    """Test polynomial evaluation and manipulation."""

    def test_evaluate_at_s(self):
        """Test evaluating H(s) at specific s values."""
        # H(s) = (s + 2) / (s + 1)
        tf = TransferFunction([1, 2], [1, 1])

        # H(0) = 2/1 = 2
        assert tf.evaluate(0) == pytest.approx(2.0)

        # H(-2) = 0 / (-1) = 0 (zero at s = -2)
        assert tf.evaluate(-2) == pytest.approx(0.0)

        # H(1j) = (1j + 2) / (1j + 1)
        h_at_j = tf.evaluate(1j)
        expected = (2 + 1j) / (1 + 1j)
        assert h_at_j == pytest.approx(expected)

    def test_evaluate_array(self):
        """Test evaluating H(s) at multiple s values."""
        tf = TransferFunction([1], [1, 1])  # H(s) = 1/(s+1)

        s_values = np.array([0, 1, -0.5, 1j])
        h_values = tf.evaluate(s_values)

        assert len(h_values) == 4
        assert h_values[0] == pytest.approx(1.0)  # H(0) = 1/1
        assert h_values[1] == pytest.approx(0.5)  # H(1) = 1/2
        assert h_values[2] == pytest.approx(2.0)  # H(-0.5) = 1/0.5

    def test_frequency_response(self):
        """Test computing frequency response H(jω)."""
        # First order lowpass: H(s) = 1/(s + 1)
        tf = TransferFunction([1], [1, 1])

        frequencies = np.array([0.1, 1, 10])  # rad/s
        response = tf.frequency_response(frequencies)

        # Check magnitude at ω=1 (should be -3dB = 1/sqrt(2))
        mag_at_1 = np.abs(response[1])
        assert mag_at_1 == pytest.approx(1 / np.sqrt(2), rel=0.01)

        # Check DC gain (ω→0)
        assert np.abs(response[0]) == pytest.approx(1.0, rel=0.01)


class TestTransferFunctionProperties:
    """Test additional transfer function properties."""

    def test_bandwidth(self):
        """Test bandwidth calculation for first-order system."""
        # H(s) = 10/(s + 10) has bandwidth at 10 rad/s
        tf = TransferFunction([10], [1, 10])

        assert tf.bandwidth == pytest.approx(10.0, rel=0.01)

    def test_bandwidth_second_order(self):
        """Test bandwidth for second-order system."""
        # Butterworth second-order with ωn = 1
        tf = TransferFunction([1], [1, np.sqrt(2), 1])

        # Bandwidth should be close to 1 rad/s
        assert tf.bandwidth == pytest.approx(1.0, rel=0.1)

    def test_is_stable(self):
        """Test stability check."""
        # Stable system (all poles in left half plane)
        tf_stable = TransferFunction([1], [1, 2, 1])  # Poles at -1
        assert tf_stable.is_stable is True

        # Unstable system (pole in right half plane)
        tf_unstable = TransferFunction([1], [1, -1])  # Pole at +1
        assert tf_unstable.is_stable is False

        # Marginally stable (pole on imaginary axis)
        tf_marginal = TransferFunction([1], [1, 0, 1])  # Poles at ±j
        assert tf_marginal.is_stable is False


class TestPoleZeroExtraction:
    """Test pole and zero identification."""

    def test_simple_poles(self):
        """Test extracting poles from denominator."""
        # (s + 1)(s + 2) = s^2 + 3s + 2
        tf = TransferFunction([1], [1, 3, 2])

        poles = tf.poles
        assert len(poles) == 2
        # Poles at s = -1 and s = -2
        assert sorted(poles.real) == pytest.approx([-2, -1])
        assert all(p.imag == 0 for p in poles)

    def test_complex_poles(self):
        """Test extracting complex conjugate poles."""
        # s^2 + 2s + 5 has poles at -1 ± 2j
        tf = TransferFunction([1], [1, 2, 5])

        poles = tf.poles
        assert len(poles) == 2
        assert poles[0].real == pytest.approx(-1)
        assert abs(poles[0].imag) == pytest.approx(2)
        # Check complex conjugate
        assert poles[0].conjugate() == pytest.approx(poles[1])

    def test_simple_zeros(self):
        """Test extracting zeros from numerator."""
        # (s + 3)(s - 1) = s^2 + 2s - 3
        tf = TransferFunction([1, 2, -3], [1, 0, 1])

        zeros = tf.zeros
        assert len(zeros) == 2
        assert sorted(zeros.real) == pytest.approx([-3, 1])

    def test_dc_gain(self):
        """Test DC gain calculation H(0)."""
        # H(s) = 10(s + 1) / (s + 2)
        tf = TransferFunction([10, 10], [1, 2])

        assert tf.dc_gain == pytest.approx(5.0)  # H(0) = 10*1/2 = 5

        # Test with zero at origin (DC gain = 0)
        tf_zero_dc = TransferFunction([1, 0], [1, 1])  # H(s) = s/(s+1)
        assert tf_zero_dc.dc_gain == pytest.approx(0.0)

    def test_no_zeros(self):
        """Test transfer function with no zeros."""
        tf = TransferFunction([5], [1, 2, 1])  # H(s) = 5/(s^2 + 2s + 1)

        zeros = tf.zeros
        assert len(zeros) == 0
        assert tf.dc_gain == pytest.approx(5.0)
