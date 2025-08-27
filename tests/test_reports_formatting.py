"""
Test cases for report formatting utilities.

Tests value formatting, unit conversions, and display formatting functions.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from circuit_sim.reports.utils.formatting import (
    format_value,
    format_units,
    format_percentage,
    format_scientific,
    format_time_duration,
    format_frequency,
    format_table_value
)


class TestFormatting:
    """Test the formatting utility functions."""

    def test_format_value_basic(self):
        """Test basic value formatting."""
        assert format_value(1.5, 'V') == "1.500 V"
        assert format_value(0, 'A') == "0.000 A"
        assert format_value(5) == "5.000 "

    def test_format_value_si_prefixes(self):
        """Test SI prefix formatting."""
        assert format_value(0.001, 'V') == "1.000 mV"
        assert format_value(1500, 'Ω') == "1.500 kΩ"
        assert format_value(1e6, 'Hz') == "1.000 MHz"
        assert format_value(1e-6, 'F') == "1.000 μF"
        assert format_value(1e-9, 'H') == "1.000 nH"
        assert format_value(1e-12, 'F') == "1.000 pF"

    def test_format_value_precision(self):
        """Test precision handling."""
        assert format_value(1.23456, 'V', precision=2) == "1.23 V"
        assert format_value(123.456, 'mA', precision=4) == "123.4560 mA"
        
    def test_format_value_large_numbers(self):
        """Test large number formatting."""
        assert format_value(1234, 'Ω') == "1.234 kΩ"
        assert format_value(1234000, 'Hz') == "1.234 MHz"
        
    def test_format_value_small_numbers(self):
        """Test very small number formatting."""
        assert format_value(1e-15, 'F') == "1.000 fF"
        assert format_value(1e-18, 'A') == "1.000e-18 A"  # Fallback to scientific

    def test_format_value_string_input(self):
        """Test string input handling."""
        assert format_value("5V") == "5V"
        assert format_value("test", "unit") == "test"

    def test_format_value_negative(self):
        """Test negative value formatting."""
        assert format_value(-1.5, 'V') == "-1.500 V"
        assert format_value(-0.001, 'A') == "-1.000 mA"

    def test_format_units(self):
        """Test unit symbol formatting."""
        assert format_units('ohm') == 'Ω'
        assert format_units('Ohms') == 'Ω'
        assert format_units('micro') == 'μ'
        assert format_units('degrees') == '°'
        assert format_units('percent') == '%'
        assert format_units('unknown') == 'unknown'

    def test_format_percentage(self):
        """Test percentage formatting."""
        assert format_percentage(0.85) == "85.0%"
        assert format_percentage(0.8534, 2) == "85.34%"
        assert format_percentage(1.25) == "125.0%"
        assert format_percentage(0) == "0.0%"

    def test_format_scientific(self):
        """Test scientific notation formatting."""
        assert format_scientific(0.00123) == "1.23 × 10⁻³"
        assert format_scientific(4567000) == "4.57 × 10⁶"
        assert format_scientific(0) == "0"
        assert format_scientific(1.0) == "1.00"
        assert format_scientific(-0.00456) == "-4.56 × 10⁻³"

    def test_format_time_duration(self):
        """Test time duration formatting."""
        assert format_time_duration(0.00123) == "1.230 ms"
        assert format_time_duration(0.000001) == "1.000 μs"
        assert format_time_duration(0.000000001) == "1.000 ns"
        assert format_time_duration(1.5) == "1.500 s"
        assert format_time_duration(75.5) == "1m 15.5s"
        assert format_time_duration(3661.5) == "1h 1m 1.5s"

    def test_format_frequency(self):
        """Test frequency formatting."""
        assert format_frequency(1000) == "1.000 kHz"
        assert format_frequency(2.4e9) == "2.400 GHz"
        assert format_frequency(50) == "50.000 Hz"

    def test_format_table_value(self):
        """Test table value formatting."""
        assert format_table_value(None) == "N/A"
        assert format_table_value("text") == "text"
        assert format_table_value(1.234, "V") == "1.234 V"
        assert format_table_value(0.001234, "A") == "1.234 mA"
        assert format_table_value(1234567) == "1.23e+06"
        assert format_table_value(0.123) == "0.123"

    def test_format_table_value_no_unit(self):
        """Test table value formatting without units."""
        assert format_table_value(1.234) == "1.234"
        assert format_table_value(0.0001234) == "1.23e-04"

    @pytest.mark.parametrize("value,unit,expected", [
        (1000, "V", "1.000 kV"),
        (0.001, "A", "1.000 mA"),
        (1e6, "Ω", "1.000 MΩ"),
        (47e-12, "F", "47.000 pF"),
        (2.2e-3, "H", "2.200 mH"),
    ])
    def test_format_value_parametrized(self, value, unit, expected):
        """Test various value/unit combinations."""
        assert format_value(value, unit) == expected

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Very large numbers
        assert "T" in format_value(1e12, "Hz")  # Should use Tera prefix
        
        # Boundary values for SI prefixes
        assert format_value(999, "Hz") == "999.000 Hz"  # Just below kilo
        assert format_value(1001, "Hz") == "1.001 kHz"  # Just above kilo
        
        # Zero handling
        assert format_value(0.0, "V") == "0.000 V"
        assert format_value(-0.0, "A") == "0.000 A"