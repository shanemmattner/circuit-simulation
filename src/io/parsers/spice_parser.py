"""
SPICE netlist parser for circuit import.

Handles standard SPICE syntax including:
- Component definitions (R, L, C, V, I, M, Q, D)
- Subcircuit definitions (.SUBCKT/.ENDS)
- Model definitions (.MODEL)
- Line continuations (+)
- Comments (*) 
"""

import re
from typing import List, Optional, Dict, Any
from circuit_sim import Circuit


class SpiceTokenizer:
    """Tokenize SPICE netlist lines."""
    
    def parse_line(self, line: str) -> List[str]:
        """
        Parse a single SPICE line into tokens.
        
        Args:
            line: Raw SPICE line
            
        Returns:
            List of tokens (empty for comments/empty lines)
        """
        # Remove leading/trailing whitespace
        line = line.strip()
        
        # Skip empty lines
        if not line:
            return []
            
        # Skip comment lines
        if line.startswith('*'):
            return []
            
        # Remove inline comments (after semicolon)
        if ';' in line:
            line = line.split(';')[0].strip()
            
        # Split by whitespace
        tokens = line.split()
        
        return tokens
    
    def parse_continued_lines(self, lines: List[str]) -> List[str]:
        """
        Handle SPICE line continuations (+ prefix).
        
        Args:
            lines: List of lines including continuations
            
        Returns:
            Combined tokens from all lines
        """
        combined_line = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith('+') and combined_line:
                # Continuation line - remove + and append
                combined_line += " " + line[1:].strip()
            else:
                if combined_line:
                    break  # End of continuation
                combined_line = line
        
        return self.parse_line(combined_line)


class SpiceParser:
    """Full SPICE netlist parser."""
    
    def __init__(self):
        self.tokenizer = SpiceTokenizer()
        self.models = {}
        self.subcircuits = {}
        
    def parse_content(self, content: str) -> Circuit:
        """
        Parse SPICE netlist content.
        
        Args:
            content: Complete SPICE netlist as string
            
        Returns:
            Circuit object with parsed components
        """
        lines = content.strip().split('\n')
        
        # Find title (first non-empty line, could be comment)
        circuit_name = "Untitled Circuit"
        title_line = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line:
                if line.startswith('*'):
                    # Extract title from comment
                    circuit_name = line[1:].strip()
                    title_line = i
                else:
                    # First non-comment line is title
                    if title_line is None:
                        circuit_name = line
                        title_line = i
                break
        
        circuit = Circuit(circuit_name)
        
        # Parse each line after title
        start_line = (title_line + 1) if title_line is not None else 1
        
        i = start_line
        while i < len(lines):
            line = lines[i]
            tokens = self.tokenizer.parse_line(line)
            if not tokens:
                i += 1
                continue
                
            if tokens[0].upper() == '.END':
                break
            elif tokens[0].upper() == '.MODEL':
                self._parse_model_definition(tokens)
                i += 1
                continue
            elif tokens[0].upper() == '.SUBCKT':
                i = self._parse_subcircuit_definition(tokens, lines, i)
                continue
                
            # Parse component based on first character
            first_char = tokens[0][0].upper()
            
            if first_char == 'R':
                self._parse_resistor(circuit, tokens)
            elif first_char == 'C':
                self._parse_capacitor(circuit, tokens)
            elif first_char == 'L':
                self._parse_inductor(circuit, tokens)
            elif first_char == 'V':
                self._parse_voltage_source(circuit, tokens)
            elif first_char == 'I':
                self._parse_current_source(circuit, tokens)
            elif first_char == 'Q':
                self._parse_bjt_transistor(circuit, tokens)
            elif first_char == 'M':
                self._parse_mosfet(circuit, tokens)
            elif first_char == 'D':
                self._parse_diode(circuit, tokens)
            
            i += 1  # Move to next line
        
        return circuit
    
    def _parse_resistor(self, circuit: Circuit, tokens: List[str]):
        """Parse resistor: R<name> n1 n2 <value>"""
        if len(tokens) >= 4:
            name, node1, node2, value = tokens[:4]
            circuit.add_resistor(name, node1, node2, value)
    
    def _parse_capacitor(self, circuit: Circuit, tokens: List[str]):
        """Parse capacitor: C<name> n1 n2 <value>"""
        if len(tokens) >= 4:
            name, node1, node2, value = tokens[:4]
            circuit.add_capacitor(name, node1, node2, value)
    
    def _parse_inductor(self, circuit: Circuit, tokens: List[str]):
        """Parse inductor: L<name> n1 n2 <value>"""
        if len(tokens) >= 4:
            name, node1, node2, value = tokens[:4] 
            circuit.add_inductor(name, node1, node2, value)
    
    def _parse_voltage_source(self, circuit: Circuit, tokens: List[str]):
        """Parse voltage source: V<name> n+ n- <value>"""
        if len(tokens) >= 4:
            name, node_pos, node_neg = tokens[:3]
            # Handle different voltage source formats
            if len(tokens) >= 5 and tokens[3].upper() == 'DC':
                value = tokens[4]
            else:
                value = tokens[3]
            circuit.add_voltage_source(name, node_pos, node_neg, value)
    
    def _parse_current_source(self, circuit: Circuit, tokens: List[str]):
        """Parse current source: I<name> n+ n- <value>"""
        if len(tokens) >= 4:
            name, node_pos, node_neg = tokens[:3]
            if len(tokens) >= 5 and tokens[3].upper() == 'DC':
                value = tokens[4]  
            else:
                value = tokens[3]
            circuit.add_current_source(name, node_pos, node_neg, value)
    
    def _parse_model_definition(self, tokens: List[str]):
        """Parse .MODEL definition: .MODEL name type(param=val ...)"""
        if len(tokens) >= 3:
            model_name = tokens[1]
            model_type = tokens[2].split('(')[0]  # Remove parameters from type
            
            # Extract parameters from parentheses
            params = {}
            if len(tokens) > 3:
                param_str = ' '.join(tokens[3:])
                if '(' in param_str and ')' in param_str:
                    param_part = param_str.split('(')[1].split(')')[0]
                    for param in param_part.split():
                        if '=' in param:
                            key, val = param.split('=', 1)
                            try:
                                params[key] = float(val)
                            except ValueError:
                                params[key] = val
            
            self.models[model_name] = {
                "type": model_type,
                "parameters": params
            }
    
    def _parse_bjt_transistor(self, circuit: Circuit, tokens: List[str]):
        """Parse BJT transistor: Q<name> nc nb ne <model>"""
        if len(tokens) >= 5:
            name, collector, base, emitter, model = tokens[:5]
            # Store as metadata - will be enhanced when we extend Circuit API
            if not hasattr(circuit, '_advanced_components'):
                circuit._advanced_components = []
            circuit._advanced_components.append({
                'name': name,
                'type': 'transistor',
                'collector': collector,
                'base': base,
                'emitter': emitter,
                'model': model
            })
    
    def _parse_mosfet(self, circuit: Circuit, tokens: List[str]):
        """Parse MOSFET: M<name> nd ng ns nb <model>"""
        if len(tokens) >= 6:
            name, drain, gate, source, bulk, model = tokens[:6]
            circuit.add_component({
                'name': name,
                'type': 'mosfet',
                'drain': drain,
                'gate': gate,
                'source': source,
                'bulk': bulk,
                'model': model
            })
    
    def _parse_diode(self, circuit: Circuit, tokens: List[str]):
        """Parse diode: D<name> n+ n- <model>"""
        if len(tokens) >= 4:
            name, anode, cathode, model = tokens[:4]
            circuit.add_component({
                'name': name,
                'type': 'diode',
                'anode': anode,
                'cathode': cathode,
                'model': model
            })
    
    def _parse_subcircuit_definition(self, tokens: List[str], all_lines: List[str], start_index: int) -> int:
        """Parse .SUBCKT definition and find matching .ENDS"""
        if len(tokens) >= 3:
            subckt_name = tokens[1]
            ports = tokens[2:]  # All remaining tokens are port names
            
            # Find matching .ENDS and collect subcircuit lines
            subckt_lines = []
            end_index = start_index + 1
            
            for j in range(start_index + 1, len(all_lines)):
                line = all_lines[j].strip()
                if line.upper().startswith('.ENDS'):
                    end_index = j
                    break
                subckt_lines.append(all_lines[j])
            
            self.subcircuits[subckt_name] = {
                "ports": ports,
                "components": subckt_lines,
                "parsed_components": []  # Will be filled when subcircuit is instantiated
            }
            
            return end_index  # Return index after .ENDS
        
        return start_index + 1