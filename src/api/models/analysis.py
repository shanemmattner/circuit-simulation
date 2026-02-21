"""
Pydantic models for circuit analysis API operations.
"""

from typing import Dict, Optional, Tuple, Union

from pydantic import BaseModel, Field


class TheveninRequest(BaseModel):
    """Request model for Thevenin/Norton equivalent analysis.

    Calculates the Thevenin or Norton equivalent circuit parameters
    as seen from two terminals of a circuit.
    """

    terminal_pos: Union[int, str] = Field(
        ..., description="Positive terminal (node ID or name)"
    )
    terminal_neg: Union[int, str] = Field(
        ..., description="Negative terminal (node ID or name)"
    )


class TheveninResponse(BaseModel):
    """Response model for Thevenin/Norton equivalent analysis.

    Contains the equivalent circuit parameters:
    - Thevenin voltage (Vth): Open-circuit voltage
    - Thevenin resistance (Rth): Equivalent resistance
    - Norton current (In): Short-circuit current (Vth/Rth)
    """

    vth: float = Field(..., description="Thevenin voltage (open-circuit) in Volts")
    rth: float = Field(..., description="Thevenin resistance in Ohms")
    in_value: float = Field(..., description="Norton current (short-circuit) in Amps")
    terminals: Tuple[Union[int, str], Union[int, str]] = Field(
        ..., description="Terminal pair analyzed (positive, negative)"
    )
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Additional analysis metadata"
    )


class NortonRequest(BaseModel):
    """Request model for Norton current calculation.

    Calculates the short-circuit current between two terminals.
    """

    terminal_pos: Union[int, str] = Field(
        ..., description="Positive terminal (node ID or name)"
    )
    terminal_neg: Union[int, str] = Field(
        ..., description="Negative terminal (node ID or name)"
    )


class NortonResponse(BaseModel):
    """Response model for Norton current calculation."""

    in_value: float = Field(..., description="Norton current in Amps")
    terminals: Tuple[Union[int, str], Union[int, str]] = Field(
        ..., description="Terminal pair analyzed (positive, negative)"
    )
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Additional analysis metadata"
    )


class TheveninResistanceRequest(BaseModel):
    """Request model for Thevenin resistance calculation only."""

    terminal_pos: Union[int, str] = Field(
        ..., description="Positive terminal (node ID or name)"
    )
    terminal_neg: Union[int, str] = Field(
        ..., description="Negative terminal (node ID or name)"
    )


class TheveninResistanceResponse(BaseModel):
    """Response model for Thevenin resistance calculation."""

    rth: float = Field(..., description="Thevenin resistance in Ohms")
    terminals: Tuple[Union[int, str], Union[int, str]] = Field(
        ..., description="Terminal pair analyzed (positive, negative)"
    )
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Additional analysis metadata"
    )
