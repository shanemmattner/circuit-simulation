"""
Tests for CircuitConnectivityAnalyzer - ground path finding and connectivity analysis.
"""

import pytest

from circuit_sim import Circuit
from circuit_sim.analysis import CircuitConnectivityAnalyzer


class TestGroundPathFinding:
    """Tests for ground path finding (nodes reachable from ground)."""

    def test_simple_circuit_ground_reachable(self):
        """Test that all nodes in a simple grounded circuit are reachable."""
        circuit = Circuit("Simple Grounded Circuit")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        circuit.add_resistor("R2", node1=2, node2=0, resistance="1k")

        analyzer = CircuitConnectivityAnalyzer(circuit)
        reachable = analyzer.find_nodes_reachable_from_ground()

        # Ground (0) and all connected nodes should be reachable
        assert 0 in reachable
        assert 1 in reachable
        assert 2 in reachable

    def test_voltage_divider_ground_reachable(self):
        """Test ground reachable nodes in a voltage divider."""
        circuit = Circuit("Voltage Divider")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="10V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        circuit.add_resistor("R2", node1=2, node2=0, resistance="1k")

        analyzer = CircuitConnectivityAnalyzer(circuit)
        reachable = analyzer.find_nodes_reachable_from_ground()

        # All three nodes (0, 1, 2) should be reachable from ground
        assert reachable == {0, 1, 2}

    def test_rc_filter_ground_reachable(self):
        """Test ground reachable nodes in an RC filter."""
        circuit = Circuit("RC Filter")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="10k")
        circuit.add_capacitor("C1", node1=2, node2=0, capacitance="100n")

        analyzer = CircuitConnectivityAnalyzer(circuit)
        reachable = analyzer.find_nodes_reachable_from_ground()

        # All three nodes should be reachable
        assert reachable == {0, 1, 2}

    def test_isolated_node_not_reachable(self):
        """Test that isolated nodes are not reachable from ground."""
        circuit = Circuit("Circuit with Isolated Node")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        # Node 3 is not connected to ground
        circuit.add_resistor("R2", node1=3, node2=4, resistance="1k")

        analyzer = CircuitConnectivityAnalyzer(circuit)
        reachable = analyzer.find_nodes_reachable_from_ground()

        # Only nodes connected to ground should be reachable
        assert 0 in reachable
        assert 1 in reachable
        assert 2 in reachable
        # Isolated nodes 3 and 4 should not be reachable
        assert 3 not in reachable
        assert 4 not in reachable

    def test_no_ground_returns_empty(self):
        """Test that circuit with no ground returns empty set."""
        circuit = Circuit("Isolated Circuit")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        circuit.add_resistor("R2", node1=3, node2=4, resistance="1k")

        analyzer = CircuitConnectivityAnalyzer(circuit)
        reachable = analyzer.find_nodes_reachable_from_ground()

        # No nodes should be reachable without ground
        assert reachable == set()

    def test_single_voltage_source(self):
        """Test ground reachable from a single voltage source."""
        circuit = Circuit("Single Source")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")

        analyzer = CircuitConnectivityAnalyzer(circuit)
        reachable = analyzer.find_nodes_reachable_from_ground()

        assert reachable == {0, 1}

    def test_ground_node_always_reachable(self):
        """Test that ground node (0) is always reachable from itself."""
        circuit = Circuit("Ground Only")
        # Just ground, no components

        analyzer = CircuitConnectivityAnalyzer(circuit)
        reachable = analyzer.find_nodes_reachable_from_ground()

        assert 0 in reachable


class TestIsolatedNodes:
    """Tests for finding isolated nodes (not reachable from ground)."""

    def test_find_isolated_nodes(self):
        """Test finding nodes not reachable from ground."""
        circuit = Circuit("Mixed Circuit")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        # Nodes 3 and 4 are isolated
        circuit.add_resistor("R2", node1=3, node2=4, resistance="1k")

        analyzer = CircuitConnectivityAnalyzer(circuit)
        isolated = analyzer.find_isolated_nodes()

        # Nodes 3 and 4 should be isolated
        assert 3 in isolated
        assert 4 in isolated
        # Ground-connected nodes should not be isolated
        assert 0 not in isolated
        assert 1 not in isolated
        assert 2 not in isolated

    def test_no_isolated_nodes(self):
        """Test that fully grounded circuit has no isolated nodes."""
        circuit = Circuit("Fully Grounded")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        circuit.add_resistor("R2", node1=2, node2=0, resistance="1k")

        analyzer = CircuitConnectivityAnalyzer(circuit)
        isolated = analyzer.find_isolated_nodes()

        assert isolated == set()

    def test_all_isolated_without_ground(self):
        """Test that circuit without ground has all nodes as isolated."""
        circuit = Circuit("No Ground")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")

        analyzer = CircuitConnectivityAnalyzer(circuit)
        isolated = analyzer.find_isolated_nodes()

        # All nodes should be isolated when there's no ground
        assert 1 in isolated
        assert 2 in isolated


class TestConnectedComponents:
    """Tests for finding connected components."""

    def test_single_component(self):
        """Test that a grounded circuit is one connected component."""
        circuit = Circuit("Single Component")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        circuit.add_resistor("R1", node1=1, node2=0, resistance="1k")

        analyzer = CircuitConnectivityAnalyzer(circuit)
        components = analyzer.find_connected_components()

        # Should be one component containing ground and node 1
        assert len(components) >= 1

    def test_multiple_components(self):
        """Test finding multiple disconnected components."""
        circuit = Circuit("Disconnected Circuit")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        # Second isolated subcircuit
        circuit.add_voltage_source("V2", positive=3, negative=4, dc_value="3V")
        circuit.add_resistor("R2", node1=3, node2=4, resistance="1k")

        analyzer = CircuitConnectivityAnalyzer(circuit)
        components = analyzer.find_connected_components()

        # Should have at least 2 components
        assert len(components) >= 2

    def test_component_sizes(self):
        """Test getting component sizes."""
        circuit = Circuit("Test Sizes")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        circuit.add_resistor("R2", node1=2, node2=3, resistance="1k")

        analyzer = CircuitConnectivityAnalyzer(circuit)
        components = analyzer.find_connected_components()

        # Find the main component (containing ground)
        main_component = None
        for comp in components:
            if 0 in comp:
                main_component = comp
                break

        assert main_component is not None
        assert len(main_component) == 4  # nodes 0, 1, 2, 3


class TestComplexCircuits:
    """Tests for more complex circuit scenarios."""

    def test_mixed_component_types(self):
        """Test ground reachability with various component types."""
        circuit = Circuit("Mixed Components")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="12V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        circuit.add_capacitor("C1", node1=2, node2=3, capacitance="10u")
        circuit.add_inductor("L1", node1=3, node2=0, inductance="1m")
        circuit.add_diode("D1", anode=2, cathode=4)
        circuit.add_resistor("R2", node1=4, node2=0, resistance="10k")

        analyzer = CircuitConnectivityAnalyzer(circuit)
        reachable = analyzer.find_nodes_reachable_from_ground()

        # All nodes connected to ground should be reachable
        assert 0 in reachable
        assert 1 in reachable
        assert 2 in reachable
        assert 3 in reachable
        assert 4 in reachable

    def test_rlc_circuit_grounded(self):
        """Test ground reachable in RLC circuit."""
        circuit = Circuit("RLC Circuit")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="12V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="100")
        circuit.add_inductor("L1", node1=2, node2=3, inductance="10m")
        circuit.add_capacitor("C1", node1=3, node2=0, capacitance="1u")

        analyzer = CircuitConnectivityAnalyzer(circuit)
        reachable = analyzer.find_nodes_reachable_from_ground()

        # All four nodes should be reachable
        assert reachable == {0, 1, 2, 3}


class TestGndAlias:
    """Tests for 'gnd' string alias handling."""

    def test_gnd_string_converts_to_node_0(self):
        """Test that 'gnd' string is properly handled."""
        circuit = Circuit("GND Alias Test")
        circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="5V")
        circuit.add_resistor("R1", node1=1, node2="gnd", resistance="1k")

        analyzer = CircuitConnectivityAnalyzer(circuit)
        reachable = analyzer.find_nodes_reachable_from_ground()

        # Node 0 should be in the circuit nodes (converted from 'gnd')
        assert 0 in circuit.nodes
        # All nodes should be reachable
        assert reachable == {0, 1}
