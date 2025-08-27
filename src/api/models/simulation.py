"""
Pydantic models for simulation-related API operations.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SimulationType(str, Enum):
    """Supported simulation types."""

    DC = "dc"
    TRANSIENT = "transient"
    AC = "ac"


class SimulationRequest(BaseModel):
    """Request model for starting a simulation."""

    type: SimulationType = Field(..., description="Type of simulation to run")
    parameters: Dict[str, Any] = Field(..., description="Simulation parameters")
    priority: int = Field(5, ge=1, le=10, description="Job priority (1=lowest, 10=highest)")


class SimulationStatus(BaseModel):
    """Response model for simulation job status."""

    job_id: str = Field(..., description="Unique job identifier")
    circuit_id: str = Field(..., description="Circuit identifier")
    type: SimulationType = Field(..., description="Simulation type")
    priority: int = Field(..., description="Job priority")
    status: str = Field(..., description="Job status: pending, running, completed, failed")
    progress: float = Field(0.0, ge=0.0, le=100.0, description="Progress percentage")
    eta_seconds: Optional[int] = Field(None, ge=0, description="Estimated time to completion")
    message: Optional[str] = Field(None, description="Status message")
    created_at: datetime = Field(..., description="Job creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Job start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Job completion timestamp")

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})


class SimulationResult(BaseModel):
    """Response model for simulation results."""

    job_id: str = Field(..., description="Job identifier")
    circuit_id: str = Field(..., description="Circuit identifier")
    type: SimulationType = Field(..., description="Simulation type")
    results: Dict[str, Any] = Field(..., description="Simulation data")
    plots: List[str] = Field(default_factory=list, description="Generated plot URLs")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    execution_time_seconds: float = Field(..., ge=0.0, description="Total execution time")
    created_at: datetime = Field(..., description="Result creation timestamp")

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
