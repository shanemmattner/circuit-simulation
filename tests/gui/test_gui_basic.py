"""Test basic GUI functionality - Chunk 1 TDD tests."""

from dash.testing.application_runners import import_app


class TestBasicDashApp:
    """Test basic Dash application functionality."""

    def test_app_imports_successfully(self):
        """Test that the Dash app can be imported without errors."""
        # This will fail initially - we haven't created the app yet
        app = import_app("src.gui.app")
        assert app is not None

    def test_app_has_title(self):
        """Test that the app has a proper title."""
        app = import_app("src.gui.app")
        assert hasattr(app, "title")
        assert "Circuit Analysis Dashboard" in app.title

    def test_app_has_layout(self):
        """Test that app has a proper layout structure."""
        app = import_app("src.gui.app")
        assert hasattr(app, "layout")
        assert app.layout is not None

    def test_layout_contains_tab_content(self):
        """Test that layout contains tab content area."""
        app = import_app("src.gui.app")
        layout_str = str(app.layout)
        assert "tab-content" in layout_str

    def test_layout_contains_header(self):
        """Test that layout contains header section."""
        app = import_app("src.gui.app")
        layout_str = str(app.layout)
        assert "header" in layout_str
        assert "Circuit Analysis Dashboard" in layout_str
