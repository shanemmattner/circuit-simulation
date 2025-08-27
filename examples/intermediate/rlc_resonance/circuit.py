"""RLC resonance circuit implementation."""

import numpy as np
from typing import Optional, Dict, Any, Tuple
from pathlib import Path


class RLCResonanceCircuit:
    """RLC resonant circuit (series or parallel).

    RLC circuits exhibit resonance where inductive and capacitive
    reactances cancel, leading to interesting frequency-dependent behavior.

    Series RLC:
        Vin ---[R]---[L]---[C]--- GND

    Parallel RLC:
        Vin ---+---[R]---+--- GND
               |         |
               [L]      [C]
               |         |
               +---------+

    Key parameters:
    - Resonant frequency: f0 = 1/(2π√(LC))
    - Quality factor: Q = f0/BW
    - Damping ratio: ζ = 1/(2Q)
    """

    def __init__(
        self,
        r: float = 10,
        l: float = 1e-3,
        c: float = 1e-6,
        topology: str = "series",
        vin: float = 1.0,
    ):
        """Initialize RLC resonance circuit.

        Args:
            r: Resistance in ohms
            l: Inductance in henries
            c: Capacitance in farads
            topology: "series" or "parallel"
            vin: Input voltage amplitude in volts
        """
        self.r = r
        self.l = l
        self.c = c
        self.topology = topology.lower()
        self.vin = vin

        if self.topology not in ["series", "parallel"]:
            raise ValueError(f"Invalid topology: {topology}")

        # Calculate resonance parameters
        self._calculate_parameters()
        self.circuit = self._build_circuit()

    def _calculate_parameters(self):
        """Calculate resonance parameters."""
        # Resonant frequency (same for series and parallel)
        self.resonant_frequency = 1 / (2 * np.pi * np.sqrt(self.l * self.c))
        self.angular_frequency = 2 * np.pi * self.resonant_frequency

        # Characteristic impedance
        self.characteristic_impedance = np.sqrt(self.l / self.c)

        # Quality factor
        if self.topology == "series":
            # Q = (1/R) * sqrt(L/C)
            self.q_factor = self.characteristic_impedance / self.r
        else:  # parallel
            # Q = R / sqrt(L/C)
            self.q_factor = self.r / self.characteristic_impedance

        # Bandwidth
        self.bandwidth = (
            self.resonant_frequency / self.q_factor if self.q_factor > 0 else float("inf")
        )

        # Damping ratio and type
        self.damping_ratio = 1 / (2 * self.q_factor) if self.q_factor > 0 else float("inf")

        if self.damping_ratio < 1:
            self.damping_type = "underdamped"
            # Calculate damped natural frequency
            self.damped_frequency = self.resonant_frequency * np.sqrt(1 - self.damping_ratio**2)
        elif abs(self.damping_ratio - 1) < 0.01:
            self.damping_type = "critically_damped"
            self.damped_frequency = 0
        else:
            self.damping_type = "overdamped"
            self.damped_frequency = 0

    def _build_circuit(self) -> Dict[str, Any]:
        """Build circuit representation."""
        circuit = {"name": f"RLC {self.topology.title()} Resonant Circuit", "components": {}}

        # Voltage source
        circuit["components"]["V1"] = {"type": "voltage", "value": self.vin, "nodes": ("in", "0")}

        if self.topology == "series":
            # Series connection
            circuit["components"]["R1"] = {
                "type": "resistor",
                "value": self.r,
                "nodes": ("in", "n1"),
            }
            circuit["components"]["L1"] = {
                "type": "inductor",
                "value": self.l,
                "nodes": ("n1", "n2"),
            }
            circuit["components"]["C1"] = {
                "type": "capacitor",
                "value": self.c,
                "nodes": ("n2", "0"),
            }
        else:  # parallel
            # Parallel connection
            circuit["components"]["R1"] = {
                "type": "resistor",
                "value": self.r,
                "nodes": ("in", "0"),
            }
            circuit["components"]["L1"] = {
                "type": "inductor",
                "value": self.l,
                "nodes": ("in", "0"),
            }
            circuit["components"]["C1"] = {
                "type": "capacitor",
                "value": self.c,
                "nodes": ("in", "0"),
            }

        return circuit

    def calculate_impedance(self, frequency: float) -> complex:
        """Calculate circuit impedance at given frequency.

        Args:
            frequency: Frequency in Hz

        Returns:
            Complex impedance
        """
        omega = 2 * np.pi * frequency

        # Inductive reactance
        x_l = omega * self.l

        # Capacitive reactance
        x_c = 1 / (omega * self.c) if omega > 0 else float("inf")

        if self.topology == "series":
            # Series: Z = R + j(XL - XC)
            z = self.r + 1j * (x_l - x_c)
        else:  # parallel
            # Parallel: 1/Z = 1/R + 1/jXL + 1/(-jXC)
            if x_l == 0:
                x_l = 1e-10  # Avoid division by zero
            if x_c == float("inf"):
                x_c = 1e10

            y = 1 / self.r + 1 / (1j * x_l) + 1 / (-1j * x_c)
            z = 1 / y if abs(y) > 0 else float("inf")

        return z

    def transfer_function(self, frequency: float) -> complex:
        """Calculate transfer function at given frequency.

        Args:
            frequency: Frequency in Hz

        Returns:
            Complex transfer function
        """
        omega = 2 * np.pi * frequency
        s = 1j * omega  # Laplace variable

        if self.topology == "series":
            # Voltage divider with output across C
            # H(s) = 1 / (LCs² + RCs + 1)
            h = 1 / (self.l * self.c * s**2 + self.r * self.c * s + 1)
        else:  # parallel
            # Current divider
            # H(s) = (RLCs²) / (LCs² + L/R*s + 1)
            h = (self.r * self.l * self.c * s**2) / (
                self.l * self.c * s**2 + self.l / self.r * s + 1
            )

        return h

    def calculate_half_power_frequencies(self) -> Tuple[float, float]:
        """Calculate -3dB (half-power) frequencies.

        Returns:
            Tuple of (lower_freq, upper_freq) in Hz
        """
        if self.q_factor <= 0:
            return (0, float("inf"))

        # Half-power frequencies
        # f_lower = f0 * (sqrt(1 + 1/(4Q²)) - 1/(2Q))
        # f_upper = f0 * (sqrt(1 + 1/(4Q²)) + 1/(2Q))

        discriminant = np.sqrt(1 + 1 / (4 * self.q_factor**2))
        f_lower = self.resonant_frequency * (discriminant - 1 / (2 * self.q_factor))
        f_upper = self.resonant_frequency * (discriminant + 1 / (2 * self.q_factor))

        return (f_lower, f_upper)

    def calculate_energy(self, time: float, current: float, voltage_c: float) -> Dict[str, float]:
        """Calculate energy stored in L and C.

        Args:
            time: Time instant
            current: Current through inductor
            voltage_c: Voltage across capacitor

        Returns:
            Dictionary with energy values
        """
        # Energy in inductor: E_L = 0.5 * L * I²
        energy_l = 0.5 * self.l * current**2

        # Energy in capacitor: E_C = 0.5 * C * V²
        energy_c = 0.5 * self.c * voltage_c**2

        # Total energy
        total_energy = energy_l + energy_c

        return {
            "inductor_energy": energy_l,
            "capacitor_energy": energy_c,
            "total_energy": total_energy,
            "time": time,
        }

    def generate_netlist(self) -> str:
        """Generate SPICE netlist for the circuit.

        Returns:
            SPICE netlist string
        """
        netlist = []
        netlist.append(f"* RLC {self.topology.title()} Resonant Circuit")
        netlist.append(f"* R={self.r} ohms, L={self.l*1e3:.2f}mH, C={self.c*1e6:.2f}uF")
        netlist.append(f"* Resonant frequency: {self.resonant_frequency:.2f} Hz")
        netlist.append(f"* Q factor: {self.q_factor:.2f}")
        netlist.append(f"* Bandwidth: {self.bandwidth:.2f} Hz")
        netlist.append("")

        # AC voltage source
        netlist.append("V1 in 0 AC 1 0")

        if self.topology == "series":
            netlist.append(f"R1 in n1 {self.r}")
            netlist.append(f"L1 n1 n2 {self.l}")
            netlist.append(f"C1 n2 0 {self.c}")
        else:  # parallel
            netlist.append(f"R1 in 0 {self.r}")
            netlist.append(f"L1 in 0 {self.l}")
            netlist.append(f"C1 in 0 {self.c}")

        # Analysis commands
        netlist.append("")
        netlist.append(f".ac dec 30 {self.resonant_frequency/100} {self.resonant_frequency*100}")
        netlist.append(".print ac v(in) i(V1) v(n2)")
        netlist.append("")

        # Transient analysis for step response
        period = 1 / self.resonant_frequency
        netlist.append(f".tran {period/100} {period*20}")
        netlist.append(".end")

        return "\n".join(netlist)

    def characterize_circuit(self) -> Dict[str, Any]:
        """Get comprehensive circuit characteristics.

        Returns:
            Dictionary of circuit parameters
        """
        f_lower, f_upper = self.calculate_half_power_frequencies()

        return {
            "topology": self.topology,
            "resistance": self.r,
            "inductance": self.l,
            "capacitance": self.c,
            "resonant_frequency": self.resonant_frequency,
            "resonant_frequency_hz": f"{self.resonant_frequency:.2f} Hz",
            "angular_frequency": self.angular_frequency,
            "q_factor": self.q_factor,
            "bandwidth": self.bandwidth,
            "bandwidth_hz": f"{self.bandwidth:.2f} Hz",
            "damping_ratio": self.damping_ratio,
            "damping_type": self.damping_type,
            "characteristic_impedance": self.characteristic_impedance,
            "half_power_frequencies": {
                "lower": f_lower,
                "upper": f_upper,
                "lower_hz": f"{f_lower:.2f} Hz",
                "upper_hz": f"{f_upper:.2f} Hz",
            },
            "selectivity": self.q_factor,  # Selectivity = Q
            "damped_frequency": (
                self.damped_frequency if self.damping_type == "underdamped" else None
            ),
        }

    def __str__(self) -> str:
        """String representation of the circuit."""
        return (
            f"RLC {self.topology.title()} Circuit: "
            f"R={self.r}Ω, L={self.l*1e3:.1f}mH, C={self.c*1e6:.2f}µF, "
            f"f0={self.resonant_frequency:.1f}Hz, Q={self.q_factor:.1f}"
        )
