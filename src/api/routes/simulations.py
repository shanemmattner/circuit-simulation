"""
Simulation job API endpoints.

Provides REST endpoints for simulation job management, status monitoring,
and result retrieval.
"""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Query

from src.api.models.simulation import SimulationRequest, SimulationStatus
from src.api.routes.circuits import circuit_service  # Import circuit service
from src.api.services.simulation_service import SimulationService

router = APIRouter(tags=["simulations"])

# Global simulation service instance
simulation_service = SimulationService(circuit_service)


@router.post(
    "/api/circuits/{circuit_id}/simulate", response_model=SimulationStatus, status_code=202
)
async def start_simulation(circuit_id: str, sim_request: SimulationRequest) -> SimulationStatus:
    """
    Start a simulation job for a circuit.

    Args:
        circuit_id: Circuit identifier
        sim_request: Simulation parameters and type

    Returns:
        SimulationStatus with job details

    Raises:
        HTTPException: 404 if circuit not found, 422 if validation fails
    """
    try:
        return simulation_service.start_simulation(circuit_id, sim_request)
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")


@router.get("/api/simulations/{job_id}", response_model=SimulationStatus)
async def get_simulation_status(job_id: str) -> SimulationStatus:
    """
    Get simulation job status.

    Args:
        job_id: Job identifier

    Returns:
        SimulationStatus with current job state

    Raises:
        HTTPException: 404 if job not found
    """
    status = simulation_service.get_simulation_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Simulation job not found")
    return status


@router.delete("/api/simulations/{job_id}", status_code=204)
async def cancel_simulation(job_id: str) -> None:
    """
    Cancel a simulation job.

    Args:
        job_id: Job identifier

    Raises:
        HTTPException: 404 if job not found
    """
    cancelled = simulation_service.cancel_simulation(job_id)
    if not cancelled:
        raise HTTPException(status_code=404, detail="Simulation job not found")


@router.get("/api/simulations", response_model=Dict)
async def list_simulations(
    skip: int = Query(0, ge=0, description="Number of simulations to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum simulations to return"),
) -> Dict:
    """
    List all simulation jobs with pagination.

    Args:
        skip: Number of simulations to skip for pagination
        limit: Maximum number of simulations to return

    Returns:
        Dictionary with simulations list, total count, and pagination info
    """
    return simulation_service.list_simulations(skip=skip, limit=limit)


@router.get("/api/simulations/{job_id}/results", response_model=Dict[str, Any])
async def get_simulation_results(job_id: str) -> Dict[str, Any]:
    """
    Get simulation results.

    Args:
        job_id: Job identifier

    Returns:
        Simulation results data

    Raises:
        HTTPException: 404 if job not found or not completed
    """
    results = simulation_service.get_simulation_results(job_id)
    if not results:
        # Check if job exists but isn't completed
        status = simulation_service.get_simulation_status(job_id)
        if not status:
            raise HTTPException(status_code=404, detail="Simulation job not found")
        elif status.status != "completed":
            raise HTTPException(
                status_code=409, detail=f"Simulation not completed (status: {status.status})"
            )
        else:
            raise HTTPException(status_code=404, detail="No results available")

    return results
