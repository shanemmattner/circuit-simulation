"""
SPICE Model Library for Circuit Simulation

Copied and adapted from circuit-synth project.
Provides comprehensive library of SPICE models for common components.
"""

import logging
from dataclasses import dataclass
from typing import Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class SpiceModel:
    """Container for SPICE model parameters."""

    name: str
    model_type: str  # D, NPN, PNP, NMOS, PMOS, etc.
    parameters: Dict[str, float]
    description: str = ""
    manufacturer: str = ""
    datasheet_url: str = ""


class ModelLibrary:
    """SPICE model library for circuit simulations."""

    def __init__(self):
        self.models = {}
        self._load_default_models()

    def get_model(self, name: str) -> Optional[SpiceModel]:
        """Get a model by name."""
        return self.models.get(name)

    def add_model(self, model: SpiceModel):
        """Add a custom model to the library."""
        self.models[model.name] = model

    def list_models(self, model_type: Optional[str] = None) -> Dict[str, SpiceModel]:
        """List all models, optionally filtered by type."""
        if model_type:
            return {
                name: model
                for name, model in self.models.items()
                if model.model_type == model_type
            }
        return self.models.copy()

    def _load_default_models(self):
        """Load default SPICE models for common components."""

        # Diode Models
        self.models["1N4148"] = SpiceModel(
            name="1N4148",
            model_type="D",
            parameters={
                "IS": 2.52e-9,  # Saturation current
                "RS": 0.568,  # Series resistance
                "N": 1.752,  # Emission coefficient
                "TT": 4e-9,  # Transit time
                "CJO": 4e-12,  # Zero-bias junction capacitance
                "VJ": 0.7,  # Junction potential
                "M": 0.333,  # Grading coefficient
                "BV": 100,  # Reverse breakdown voltage
                "IBV": 0.1e-3,  # Current at breakdown
            },
            description="Fast switching diode",
            manufacturer="Various",
        )

        self.models["1N4007"] = SpiceModel(
            name="1N4007",
            model_type="D",
            parameters={
                "IS": 7.02e-9,
                "RS": 0.0341,
                "N": 1.8,
                "TT": 4.32e-6,
                "CJO": 18.5e-12,
                "VJ": 0.75,
                "M": 0.333,
                "BV": 1000,
                "IBV": 5e-6,
            },
            description="1A 1000V rectifier diode",
            manufacturer="Various",
        )

        self.models["LED_Red"] = SpiceModel(
            name="LED_Red",
            model_type="D",
            parameters={
                "IS": 1e-20,
                "RS": 2.5,
                "N": 1.5,
                "BV": 5,
                "IBV": 10e-6,
            },
            description="Red LED (Vf ~1.8V)",
        )

        # BJT Transistor Models
        self.models["2N3904"] = SpiceModel(
            name="2N3904",
            model_type="NPN",
            parameters={
                "IS": 6.734e-15,  # Saturation current
                "BF": 416.4,  # Forward current gain
                "NF": 1,  # Forward emission coefficient
                "VAF": 74.03,  # Forward Early voltage
                "IKF": 0.06678,  # Forward knee current
                "ISE": 6.734e-15,  # B-E leakage saturation current
                "NE": 1.259,  # B-E leakage emission coefficient
                "BR": 0.7371,  # Reverse current gain
                "NR": 1,  # Reverse emission coefficient
                "VAR": 50,  # Reverse Early voltage
                "RB": 10,  # Base resistance
                "RC": 1,  # Collector resistance
                "RE": 0.1,  # Emitter resistance
                "CJE": 4.493e-12,  # B-E zero-bias capacitance
                "CJC": 3.638e-12,  # B-C zero-bias capacitance
                "TF": 301.2e-12,  # Forward transit time
                "TR": 239.5e-9,  # Reverse transit time
            },
            description="General purpose NPN transistor",
            manufacturer="Various",
        )

        self.models["2N3906"] = SpiceModel(
            name="2N3906",
            model_type="PNP",
            parameters={
                "IS": 1.41e-15,
                "BF": 180.7,
                "NF": 1,
                "VAF": 35.99,
                "IKF": 0.08,
                "ISE": 3.31e-15,
                "NE": 1.5,
                "BR": 4.977,
                "NR": 1,
                "VAR": 50,
                "RB": 20,
                "RC": 2,
                "RE": 0.2,
                "CJE": 8.504e-12,
                "CJC": 4.962e-12,
                "TF": 466.5e-12,
                "TR": 51.35e-9,
            },
            description="General purpose PNP transistor",
            manufacturer="Various",
        )

        # MOSFET Models
        self.models["2N7000"] = SpiceModel(
            name="2N7000",
            model_type="NMOS",
            parameters={
                "VTO": 1.8,  # Threshold voltage
                "KP": 0.24,  # Transconductance parameter
                "GAMMA": 0.37,  # Body effect parameter
                "PHI": 0.65,  # Surface potential
                "LAMBDA": 0.01,  # Channel length modulation
                "RD": 1,  # Drain resistance
                "RS": 0.5,  # Source resistance
                "CBD": 35e-12,  # B-D junction capacitance
                "CBS": 35e-12,  # B-S junction capacitance
                "IS": 1e-14,  # Bulk junction saturation current
                "PB": 0.8,  # Bulk junction potential
                "CGSO": 88e-12,  # Gate-source overlap capacitance
                "CGDO": 88e-12,  # Gate-drain overlap capacitance
                "CGBO": 200e-12,  # Gate-bulk overlap capacitance
            },
            description="N-channel enhancement mode MOSFET",
            manufacturer="Various",
        )

        self.models["BS250"] = SpiceModel(
            name="BS250",
            model_type="PMOS",
            parameters={
                "VTO": -3.0,
                "KP": 0.12,
                "GAMMA": 0.4,
                "PHI": 0.65,
                "LAMBDA": 0.02,
                "RD": 2,
                "RS": 1,
                "CBD": 40e-12,
                "CBS": 40e-12,
                "IS": 1e-14,
                "PB": 0.8,
                "CGSO": 100e-12,
                "CGDO": 100e-12,
                "CGBO": 250e-12,
            },
            description="P-channel enhancement mode MOSFET",
            manufacturer="Various",
        )

        self.models["IRF540"] = SpiceModel(
            name="IRF540",
            model_type="NMOS",
            parameters={
                "VTO": 3.9,
                "KP": 20,
                "GAMMA": 0.5,
                "PHI": 0.65,
                "LAMBDA": 0.001,
                "RD": 0.044,
                "RS": 0.028,
                "CBD": 1700e-12,
                "CBS": 2100e-12,
            },
            description="Power NMOS transistor (28A, 100V)",
            manufacturer="Various",
        )

        # Default fallback models
        self.models["DefaultDiode"] = SpiceModel(
            name="DefaultDiode",
            model_type="D",
            parameters={"IS": 1e-12, "RS": 0.1, "N": 1.0},
            description="Generic diode model",
        )

        self.models["DefaultNPN"] = SpiceModel(
            name="DefaultNPN",
            model_type="NPN",
            parameters={"IS": 1e-14, "BF": 100, "VAF": 50},
            description="Generic NPN transistor",
        )

        self.models["DefaultPNP"] = SpiceModel(
            name="DefaultPNP",
            model_type="PNP",
            parameters={"IS": 1e-14, "BF": 100, "VAF": 50},
            description="Generic PNP transistor",
        )
