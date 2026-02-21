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
