"""
Circuit-synth integration for circuit-simulation.

This module provides a clean interface for circuit-synth to use circuit-simulation
as a tool for simulating circuits. The libraries remain completely independent.
"""

from typing import Dict, Any
import logging

from circuit_sim.circuit import Circuit
from circuit_sim.simulator.engine import SimulationEngine
from circuit_sim.simulator.results import SimulationResults
from circuit_sim.smart_spice_mapper import SmartSpiceMapper, ComponentMapping
# Import SpiceParser with correct absolute path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from io.parsers.spice_parser import SpiceParser

logger = logging.getLogger(__name__)


class CircuitSynthError(Exception):
    """Exception for circuit-synth integration errors."""

    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


def simulate_from_circuit_synth(
    json_data: Dict[str, Any], analysis_type: str = "dc"
) -> SimulationResults:
    """
    Simulate a circuit from circuit-synth JSON data.

    This is the main integration point for circuit-synth to use circuit-simulation.
    Circuit-synth can call this function directly with its JSON output.

    Args:
        json_data: Circuit data in circuit-synth JSON format
        analysis_type: Type of analysis ("dc", "ac", "transient")

    Returns:
        SimulationResults: Results from the simulation

    Raises:
        CircuitSynthError: If the JSON data is invalid or simulation fails

    Example:
        >>> circuit_data = {
        ...     "name": "RC Filter",
        ...     "components": {
        ...         "R1": {
        ...             "symbol": "Device:R",
        ...             "value": "1k",
        ...             "ref": "R1",
        ...             "footprint": "Resistor_SMD:R_0603_1608Metric"
        ...         },
        ...         "C1": {
        ...             "symbol": "Device:C",
        ...             "value": "100nF",
        ...             "ref": "C1",
        ...             "footprint": "Capacitor_SMD:C_0603_1608Metric"
        ...         }
        ...     },
        ...     "nets": {
        ...         "INPUT": [{"component": "R1", "pin": {"number": "1", "name": "~", "type": "passive"}}],
        ...         "OUTPUT": [
        ...             {"component": "R1", "pin": {"number": "2", "name": "~", "type": "passive"}},
        ...             {"component": "C1", "pin": {"number": "1", "name": "~", "type": "passive"}}
        ...         ],
        ...         "GND": [{"component": "C1", "pin": {"number": "2", "name": "~", "type": "passive"}}]
        ...     }
        ... }
        >>> results = simulate_from_circuit_synth(circuit_data)
    """
    try:
        # Strict validation
        _validate_circuit_synth_json(json_data)

        # Convert circuit-synth JSON to circuit-simulation format
        circuit = _convert_to_circuit(json_data)

        # Run simulation based on analysis type
        engine = SimulationEngine()
        
        if analysis_type == "dc":
            results = engine.simulate_dc(circuit)
        elif analysis_type == "ac":
            # AC analysis with sensible defaults for filter circuits
            results = engine.simulate_ac(
                circuit, 
                start_frequency=1.0,      # 1 Hz
                stop_frequency=1e6,       # 1 MHz  
                points_per_decade=20,     # High resolution
                variation="dec"
            )
        elif analysis_type == "transient":
            # Transient analysis with sensible defaults
            results = engine.simulate_transient(
                circuit,
                stop_time=1e-3,          # 1 ms
                step_time=1e-6           # 1 μs
            )
        else:
            raise ValueError(f"Unsupported analysis type: {analysis_type}")

        return results

    except Exception as e:
        # Exception with structured details
        error_details = {
            "error_type": type(e).__name__,
            "json_data": json_data,
            "validation_errors": _get_validation_errors(json_data),
        }
        raise CircuitSynthError(
            f"Circuit-synth simulation failed: {str(e)}", error_details
        )


def simulate_from_spice(spice_netlist: str, analysis_type: str = "dc") -> SimulationResults:
    """
    Simulate a circuit from SPICE netlist string.
    
    This provides direct SPICE simulation capability for circuit-synth integration.
    Circuit-synth can export SPICE netlists and simulate them directly.
    
    Args:
        spice_netlist: Complete SPICE netlist as string
        analysis_type: Type of analysis ("dc", "ac", "transient")
    
    Returns:
        SimulationResults: Results from the simulation
        
    Raises:
        CircuitSynthError: If the SPICE netlist is invalid or simulation fails
    
    Example:
        >>> spice_netlist = '''
        ... * Power Regulation Test
        ... .title Power_Regulation_Test
        ... XU1 VBUS 0 VCC_3V3 AMS1117_3V3
        ... CC1 VBUS VCC_3V3 10uF
        ... CC2 VBUS VCC_3V3 22uF
        ... RR1 VBUS VCC_3V3 16.5
        ... VIN VBUS 0 DC 5V
        ... .DC VIN 3 6 0.1
        ... .END
        ... '''
        >>> results = simulate_from_spice(spice_netlist)
    """
    try:
        # Create a temporary file for the SPICE netlist
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cir', delete=False) as f:
            f.write(spice_netlist)
            spice_file_path = f.name
        
        try:
            # Parse the SPICE netlist
            parser = SpiceParser()
            circuit = parser.parse_file(spice_file_path)
            
            # Run simulation based on analysis type
            engine = SimulationEngine()
            
            if analysis_type == "dc":
                results = engine.simulate_dc(circuit)
            elif analysis_type == "ac":
                results = engine.simulate_ac(
                    circuit, 
                    start_frequency=1.0,      # 1 Hz
                    stop_frequency=1e6,       # 1 MHz  
                    points_per_decade=20,     # High resolution
                    variation="dec"
                )
            elif analysis_type == "transient":
                results = engine.simulate_transient(
                    circuit,
                    stop_time=1e-3,          # 1 ms
                    step_time=1e-6           # 1 μs
                )
            else:
                raise ValueError(f"Unsupported analysis type: {analysis_type}")

            return results
            
        finally:
            # Clean up temporary file
            if os.path.exists(spice_file_path):
                os.unlink(spice_file_path)
                
    except Exception as e:
        error_details = {
            "error_type": type(e).__name__,
            "analysis_type": analysis_type,
            "spice_preview": spice_netlist[:500] + "..." if len(spice_netlist) > 500 else spice_netlist
        }
        raise CircuitSynthError(
            f"SPICE simulation failed: {str(e)}", error_details
        )


def _validate_circuit_synth_json(json_data: Dict[str, Any]) -> None:
    """Strict validation of circuit-synth JSON format."""
    required_fields = ["name", "components", "nets"]

    for field in required_fields:
        if field not in json_data:
            raise ValueError(f"Missing required field: {field}")

    if not isinstance(json_data["components"], dict):
        raise ValueError("'components' must be a dictionary")

    if not isinstance(json_data["nets"], dict):
        raise ValueError("'nets' must be a dictionary")

    # Validate components have required fields
    for comp_name, comp_data in json_data["components"].items():
        if "symbol" not in comp_data:
            raise ValueError(f"Component {comp_name} missing 'symbol' field")
        if "value" not in comp_data:
            raise ValueError(f"Component {comp_name} missing 'value' field")

    # Validate nets reference existing components
    for net_name, connections in json_data["nets"].items():
        if not isinstance(connections, list):
            raise ValueError(f"Net {net_name} must be a list of connections")

        for connection in connections:
            if not isinstance(connection, dict):
                raise ValueError(f"Net {net_name} connection must be a dictionary")
            if "component" not in connection:
                raise ValueError(f"Net {net_name} connection missing 'component' field")
            if "pin" not in connection:
                raise ValueError(f"Net {net_name} connection missing 'pin' field")

            comp_name = connection["component"]
            if comp_name not in json_data["components"]:
                raise ValueError(
                    f"Net {net_name} references unknown component {comp_name}"
                )

            # Validate pin format - can be string or dict with "number" field
            pin = connection["pin"]
            if isinstance(pin, dict):
                if "number" not in pin:
                    raise ValueError(f"Net {net_name} pin dict missing 'number' field")
            elif not isinstance(pin, str):
                raise ValueError(
                    f"Net {net_name} pin must be string or dict with 'number'"
                )


def _convert_to_circuit(json_data: Dict[str, Any]) -> Circuit:
    """Convert circuit-synth JSON to Circuit object using smart SPICE mapping."""
    circuit = Circuit(json_data["name"])
    mapper = SmartSpiceMapper()

    successful_mappings = 0
    failed_mappings = 0

    # Process all components
    for comp_name, comp_data in json_data["components"].items():
        symbol = comp_data["symbol"]
        value = comp_data.get("value", "")
        ref = comp_data.get("ref", comp_name)
        footprint = comp_data.get("footprint", "")

        # Get pin connections for this component
        pins = _get_component_pins(comp_name, json_data["nets"])

        # Use smart mapper to resolve component
        mapping = mapper.resolve_component(symbol, value, ref, pins, footprint)

        if mapping.spice_model is None and mapping.error_message:
            logger.warning(f"⚠️  {mapping.error_message}")
            failed_mappings += 1
            continue

        # Add component to circuit using mapped method
        success = _add_component_to_circuit(circuit, mapping)
        if success:
            successful_mappings += 1
            confidence_icon = (
                "🎯"
                if mapping.confidence >= 0.9
                else "✅" if mapping.confidence >= 0.7 else "🔄"
            )
            fallback_note = " (fallback)" if mapping.fallback_used else ""
            logger.info(
                f"{confidence_icon} {ref} ({symbol}) → {mapping.spice_model}{fallback_note}"
            )
        else:
            failed_mappings += 1

    logger.info(
        f"Circuit conversion: {successful_mappings} successful, {failed_mappings} failed"
    )

    return circuit


def _add_component_to_circuit(circuit: Circuit, mapping: ComponentMapping) -> bool:
    """Add a component to the circuit using the resolved mapping."""
    try:
        method = getattr(circuit, mapping.circuit_method)

        # Basic components (R, L, C, V) - use value directly
        if mapping.circuit_method in [
            "add_resistor",
            "add_capacitor",
            "add_inductor",
            "add_voltage_source",
        ]:
            method(
                mapping.component_name,
                mapping.pins[0],
                mapping.pins[1],
                mapping.spice_model,
            )

        # BJT transistors
        elif mapping.circuit_method == "add_bjt_transistor":
            method(
                mapping.component_name,
                mapping.pins[0],
                mapping.pins[1],
                mapping.pins[2],  # C, B, E
                model=mapping.spice_model,
            )

        # MOSFETs
        elif mapping.circuit_method == "add_mosfet":
            method(
                mapping.component_name,
                mapping.pins[0],
                mapping.pins[1],
                mapping.pins[2],  # D, G, S
                model=mapping.spice_model,
            )

        # Diodes
        elif mapping.circuit_method == "add_diode":
            method(
                mapping.component_name,
                mapping.pins[0],
                mapping.pins[1],  # A, K
                model=mapping.spice_model,
            )

        # Op-amps
        elif mapping.circuit_method == "add_opamp":
            method(
                mapping.component_name,
                mapping.pins[0],
                mapping.pins[1],
                mapping.pins[2],  # out, in-, in+
                mapping.pins[3],
                mapping.pins[4],  # V+, V-
                model=mapping.spice_model,
            )

        else:
            logger.error(f"Unknown circuit method: {mapping.circuit_method}")
            return False

        return True

    except Exception as e:
        logger.error(f"Failed to add component {mapping.component_name}: {e}")
        return False


def _get_component_pins(comp_name: str, nets: Dict[str, Any]) -> list:
    """Get the pin connections for a component."""
    pin_to_net = {}

    for net_name, connections in nets.items():
        for connection in connections:
            if connection["component"] == comp_name:
                pin_data = connection["pin"]

                # Handle both formats: string pin or dict with "number" field
                if isinstance(pin_data, dict):
                    pin_num = pin_data["number"]
                else:
                    pin_num = pin_data

                pin_to_net[pin_num] = net_name

    # Return pins in order (1, 2, 3, ...)
    pins = []
    for pin_num in sorted(pin_to_net.keys()):
        pins.append(pin_to_net[pin_num])

    return pins


def _get_validation_errors(json_data: Dict[str, Any]) -> list:
    """Get detailed validation errors for debugging."""
    errors = []

    try:
        _validate_circuit_synth_json(json_data)
    except Exception as e:
        errors.append(str(e))

    return errors
