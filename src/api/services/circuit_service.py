"""
Circuit service for business logic operations.

Handles circuit creation, validation, storage, and retrieval.
"""

import uuid
from datetime import datetime
from typing import Dict, Optional

from src.api.models.circuit import CircuitCreate, CircuitResponse
from src.circuit_sim.circuit import Circuit


class CircuitService:
    """Service for managing circuits."""

    def __init__(self):
        """Initialize circuit service with in-memory storage."""
        self._circuits: Dict[str, dict] = {}

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
                circuit.add_resistor(comp.name, comp.positive_node, comp.negative_node, comp.value)
            elif comp.type == "capacitor":
                circuit.add_capacitor(comp.name, comp.positive_node, comp.negative_node, comp.value)
            elif comp.type == "inductor":
                circuit.add_inductor(comp.name, comp.positive_node, comp.negative_node, comp.value)
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
        response_data = {k: v for k, v in circuit_record.items() if k != "circuit_object"}
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
            response_data = {k: v for k, v in circuit_record.items() if k != "circuit_object"}
            circuit_responses.append(CircuitResponse(**response_data))

        return {"circuits": circuit_responses, "total": total, "skip": skip, "limit": limit}

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
