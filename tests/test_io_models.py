"""
Test module for SPICE model loading functionality.
"""

from src.io.models.spice_models import ModelLibrary


class TestModelLibrary:
    """Test SPICE model library functionality."""

    def test_load_spice_model_2n3904(self):
        """Test loading 2N3904 NPN transistor model."""
        model_lib = ModelLibrary()
        model = model_lib.get_model("2N3904")

        assert model is not None
        assert model.name == "2N3904"
        assert model.model_type == "NPN"
        assert model.parameters["BF"] == 416.4  # Forward current gain
        assert model.parameters["IS"] == 6.734e-15  # Saturation current

    def test_load_spice_model_1n4148(self):
        """Test loading 1N4148 diode model."""
        model_lib = ModelLibrary()
        model = model_lib.get_model("1N4148")

        assert model is not None
        assert model.name == "1N4148"
        assert model.model_type == "D"
        assert model.parameters["IS"] == 2.52e-9
        assert "Fast switching diode" in model.description

    def test_model_library_initialization(self):
        """Test that model library loads with expected models."""
        model_lib = ModelLibrary()

        # Should have basic component models
        assert "2N3904" in model_lib.models
        assert "1N4148" in model_lib.models
        assert "LED_Red" in model_lib.models

        # Should have at least 10 models
        assert len(model_lib.models) >= 10

    def test_nonexistent_model(self):
        """Test handling of non-existent model."""
        model_lib = ModelLibrary()
        model = model_lib.get_model("DOESNOTEXIST")
        assert model is None
