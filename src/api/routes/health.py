"""Health check endpoint for API monitoring."""

from datetime import datetime

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "circuit-simulation-api",
        "version": "1.0.0",
    }


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    # Add any service dependency checks here
    # For example: database connectivity, external service availability
    
    return {
        "status": "ready",
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "simulation_engine": "ok",
            # Add more dependency checks as needed
        },
    }


@router.get("/live")
async def liveness_check():
    """Liveness check endpoint for Kubernetes/Docker health checks."""
    return {"status": "alive", "timestamp": datetime.now().isoformat()}