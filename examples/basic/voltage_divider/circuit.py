"""Voltage divider circuit implementation."""

from typing import Optional
from pathlib import Path


class VoltageDividerCircuit:
    """A simple voltage divider circuit.

    The voltage divider is one of the most fundamental circuits in electronics.
    It uses two resistors in series to reduce an input voltage to a desired
    output voltage level.

    Circuit topology:
        Vin ---[R1]---+--- Vout
                      |
                     [R2]
                      |
                     GND

    The output voltage is given by: Vout = Vin * R2 / (R1 + R2)
    """

    def __init__(
        self, r1: float = 1000, r2: float = 1000, vin: float = 5.0, r_load: Optional[float] = None
    ):
        """Initialize voltage divider circuit.

        Args:
            r1: First resistor value in ohms
            r2: Second resistor value in ohms
            vin: Input voltage in volts
            r_load: Optional load resistance in ohms
        """
        self.r1 = r1
        self.r2 = r2
        self.vin = vin
        self.r_load = r_load
        self.circuit = self._build_circuit()

    def _build_circuit(self):
        """Build the circuit representation."""
        # This would integrate with PySpice or generate netlist
        circuit = {
            "name": "Voltage Divider",
            "components": {
                "V1": {"type": "voltage", "value": self.vin, "nodes": ("in", "0")},
                "R1": {"type": "resistor", "value": self.r1, "nodes": ("in", "out")},
                "R2": {"type": "resistor", "value": self.r2, "nodes": ("out", "0")},
            },
        }

        if self.r_load:
            circuit["components"]["R_load"] = {
                "type": "resistor",
                "value": self.r_load,
                "nodes": ("out", "0"),
            }

        return circuit

    def calculate_theoretical_output(self) -> float:
        """Calculate theoretical output voltage.

        Returns:
            Output voltage in volts
        """
        if self.r_load:
            # Calculate parallel resistance of R2 and R_load
            r2_effective = (self.r2 * self.r_load) / (self.r2 + self.r_load)
        else:
            r2_effective = self.r2

        # Voltage divider formula
        vout = self.vin * r2_effective / (self.r1 + r2_effective)
        return vout

    def calculate_power_dissipation(self) -> dict:
        """Calculate power dissipation in each component.

        Returns:
            Dictionary with power values for each component
        """
        vout = self.calculate_theoretical_output()
        v_r1 = self.vin - vout

        # Current through R1
        i_r1 = v_r1 / self.r1

        # Current through R2
        i_r2 = vout / self.r2

        power = {"R1": v_r1 * i_r1, "R2": vout * i_r2, "total": self.vin * i_r1}

        if self.r_load:
            i_load = vout / self.r_load
            power["R_load"] = vout * i_load
            power["total"] = self.vin * (i_r1 + i_load)

        return power

    def generate_netlist(self) -> str:
        """Generate SPICE netlist for the circuit.

        Returns:
            SPICE netlist string
        """
        netlist = []
        netlist.append("* Voltage Divider Circuit")
        netlist.append(f"* R1={self.r1} ohms, R2={self.r2} ohms, Vin={self.vin}V")
        netlist.append("")

        # Voltage source
        netlist.append(f"V1 in 0 DC {self.vin}")

        # Resistors
        netlist.append(f"R1 in out {self._format_resistance(self.r1)}")
        netlist.append(f"R2 out 0 {self._format_resistance(self.r2)}")

        if self.r_load:
            netlist.append(f"R_load out 0 {self._format_resistance(self.r_load)}")

        # Analysis commands
        netlist.append("")
        netlist.append(".dc V1 0 10 0.1")  # DC sweep from 0 to 10V
        netlist.append(".print dc v(out) i(V1)")
        netlist.append(".end")

        return "\n".join(netlist)

    def _format_resistance(self, value: float) -> str:
        """Format resistance value for SPICE."""
        if value >= 1e6:
            return f"{value/1e6:.1f}Meg"
        elif value >= 1e3:
            return f"{value/1e3:.1f}k"
        else:
            return f"{value:.1f}"

    def save_netlist(self, filepath: Path):
        """Save netlist to file.

        Args:
            filepath: Path to save the netlist
        """
        netlist = self.generate_netlist()
        filepath.write_text(netlist)

    def get_component_values(self) -> dict:
        """Get all component values.

        Returns:
            Dictionary of component values
        """
        values = {"R1": self.r1, "R2": self.r2, "Vin": self.vin}

        if self.r_load:
            values["R_load"] = self.r_load

        return values

    def __str__(self) -> str:
        """String representation of the circuit."""
        return (
            f"Voltage Divider: R1={self.r1}Ω, R2={self.r2}Ω, "
            f"Vin={self.vin}V, Vout={self.calculate_theoretical_output():.2f}V"
        )
