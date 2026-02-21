"""
Analysis service for circuit analysis operations.

Provides business logic for Thevenin/Norton equivalent circuit analysis.
"""

from typing import Dict

from src.api.models.analysis import (
    NortonResponse,
    TheveninResistanceResponse,
    TheveninResponse,
)
from src.api.services.circuit_service import CircuitService
from src.circuit_sim.analysis.thevenin import (
    calculate_norton_current,
    calculate_rth,
    calculate_thevenin,
)


class AnalysisService:
    """Service for circuit analysis operations."""

    def __init__(self, circuit_service: CircuitService):
        """Initialize analysis service.

        Args:
            circuit_service: Circuit service for circuit retrieval
        """
        self.circuit_service = circuit_service

    def calculate_thevenin(
        self,
        circuit_id: str,
        terminal_pos,
        terminal_neg,
    ) -> TheveninResponse:
        """Calculate Thevenin equivalent circuit parameters.

        Calculates the open-circuit voltage (Vth), Thevenin resistance (Rth),
        and Norton current (In = Vth/Rth) as seen from the specified terminals.

        Args:
            circuit_id: Circuit identifier
            terminal_pos: Positive terminal
            terminal_neg: Negative terminal

        Returns:
            TheveninResponse with Vth, Rth, and In

        Raises:
            ValueError: If circuit not found or terminals invalid
            RuntimeError: If simulation fails
        """
        circuit = self.circuit_service.get_circuit_object(circuit_id)
        if not circuit:
            raise ValueError("Circuit not found")

        result = calculate_thevenin(circuit, terminal_pos, terminal_neg)

        return TheveninResponse(
            vth=result["vth"],
            rth=result["rth"],
            in_value=result["in"],
            terminals=(terminal_pos, terminal_neg),
            metadata={
                "description": "Thevenin/Norton equivalent circuit parameters",
                "formula_in": "In = Vth / Rth",
            },
        )

    def calculate_norton_current(
        self,
        circuit_id: str,
        terminal_pos,
        terminal_neg,
    ) -> NortonResponse:
        """Calculate Norton current (short-circuit current).

        Calculates the current that would flow through a short circuit
        connected between the two terminals.

        Args:
            circuit_id: Circuit identifier
            terminal_pos: Positive terminal
            terminal_neg: Negative terminal

        Returns:
            NortonResponse with Norton current

        Raises:
            ValueError: If circuit not found or terminals invalid
            RuntimeError: If simulation fails
        """
        circuit = self.circuit_service.get_circuit_object(circuit_id)
        if not circuit:
            raise ValueError("Circuit not found")

        in_value = calculate_norton_current(circuit, terminal_pos, terminal_neg)

        return NortonResponse(
            in_value=in_value,
            terminals=(terminal_pos, terminal_neg),
            metadata={
                "description": "Norton current (short-circuit current)",
                "formula": "In = Vth / Rth",
            },
        )

    def calculate_thevenin_resistance(
        self,
        circuit_id: str,
        terminal_pos,
        terminal_neg,
    ) -> TheveninResistanceResponse:
        """Calculate Thevenin resistance.

        Calculates the equivalent resistance looking into the circuit
        from the specified terminals with all independent sources set to zero.

        Args:
            circuit_id: Circuit identifier
            terminal_pos: Positive terminal
            terminal_neg: Negative terminal

        Returns:
            TheveninResistanceResponse with Rth

        Raises:
            ValueError: If circuit not found or terminals invalid
            RuntimeError: If simulation fails
        """
        circuit = self.circuit_service.get_circuit_object(circuit_id)
        if not circuit:
            raise ValueError("Circuit not found")

        rth = calculate_rth(circuit, terminal_pos, terminal_neg)

        return TheveninResistanceResponse(
            rth=rth,
            terminals=(terminal_pos, terminal_neg),
            metadata={
                "description": "Thevenin resistance (Rth)",
                "method": "Zero all sources, inject test current, measure voltage response",
            },
        )
