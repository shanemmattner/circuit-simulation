"""Complete power supply circuit implementation."""

from typing import Optional

import numpy as np


class PowerSupplyCircuit:
    """Complete power supply with rectification and regulation."""

    def __init__(
        self,
        v_ac_input: float,
        v_dc_output: float,
        i_max: float,
        regulator_type: str = "linear",
        filter_capacitor: float = 1000e-6,
        switching_freq: Optional[float] = None,
    ):
        """Initialize power supply.

        Args:
            v_ac_input: AC input voltage (RMS)
            v_dc_output: Regulated DC output
            i_max: Maximum output current
            regulator_type: "linear" or "switching"
            filter_capacitor: Filter capacitor value
            switching_freq: Switching frequency (for SMPS)
        """
        self.v_ac_input = v_ac_input
        self.v_dc_output = v_dc_output
        self.i_max = i_max
        self.regulator_type = regulator_type
        self.filter_capacitor = filter_capacitor
        self.switching_freq = switching_freq or 100e3

        # Calculate intermediate voltages
        self.v_rectified = v_ac_input * np.sqrt(2) - 1.4  # After bridge
        self.v_filtered = self.v_rectified - self._calculate_ripple() / 2

    def _calculate_ripple(self) -> float:
        """Calculate ripple voltage."""
        # Ripple for full-wave rectifier
        return self.i_max / (120 * self.filter_capacitor)  # 120Hz for 60Hz input

    def calculate_efficiency(self) -> float:
        """Calculate power supply efficiency."""
        if self.regulator_type == "linear":
            # Linear regulator efficiency
            return (self.v_dc_output / self.v_filtered) * 100
        else:
            # Switching regulator efficiency (typical)
            return 85.0  # Typical 85% for buck converter

    def calculate_load_regulation(self) -> float:
        """Calculate load regulation percentage."""
        # Typical values
        if self.regulator_type == "linear":
            return 2.0  # 2% typical for linear
        else:
            return 1.0  # 1% for switching

    def calculate_ripple_rejection(self) -> float:
        """Calculate ripple rejection in dB."""
        if self.regulator_type == "linear":
            return 60  # Typical 60dB for linear regulator
        else:
            return 40  # Lower for switching

    def calculate_output_ripple(self) -> float:
        """Calculate output ripple voltage."""
        input_ripple = self._calculate_ripple()
        rejection_ratio = 10 ** (self.calculate_ripple_rejection() / 20)
        return input_ripple / rejection_ratio
