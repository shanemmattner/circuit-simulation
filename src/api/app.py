"""FastAPI application for circuit simulation API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import circuits, simulations, health

app = FastAPI(
    title="Circuit Simulation API",
    description="Professional circuit simulation service with interactive reports",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for web frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(circuits.router, prefix="/api/v1/circuits", tags=["circuits"])
app.include_router(simulations.router, prefix="/api/v1/simulations", tags=["simulations"])

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Circuit Simulation API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/api/v1/health",
    }