"""
Tests for the Circuit class.
"""

import pytest

from circuit_sim import Circuit


class TestCircuitBasics:
    """Test basic circuit creation and component addition."""

    def test_create_circuit(self):
        """Test creating a circuit with a name."""
        circuit = Circuit("Test Circuit")
        assert circuit.name == "Test Circuit"
        assert len(circuit.components) == 0
        assert 0 in circuit.nodes  # Ground should always exist

    def test_add_voltage_source(self):
        """Test adding a voltage source."""
        circuit = Circuit("Test")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")

        assert len(circuit.components) == 1
        component = circuit.components[0]
        assert component["type"] == "voltage_source"
        assert component["name"] == "V1"
        assert component["positive"] == 1
        assert component["negative"] == 0
        assert component["dc_value"] == "5V"
        assert 1 in circuit.nodes

    def test_add_resistor(self):
        """Test adding a resistor."""
        circuit = Circuit("Test")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")

        assert len(circuit.components) == 1
        component = circuit.components[0]
        assert component["type"] == "resistor"
        assert component["name"] == "R1"
        assert component["node1"] == 1
        assert component["node2"] == 2
        assert component["resistance"] == "1k"
        assert 1 in circuit.nodes
        assert 2 in circuit.nodes

    def test_add_capacitor(self):
        """Test adding a capacitor."""
        circuit = Circuit("Test")
        circuit.add_capacitor("C1", node1=1, node2=0, capacitance="10u")

        assert len(circuit.components) == 1
        component = circuit.components[0]
        assert component["type"] == "capacitor"
        assert component["name"] == "C1"
        assert component["capacitance"] == "10u"

    def test_add_inductor(self):
        """Test adding an inductor."""
        circuit = Circuit("Test")
        circuit.add_inductor("L1", node1=1, node2=2, inductance="1m")

        assert len(circuit.components) == 1
        component = circuit.components[0]
        assert component["type"] == "inductor"
        assert component["inductance"] == "1m"

    def test_add_current_source(self):
        """Test adding a current source."""
        circuit = Circuit("Test")
        circuit.add_current_source("I1", positive=1, negative=0, dc_value="10mA")

        assert len(circuit.components) == 1
        component = circuit.components[0]
        assert component["type"] == "current_source"
        assert component["dc_value"] == "10mA"

    def test_gnd_alias(self):
        """Test that 'gnd' is converted to node 0."""
        circuit = Circuit("Test")
        circuit.add_resistor("R1", node1=1, node2="gnd", resistance="1k")

        component = circuit.components[0]
        assert component["node2"] == 0

    def test_method_chaining(self):
        """Test that methods can be chained."""
        circuit = (
            Circuit("Test")
            .add_voltage_source("V1", 1, 0, "5V")
            .add_resistor("R1", 1, 2, "1k")
            .add_capacitor("C1", 2, 0, "1u")
        )

        assert len(circuit.components) == 3
        assert circuit.name == "Test"

    def test_circuit_repr(self):
        """Test string representation of circuit."""
        circuit = Circuit("RC Filter")
        circuit.add_resistor("R1", 1, 2, "1k")
        circuit.add_capacitor("C1", 2, 0, "1u")

        repr_str = repr(circuit)
        assert "RC Filter" in repr_str
        assert "2 components" in repr_str
        assert "3 nodes" in repr_str  # nodes 0, 1, 2


class TestCompleteCircuits:
    """Test complete circuit examples."""

    def test_voltage_divider(self):
        """Test creating a voltage divider circuit."""
        circuit = Circuit("Voltage Divider")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="10V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        circuit.add_resistor("R2", node1=2, node2=0, resistance="1k")

        assert len(circuit.components) == 3
        assert len(circuit.nodes) == 3  # 0, 1, 2

    def test_rc_filter(self):
        """Test creating an RC filter circuit."""
        circuit = Circuit("RC Low-Pass Filter")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="10k")
        circuit.add_capacitor("C1", node1=2, node2=0, capacitance="100n")

        assert len(circuit.components) == 3
        # Find components by type
        voltage_sources = [
            c for c in circuit.components if c["type"] == "voltage_source"
        ]
        resistors = [c for c in circuit.components if c["type"] == "resistor"]
        capacitors = [c for c in circuit.components if c["type"] == "capacitor"]

        assert len(voltage_sources) == 1
        assert len(resistors) == 1
        assert len(capacitors) == 1

    def test_rlc_circuit(self):
        """Test creating an RLC circuit."""
        circuit = (
            Circuit("RLC Circuit")
            .add_voltage_source("V1", 1, 0, "12V")
            .add_resistor("R1", 1, 2, "100")
            .add_inductor("L1", 2, 3, "10m")
            .add_capacitor("C1", 3, 0, "1u")
        )

        assert len(circuit.components) == 4
        assert len(circuit.nodes) == 4  # 0, 1, 2, 3


class TestSimulation:
    """Test simulation functionality (placeholder for now)."""

    def test_simulate_not_implemented(self):
        """Test that simulate raises NotImplementedError for now."""
        circuit = Circuit("Test")
        circuit.add_voltage_source("V1", 1, 0, "5V")
        circuit.add_resistor("R1", 1, 0, "1k")

        with pytest.raises(NotImplementedError):
            circuit.simulate(analysis="dc")
