"""
Test KiCad format detection capability.
"""

from src.io.parsers.format_detector import FormatDetector, KiCadVersion, FormatInfo


class TestFormatDetector:
    """Test the KiCad format detection functionality."""

    def setup_method(self):
        self.detector = FormatDetector()

    def test_detect_v4_legacy_format(self):
        """Test detecting KiCad v4.x legacy format."""
        v4_content = """(export (version D)
  (design
    (source /path/to/test.sch)
    (tool "Eeschema (4.0.7)"))
  (components
    (comp (ref R1) (value 10k)))"""

        format_info = self.detector.detect_format(v4_content)

        assert format_info.version == KiCadVersion.V4_LEGACY
        assert format_info.format_type == "legacy_sexpr"
        assert format_info.supported is True
        assert format_info.confidence > 0.8

    def test_detect_v6_modern_format(self):
        """Test detecting KiCad v6.x modern format."""
        v6_content = """(kicad_netlist (version "6.0.1")
  (design
    (source test.kicad_sch)
    (tool "Eeschema (6.0.1)"))
  (components
    (comp (ref "R1") (value "10k"))))"""

        format_info = self.detector.detect_format(v6_content)

        assert format_info.version == KiCadVersion.V6_MODERN
        assert format_info.format_type == "modern_sexpr"
        assert format_info.supported is True

    def test_detect_unknown_format(self):
        """Test handling unknown or malformed formats."""
        unknown_content = """This is not a valid KiCad netlist
        Random content that doesn't match patterns"""

        format_info = self.detector.detect_format(unknown_content)

        assert format_info.version == KiCadVersion.UNKNOWN
        assert format_info.supported is False
        assert len(format_info.warnings) > 0

    def test_feature_analysis(self):
        """Test analyzing format features."""
        content = """(export (version D)
  (components
    (comp (ref R1) (value "10k"))
    (comp (ref R2) (value "2k2")))
  (nets
    (net (code 1) (name "+3V3/nested") 
      (node (ref R1) (pin 1)))
    (net (code 2) (name "GND")
      (node (ref R2) (pin 2))))"""

        format_info = self.detector.detect_format(content)

        assert format_info.features["has_components"] is True
        assert format_info.features["has_nets"] is True
        assert format_info.features["component_count"] == 2
        assert format_info.features["net_count"] == 2
        assert format_info.features["hierarchical"] is True  # "/nested" in name
        assert format_info.features["quoted_values"] is True

    def test_multiline_format_detection(self):
        """Test detecting multi-line component format."""
        multiline_content = """(export (version D)
  (components
    (comp (ref R1)
      (footprint Resistor_SMD:R_0603)
      (libsource (lib Device) (part R)))
    (value 10k)))"""

        format_info = self.detector.detect_format(multiline_content)

        assert format_info.features["multiline_format"] is True
        assert "multi-line" in str(format_info.warnings).lower()

    def test_large_netlist_warning(self):
        """Test warning for large netlists."""
        # Create content with many components
        components = []
        for i in range(1500):  # More than 1000 components
            components.append(f"(comp (ref R{i}) (value 1k))")

        large_content = f"""(export (version D)
  (components
    {' '.join(components)}))"""

        format_info = self.detector.detect_format(large_content)

        assert format_info.features["component_count"] == 1500
        assert any("large netlist" in w.lower() for w in format_info.warnings)

    def test_parser_recommendations(self):
        """Test getting parser configuration recommendations."""
        v6_content = """(kicad_netlist (version "6.0")
  (components
    (comp (ref "R1")
      (value "10k")
      (footprint "Resistor:R_0603"))))"""

        format_info = self.detector.detect_format(v6_content)
        recommendations = self.detector.get_parser_recommendations(format_info)

        assert recommendations["use_value_extractor"] is True
        assert recommendations["quoted_value_handling"] is True
        assert recommendations["modern_format"] is True
        assert "strict_parsing" in recommendations

    def test_hierarchical_detection(self):
        """Test detecting hierarchical designs."""
        hierarchical_content = """(export (version D)
  (nets
    (net (code 1) (name "/Power_Supply/+3V3")
      (node (ref U1) (pin 1)))
    (net (code 2) (name "/Analog_Frontend/VREF")
      (node (ref U2) (pin 5)))))"""

        format_info = self.detector.detect_format(hierarchical_content)

        assert format_info.features["hierarchical"] is True
        recommendations = self.detector.get_parser_recommendations(format_info)
        assert recommendations["hierarchical_support"] is True

    def test_format_info_string_representation(self):
        """Test string representation of FormatInfo."""
        format_info = FormatInfo(
            version=KiCadVersion.V6_MODERN,
            format_type="modern_sexpr",
            supported=True,
            confidence=0.95,
            features={},
            warnings=[],
        )

        format_str = str(format_info)

        assert "KiCad 6.x" in format_str
        assert "modern_sexpr" in format_str
        assert "✓ Supported" in format_str

    def test_unsupported_version_warning(self):
        """Test warning for unsupported versions."""
        future_content = """(kicad_netlist (version "8.0")
  (tool "Eeschema (8.0.0-dev)"))"""

        format_info = self.detector.detect_format(future_content)

        assert format_info.version == KiCadVersion.V8_FUTURE
        assert format_info.supported is False
        assert any("not fully tested" in w for w in format_info.warnings)
