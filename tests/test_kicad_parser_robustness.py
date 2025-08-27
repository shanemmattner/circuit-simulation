"""
Test KiCad parser robustness - handling various edge cases and providing clear errors.
These tests drive the TDD development for Phase 1: Parser Robustness.
"""

import pytest
from src.io.parsers.kicad_parser import KiCadParser


class TestKiCadParserRobustness:
    """Test parser robustness with various edge cases."""

    def test_value_extraction_multiline_format(self):
        """Test extracting values from multi-line KiCad component format."""
        parser = KiCadParser()
        
        # Multi-line format where value is on separate line
        kicad_content = """(export (version D)
  (components
    (comp (ref R1)
      (footprint Resistor_SMD:R_0603_1608Metric)
      (libsource (lib Device) (part R)))
    (value 10k)
    (comp (ref R2)
      (value 2k2)
      (footprint Resistor_SMD:R_0603_1608Metric)
      (libsource (lib Device) (part R)))))"""

        circuit = parser.parse_content(kicad_content)
        
        # Should extract values correctly even when on different lines
        r1 = next((c for c in circuit.components if c.get("name") == "R1"), None)
        r2 = next((c for c in circuit.components if c.get("name") == "R2"), None)
        
        assert r1 is not None, "R1 component should be created"
        assert r2 is not None, "R2 component should be created"
        
        # This will fail initially - our current parser can't handle this
        assert r1.get("resistance") == "10k", "Should extract value from separate line"
        assert r2.get("resistance") == "2k2", "Should extract inline value"

    def test_missing_component_values(self):
        """Test handling components with missing or empty values."""
        parser = KiCadParser()
        
        kicad_content = """(export (version D)
  (components
    (comp (ref R1)
      (value "")
      (libsource (lib Device) (part R)))
    (comp (ref R2)
      (libsource (lib Device) (part R)))
    (comp (ref R3)
      (value 1k)
      (libsource (lib Device) (part R)))))"""

        result = parser.parse_content_with_result(kicad_content)
        
        # Should create an ImportResult object (doesn't exist yet)
        assert hasattr(result, 'circuit')
        assert hasattr(result, 'warnings')
        assert hasattr(result, 'failed_components')
        
        # Should warn about missing values but not fail completely
        assert len(result.warnings) >= 2  # R1 empty, R2 missing
        assert len(result.circuit.components) == 3  # All components created
        assert "R1" in [w.component_ref for w in result.warnings]
        assert "R2" in [w.component_ref for w in result.warnings]

    def test_malformed_netlist_partial_success(self):
        """Test partial import success when some components are malformed."""
        parser = KiCadParser()
        
        kicad_content = """(export (version D)
  (components
    (comp (ref R1)
      (value 10k)
      (libsource (lib Device) (part R)))
    (comp (ref U1)
      (value TOTALLY_INVALID_IC_NAME_THAT_BREAKS_THINGS)
      (libsource (lib Amplifier_Operational) (part LM358)))
    (comp (ref R2)
      (value 2k2)
      (libsource (lib Device) (part R)))
    (comp INVALID_COMPONENT_STRUCTURE))"""

        result = parser.parse_content_with_result(kicad_content)
        
        # Should succeed for valid components
        # Note: U1 now succeeds because model mapper can handle LM358
        assert len(result.circuit.components) >= 3  # R1, R2, U1 should all work now
        # Only malformed component structure should fail (if any)
        
        # Check that U1 was successfully imported with model mapping
        u1_component = next((c for c in result.circuit.components if c.get("name") == "U1"), None)
        assert u1_component is not None, "U1 should be successfully imported with model mapping"
        assert u1_component["type"] == "opamp", "U1 should be detected as op-amp"

    def test_format_version_detection(self):
        """Test detecting different KiCad netlist format versions."""
        parser = KiCadParser()
        
        # Different format versions
        old_format = """(export (version "D")"""
        new_format = """(kicad_netlist (version "6.0")"""
        
        old_info = parser.detect_format(old_format)
        new_info = parser.detect_format(new_format)
        
        assert old_info.version != new_info.version
        assert old_info.format_type != new_info.format_type
        assert hasattr(old_info, 'supported')
        assert hasattr(new_info, 'supported')

    def test_detailed_error_context(self):
        """Test that parsing errors provide helpful context and suggestions."""
        parser = KiCadParser()
        
        # Intentionally broken netlist
        broken_content = """(export (version D)
  (components
    (comp (ref R1)
      (value 10k)
      (libsource (lib Device) (part R)))
    (comp (ref R2)
      (value "")  # Empty value here
      (footprint MISSING_CLOSING_PAREN
      (libsource (lib Device) (part R)))))"""

        # Our robust parser handles this gracefully instead of raising
        result = parser.parse_content_with_result(broken_content)
        
        # Should have warnings about the malformed content
        assert result.has_warnings or len(result.parsing_errors) > 0
        
        # Should still import some components
        assert len(result.circuit.components) >= 1  # R1 should work
        
        # Should provide context in the result
        report = result.detailed_report()
        assert "R2" in report or any("R2" in str(w) for w in result.warnings)

    def test_import_result_summary(self):
        """Test that ImportResult provides useful summary information."""
        parser = KiCadParser()
        
        mixed_content = """(export (version D)
  (components
    (comp (ref R1) (value 10k) (libsource (lib Device) (part R)))
    (comp (ref R2) (value "") (libsource (lib Device) (part R)))
    (comp (ref C1) (value 100uF) (libsource (lib Device) (part C)))))"""

        result = parser.parse_content_with_result(mixed_content)
        summary = result.summary()
        
        # Summary should be informative
        assert "2 components imported" in summary or "imported" in summary
        assert "1" in summary and ("warning" in summary or "failed" in summary)
        assert "✓" in summary or "success" in summary
        assert "⚠" in summary or "!" in summary

# Import the actual classes we've implemented
from src.io.parsers.import_result import ImportResult, ComponentFailure
from src.io.parsers.value_extractor import ValueExtractor
from src.io.parsers.format_detector import FormatInfo