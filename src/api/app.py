"""FastAPI application for circuit simulation."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import circuits, health, simulations

app = FastAPI(
    title="Circuit Simulation API",
    description="Professional circuit simulation service with interactive reports",
    version="1.0.0",
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
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(circuits.router, prefix="/api/v1/circuits", tags=["circuits"])
app.include_router(
    simulations.router, prefix="/api/v1/simulations", tags=["simulations"]
)


@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "name": "Circuit Simulation API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
