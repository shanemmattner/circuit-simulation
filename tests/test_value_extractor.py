"""
Test the ValueExtractor class in isolation.
"""

from src.io.parsers.value_extractor import ValueExtractor


class TestValueExtractor:
    """Test the ValueExtractor fallback strategies."""

    def setup_method(self):
        self.extractor = ValueExtractor()

    def test_inline_value_extraction(self):
        """Test extracting values from inline format."""
        content = "(comp (ref R1) (value 10k) (libsource (lib Device) (part R)))"

        result = self.extractor.extract_value(content, "R1", "R")

        assert result.value == "10k"
        assert result.confidence > 0.8
        assert result.method == "inline_value"

    def test_multiline_value_extraction(self):
        """Test extracting values when on separate line."""
        content = """(comp (ref R1)
      (footprint Resistor_SMD:R_0603_1608Metric)
      (libsource (lib Device) (part R)))
    (value 10k)"""

        result = self.extractor.extract_value(content, "R1", "R")

        assert result.value == "10k"
        assert result.method == "multiline_value"
        assert result.confidence > 0.5

    def test_default_value_fallback(self):
        """Test falling back to default values."""
        content = "(comp (ref R1) (libsource (lib Device) (part R)))"

        result = self.extractor.extract_value(content, "R1", "R")

        assert result.value == "1k"  # Default resistor value
        assert result.method == "default_value"
        assert result.warning is not None
        assert "default" in result.warning.lower()

    def test_empty_value_handling(self):
        """Test handling of empty value fields."""
        content = '(comp (ref R1) (value "") (libsource (lib Device) (part R)))'

        result = self.extractor.extract_value(content, "R1", "R")

        # Should skip empty value and use default
        assert result.value == "1k"
        assert result.method == "default_value"
