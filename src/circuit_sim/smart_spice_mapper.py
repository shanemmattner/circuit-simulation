"""
Smart SPICE Model Mapper for KiCad Components

Provides intelligent mapping from KiCad component symbols to SPICE models
using the KiCad-Spice-Library database (50K+ models).
"""

import re
import logging
from pathlib import Path
from typing import Dict, Optional, Set, List, NamedTuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Path to KiCad-Spice-Library submodule
KICAD_SPICE_LIBRARY = (
    Path(__file__).parent.parent.parent / "submodules" / "KiCad-Spice-Library"
)


@dataclass
class ComponentMapping:
    """Result of component → SPICE model mapping."""

    component_name: str
    spice_model: Optional[str]
    circuit_method: str  # "add_bjt_transistor", "add_diode", etc.
    pins: List[str]
    confidence: float  # 0.0-1.0
    fallback_used: bool
    error_message: Optional[str] = None
    transistor_type: Optional[str] = None  # For BJT transistors


class PinMapping(NamedTuple):
    """Pin mapping for a component type."""

    circuit_method: str
    pin_names: List[str]  # In order expected by circuit method


class SmartSpiceMapper:
    """Maps KiCad components to SPICE models using KiCad-Spice-Library."""

    def __init__(self):
        self.supported_models: Set[str] = set()
        self.model_cache: Dict[str, str] = {}  # Cache for loaded .lib file contents

        # Component type mappings
        self.component_mappings = {
            # Basic components (no SPICE model needed)
            "Device:R": PinMapping("add_resistor", ["pin1", "pin2"]),
            "Device:C": PinMapping("add_capacitor", ["pin1", "pin2"]),
            "Device:L": PinMapping("add_inductor", ["pin1", "pin2"]),
            "Device:V": PinMapping("add_voltage_source", ["positive", "negative"]),
            # Components requiring SPICE models
            "Device:D": PinMapping("add_diode", ["anode", "cathode"]),
            "Device:Q_NPN_CBE": PinMapping(
                "add_bjt_transistor", ["collector", "base", "emitter"]
            ),
            "Device:Q_PNP_CBE": PinMapping(
                "add_bjt_transistor", ["collector", "base", "emitter"]
            ),
            "Device:Q_NMOS_GDS": PinMapping("add_mosfet", ["drain", "gate", "source"]),
            "Device:Q_PMOS_GDS": PinMapping("add_mosfet", ["drain", "gate", "source"]),
        }

        # Symbol pattern mappings for op-amps
        self.opamp_patterns = [
            "Amplifier_Operational",
            "Amplifier_Audio",
            "Amplifier_Instrumentation",
            "Linear",
        ]

        # Default models for fallbacks
        self.default_models = {
            "Device:Q_NPN_CBE": "2N3904",
            "Device:Q_PNP_CBE": "2N3906",
            "Device:D": "1N4148",
            "Device:Q_NMOS_GDS": "2N7000",
            "Device:Q_PMOS_GDS": "BS250",
        }

        self.load_supported_models()

    def load_supported_models(self) -> None:
        """Load all supported SPICE model names from KiCad-Spice-Library."""
        supported_file = KICAD_SPICE_LIBRARY / "Supported.txt"

        if not supported_file.exists():
            logger.warning(f"KiCad-Spice-Library not found at {KICAD_SPICE_LIBRARY}")
            logger.warning("Falling back to basic built-in models only")
            return

        try:
            with open(supported_file, "r", encoding="utf-8", errors="ignore") as f:
                self.supported_models = {
                    line.strip().lower() for line in f if line.strip()
                }

            logger.info(
                f"Loaded {len(self.supported_models)} SPICE models from KiCad-Spice-Library"
            )

        except Exception as e:
            logger.error(f"Failed to load SPICE model database: {e}")

    def resolve_component(
        self, symbol: str, value: str, ref: str, pins: List[str], footprint: str = ""
    ) -> ComponentMapping:
        """
        Resolve KiCad component to SPICE model and circuit method.

        Args:
            symbol: KiCad symbol (e.g., "Device:Q_NPN_CBE")
            value: Component value (e.g., "2N3904", "1k", "100nF")
            ref: Reference designator (e.g., "Q1", "R1")
            pins: List of net names connected to component pins
            footprint: KiCad footprint (optional)

        Returns:
            ComponentMapping with model resolution results
        """

        # Handle basic components first (no SPICE model needed)
        if symbol in ["Device:R", "Device:C", "Device:L", "Device:V"]:
            return self._map_basic_component(symbol, value, ref, pins)

        # Handle components requiring SPICE models
        if symbol in self.component_mappings:
            return self._map_spice_component(symbol, value, ref, pins)

        # Handle op-amps (pattern-based matching)
        if any(pattern in symbol for pattern in self.opamp_patterns):
            return self._map_opamp_component(symbol, value, ref, pins)

        # Unknown component type
        return ComponentMapping(
            component_name=ref,
            spice_model=None,
            circuit_method="",
            pins=pins,
            confidence=0.0,
            fallback_used=False,
            error_message=f"Unsupported component type: {symbol}",
        )

    def _map_basic_component(
        self, symbol: str, value: str, ref: str, pins: List[str]
    ) -> ComponentMapping:
        """Map basic components (R, L, C, V) that don't need SPICE models."""

        pin_mapping = self.component_mappings[symbol]

        if len(pins) < len(pin_mapping.pin_names):
            return ComponentMapping(
                component_name=ref,
                spice_model=None,
                circuit_method="",
                pins=pins,
                confidence=0.0,
                fallback_used=False,
                error_message=f"Insufficient pins: {symbol} needs {len(pin_mapping.pin_names)}, got {len(pins)}",
            )

        return ComponentMapping(
            component_name=ref,
            spice_model=value,  # Value is used directly (1k, 100nF, 5V)
            circuit_method=pin_mapping.circuit_method,
            pins=pins[: len(pin_mapping.pin_names)],  # Take only needed pins
            confidence=1.0,
            fallback_used=False,
        )

    def _map_spice_component(
        self, symbol: str, value: str, ref: str, pins: List[str]
    ) -> ComponentMapping:
        """Map components that require SPICE models (transistors, diodes)."""

        pin_mapping = self.component_mappings[symbol]

        if len(pins) < len(pin_mapping.pin_names):
            return ComponentMapping(
                component_name=ref,
                spice_model=None,
                circuit_method="",
                pins=pins,
                confidence=0.0,
                fallback_used=False,
                error_message=f"Insufficient pins: {symbol} needs {len(pin_mapping.pin_names)}, got {len(pins)}",
            )

        # Find SPICE model using confidence-scored approach
        spice_model, confidence, fallback_used = self._find_spice_model(
            value, symbol, ref
        )

        # Handle transistor types for BJT components
        transistor_type = None
        if "Q_NPN_CBE" in symbol:
            transistor_type = "NPN"
        elif "Q_PNP_CBE" in symbol:
            transistor_type = "PNP"

        return ComponentMapping(
            component_name=ref,
            spice_model=spice_model,
            circuit_method=pin_mapping.circuit_method,
            pins=pins[: len(pin_mapping.pin_names)],
            confidence=confidence,
            fallback_used=fallback_used,
            transistor_type=transistor_type,
        )

    def _map_opamp_component(
        self, symbol: str, value: str, ref: str, pins: List[str]
    ) -> ComponentMapping:
        """Map operational amplifier components."""

        # Op-amps typically need 5 pins: [out, in-, in+, V+, V-]
        if len(pins) < 5:
            return ComponentMapping(
                component_name=ref,
                spice_model=None,
                circuit_method="",
                pins=pins,
                confidence=0.0,
                fallback_used=False,
                error_message=f"Op-amp needs 5 pins, got {len(pins)}",
            )

        spice_model, confidence, fallback_used = self._find_spice_model(
            value, symbol, ref
        )

        # Handle multi-unit op-amps (like LM358 dual op-amp)
        if self._is_multi_unit_opamp(spice_model or value):
            # For now, map to single op-amp, but note that it's multi-unit
            logger.info(
                f"Multi-unit op-amp {spice_model} mapped as single unit - consider creating {ref}A, {ref}B instances"
            )

        return ComponentMapping(
            component_name=ref,
            spice_model=spice_model,
            circuit_method="add_opamp",
            pins=pins[:5],  # [out, in-, in+, V+, V-]
            confidence=confidence,
            fallback_used=fallback_used,
        )

    def _find_spice_model(
        self, value: str, symbol: str, ref: str
    ) -> tuple[Optional[str], float, bool]:
        """
        Find best SPICE model using confidence-scored fallback chain.

        Returns:
            (model_name, confidence_score, fallback_used)
        """

        if not value:
            value = ""

        # 1. Exact value match (confidence: 1.0)
        if value.lower() in self.supported_models:
            return value, 1.0, False

        # 2. Pattern extraction from value (confidence: 0.9)
        model_patterns = [
            r"([A-Z0-9]+)",  # BC546, 2N3904, LM358
            r"([0-9]+[A-Z][0-9]+)",  # 2N3904, 1N4148
            r"(LM[0-9]+)",  # LM358, LM741
            r"(BC[0-9]+[A-Z]?)",  # BC546B, BC547
            r"([0-9]+N[0-9]+)",  # 1N4148, 2N7000
            r"(IRF[0-9]+)",  # IRF540, IRF9540
            r"(BS[0-9]+)",  # BS250
        ]

        for pattern in model_patterns:
            match = re.search(pattern, value.upper())
            if match:
                candidate = match.group(1)
                if candidate.lower() in self.supported_models:
                    return candidate, 0.9, False

        # 3. Symbol-based defaults (confidence: 0.7)
        if symbol in self.default_models:
            default_model = self.default_models[symbol]
            if default_model.lower() in self.supported_models:
                return default_model, 0.7, True

        # 4. Reference-based guessing (confidence: 0.5)
        ref_defaults = {
            "Q": "2N3904",  # Generic NPN
            "D": "1N4148",  # Generic diode
            "U": "LM358",  # Generic op-amp
        }

        if ref and ref[0] in ref_defaults:
            candidate = ref_defaults[ref[0]]
            if candidate.lower() in self.supported_models:
                return candidate, 0.5, True

        # No model found
        return None, 0.0, True

    def _is_multi_unit_opamp(self, model_name: str) -> bool:
        """Check if op-amp model is multi-unit (like LM358 dual op-amp)."""
        multi_unit_opamps = {
            "lm358",
            "lm324",
            "lm339",
            "lm393",
            "tl072",
            "tl074",
            "lm833",
            "ne5532",
            "opa2134",
            "ad8066",
        }

        if not model_name:
            return False

        return model_name.lower() in multi_unit_opamps

    def get_spice_lib_path(self, model_name: str) -> Optional[Path]:
        """Find the .lib file containing a specific SPICE model."""
        if not model_name or not KICAD_SPICE_LIBRARY.exists():
            return None

        # Search in Models directory structure
        search_paths = [
            KICAD_SPICE_LIBRARY / "Models" / "Transistor",
            KICAD_SPICE_LIBRARY / "Models" / "Diode",
            KICAD_SPICE_LIBRARY / "Models" / "Operational Amplifier",
            KICAD_SPICE_LIBRARY / "Models" / "Manufacturer",
            KICAD_SPICE_LIBRARY / "Models" / "uncategorized",
        ]

        for search_path in search_paths:
            if not search_path.exists():
                continue

            for lib_file in search_path.rglob("*.lib"):
                try:
                    with open(lib_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read().lower()
                        if f".model {model_name.lower()}" in content:
                            return lib_file
                except Exception as e:
                    logger.debug(f"Error reading {lib_file}: {e}")
                    continue

        return None

    def load_spice_model_definition(self, model_name: str) -> Optional[str]:
        """Load the full SPICE model definition from .lib files."""
        if model_name in self.model_cache:
            return self.model_cache[model_name]

        lib_path = self.get_spice_lib_path(model_name)
        if not lib_path:
            logger.warning(f"SPICE model {model_name} not found in library")
            return None

        try:
            with open(lib_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Extract the specific model definition
            pattern = rf"\.model\s+{re.escape(model_name)}\s+.*"
            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)

            if match:
                model_definition = match.group(0)
                self.model_cache[model_name] = model_definition
                logger.debug(f"Loaded SPICE model: {model_name}")
                return model_definition
            else:
                logger.warning(
                    f"Model definition for {model_name} not found in {lib_path}"
                )
                return None

        except Exception as e:
            logger.error(f"Failed to load model {model_name} from {lib_path}: {e}")
            return None
