"""
Tests for KiCad model library integration (Phase 3).
Test-driven development for component-to-model mapping.
"""

import pytest
from unittest.mock import Mock, MagicMock
from src.models.spice_loader import SpiceModelLoader


class TestComponentTypeDetector:
    """Test component type detection from KiCad symbols."""
    
    def test_detect_bjt_transistor_types(self):
        """Test detection of BJT transistors from KiCad symbols."""
        from src.io.parsers.component_model_mapper import ComponentTypeDetector
        
        detector = ComponentTypeDetector()
        
        # Test various BJT patterns
        assert detector.detect_type("Device:Q_NPN_BCE", "Q1", "2N3904") == "transistor_bjt_npn"
        assert detector.detect_type("Device:Q_PNP_BCE", "Q2", "2N3906") == "transistor_bjt_pnp" 
        assert detector.detect_type("Transistor_BJT:2N3904", "Q1", "2N3904") == "transistor_bjt_npn"
        assert detector.detect_type("Device:2N3904", "Q1", "") == "transistor_bjt_npn"
        
        # Test with component reference patterns
        assert detector.detect_type("unknown_symbol", "Q1", "some_value") == "transistor_bjt"
        
    def test_detect_mosfet_types(self):
        """Test detection of MOSFET transistors."""
        from src.io.parsers.component_model_mapper import ComponentTypeDetector
        
        detector = ComponentTypeDetector()
        
        assert detector.detect_type("Device:Q_NMOS_GSD", "Q1", "IRF540") == "transistor_mosfet_n"
        assert detector.detect_type("Device:Q_PMOS_GSD", "Q2", "IRF9540") == "transistor_mosfet_p"
        assert detector.detect_type("Transistor_FET:IRF540N", "Q1", "") == "transistor_mosfet_n"
        
    def test_detect_diode_types(self):
        """Test detection of various diode types."""
        from src.io.parsers.component_model_mapper import ComponentTypeDetector
        
        detector = ComponentTypeDetector()
        
        assert detector.detect_type("Device:D", "D1", "1N4148") == "diode_signal"
        assert detector.detect_type("Device:D_Zener", "D2", "1N4733") == "diode_zener" 
        assert detector.detect_type("Device:LED", "D3", "RED") == "diode_led"
        assert detector.detect_type("Diode:1N4007", "D1", "") == "diode_power"
        
        # Reference-based detection
        assert detector.detect_type("unknown", "D5", "unknown") == "diode"
        
    def test_detect_opamp_types(self):
        """Test detection of operational amplifiers."""
        from src.io.parsers.component_model_mapper import ComponentTypeDetector
        
        detector = ComponentTypeDetector()
        
        assert detector.detect_type("Amplifier_Operational:LM358", "U1", "") == "opamp"
        assert detector.detect_type("Device:Opamp_Dual", "U2", "TL072") == "opamp"
        assert detector.detect_type("Linear:LM741", "U3", "") == "opamp"
        
    def test_detect_logic_types(self):
        """Test detection of logic gates and digital ICs."""
        from src.io.parsers.component_model_mapper import ComponentTypeDetector
        
        detector = ComponentTypeDetector()
        
        assert detector.detect_type("74xx:74LS00", "U1", "") == "logic_gate"
        assert detector.detect_type("4xxx:4011", "U2", "") == "logic_gate"
        assert detector.detect_type("Logic_74:74HC04", "U3", "") == "logic_gate"
        
    def test_detect_regulator_types(self):
        """Test detection of voltage regulators.""" 
        from src.io.parsers.component_model_mapper import ComponentTypeDetector
        
        detector = ComponentTypeDetector()
        
        assert detector.detect_type("Regulator_Linear:L7805", "U1", "") == "regulator_linear"
        assert detector.detect_type("Device:78L05", "U2", "") == "regulator_linear"
        assert detector.detect_type("Regulator_Switching:LM2596", "U3", "") == "regulator_switching"


class TestExactSymbolMatch:
    """Test exact symbol matching strategy."""
    
    def setup_method(self):
        """Set up test environment with mock model loader."""
        self.mock_loader = Mock(spec=SpiceModelLoader)
        
    def test_exact_value_match(self):
        """Test exact match on component value."""
        from src.io.parsers.component_model_mapper import ExactSymbolMatch
        
        # Mock successful model loading
        self.mock_loader.load_transistor.return_value = "Mock 2N3904 SPICE model"
        
        matcher = ExactSymbolMatch(self.mock_loader)
        
        result = matcher.find_model("Device:Q_NPN_BCE", "Q1", "2N3904")
        
        assert result is not None
        assert result.spice_model == "Mock 2N3904 SPICE model"
        assert result.type == "transistor_bjt_npn"
        assert result.confidence == 1.0
        self.mock_loader.load_transistor.assert_called_once_with("2N3904")
        
    def test_exact_symbol_match(self):
        """Test exact match on KiCad symbol name."""
        from src.io.parsers.component_model_mapper import ExactSymbolMatch
        
        self.mock_loader.load_transistor.return_value = "Mock 2N3904 SPICE model"
        
        matcher = ExactSymbolMatch(self.mock_loader)
        
        result = matcher.find_model("Transistor_BJT:2N3904", "Q1", "")
        
        assert result is not None
        assert result.spice_model == "Mock 2N3904 SPICE model"
        self.mock_loader.load_transistor.assert_called_once_with("2N3904")
        
    def test_no_match_returns_none(self):
        """Test that no match returns None."""
        from src.io.parsers.component_model_mapper import ExactSymbolMatch
        
        # Mock model not found
        self.mock_loader.load_transistor.side_effect = Exception("Model not found")
        
        matcher = ExactSymbolMatch(self.mock_loader)
        
        result = matcher.find_model("Device:Unknown", "Q1", "UnknownModel")
        
        assert result is None


class TestFuzzySymbolMatch:
    """Test fuzzy symbol matching strategy."""
    
    def setup_method(self):
        self.mock_loader = Mock(spec=SpiceModelLoader)
        
    def test_fuzzy_transistor_match(self):
        """Test fuzzy matching for similar transistor models."""
        from src.io.parsers.component_model_mapper import FuzzySymbolMatch
        
        # Mock available models
        self.mock_loader.get_available_models.return_value = ["2N3904", "2N3906", "BC547"]
        self.mock_loader.load_transistor.return_value = "Mock 2N3904 SPICE model"
        
        matcher = FuzzySymbolMatch(self.mock_loader)
        
        # Test fuzzy match: "2N3903" should match "2N3904"
        result = matcher.find_model("Device:Q_NPN", "Q1", "2N3903")
        
        assert result is not None
        assert result.confidence < 1.0  # Should be less than exact match
        assert result.confidence > 0.5  # But still good match
        
    def test_generic_type_matching(self):
        """Test generic type-based matching."""
        from src.io.parsers.component_model_mapper import FuzzySymbolMatch
        
        self.mock_loader.get_available_models.return_value = ["2N3904"]
        self.mock_loader.load_transistor.return_value = "Generic NPN SPICE model"
        
        matcher = FuzzySymbolMatch(self.mock_loader)
        
        # Generic NPN should get a common NPN model
        result = matcher.find_model("Device:Q_NPN_BCE", "Q1", "")
        
        assert result is not None
        assert result.confidence > 0.3
        

class TestDefaultBehavioral:
    """Test default behavioral model fallback."""
    
    def test_unknown_component_fallback(self):
        """Test fallback for completely unknown components."""
        from src.io.parsers.component_model_mapper import DefaultBehavioral
        
        fallback = DefaultBehavioral()
        
        # Use a truly unknown reference pattern to force unknown detection
        result = fallback.find_model("Unknown:WeirdComponent", "X1", "SomeValue")
        
        assert result is not None
        assert result.type == "unknown" or result.type == "behavioral"
        assert result.confidence < 0.3
        assert result.method == "default_behavioral"
        
    def test_behavioral_model_generation(self):
        """Test that behavioral models are generated correctly."""
        from src.io.parsers.component_model_mapper import DefaultBehavioral
        
        fallback = DefaultBehavioral()
        
        # Test transistor detection and behavioral model
        result = fallback.find_model("Unknown:Component", "Q1", "UnknownTransistor")
        
        assert result is not None
        assert result.type == "transistor_bjt"  # Q prefix should detect transistor
        assert "NPN" in result.spice_model or "BJT" in result.spice_model
        assert result.confidence == 0.2  # Behavioral confidence


class TestComponentModelMapper:
    """Test the main component model mapper orchestration."""
    
    def setup_method(self):
        self.mock_loader = Mock(spec=SpiceModelLoader)
        
    def test_mapping_strategy_cascade(self):
        """Test that mapping strategies are tried in order."""
        from src.io.parsers.component_model_mapper import ComponentModelMapper
        
        # Configure mock loader
        self.mock_loader.load_transistor.return_value = "2N3904 SPICE Model"
        
        mapper = ComponentModelMapper(self.mock_loader)
        
        # Should find exact match first
        result = mapper.map_component("Device:Q_NPN_BCE", "Q1", "2N3904")
        
        assert result is not None
        assert result.confidence == 1.0  # Exact match confidence
        assert result.method == "exact_value_match"
        
    def test_fallback_to_behavioral(self):
        """Test that unknown components fall back to behavioral."""
        from src.io.parsers.component_model_mapper import ComponentModelMapper
        
        # Mock all model loading to fail
        self.mock_loader.load_transistor.side_effect = Exception("Not found")
        self.mock_loader.load_diode.side_effect = Exception("Not found") 
        self.mock_loader.load_opamp.side_effect = Exception("Not found")
        
        mapper = ComponentModelMapper(self.mock_loader)
        
        # Use X prefix to avoid U1 being detected as opamp
        result = mapper.map_component("Unknown:Component", "X1", "Unknown")
        
        assert result is not None
        assert result.method == "default_behavioral"
        
    def test_performance_with_caching(self):
        """Test that model mapping is cached for performance."""
        from src.io.parsers.component_model_mapper import ComponentModelMapper
        
        self.mock_loader.load_transistor.return_value = "2N3904 Model"
        
        mapper = ComponentModelMapper(self.mock_loader)
        
        # First call
        result1 = mapper.map_component("Device:Q_NPN_BCE", "Q1", "2N3904")
        # Second call with same symbol and value (should be cached)
        result2 = mapper.map_component("Device:Q_NPN_BCE", "Q1", "2N3904")
        
        # Should only call loader once due to caching (same cache key)
        assert self.mock_loader.load_transistor.call_count == 1
        assert result1.spice_model == result2.spice_model


class TestCircuitIntegration:
    """Test integration with Circuit API for new component types."""
    
    def test_circuit_bjt_addition(self):
        """Test adding BJT transistor to circuit."""
        from circuit_sim import Circuit
        
        circuit = Circuit("Test BJT Circuit")
        
        # This method doesn't exist yet - will fail initially
        circuit.add_bjt_transistor("Q1", collector="2", base="1", emitter="0", model="2N3904")
        
        # Verify component was added correctly
        assert len(circuit.components) == 1
        bjt = circuit.components[0]
        assert bjt["name"] == "Q1"
        assert bjt["type"] == "bjt_transistor"
        assert bjt["model"] == "2N3904"
        
    def test_circuit_diode_addition(self):
        """Test adding diode to circuit."""
        from circuit_sim import Circuit
        
        circuit = Circuit("Test Diode Circuit")
        
        circuit.add_diode("D1", anode="1", cathode="0", model="1N4148")
        
        assert len(circuit.components) == 1
        diode = circuit.components[0]
        assert diode["name"] == "D1"
        assert diode["type"] == "diode"
        assert diode["model"] == "1N4148"
        
    def test_circuit_opamp_addition(self):
        """Test adding operational amplifier to circuit."""
        from circuit_sim import Circuit
        
        circuit = Circuit("Test OpAmp Circuit")
        
        circuit.add_opamp("U1", vplus="1", vminus="2", vout="3", vcc="4", vee="0", model="LM358")
        
        assert len(circuit.components) == 1
        opamp = circuit.components[0]
        assert opamp["name"] == "U1"
        assert opamp["type"] == "opamp"
        assert opamp["model"] == "LM358"


class TestKiCadParserIntegration:
    """Test integration of model mapping into KiCad parser."""
    
    def test_enhanced_parser_with_transistor(self):
        """Test parsing KiCad content with transistors."""
        from src.io.parsers.kicad_parser import KiCadParser
        
        kicad_content = """(export (version D)
  (components
    (comp (ref Q1)
      (value 2N3904)
      (libsource (lib Device) (part Q_NPN_BCE)))
    (comp (ref R1)
      (value 10k)
      (libsource (lib Device) (part R)))))"""
        
        parser = KiCadParser()
        result = parser.parse_content_with_result(kicad_content)
        
        # Should successfully import both components with appropriate models
        assert len(result.circuit.components) == 2
        assert result.is_successful
        
        # Find the transistor component
        transistor = next(c for c in result.circuit.components if c.get("name") == "Q1")
        assert transistor["type"] == "bjt_transistor"
        # Model will be behavioral since we're using mock model loader
        assert transistor["model"] is not None
        
    def test_enhanced_parser_with_mixed_components(self):
        """Test parsing complex circuit with multiple component types."""
        from src.io.parsers.kicad_parser import KiCadParser
        
        complex_content = """(export (version D)
  (components
    (comp (ref R1) (value 10k) (libsource (lib Device) (part R)))
    (comp (ref Q1) (value 2N3904) (libsource (lib Device) (part Q_NPN_BCE)))
    (comp (ref D1) (value 1N4148) (libsource (lib Device) (part D)))
    (comp (ref U1) (value LM358) (libsource (lib Amplifier_Operational) (part LM358)))
    (comp (ref C1) (value 100uF) (libsource (lib Device) (part C)))))"""
        
        parser = KiCadParser()
        result = parser.parse_content_with_result(complex_content)
        
        assert len(result.circuit.components) == 5
        assert result.is_successful
        
        # Check that different component types were created correctly
        component_types = [c.get("type") for c in result.circuit.components]
        assert "resistor" in component_types
        assert "bjt_transistor" in component_types  
        assert "diode" in component_types
        assert "opamp" in component_types
        assert "capacitor" in component_types


# Placeholder imports - these will be implemented in subsequent chunks
class ComponentFailureForModelTest(Exception):
    """Placeholder exception for components that will fail to import due to missing model classes."""
    pass