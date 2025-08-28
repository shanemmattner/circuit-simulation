"""
Tests for short circuit detection validation.
"""

from circuit_sim.circuit import Circuit
from circuit_sim.validation import ShortCircuitDetector, ValidationResult


class TestShortCircuitDetection:
    """Test short circuit detection in circuits."""

    def test_no_short_circuit_single_source(self):
        """Test that single voltage source has no short circuit."""
        circuit = Circuit("Single Source")
        circuit.add_voltage_source("V1", 1, 0, "5V")
        circuit.add_resistor("R1", 1, 0, "1k")

        detector = ShortCircuitDetector()
        result = detector.validate(circuit)

        assert result.is_valid
        assert len(result.issues) == 0

    def test_short_circuit_direct_connection(self):
        """Test detection of directly connected voltage sources."""
        circuit = Circuit("Direct Short")
        circuit.add_voltage_source("V1", 1, 0, "5V")
        circuit.add_voltage_source("V2", 1, 0, "3V")  # Same nodes = direct short

        detector = ShortCircuitDetector()
        result = detector.validate(circuit)

        assert not result.is_valid
        assert len(result.issues) == 1
        assert "short circuit" in result.issues[0].message.lower()
        assert "V1" in result.issues[0].components
        assert "V2" in result.issues[0].components

    def test_short_circuit_through_wire(self):
        """Test detection of voltage sources connected through zero resistance."""
        circuit = Circuit("Wire Short")
        circuit.add_voltage_source("V1", 1, 0, "5V")
        circuit.add_voltage_source("V2", 2, 0, "3V")
        circuit.add_resistor("R1", 1, 2, "0")  # Zero resistance = wire

        detector = ShortCircuitDetector()
        result = detector.validate(circuit)

        assert not result.is_valid
        assert len(result.issues) == 1

    def test_near_short_circuit(self):
        """Test detection of very low resistance between sources."""
        circuit = Circuit("Near Short")
        circuit.add_voltage_source("V1", 1, 0, "5V")
        circuit.add_voltage_source("V2", 2, 0, "3V")
        circuit.add_resistor("R1", 1, 2, "0.0001")  # 0.1mΩ = near short

        detector = ShortCircuitDetector()
        result = detector.validate(circuit)

        # 0.1mΩ is below 1mΩ threshold, so should be error
        assert not result.is_valid  # Error, not warning
        assert len(result.issues) == 1
        assert "short circuit" in result.issues[0].message.lower()

    def test_valid_series_resistance(self):
        """Test that adequate series resistance is allowed."""
        circuit = Circuit("Series Resistance")
        circuit.add_voltage_source("V1", 1, 0, "5V")
        circuit.add_voltage_source("V2", 2, 0, "3V")
        circuit.add_resistor("R1", 1, 2, "10")  # 10Ω series resistance

        detector = ShortCircuitDetector()
        result = detector.validate(circuit)

        assert result.is_valid
        assert len(result.issues) == 0
        assert len(result.warnings) == 0

    def test_multiple_voltage_sources_no_shorts(self):
        """Test multiple voltage sources with proper isolation."""
        circuit = Circuit("Multiple Sources")
        circuit.add_voltage_source("V1", 1, 0, "5V")
        circuit.add_voltage_source("V2", 2, 0, "3V")
        circuit.add_voltage_source("V3", 3, 0, "12V")
        circuit.add_resistor("R1", 1, 4, "1k")
        circuit.add_resistor("R2", 2, 4, "2k")
        circuit.add_resistor("R3", 3, 4, "3k")

        detector = ShortCircuitDetector()
        result = detector.validate(circuit)

        assert result.is_valid

    def test_complex_short_circuit_path(self):
        """Test detection of short through multiple components."""
        circuit = Circuit("Complex Short Path")
        circuit.add_voltage_source("V1", 1, 0, "5V")
        circuit.add_voltage_source("V2", 3, 0, "3V")
        circuit.add_resistor("R1", 1, 2, "0")  # Wire
        circuit.add_resistor("R2", 2, 3, "0")  # Wire - creates short path

        detector = ShortCircuitDetector()
        result = detector.validate(circuit)

        assert not result.is_valid
        assert len(result.issues) == 1

    def test_same_voltage_sources_allowed(self):
        """Test that same voltage sources can be connected."""
        circuit = Circuit("Same Voltage")
        circuit.add_voltage_source("V1", 1, 0, "5V")
        circuit.add_voltage_source("V2", 1, 0, "5V")  # Same voltage - allowed

        detector = ShortCircuitDetector()
        result = detector.validate(circuit)

        # This should be valid but with warning (parallel voltage sources with same value)
        assert result.is_valid
        assert len(result.warnings) == 1
        assert "directly connected" in result.warnings[0].message.lower()

    def test_validation_result_structure(self):
        """Test that validation result has proper structure."""
        circuit = Circuit("Test Structure")
        circuit.add_voltage_source("V1", 1, 0, "5V")
        circuit.add_voltage_source("V2", 1, 0, "3V")

        detector = ShortCircuitDetector()
        result = detector.validate(circuit)

        assert isinstance(result, ValidationResult)
        assert hasattr(result, "is_valid")
        assert hasattr(result, "issues")
        assert hasattr(result, "warnings")
        assert hasattr(result, "suggestions")

        # Check issue structure
        if result.issues:
            issue = result.issues[0]
            assert hasattr(issue, "type")
            assert hasattr(issue, "severity")
            assert hasattr(issue, "message")
            assert hasattr(issue, "components")
            assert hasattr(issue, "suggestion")


class TestShortCircuitThresholds:
    """Test configurable thresholds for short circuit detection."""

    def test_custom_threshold(self):
        """Test custom resistance threshold."""
        circuit = Circuit("Custom Threshold")
        circuit.add_voltage_source("V1", 1, 0, "5V")
        circuit.add_voltage_source("V2", 2, 0, "3V")
        circuit.add_resistor("R1", 1, 2, "0.1")  # 0.1Ω

        # Default threshold (1mΩ) - 0.1Ω should be warning
        detector = ShortCircuitDetector()
        result = detector.validate(circuit)
        assert result.is_valid  # 0.1Ω > 1mΩ but < 100mΩ = warning
        assert len(result.warnings) == 1

        # Custom threshold (0.01Ω) - should be valid for 0.1Ω
        detector_custom = ShortCircuitDetector(
            short_threshold=0.01, warning_threshold=2.0
        )
        result_custom = detector_custom.validate(circuit)
        assert result_custom.is_valid

    def test_warning_threshold(self):
        """Test separate warning threshold."""
        circuit = Circuit("Warning Threshold")
        circuit.add_voltage_source("V1", 1, 0, "5V")
        circuit.add_voltage_source("V2", 2, 0, "3V")
        circuit.add_resistor("R1", 1, 2, "0.01")  # 10mΩ

        detector = ShortCircuitDetector(
            short_threshold=0.001,  # 1mΩ error threshold
            warning_threshold=0.1,  # 100mΩ warning threshold
        )
        result = detector.validate(circuit)

        assert result.is_valid  # No error
        assert len(result.warnings) == 1  # But has warning
