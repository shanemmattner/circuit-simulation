"""Tests for SPICE model loader utility."""

import pytest

from src.models.spice_loader import SpiceModelLoader, ModelNotFoundError


class TestSpiceModelLoader:
    """Test SPICE model loading functionality."""

    @pytest.fixture
    def loader(self):
        """Create a SpiceModelLoader instance."""
        return SpiceModelLoader()

    def test_initialization(self, loader):
        """Test loader initialization."""
        assert loader.library_path.exists()
        assert loader.library_path.name == "KiCad-Spice-Library"
        assert isinstance(loader.model_cache, dict)

    def test_find_model_in_library(self, loader):
        """Test finding a model file in the library."""
        # Test finding a common transistor
        results = loader._find_model_files("2N2222")
        assert len(results) > 0
        assert any("2n2222" in str(f).lower() for f in results)

    def test_load_transistor_model(self, loader):
        """Test loading a transistor model."""
        # Test with 2N3904 - common NPN transistor
        model = loader.load_transistor("2N3904")
        assert model is not None
        assert ".model" in model.lower() or ".subckt" in model.lower()

    def test_load_opamp_model(self, loader):
        """Test loading an op-amp model."""
        # Test with LM358 - common op-amp
        model = loader.load_opamp("LM358")
        assert model is not None
        assert ".subckt" in model.lower()

    def test_load_diode_model(self, loader):
        """Test loading a diode model."""
        # Test with 1N4148 - common signal diode
        model = loader.load_diode("1N4148")
        assert model is not None
        assert ".model" in model.lower()

    def test_model_caching(self, loader):
        """Test that models are cached after first load."""
        # Load a model twice
        model1 = loader.load_transistor("2N3904")
        model2 = loader.load_transistor("2N3904")

        # Should be the same cached instance
        assert model1 is model2
        assert "transistor_2N3904" in loader.model_cache

    def test_model_not_found_error(self, loader):
        """Test error handling for non-existent models."""
        with pytest.raises(ModelNotFoundError) as exc_info:
            loader.load_transistor("NONEXISTENT123")

        assert "NONEXISTENT123" in str(exc_info.value)

    def test_load_555_timer(self, loader):
        """Test loading 555 timer model."""
        model = loader.load_555_timer()
        assert model is not None
        # 555 timer should have multiple subcircuits
        assert ".subckt" in model.lower()

    def test_extract_model_from_lib(self, loader):
        """Test extracting specific model from library file."""
        lib_content = """
        * Test library
        .model 2N3904 NPN(Is=1e-14 Vaf=100)
        .model 2N3906 PNP(Is=1e-14 Vaf=100)
        """

        # Test extracting specific model
        model = loader._extract_model(lib_content, "2N3904")
        assert "2N3904" in model
        assert "NPN" in model
        assert "2N3906" not in model

    def test_search_priority(self, loader):
        """Test that manufacturer models are prioritized."""
        # When searching for a model, manufacturer should come first
        results = loader._find_model_files("LM358", prioritize=True)
        if results:
            # First result should be from manufacturer if available
            first_result = str(results[0])
            assert (
                "Manufacturer" in first_result
                or "Texas" in first_result
                or len(results) == 1
            )

    def test_get_available_models(self, loader):
        """Test listing available models by category."""
        # Get available op-amps
        opamps = loader.get_available_models("opamp")
        assert isinstance(opamps, list)
        assert len(opamps) > 0

        # Get available transistors
        transistors = loader.get_available_models("transistor")
        assert isinstance(transistors, list)
        assert len(transistors) > 0

    def test_load_resistor_model(self, loader):
        """Test loading a basic resistor model."""
        model = loader.load_passive("R", 1000)
        assert model is not None
        assert "1k" in model or "1000" in model

    def test_load_capacitor_model(self, loader):
        """Test loading a basic capacitor model."""
        model = loader.load_passive("C", 1e-6)
        assert model is not None
        assert "1u" in model or "1e-6" in model

    def test_load_inductor_model(self, loader):
        """Test loading a basic inductor model."""
        model = loader.load_passive("L", 1e-3)
        assert model is not None
        assert "1m" in model or "1e-3" in model


class TestModelNotFoundError:
    """Test custom exception for model not found."""

    def test_error_message(self):
        """Test error message formatting."""
        error = ModelNotFoundError("LM741", ["path1", "path2"])
        assert "LM741" in str(error)
        assert "Searched in:" in str(error)
