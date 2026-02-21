"""
Circuit analysis API endpoints.

Provides REST endpoints for circuit analysis operations including
Thevenin/Norton equivalent circuit analysis.
"""

from fastapi import APIRouter, HTTPException

from src.api.models.analysis import (
    NortonRequest,
    NortonResponse,
    TheveninRequest,
    TheveninResistanceRequest,
    TheveninResistanceResponse,
    TheveninResponse,
)
from src.api.routes.circuits import circuit_service
from src.api.services.analysis_service import AnalysisService

router = APIRouter(prefix="/api/v1/circuits", tags=["analysis"])

# Global analysis service instance
analysis_service = AnalysisService(circuit_service)


@router.post(
    "/{circuit_id}/analysis/thevenin",
    response_model=TheveninResponse,
    summary="Calculate Thevenin equivalent",
    description="""
    Calculate Thevenin equivalent circuit parameters (Vth, Rth, In)
    as seen from two terminals of the circuit.
    
    - **Vth**: Open-circuit voltage between the terminals
    - **Rth**: Thevenin resistance (equivalent resistance with sources zeroed)
    - **In**: Norton current = Vth / Rth
    """,
)
async def calculate_thevenin_equivalent(
    circuit_id: str, request: TheveninRequest
) -> TheveninResponse:
    """Calculate Thevenin/Norton equivalent circuit parameters.

    Args:
        circuit_id: Circuit identifier
        request: Analysis request with terminal specifications

    Returns:
        TheveninResponse with Vth, Rth, and In values

    Raises:
        HTTPException: 404 if circuit not found, 422 if validation fails
    """
    try:
        return analysis_service.calculate_thevenin(
            circuit_id, request.terminal_pos, request.terminal_neg
        )
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post(
    "/{circuit_id}/analysis/norton",
    response_model=NortonResponse,
    summary="Calculate Norton current",
    description="""
    Calculate the Norton current (short-circuit current) that would flow
    between the specified terminals.
    
    The Norton current is calculated as In = Vth / Rth.
    """,
)
async def calculate_norton_current(
    circuit_id: str, request: NortonRequest
) -> NortonResponse:
    """Calculate Norton current (short-circuit current).

    Args:
        circuit_id: Circuit identifier
        request: Analysis request with terminal specifications

    Returns:
        NortonResponse with Norton current value

    Raises:
        HTTPException: 404 if circuit not found, 422 if validation fails
    """
    try:
        return analysis_service.calculate_norton_current(
            circuit_id, request.terminal_pos, request.terminal_neg
        )
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post(
    "/{circuit_id}/analysis/thevenin-resistance",
    response_model=TheveninResistanceResponse,
    summary="Calculate Thevenin resistance",
    description="""
    Calculate the Thevenin resistance (Rth) seen from two terminals.
    
    Rth is calculated by zeroing all independent sources and measuring
    the equivalent resistance looking into the terminals.
    """,
)
async def calculate_thevenin_resistance(
    circuit_id: str, request: TheveninResistanceRequest
) -> TheveninResistanceResponse:
    """Calculate Thevenin resistance (Rth).

    Args:
        circuit_id: Circuit identifier
        request: Analysis request with terminal specifications

    Returns:
        TheveninResistanceResponse with Rth value

    Raises:
        HTTPException: 404 if circuit not found, 422 if validation fails
    """
    try:
        return analysis_service.calculate_thevenin_resistance(
            circuit_id, request.terminal_pos, request.terminal_neg
        )
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
