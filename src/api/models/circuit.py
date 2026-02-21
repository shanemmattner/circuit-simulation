"""
Pydantic models for circuit-related API operations.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ComponentType(str, Enum):
    """Supported component types."""

    RESISTOR = "resistor"
    CAPACITOR = "capacitor"
    INDUCTOR = "inductor"
    VOLTAGE_SOURCE = "voltage_source"
    CURRENT_SOURCE = "current_source"


class ComponentInput(BaseModel):
    """Input model for circuit components."""

    type: ComponentType = Field(..., description="Component type")
    name: str = Field(
        ..., min_length=1, description="Component identifier (e.g., 'R1')"
    )
    positive_node: str = Field(..., description="Positive terminal node")
    negative_node: str = Field(..., description="Negative terminal node")
    value: str = Field(
        ..., min_length=1, description="Component value (e.g., '1k', '5V')"
    )
    model: Optional[str] = Field(None, description="Optional SPICE model")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """Ensure component name is valid identifier."""
        if not v.replace("_", "").isalnum():
            raise ValueError(
                "Component name must be alphanumeric with optional underscores"
            )
        return v


class CircuitCreate(BaseModel):
    """Request model for creating a new circuit."""

    name: str = Field(..., min_length=1, max_length=100, description="Circuit name")
    description: Optional[str] = Field(
        None, max_length=500, description="Circuit description"
    )
    components: List[ComponentInput] = Field(
        ..., min_length=1, description="Circuit components"
    )

    @field_validator("components")
    @classmethod
    def validate_components(cls, v):
        """Ensure component names are unique."""
        names = [comp.name for comp in v]
        if len(names) != len(set(names)):
            raise ValueError("Component names must be unique")
        return v


class CircuitResponse(BaseModel):
    """Response model for circuit information."""

    id: str = Field(..., description="Circuit unique identifier")
    name: str = Field(..., description="Circuit name")
    description: Optional[str] = Field(None, description="Circuit description")
    component_count: int = Field(..., description="Number of components")
    node_count: int = Field(..., description="Number of nodes")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})


class ValidationIssueResponse(BaseModel):
    """Response model for validation issues."""

    type: str = Field(..., description="Issue type")
    severity: str = Field(..., description="Issue severity (error, warning, info)")
    message: str = Field(..., description="Human-readable message")
    components: List[str] = Field(default_factory=list, description="Components involved")
    nodes: Optional[List[int]] = Field(None, description="Nodes involved")
    suggestion: Optional[str] = Field(None, description="Suggestion to fix the issue")


class ValidationResultResponse(BaseModel):
    """Response model for validation results."""

    rule_name: str = Field(..., description="Name of the validation rule")
    is_valid: bool = Field(..., description="Whether validation passed")
    issues: List[ValidationIssueResponse] = Field(
        default_factory=list, description="Error-level issues"
    )
    warnings: List[ValidationIssueResponse] = Field(
        default_factory=list, description="Warning-level issues"
    )
    info: List[ValidationIssueResponse] = Field(
        default_factory=list, description="Informational messages"
    )
    suggestions: List[str] = Field(
        default_factory=list, description="Suggestions to fix issues"
    )


class CircuitValidationResponse(BaseModel):
    """Response model for circuit validation."""

    is_valid: bool = Field(..., description="Overall validation status")
    total_errors: int = Field(..., description="Total number of errors")
    total_warnings: int = Field(..., description="Total number of warnings")
    results: List[ValidationResultResponse] = Field(
        default_factory=list, description="Validation results for each rule"
    )


class CircuitUpdate(BaseModel):
    """Request model for updating a circuit."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Circuit name"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Circuit description"
    )
    components: Optional[List[ComponentInput]] = Field(
        None, min_length=1, description="Circuit components"
    )

    @field_validator("components")
    @classmethod
    def validate_components(cls, v):
        """Ensure component names are unique if provided."""
        if v is not None:
            names = [comp.name for comp in v]
            if len(names) != len(set(names)):
                raise ValueError("Component names must be unique")
        return v
