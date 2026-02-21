"""
Tests for graph connectivity detection functions.
"""

import pytest

from circuit_sim import Circuit
from circuit_sim.graph import (
    build_adjacency_graph,
    find_connected_components,
    find_isolated_nodes,
    find_isolated_subcircuits,
    find_nodes_reachable_from_ground,
    get_component_size,
    get_isolation_report,
    is_connected,
)


class TestBuildAdjacencyGraph:
    """Test adjacency graph building."""

    def test_simple_circuit(self):
        """Test building graph for simple circuit."""
        circuit = Circuit("Test")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        circuit.add_resistor("R2", node1=2, node2=3, resistance="1k")

        graph = build_adjacency_graph(circuit)

        assert 0 in graph  # Ground is always present
        assert 1 in graph
        assert 2 in graph
        assert 3 in graph
        assert 2 in graph[1]  # R1 connects nodes 1 and 2
        assert 1 in graph[2]
        assert 3 in graph[2]  # R2 connects nodes 2 and 3
        assert 2 in graph[3]

    def test_voltage_source_connections(self):
        """Test graph with voltage source."""
        circuit = Circuit("Test")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")

        graph = build_adjacency_graph(circuit)

        assert 0 in graph[1]
        assert 1 in graph[0]
        assert 2 in graph[1]
        assert 1 in graph[2]


class TestFindConnectedComponents:
    """Test connected component detection."""

    def test_single_component(self):
        """Test single connected component."""
        circuit = Circuit("Test")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")

        components = find_connected_components(circuit)

        # All nodes should be in one component
        assert len(components) == 1

    def test_multiple_components(self):
        """Test multiple disconnected components."""
        circuit = Circuit("Test")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        circuit.add_resistor("R2", node1=3, node2=4, resistance="1k")

        components = find_connected_components(circuit)

        assert len(components) == 3  # {0}, {1,2}, {3,4}


class TestFindNodesReachableFromGround:
    """Test finding nodes reachable from ground."""

    def test_all_nodes_connected_to_ground(self):
        """Test when all nodes are connected to ground."""
        circuit = Circuit("Test")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        circuit.add_capacitor("C1", node1=2, node2=0, capacitance="1u")

        reachable = find_nodes_reachable_from_ground(circuit)

        assert 0 in reachable
        assert 1 in reachable
        assert 2 in reachable

    def test_isolated_nodes_not_reachable(self):
        """Test that isolated nodes are not reachable."""
        circuit = Circuit("Test")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        circuit.add_resistor("R2", node1=3, node2=4, resistance="1k")  # Isolated

        reachable = find_nodes_reachable_from_ground(circuit)

        assert 0 in reachable
        assert 1 in reachable
        assert 2 in reachable
        assert 3 not in reachable
        assert 4 not in reachable


class TestFindIsolatedNodes:
    """Test finding isolated nodes."""

    def test_no_isolated_nodes(self):
        """Test circuit with no isolated nodes."""
        circuit = Circuit("Test")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")

        isolated = find_isolated_nodes(circuit)

        assert len(isolated) == 0

    def test_isolated_nodes_exist(self):
        """Test circuit with isolated nodes."""
        circuit = Circuit("Test")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        circuit.add_resistor("R2", node1=3, node2=4, resistance="1k")

        isolated = find_isolated_nodes(circuit)

        assert 3 in isolated
        assert 4 in isolated
        assert 0 not in isolated
        assert 1 not in isolated
        assert 2 not in isolated


class TestFindIsolatedSubcircuits:
    """Test finding isolated subcircuits."""

    def test_no_isolated_subcircuits(self):
        """Test circuit with no isolated subcircuits."""
        circuit = Circuit("Test")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")

        isolated = find_isolated_subcircuits(circuit)

        assert len(isolated) == 0

    def test_single_isolated_subcircuit(self):
        """Test circuit with one isolated subcircuit."""
        circuit = Circuit("Test")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        circuit.add_resistor("R2", node1=3, node2=4, resistance="1k")
        circuit.add_capacitor("C1", node1=4, node2=5, capacitance="1u")

        isolated = find_isolated_subcircuits(circuit)

        assert len(isolated) == 1
        assert 0 not in isolated[0]  # Ground should not be in isolated

    def test_multiple_isolated_subcircuits(self):
        """Test circuit with multiple isolated subcircuits."""
        circuit = Circuit("Test")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        circuit.add_resistor("R2", node1=3, node2=4, resistance="1k")
        circuit.add_resistor("R3", node1=5, node2=6, resistance="1k")

        isolated = find_isolated_subcircuits(circuit)

        # {0,1,2} connected to ground, {3,4} and {5,6} are isolated
        assert len(isolated) == 2


class TestGetIsolationReport:
    """Test the comprehensive isolation report."""

    def test_connected_circuit_report(self):
        """Test report for fully connected circuit."""
        circuit = Circuit("Test")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")

        report = get_isolation_report(circuit)

        assert report["is_ground_connected"] is True
        assert report["has_isolated_sections"] is False
        assert 0 in report["reachable_nodes"]
        assert 1 in report["reachable_nodes"]
        assert 2 in report["reachable_nodes"]
        assert len(report["isolated_nodes"]) == 0
        assert len(report["isolated_subcircuits"]) == 0

    def test_isolated_circuit_report(self):
        """Test report for circuit with isolated sections."""
        circuit = Circuit("Test")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        circuit.add_resistor("R2", node1=3, node2=4, resistance="1k")

        report = get_isolation_report(circuit)

        assert report["is_ground_connected"] is True
        assert report["has_isolated_sections"] is True
        assert 0 in report["reachable_nodes"]
        assert 1 in report["reachable_nodes"]
        assert 2 in report["reachable_nodes"]
        assert 3 in report["isolated_nodes"]
        assert 4 in report["isolated_nodes"]
        assert len(report["isolated_subcircuits"]) == 1


class TestIsConnected:
    """Test is_connected function."""

    def test_same_node(self):
        """Test connecting node to itself."""
        circuit = Circuit("Test")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")

        assert is_connected(circuit, 1, 1) is True

    def test_directly_connected(self):
        """Test directly connected nodes."""
        circuit = Circuit("Test")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")

        assert is_connected(circuit, 1, 2) is True

    def test_indirectly_connected(self):
        """Test indirectly connected nodes."""
        circuit = Circuit("Test")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        circuit.add_resistor("R2", node1=2, node2=3, resistance="1k")

        assert is_connected(circuit, 1, 3) is True

    def test_not_connected(self):
        """Test unconnected nodes."""
        circuit = Circuit("Test")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        circuit.add_resistor("R2", node1=3, node2=4, resistance="1k")

        assert is_connected(circuit, 1, 3) is False


class TestGetComponentSize:
    """Test get_component_size function."""

    def test_single_component(self):
        """Test single connected circuit."""
        circuit = Circuit("Test")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")

        size = get_component_size(circuit)

        assert size == 1

    def test_multiple_components(self):
        """Test multiple disconnected circuits."""
        circuit = Circuit("Test")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        circuit.add_resistor("R2", node1=3, node2=4, resistance="1k")

        size = get_component_size(circuit)

        assert size == 3  # {0}, {1,2}, {3,4}


class TestRealWorldCircuits:
    """Test with real-world circuit examples."""

    def test_voltage_divider(self):
        """Test voltage divider circuit."""
        circuit = Circuit("Voltage Divider")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="10V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        circuit.add_resistor("R2", node1=2, node2=0, resistance="1k")

        reachable = find_nodes_reachable_from_ground(circuit)
        isolated = find_isolated_nodes(circuit)

        # All nodes should be connected to ground
        assert reachable == {0, 1, 2}
        assert isolated == set()

    def test_rc_filter_with_isolated_output(self):
        """Test RC filter with isolated output (AC coupling)."""
        circuit = Circuit("AC Coupled RC Filter")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="10k")
        circuit.add_capacitor("C1", node1=2, node2=3, capacitance="1u")  # AC coupling
        circuit.add_resistor("R2", node1=3, node2=0, resistance="10k")

        # Node 3 is connected to ground through R2, so everything should be reachable
        reachable = find_nodes_reachable_from_ground(circuit)
        assert 3 in reachable

    def test_floating_opamp_circuit(self):
        """Test opamp circuit with floating section."""
        circuit = Circuit("Opamp with floating section")
        # Main circuit connected to ground
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        circuit.add_resistor("R1", node1=1, node2=2, resistance="10k")
        circuit.add_resistor("R2", node1=2, node2=0, resistance="10k")
        # Floating/unconnected subcircuit
        circuit.add_resistor("R3", node1=3, node2=4, resistance="1k")
        circuit.add_capacitor("C1", node1=4, node2=5, capacitance="1u")

        report = get_isolation_report(circuit)

        assert report["has_isolated_sections"] is True
        assert 3 in report["isolated_nodes"]
        assert 4 in report["isolated_nodes"]
        assert 5 in report["isolated_nodes"]
