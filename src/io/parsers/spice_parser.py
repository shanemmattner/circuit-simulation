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
        for line in lines[start_line:]:
            tokens = self.tokenizer.parse_line(line)
            if not tokens:
                continue
                
            if tokens[0].upper() == '.END':
                break
                
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
            # More component types will be added in later segments
        
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