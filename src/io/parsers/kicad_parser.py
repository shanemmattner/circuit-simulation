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
        lines = content.strip().split('\n')
        
        circuit_name = self._extract_circuit_name(content)
        circuit = Circuit(circuit_name)
        
        # Parse components section
        in_components = False
        in_nets = False
        current_component = None
        
        for line in lines:
            line = line.strip()
            
            if '(components' in line:
                in_components = True
                continue
            elif '(nets' in line:
                in_components = False
                in_nets = True
                continue
            elif line.startswith('(comp'):
                current_component = self._parse_component_line(line)
            elif line.startswith('(net'):
                self._parse_net_line(line, circuit)
                
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