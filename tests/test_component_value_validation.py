"""
Tests for component value validation functions.
"""

import pytest

from circuit_sim.validation import (
    ComponentValueValidationResult,
    ComponentValueValidator,
    validate_capacitance,
    validate_inductance,
    validate_resistance,
    RESISTANCE_MAX,
    RESISTANCE_MIN,
    CAPACITANCE_MAX,
    CAPACITANCE_MIN,
    INDUCTANCE_MAX,
    INDUCTANCE_MIN,
)


class TestValidateResistance:
    """Test resistance validation function."""

    def test_valid_resistance_mid_range(self):
        """Test resistance in the middle of valid range."""
        result = validate_resistance(1000)  # 1kΩ
        assert result.is_valid
        assert result.value == 1000
        assert result.component_type == "resistor"
        assert result.error_message is None

    def test_valid_resistance_minimum(self):
        """Test resistance at minimum boundary (1mΩ)."""
        result = validate_resistance(RESISTANCE_MIN)
        assert result.is_valid
        assert result.value == RESISTANCE_MIN

    def test_valid_resistance_maximum(self):
        """Test resistance at maximum boundary (1GΩ)."""
        result = validate_resistance(RESISTANCE_MAX)
        assert result.is_valid
        assert result.value == RESISTANCE_MAX

    def test_valid_resistance_kilohm(self):
        """Test resistance in kilohms."""
        result = validate_resistance(4.7e3)  # 4.7kΩ
        assert result.is_valid
        assert result.value == 4700

    def test_valid_resistance_megohm(self):
        """Test resistance in megohms."""
        result = validate_resistance(1e6)  # 1MΩ
        assert result.is_valid

    def test_resistance_below_minimum(self):
        """Test resistance below minimum (1mΩ)."""
        result = validate_resistance(0.0001)  # 0.1mΩ
        assert not result.is_valid
        assert "below minimum" in result.error_message.lower()
        assert "1mΩ" in result.error_message or "0.001" in result.error_message

    def test_resistance_above_maximum(self):
        """Test resistance above maximum (1GΩ)."""
        result = validate_resistance(2e9)  # 2GΩ
        assert not result.is_valid
        assert "above maximum" in result.error_message.lower()
        assert "1GΩ" in result.error_message or "1000000000" in result.error_message


class TestValidateCapacitance:
    """Test capacitance validation function."""

    def test_valid_capacitance_mid_range(self):
        """Test capacitance in the middle of valid range."""
        result = validate_capacitance(1e-6)  # 1µF
        assert result.is_valid
        assert result.value == 1e-6
        assert result.component_type == "capacitor"
        assert result.error_message is None

    def test_valid_capacitance_minimum(self):
        """Test capacitance at minimum boundary (1pF)."""
        result = validate_capacitance(CAPACITANCE_MIN)
        assert result.is_valid
        assert result.value == CAPACITANCE_MIN

    def test_valid_capacitance_maximum(self):
        """Test capacitance at maximum boundary (10000µF = 0.01F)."""
        result = validate_capacitance(CAPACITANCE_MAX)
        assert result.is_valid
        assert result.value == CAPACITANCE_MAX

    def test_valid_capacitance_picofarad(self):
        """Test capacitance in picofarads."""
        result = validate_capacitance(100e-12)  # 100pF
        assert result.is_valid
        assert result.value == 1e-10

    def test_valid_capacitance_microfarad(self):
        """Test capacitance in microfarads."""
        result = validate_capacitance(10e-6)  # 10µF
        assert result.is_valid

    def test_valid_capacitance_millifarad(self):
        """Test capacitance in millifarads."""
        result = validate_capacitance(1e-3)  # 1mF = 1000µF
        assert result.is_valid

    def test_capacitance_below_minimum(self):
        """Test capacitance below minimum (1pF)."""
        result = validate_capacitance(0.5e-12)  # 0.5pF
        assert not result.is_valid
        assert "below minimum" in result.error_message.lower()
        assert "1pF" in result.error_message or "1e-12" in result.error_message

    def test_capacitance_above_maximum(self):
        """Test capacitance above maximum (10000µF)."""
        result = validate_capacitance(0.02)  # 20000µF
        assert not result.is_valid
        assert "above maximum" in result.error_message.lower()


class TestValidateInductance:
    """Test inductance validation function."""

    def test_valid_inductance_mid_range(self):
        """Test inductance in the middle of valid range."""
        result = validate_inductance(1e-3)  # 1mH
        assert result.is_valid
        assert result.value == 1e-3
        assert result.component_type == "inductor"
        assert result.error_message is None

    def test_valid_inductance_minimum(self):
        """Test inductance at minimum boundary (1nH)."""
        result = validate_inductance(INDUCTANCE_MIN)
        assert result.is_valid
        assert result.value == INDUCTANCE_MIN

    def test_valid_inductance_maximum(self):
        """Test inductance at maximum boundary (10H)."""
        result = validate_inductance(INDUCTANCE_MAX)
        assert result.is_valid
        assert result.value == INDUCTANCE_MAX

    def test_valid_inductance_microhenry(self):
        """Test inductance in microhenrys."""
        result = validate_inductance(100e-6)  # 100µH
        assert result.is_valid

    def test_valid_inductance_millihenry(self):
        """Test inductance in millihenrys."""
        result = validate_inductance(10e-3)  # 10mH
        assert result.is_valid

    def test_valid_inductance_henry(self):
        """Test inductance in henrys."""
        result = validate_inductance(5)  # 5H
        assert result.is_valid

    def test_inductance_below_minimum(self):
        """Test inductance below minimum (1nH)."""
        result = validate_inductance(0.5e-9)  # 0.5nH
        assert not result.is_valid
        assert "below minimum" in result.error_message.lower()
        assert "1nH" in result.error_message or "1e-9" in result.error_message

    def test_inductance_above_maximum(self):
        """Test inductance above maximum (10H)."""
        result = validate_inductance(20)  # 20H
        assert not result.is_valid
        assert "above maximum" in result.error_message.lower()


class TestComponentValueValidator:
    """Test ComponentValueValidator class."""

    def test_validator_valid_resistor(self):
        """Test validator with valid resistor."""
        from circuit_sim.circuit import Circuit

        circuit = Circuit("Test")
        circuit.add_resistor("R1", 1, 0, "1k")

        validator = ComponentValueValidator()
        result = validator.validate(circuit)

        assert result.is_valid
        assert len(result.issues) == 0

    def test_validator_invalid_resistor(self):
        """Test validator with invalid resistor (below minimum)."""
        from circuit_sim.circuit import Circuit

        circuit = Circuit("Test")
        circuit.add_resistor("R1", 1, 0, "0.0001")  # 0.1mΩ

        validator = ComponentValueValidator()
        result = validator.validate(circuit)

        assert not result.is_valid
        assert len(result.issues) == 1
        assert "R1" in result.issues[0].components

    def test_validator_valid_capacitor(self):
        """Test validator with valid capacitor."""
        from circuit_sim.circuit import Circuit

        circuit = Circuit("Test")
        circuit.add_capacitor("C1", 1, 0, "1u")

        validator = ComponentValueValidator()
        result = validator.validate(circuit)

        assert result.is_valid

    def test_validator_invalid_capacitor(self):
        """Test validator with invalid capacitor (above maximum)."""
        from circuit_sim.circuit import Circuit

        circuit = Circuit("Test")
        circuit.add_capacitor("C1", 1, 0, "20000u")  # 20000µF > 10000µF

        validator = ComponentValueValidator()
        result = validator.validate(circuit)

        assert not result.is_valid

    def test_validator_valid_inductor(self):
        """Test validator with valid inductor."""
        from circuit_sim.circuit import Circuit

        circuit = Circuit("Test")
        circuit.add_inductor("L1", 1, 0, "1m")

        validator = ComponentValueValidator()
        result = validator.validate(circuit)

        assert result.is_valid

    def test_validator_invalid_inductor(self):
        """Test validator with invalid inductor (below minimum)."""
        from circuit_sim.circuit import Circuit

        circuit = Circuit("Test")
        circuit.add_inductor("L1", 1, 0, "0.5n")  # 0.5nH < 1nH

        validator = ComponentValueValidator()
        result = validator.validate(circuit)

        assert not result.is_valid

    def test_validator_custom_ranges(self):
        """Test validator with custom ranges."""
        from circuit_sim.circuit import Circuit

        circuit = Circuit("Test")
        circuit.add_resistor("R1", 1, 0, "100")  # 100Ω

        # Custom range: 50Ω to 200Ω
        validator = ComponentValueValidator(
            resistance_range=(50, 200)
        )
        result = validator.validate(circuit)

        assert result.is_valid

    def test_validator_multiple_components(self):
        """Test validator with multiple components."""
        from circuit_sim.circuit import Circuit

        circuit = Circuit("Test")
        circuit.add_resistor("R1", 1, 0, "1k")  # Valid
        circuit.add_capacitor("C1", 1, 0, "1u")  # Valid
        circuit.add_inductor("L1", 1, 0, "1m")  # Valid

        validator = ComponentValueValidator()
        result = validator.validate(circuit)

        assert result.is_valid
        assert len(result.issues) == 0

    def test_validator_mixed_valid_invalid(self):
        """Test validator with mix of valid and invalid components."""
        from circuit_sim.circuit import Circuit

        circuit = Circuit("Test")
        circuit.add_resistor("R1", 1, 0, "1k")  # Valid
        circuit.add_resistor("R2", 1, 0, "0.0001")  # Invalid

        validator = ComponentValueValidator()
        result = validator.validate(circuit)

        assert not result.is_valid
        assert len(result.issues) == 1
        assert "R2" in result.issues[0].components


class TestComponentValueRanges:
    """Test that constants define correct ranges."""

    def test_resistance_range(self):
        """Test resistance range boundaries."""
        assert RESISTANCE_MIN == 0.001  # 1mΩ
        assert RESISTANCE_MAX == 1_000_000_000  # 1GΩ

    def test_capacitance_range(self):
        """Test capacitance range boundaries."""
        assert CAPACITANCE_MIN == 1e-12  # 1pF
        assert CAPACITANCE_MAX == 0.01  # 10000µF = 0.01F

    def test_inductance_range(self):
        """Test inductance range boundaries."""
        assert INDUCTANCE_MIN == 1e-9  # 1nH
        assert INDUCTANCE_MAX == 10  # 10H
