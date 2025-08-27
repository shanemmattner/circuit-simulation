"""Bridge rectifier circuit implementation."""

from typing import Optional

import numpy as np


class BridgeRectifierCircuit:
    """Bridge rectifier circuit for AC to DC conversion.

    Full-wave bridge rectifier using 4 diodes with optional
    filter capacitor for smoothing.
    """

    def __init__(
        self,
        v_ac_rms: float = 12.0,
        frequency: float = 60.0,
        load_resistance: float = 100.0,
        filter_capacitor: Optional[float] = None,
        diode_drop: float = 0.7,
    ):
        """Initialize bridge rectifier.

        Args:
            v_ac_rms: AC input voltage (RMS)
            frequency: AC frequency in Hz
            load_resistance: Load resistance in ohms
            filter_capacitor: Filter capacitor in farads
            diode_drop: Forward voltage drop per diode
        """
        self.v_ac_rms = v_ac_rms
        self.v_ac_peak = v_ac_rms * np.sqrt(2)
        self.frequency = frequency
        self.load_resistance = load_resistance
        self.filter_capacitor = filter_capacitor
        self.diode_drop = diode_drop

        # Calculate DC output
        self._calculate_output()

    def _calculate_output(self):
        """Calculate DC output parameters."""
        # Account for 2 diode drops in bridge
        v_peak_rectified = self.v_ac_peak - 2 * self.diode_drop

        if self.filter_capacitor:
            # With filter capacitor
            self.v_dc_no_load = v_peak_rectified

            # Calculate ripple
            self.ripple_voltage = self.calculate_ripple_voltage()
            self.v_dc_loaded = v_peak_rectified - self.ripple_voltage / 2
        else:
            # Without filter (pure rectification)
            # Average of rectified sine wave
            self.v_dc_no_load = (2 * v_peak_rectified) / np.pi  # 0.637 * Vpeak
            self.v_dc_loaded = self.v_dc_no_load
            self.ripple_voltage = v_peak_rectified  # 100% ripple

    def calculate_ripple_voltage(self) -> float:
        """Calculate peak-to-peak ripple voltage.

        Returns:
            Ripple voltage in volts
        """
        if not self.filter_capacitor:
            return self.v_ac_peak

        # For full-wave rectifier: Vripple = I/(2*f*C)
        i_load = self.v_dc_no_load / self.load_resistance
        ripple = i_load / (2 * self.frequency * self.filter_capacitor)

        return ripple

    def calculate_output_voltage(self) -> float:
        """Calculate output voltage under load.

        Returns:
            DC output voltage
        """
        if self.filter_capacitor:
            # With capacitor, voltage drops by half ripple
            return self.v_dc_no_load - self.calculate_ripple_voltage() / 2
        else:
            return self.v_dc_no_load

    def calculate_efficiency(self) -> float:
        """Calculate rectifier efficiency.

        Returns:
            Efficiency as percentage
        """
        p_out = self.v_dc_loaded**2 / self.load_resistance

        # Input power (RMS)
        p_in = self.v_ac_rms**2 / self.load_resistance

        # Account for diode losses
        i_load = self.v_dc_loaded / self.load_resistance
        p_diode = 2 * self.diode_drop * i_load  # 2 diodes conduct

        efficiency = (p_out / (p_out + p_diode)) * 100

        return min(efficiency, 95)  # Cap at realistic max
