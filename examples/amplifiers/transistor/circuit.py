"""Transistor amplifier circuit implementation."""

from typing import Optional


class TransistorAmplifierCircuit:
    """Bipolar junction transistor amplifier circuit.

    Supports common emitter, common collector, and common base configurations.
    """

    def __init__(
        self,
        config: str = "common_emitter",
        vcc: float = 12.0,
        rc: Optional[float] = None,
        re: Optional[float] = None,
        r1: Optional[float] = None,
        r2: Optional[float] = None,
        beta: float = 100,
        vbe: float = 0.7,
        bypass_capacitor: Optional[float] = None,
    ):
        """Initialize transistor amplifier.

        Args:
            config: Configuration type
            vcc: Supply voltage
            rc: Collector resistor
            re: Emitter resistor
            r1: Base bias resistor 1
            r2: Base bias resistor 2
            beta: Current gain (hfe)
            vbe: Base-emitter voltage
            bypass_capacitor: Emitter bypass capacitor
        """
        self.config = config
        self.vcc = vcc
        self.rc = rc
        self.re = re
        self.r1 = r1
        self.r2 = r2
        self.beta = beta
        self.vbe = vbe
        self.bypass_capacitor = bypass_capacitor

    def calculate_voltage_gain(self) -> float:
        """Calculate small-signal voltage gain.

        Returns:
            Voltage gain (Av)
        """
        if self.config == "common_emitter":
            if self.bypass_capacitor:
                # With bypass capacitor, no degeneration
                # Av = -gm * Rc where gm = Ic/Vt
                ic = self._calculate_collector_current()
                vt = 0.026  # Thermal voltage at room temp
                gm = ic / vt
                return -gm * self.rc if self.rc else 0
            else:
                # With emitter degeneration
                if self.re and self.rc:
                    return -self.rc / self.re
                else:
                    return 0

        elif self.config == "common_collector":
            # Emitter follower, gain ~1
            return 0.95

        elif self.config == "common_base":
            # Non-inverting, similar magnitude to CE
            if self.rc and self.re:
                return self.rc / self.re
            else:
                return 0

        return 0

    def calculate_input_impedance(self) -> float:
        """Calculate input impedance.

        Returns:
            Input impedance in ohms
        """
        if self.config == "common_emitter":
            # Zin = R1 || R2 || (β * re)
            r_bias = (
                (self.r1 * self.r2) / (self.r1 + self.r2)
                if self.r1 and self.r2
                else 10000
            )

            if self.re:
                z_transistor = self.beta * self.re
                return (r_bias * z_transistor) / (r_bias + z_transistor)
            else:
                return r_bias

        elif self.config == "common_collector":
            # High input impedance
            if self.re:
                return self.beta * self.re
            else:
                return 10000

        elif self.config == "common_base":
            # Low input impedance
            return (
                26 / self._calculate_collector_current()
                if self._calculate_collector_current() > 0
                else 50
            )

        return 1000

    def calculate_stability_factor(self) -> float:
        """Calculate bias stability factor.

        Returns:
            Stability factor S
        """
        if not self.r1 or not self.r2:
            return 100  # Poor stability

        # S = (1 + Rb/Re) where Rb = R1||R2
        rb = (self.r1 * self.r2) / (self.r1 + self.r2)

        if self.re:
            return 1 + rb / self.re
        else:
            return 100  # Poor stability without Re

    def _calculate_collector_current(self) -> float:
        """Calculate quiescent collector current.

        Returns:
            Collector current in amperes
        """
        if not self.r1 or not self.r2:
            return 1e-3  # Default 1mA

        # Voltage divider bias
        vb = self.vcc * self.r2 / (self.r1 + self.r2)

        if self.re:
            ve = vb - self.vbe
            ie = ve / self.re
            ic = ie * self.beta / (self.beta + 1)
            return ic
        else:
            # Rough estimate without Re
            return 1e-3
