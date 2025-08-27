"""
Circuit CRUD API endpoints.

Provides REST endpoints for circuit creation, retrieval, listing, and deletion.
"""

from typing import Dict

from fastapi import APIRouter, HTTPException, Query

from src.api.models.circuit import CircuitCreate, CircuitResponse
from src.api.services.circuit_service import CircuitService

router = APIRouter(prefix="/api/circuits", tags=["circuits"])

# Global circuit service instance (in production, use dependency injection)
circuit_service = CircuitService()


@router.post("", response_model=CircuitResponse, status_code=201)
async def create_circuit(circuit_data: CircuitCreate) -> CircuitResponse:
    """
    Create a new circuit.

    Args:
        circuit_data: Circuit creation request with components

    Returns:
        Created circuit with generated ID and metadata

    Raises:
        HTTPException: 422 if validation fails
    """
    try:
        return circuit_service.create_circuit(circuit_data)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/{circuit_id}", response_model=CircuitResponse)
async def get_circuit(circuit_id: str) -> CircuitResponse:
    """
    Get circuit by ID.

    Args:
        circuit_id: Unique circuit identifier

    Returns:
        Circuit details

    Raises:
        HTTPException: 404 if circuit not found
    """
    circuit = circuit_service.get_circuit(circuit_id)
    if not circuit:
        raise HTTPException(status_code=404, detail="Circuit not found")
    return circuit


@router.get("", response_model=Dict)
async def list_circuits(
    skip: int = Query(0, ge=0, description="Number of circuits to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum circuits to return"),
) -> Dict:
    """
    List all circuits with pagination.

    Args:
        skip: Number of circuits to skip for pagination
        limit: Maximum number of circuits to return

    Returns:
        Dictionary with circuits list, total count, and pagination info
    """
    return circuit_service.list_circuits(skip=skip, limit=limit)


@router.delete("/{circuit_id}", status_code=204)
async def delete_circuit(circuit_id: str) -> None:
    """
    Delete circuit by ID.

    Args:
        circuit_id: Unique circuit identifier

    Raises:
        HTTPException: 404 if circuit not found
    """
    deleted = circuit_service.delete_circuit(circuit_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Circuit not found")
