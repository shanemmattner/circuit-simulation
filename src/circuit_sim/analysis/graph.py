"""
Circuit connectivity analysis module.

This module provides graph-based analysis for detecting isolated subcircuits,
finding nodes reachable from ground, and identifying floating components.
"""

from collections import defaultdict, deque
from typing import Any, Dict, List, Set, Tuple, Optional

from ..circuit import Circuit


class CircuitConnectivityAnalyzer:
    """
    Analyzes circuit connectivity using graph algorithms.
    
    This class builds a graph representation of the circuit and provides
    methods to identify disconnected sections, nodes reachable from ground,
    and isolated subcircuits.
    
    Example:
        >>> circuit = Circuit("Test Circuit")
        >>> circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
        >>> circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        >>> analyzer = CircuitConnectivityAnalyzer(circuit)
        >>> isolated = analyzer.find_isolated_nodes()
    """

    def __init__(self, circuit: Circuit) -> None:
        """
        Initialize the analyzer with a circuit.
        
        Args:
            circuit: Circuit to analyze
        """
        self.circuit = circuit
        self.graph: Dict[int, List[int]] = defaultdict(list)
        self._build_graph()

    def _build_graph(self) -> None:
        """Build graph representation from circuit components."""
        for component in self.circuit.components:
            nodes = self._get_component_nodes(component)
            # Add edges between all pairs of nodes
            for i, node1 in enumerate(nodes):
                for node2 in nodes[i + 1:]:
                    if node1 not in self.graph[node2]:
                        self.graph[node2].append(node1)
                    if node2 not in self.graph[node1]:
                        self.graph[node1].append(node2)

    def _get_component_nodes(self, component: Dict[str, Any]) -> List[int]:
        """
        Get all connection nodes for a component.
        
        Args:
            component: Component dictionary
            
        Returns:
            List of node IDs that this component connects to
        """
        terminals = []
        
        # Standard two-terminal components
        if "positive" in component and "negative" in component:
            terminals.extend([component["positive"], component["negative"]])
        elif "node1" in component and "node2" in component:
            terminals.extend([component["node1"], component["node2"]])
        
        # Handle component-specific terminals
        if component.get("type") == "opamp":
            # Opamp has 5 terminals: vplus, vminus, vout, vcc, vee
            if "vplus" in component and "vplus" not in terminals:
                terminals.append(component["vplus"])
            if "vminus" in component and "vminus" not in terminals:
                terminals.append(component["vminus"])
            if "vout" in component and "vout" not in terminals:
                terminals.append(component["vout"])
            if "vcc" in component and "vcc" not in terminals:
                terminals.append(component["vcc"])
            if "vee" in component and "vee" not in terminals:
                terminals.append(component["vee"])
        elif component.get("type") == "bjt_transistor":
            # BJT has 3 terminals
            for key in ["collector", "base", "emitter"]:
                if key in component and component[key] not in terminals:
                    terminals.append(component[key])
        elif component.get("type") == "mosfet":
            # MOSFET has 4 terminals
            for key in ["drain", "gate", "source", "bulk"]:
                if key in component and component[key] not in terminals:
                    terminals.append(component[key])
        elif component.get("type") == "diode":
            # Diode has anode and cathode
            if "anode" in component and "anode" not in terminals:
                terminals.append(component["anode"])
            if "cathode" in component and "cathode" not in terminals:
                terminals.append(component["cathode"])
        
        # Filter out invalid nodes
        return [n for n in terminals if n is not None]

    def find_connected_components(self) -> List[Set[int]]:
        """
        Find all connected components in the circuit.
        
        Returns:
            List of sets, where each set contains nodes in one connected component
            
        Example:
            >>> components = analyzer.find_connected_components()
            >>> print(f"Found {len(components)} connected components")
        """
        visited: Set[int] = set()
        components: List[Set[int]] = []
        
        for node in self.graph:
            if node not in visited:
                component = self._bfs_component(node, visited)
                components.append(component)
        
        # Also check nodes that have no connections (isolated nodes)
        all_circuit_nodes = set(self.circuit.nodes)
        connected_nodes = set()
        for comp in components:
            connected_nodes.update(comp)
        
        isolated_nodes = all_circuit_nodes - connected_nodes
        for node in isolated_nodes:
            if node != 0:  # Ground is handled in components
                components.append({node})
        
        return components

    def _bfs_component(self, start: int, visited: Set[int]) -> Set[int]:
        """Find all nodes in the component containing start using BFS."""
        component = set()
        queue = deque([start])
        
        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            component.add(node)
            
            for neighbor in self.graph.get(node, []):
                if neighbor not in visited:
                    queue.append(neighbor)
        
        return component

    def get_component_size(self, component: Set[int]) -> int:
        """
        Get the size (number of nodes) in a component.
        
        Args:
            component: Set of nodes in the component
            
        Returns:
            Number of nodes in the component
        """
        return len(component)

    def find_nodes_reachable_from_ground(self) -> Set[int]:
        """
        Find all nodes reachable from ground (node 0) using BFS.
        
        Returns:
            Set of node IDs reachable from ground
            
        Example:
            >>> reachable = analyzer.find_nodes_reachable_from_ground()
            >>> isolated = analyzer.circuit.nodes - reachable
        """
        if 0 not in self.graph and 0 not in self.circuit.nodes:
            return set()
        
        visited: Set[int] = set()
        queue = deque([0])
        
        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            
            for neighbor in self.graph.get(node, []):
                if neighbor not in visited:
                    queue.append(neighbor)
        
        return visited

    def find_isolated_nodes(self) -> Set[int]:
        """
        Find nodes not reachable from ground.
        
        Returns:
            Set of isolated node IDs
            
        Example:
            >>> isolated = analyzer.find_isolated_nodes()
            >>> if isolated:
            ...     print(f"Found {len(isolated)} isolated nodes: {isolated}")
        """
        reachable = self.find_nodes_reachable_from_ground()
        all_nodes = set(self.circuit.nodes)
        return all_nodes - reachable

    def find_isolated_subcircuits(self) -> List[Dict[str, Any]]:
        """
        Find subcircuits that have no ground connection.
        
        Returns:
            List of isolated subcircuit descriptions
            
        Example:
            >>> subcircuits = analyzer.find_isolated_subcircuits()
            >>> for sub in subcircuits:
            ...     print(f"Isolated: {sub['nodes']}")
        """
        components = self.find_connected_components()
        ground_component = None
        isolated = []
        
        for component in components:
            if 0 in component:
                ground_component = component
            elif len(component) > 0:
                isolated.append({
                    "nodes": list(component),
                    "size": len(component),
                    "node_list": sorted(component)
                })
        
        return isolated

    def visualize_isolated_sections(self) -> Dict[str, Any]:
        """
        Provide visualization data for isolated sections.
        
        Returns:
            Dictionary containing visualization data including:
            - isolated_nodes: List of isolated node IDs
            - isolated_subcircuits: List of isolated subcircuit info
            - graph_data: Adjacency list for visualization
            - component_info: Information about each connected component
            
        Example:
            >>> viz = analyzer.visualize_isolated_sections()
            >>> print(f"Isolated nodes: {viz['isolated_nodes']}")
        """
        isolated_nodes = list(self.find_isolated_nodes())
        isolated_subcircuits = self.find_isolated_subcircuits()
        components = self.find_connected_components()
        
        # Build component info
        component_info = []
        for i, comp in enumerate(components):
            comp_info = {
                "id": i,
                "nodes": sorted(comp),
                "size": len(comp),
                "has_ground": 0 in comp,
                "is_isolated": 0 not in comp
            }
            
            # Find components in this subcircuit
            comp_list = []
            for comp_obj in self.circuit.components:
                comp_nodes = self._get_component_nodes(comp_obj)
                if any(n in comp for n in comp_nodes):
                    comp_list.append(comp_obj.get("name", "unknown"))
            
            comp_info["components"] = comp_list
            component_info.append(comp_info)
        
        return {
            "isolated_nodes": isolated_nodes,
            "isolated_subcircuits": isolated_subcircuits,
            "total_components": len(components),
            "isolated_count": len(isolated_subcircuits),
            "graph_data": dict(self.graph),
            "component_info": component_info,
            "ground_reachable": list(self.find_nodes_reachable_from_ground())
        }

    def suggest_connection_points(self) -> List[Dict[str, Any]]:
        """
        Suggest potential connection points for isolated sections.
        
        This identifies isolated subcircuits and suggests the nearest
        ground-reachable nodes that could be used for connection.
        
        Returns:
            List of suggestions, each containing:
            - isolated_nodes: The isolated nodes
            - suggested_connection: Nearest ground-reachable node
            - distance: Graph distance to the suggested connection point
            - reason: Explanation of why this connection is suggested
            
        Example:
            >>> suggestions = analyzer.suggest_connection_points()
            >>> for s in suggestions:
            ...     print(f"Connect to node {s['suggested_connection']}")
        """
        isolated_subcircuits = self.find_isolated_subcircuits()
        reachable = self.find_nodes_reachable_from_ground()
        
        if not reachable:
            return []
        
        suggestions = []
        
        for subcircuit in isolated_subcircuits:
            isolated_nodes = subcircuit["nodes"]
            best_connection = None
            best_distance = float('inf')
            
            # Find the nearest reachable node for each isolated node
            for iso_node in isolated_nodes:
                # BFS to find nearest reachable node
                distance = self._find_nearest_reachable(iso_node, reachable)
                if distance is not None and distance < best_distance:
                    best_distance = distance
                    best_connection = iso_node
            
            if best_connection is not None:
                suggestions.append({
                    "isolated_nodes": isolated_nodes,
                    "suggested_connection": best_connection,
                    "distance": best_distance,
                    "reason": f"Nearest ground-reachable node at distance {best_distance}"
                })
        
        return suggestions

    def _find_nearest_reachable(self, start: int, reachable: Set[int]) -> Optional[int]:
        """Find the shortest distance from start to any reachable node."""
        if start in reachable:
            return 0
        
        visited = {start}
        queue = deque([(start, 0)])
        
        while queue:
            node, dist = queue.popleft()
            
            for neighbor in self.graph.get(node, []):
                if neighbor in reachable:
                    return dist + 1
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))
        
        return None

    def get_isolation_report(self) -> Dict[str, Any]:
        """
        Get a comprehensive isolation report for the circuit.
        
        Returns:
            Dictionary containing complete isolation analysis
            
        Example:
            >>> report = analyzer.get_isolation_report()
            >>> print(report["summary"])
        """
        reachable = self.find_nodes_reachable_from_ground()
        isolated_nodes = self.find_isolated_nodes()
        isolated_subcircuits = self.find_isolated_subcircuits()
        components = self.find_connected_components()
        visualization = self.visualize_isolated_sections()
        suggestions = self.suggest_connection_points()
        
        return {
            "summary": {
                "total_nodes": len(self.circuit.nodes),
                "ground_reachable_nodes": len(reachable),
                "isolated_nodes": len(isolated_nodes),
                "total_components": len(components),
                "isolated_subcircuits": len(isolated_subcircuits),
                "has_isolation_issues": len(isolated_nodes) > 0
            },
            "reachable_nodes": sorted(reachable),
            "isolated_nodes": sorted(isolated_nodes),
            "isolated_subcircuits": isolated_subcircuits,
            "component_sizes": [
                {"component_id": i, "size": len(c), "has_ground": 0 in c}
                for i, c in enumerate(components)
            ],
            "visualization": visualization,
            "connection_suggestions": suggestions
        }
