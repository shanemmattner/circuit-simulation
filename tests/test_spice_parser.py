"""
Test module for SPICE parser functionality.
"""
import pytest
from src.io.parsers.spice_parser import SpiceTokenizer, SpiceParser


class TestSpiceTokenizer:
    """Test SPICE tokenization functionality."""
    
    def test_parse_resistor_line(self):
        """Test parsing basic resistor line."""
        tokenizer = SpiceTokenizer()
        tokens = tokenizer.parse_line("R1 1 2 1k")
        
        assert tokens == ["R1", "1", "2", "1k"]
        
    def test_parse_capacitor_line(self):
        """Test parsing capacitor with comments."""
        tokenizer = SpiceTokenizer()
        tokens = tokenizer.parse_line("C1 node1 gnd 100uF ; bypass cap")
        
        assert tokens == ["C1", "node1", "gnd", "100uF"]  # Comment stripped
        
    def test_parse_line_continuation(self):
        """Test SPICE line continuation with +."""
        tokenizer = SpiceTokenizer()
        lines = [
            "M1 drain gate source bulk NMOS_MODEL",
            "+ W=10u L=1u"
        ]
        tokens = tokenizer.parse_continued_lines(lines)
        
        expected = ["M1", "drain", "gate", "source", "bulk", "NMOS_MODEL", "W=10u", "L=1u"]
        assert tokens == expected
        
    def test_skip_comments_and_empty_lines(self):
        """Test skipping comment and empty lines."""
        tokenizer = SpiceTokenizer()
        
        # Comment line should return empty
        tokens = tokenizer.parse_line("* This is a comment")
        assert tokens == []
        
        # Empty line should return empty
        tokens = tokenizer.parse_line("   ")
        assert tokens == []
        
    def test_parse_subcircuit_definition(self):
        """Test parsing .SUBCKT line."""
        tokenizer = SpiceTokenizer()
        tokens = tokenizer.parse_line(".SUBCKT OPAMP inp inn vcc vee out")
        
        expected = [".SUBCKT", "OPAMP", "inp", "inn", "vcc", "vee", "out"]
        assert tokens == expected


class TestSpiceParser:
    """Test full SPICE file parsing."""
    
    def test_parse_simple_circuit(self):
        """Test parsing a simple voltage divider circuit."""
        parser = SpiceParser()
        
        spice_content = """
* Simple voltage divider
V1 vcc gnd DC 10V
R1 vcc out 1k
R2 out gnd 1k
.END
        """
        
        circuit = parser.parse_content(spice_content)
        
        assert circuit.name == "Simple voltage divider"
        assert len(circuit.components) == 3  # V1, R1, R2
        
        # Check components exist
        component_names = [comp.get('name', '') for comp in circuit.components]
        assert "V1" in component_names
        assert "R1" in component_names  
        assert "R2" in component_names
        
    def test_parse_transistor_with_model(self):
        """Test parsing BJT transistor with model reference."""
        parser = SpiceParser()
        
        spice_content = """
* Transistor amplifier
.MODEL 2N3904 NPN(BF=300 IS=1e-14)
Q1 collector base emitter 2N3904
.END
        """
        
        circuit = parser.parse_content(spice_content)
        
        # Check transistor was parsed and stored
        assert hasattr(circuit, '_advanced_components')
        advanced_names = [comp['name'] for comp in circuit._advanced_components]
        assert "Q1" in advanced_names
        assert "2N3904" in parser.models
        assert parser.models["2N3904"]["type"] == "NPN"
        
    def test_parse_subcircuit_definition(self):
        """Test parsing .SUBCKT definition."""
        parser = SpiceParser()
        
        spice_content = """
* Op-amp subcircuit
.SUBCKT OPAMP inp inn vcc vee out
R1 inp 1 1meg
R2 inn 1 1meg
.ENDS OPAMP
.END
        """
        
        circuit = parser.parse_content(spice_content)
        
        assert "OPAMP" in parser.subcircuits
        subckt = parser.subcircuits["OPAMP"]
        assert subckt["ports"] == ["inp", "inn", "vcc", "vee", "out"]
        assert len(subckt["components"]) == 2  # R1, R2