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

logger = logging.getLogger(__name__)


class CircuitSynthError(Exception):
    """Exception for circuit-synth integration errors."""

    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


def simulate_from_circuit_synth(json_data: Dict[str, Any]) -> SimulationResults:
    """
    Simulate a circuit from circuit-synth JSON data.

    This is the main integration point for circuit-synth to use circuit-simulation.
    Circuit-synth can call this function directly with its JSON output.

    Args:
        json_data: Circuit data in circuit-synth JSON format

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

        # Run simulation
        engine = SimulationEngine()
        results = engine.simulate_dc(circuit)

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
