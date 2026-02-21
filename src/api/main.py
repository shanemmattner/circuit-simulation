"""
FastAPI main application for circuit simulation web service.

Provides REST API endpoints for circuit creation, simulation job management,
and WebSocket support for real-time updates.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import circuits, simulations, websocket, complexity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app with metadata
app = FastAPI(
    title="Circuit Simulation API",
    description="Professional circuit simulation service with real-time updates",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(circuits.router)
app.include_router(simulations.router)
app.include_router(websocket.router)
app.include_router(complexity.router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Circuit Simulation API - Visit /docs for interactive documentation",
        "version": "0.1.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "circuits": "/api/circuits",
            "simulations": "/api/simulations",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "circuit-simulation-api"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
