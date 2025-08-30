"""
Circuit CRUD API endpoints.

Provides REST endpoints for circuit creation, retrieval, listing, and deletion.
"""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Query, Body

from src.api.models.circuit import CircuitCreate, CircuitResponse
from src.api.services.circuit_service import CircuitService
from src.io.parsers.circuit_synth_parser import CircuitSynthParser

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


@router.post("/import/circuit-synth", response_model=CircuitResponse, status_code=201)
async def import_circuit_synth(
    circuit_data: Dict[str, Any] = Body(...),
) -> CircuitResponse:
    """
    Import circuit from circuit-synth JSON format.

    This endpoint accepts circuit-synth JSON format and converts it to a
    simulatable circuit using intelligent component mapping.

    Args:
        circuit_data: Circuit-synth JSON data with components, nets, etc.

    Returns:
        Created circuit with generated ID and metadata

    Raises:
        HTTPException: 400 if import fails
        HTTPException: 422 if circuit-synth format is invalid

    Example:
        ```python
        import requests

        circuit_synth_data = {
            "name": "RC Filter",
            "components": {
                "R1": {"symbol": "Device:R", "value": "10k"},
                "C1": {"symbol": "Device:C", "value": "100nF"}
            },
            "nets": {
                "input": [{"component": "R1", "pin": "1"}],
                "output": [{"component": "R1", "pin": "2"}, {"component": "C1", "pin": "1"}],
                "gnd": [{"component": "C1", "pin": "2"}]
            }
        }

        response = requests.post(
            "http://localhost:8000/api/circuits/import/circuit-synth",
            json=circuit_synth_data
        )
        ```
    """
    try:
        # Parse circuit-synth data
        parser = CircuitSynthParser()
        import_result = parser.parse_dict(circuit_data)

        if not import_result.success:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to import circuit-synth data: {import_result.error}",
            )

        if not import_result.circuit:
            raise HTTPException(
                status_code=400, detail="Import succeeded but no circuit was created"
            )

        # Convert to circuit service format and create
        circuit_response = circuit_service.create_circuit_from_object(
            import_result.circuit
        )

        # Add import metadata
        circuit_response.metadata = circuit_response.metadata or {}
        circuit_response.metadata.update(
            {
                "import_format": "circuit-synth",
                "import_warnings": (
                    [w.message for w in import_result.warnings]
                    if import_result.warnings
                    else []
                ),
                "failed_components": (
                    len(import_result.failed_components)
                    if import_result.failed_components
                    else 0
                ),
                "format_info": import_result.format_info,
            }
        )

        return circuit_response

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=422, detail=f"Invalid circuit-synth format: {str(e)}"
        )
