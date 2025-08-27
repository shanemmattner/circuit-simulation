"""555 timer circuit implementation."""

from typing import Dict, Optional


class Timer555Circuit:
    """555 timer IC circuit in various configurations.

    Modes:
    - Astable: Free-running oscillator
    - Monostable: One-shot pulse generator
    - Bistable: Flip-flop
    - PWM: Pulse width modulation
    """

    def __init__(
        self,
        mode: str = "astable",
        r1: Optional[float] = None,
        r2: Optional[float] = None,
        c: Optional[float] = None,
        vcc: float = 5.0,
        control_voltage: Optional[float] = None,
        has_diode: bool = False,
    ):
        """Initialize 555 timer circuit.

        Args:
            mode: Operating mode
            r1: Resistor 1 (charging resistor for astable)
            r2: Resistor 2 (discharge resistor for astable)
            c: Timing capacitor
            vcc: Supply voltage
            control_voltage: Control voltage for PWM
            has_diode: Diode bypass for 50% duty cycle
        """
        self.mode = mode.lower()
        self.r1 = r1
        self.r2 = r2
        self.c = c
        self.vcc = vcc
        self.control_voltage = control_voltage
        self.has_diode = has_diode

        # Calculate timing parameters
        self._calculate_parameters()

    def _calculate_parameters(self):
        """Calculate timing parameters based on mode."""
        if self.mode == "astable":
            if self.r1 and self.r2 and self.c:
                # Astable frequency and duty cycle
                if self.has_diode:
                    # With diode bypass for 50% duty cycle
                    self.frequency = 1.44 / ((self.r1 + self.r2) * self.c)
                    self.duty_cycle = 0.5
                else:
                    # Standard astable
                    self.frequency = 1.44 / ((self.r1 + 2 * self.r2) * self.c)
                    self.duty_cycle = (self.r1 + self.r2) / (self.r1 + 2 * self.r2)

                self.period = 1 / self.frequency
                self.high_time = 0.693 * (self.r1 + self.r2) * self.c
                self.low_time = 0.693 * self.r2 * self.c
            else:
                self.frequency = None
                self.duty_cycle = None
                self.period = None

        elif self.mode == "monostable":
            if self.r1 and self.c:
                # Monostable pulse width
                self.pulse_width = 1.1 * self.r1 * self.c
                self.frequency = None
                self.duty_cycle = None
            else:
                self.pulse_width = None

        elif self.mode == "bistable":
            # Bistable has no fixed timing
            self.frequency = None
            self.duty_cycle = None
            self.pulse_width = None

        elif self.mode == "pwm":
            # PWM mode with variable duty cycle
            if self.r1 and self.r2 and self.c:
                self.frequency = 1.44 / ((self.r1 + 2 * self.r2) * self.c)
                # Duty cycle controlled by control voltage
                if self.control_voltage:
                    # Control voltage varies threshold
                    threshold_ratio = self.control_voltage / self.vcc
                    self.duty_cycle = threshold_ratio
                else:
                    self.duty_cycle = 0.5
            else:
                self.frequency = None
                self.duty_cycle = None

    def get_threshold_voltages(self) -> Dict[str, float]:
        """Get threshold voltages for 555 operation.

        Returns:
            Dictionary with threshold voltages
        """
        if self.control_voltage:
            v_threshold = self.control_voltage
        else:
            v_threshold = (2 / 3) * self.vcc

        v_trigger = v_threshold / 2

        return {
            "upper_threshold": v_threshold,
            "lower_threshold": v_trigger,
            "control_voltage": self.control_voltage or v_threshold,
        }

    def generate_netlist(self) -> str:
        """Generate SPICE netlist for the circuit.

        Returns:
            SPICE netlist string
        """
        netlist = []
        netlist.append(f"* 555 Timer - {self.mode.title()} Mode")
        netlist.append(f"* VCC = {self.vcc}V")

        if self.frequency:
            netlist.append(f"* Frequency = {self.frequency:.1f} Hz")
        if self.duty_cycle:
            netlist.append(f"* Duty Cycle = {self.duty_cycle*100:.1f}%")
        if self.pulse_width:
            netlist.append(f"* Pulse Width = {self.pulse_width*1000:.2f} ms")

        netlist.append("")
        netlist.append(f"VCC vcc 0 {self.vcc}")

        # Mode-specific components
        if self.mode == "astable":
            netlist.append(f"R1 vcc discharge {self.r1}")
            netlist.append(f"R2 discharge threshold {self.r2}")
            netlist.append(f"C1 threshold 0 {self.c}")
            if self.has_diode:
                netlist.append("D1 discharge vcc diode")
        elif self.mode == "monostable":
            netlist.append(f"R1 vcc discharge {self.r1}")
            netlist.append(f"C1 discharge 0 {self.c}")

        netlist.append("")
        netlist.append(".end")

        return "\n".join(netlist)
