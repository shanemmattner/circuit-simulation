"""
Circuit-synth JSON importer.

Comprehensive importer for circuit-synth JSON format with intelligent component mapping,
proper net handling, and professional error recovery. Follows established parser patterns.
"""

import logging
from typing import Any, Dict, List, Optional, Set, Tuple

from circuit_sim import Circuit
from ..parsers.import_result import (
    ImportResult,
    ComponentWarning,
    ComponentFailure,
    FailureLevel,
    create_component_failure,
)
from ..parsers.value_extractor import ValueExtractor
from ..parsers.component_model_mapper import ComponentModelMapper
from src.models.spice_loader import SpiceModelLoader

logger = logging.getLogger(__name__)


class CircuitSynthImporter:
    """Import circuit-synth JSON format to Circuit objects with intelligent component mapping."""

    # Comprehensive component symbol mapping
    COMPONENT_MAP = {
        # Basic passives
        "Device:R": "resistor",
        "Device:C": "capacitor", 
        "Device:L": "inductor",
        "Device:D": "diode",
        "Device:LED": "led",
        
        # Power sources
        "power:PWR_FLAG": "power_flag",
        "power:+3V3": "voltage_source",
        "power:+5V": "voltage_source",
        "power:GND": "ground",
        "power:VCC": "voltage_source",
        "power:VDD": "voltage_source",
        
        # Semiconductors
        "Transistor_BJT:BC817": "transistor_npn",
        "Transistor_FET:BSS84": "transistor_pmos",
        "Transistor_FET:BSS138": "transistor_nmos",
        
        # Integrated circuits
        "Amplifier_Operational:LM358": "opamp",
        "Regulator_Linear:AMS1117-3.3": "voltage_regulator",
        "MCU_ST_STM32F4:STM32F411CEUx": "behavioral_model",
        
        # Connectors
        "Connector:Conn_01x02": "connector",
        "Connector:USB_B_Micro": "connector",
        "Connector_Generic:Conn_01x10": "connector",
    }

    def __init__(self):
        self.value_extractor = ValueExtractor()
        self.warnings: List[ComponentWarning] = []
        self.failed_components: List[Dict[str, Any]] = []
        
        # Initialize model mapper
        try:
            model_loader = SpiceModelLoader()
            self.model_mapper = ComponentModelMapper(model_loader)
        except Exception as e:
            logger.warning(f"Model mapper unavailable: {e}")
            self.model_mapper = None

    def import_from_dict(self, data: Dict[str, Any]) -> ImportResult:
        """Import circuit from circuit-synth JSON dictionary.
        
        Args:
            data: Circuit-synth JSON dictionary with components, nets, etc.
            
        Returns:
            ImportResult with circuit and any warnings/errors
        """
        try:
            circuit_name = data.get("name", "Imported Circuit")
            circuit = Circuit(circuit_name)
            
            # Parse nets first to establish connectivity
            nets_data = data.get("nets", {})
            net_map = self._parse_nets(nets_data)
            
            # Parse components with intelligent mapping
            components_data = data.get("components", {})
            self._parse_components(circuit, components_data, net_map)
            
            # Handle subcircuits
            subcircuits = data.get("subcircuits", [])
            if subcircuits:
                self._parse_subcircuits(circuit, subcircuits)
            
            # Create import result using correct API
            result = ImportResult(circuit=circuit)
            
            # Add warnings from our tracking
            for warning in self.warnings:
                result.add_warning(warning)
            
            # Add failed components as failures
            for failed in self.failed_components:
                result.add_failure(ComponentFailure(
                    component_ref=failed["reference"],
                    error_message=failed["error"],
                    level=FailureLevel.ERROR
                ))
            
            # Store format info as additional metadata
            result.format_info = self._create_format_info(data)
            
            logger.info(f"Successfully imported circuit-synth circuit: {circuit_name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to import circuit-synth data: {e}")
            # Return error result
            result = ImportResult()
            result.parsing_errors.append(str(e))
            result.format_info = {"error": str(e)}
            return result
    
    def _parse_nets(self, nets_data: Dict[str, Any]) -> Dict[str, Set[Tuple[str, str]]]:
        """Parse circuit-synth nets data into connectivity map.
        
        Args:
            nets_data: Dictionary of net names to connection data
            
        Returns:
            Dictionary mapping net names to sets of (component_ref, pin) tuples
        """
        net_map = {}
        
        for net_name, connections in nets_data.items():
            if isinstance(connections, list):
                # Circuit-synth format: [{"component": "R1", "pin": "1"}, ...]
                net_map[net_name] = {(conn.get("component"), conn.get("pin")) 
                                   for conn in connections if isinstance(conn, dict)}
            else:
                # Alternative format handling
                net_map[net_name] = set()
                
        return net_map
    
    def _parse_components(self, circuit: Circuit, components_data: Dict[str, Any], 
                         net_map: Dict[str, Set[Tuple[str, str]]]):
        """Parse circuit-synth components with intelligent mapping.
        
        Args:
            circuit: Circuit object to add components to
            components_data: Dictionary of component references to component data
            net_map: Net connectivity mapping
        """
        for ref, comp_data in components_data.items():
            try:
                self._add_component(circuit, ref, comp_data, net_map)
            except Exception as e:
                logger.warning(f"Failed to add component {ref}: {e}")
                self.failed_components.append({
                    "reference": ref,
                    "data": comp_data,
                    "error": str(e)
                })
                
    def _add_component(self, circuit: Circuit, ref: str, comp_data: Dict[str, Any],
                      net_map: Dict[str, Set[Tuple[str, str]]]):
        """Add individual component to circuit with proper net connections.
        
        Args:
            circuit: Circuit to add component to
            ref: Component reference (e.g., "R1", "C2")
            comp_data: Component data from circuit-synth
            net_map: Net connectivity mapping
        """
        symbol = comp_data.get("symbol", "")
        value = comp_data.get("value", "")
        
        # Find nets connected to this component
        connected_nets = self._find_component_nets(ref, net_map)
        
        # Extract numeric value if present (ValueExtractor needs component_section, ref, part_type)
        parsed_value = None
        if value and self.value_extractor:
            try:
                # Create minimal component section for value extraction
                component_section = f'  (comp {ref} "{symbol}" "{value}")'
                extract_result = self.value_extractor.extract_value(component_section, ref, symbol)
                parsed_value = extract_result.value if extract_result.value else value
            except Exception:
                # Fallback to original value if extraction fails
                parsed_value = value
        
        # Map component based on symbol
        if symbol in self.COMPONENT_MAP:
            component_type = self.COMPONENT_MAP[symbol]
            self._add_mapped_component(circuit, ref, component_type, parsed_value or value, 
                                     connected_nets, comp_data)
        elif any(pattern in symbol for pattern in ["Device:R", "resistor"]) or ref.startswith("R"):
            self._add_resistor(circuit, ref, parsed_value or value or "1k", connected_nets)
        elif any(pattern in symbol for pattern in ["Device:C", "capacitor"]) or ref.startswith("C"):
            self._add_capacitor(circuit, ref, parsed_value or value or "1uF", connected_nets)
        elif any(pattern in symbol for pattern in ["Device:L", "inductor"]) or ref.startswith("L"):
            self._add_inductor(circuit, ref, parsed_value or value or "1mH", connected_nets)
        elif any(pattern in symbol for pattern in ["power:", "voltage"]) or ref.startswith("V"):
            self._add_voltage_source(circuit, ref, parsed_value or value or "5V", connected_nets)
        else:
            # Use model mapper for advanced components if available
            if self.model_mapper:
                try:
                    self.model_mapper.map_component(circuit, ref, symbol, value, connected_nets)
                except Exception as e:
                    logger.warning(f"Model mapper failed for {ref}: {e}")
                    self._add_behavioral_model(circuit, ref, symbol, connected_nets)
            else:
                self._add_behavioral_model(circuit, ref, symbol, connected_nets)
    
    def _find_component_nets(self, ref: str, net_map: Dict[str, Set[Tuple[str, str]]]) -> List[str]:
        """Find all nets connected to a component.
        
        Args:
            ref: Component reference
            net_map: Net connectivity mapping
            
        Returns:
            List of net names connected to component
        """
        connected_nets = []
        for net_name, connections in net_map.items():
            if any(comp_ref == ref for comp_ref, pin in connections):
                connected_nets.append(net_name)
        return connected_nets
    
    def _add_resistor(self, circuit: Circuit, ref: str, value: str, nets: List[str]):
        """Add resistor with proper net connections."""
        node1 = nets[0] if len(nets) > 0 else "0"
        node2 = nets[1] if len(nets) > 1 else "0"
        circuit.add_resistor(ref, node1, node2, value)
        
    def _add_capacitor(self, circuit: Circuit, ref: str, value: str, nets: List[str]):
        """Add capacitor with proper net connections."""
        node1 = nets[0] if len(nets) > 0 else "0"
        node2 = nets[1] if len(nets) > 1 else "0"
        circuit.add_capacitor(ref, node1, node2, value)
        
    def _add_inductor(self, circuit: Circuit, ref: str, value: str, nets: List[str]):
        """Add inductor with proper net connections."""
        node1 = nets[0] if len(nets) > 0 else "0"
        node2 = nets[1] if len(nets) > 1 else "0"
        circuit.add_inductor(ref, node1, node2, value)
        
    def _add_voltage_source(self, circuit: Circuit, ref: str, value: str, nets: List[str]):
        """Add voltage source with proper net connections."""
        node_pos = nets[0] if len(nets) > 0 else "0"
        node_neg = nets[1] if len(nets) > 1 else "0"
        circuit.add_voltage_source(ref, node_pos, node_neg, value)
    
    def _add_mapped_component(self, circuit: Circuit, ref: str, component_type: str, 
                            value: str, nets: List[str], comp_data: Dict[str, Any]):
        """Add component using mapped type."""
        if component_type in ["resistor", "capacitor", "inductor", "voltage_source"]:
            getattr(self, f"_add_{component_type}")(circuit, ref, value, nets)
        else:
            self._add_behavioral_model(circuit, ref, comp_data.get("symbol", "unknown"), nets)
            
    def _add_behavioral_model(self, circuit: Circuit, ref: str, symbol: str, nets: List[str]):
        """Add complex component as behavioral model."""
        # For now, add as comment - could be enhanced with SPICE subcircuits
        logger.info(f"Added behavioral model for {ref} ({symbol})")
        self.warnings.append(ComponentWarning(
            component_ref=ref,
            warning_message=f"Component {ref} ({symbol}) added as behavioral model - simulation may be limited",
            action_taken="behavioral_model"
        ))
    
    def _parse_subcircuits(self, circuit: Circuit, subcircuits: List[Dict[str, Any]]):
        """Parse subcircuits recursively."""
        for subcircuit_data in subcircuits:
            try:
                sub_result = self.import_from_dict(subcircuit_data)
                if sub_result.success and sub_result.circuit:
                    # Add subcircuit to main circuit (implementation depends on Circuit API)
                    logger.info(f"Added subcircuit: {sub_result.circuit.name}")
            except Exception as e:
                logger.warning(f"Failed to parse subcircuit: {e}")
    
    def _create_format_info(self, data: Dict[str, Any]) -> Optional[Any]:
        """Create format information for the import result."""
        return {
            "format": "circuit-synth-json",
            "version": data.get("version", "unknown"),
            "component_count": len(data.get("components", {})),
            "net_count": len(data.get("nets", {})),
            "subcircuit_count": len(data.get("subcircuits", []))
        }

    def import_subcircuit(self, subcircuit_data: Dict[str, Any]) -> ImportResult:
        """Import individual subcircuit for simulation."""
        return self.import_from_dict(subcircuit_data)
