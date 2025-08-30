"""
PySpice circuit builder.

Converts our simplified Circuit representation to PySpice format.
"""

from typing import Any, Dict, Set
import logging

from ..circuit import Circuit
from ..parser import parse_value
from ..smart_spice_mapper import SmartSpiceMapper

logger = logging.getLogger(__name__)


class PySpiceBuilder:
    """Builds PySpice circuits from our Circuit representation."""

    def __init__(self):
        """Initialize the builder."""
        self._pyspice_available = self._check_pyspice()
        self._mapper = SmartSpiceMapper()
        self._loaded_models: Set[str] = set()

    def _check_pyspice(self) -> bool:
        """Check if PySpice is available."""
        try:
            import importlib.util

            # Check if PySpice can be imported
            spec = importlib.util.find_spec("PySpice")
            return spec is not None
        except (ImportError, ValueError):
            return False

    def build_circuit(self, circuit: Circuit, for_ac_analysis: bool = False) -> Any:
        """
        Convert our Circuit to a PySpice Circuit.

        Args:
            circuit: Our Circuit representation
            for_ac_analysis: If True, use SinusoidalVoltageSource for AC analysis

        Returns:
            PySpice Circuit object

        Raises:
            ImportError: If PySpice is not installed
            ValueError: If circuit has invalid components
        """
        if not self._pyspice_available:
            raise ImportError(
                "PySpice is not installed. Install it with: pip install PySpice"
            )

        from PySpice.Spice.Netlist import Circuit as PySpiceCircuit

        # Create PySpice circuit
        pyspice_circuit = PySpiceCircuit(circuit.name)

        # Load SPICE model definitions first
        self._load_required_models(pyspice_circuit, circuit)

        # Track component counts for unique naming
        component_counts: Dict[str, int] = {}

        # Process each component
        for comp in circuit.components:
            comp_type = comp["type"]

            if comp_type == "voltage_source":
                self._add_voltage_source(pyspice_circuit, comp, component_counts, for_ac_analysis)
            elif comp_type == "current_source":
                self._add_current_source(pyspice_circuit, comp, component_counts)
            elif comp_type == "resistor":
                self._add_resistor(pyspice_circuit, comp, component_counts)
            elif comp_type == "capacitor":
                self._add_capacitor(pyspice_circuit, comp, component_counts)
            elif comp_type == "inductor":
                self._add_inductor(pyspice_circuit, comp, component_counts)
            elif comp_type == "bjt_transistor":
                self._add_bjt_transistor(pyspice_circuit, comp, component_counts)
            elif comp_type == "diode":
                self._add_diode(pyspice_circuit, comp, component_counts)
            elif comp_type == "opamp":
                self._add_opamp(pyspice_circuit, comp, component_counts)
            elif comp_type == "mosfet":
                self._add_mosfet(pyspice_circuit, comp, component_counts)
            else:
                raise ValueError(f"Unknown component type: {comp_type}")

        return pyspice_circuit

    def _get_component_id(self, comp: Dict, counts: Dict[str, int]) -> str:
        """Get unique component identifier."""
        # Use provided name if it doesn't start with the type prefix
        name = comp.get("name", "")
        comp_type = comp["type"]

        # Map component types to SPICE prefixes
        type_prefixes = {
            "voltage_source": "V",
            "current_source": "I",
            "resistor": "R",
            "capacitor": "C",
            "inductor": "L",
        }

        prefix = type_prefixes.get(comp_type, "X")

        # If name starts with correct prefix, use it as-is
        if name.upper().startswith(prefix):
            return name

        # Otherwise, generate a unique name
        if comp_type not in counts:
            counts[comp_type] = 0
        counts[comp_type] += 1

        # If user provided a name, append it
        if name:
            return f"{prefix}{counts[comp_type]}_{name}"
        else:
            return f"{prefix}{counts[comp_type]}"

    def _node_to_pyspice(self, node: Any, pyspice_circuit: Any) -> Any:
        """Convert node identifier to PySpice format."""
        # Node 0 is ground in PySpice
        if node == 0 or node == "0" or str(node).lower() == "gnd":
            return pyspice_circuit.gnd
        return node

    def _add_voltage_source(self, pyspice_circuit: Any, comp: Dict, counts: Dict[str, int], for_ac_analysis: bool = False):
        """Add voltage source to PySpice circuit."""

        name = self._get_component_id(comp, counts)
        node1 = self._node_to_pyspice(comp["positive"], pyspice_circuit)
        node2 = self._node_to_pyspice(comp["negative"], pyspice_circuit)

        # Parse voltage value
        voltage = parse_value(comp["dc_value"])

        # Add to circuit (remove the prefix from name since PySpice adds it)
        if name.upper().startswith("V"):
            name = name[1:]  # Remove V prefix

        from PySpice.Unit import u_V

        if for_ac_analysis:
            # For AC analysis, use SinusoidalVoltageSource which properly generates AC netlist
            voltage_source = pyspice_circuit.SinusoidalVoltageSource(
                name, node1, node2, 
                amplitude=1 @ u_V  # 1V AC amplitude for small-signal analysis
            )
            
            # Track AC sources for identification
            if not hasattr(pyspice_circuit, '_ac_sources'):
                pyspice_circuit._ac_sources = []
            pyspice_circuit._ac_sources.append(voltage_source)
        else:
            # For DC and transient analysis, use regular voltage source
            voltage_source = pyspice_circuit.V(name, node1, node2, voltage @ u_V)

    def _add_current_source(
        self, pyspice_circuit: Any, comp: Dict, counts: Dict[str, int]
    ):
        """Add current source to PySpice circuit."""
        from PySpice.Unit import u_A

        name = self._get_component_id(comp, counts)
        node1 = self._node_to_pyspice(comp["positive"], pyspice_circuit)
        node2 = self._node_to_pyspice(comp["negative"], pyspice_circuit)

        # Parse current value
        current = parse_value(comp["dc_value"])

        # Add to circuit
        if name.upper().startswith("I"):
            name = name[1:]  # Remove I prefix

        # Use PySpice units correctly
        pyspice_circuit.I(name, node1, node2, current @ u_A)

    def _add_resistor(self, pyspice_circuit: Any, comp: Dict, counts: Dict[str, int]):
        """Add resistor to PySpice circuit."""
        from PySpice.Unit import u_Ohm

        name = self._get_component_id(comp, counts)
        node1 = self._node_to_pyspice(comp["node1"], pyspice_circuit)
        node2 = self._node_to_pyspice(comp["node2"], pyspice_circuit)

        # Parse resistance value
        resistance = parse_value(comp["resistance"])

        # Add to circuit
        if name.upper().startswith("R"):
            name = name[1:]  # Remove R prefix

        # Use PySpice units correctly
        pyspice_circuit.R(name, node1, node2, resistance @ u_Ohm)

    def _add_capacitor(self, pyspice_circuit: Any, comp: Dict, counts: Dict[str, int]):
        """Add capacitor to PySpice circuit."""
        from PySpice.Unit import u_F

        name = self._get_component_id(comp, counts)
        node1 = self._node_to_pyspice(comp["node1"], pyspice_circuit)
        node2 = self._node_to_pyspice(comp["node2"], pyspice_circuit)

        # Parse capacitance value
        capacitance = parse_value(comp["capacitance"])

        # Add to circuit
        if name.upper().startswith("C"):
            name = name[1:]  # Remove C prefix

        # Use PySpice units correctly
        pyspice_circuit.C(name, node1, node2, capacitance @ u_F)

    def _add_inductor(self, pyspice_circuit: Any, comp: Dict, counts: Dict[str, int]):
        """Add inductor to PySpice circuit."""
        from PySpice.Unit import u_H

        name = self._get_component_id(comp, counts)
        node1 = self._node_to_pyspice(comp["node1"], pyspice_circuit)
        node2 = self._node_to_pyspice(comp["node2"], pyspice_circuit)

        # Parse inductance value
        inductance = parse_value(comp["inductance"])

        # Add to circuit
        if name.upper().startswith("L"):
            name = name[1:]  # Remove L prefix

        # Use PySpice units correctly
        pyspice_circuit.L(name, node1, node2, inductance @ u_H)

    def _add_bjt_transistor(
        self, pyspice_circuit: Any, comp: Dict, counts: Dict[str, int]
    ):
        """Add BJT transistor to PySpice circuit."""
        name = self._get_component_id(comp, counts)
        collector = self._node_to_pyspice(comp["collector"], pyspice_circuit)
        base = self._node_to_pyspice(comp["base"], pyspice_circuit)
        emitter = self._node_to_pyspice(comp["emitter"], pyspice_circuit)

        # Get model name
        model = comp.get("model", "2N3904")

        # Add to circuit
        if name.upper().startswith("Q"):
            name = name[1:]  # Remove Q prefix

        # Add BJT transistor
        pyspice_circuit.BJT(name, collector, base, emitter, model=model)

    def _add_diode(self, pyspice_circuit: Any, comp: Dict, counts: Dict[str, int]):
        """Add diode to PySpice circuit."""
        name = self._get_component_id(comp, counts)
        anode = self._node_to_pyspice(comp["anode"], pyspice_circuit)
        cathode = self._node_to_pyspice(comp["cathode"], pyspice_circuit)

        # Get model name
        model = comp.get("model", "1N4148")

        # Add to circuit
        if name.upper().startswith("D"):
            name = name[1:]  # Remove D prefix

        # Add diode
        pyspice_circuit.Diode(name, anode, cathode, model=model)

    def _add_opamp(self, pyspice_circuit: Any, comp: Dict, counts: Dict[str, int]):
        """Add op-amp to PySpice circuit."""
        name = self._get_component_id(comp, counts)
        output = self._node_to_pyspice(comp["output"], pyspice_circuit)
        input_neg = self._node_to_pyspice(comp["input_negative"], pyspice_circuit)
        input_pos = self._node_to_pyspice(comp["input_positive"], pyspice_circuit)
        vdd = self._node_to_pyspice(comp["vdd"], pyspice_circuit)
        vss = self._node_to_pyspice(comp["vss"], pyspice_circuit)

        # Get model name
        model = comp.get("model", "LM358")

        # Add to circuit
        if name.upper().startswith("U"):
            name = name[1:]  # Remove U prefix

        # Add op-amp (using subcircuit model)
        pyspice_circuit.X(name, model, output, input_neg, input_pos, vdd, vss)

    def _add_mosfet(self, pyspice_circuit: Any, comp: Dict, counts: Dict[str, int]):
        """Add MOSFET to PySpice circuit."""
        name = self._get_component_id(comp, counts)
        drain = self._node_to_pyspice(comp["drain"], pyspice_circuit)
        gate = self._node_to_pyspice(comp["gate"], pyspice_circuit)
        source = self._node_to_pyspice(comp["source"], pyspice_circuit)

        # Get model name
        model = comp.get("model", "2N7000")

        # Add to circuit
        if name.upper().startswith("M"):
            name = name[1:]  # Remove M prefix

        # Add MOSFET
        pyspice_circuit.MOSFET(name, drain, gate, source, model=model)

    def _load_required_models(self, pyspice_circuit: Any, circuit: Circuit):
        """Load SPICE model definitions for all components that need them."""
        required_models = set()

        # Collect all model names needed
        for comp in circuit.components:
            comp_type = comp["type"]

            if comp_type in ["bjt_transistor", "diode", "mosfet"]:
                model_name = comp.get("model")
                if model_name:
                    required_models.add(model_name)

        # Load each required model
        for model_name in required_models:
            if model_name not in self._loaded_models:
                self._load_spice_model(pyspice_circuit, model_name)
                self._loaded_models.add(model_name)

    def _load_spice_model(self, pyspice_circuit: Any, model_name: str):
        """Load a specific SPICE model definition into the circuit."""
        try:
            # For now, always use generic models since KiCad models have compatibility issues
            # TODO: Improve KiCad model parsing to handle manufacturer-specific syntax
            self._add_generic_model(pyspice_circuit, model_name)
            logger.info(f"📚 Using built-in model for {model_name}")

        except Exception as e:
            logger.error(f"❌ Failed to load model {model_name}: {e}")
            self._add_generic_model(pyspice_circuit, model_name)

    def _add_generic_model(self, pyspice_circuit: Any, model_name: str):
        """Add generic SPICE model when specific model not found."""
        # Basic generic models for common components
        generic_models = {
            "2N3904": ".model 2N3904 NPN(BF=300 BR=4 IS=6.734e-15 VAF=74.03 IKF=0.2847 ISE=6.734e-15)",
            "2N3906": ".model 2N3906 PNP(BF=200 BR=4 IS=1.41e-15 VAF=18.7 IKF=0.2847 ISE=1.41e-15)",
            "1N4148": ".model 1N4148 D(IS=2.52e-9 N=1.752 CJO=4e-12 M=0.4 TT=20e-9)",
            "1N4007": ".model 1N4007 D(IS=76.9e-9 N=2 CJO=26.5e-12 M=0.44 TT=8.67e-6)",
            "2N7000": ".model 2N7000 NMOS(VTO=2.0 KP=300e-6 LAMBDA=0.02 CGSO=7e-11 CGDO=1e-11)",
            "BS250": ".model BS250 PMOS(VTO=-2.5 KP=190e-6 LAMBDA=0.02 CGSO=7e-11 CGDO=1e-11)",
        }

        if model_name in generic_models:
            pyspice_circuit.raw_spice += f"\n{generic_models[model_name]}"
        else:
            # Ultra-generic fallback
            if model_name.upper().startswith(
                ("2N39", "BC5", "2N22")
            ):  # Common NPN patterns
                pyspice_circuit.raw_spice += (
                    f"\n.model {model_name} NPN(BF=200 IS=1e-14 VAF=100)"
                )
            elif model_name.upper().startswith(("2N39", "BC5")):  # Common PNP patterns
                pyspice_circuit.raw_spice += (
                    f"\n.model {model_name} PNP(BF=200 IS=1e-14 VAF=100)"
                )
            elif "N" in model_name.upper():  # Diode pattern
                pyspice_circuit.raw_spice += f"\n.model {model_name} D(IS=1e-14 N=1)"
            else:
                logger.warning(f"No generic model available for {model_name}")

        logger.debug(f"Added generic model for {model_name}")

    def _is_valid_spice_model(self, model_definition: str) -> bool:
        """Check if SPICE model definition has valid syntax for ngspice."""
        # Check for problematic patterns in KiCad models
        invalid_patterns = [
            "[philips]",
            "[onsemi]",
            "[fairchild]",
            "[ti]",
            "[vishay]",  # Manufacturer tags
            "temp_adj",
            "temp_drift",  # Non-standard parameters
            "{",
            "}",  # Curly braces not supported
        ]

        model_lower = model_definition.lower()
        for pattern in invalid_patterns:
            if pattern.lower() in model_lower:
                logger.debug(f"Invalid pattern found in model: {pattern}")
                return False

        return True
    
    def fix_ac_netlist(self, pyspice_circuit: Any) -> str:
        """
        Fix PySpice netlist to include AC components for voltage sources.
        
        PySpice doesn't automatically include AC components in netlist generation,
        so we post-process the netlist to add them manually.
        
        Args:
            pyspice_circuit: PySpice Circuit object
            
        Returns:
            Fixed SPICE netlist string with proper AC components
        """
        # Get original netlist
        original_netlist = str(pyspice_circuit)
        
        # Check if there are AC sources to fix
        if not hasattr(pyspice_circuit, '_ac_sources') or not pyspice_circuit._ac_sources:
            return original_netlist
            
        # Split into lines for processing
        lines = original_netlist.split('\n')
        fixed_lines = []
        
        # Create mapping of voltage source names to AC values
        ac_source_map = {}
        for v_source in pyspice_circuit._ac_sources:
            if hasattr(v_source, 'ac') and hasattr(v_source, 'name'):
                # Extract AC magnitude (handle both unit and numeric values)
                ac_value = v_source.ac
                if hasattr(ac_value, '__float__'):
                    ac_magnitude = float(ac_value)
                else:
                    ac_magnitude = 1.0  # Default fallback
                    
                ac_source_map[v_source.name] = ac_magnitude
        
        # Process each line
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('V'):
                # This is a voltage source line - check if it needs AC component
                parts = stripped.split()
                if len(parts) >= 4:  # Vname node1 node2 dc_value
                    # The SPICE line format is "V1 1 0 1.0V", so parts[0] is the full name "V1"
                    v_full_name = parts[0]  # Keep the full name including V prefix
                    
                    # Check if this voltage source is in our AC source map
                    if v_full_name in ac_source_map:
                        ac_magnitude = ac_source_map[v_full_name]
                        # Convert: "V1 1 0 1.0V" -> "V1 1 0 DC 1.0V AC 1.0"
                        fixed_line = f"{parts[0]} {parts[1]} {parts[2]} DC {parts[3]} AC {ac_magnitude}"
                        fixed_lines.append(fixed_line)
                        continue
                        
            # Keep original line if no AC fix needed
            fixed_lines.append(line)
            
        return '\n'.join(fixed_lines)
