"""Tests for Thevenin and Norton equivalent circuit analysis."""

import pytest
from src.circuit_sim.analysis.thevenin import (
    calculate_norton_from_thevenin,
    TheveninResult,
)


class TestCalculateNortonFromThevenin:
    """Tests for calculate_norton_from_thevenin function."""

    def test_basic_calculation(self):
        """Test basic In = Vth / Rth calculation."""
        # 10V / 1000Ω = 10mA
        result = calculate_norton_from_thevenin(10.0, 1000.0)
        assert result == 0.01  # 10mA

    def test_voltage_divider_example(self):
        """Test with voltage divider values: Vth=5V, Rth=500Ω -> In=10mA."""
        result = calculate_norton_from_thevenin(5.0, 500.0)
        assert result == 0.01  # 10mA

    def test_low_resistance(self):
        """Test with low resistance: 1V / 10Ω = 100mA."""
        result = calculate_norton_from_thevenin(1.0, 10.0)
        assert result == 0.1  # 100mA

    def test_high_resistance(self):
        """Test with high resistance: 100V / 1MΩ = 100μA."""
        result = calculate_norton_from_thevenin(100.0, 1_000_000.0)
        assert result == 0.0001  # 100μA

    def test_negative_voltage(self):
        """Test with negative voltage (direction reversal)."""
        result = calculate_norton_from_thevenin(-5.0, 1000.0)
        assert result == -0.005  # -5mA

    def test_zero_voltage(self):
        """Test with zero voltage."""
        result = calculate_norton_from_thevenin(0.0, 1000.0)
        assert result == 0.0

    def test_zero_resistance_raises_error(self):
        """Test that zero resistance raises ValueError."""
        with pytest.raises(ValueError, match="cannot be zero"):
            calculate_norton_from_thevenin(5.0, 0.0)

    def test_floating_point_precision(self):
        """Test with realistic floating point values."""
        result = calculate_norton_from_thevenin(3.3, 470.0)
        expected = 3.3 / 470.0
        assert abs(result - expected) < 1e-10


class TestTheveninResult:
    """Tests for TheveninResult dataclass."""

    def test_in_value_property_with_vth(self):
        """Test in_value property when Vth is available."""
        result = TheveninResult(rth=1000.0, vth=10.0, terminals=(1, 0))
        assert result.in_value == 0.01  # 10mA

    def test_in_value_property_without_vth(self):
        """Test in_value property when Vth is None."""
        result = TheveninResult(rth=1000.0, vth=None, terminals=(1, 0))
        assert result.in_value is None

    def test_in_value_zero_voltage(self):
        """Test in_value property with zero voltage."""
        result = TheveninResult(rth=1000.0, vth=0.0, terminals=(1, 0))
        assert result.in_value == 0.0
