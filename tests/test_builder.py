"""
Tests for the PySpice circuit builder.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from circuit_sim import Circuit
from circuit_sim.simulator.builder import PySpiceBuilder


class TestPySpiceBuilder:
    """Test the PySpice builder."""

    def test_builder_creation(self):
        """Test that builder can be created."""
        builder = PySpiceBuilder()
        assert builder is not None

    def test_pyspice_not_installed(self):
        """Test error when PySpice is not installed."""
        builder = PySpiceBuilder()
        builder._pyspice_available = False

        circuit = Circuit("Test")
        with pytest.raises(ImportError, match="PySpice is not installed"):
            builder.build_circuit(circuit)

    @patch("circuit_sim.simulator.builder.PySpiceBuilder._check_pyspice")
    def test_build_simple_resistor(self, mock_check):
        """Test building a simple resistor circuit."""
        mock_check.return_value = True

        # Mock PySpice imports inside the method

        mock_pyspice = MagicMock()
        mock_pyspice.Spice.Netlist.Circuit = MagicMock()

        # Mock units to support @ operator (matrix multiplication in Python 3.5+)
        # Create mock unit objects that return the numeric value when used with @
        class MockUnit:
            def __init__(self, multiplier=1):
                self.multiplier = multiplier

            def __rmatmul__(self, other):
                # This is called for: value @ unit
                return other * self.multiplier

        mock_pyspice.Unit.u_V = MockUnit()
        mock_pyspice.Unit.u_A = MockUnit()
        mock_pyspice.Unit.u_Ohm = MockUnit()
        mock_pyspice.Unit.u_F = MockUnit()
        mock_pyspice.Unit.u_H = MockUnit()

        with patch.dict(
            "sys.modules",
            {
                "PySpice": mock_pyspice,
                "PySpice.Spice": mock_pyspice.Spice,
                "PySpice.Spice.Netlist": mock_pyspice.Spice.Netlist,
                "PySpice.Unit": mock_pyspice.Unit,
            },
        ):
            builder = PySpiceBuilder()

            # Create simple circuit
            circuit = Circuit("Test")
            circuit.add_resistor("R1", 1, 0, "1k")

            # Build PySpice circuit
            builder.build_circuit(circuit)

            # Verify PySpice circuit was created
            mock_pyspice.Spice.Netlist.Circuit.assert_called_once_with("Test")

            # Verify resistor was added
            pyspice_instance = mock_pyspice.Spice.Netlist.Circuit.return_value
            pyspice_instance.R.assert_called_once()

    @patch("circuit_sim.simulator.builder.PySpiceBuilder._check_pyspice")
    def test_build_voltage_divider(self, mock_check):
        """Test building a voltage divider circuit."""
        mock_check.return_value = True

        # Mock PySpice

        mock_pyspice = MagicMock()
        mock_pyspice.Spice.Netlist.Circuit = MagicMock()

        class MockUnit:
            def __rmatmul__(self, other):
                return other

        mock_pyspice.Unit.u_V = MockUnit()
        mock_pyspice.Unit.u_A = MockUnit()
        mock_pyspice.Unit.u_Ohm = MockUnit()
        mock_pyspice.Unit.u_F = MockUnit()
        mock_pyspice.Unit.u_H = MockUnit()

        with patch.dict(
            "sys.modules",
            {
                "PySpice": mock_pyspice,
                "PySpice.Spice": mock_pyspice.Spice,
                "PySpice.Spice.Netlist": mock_pyspice.Spice.Netlist,
                "PySpice.Unit": mock_pyspice.Unit,
            },
        ):
            builder = PySpiceBuilder()

            # Create voltage divider
            circuit = (
                Circuit("Voltage Divider")
                .add_voltage_source("V1", 1, 0, "5V")
                .add_resistor("R1", 1, 2, "1k")
                .add_resistor("R2", 2, 0, "1k")
            )

            # Build PySpice circuit
            builder.build_circuit(circuit)

            pyspice_instance = mock_pyspice.Spice.Netlist.Circuit.return_value

            # Check voltage source added
            pyspice_instance.V.assert_called()

            # Check resistors added (2 calls)
            assert pyspice_instance.R.call_count == 2

    @patch("circuit_sim.simulator.builder.PySpiceBuilder._check_pyspice")
    def test_build_rc_circuit(self, mock_check):
        """Test building an RC circuit."""
        mock_check.return_value = True

        # Mock PySpice

        mock_pyspice = MagicMock()
        mock_pyspice.Spice.Netlist.Circuit = MagicMock()

        class MockUnit:
            def __rmatmul__(self, other):
                return other

        mock_pyspice.Unit.u_V = MockUnit()
        mock_pyspice.Unit.u_A = MockUnit()
        mock_pyspice.Unit.u_Ohm = MockUnit()
        mock_pyspice.Unit.u_F = MockUnit()
        mock_pyspice.Unit.u_H = MockUnit()

        with patch.dict(
            "sys.modules",
            {
                "PySpice": mock_pyspice,
                "PySpice.Spice": mock_pyspice.Spice,
                "PySpice.Spice.Netlist": mock_pyspice.Spice.Netlist,
                "PySpice.Unit": mock_pyspice.Unit,
            },
        ):
            builder = PySpiceBuilder()

            # Create RC circuit
            circuit = Circuit("RC Filter")
            circuit.add_voltage_source("Vin", 1, 0, "1V")
            circuit.add_resistor("R", 1, 2, "10k")
            circuit.add_capacitor("C", 2, 0, "100n")

            # Build PySpice circuit
            builder.build_circuit(circuit)

            pyspice_instance = mock_pyspice.Spice.Netlist.Circuit.return_value

            # Check all components added
            pyspice_instance.V.assert_called_once()
            pyspice_instance.R.assert_called_once()
            pyspice_instance.C.assert_called_once()

    @patch("circuit_sim.simulator.builder.PySpiceBuilder._check_pyspice")
    def test_build_inductor_circuit(self, mock_check):
        """Test building a circuit with an inductor."""
        mock_check.return_value = True

        # Mock PySpice

        mock_pyspice = MagicMock()
        mock_pyspice.Spice.Netlist.Circuit = MagicMock()

        class MockUnit:
            def __rmatmul__(self, other):
                return other

        mock_pyspice.Unit.u_V = MockUnit()
        mock_pyspice.Unit.u_A = MockUnit()
        mock_pyspice.Unit.u_Ohm = MockUnit()
        mock_pyspice.Unit.u_F = MockUnit()
        mock_pyspice.Unit.u_H = MockUnit()

        with patch.dict(
            "sys.modules",
            {
                "PySpice": mock_pyspice,
                "PySpice.Spice": mock_pyspice.Spice,
                "PySpice.Spice.Netlist": mock_pyspice.Spice.Netlist,
                "PySpice.Unit": mock_pyspice.Unit,
            },
        ):
            builder = PySpiceBuilder()

            # Create RL circuit
            circuit = Circuit("RL Circuit")
            circuit.add_voltage_source("V1", 1, 0, "12V")
            circuit.add_inductor("L1", 1, 2, "100m")  # 100mH
            circuit.add_resistor("R1", 2, 0, "100")

            # Build PySpice circuit
            builder.build_circuit(circuit)

            pyspice_instance = mock_pyspice.Spice.Netlist.Circuit.return_value

            # Check all components added
            pyspice_instance.V.assert_called_once()
            pyspice_instance.L.assert_called_once()
            pyspice_instance.R.assert_called_once()

    @patch("circuit_sim.simulator.builder.PySpiceBuilder._check_pyspice")
    def test_build_current_source(self, mock_check):
        """Test building a circuit with current source."""
        mock_check.return_value = True

        # Mock PySpice

        mock_pyspice = MagicMock()
        mock_pyspice.Spice.Netlist.Circuit = MagicMock()

        class MockUnit:
            def __rmatmul__(self, other):
                return other

        mock_pyspice.Unit.u_V = MockUnit()
        mock_pyspice.Unit.u_A = MockUnit()
        mock_pyspice.Unit.u_Ohm = MockUnit()
        mock_pyspice.Unit.u_F = MockUnit()
        mock_pyspice.Unit.u_H = MockUnit()

        with patch.dict(
            "sys.modules",
            {
                "PySpice": mock_pyspice,
                "PySpice.Spice": mock_pyspice.Spice,
                "PySpice.Spice.Netlist": mock_pyspice.Spice.Netlist,
                "PySpice.Unit": mock_pyspice.Unit,
            },
        ):
            builder = PySpiceBuilder()

            # Create current source circuit
            circuit = Circuit("Current Source")
            circuit.add_current_source("I1", 1, 0, "10m")  # 10mA
            circuit.add_resistor("R_load", 1, 0, "1k")

            # Build PySpice circuit
            builder.build_circuit(circuit)

            pyspice_instance = mock_pyspice.Spice.Netlist.Circuit.return_value

            # Check components added
            pyspice_instance.I.assert_called_once()
            pyspice_instance.R.assert_called_once()

    @patch("circuit_sim.simulator.builder.PySpiceBuilder._check_pyspice")
    def test_ground_node_handling(self, mock_check):
        """Test that ground nodes are handled correctly."""
        mock_check.return_value = True

        # Mock PySpice

        mock_pyspice = MagicMock()
        mock_pyspice.Spice.Netlist.Circuit = MagicMock()
        mock_gnd = Mock()
        mock_pyspice.Spice.Netlist.Circuit.return_value.gnd = mock_gnd

        class MockUnit:
            def __rmatmul__(self, other):
                return other

        mock_pyspice.Unit.u_V = MockUnit()
        mock_pyspice.Unit.u_A = MockUnit()
        mock_pyspice.Unit.u_Ohm = MockUnit()
        mock_pyspice.Unit.u_F = MockUnit()
        mock_pyspice.Unit.u_H = MockUnit()

        with patch.dict(
            "sys.modules",
            {
                "PySpice": mock_pyspice,
                "PySpice.Spice": mock_pyspice.Spice,
                "PySpice.Spice.Netlist": mock_pyspice.Spice.Netlist,
                "PySpice.Unit": mock_pyspice.Unit,
            },
        ):
            builder = PySpiceBuilder()

            # Create circuit with various ground representations
            circuit = Circuit("Ground Test")
            circuit.add_resistor("R1", 1, 0, "1k")  # numeric 0
            circuit.add_resistor("R2", 1, "gnd", "2k")  # string "gnd"
            circuit.add_resistor("R3", 1, "GND", "3k")  # uppercase "GND"

            # Build PySpice circuit
            builder.build_circuit(circuit)

            pyspice_instance = mock_pyspice.Spice.Netlist.Circuit.return_value

            # All ground nodes should use pyspice_circuit.gnd
            assert pyspice_instance.R.call_count == 3

    def test_unknown_component_type(self):
        """Test that unknown component types raise an error."""
        builder = PySpiceBuilder()
        builder._pyspice_available = True

        # Create circuit with invalid component
        circuit = Circuit("Invalid")
        circuit.components.append({"type": "unknown_component", "name": "X1"})

        # Mock PySpice

        mock_pyspice = MagicMock()
        mock_pyspice.Spice.Netlist.Circuit = MagicMock()

        class MockUnit:
            def __rmatmul__(self, other):
                return other

        mock_pyspice.Unit.u_V = MockUnit()
        mock_pyspice.Unit.u_A = MockUnit()
        mock_pyspice.Unit.u_Ohm = MockUnit()
        mock_pyspice.Unit.u_F = MockUnit()
        mock_pyspice.Unit.u_H = MockUnit()

        with patch.dict(
            "sys.modules",
            {
                "PySpice": mock_pyspice,
                "PySpice.Spice": mock_pyspice.Spice,
                "PySpice.Spice.Netlist": mock_pyspice.Spice.Netlist,
                "PySpice.Unit": mock_pyspice.Unit,
            },
        ):
            with pytest.raises(ValueError, match="Unknown component type"):
                builder.build_circuit(circuit)
