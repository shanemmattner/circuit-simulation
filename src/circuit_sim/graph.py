"""
Graph connectivity detection for circuits.

This module provides tools for analyzing circuit connectivity,
including adjacency representation and connected components detection.
"""

from collections import defaultdict
from typing import Any, Dict, List, Set


def build_adjacency_graph(circuit: Any) -> Dict[Any, List[Any]]:
    """
    Build an adjacency list representation of a circuit.

    Creates a graph where nodes are circuit nodes and edges represent
    electrical connections between components.

    Args:
        circuit: Circuit object with components and nodes attributes

    Returns:
        Adjacency dictionary where keys are node IDs and values are
        lists of connected node IDs

    Example:
        >>> circuit = Circuit("Test Circuit")
        >>> circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        >>> circuit.add_resistor("R2", node1=2, node2=3, resistance="1k")
        >>> graph = build_adjacency_graph(circuit)
        >>> # Returns: {1: [2], 2: [1, 3], 3: [2], 0: []}
    """
    adjacency: Dict[Any, List[Any]] = defaultdict(list)

    # Initialize all nodes in the circuit
    for node in circuit.nodes:
        if node not in adjacency:
            adjacency[node] = []

    # Add edges for each component
    for component in circuit.components:
        nodes = _get_component_nodes(component)
        if len(nodes) >= 2:
            # Add edges between all pairs of nodes (for multi-terminal components)
            for i in range(len(nodes)):
                for j in range(i + 1, len(nodes)):
                    node1, node2 = nodes[i], nodes[j]
                    # Add bidirectional edge
                    if node2 not in adjacency[node1]:
                        adjacency[node1].append(node2)
                    if node1 not in adjacency[node2]:
                        adjacency[node2].append(node1)

    return dict(adjacency)


def _get_component_nodes(component: Dict[str, Any]) -> List[Any]:
    """
    Extract the connection nodes from a component.

    Args:
        component: Component dictionary

    Returns:
        List of node IDs (all terminals)
    """
    # Handle components with positive/negative terminals
    if "positive" in component and "negative" in component:
        return [component["positive"], component["negative"]]

    # Handle components with node1/node2
    if "node1" in component and "node2" in component:
        return [component["node1"], component["node2"]]

    # Handle 3-terminal components (transistors, opamps, etc.)
    terminals = []
    for key in ["collector", "base", "emitter"]:
        if key in component:
            terminals.append(component[key])
    for key in ["drain", "gate", "source"]:
        if key in component:
            terminals.append(component[key])
    if "vplus" in component:
        terminals.append(component["vplus"])
    if "vminus" in component:
        terminals.append(component["vminus"])
    if "vout" in component:
        terminals.append(component["vout"])
    if "vin" in component and "vin" not in terminals:
        terminals.append(component["vin"])

    return terminals


def find_connected_components(circuit: Any) -> List[Set[Any]]:
    """
    Find all connected components in a circuit using BFS/DFS.

    A connected component is a set of nodes that are electrically
    connected through one or more components.

    Args:
        circuit: Circuit object with components and nodes attributes

    Returns:
        List of sets, where each set contains the node IDs in that
        connected component

    Example:
        >>> circuit = Circuit("Test Circuit")
        >>> circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        >>> circuit.add_resistor("R2", node1=3, node2=4, resistance="1k")
        >>> components = find_connected_components(circuit)
        >>> # Returns: [{0}, {1, 2}, {3, 4}] (assuming node 0 is ground)
    """
    graph = build_adjacency_graph(circuit)

    if not graph:
        return []

    visited: Set[Any] = set()
    components: List[Set[Any]] = []

    for node in graph:
        if node not in visited:
            # BFS to find all nodes in this component
            component_nodes: Set[Any] = set()
            queue = [node]

            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue

                visited.add(current)
                component_nodes.add(current)

                # Add unvisited neighbors to queue
                for neighbor in graph.get(current, []):
                    if neighbor not in visited:
                        queue.append(neighbor)

            components.append(component_nodes)

    return components


def is_connected(circuit: Any, node1: Any, node2: Any) -> bool:
    """
    Check if two nodes are electrically connected.

    Args:
        circuit: Circuit object with components and nodes attributes
        node1: First node ID
        node2: Second node ID

    Returns:
        True if nodes are connected, False otherwise

    Example:
        >>> circuit = Circuit("Test Circuit")
        >>> circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        >>> is_connected(circuit, 1, 2)  # True
        >>> is_connected(circuit, 1, 3)  # False
    """
    if node1 == node2:
        return True

    graph = build_adjacency_graph(circuit)

    # BFS from node1 to see if we can reach node2
    visited: Set[Any] = set()
    queue = [node1]

    while queue:
        current = queue.pop(0)
        if current == node2:
            return True

        if current in visited:
            continue

        visited.add(current)

        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                queue.append(neighbor)

    return False


def get_component_size(circuit: Any) -> int:
    """
    Get the number of connected components in the circuit.

    Args:
        circuit: Circuit object with components and nodes attributes

    Returns:
        Number of connected components

    Example:
        >>> circuit = Circuit("Test Circuit")
        >>> circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        >>> get_component_size(circuit)  # Returns number of components
    """
    return len(find_connected_components(circuit))


def find_nodes_reachable_from_ground(circuit: Any) -> Set[Any]:
    """
    Find all nodes reachable from ground (node 0) using BFS.

    Performs a breadth-first search starting from ground (node 0)
    to find all nodes electrically connected to the ground reference.

    Args:
        circuit: Circuit object with components and nodes attributes

    Returns:
        Set of node IDs that are reachable from ground

    Example:
        >>> circuit = Circuit("Test Circuit")
        >>> circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        >>> circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        >>> circuit.add_resistor("R2", node1=3, node2=4, resistance="1k")
        >>> reachable = find_nodes_reachable_from_ground(circuit)
        >>> # Returns: {0, 1, 2} (nodes 3, 4 are not reachable from ground)
    """
    graph = build_adjacency_graph(circuit)

    if 0 not in graph:
        return set()

    visited: Set[Any] = set()
    queue = [0]

    while queue:
        current = queue.pop(0)
        if current in visited:
            continue

        visited.add(current)

        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                queue.append(neighbor)

    return visited


def find_isolated_nodes(circuit: Any) -> Set[Any]:
    """
    Find all nodes NOT reachable from ground (isolated nodes).

    These are nodes that have no electrical path to ground (node 0),
    meaning they are part of isolated or floating sections of the circuit.

    Args:
        circuit: Circuit object with components and nodes attributes

    Returns:
        Set of node IDs that are not reachable from ground

    Example:
        >>> circuit = Circuit("Test Circuit")
        >>> circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        >>> circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        >>> circuit.add_resistor("R2", node1=3, node2=4, resistance="1k")
        >>> isolated = find_isolated_nodes(circuit)
        >>> # Returns: {3, 4} (these nodes are not connected to ground)
    """
    reachable = find_nodes_reachable_from_ground(circuit)
    all_nodes = set(circuit.nodes)

    return all_nodes - reachable


def find_isolated_subcircuits(circuit: Any) -> List[Set[Any]]:
    """
    Find isolated subcircuits (connected components not connected to ground).

    An isolated subcircuit is a group of nodes that are electrically
    connected to each other but have no connection to ground (node 0).
    These represent floating sections of the circuit that may be
    intentional (e.g., AC coupling) or unintentional (design errors).

    Args:
        circuit: Circuit object with components and nodes attributes

    Returns:
        List of sets, where each set contains the node IDs in that
        isolated subcircuit. Empty list if no isolated subcircuits exist.

    Example:
        >>> circuit = Circuit("Test Circuit")
        >>> circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        >>> circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        >>> circuit.add_resistor("R2", node1=3, node2=4, resistance="1k")  # Isolated
        >>> circuit.add_capacitor("C1", node1=4, node2=5, capacitance="1u")  # Part of isolated
        >>> isolated = find_isolated_subcircuits(circuit)
        >>> # Returns: [{3, 4, 5}] (one isolated subcircuit with nodes 3, 4, 5)
    """
    reachable = find_nodes_reachable_from_ground(circuit)

    # Get all connected components
    all_components = find_connected_components(circuit)

    # Filter to only include components that don't contain ground
    isolated = []
    for component in all_components:
        if 0 not in component:
            isolated.append(component)

    return isolated


def get_isolation_report(circuit: Any) -> Dict[str, Any]:
    """
    Generate a comprehensive isolation report for the circuit.

    Provides detailed information about the circuit's connectivity
    relative to ground, including reachable nodes, isolated nodes,
    and isolated subcircuits.

    Args:
        circuit: Circuit object with components and nodes attributes

    Returns:
        Dictionary containing:
        - reachable_nodes: Set of nodes reachable from ground
        - isolated_nodes: Set of nodes not reachable from ground
        - isolated_subcircuits: List of isolated connected components
        - is_ground_connected: Whether ground (node 0) exists in the circuit
        - has_isolated_sections: Whether there are any isolated sections

    Example:
        >>> circuit = Circuit("Test Circuit")
        >>> circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        >>> circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        >>> circuit.add_resistor("R2", node1=3, node2=4, resistance="1k")
        >>> report = get_isolation_report(circuit)
        >>> # Returns detailed isolation analysis
    """
    reachable = find_nodes_reachable_from_ground(circuit)
    isolated_nodes = find_isolated_nodes(circuit)
    isolated_subcircuits = find_isolated_subcircuits(circuit)

    return {
        "reachable_nodes": reachable,
        "isolated_nodes": isolated_nodes,
        "isolated_subcircuits": isolated_subcircuits,
        "is_ground_connected": 0 in circuit.nodes,
        "has_isolated_sections": len(isolated_subcircuits) > 0,
    }


def find_ground_reachable_nodes(circuit: Any) -> Set[Any]:
    """
    Find all nodes reachable from ground (node 0) using BFS.

    This function traverses the circuit graph starting from the ground
    node (node 0) using breadth-first search to find all electrically
    connected nodes.

    Args:
        circuit: Circuit object with components and nodes attributes

    Returns:
        Set of node IDs that are electrically connected to ground

    Example:
        >>> circuit = Circuit("Test Circuit")
        >>> circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        >>> circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        >>> circuit.add_resistor("R2", node1=3, node2=4, resistance="1k")
        >>> ground_nodes = find_ground_reachable_nodes(circuit)
        >>> # Returns: {0, 1, 2} (node 3 and 4 are isolated)
    """
    graph = build_adjacency_graph(circuit)

    if 0 not in graph:
        return set()

    visited: Set[Any] = set()
    queue = [0]

    while queue:
        current = queue.pop(0)
        if current in visited:
            continue

        visited.add(current)

        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                queue.append(neighbor)

    return visited


def find_ground_reachable_nodes_dfs(circuit: Any) -> Set[Any]:
    """
    Find all nodes reachable from ground (node 0) using DFS.

    This function traverses the circuit graph starting from the ground
    node (node 0) using depth-first search to find all electrically
    connected nodes.

    Args:
        circuit: Circuit object with components and nodes attributes

    Returns:
        Set of node IDs that are electrically connected to ground

    Example:
        >>> circuit = Circuit("Test Circuit")
        >>> circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        >>> circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        >>> circuit.add_resistor("R2", node1=3, node2=4, resistance="1k")
        >>> ground_nodes = find_ground_reachable_nodes_dfs(circuit)
        >>> # Returns: {0, 1, 2} (node 3 and 4 are isolated)
    """
    graph = build_adjacency_graph(circuit)

    if 0 not in graph:
        return set()

    visited: Set[Any] = set()
    stack = [0]

    while stack:
        current = stack.pop()
        if current in visited:
            continue

        visited.add(current)

        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                stack.append(neighbor)

    return visited


def is_grounded(circuit: Any, node: Any) -> bool:
    """
    Check if a node is electrically connected to ground.

    Uses BFS to determine if the given node can be reached from
    the ground node (node 0).

    Args:
        circuit: Circuit object with components and nodes attributes
        node: Node ID to check

    Returns:
        True if node is connected to ground, False otherwise

    Example:
        >>> circuit = Circuit("Test Circuit")
        >>> circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        >>> circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        >>> is_grounded(circuit, 2)  # True (connected through R1 to ground)
        >>> is_grounded(circuit, 3)  # False (isolated node)
    """
    if node == 0:
        return True

    graph = build_adjacency_graph(circuit)

    # BFS from ground to see if we can reach the target node
    visited: Set[Any] = set()
    queue = [0]

    while queue:
        current = queue.pop(0)
        if current == node:
            return True

        if current in visited:
            continue

        visited.add(current)

        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                queue.append(neighbor)

    return False
