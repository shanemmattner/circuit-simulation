"""Op-amp amplifier circuit implementations."""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models.spice_loader import ModelNotFoundError, SpiceModelLoader


class OpAmpCircuit:
    """Op-amp amplifier circuit with various configurations.

    Supports:
    - Inverting amplifier
    - Non-inverting amplifier
    - Differential amplifier
    - Buffer (voltage follower)
    - Integrator
    - Differentiator

    Can use real SPICE models from KiCad library or ideal model.
    """

    def __init__(
        self,
        config: str = "inverting",
        r_in: float = 10000,
        r_feedback: float = 100000,
        r_in2: Optional[float] = None,
        r_ground: Optional[float] = None,
        c_feedback: Optional[float] = None,
        c_compensation: Optional[float] = None,
        model: str = "ideal",
        vin: float = 1.0,
        vcc: float = 15.0,
        vee: float = -15.0,
        gbw: Optional[float] = None,
        slew_rate: Optional[float] = None,
    ):
        """Initialize op-amp circuit.

        Args:
            config: Configuration type
            r_in: Input resistance in ohms
            r_feedback: Feedback resistance in ohms
            r_in2: Second input resistance (for differential)
            r_ground: Ground resistance (for differential)
            c_feedback: Feedback capacitance (for integrator)
            c_compensation: Compensation capacitance
            model: Op-amp model ("ideal", "LM358", "TL072", etc.)
            vin: Input voltage
            vcc: Positive supply voltage
            vee: Negative supply voltage
            gbw: Gain-bandwidth product in Hz
            slew_rate: Slew rate in V/s
        """
        self.config = config.lower()
        self.r_in = r_in
        self.r_feedback = r_feedback
        self.r_in2 = r_in2
        self.r_ground = r_ground
        self.c_feedback = c_feedback
        self.c_compensation = c_compensation
        self.model = model
        self.vin = vin
        self.vcc = vcc
        self.vee = vee
        self.gbw = gbw
        self.slew_rate = slew_rate

        # Load SPICE model if not ideal
        self.spice_model = self._load_model()

        # Calculate time constant for integrator/differentiator
        if self.config == "integrator" and c_feedback:
            self.time_constant = r_in * c_feedback
        elif self.config == "differentiator" and c_feedback:
            self.time_constant = r_feedback * c_feedback
        else:
            self.time_constant = None

        # Build circuit
        self.circuit = self._build_circuit()

    def _load_model(self) -> Optional[str]:
        """Load SPICE model from library.

        Returns:
            SPICE model string or None for ideal model
        """
        if self.model == "ideal":
            return None

        try:
            loader = SpiceModelLoader()

            # Try to load op-amp model
            model_content = loader.load_opamp(self.model)

            # Set GBW and slew rate from model if not specified
            if self.gbw is None:
                # Extract from model or use defaults
                if "LM358" in self.model.upper():
                    self.gbw = 1e6  # 1MHz
                    self.slew_rate = 0.5e6  # 0.5V/µs
                elif "TL072" in self.model.upper():
                    self.gbw = 3e6  # 3MHz
                    self.slew_rate = 13e6  # 13V/µs
                elif "LF351" in self.model.upper():
                    self.gbw = 4e6  # 4MHz
                    self.slew_rate = 13e6  # 13V/µs

            return model_content

        except ModelNotFoundError:
            # Fall back to ideal model
            print(f"Warning: Model {self.model} not found, using ideal model")
            return None

    def _build_circuit(self) -> Dict[str, Any]:
        """Build circuit representation.

        Returns:
            Circuit dictionary
        """
        circuit = {
            "name": f"Op-Amp {self.config.replace('_', ' ').title()} Amplifier",
            "components": {},
        }

        # Add op-amp
        if self.spice_model:
            circuit["components"]["U1"] = {
                "type": "subcircuit",
                "model": self.spice_model,
                "pins": {
                    "IN+": "v_plus",
                    "IN-": "v_minus",
                    "OUT": "out",
                    "V+": "vcc",
                    "V-": "vee",
                },
            }
        else:
            # Ideal op-amp representation
            circuit["components"]["U1"] = {
                "type": "ideal_opamp",
                "gain": 1e6,  # Open-loop gain
                "nodes": ("v_plus", "v_minus", "out"),
            }

        # Add power supplies
        circuit["components"]["VCC"] = {
            "type": "voltage",
            "value": self.vcc,
            "nodes": ("vcc", "0"),
        }
        circuit["components"]["VEE"] = {
            "type": "voltage",
            "value": self.vee,
            "nodes": ("0", "vee"),
        }

        # Add input voltage source
        circuit["components"]["VIN"] = {
            "type": "voltage",
            "value": self.vin,
            "nodes": ("in", "0"),
        }

        # Configuration-specific components
        if self.config == "inverting":
            circuit["components"]["RIN"] = {
                "type": "resistor",
                "value": self.r_in,
                "nodes": ("in", "v_minus"),
            }
            circuit["components"]["RF"] = {
                "type": "resistor",
                "value": self.r_feedback,
                "nodes": ("v_minus", "out"),
            }
            # Non-inverting input to ground
            circuit["components"]["RGND"] = {
                "type": "resistor",
                "value": 10,  # Small resistance to ground
                "nodes": ("v_plus", "0"),
            }

        elif self.config == "non_inverting":
            # Input to non-inverting terminal
            circuit["components"]["RIN_DUMMY"] = {
                "type": "resistor",
                "value": 1e9,  # Very high impedance
                "nodes": ("in", "v_plus"),
            }
            # Feedback network
            circuit["components"]["RF"] = {
                "type": "resistor",
                "value": self.r_feedback,
                "nodes": ("out", "v_minus"),
            }
            circuit["components"]["RG"] = {
                "type": "resistor",
                "value": self.r_in,
                "nodes": ("v_minus", "0"),
            }

        elif self.config == "differential":
            # Differential amplifier with 4 resistors
            circuit["components"]["R1"] = {
                "type": "resistor",
                "value": self.r_in,
                "nodes": ("in", "v_minus"),
            }
            circuit["components"]["R2"] = {
                "type": "resistor",
                "value": self.r_feedback,
                "nodes": ("v_minus", "out"),
            }
            circuit["components"]["R3"] = {
                "type": "resistor",
                "value": self.r_in2 or self.r_in,
                "nodes": ("in2", "v_plus"),
            }
            circuit["components"]["R4"] = {
                "type": "resistor",
                "value": self.r_ground or self.r_feedback,
                "nodes": ("v_plus", "0"),
            }
            # Second input
            circuit["components"]["VIN2"] = {
                "type": "voltage",
                "value": 0,  # Differential input
                "nodes": ("in2", "0"),
            }

        elif self.config == "buffer":
            # Unity gain buffer
            circuit["components"]["RIN_DUMMY"] = {
                "type": "resistor",
                "value": 1e9,
                "nodes": ("in", "v_plus"),
            }
            # Direct feedback
            circuit["components"]["WIRE"] = {
                "type": "wire",
                "nodes": ("out", "v_minus"),
            }

        elif self.config == "integrator":
            # Integrator with capacitor feedback
            circuit["components"]["RIN"] = {
                "type": "resistor",
                "value": self.r_in,
                "nodes": ("in", "v_minus"),
            }
            circuit["components"]["CF"] = {
                "type": "capacitor",
                "value": self.c_feedback,
                "nodes": ("v_minus", "out"),
            }
            # DC path for stability
            circuit["components"]["RF_LARGE"] = {
                "type": "resistor",
                "value": 10e6,  # Large parallel resistance
                "nodes": ("v_minus", "out"),
            }
            circuit["components"]["RGND"] = {
                "type": "resistor",
                "value": 10,
                "nodes": ("v_plus", "0"),
            }

        # Add compensation capacitor if specified
        if self.c_compensation:
            circuit["components"]["CCOMP"] = {
                "type": "capacitor",
                "value": self.c_compensation,
                "nodes": ("v_minus", "out"),
            }

        return circuit

    def calculate_ideal_gain(self) -> float:
        """Calculate ideal closed-loop gain.

        Returns:
            Ideal voltage gain
        """
        if self.config == "inverting":
            return -self.r_feedback / self.r_in

        elif self.config == "non_inverting":
            return 1 + self.r_feedback / self.r_in

        elif self.config == "differential":
            # For differential amplifier with 4 resistors
            # Gain = Rf/Rin when all 4 resistors are matched
            if self.r_in2 and self.r_ground:
                # Check if resistors are matched
                if self.r_feedback == self.r_ground and self.r_in == self.r_in2:
                    # Perfectly matched - unity gain
                    return self.r_feedback / self.r_in
                else:
                    # General case - more complex
                    return self.r_feedback / self.r_in
            else:
                # Assume matched resistors
                return self.r_feedback / self.r_in

        elif self.config == "buffer":
            return 1.0

        elif self.config == "integrator":
            # Gain is frequency dependent: -1/(jωRC)
            return None  # Frequency dependent

        else:
            return 1.0

    def calculate_input_impedance(self) -> float:
        """Calculate input impedance.

        Returns:
            Input impedance in ohms
        """
        if self.config == "inverting":
            return self.r_in  # Virtual ground at inverting input

        elif self.config == "non_inverting":
            return 1e9  # Very high (limited by op-amp input impedance)

        elif self.config == "differential":
            return self.r_in  # For inverting input

        elif self.config == "buffer":
            return 1e9  # Very high

        else:
            return self.r_in

    def calculate_output_impedance(self) -> float:
        """Calculate output impedance.

        Returns:
            Output impedance in ohms
        """
        # Ideal op-amp has zero output impedance
        # Real op-amps have ~50-100Ω reduced by loop gain
        if self.model == "ideal":
            return 0.01
        else:
            # Typical value reduced by negative feedback
            open_loop_gain = 1e5
            loop_gain = open_loop_gain / (1 + abs(self.calculate_ideal_gain() or 1))
            return 75 / loop_gain  # Typical 75Ω open-loop

    def calculate_bandwidth(self) -> Optional[float]:
        """Calculate closed-loop bandwidth.

        Returns:
            Bandwidth in Hz
        """
        if self.gbw is None:
            return None

        gain = abs(self.calculate_ideal_gain() or 1)

        # For voltage feedback op-amps: BW = GBW / Gain
        return self.gbw / gain

    def generate_netlist(self) -> str:
        """Generate SPICE netlist.

        Returns:
            SPICE netlist string
        """
        netlist = []
        netlist.append(f"* Op-Amp {self.config.title()} Amplifier")
        netlist.append(f"* Model: {self.model}")

        gain = self.calculate_ideal_gain()
        if gain is not None:
            netlist.append(f"* Ideal Gain: {gain:.2f}")

        netlist.append("")

        # Add components based on configuration
        # This is simplified - real implementation would be more detailed
        netlist.append("* Input")
        netlist.append(f"Vin in 0 DC {self.vin}")
        netlist.append("")

        netlist.append("* Power supplies")
        netlist.append(f"Vcc vcc 0 DC {self.vcc}")
        netlist.append(f"Vee vee 0 DC {self.vee}")
        netlist.append("")

        # Add op-amp model or ideal VCVS
        if self.spice_model:
            netlist.append("* Op-amp subcircuit")
            netlist.append(self.spice_model)
            netlist.append("XU1 v_plus v_minus vcc vee out " + self.model)
        else:
            netlist.append("* Ideal op-amp (VCVS)")
            netlist.append("EU1 out 0 v_plus v_minus 1000000")

        netlist.append("")
        netlist.append("* Configuration components")

        # Add configuration-specific components
        if self.config == "inverting":
            netlist.append(f"Rin in v_minus {self.r_in}")
            netlist.append(f"Rf v_minus out {self.r_feedback}")
            netlist.append("Rgnd v_plus 0 10")

        # ... (other configurations)

        netlist.append("")
        netlist.append("* Analysis")
        netlist.append(".dc Vin -1 1 0.01")
        netlist.append(".ac dec 10 1 1e6")
        netlist.append(".print dc v(out)")
        netlist.append(".print ac vdb(out) vp(out)")
        netlist.append(".end")

        return "\n".join(netlist)


class InstrumentationAmplifier:
    """Three op-amp instrumentation amplifier."""

    def __init__(self, gain: float = 100, r_gain: float = 1000, model: str = "LM358"):
        """Initialize instrumentation amplifier.

        Args:
            gain: Differential gain
            r_gain: Gain-setting resistor
            model: Op-amp model to use
        """
        self.gain = gain
        self.differential_gain = gain
        self.r_gain = r_gain
        self.model = model

        # Calculate other resistor values
        self.r1 = 10000  # Input stage resistors
        self.r2 = self.r1 * (gain - 1) / 2
        self.r3 = 10000  # Difference amplifier resistors

        # Common mode gain should be very low
        self.common_mode_gain = 1 / 1000  # Typical CMRR > 60dB

    def calculate_cmrr(self) -> float:
        """Calculate common-mode rejection ratio.

        Returns:
            CMRR in dB
        """
        return 20 * np.log10(self.differential_gain / self.common_mode_gain)


class ActiveFilter:
    """Active filter using op-amp."""

    def __init__(
        self,
        filter_type: str = "lowpass",
        cutoff_freq: float = 1000,
        gain: float = 1,
        order: int = 2,
        model: str = "TL072",
    ):
        """Initialize active filter.

        Args:
            filter_type: "lowpass", "highpass", "bandpass"
            cutoff_freq: Cutoff frequency in Hz
            gain: Passband gain
            order: Filter order
            model: Op-amp model
        """
        self.filter_type = filter_type
        self.cutoff_frequency = cutoff_freq
        self.passband_gain = gain
        self.order = order
        self.model = model

        # Calculate component values for Butterworth response
        self._calculate_components()

    def _calculate_components(self):
        """Calculate R and C values for desired response."""
        # Simplified - assumes unity gain Sallen-Key topology
        omega = 2 * np.pi * self.cutoff_frequency

        # Choose C, calculate R
        self.c = 100e-9  # 100nF
        self.r = 1 / (omega * self.c)

    def frequency_response(self, freq: float) -> complex:
        """Calculate frequency response.

        Args:
            freq: Frequency in Hz

        Returns:
            Complex transfer function value
        """
        s = 1j * 2 * np.pi * freq
        omega_c = 2 * np.pi * self.cutoff_frequency

        if self.filter_type == "lowpass":
            # Butterworth lowpass
            h = self.passband_gain / (1 + (s / omega_c) ** self.order)
        elif self.filter_type == "highpass":
            h = (
                self.passband_gain
                * (s / omega_c) ** self.order
                / (1 + (s / omega_c) ** self.order)
            )
        else:
            h = self.passband_gain

        return h


class Comparator:
    """Op-amp as comparator with hysteresis."""

    def __init__(
        self,
        threshold: float = 0,
        hysteresis: float = 0,
        model: str = "LM358",
        vcc: float = 5.0,
    ):
        """Initialize comparator.

        Args:
            threshold: Switching threshold voltage
            hysteresis: Hysteresis voltage width
            model: Op-amp model
            vcc: Supply voltage
        """
        self.threshold = threshold
        self.hysteresis = hysteresis
        self.model = model
        self.vcc = vcc

        # Calculate switching thresholds
        self.upper_threshold = threshold + hysteresis / 2
        self.lower_threshold = threshold - hysteresis / 2

    def compare(self, vin: float, current_state: bool = False) -> float:
        """Compare input voltage to threshold.

        Args:
            vin: Input voltage
            current_state: Current output state for hysteresis

        Returns:
            Output voltage (0 or vcc)
        """
        if self.hysteresis > 0:
            # With hysteresis
            if current_state:
                # Currently high, switch low at lower threshold
                return self.vcc if vin > self.lower_threshold else 0
            else:
                # Currently low, switch high at upper threshold
                return self.vcc if vin > self.upper_threshold else 0
        else:
            # Simple comparison
            return self.vcc if vin > self.threshold else 0
