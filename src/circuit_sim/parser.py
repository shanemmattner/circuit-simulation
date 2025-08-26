"""
Value parser for human-readable electronic component values.

This module converts strings like "1k", "10uF", "3.3V" to numeric values.
"""

import re
from typing import Dict

# Define unit multipliers
MULTIPLIERS: Dict[str, float] = {
    # Standard SI prefixes
    "T": 1e12,  # tera
    "G": 1e9,  # giga
    "MEG": 1e6,  # mega (alternative)
    "M": 1e6,  # mega (but also milli context-dependent)
    "k": 1e3,  # kilo
    "K": 1e3,  # kilo (alternative)
    # Base unit (no prefix)
    "": 1,
    # Sub-unit prefixes
    "m": 1e-3,  # milli
    "u": 1e-6,  # micro (μ)
    "μ": 1e-6,  # micro (unicode)
    "n": 1e-9,  # nano
    "p": 1e-12,  # pico
    "f": 1e-15,  # femto
}

# Units that can be ignored (they don't affect the value)
UNIT_SUFFIXES = {
    "F",
    "FARAD",
    "FARADS",  # Capacitance
    "H",
    "HENRY",
    "HENRIES",  # Inductance
    "OHM",
    "OHMS",
    "Ω",  # Resistance
    "V",
    "VOLT",
    "VOLTS",  # Voltage
    "A",
    "AMP",
    "AMPS",
    "AMPERE",
    "AMPERES",  # Current
    "HZ",
    "HERTZ",  # Frequency
    "S",
    "SEC",
    "SECOND",
    "SECONDS",  # Time
}


def parse_value(value_str: str) -> float:
    """
    Parse a human-readable value string to a float.

    Handles common electronic component notation:
    - Resistors: "1k", "10M", "4.7k"
    - Capacitors: "10u", "100n", "1p"
    - Inductors: "1m", "100u", "10n"
    - Voltages: "5V", "3.3V", "-12V"
    - Currents: "10mA", "1A", "50uA"

    Args:
        value_str: String representation of the value

    Returns:
        Numeric value as a float

    Raises:
        ValueError: If the string cannot be parsed

    Examples:
        >>> parse_value("1k")
        1000.0
        >>> parse_value("10uF")
        1e-05
        >>> parse_value("3.3V")
        3.3
    """
    if not value_str:
        raise ValueError("Empty value string")

    # Clean up the string
    original = value_str
    value_str = value_str.strip().replace(" ", "")

    # Special case for "MEG" (mega) vs "M" (which could be mega or milli)
    # In electronics, standalone M usually means mega for resistors
    # But mH means millihenries, mA means milliamps
    value_str = re.sub(r"(\d)MEG", r"\1M", value_str, flags=re.IGNORECASE)

    # Regular expression to parse the value
    # Matches: optional sign, number (int or float, optional scientific), optional multiplier, optional unit
    pattern = r"^([+-]?)(\d+\.?\d*|\d*\.\d+)([eE][+-]?\d+)?([TGMKkmunpfuμ]?)([a-zA-ZΩ]*)$"

    match = re.match(pattern, value_str, re.IGNORECASE)

    if not match:
        raise ValueError(f"Cannot parse value: '{original}'")

    sign, number, exponent, multiplier, unit = match.groups()

    # Parse the numeric part
    try:
        if exponent:
            numeric_value = float(number + exponent)
        else:
            numeric_value = float(number)
    except ValueError:
        raise ValueError(f"Cannot parse number in: '{original}'")

    # Apply sign
    if sign == "-":
        numeric_value = -numeric_value

    # Handle multiplier
    if multiplier:
        mult_upper = multiplier.upper()

        # Special handling for various multipliers
        if multiplier == "M":
            # Capital M is always Mega
            mult_value = 1e6
        elif multiplier == "m":
            # Lowercase m is always milli
            mult_value = 1e-3
        elif mult_upper == "U" or multiplier == "μ":
            # u or μ is always micro
            mult_value = 1e-6
        elif mult_upper == "N":
            # n is nano
            mult_value = 1e-9
        elif mult_upper == "P":
            # p is pico
            mult_value = 1e-12
        elif mult_upper == "F":
            # f is femto
            mult_value = 1e-15
        elif mult_upper == "K":
            # k is kilo
            mult_value = 1e3
        elif mult_upper == "G":
            # G is giga
            mult_value = 1e9
        elif mult_upper == "T":
            # T is tera
            mult_value = 1e12
        elif mult_upper in MULTIPLIERS:
            mult_value = MULTIPLIERS[mult_upper]
        else:
            raise ValueError(f"Unknown multiplier '{multiplier}' in: '{original}'")

        numeric_value *= mult_value

    # Check if unit is valid (but don't use it for calculation)
    if unit:
        unit_upper = unit.upper()
        # Special handling for common units
        if unit_upper in UNIT_SUFFIXES:
            pass  # Valid unit, ignore it
        elif unit_upper in ["", "R"]:  # R is sometimes used for resistors
            pass  # No unit or resistor indicator
        else:
            # Check if it might be a compound unit like "OHM" or "OHMS"
            if not any(unit_upper.startswith(valid) for valid in UNIT_SUFFIXES):
                raise ValueError(f"Unknown unit '{unit}' in: '{original}'")

    return numeric_value
