"""
Tests for the value parser module.
Following TDD - write tests first!
"""

import pytest
from pytest import approx

from circuit_sim.parser import parse_value


class TestValueParser:
    """Test parsing of human-readable values."""
    
    def test_parse_simple_numbers(self):
        """Test parsing plain numbers."""
        assert parse_value("10") == 10.0
        assert parse_value("3.14") == 3.14
        assert parse_value("0.001") == 0.001
        assert parse_value("1e3") == 1000.0
        assert parse_value("2.2e-6") == 2.2e-6
    
    def test_parse_resistor_values(self):
        """Test parsing common resistor values."""
        assert parse_value("1k") == 1000.0
        assert parse_value("10k") == 10000.0
        assert parse_value("4.7k") == 4700.0
        assert parse_value("1M") == 1e6
        assert parse_value("10M") == 10e6
        assert parse_value("100") == 100.0
        assert parse_value("47") == 47.0
        assert parse_value("2.2k") == 2200.0
    
    def test_parse_capacitor_values(self):
        """Test parsing common capacitor values."""
        assert parse_value("1u") == approx(1e-6)
        assert parse_value("10u") == approx(10e-6)
        assert parse_value("100n") == approx(100e-9)
        assert parse_value("1n") == approx(1e-9)
        assert parse_value("100p") == approx(100e-12)
        assert parse_value("1p") == approx(1e-12)
        assert parse_value("0.1u") == approx(0.1e-6)
        assert parse_value("22u") == approx(22e-6)
    
    def test_parse_inductor_values(self):
        """Test parsing common inductor values."""
        assert parse_value("1m") == approx(1e-3)
        assert parse_value("10m") == approx(10e-3)
        assert parse_value("100u") == approx(100e-6)
        assert parse_value("1u") == approx(1e-6)
        assert parse_value("1H") == approx(1.0)
        assert parse_value("100mH") == approx(0.1)
    
    def test_parse_voltage_values(self):
        """Test parsing voltage values."""
        assert parse_value("5V") == 5.0
        assert parse_value("3.3V") == 3.3
        assert parse_value("12V") == 12.0
        assert parse_value("-5V") == -5.0
        assert parse_value("1.8V") == 1.8
        assert parse_value("0V") == 0.0
    
    def test_parse_current_values(self):
        """Test parsing current values."""
        assert parse_value("10mA") == approx(10e-3)
        assert parse_value("1A") == approx(1.0)
        assert parse_value("50uA") == approx(50e-6)
        assert parse_value("100mA") == approx(100e-3)
        assert parse_value("2.5A") == approx(2.5)
    
    def test_case_insensitive(self):
        """Test that parsing is case-insensitive."""
        assert parse_value("1K") == parse_value("1k")
        assert parse_value("10M") == 10e6  # Capital M = mega
        assert parse_value("10m") == 10e-3  # lowercase m = milli
        assert parse_value("10MEG") == parse_value("10Meg") == 10e6  # MEG = mega
        assert parse_value("1U") == parse_value("1u")
    
    def test_whitespace_handling(self):
        """Test that whitespace is handled correctly."""
        assert parse_value(" 1k ") == approx(1000.0)
        assert parse_value("1 k") == approx(1000.0)
        assert parse_value(" 10 uF ") == approx(10e-6)
    
    def test_unit_variants(self):
        """Test different unit representations."""
        # Farads
        assert parse_value("10uF") == approx(10e-6)
        assert parse_value("10u") == approx(10e-6)  # u alone assumes Farads for caps
        
        # Ohms  
        assert parse_value("1kOhm") == approx(1000.0)
        assert parse_value("1kohm") == approx(1000.0)
        assert parse_value("1kΩ") == approx(1000.0)  # Unicode omega
        
        # Henries
        assert parse_value("10mH") == approx(10e-3)
    
    def test_edge_cases(self):
        """Test edge cases."""
        assert parse_value("0") == 0.0
        assert parse_value("0k") == 0.0
        assert parse_value(".1") == 0.1
        assert parse_value("1.") == 1.0
    
    def test_invalid_values(self):
        """Test that invalid values raise ValueError."""
        with pytest.raises(ValueError):
            parse_value("")
        
        with pytest.raises(ValueError):
            parse_value("abc")
        
        with pytest.raises(ValueError):
            parse_value("1X")  # Invalid suffix
        
        with pytest.raises(ValueError):
            parse_value("k10")  # Suffix before number
    
    def test_scientific_notation_with_suffix(self):
        """Test scientific notation combined with suffixes."""
        assert parse_value("1e3k") == 1e6  # 1e3 * 1k
        assert parse_value("2.2e-3M") == 2200.0  # 2.2e-3 * 1M