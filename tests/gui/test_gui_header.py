"""Test navigation header component - Chunk 2 TDD tests."""

from src.gui.components.header import create_header


class TestHeaderComponent:
    """Test navigation header component functionality."""

    def test_create_header_returns_component(self):
        """Test that create_header returns a valid Dash component."""
        # This will fail initially - we haven't created the header module yet
        header = create_header()
        assert header is not None

    def test_header_contains_title(self):
        """Test that header contains the dashboard title."""
        header = create_header()
        header_str = str(header)
        assert "Circuit Analysis Dashboard" in header_str

    def test_header_contains_circuit_selector(self):
        """Test that header contains a circuit selection dropdown."""
        header = create_header()
        header_str = str(header)
        # Look for dropdown component
        assert "dcc.Dropdown" in header_str or "Dropdown" in header_str

    def test_header_has_proper_id(self):
        """Test that header has the expected ID for CSS/callbacks."""
        header = create_header()
        header_str = str(header)
        assert "header" in header_str

    def test_header_with_custom_circuits(self):
        """Test that header accepts circuit options."""
        circuit_options = [
            {"label": "RC Filter", "value": "rc_filter"},
            {"label": "Voltage Divider", "value": "voltage_divider"},
        ]
        header = create_header(circuit_options=circuit_options)
        header_str = str(header)
        assert "RC Filter" in header_str
        assert "Voltage Divider" in header_str
