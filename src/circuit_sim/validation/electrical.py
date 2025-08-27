"""
Electrical validation rules for circuits.
"""

import logging
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from ..circuit import Circuit
from .base import Severity, ValidationIssue, ValidationResult, ValidationRule

logger = logging.getLogger(__name__)


class ShortCircuitDetector(ValidationRule):
    """Detects short circuits between voltage sources."""

    def __init__(
        self,
        short_threshold: float = 0.001,  # 1mΩ
        warning_threshold: float = 0.1,  # 100mΩ
        name: Optional[str] = None
    ):
        """
        Initialize short circuit detector.
        
        Args:
            short_threshold: Resistance below which it's considered a short (Ω)
            warning_threshold: Resistance below which to warn (Ω)
            name: Optional custom name for this rule
        """
        super().__init__(name or "ShortCircuitDetector")
        self.short_threshold = short_threshold
        self.warning_threshold = warning_threshold

    def validate(self, circuit: Circuit) -> ValidationResult:
        """
        Detect short circuits between voltage sources.
        
        Args:
            circuit: Circuit to validate
            
        Returns:
            ValidationResult with any short circuits found
        """
        # Find all voltage sources
        voltage_sources = self._find_voltage_sources(circuit)

        if len(voltage_sources) < 2:
            # Need at least 2 voltage sources to have a short
            return self._create_result(is_valid=True)

        # Build circuit graph
        graph = self._build_circuit_graph(circuit)

        # Check all pairs of voltage sources
        issues = []
        for i, source1 in enumerate(voltage_sources):
            for source2 in voltage_sources[i+1:]:
                resistance = self._find_path_resistance(graph, source1, source2)

                if resistance is not None:
                    issue = self._check_voltage_source_connection(
                        source1, source2, resistance
                    )
                    if issue:
                        issues.append(issue)

        # Determine overall validity (no errors)
        errors = [issue for issue in issues if issue.severity == Severity.ERROR]
        is_valid = len(errors) == 0

        return self._create_result(is_valid=is_valid, issues=issues)

    def _find_voltage_sources(self, circuit: Circuit) -> List[Dict]:
        """
        Find all voltage sources in the circuit.
        
        Args:
            circuit: Circuit to search
            
        Returns:
            List of voltage source information
        """
        sources = []

        for component in circuit.components:
            if component.get('type') == 'voltage_source':
                # Extract voltage value
                voltage = 0.0
                if 'dc_value' in component:
                    try:
                        # Handle string values like "5V"
                        voltage_str = str(component['dc_value']).upper().replace('V', '')
                        voltage = float(voltage_str)
                    except (ValueError, AttributeError):
                        voltage = 0.0

                sources.append({
                    'name': component['name'],
                    'positive': component.get('positive', component.get('node1', 0)),
                    'negative': component.get('negative', component.get('node2', 0)),
                    'voltage': voltage,
                    'component': component
                })

        return sources

    def _build_circuit_graph(self, circuit: Circuit) -> Dict[int, List[Tuple[int, float]]]:
        """
        Build a graph representation of the circuit.
        
        Args:
            circuit: Circuit to convert
            
        Returns:
            Graph as adjacency list with resistances
        """
        graph = defaultdict(list)

        for component in circuit.components:
            # Skip voltage sources (they don't contribute to path resistance)
            if component.get('type') == 'voltage_source':
                continue

            # Get nodes
            node1, node2 = self._get_component_nodes(component)

            # Get resistance
            resistance = self._get_component_resistance(component)

            # Add bidirectional edges
            graph[node1].append((node2, resistance))
            graph[node2].append((node1, resistance))

        return dict(graph)

    def _get_component_nodes(self, component) -> Tuple[int, int]:
        """Get the two nodes of a component."""
        if 'positive' in component and 'negative' in component:
            return component['positive'], component['negative']
        elif 'node1' in component and 'node2' in component:
            return component['node1'], component['node2']
        else:
            # Default fallback
            return 0, 1

    def _get_component_resistance(self, component) -> float:
        """Get the resistance of a component."""
        if 'resistance' in component:
            try:
                # Handle string values like "1k", "0"
                resistance_str = str(component['resistance']).upper()
                resistance_str = resistance_str.replace('K', '000').replace('M', '000000')
                resistance_str = resistance_str.replace('Ω', '').replace('OHM', '')
                return float(resistance_str)
            except (ValueError, AttributeError):
                return float('inf')  # Unknown resistance - treat as open
        elif 'type' in component:
            if component['type'] == 'resistor':
                return float('inf')  # Unknown resistor value
            elif component['type'] in ['capacitor', 'inductor']:
                # For DC analysis, capacitors are open, inductors are short
                return float('inf') if component['type'] == 'capacitor' else 0.0
            elif component['type'] in ['current_source']:
                return float('inf')  # Current sources are open for resistance calc

        return float('inf')  # Default to open circuit

    def _find_path_resistance(
        self,
        graph: Dict[int, List[Tuple[int, float]]],
        source1: Dict,
        source2: Dict
    ) -> Optional[float]:
        """
        Find minimum resistance path between two voltage sources.
        
        Args:
            graph: Circuit graph
            source1: First voltage source info
            source2: Second voltage source info
            
        Returns:
            Minimum resistance or None if no path exists
        """
        # Check if sources share nodes (direct connection)
        if (source1['positive'] == source2['positive'] and
            source1['negative'] == source2['negative']) or \
           (source1['positive'] == source2['negative'] and
            source1['negative'] == source2['positive']):
            return 0.0  # Direct connection

        # Use Dijkstra's algorithm to find minimum resistance path
        # For voltage sources, we need to find if there's a low resistance path
        # between their terminals (excluding the direct ground connections)

        # Special case: if both sources share ground, only check positive terminals
        if source1['negative'] == 0 and source2['negative'] == 0:
            # Both grounded sources - check path between positive terminals
            resistance = self._dijkstra_min_resistance(graph, source1['positive'], source2['positive'])
            return resistance

        # Try all combinations of terminals for more complex cases
        paths = []
        for s1_node in [source1['positive'], source1['negative']]:
            for s2_node in [source2['positive'], source2['negative']]:
                if s1_node != s2_node:  # Skip same node
                    resistance = self._dijkstra_min_resistance(graph, s1_node, s2_node)
                    if resistance is not None:
                        paths.append(resistance)

        return min(paths) if paths else None

    def _dijkstra_min_resistance(
        self,
        graph: Dict[int, List[Tuple[int, float]]],
        start: int,
        end: int
    ) -> Optional[float]:
        """
        Find minimum resistance path using Dijkstra's algorithm.
        
        Args:
            graph: Circuit graph
            start: Start node
            end: End node
            
        Returns:
            Minimum resistance or None if no path
        """
        import heapq

        distances = {node: float('inf') for node in graph}
        distances[start] = 0.0
        pq = [(0.0, start)]
        visited = set()

        while pq:
            current_dist, current_node = heapq.heappop(pq)

            if current_node in visited:
                continue

            visited.add(current_node)

            if current_node == end:
                return current_dist

            if current_node in graph:
                for neighbor, resistance in graph[current_node]:
                    if neighbor not in visited:
                        new_dist = current_dist + resistance
                        if new_dist < distances[neighbor]:
                            distances[neighbor] = new_dist
                            heapq.heappush(pq, (new_dist, neighbor))

        return None  # No path found

    def _check_voltage_source_connection(
        self,
        source1: Dict,
        source2: Dict,
        resistance: float
    ) -> Optional[ValidationIssue]:
        """
        Check if voltage source connection violates rules.
        
        Args:
            source1: First voltage source
            source2: Second voltage source  
            resistance: Resistance between them
            
        Returns:
            ValidationIssue if there's a problem, None otherwise
        """
        # Check thresholds first
        if resistance <= self.short_threshold:
            # Same voltage sources can be connected (parallel) - but warn if same nodes
            if abs(source1['voltage'] - source2['voltage']) < 0.001:  # 1mV tolerance
                if resistance == 0.0:  # Direct connection (same nodes)
                    return self._create_issue(
                        issue_type="direct_parallel",
                        severity=Severity.WARNING,
                        message=f"Voltage sources {source1['name']} and {source2['name']} are directly connected (same nodes) - {source1['voltage']}V",
                        components=[source1['name'], source2['name']],
                        suggestion="This is valid for parallel sources but consider if this was intentional"
                    )
                return None  # Same voltage, some resistance - OK
            else:
                # Different voltages with short/direct connection - ERROR
                return self._create_issue(
                    issue_type="short_circuit",
                    severity=Severity.ERROR,
                    message=f"Short circuit detected between {source1['name']} ({source1['voltage']}V) and {source2['name']} ({source2['voltage']}V) - resistance = {resistance:.6f}Ω",
                    components=[source1['name'], source2['name']],
                    suggestion=f"Add series resistance between voltage sources (recommended > {self.warning_threshold}Ω)"
                )
        elif resistance <= self.warning_threshold:
            # Same voltage check for warnings too
            if abs(source1['voltage'] - source2['voltage']) > 0.001:
                return self._create_issue(
                    issue_type="near_short_circuit",
                    severity=Severity.WARNING,
                    message=f"Near short circuit between {source1['name']} ({source1['voltage']}V) and {source2['name']} ({source2['voltage']}V) - resistance = {resistance:.6f}Ω",
                    components=[source1['name'], source2['name']],
                    suggestion=f"Consider increasing series resistance (recommended > {self.warning_threshold}Ω)"
                )

        return None
