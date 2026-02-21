"""
Complexity analysis API endpoints.

Provides REST endpoints for circuit complexity scoring and analysis.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from src.api.models.complexity import ComplexityResponse, ComplexityRequest
from src.api.services.complexity_service import ComplexityService
from src.circuit_sim.analysis.complexity import CalculateComplexityScore

router = APIRouter(prefix="/api/complexity", tags=["complexity"])

# Global complexity service instance
complexity_service = ComplexityService()


@router.post("/analyze", response_model=ComplexityResponse)
async def analyze_complexity(request: ComplexityRequest) -> ComplexityResponse:
    """
    Analyze circuit complexity.
    
    Accepts circuit component data and returns complexity metrics including
    the overall complexity score, component breakdown, and difficulty level.

    Args:
        request: Circuit data for complexity analysis

    Returns:
        ComplexityResponse with detailed metrics and scores

    Raises:
        HTTPException: 422 if validation fails
    """
    try:
        # Calculate complexity metrics
        metrics = CalculateComplexityScore(request.to_circuit())
        
        # Build response
        return complexity_service.build_response(metrics)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/score/{circuit_id}", response_model=ComplexityResponse)
async def get_complexity_score(circuit_id: str) -> ComplexityResponse:
    """
    Get complexity score for an existing circuit.
    
    Retrieves previously calculated complexity metrics for a stored circuit.

    Args:
        circuit_id: Unique circuit identifier

    Returns:
        ComplexityResponse with cached complexity metrics

    Raises:
        HTTPException: 404 if circuit not found or has no complexity data
    """
    result = complexity_service.get_cached(circuit_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No complexity data found for circuit: {circuit_id}"
        )
    return result


@router.post("/score/{circuit_id}", response_model=ComplexityResponse)
async def calculate_and_cache_complexity(
    circuit_id: str,
    components: list,
) -> ComplexityResponse:
    """
    Calculate and cache complexity score for a circuit.
    
    Accepts circuit components and stores the complexity result
    for future retrieval.

    Args:
        circuit_id: Unique circuit identifier
        components: List of circuit components

    Returns:
        ComplexityResponse with calculated complexity metrics

    Raises:
        HTTPException: 422 if calculation fails
    """
    try:
        # Build circuit from components
        from src.circuit_sim.circuit import Circuit
        
        circuit = Circuit(f"circuit_{circuit_id}")
        for comp in components:
            comp_type = comp.get("type", "")
            name = comp.get("name", "")
            node1 = comp.get("positive_node", comp.get("node1", ""))
            node2 = comp.get("negative_node", comp.get("node2", ""))
            value = comp.get("value", "")
            
            if comp_type == "resistor":
                circuit.add_resistor(name, node1, node2, value)
            elif comp_type == "capacitor":
                circuit.add_capacitor(name, node1, node2, value)
            elif comp_type == "inductor":
                circuit.add_inductor(name, node1, node2, value)
            elif comp_type == "voltage_source":
                circuit.add_voltage_source(name, node1, node2, value)
            elif comp_type == "current_source":
                circuit.add_current_source(name, node1, node2, value)
            elif comp_type == "diode":
                circuit.add_diode(name, node1, node2)
            elif comp_type == "led":
                circuit.add_led(name, node1, node2)
            elif comp_type == "zener":
                circuit.add_zener(name, node1, node2)
            elif comp_type == "mosfet":
                circuit.add_mosfet(name, node1, node2, node1)  # Simplified
            elif comp_type == "opamp":
                circuit.add_opamp(name, node1, node2, node1, node1, node1)  # Simplified
            elif comp_type == "bjt_transistor":
                circuit.add_bjt_transistor(name, node1, node2, node1)  # Simplified
            elif comp_type == "transformer":
                circuit.add_transformer(name, node1, node2, node1, node2)  # Simplified
            elif comp_type == "switch":
                circuit.add_switch(name, node1, node2)
        
        # Calculate complexity
        metrics = CalculateComplexityScore(circuit)
        
        # Cache and return
        response = complexity_service.build_response(metrics)
        complexity_service.cache_result(circuit_id, response)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
