"""
KiCad netlist parser for circuit import.

Adapted from circuit-synth netlist processing logic.
Handles KiCad netlist format (.net files) and converts to Circuit objects.
"""

import re
from typing import Any, Dict, List, Optional

from circuit_sim import Circuit
from .import_result import ImportResult, ComponentFailure, ComponentWarning, FailureLevel, create_component_failure
from .value_extractor import ValueExtractor, ValueExtractionResult
from .format_detector import FormatDetector, FormatInfo


class KiCadParser:
    """Parse KiCad netlist files."""

    def __init__(self):
        self.components = {}
        self.nets = {}
        self.value_extractor = ValueExtractor()
        self.format_detector = FormatDetector()

    def parse_content(self, content: str) -> Circuit:
        """
        Parse KiCad netlist content.

        Args:
            content: Complete KiCad netlist as string

        Returns:
            Circuit object with parsed components
        """
        circuit_name = self._extract_circuit_name(content)
        circuit = Circuit(circuit_name)

        # Extract components and nets sections
        components = self._extract_components_section(content)
        nets = self._extract_nets_section(content)

        # Create components with proper node mapping
        node_map = self._create_node_mapping(nets)

        for ref, comp_data in components.items():
            symbol = comp_data.get("part", "")
            value = comp_data.get("value", "1k")  # Default value

            # Find nodes for this component
            comp_nodes = self._find_component_nodes(ref, nets, node_map)

            # Map to circuit API with real nodes
            if symbol == "R" or ref.startswith("R"):
                circuit.add_resistor(ref, comp_nodes.get("1", 1), comp_nodes.get("2", 0), value)
            elif symbol == "C" or ref.startswith("C"):
                circuit.add_capacitor(ref, comp_nodes.get("1", 1), comp_nodes.get("2", 0), value)
            elif symbol == "L" or ref.startswith("L"):
                circuit.add_inductor(ref, comp_nodes.get("1", 1), comp_nodes.get("2", 0), value)

        return circuit

    def parse_content_with_result(self, content: str) -> ImportResult:
        """
        Parse KiCad netlist content with detailed result tracking.
        
        This is the new robust parsing method that provides detailed
        information about what succeeded and what failed.
        
        Args:
            content: Complete KiCad netlist as string
            
        Returns:
            ImportResult with circuit and detailed success/failure information
        """
        # Initialize result tracker
        result = ImportResult()
        
        try:
            # Detect format first
            format_info = self.format_detector.detect_format(content)
            
            # Add format warnings to result
            for warning in format_info.warnings:
                result.add_parsing_error(f"Format detection: {warning}")
                
            if not format_info.supported:
                result.add_parsing_error(
                    f"Format {format_info.format_type} (KiCad {format_info.version.value}) "
                    f"has limited support"
                )
            
            # Extract basic info
            circuit_name = self._extract_circuit_name(content)
            result.circuit = Circuit(circuit_name)
            
            # Parse components with robust handling
            self._parse_components_robust(content, result, format_info)
            
            # Parse connectivity
            nets = self._extract_nets_section(content)
            if nets:
                self._apply_connectivity_robust(result.circuit, nets, result)
            else:
                result.add_parsing_error("No nets section found - components will have default connections")
                
        except Exception as e:
            # Critical parsing error
            failure = create_component_failure(
                "PARSER",
                f"Critical parsing error: {str(e)}",
                FailureLevel.CRITICAL,
                suggestion="Check if netlist is valid KiCad format"
            )
            result.add_failure(failure)
            
        return result
        
    def detect_format(self, content: str) -> FormatInfo:
        """Public method to detect format without parsing."""
        return self.format_detector.detect_format(content)
        
    def _parse_components_robust(self, content: str, result: ImportResult, format_info: FormatInfo):
        """Parse components using robust value extraction."""
        try:
            components = self._extract_components_section(content)
            
            for ref, comp_data in components.items():
                try:
                    self._process_single_component_robust(ref, comp_data, content, result)
                except Exception as e:
                    failure = create_component_failure(
                        ref,
                        f"Failed to process component: {str(e)}",
                        FailureLevel.ERROR,
                        suggestion="Check component definition in netlist"
                    )
                    result.add_failure(failure)
                    
        except Exception as e:
            result.add_parsing_error(f"Failed to extract components section: {str(e)}")
            
    def _process_single_component_robust(self, ref: str, comp_data: dict, full_content: str, result: ImportResult):
        """Process a single component with robust value extraction and error handling."""
        
        # Extract component type
        symbol = comp_data.get("part", "")
        
        # First try to use the already-extracted value from component data
        extracted_value = comp_data.get("value", "")
        
        if extracted_value and extracted_value.strip() and extracted_value != '""':
            # We have a good value from the component extraction
            value_result = type('ValueResult', (), {
                'value': extracted_value,
                'confidence': 0.9,
                'method': 'component_extraction',
                'warning': None
            })()
        else:
            # Fall back to robust value extraction on raw content
            value_result = self.value_extractor.extract_value(
                full_content, 
                ref, 
                symbol
            )
        
        # Handle value extraction results
        if value_result.warning:
            warning = ComponentWarning(
                component_ref=ref,
                warning_message=value_result.warning,
                action_taken=f"Used value: {value_result.value}"
            )
            result.add_warning(warning)
        
        if not value_result.value:
            failure = create_component_failure(
                ref,
                "Could not determine component value",
                FailureLevel.ERROR,
                suggestion=f"Add value for {ref} in KiCad schematic"
            )
            result.add_failure(failure)
            return
            
        # Create component based on type
        try:
            success = self._create_circuit_component(
                result.circuit, 
                ref, 
                symbol, 
                value_result.value
            )
            
            if success:
                result.add_success(ref)
            else:
                failure = create_component_failure(
                    ref,
                    f"Unsupported component type: {symbol}",
                    FailureLevel.ERROR,
                    suggestion=f"Component type {symbol} not yet supported - add manually after import"
                )
                result.add_failure(failure)
                
        except Exception as e:
            failure = create_component_failure(
                ref,
                f"Error creating component: {str(e)}",
                FailureLevel.ERROR
            )
            result.add_failure(failure)
            
    def _create_circuit_component(self, circuit: Circuit, ref: str, symbol: str, value: str) -> bool:
        """Create appropriate circuit component. Returns True if successful."""
        
        # Default nodes - will be updated by connectivity analysis
        node1, node2 = 1, 0
        
        try:
            if symbol == "R" or ref.startswith("R"):
                circuit.add_resistor(ref, node1, node2, value)
                return True
            elif symbol == "C" or ref.startswith("C"):
                circuit.add_capacitor(ref, node1, node2, value)
                return True
            elif symbol == "L" or ref.startswith("L"):
                circuit.add_inductor(ref, node1, node2, value)
                return True
            elif symbol in ["V", "VDC"] or ref.startswith("V"):
                circuit.add_voltage_source(ref, node1, node2, value)
                return True
            elif symbol == "I" or ref.startswith("I"):
                circuit.add_current_source(ref, node1, node2, value)
                return True
            else:
                # Unsupported component type
                return False
                
        except Exception:
            return False
            
    def _apply_connectivity_robust(self, circuit: Circuit, nets: dict, result: ImportResult):
        """Apply network connectivity with error handling."""
        try:
            node_map = self._create_node_mapping(nets)
            
            # Update each component's connections
            for component in circuit.components:
                comp_ref = component.get("name", "")
                if not comp_ref:
                    continue
                    
                try:
                    comp_nodes = self._find_component_nodes(comp_ref, nets, node_map)
                    
                    if len(comp_nodes) >= 2:
                        pins = sorted(comp_nodes.keys())
                        node1 = comp_nodes[pins[0]]
                        node2 = comp_nodes[pins[1]]
                        
                        # Update component nodes
                        self._update_component_nodes(component, node1, node2)
                    else:
                        warning = ComponentWarning(
                            component_ref=comp_ref,
                            warning_message="Insufficient pin connections found",
                            action_taken="Using default node connections"
                        )
                        result.add_warning(warning)
                        
                except Exception as e:
                    warning = ComponentWarning(
                        component_ref=comp_ref,
                        warning_message=f"Failed to update connectivity: {str(e)}",
                        action_taken="Using default connections"
                    )
                    result.add_warning(warning)
                    
        except Exception as e:
            result.add_parsing_error(f"Failed to apply connectivity: {str(e)}")
            
    def _update_component_nodes(self, component: dict, node1: int, node2: int):
        """Update component node assignments."""
        if "node1" in component:
            component["node1"] = node1
            component["node2"] = node2
        elif "positive" in component:
            component["positive"] = node1
            component["negative"] = node2
        # Add more component types as needed

    def _extract_circuit_name(self, content: str) -> str:
        """Extract circuit name from KiCad netlist."""
        # Look for design source
        match = re.search(r"\(source\s+([^)]+)\)", content)
        if match:
            source_path = match.group(1)
            # Extract filename without path and extension
            import os

            name = os.path.splitext(os.path.basename(source_path))[0]
            return name
        return "Imported KiCad Circuit"

    def _parse_component_line(self, line: str) -> Optional[Dict]:
        """Parse KiCad component definition."""
        # Basic component parsing - will be enhanced
        ref_match = re.search(r"\(ref\s+([^)]+)\)", line)
        value_match = re.search(r"\(value\s+([^)]+)\)", line)

        if ref_match:
            component = {
                "ref": ref_match.group(1),
                "value": value_match.group(1) if value_match else "",
            }

            # Store for net parsing
            self.components[component["ref"]] = component
            return component

        return None

    def _parse_net_line(self, line: str, circuit: Circuit):
        """Parse KiCad net definition."""
        # Extract net name
        name_match = re.search(r'\(name\s+"?([^)"]+)"?\)', line)
        if not name_match:
            return

        net_name = name_match.group(1)

        # For now, just add basic components we find
        # This is a simplified version - full implementation in next segments
        for ref, comp_data in self.components.items():
            value = comp_data.get("value", "1k")

            if ref.startswith("R") and ref not in [c.get("name", "") for c in circuit.components]:
                # Add resistor if not already added
                circuit.add_resistor(ref, "1", "0", value)  # Simplified nodes
            elif ref.startswith("C") and ref not in [c.get("name", "") for c in circuit.components]:
                circuit.add_capacitor(ref, "1", "0", value)
            elif ref.startswith("L") and ref not in [c.get("name", "") for c in circuit.components]:
                circuit.add_inductor(ref, "1", "0", value)

    def _extract_components_section(self, content: str) -> Dict[str, Dict[str, str]]:
        """Extract components from KiCad netlist."""
        components = {}

        # Split into lines and find components section
        lines = content.split("\n")
        in_components = False

        for line in lines:
            line = line.strip()

            if "(components" in line:
                in_components = True
                continue
            elif in_components and line.startswith("(comp"):
                # Extract ref and value from multi-line component
                # Handle both quoted and unquoted references
                ref_patterns = [
                    r'\(ref "([^"]+)"\)',  # Quoted: (ref "R1")
                    r'\(ref ([^)]+)\)'     # Unquoted: (ref R1)
                ]
                ref = None
                for pattern in ref_patterns:
                    ref_match = re.search(pattern, line)
                    if ref_match:
                        ref = ref_match.group(1).strip()
                        break
                        
                if ref:
                    components[ref] = {"ref": ref}

            elif in_components and line.strip().startswith("(value"):
                # Extract value - handle quoted and unquoted
                # Only match lines that START with (value, not nested values
                value_patterns = [
                    r'^\s*\(value "([^"]*)"\)',  # Quoted: (value "10k")  
                    r'^\s*\(value ([^)]+)\)'     # Unquoted: (value 10k)
                ]
                value = None
                for pattern in value_patterns:
                    value_match = re.search(pattern, line)
                    if value_match:
                        value = value_match.group(1).strip()
                        break
                        
                if value and components:
                    last_ref = list(components.keys())[-1]
                    # Only set if we don't already have a value (prevent overwrites)
                    if "value" not in components[last_ref]:
                        components[last_ref]["value"] = value

            elif in_components and "(libsource" in line:
                # Extract part type - handle quoted and unquoted
                part_patterns = [
                    r'\(part "([^"]+)"\)',  # Quoted: (part "R")
                    r'\(part ([^)]+)\)'     # Unquoted: (part R)
                ]
                part = None
                for pattern in part_patterns:
                    part_match = re.search(pattern, line)
                    if part_match:
                        part = part_match.group(1).strip()
                        break
                        
                if part and components:
                    last_ref = list(components.keys())[-1]
                    components[last_ref]["part"] = part

            elif in_components and line.startswith("(libparts"):
                break  # End of components section

        return components

    def _extract_nets_section(self, content: str) -> Dict[str, List[Dict[str, str]]]:
        """Extract net connectivity from KiCad netlist."""
        nets = {}

        # Split content and look for nets section
        lines = content.split("\n")
        in_nets = False
        current_net = None

        for line in lines:
            line = line.strip()

            if "(nets" in line:
                in_nets = True
                continue
            elif in_nets and line.startswith("(net"):
                # Extract net name
                name_match = re.search(r'\(name "([^"]+)"\)', line)
                if name_match:
                    current_net = name_match.group(1)
                    nets[current_net] = []
            elif in_nets and current_net and "(node" in line:
                # Extract node connection
                ref_match = re.search(r'\(ref "([^"]+)"\)', line)
                pin_match = re.search(r'\(pin "([^"]+)"\)', line)

                if ref_match and pin_match:
                    nets[current_net].append(
                        {"component": ref_match.group(1), "pin": pin_match.group(1)}
                    )

        return nets

    def _apply_net_connectivity(self, circuit: Circuit, nets: Dict, components: Dict):
        """Update component node connections based on net analysis."""
        # Create node mapping from nets
        node_map = {}
        node_counter = 1

        # Map each net name to a node number
        for net_name in nets.keys():
            if net_name == "GND":
                node_map[net_name] = 0  # Ground is always node 0
            else:
                node_map[net_name] = node_counter
                node_counter += 1

        # Update each component's nodes based on net connections
        for component in circuit.components:
            comp_ref = component.get("name", "")

            # Find which nets this component is connected to
            comp_nets = {}  # pin -> net_name
            for net_name, connections in nets.items():
                for conn in connections:
                    if conn["component"] == comp_ref:
                        comp_nets[conn["pin"]] = net_name

            # Update component node assignments
            if len(comp_nets) >= 2:
                pins = sorted(comp_nets.keys())
                node1 = node_map.get(comp_nets[pins[0]], 1)
                node2 = node_map.get(comp_nets[pins[1]], 0)

                # Update component definition
                if "node1" in component:
                    component["node1"] = node1
                    component["node2"] = node2
                elif "positive" in component:
                    component["positive"] = node1
                    component["negative"] = node2

    def _create_node_mapping(self, nets: Dict) -> Dict[str, int]:
        """Create mapping from net names to node numbers."""
        node_map = {}
        node_counter = 1

        for net_name in nets.keys():
            if net_name == "GND":
                node_map[net_name] = 0  # Ground is always 0
            else:
                node_map[net_name] = node_counter
                node_counter += 1

        return node_map

    def _find_component_nodes(
        self, component_ref: str, nets: Dict, node_map: Dict
    ) -> Dict[str, int]:
        """Find which nodes a component connects to."""
        comp_nodes = {}

        for net_name, connections in nets.items():
            for conn in connections:
                if conn["component"] == component_ref:
                    pin_num = conn["pin"]
                    comp_nodes[pin_num] = node_map.get(net_name, 1)

        return comp_nodes


class CircuitSynthImporter:
    """Import circuit-synth JSON format."""

    def import_from_dict(self, data: Dict[str, Any]) -> Circuit:
        """Import circuit from circuit-synth JSON dictionary."""
        circuit_name = data.get("name", "Imported Circuit")
        circuit = Circuit(circuit_name)

        # Parse components
        components_data = data.get("components", {})
        for ref, comp_data in components_data.items():
            symbol = comp_data.get("symbol", "")
            value = comp_data.get("value", "")

            # Map common symbols to circuit components
            if "Device:R" in symbol or ref.startswith("R"):
                circuit.add_resistor(ref, "1", "0", value or "1k")
            elif "Device:C" in symbol or ref.startswith("C"):
                circuit.add_capacitor(ref, "1", "0", value or "1uF")
            elif "Device:L" in symbol or ref.startswith("L"):
                circuit.add_inductor(ref, "1", "0", value or "1mH")
            elif "power:" in symbol or ref.startswith("V"):
                # Power supply symbols
                circuit.add_voltage_source(ref, "1", "0", value or "5V")

        # Store subcircuits for later processing
        subcircuits = data.get("subcircuits", [])
        if subcircuits:
            if not hasattr(circuit, "_subcircuits"):
                circuit._subcircuits = []
            circuit._subcircuits.extend(subcircuits)

        return circuit

    def import_subcircuit(self, subcircuit_data: Dict[str, Any]) -> Circuit:
        """Import individual subcircuit for simulation."""
        return self.import_from_dict(subcircuit_data)
