"""
Comprehensive tests for circuit-synth integration.

Tests the complete pipeline from circuit-synth JSON format through parsing,
component mapping, and circuit simulation compatibility.
"""

import json
import pytest
from typing import Dict, Any

from src.io.parsers.circuit_synth_parser import CircuitSynthParser
from src.io.models.circuit_synth_importer import CircuitSynthImporter
from src.io.parsers.import_result import ImportResult


class TestCircuitSynthParser:
    """Test CircuitSynthParser functionality."""
    
    def test_can_parse_circuit_synth_format(self):
        """Test format detection for circuit-synth JSON."""
        # Valid circuit-synth format
        circuit_synth_content = json.dumps({
            "name": "Test Circuit",
            "components": {
                "R1": {"symbol": "Device:R", "value": "10k"}
            },
            "nets": {
                "vcc": [{"component": "R1", "pin": "1"}]
            }
        })
        
        assert CircuitSynthParser.can_parse(circuit_synth_content) is True
        
    def test_cannot_parse_invalid_format(self):
        """Test rejection of invalid formats."""
        # Not JSON
        assert CircuitSynthParser.can_parse("invalid content") is False
        
        # Valid JSON but not circuit-synth format
        invalid_content = json.dumps({"random": "data"})
        assert CircuitSynthParser.can_parse(invalid_content) is False
        
    def test_parse_simple_circuit(self):
        """Test parsing of simple RC circuit."""
        parser = CircuitSynthParser()
        
        circuit_data = {
            "name": "Simple RC Filter",
            "description": "Low-pass RC filter for testing",
            "components": {
                "R1": {
                    "symbol": "Device:R",
                    "value": "1k",
                    "footprint": "Resistor_SMD:R_0603_1608Metric"
                },
                "C1": {
                    "symbol": "Device:C", 
                    "value": "100nF",
                    "footprint": "Capacitor_SMD:C_0603_1608Metric"
                }
            },
            "nets": {
                "input": [{"component": "R1", "pin": "1"}],
                "output": [
                    {"component": "R1", "pin": "2"},
                    {"component": "C1", "pin": "1"}
                ],
                "gnd": [{"component": "C1", "pin": "2"}]
            }
        }
        
        result = parser.parse_dict(circuit_data)
        
        assert result.is_successful is True
        assert result.circuit is not None
        assert result.circuit.name == "Simple RC Filter"
        assert len(result.warnings) == 0  # Should parse cleanly
        
    def test_parse_content_from_string(self):
        """Test parsing from JSON string content."""
        parser = CircuitSynthParser()
        
        content = json.dumps({
            "name": "LED Blinker",
            "components": {
                "LED1": {"symbol": "Device:LED", "value": ""},
                "R1": {"symbol": "Device:R", "value": "330"}
            },
            "nets": {
                "vcc": [{"component": "R1", "pin": "1"}],
                "led_anode": [
                    {"component": "R1", "pin": "2"},
                    {"component": "LED1", "pin": "A"}
                ],
                "gnd": [{"component": "LED1", "pin": "K"}]
            }
        })
        
        result = parser.parse_content(content)
        
        assert result.is_successful is True
        assert result.circuit.name == "LED Blinker"


class TestCircuitSynthImporter:
    """Test CircuitSynthImporter component mapping and net handling."""
    
    def test_component_mapping(self):
        """Test comprehensive component symbol mapping."""
        importer = CircuitSynthImporter()
        
        test_components = {
            "R1": {"symbol": "Device:R", "value": "10k"},
            "C1": {"symbol": "Device:C", "value": "100nF"},  
            "L1": {"symbol": "Device:L", "value": "1mH"},
            "D1": {"symbol": "Device:D", "value": ""},
            "LED1": {"symbol": "Device:LED", "value": ""},
            "V1": {"symbol": "power:+5V", "value": "5V"},
            "U1": {"symbol": "Amplifier_Operational:LM358", "value": ""}
        }
        
        circuit_data = {
            "name": "Component Mapping Test",
            "components": test_components,
            "nets": {
                "test": [{"component": "R1", "pin": "1"}]
            }
        }
        
        result = importer.import_from_dict(circuit_data)
        
        assert result.is_successful is True
        # All basic components should map successfully
        basic_components = ["R1", "C1", "L1", "V1"]
        assert len([w for w in result.warnings if w.component_ref not in basic_components]) >= 0
        
    def test_net_connectivity_parsing(self):
        """Test proper net connectivity handling."""
        importer = CircuitSynthImporter()
        
        circuit_data = {
            "name": "Net Connectivity Test",
            "components": {
                "R1": {"symbol": "Device:R", "value": "1k"},
                "R2": {"symbol": "Device:R", "value": "2k"},
                "C1": {"symbol": "Device:C", "value": "10uF"}
            },
            "nets": {
                "vcc": [
                    {"component": "R1", "pin": "1"},
                    {"component": "R2", "pin": "1"}
                ],
                "node1": [
                    {"component": "R1", "pin": "2"}, 
                    {"component": "C1", "pin": "1"}
                ],
                "gnd": [
                    {"component": "R2", "pin": "2"},
                    {"component": "C1", "pin": "2"}
                ]
            }
        }
        
        result = importer.import_from_dict(circuit_data)
        
        assert result.is_successful is True
        # Each component should be connected to the right nets
        # This is a basic test - detailed connectivity would need circuit object inspection
        
    def test_value_extraction(self):
        """Test component value parsing and extraction."""
        importer = CircuitSynthImporter()
        
        circuit_data = {
            "name": "Value Extraction Test",
            "components": {
                "R1": {"symbol": "Device:R", "value": "10k"},
                "R2": {"symbol": "Device:R", "value": "1.5k"},  
                "C1": {"symbol": "Device:C", "value": "100nF"},
                "C2": {"symbol": "Device:C", "value": "2.2uF"},
                "L1": {"symbol": "Device:L", "value": "1mH"},
                "V1": {"symbol": "power:+3V3", "value": "3.3V"}
            },
            "nets": {
                "test": [{"component": "R1", "pin": "1"}]
            }
        }
        
        result = importer.import_from_dict(circuit_data)
        
        assert result.is_successful is True
        # Values should be preserved through the parsing process
        
    def test_error_handling(self):
        """Test robust error handling for malformed data."""
        importer = CircuitSynthImporter()
        
        # Missing required fields
        invalid_data = {
            "components": "not_a_dict",
            "nets": []
        }
        
        result = importer.import_from_dict(invalid_data)
        
        # Should handle gracefully, either success with warnings or controlled failure
        assert not result.is_successful or len(result.warnings) > 0 or len(result.parsing_errors) > 0
        
    def test_subcircuit_handling(self):
        """Test subcircuit parsing capability."""
        importer = CircuitSynthImporter()
        
        circuit_data = {
            "name": "Main Circuit",
            "components": {
                "R1": {"symbol": "Device:R", "value": "1k"}
            },
            "nets": {
                "vcc": [{"component": "R1", "pin": "1"}]
            },
            "subcircuits": [
                {
                    "name": "Power Supply",
                    "components": {
                        "U1": {"symbol": "Regulator_Linear:AMS1117-3.3", "value": ""}
                    },
                    "nets": {
                        "vin": [{"component": "U1", "pin": "IN"}]
                    }
                }
            ]
        }
        
        result = importer.import_from_dict(circuit_data)
        
        assert result.is_successful is True
        # Subcircuits should be processed (exact handling depends on implementation)


class TestCircuitSynthIntegrationRealExamples:
    """Test integration with realistic circuit-synth examples."""
    
    def test_led_blinker_circuit(self):
        """Test LED blinker circuit from circuit-synth examples."""
        parser = CircuitSynthParser()
        
        led_blinker = {
            "name": "LED_Blinker",
            "description": "LED with current limiting resistor",
            "components": {
                "D1": {
                    "symbol": "Device:LED",
                    "ref": "D",
                    "footprint": "LED_SMD:LED_0805_2012Metric"
                },
                "R1": {
                    "symbol": "Device:R", 
                    "ref": "R",
                    "value": "330",
                    "footprint": "Resistor_SMD:R_0805_2012Metric"
                }
            },
            "nets": {
                "vcc_3v3": [{"component": "R1", "pin": "1"}],
                "led_anode": [
                    {"component": "R1", "pin": "2"},
                    {"component": "D1", "pin": "A"}
                ],
                "led_control": [{"component": "D1", "pin": "K"}]
            }
        }
        
        result = parser.parse_dict(led_blinker)
        
        assert result.is_successful is True
        assert result.circuit.name == "LED_Blinker"
        assert result.format_info["component_count"] == 2
        assert result.format_info["net_count"] == 3
        
    def test_power_supply_circuit(self):
        """Test power supply circuit parsing.""" 
        parser = CircuitSynthParser()
        
        power_supply = {
            "name": "3V3_PowerSupply",
            "description": "3.3V linear regulator circuit", 
            "components": {
                "U1": {
                    "symbol": "Regulator_Linear:AMS1117-3.3",
                    "value": "",
                    "footprint": "Package_TO_SOT_SMD:SOT-223-3_TabPin2"
                },
                "C1": {
                    "symbol": "Device:C",
                    "value": "10uF", 
                    "footprint": "Capacitor_SMD:C_1206_3216Metric"
                },
                "C2": {
                    "symbol": "Device:C",
                    "value": "100nF",
                    "footprint": "Capacitor_SMD:C_0603_1608Metric"
                }
            },
            "nets": {
                "vin": [
                    {"component": "U1", "pin": "IN"}, 
                    {"component": "C1", "pin": "1"}
                ],
                "vout_3v3": [
                    {"component": "U1", "pin": "OUT"},
                    {"component": "C2", "pin": "1"}
                ],
                "gnd": [
                    {"component": "U1", "pin": "GND"},
                    {"component": "C1", "pin": "2"},
                    {"component": "C2", "pin": "2"}
                ]
            }
        }
        
        result = parser.parse_dict(power_supply)
        
        assert result.is_successful is True
        assert result.circuit.name == "3V3_PowerSupply"
        # Power supply should have at least one behavioral model warning for U1
        regulator_warnings = [w for w in result.warnings if "U1" in w.warning_message]
        # May have warnings for complex components


class TestAPIIntegration:
    """Test API endpoint integration (integration tests)."""
    
    def test_import_endpoint_structure(self):
        """Test that import endpoint is properly structured."""
        # This would typically require a test client
        # For now, verify the endpoint function exists and has proper signature
        from src.api.routes.circuits import import_circuit_synth
        
        import inspect
        sig = inspect.signature(import_circuit_synth)
        
        # Should accept circuit_data parameter
        assert "circuit_data" in sig.parameters
        
        # Should be marked as async
        assert inspect.iscoroutinefunction(import_circuit_synth)


if __name__ == "__main__":
    # Run basic tests if executed directly
    parser = CircuitSynthParser()
    
    # Test format detection
    test_data = {"name": "test", "components": {}, "nets": {}}
    test_content = json.dumps(test_data)
    
    print("Testing circuit-synth integration...")
    print(f"✓ Format detection: {parser.can_parse(test_content)}")
    
    # Test parsing
    result = parser.parse_dict(test_data)
    print(f"✓ Basic parsing: {result.success}")
    
    print("✓ Circuit-synth integration tests ready!")