"""
KiCad netlist parser for circuit import.

Adapted from circuit-synth netlist processing logic.
Handles KiCad netlist format (.net files) and converts to Circuit objects.
"""

import re
from typing import Dict, List, Optional, Any
from circuit_sim import Circuit


class KiCadParser:
    """Parse KiCad netlist files."""
    
    def __init__(self):
        self.components = {}
        self.nets = {}
        
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
            symbol = comp_data.get('part', '')
            value = comp_data.get('value', '1k')  # Default value
            
            # Find nodes for this component
            comp_nodes = self._find_component_nodes(ref, nets, node_map)
            
            # Map to circuit API with real nodes
            if symbol == 'R' or ref.startswith('R'):
                circuit.add_resistor(ref, comp_nodes.get('1', 1), comp_nodes.get('2', 0), value)
            elif symbol == 'C' or ref.startswith('C'):
                circuit.add_capacitor(ref, comp_nodes.get('1', 1), comp_nodes.get('2', 0), value)
            elif symbol == 'L' or ref.startswith('L'):
                circuit.add_inductor(ref, comp_nodes.get('1', 1), comp_nodes.get('2', 0), value)
                
        return circuit
    
    def _extract_circuit_name(self, content: str) -> str:
        """Extract circuit name from KiCad netlist."""
        # Look for design source
        match = re.search(r'\(source\s+([^)]+)\)', content)
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
        ref_match = re.search(r'\(ref\s+([^)]+)\)', line)
        value_match = re.search(r'\(value\s+([^)]+)\)', line)
        
        if ref_match:
            component = {
                'ref': ref_match.group(1),
                'value': value_match.group(1) if value_match else '',
            }
            
            # Store for net parsing
            self.components[component['ref']] = component
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
            value = comp_data.get('value', '1k')
            
            if ref.startswith('R') and ref not in [c.get('name', '') for c in circuit.components]:
                # Add resistor if not already added
                circuit.add_resistor(ref, '1', '0', value)  # Simplified nodes
            elif ref.startswith('C') and ref not in [c.get('name', '') for c in circuit.components]:
                circuit.add_capacitor(ref, '1', '0', value)
            elif ref.startswith('L') and ref not in [c.get('name', '') for c in circuit.components]:
                circuit.add_inductor(ref, '1', '0', value)
    
    def _extract_components_section(self, content: str) -> Dict[str, Dict[str, str]]:
        """Extract components from KiCad netlist."""
        components = {}
        
        # Split into lines and find components section
        lines = content.split('\n')
        in_components = False
        
        for line in lines:
            line = line.strip()
            
            if '(components' in line:
                in_components = True
                continue
            elif in_components and line.startswith('(comp'):
                # Extract ref and value from multi-line component
                ref_match = re.search(r'\(ref "([^"]+)"\)', line)
                if ref_match:
                    ref = ref_match.group(1)
                    components[ref] = {'ref': ref}
                    
            elif in_components and '(value' in line:
                # Extract value 
                value_match = re.search(r'\(value "([^"]*)"\)', line)
                if value_match and components:
                    last_ref = list(components.keys())[-1]
                    components[last_ref]['value'] = value_match.group(1)
                    
            elif in_components and '(libsource' in line:
                # Extract part type
                part_match = re.search(r'\(part "([^"]+)"\)', line)
                if part_match and components:
                    last_ref = list(components.keys())[-1] 
                    components[last_ref]['part'] = part_match.group(1)
                    
            elif in_components and line.startswith('(libparts'):
                break  # End of components section
                
        return components
    
    def _extract_nets_section(self, content: str) -> Dict[str, List[Dict[str, str]]]:
        """Extract net connectivity from KiCad netlist."""
        nets = {}
        
        # Split content and look for nets section
        lines = content.split('\n')
        in_nets = False
        current_net = None
        
        for line in lines:
            line = line.strip()
            
            if '(nets' in line:
                in_nets = True
                continue
            elif in_nets and line.startswith('(net'):
                # Extract net name
                name_match = re.search(r'\(name "([^"]+)"\)', line)
                if name_match:
                    current_net = name_match.group(1)
                    nets[current_net] = []
            elif in_nets and current_net and '(node' in line:
                # Extract node connection
                ref_match = re.search(r'\(ref "([^"]+)"\)', line)
                pin_match = re.search(r'\(pin "([^"]+)"\)', line)
                
                if ref_match and pin_match:
                    nets[current_net].append({
                        'component': ref_match.group(1),
                        'pin': pin_match.group(1)
                    })
        
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
            comp_ref = component.get('name', '')
            
            # Find which nets this component is connected to
            comp_nets = {}  # pin -> net_name
            for net_name, connections in nets.items():
                for conn in connections:
                    if conn['component'] == comp_ref:
                        comp_nets[conn['pin']] = net_name
            
            # Update component node assignments
            if len(comp_nets) >= 2:
                pins = sorted(comp_nets.keys())
                node1 = node_map.get(comp_nets[pins[0]], 1)
                node2 = node_map.get(comp_nets[pins[1]], 0)
                
                # Update component definition
                if 'node1' in component:
                    component['node1'] = node1
                    component['node2'] = node2
                elif 'positive' in component:
                    component['positive'] = node1 
                    component['negative'] = node2
    
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
    
    def _find_component_nodes(self, component_ref: str, nets: Dict, node_map: Dict) -> Dict[str, int]:
        """Find which nodes a component connects to.""" 
        comp_nodes = {}
        
        for net_name, connections in nets.items():
            for conn in connections:
                if conn['component'] == component_ref:
                    pin_num = conn['pin']
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
            if "Device:R" in symbol or ref.startswith('R'):
                circuit.add_resistor(ref, '1', '0', value or '1k')
            elif "Device:C" in symbol or ref.startswith('C'):
                circuit.add_capacitor(ref, '1', '0', value or '1uF')
            elif "Device:L" in symbol or ref.startswith('L'):
                circuit.add_inductor(ref, '1', '0', value or '1mH')
            elif "power:" in symbol or ref.startswith('V'):
                # Power supply symbols
                circuit.add_voltage_source(ref, '1', '0', value or '5V')
        
        # Store subcircuits for later processing
        subcircuits = data.get("subcircuits", [])
        if subcircuits:
            if not hasattr(circuit, '_subcircuits'):
                circuit._subcircuits = []
            circuit._subcircuits.extend(subcircuits)
            
        return circuit
    
    def import_subcircuit(self, subcircuit_data: Dict[str, Any]) -> Circuit:
        """Import individual subcircuit for simulation."""
        return self.import_from_dict(subcircuit_data)