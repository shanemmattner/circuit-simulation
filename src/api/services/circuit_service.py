"""
Circuit service for business logic operations.

Handles circuit creation, validation, storage, and retrieval.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from src.api.models.circuit import (
    CircuitCreate,
    CircuitResponse,
    CircuitUpdate,
    CircuitValidationResponse,
    ValidationIssueResponse,
    ValidationResultResponse,
)
from src.circuit_sim.circuit import Circuit
from src.circuit_sim.validation import (
    BasicCircuitValidator,
    CircuitValidator,
    ComponentValueValidator,
)


class CircuitService:
    """Service for managing circuits."""

    def __init__(self):
        """Initialize circuit service with in-memory storage."""
        self._circuits: Dict[str, dict] = {}

    def _build_circuit_object(self, name: str, components: List[dict]) -> Circuit:
        """
        Build a Circuit object from component data.

        Args:
            name: Circuit name
            components: List of component dictionaries

        Returns:
            Circuit object
        """
        circuit = Circuit(name)

        for comp in components:
            comp_type = comp.get("type")
            comp_name = comp.get("name")
            pos_node = comp.get("positive_node")
            neg_node = comp.get("negative_node")
            value = comp.get("value")

            if comp_type == "voltage_source":
                circuit.add_voltage_source(comp_name, pos_node, neg_node, value)
            elif comp_type == "resistor":
                circuit.add_resistor(comp_name, pos_node, neg_node, value)
            elif comp_type == "capacitor":
                circuit.add_capacitor(comp_name, pos_node, neg_node, value)
            elif comp_type == "inductor":
                circuit.add_inductor(comp_name, pos_node, neg_node, value)
            elif comp_type == "current_source":
                circuit.add_current_source(comp_name, pos_node, neg_node, value)

        return circuit

    def validate_circuit(self, circuit_id: str) -> Optional[CircuitValidationResponse]:
        """
        Validate a circuit using the validation framework.

        Args:
            circuit_id: Circuit identifier

        Returns:
            CircuitValidationResponse if circuit found, None otherwise
        """
        circuit_record = self._circuits.get(circuit_id)
        if not circuit_record:
            return None

        # Build circuit object from stored components
        circuit = self._build_circuit_object(
            circuit_record["name"], circuit_record["components"]
        )

        # Set up validator with all validation rules
        validator = CircuitValidator()
        validator.add_rule(BasicCircuitValidator())
        validator.add_rule(ComponentValueValidator())

        # Run validation
        results = validator.validate(circuit)

        # Convert results to response format
        validation_results = []
        total_errors = 0
        total_warnings = 0

        for rule_name, result in results.items():
            issues = []
            warnings = []
            info = []

            for issue in result.issues:
                issues.append(
                    ValidationIssueResponse(
                        type=issue.type,
                        severity="error",
                        message=issue.message,
                        components=issue.components,
                        nodes=issue.nodes,
                        suggestion=issue.suggestion,
                    )
                )

            for warning in result.warnings:
                warnings.append(
                    ValidationIssueResponse(
                        type=warning.type,
                        severity="warning",
                        message=warning.message,
                        components=warning.components,
                        nodes=warning.nodes,
                        suggestion=warning.suggestion,
                    )
                )

            for info_item in result.info:
                info.append(
                    ValidationIssueResponse(
                        type=info_item.type,
                        severity="info",
                        message=info_item.message,
                        components=info_item.components,
                        nodes=info_item.nodes,
                        suggestion=info_item.suggestion,
                    )
                )

            validation_results.append(
                ValidationResultResponse(
                    rule_name=rule_name,
                    is_valid=result.is_valid,
                    issues=issues,
                    warnings=warnings,
                    info=info,
                    suggestions=result.suggestions,
                )
            )

            total_errors += len(issues) + len(warnings)
            total_warnings += len(warnings)

        return CircuitValidationResponse(
            is_valid=total_errors == 0,
            total_errors=total_errors,
            total_warnings=total_warnings,
            results=validation_results,
        )

    def create_circuit(self, circuit_data: CircuitCreate) -> CircuitResponse:
        """
        Create a new circuit from input data.

        Args:
            circuit_data: Circuit creation request data

        Returns:
            CircuitResponse with circuit details
        """
        # Generate unique ID
        circuit_id = str(uuid.uuid4())

        # Create internal circuit object to validate and count nodes
        circuit = Circuit(circuit_data.name)

        # Add components to count nodes properly
        for comp in circuit_data.components:
            if comp.type == "voltage_source":
                circuit.add_voltage_source(
                    comp.name, comp.positive_node, comp.negative_node, comp.value
                )
            elif comp.type == "resistor":
                circuit.add_resistor(
                    comp.name, comp.positive_node, comp.negative_node, comp.value
                )
            elif comp.type == "capacitor":
                circuit.add_capacitor(
                    comp.name, comp.positive_node, comp.negative_node, comp.value
                )
            elif comp.type == "inductor":
                circuit.add_inductor(
                    comp.name, comp.positive_node, comp.negative_node, comp.value
                )
            elif comp.type == "current_source":
                circuit.add_current_source(
                    comp.name, comp.positive_node, comp.negative_node, comp.value
                )

        # Store circuit data
        now = datetime.now()
        circuit_record = {
            "id": circuit_id,
            "name": circuit_data.name,
            "description": circuit_data.description,
            "components": [comp.model_dump() for comp in circuit_data.components],
            "component_count": len(circuit_data.components),
            "node_count": len(circuit.nodes),
            "created_at": now,
            "updated_at": now,
            "circuit_object": circuit,  # Keep for simulation
        }

        self._circuits[circuit_id] = circuit_record

        return CircuitResponse(**circuit_record)

    def get_circuit(self, circuit_id: str) -> Optional[CircuitResponse]:
        """
        Get circuit by ID.

        Args:
            circuit_id: Circuit identifier

        Returns:
            CircuitResponse if found, None otherwise
        """
        circuit_record = self._circuits.get(circuit_id)
        if not circuit_record:
            return None

        # Don't include circuit_object in response
        response_data = {
            k: v for k, v in circuit_record.items() if k != "circuit_object"
        }
        return CircuitResponse(**response_data)

    def list_circuits(self, skip: int = 0, limit: int = 100) -> Dict:
        """
        List all circuits with pagination.

        Args:
            skip: Number of circuits to skip
            limit: Maximum number of circuits to return

        Returns:
            Dictionary with circuits list and total count
        """
        circuits = list(self._circuits.values())
        total = len(circuits)

        # Apply pagination
        paginated_circuits = circuits[skip : skip + limit]

        # Convert to response format
        circuit_responses = []
        for circuit_record in paginated_circuits:
            response_data = {
                k: v for k, v in circuit_record.items() if k != "circuit_object"
            }
            circuit_responses.append(CircuitResponse(**response_data))

        return {
            "circuits": circuit_responses,
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    def delete_circuit(self, circuit_id: str) -> bool:
        """
        Delete circuit by ID.

        Args:
            circuit_id: Circuit identifier

        Returns:
            True if deleted, False if not found
        """
        if circuit_id in self._circuits:
            del self._circuits[circuit_id]
            return True
        return False

    def get_circuit_object(self, circuit_id: str) -> Optional[Circuit]:
        """
        Get internal circuit object for simulation.

        Args:
            circuit_id: Circuit identifier

        Returns:
            Circuit object if found, None otherwise
        """
        circuit_record = self._circuits.get(circuit_id)
        if circuit_record:
            return circuit_record["circuit_object"]
        return None
