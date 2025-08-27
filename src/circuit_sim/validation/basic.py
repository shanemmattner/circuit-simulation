"""
Basic circuit validation rules.
"""

from typing import List

from ..circuit import Circuit
from .base import Severity, ValidationResult, ValidationRule


class BasicCircuitValidator(ValidationRule):
    """Basic circuit validation checks."""

    def __init__(self, name: str = "BasicCircuitValidator"):
        """Initialize basic circuit validator."""
        super().__init__(name)

    def validate(self, circuit: Circuit) -> ValidationResult:
        """
        Run basic validation checks.
        
        Args:
            circuit: Circuit to validate
            
        Returns:
            ValidationResult with basic validation issues
        """
        issues = []

        # Check if circuit has components
        if not circuit.components:
            issues.append(self._create_issue(
                issue_type="no_components",
                severity=Severity.ERROR,
                message="Circuit has no components",
                components=[],
                suggestion="Add at least one component to the circuit"
            ))

        # Check if circuit has at least one source
        has_source = any(
            comp.get('type') in ["voltage_source", "current_source"]
            for comp in circuit.components
        )
        if not has_source:
            issues.append(self._create_issue(
                issue_type="no_sources",
                severity=Severity.ERROR,
                message="Circuit has no voltage or current sources",
                components=[],
                suggestion="Add at least one voltage or current source"
            ))

        # Check for ground connection (node 0)
        if 0 not in circuit.nodes:
            issues.append(self._create_issue(
                issue_type="no_ground",
                severity=Severity.WARNING,
                message="Circuit has no explicit ground (node 0)",
                components=[],
                suggestion="Connect at least one component to node 0 (ground)"
            ))

        # Check for floating nodes (nodes with only one connection)
        floating_nodes = self._find_floating_nodes(circuit)
        for node in floating_nodes:
            issues.append(self._create_issue(
                issue_type="floating_node",
                severity=Severity.WARNING,
                message=f"Node {node} has only one connection (might be floating)",
                components=self._get_components_on_node(circuit, node),
                nodes=[node],
                suggestion=f"Connect node {node} to at least one more component"
            ))

        # Check for duplicate component names
        duplicates = self._find_duplicate_names(circuit)
        if duplicates:
            issues.append(self._create_issue(
                issue_type="duplicate_names",
                severity=Severity.ERROR,
                message=f"Duplicate component names: {', '.join(sorted(duplicates))}",
                components=list(duplicates),
                suggestion="Rename components to have unique names"
            ))

        # Separate errors and warnings
        errors = [issue for issue in issues if issue.severity == Severity.ERROR]
        is_valid = len(errors) == 0

        return self._create_result(is_valid=is_valid, issues=issues)

    def _find_floating_nodes(self, circuit: Circuit) -> List[int]:
        """Find nodes with only one connection."""
        node_connections = {}

        for comp in circuit.components:
            # Count connections for each node
            for node_key in ['positive', 'negative', 'node1', 'node2']:
                if node_key in comp:
                    node = comp[node_key]
                    node_connections[node] = node_connections.get(node, 0) + 1

        # Find nodes with only one connection (excluding ground)
        floating = []
        for node, count in node_connections.items():
            if count == 1 and node != 0:
                floating.append(node)

        return floating

    def _get_components_on_node(self, circuit: Circuit, node: int) -> List[str]:
        """Get names of components connected to a node."""
        components = []

        for comp in circuit.components:
            for node_key in ['positive', 'negative', 'node1', 'node2']:
                if comp.get(node_key) == node:
                    components.append(comp.get('name', 'unnamed'))
                    break

        return components

    def _find_duplicate_names(self, circuit: Circuit) -> set:
        """Find duplicate component names."""
        names = [comp.get('name', 'unnamed') for comp in circuit.components]
        duplicates = set()

        for name in names:
            if names.count(name) > 1:
                duplicates.add(name)

        return duplicates
