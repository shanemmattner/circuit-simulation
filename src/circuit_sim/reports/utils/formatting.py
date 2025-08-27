"""
Formatting utilities for circuit analysis reports.

This module provides functions for formatting numerical values,
units, and other display elements in reports.
"""

from typing import Union, Optional
import math


def format_value(value: Union[float, int, str], unit: Optional[str] = None, precision: int = 3) -> str:
    """
    Format a numerical value with appropriate SI prefix and unit.

    Args:
        value: Numerical value to format
        unit: Unit symbol (e.g., 'V', 'A', 'Ω', 'F', 'H')
        precision: Number of significant digits

    Returns:
        Formatted string with value, prefix, and unit

    Examples:
        >>> format_value(0.001, 'V')
        '1.000 mV'
        >>> format_value(1500, 'Ω')
        '1.500 kΩ'
        >>> format_value(1e-6, 'F')
        '1.000 μF'
    """
    if isinstance(value, str):
        return value
    
    if value == 0:
        if unit:
            return f"0.000 {unit}"
        else:
            return "0.000 "

    # SI prefixes (power of 10)
    si_prefixes = [
        (1e12, 'T'),   # Tera
        (1e9, 'G'),    # Giga
        (1e6, 'M'),    # Mega
        (1e3, 'k'),    # Kilo
        (1, ''),       # Base unit
        (1e-3, 'm'),   # Milli
        (1e-6, 'μ'),   # Micro
        (1e-9, 'n'),   # Nano
        (1e-12, 'p'),  # Pico
        (1e-15, 'f'),  # Femto
    ]

    abs_value = abs(value)
    
    # Find appropriate SI prefix
    for scale, prefix in si_prefixes:
        if abs_value >= scale:
            scaled_value = value / scale
            
            # Format with specified precision - always use full precision for consistency
            formatted = f"{scaled_value:.{precision}f}"
            
            # Build final string
            result = formatted
            if prefix:
                result += f" {prefix}"
                if unit:
                    result += unit
            else:
                if unit:
                    result += f" {unit}"
                else:
                    result += " "
            
            return result
    
    # Fallback for very small values
    formatted = f"{value:.{precision}e}"
    if unit:
        formatted += f" {unit}"
    return formatted


def format_units(unit: str) -> str:
    """
    Format unit symbols with proper typography.

    Args:
        unit: Unit string to format

    Returns:
        Properly formatted unit string

    Examples:
        >>> format_units('ohm')
        'Ω'
        >>> format_units('micro')
        'μ'
        >>> format_units('degrees')
        '°'
    """
    unit_map = {
        'ohm': 'Ω',
        'ohms': 'Ω',
        'micro': 'μ',
        'mu': 'μ',
        'degrees': '°',
        'degree': '°',
        'deg': '°',
        'celsius': '°C',
        'fahrenheit': '°F',
        'percent': '%',
        'pi': 'π',
    }
    
    return unit_map.get(unit.lower(), unit)


def format_percentage(value: float, decimal_places: int = 1) -> str:
    """
    Format a decimal value as a percentage.

    Args:
        value: Decimal value (e.g., 0.85 for 85%)
        decimal_places: Number of decimal places in percentage

    Returns:
        Formatted percentage string

    Examples:
        >>> format_percentage(0.8534)
        '85.3%'
        >>> format_percentage(0.8534, 2)
        '85.34%'
    """
    percentage = value * 100
    return f"{percentage:.{decimal_places}f}%"


def format_scientific(value: Union[float, int], precision: int = 2) -> str:
    """
    Format a number in scientific notation.

    Args:
        value: Numerical value
        precision: Number of decimal places in mantissa

    Returns:
        Scientific notation string

    Examples:
        >>> format_scientific(0.00123)
        '1.23 × 10⁻³'
        >>> format_scientific(4567000)
        '4.57 × 10⁶'
    """
    if value == 0:
        return "0"
    
    exponent = int(math.floor(math.log10(abs(value))))
    mantissa = value / (10 ** exponent)
    
    # Use proper multiplication and superscript symbols
    if exponent == 0:
        return f"{mantissa:.{precision}f}"
    elif exponent > 0:
        exp_str = ''.join('⁰¹²³⁴⁵⁶⁷⁸⁹'[int(d)] for d in str(exponent))
    else:
        exp_str = '⁻' + ''.join('⁰¹²³⁴⁵⁶⁷⁸⁹'[int(d)] for d in str(-exponent))
    
    return f"{mantissa:.{precision}f} × 10{exp_str}"


def format_time_duration(seconds: float) -> str:
    """
    Format time duration in human-readable format.

    Args:
        seconds: Time duration in seconds

    Returns:
        Formatted time string

    Examples:
        >>> format_time_duration(0.00123)
        '1.23 ms'
        >>> format_time_duration(75.5)
        '1m 15.5s'
    """
    if seconds < 1e-6:
        return format_value(seconds * 1e9, 'ns')
    elif seconds < 1e-3:
        return format_value(seconds * 1e6, 'μs')
    elif seconds < 1:
        return format_value(seconds * 1e3, 'ms')
    elif seconds < 60:
        return format_value(seconds, 's')
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"
    else:
        hours = int(seconds // 3600)
        remaining_minutes = int((seconds % 3600) // 60)
        remaining_seconds = seconds % 60
        return f"{hours}h {remaining_minutes}m {remaining_seconds:.1f}s"


def format_frequency(freq_hz: float) -> str:
    """
    Format frequency values with appropriate units.

    Args:
        freq_hz: Frequency in Hz

    Returns:
        Formatted frequency string

    Examples:
        >>> format_frequency(1500)
        '1.500 kHz'
        >>> format_frequency(2.4e9)
        '2.400 GHz'
    """
    return format_value(freq_hz, 'Hz')


def format_table_value(value: Union[float, int, str, None], unit: Optional[str] = None) -> str:
    """
    Format values for display in tables with consistent width.

    Args:
        value: Value to format
        unit: Optional unit

    Returns:
        Formatted string suitable for table display
    """
    if value is None:
        return "N/A"
    
    if isinstance(value, str):
        return value
    
    if isinstance(value, (int, float)):
        if unit:
            return format_value(value, unit, precision=3)
        else:
            if abs(value) >= 1000 or abs(value) < 0.001:
                return f"{value:.2e}"
            else:
                return f"{value:.3f}"
    
    return str(value)