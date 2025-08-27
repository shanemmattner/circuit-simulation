"""RC filter circuit implementation."""

import numpy as np
from typing import Optional, Dict, Any, List
from pathlib import Path


class RCFilterCircuit:
    """RC filter circuit (low-pass or high-pass).

    An RC filter uses a resistor and capacitor to create frequency-dependent
    behavior. The cutoff frequency is determined by fc = 1/(2πRC).

    Low-pass configuration:
        Vin ---[R]---+--- Vout
                     |
                    [C]
                     |
                    GND

    High-pass configuration:
        Vin ---[C]---+--- Vout
                     |
                    [R]
                     |
                    GND
    """

    def __init__(
        self, r: float = 1000, c: float = 1e-6, filter_type: str = "lowpass", vin: float = 1.0
    ):
        """Initialize RC filter circuit.

        Args:
            r: Resistance in ohms
            c: Capacitance in farads
            filter_type: "lowpass" or "highpass"
            vin: Input voltage amplitude in volts
        """
        self.r = r
        self.c = c
        self.filter_type = filter_type.lower()
        self.vin = vin

        if self.filter_type not in ["lowpass", "highpass"]:
            raise ValueError(f"Invalid filter type: {filter_type}")

        # Calculate key parameters
        self.time_constant = r * c
        self.cutoff_frequency = 1 / (2 * np.pi * self.time_constant)

        self.circuit = self._build_circuit()

    def _build_circuit(self) -> Dict[str, Any]:
        """Build the circuit representation."""
        circuit = {"name": f"RC {self.filter_type.title()} Filter", "components": {}}

        # Voltage source
        circuit["components"]["V1"] = {"type": "voltage", "value": self.vin, "nodes": ("in", "0")}

        if self.filter_type == "lowpass":
            # Lowpass: R then C to ground
            circuit["components"]["R1"] = {
                "type": "resistor",
                "value": self.r,
                "nodes": ("in", "out"),
            }
            circuit["components"]["C1"] = {
                "type": "capacitor",
                "value": self.c,
                "nodes": ("out", "0"),
            }
        else:  # highpass
            # Highpass: C then R to ground
            circuit["components"]["C1"] = {
                "type": "capacitor",
                "value": self.c,
                "nodes": ("in", "out"),
            }
            circuit["components"]["R1"] = {
                "type": "resistor",
                "value": self.r,
                "nodes": ("out", "0"),
            }

        return circuit

    def transfer_function(self, frequency: float) -> complex:
        """Calculate transfer function H(jω) at given frequency.

        Args:
            frequency: Frequency in Hz

        Returns:
            Complex transfer function value
        """
        omega = 2 * np.pi * frequency

        if self.filter_type == "lowpass":
            # H(jω) = 1 / (1 + jωRC)
            return 1 / (1 + 1j * omega * self.r * self.c)
        else:  # highpass
            # H(jω) = jωRC / (1 + jωRC)
            return (1j * omega * self.r * self.c) / (1 + 1j * omega * self.r * self.c)

    def magnitude_response(self, frequency: float) -> float:
        """Calculate magnitude response at given frequency.

        Args:
            frequency: Frequency in Hz

        Returns:
            Magnitude (0 to 1)
        """
        h = self.transfer_function(frequency)
        return abs(h)

    def phase_response(self, frequency: float) -> float:
        """Calculate phase response at given frequency.

        Args:
            frequency: Frequency in Hz

        Returns:
            Phase in degrees
        """
        h = self.transfer_function(frequency)
        return np.degrees(np.angle(h))

    def magnitude_db(self, frequency: float) -> float:
        """Calculate magnitude response in dB.

        Args:
            frequency: Frequency in Hz

        Returns:
            Magnitude in dB
        """
        mag = self.magnitude_response(frequency)
        return 20 * np.log10(mag) if mag > 0 else -100

    def characterize_filter(self) -> Dict[str, Any]:
        """Get filter characteristics.

        Returns:
            Dictionary of filter parameters
        """
        return {
            "filter_type": self.filter_type,
            "cutoff_frequency": self.cutoff_frequency,
            "cutoff_frequency_hz": f"{self.cutoff_frequency:.2f} Hz",
            "time_constant": self.time_constant,
            "time_constant_ms": f"{self.time_constant * 1000:.3f} ms",
            "attenuation_per_decade": -20,  # First-order filter
            "attenuation_per_octave": -6,  # First-order filter
            "resistance": self.r,
            "capacitance": self.c,
            "3db_frequency": self.cutoff_frequency,
        }

    def calculate_group_delay(self, frequencies: List[float]) -> List[float]:
        """Calculate group delay at given frequencies.

        Group delay is the derivative of phase with respect to frequency.

        Args:
            frequencies: List of frequencies in Hz

        Returns:
            List of group delays in seconds
        """
        delays = []

        for freq in frequencies:
            omega = 2 * np.pi * freq

            if self.filter_type == "lowpass":
                # Group delay for lowpass RC filter
                delay = self.r * self.c / (1 + (omega * self.r * self.c) ** 2)
            else:  # highpass
                # Group delay for highpass RC filter
                delay = self.r * self.c / (1 + (omega * self.r * self.c) ** 2)

            delays.append(delay)

        return delays

    def calculate_cascade_response(self, n_stages: int, frequency: float) -> Dict[str, float]:
        """Calculate response of n cascaded identical RC stages.

        Args:
            n_stages: Number of cascaded stages
            frequency: Frequency in Hz

        Returns:
            Dictionary with magnitude and phase
        """
        single_response = self.transfer_function(frequency)
        cascade_response = single_response**n_stages

        return {
            "magnitude": abs(cascade_response),
            "phase": np.degrees(np.angle(cascade_response)),
            "magnitude_db": 20 * np.log10(abs(cascade_response)),
        }

    def generate_netlist(self) -> str:
        """Generate SPICE netlist for the circuit.

        Returns:
            SPICE netlist string
        """
        netlist = []
        filter_name = f"RC {self.filter_type.title().replace('pass', '-Pass')} Filter"
        netlist.append(f"* {filter_name}")
        netlist.append(f"* R={self.r} ohms, C={self.c*1e6:.2f}uF")
        netlist.append(f"* Cutoff frequency: {self.cutoff_frequency:.2f} Hz")
        netlist.append("")

        # AC voltage source for frequency response
        netlist.append("V1 in 0 AC 1 0")  # 1V amplitude, 0 phase

        if self.filter_type == "lowpass":
            netlist.append(f"R1 in out {self._format_value(self.r, 'R')}")
            netlist.append(f"C1 out 0 {self._format_value(self.c, 'C')}")
        else:  # highpass
            netlist.append(f"C1 in out {self._format_value(self.c, 'C')}")
            netlist.append(f"R1 out 0 {self._format_value(self.r, 'R')}")

        # Analysis commands
        netlist.append("")
        netlist.append(".ac dec 20 1 100k")  # AC sweep: 1Hz to 100kHz
        netlist.append(".print ac v(out) vp(out)")  # Magnitude and phase

        # Transient analysis for step response
        netlist.append(f".tran {self.time_constant/100} {self.time_constant*10}")
        netlist.append(".end")

        return "\n".join(netlist)

    def _format_value(self, value: float, component_type: str) -> str:
        """Format component value for SPICE.

        Args:
            value: Component value
            component_type: 'R' for resistor, 'C' for capacitor

        Returns:
            Formatted string
        """
        if component_type == "R":
            if value >= 1e6:
                return f"{value/1e6:.1f}Meg"
            elif value >= 1e3:
                return f"{value/1e3:.1f}k"
            else:
                return f"{value:.1f}"
        else:  # Capacitor
            if value >= 1e-6:
                return f"{value*1e6:.2f}u"
            elif value >= 1e-9:
                return f"{value*1e9:.2f}n"
            else:
                return f"{value*1e12:.2f}p"

    def save_netlist(self, filepath: Path):
        """Save netlist to file.

        Args:
            filepath: Path to save the netlist
        """
        netlist = self.generate_netlist()
        filepath.write_text(netlist)

    def __str__(self) -> str:
        """String representation of the circuit."""
        return (
            f"RC {self.filter_type.title()}-Pass Filter: "
            f"R={self.r}Ω, C={self.c*1e6:.2f}µF, "
            f"fc={self.cutoff_frequency:.1f}Hz"
        )
