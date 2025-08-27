"""
Flexible value extraction for KiCad components using multiple fallback strategies.
"""

import re
from typing import Optional, List, Tuple
from dataclasses import dataclass


@dataclass
class ValueExtractionResult:
    """Result of attempting to extract a component value."""
    value: Optional[str]
    confidence: float  # 0.0 to 1.0
    method: str       # Which strategy worked
    warning: Optional[str] = None


class ValueExtractor:
    """
    Extract component values using multiple fallback strategies.
    Handles various KiCad netlist format variations gracefully.
    """
    
    def __init__(self):
        self.strategies = [
            self._extract_inline_value,
            self._extract_multiline_value,
            self._extract_from_component_block,
            self._extract_from_part_name,
            self._extract_default_value
        ]
    
    def extract_value(self, component_section: str, ref: str, part_type: str = "") -> ValueExtractionResult:
        """
        Try multiple strategies to extract component value.
        
        Args:
            component_section: Raw text containing component definition
            ref: Component reference (e.g., "R1")
            part_type: Component type if known (e.g., "R", "Device:R")
            
        Returns:
            ValueExtractionResult with best attempt at finding value
        """
        for strategy in self.strategies:
            result = strategy(component_section, ref, part_type)
            if result.value is not None:
                return result
        
        # If all strategies fail, return empty result with warning
        return ValueExtractionResult(
            value=None,
            confidence=0.0,
            method="no_strategy_worked",
            warning=f"Could not extract value for {ref} using any method"
        )
    
    def _extract_inline_value(self, content: str, ref: str, part_type: str) -> ValueExtractionResult:
        """Strategy 1: Look for (value "...") in same line as component."""
        # Look for value on same line - handle both quoted and unquoted
        patterns = [
            rf'\(comp.*?{re.escape(ref)}.*?\(value\s+"([^"]+)"\)',  # Quoted
            rf'\(comp.*?{re.escape(ref)}.*?\(value\s+([^)\s]+)\)'   # Unquoted
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                value = match.group(1).strip()
                # Skip empty values or quoted empty strings
                if value and value != "" and value != '""' and value != "''":
                    return ValueExtractionResult(
                        value=value,
                        confidence=0.9,
                        method="inline_value"
                    )
        
        return ValueExtractionResult(None, 0.0, "inline_value")
    
    def _extract_multiline_value(self, content: str, ref: str, part_type: str) -> ValueExtractionResult:
        """Strategy 2: Look for value on separate lines near the component."""
        
        # Find the component definition line
        comp_pattern = rf'\(comp.*?{re.escape(ref)}'
        comp_match = re.search(comp_pattern, content)
        
        if not comp_match:
            return ValueExtractionResult(None, 0.0, "multiline_value")
        
        # Look for value within next few lines
        start_pos = comp_match.start()
        
        # Get text from component line to end of next component or end of components section
        remaining_text = content[start_pos:]
        
        # Look for next component or end of section to limit search scope  
        next_comp = re.search(r'\(comp\s+\(ref\s+(?!' + re.escape(ref) + r')', remaining_text)
        end_components = re.search(r'\)\s*\((?:libparts|nets)', remaining_text)
        
        search_limit = min(
            next_comp.start() if next_comp else len(remaining_text),
            end_components.start() if end_components else len(remaining_text),
            1000  # Don't search more than 1000 chars
        )
        
        search_text = remaining_text[:search_limit]
        
        # Look for value in this limited scope
        value_pattern = r'\(value\s+"?([^")\s]+)"?\)'
        value_match = re.search(value_pattern, search_text)
        
        if value_match:
            value = value_match.group(1).strip()
            if value and value != "":
                return ValueExtractionResult(
                    value=value,
                    confidence=0.8,
                    method="multiline_value"
                )
        
        return ValueExtractionResult(None, 0.0, "multiline_value")
    
    def _extract_from_component_block(self, content: str, ref: str, part_type: str) -> ValueExtractionResult:
        """Strategy 3: Parse entire component block more carefully."""
        
        # Find the complete component block
        pattern = rf'\(comp\s+\(ref\s+{re.escape(ref)}\).*?\)\s*(?=\(comp|\(libparts|\)$)'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            return ValueExtractionResult(None, 0.0, "component_block")
        
        comp_block = match.group(0)
        
        # Look for any value field in this block
        value_patterns = [
            r'\(value\s+"([^"]+)"\)',     # Quoted value
            r'\(value\s+([^)\s]+)\)',     # Unquoted value  
            r'value\s*=\s*"([^"]+)"',     # Alternative format
            r'value\s*:\s*([^\s\)]+)'     # Colon format
        ]
        
        for pattern in value_patterns:
            match = re.search(pattern, comp_block)
            if match:
                value = match.group(1).strip()
                # Skip empty values
                if value and value != "" and value != '""' and value != "''":
                    return ValueExtractionResult(
                        value=value,
                        confidence=0.7,
                        method="component_block"
                    )
        
        return ValueExtractionResult(None, 0.0, "component_block")
    
    def _extract_from_part_name(self, content: str, ref: str, part_type: str) -> ValueExtractionResult:
        """Strategy 4: Infer value from part name or footprint if common patterns."""
        
        if not part_type:
            return ValueExtractionResult(None, 0.0, "part_name")
        
        # Common value patterns in part names
        value_patterns = {
            r'(\d+[kK])\b': lambda m: m.group(1).replace('K', 'k'),  # 10K -> 10k
            r'(\d+[rR])\b': lambda m: m.group(1).replace('R', ''),   # 100R -> 100
            r'(\d+[uU][fF])\b': lambda m: m.group(1).replace('U', 'u').replace('F', 'F'),  # 100UF -> 100uF
            r'(\d+[pP][fF])\b': lambda m: m.group(1),                # 100PF -> 100pF
            r'(\d+[nN][fF])\b': lambda m: m.group(1),                # 100NF -> 100nF
            r'(\d+[mM][hH])\b': lambda m: m.group(1),                # 100MH -> 100mH
        }
        
        # Search in part type and nearby text
        search_text = f"{part_type} {ref}"
        
        for pattern, transformer in value_patterns.items():
            match = re.search(pattern, search_text, re.IGNORECASE)
            if match:
                value = transformer(match)
                return ValueExtractionResult(
                    value=value,
                    confidence=0.5,
                    method="part_name",
                    warning="Value inferred from part name - verify correctness"
                )
        
        return ValueExtractionResult(None, 0.0, "part_name")
    
    def _extract_default_value(self, content: str, ref: str, part_type: str) -> ValueExtractionResult:
        """Strategy 5: Provide sensible defaults based on component type."""
        
        # Default values for common component types
        defaults = {
            'R': '1k',
            'C': '1uF', 
            'L': '1mH',
            'D': '1N4148',
            'Q': '2N3904',
            'U': 'LM358'
        }
        
        # Extract component type from reference or part_type
        comp_type = None
        if ref and len(ref) > 0:
            comp_type = ref[0].upper()
        
        if comp_type in defaults:
            return ValueExtractionResult(
                value=defaults[comp_type],
                confidence=0.1,
                method="default_value", 
                warning=f"Using default value {defaults[comp_type]} for {ref} - please verify"
            )
        
        return ValueExtractionResult(None, 0.0, "default_value")